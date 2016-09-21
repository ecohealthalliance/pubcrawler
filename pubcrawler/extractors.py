"""
Iterate over the PubMED articles that mention infecious diseases from the
disease ontology.
"""
import rdflib
from pylru import lrudecorator
import pubcrawler.article as pubcrawler
from annotator.keyword_annotator import KeywordAnnotator
from annotator.geoname_annotator import GeonameAnnotator
from annotator.geoname_annotator import GeoSpan
from annotator.annotator import AnnoDoc
import re
import json
import numpy

@lrudecorator(1)
def get_disease_ontology():
    disease_ontology = rdflib.Graph()
    disease_ontology.parse(
        "http://purl.obolibrary.org/obo/doid.owl",
        format="xml"
    )
    return(disease_ontology)

def get_annotation_keywords():
    qres = get_disease_ontology().query("""
    prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
    prefix obo: <http://purl.obolibrary.org/obo/>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?entity ?label
    WHERE {
        # only resolve diseases by infectious agent
        ?entity rdfs:subClassOf* obo:DOID_0050117
        ; oboInOwl:hasNarrowSynonym|oboInOwl:hasRelatedSynonym|oboInOwl:hasExactSynonym|rdfs:label ?label
    }
    """)
    def remove_parenthetical_notes(label):
        label = re.sub(r"\s\(.*\)","", label)
        label = re.sub(r"\s\[.*\]","", label)
        assert(len(label) > 0)
        return label
    return list(set([remove_parenthetical_notes(str(r[1])) for r in qres]))

def str_escape(s):
    return json.dumps(s)[1:-1]

@lrudecorator(500)
def resolve_keyword(keyword):
    query = """
    prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
    prefix obo: <http://purl.obolibrary.org/obo/>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?entity
    WHERE {
        # only resolve diseases by infectious agent
        ?entity rdfs:subClassOf* obo:DOID_0050117
        ; oboInOwl:hasNarrowSynonym|oboInOwl:hasRelatedSynonym|oboInOwl:hasExactSynonym|rdfs:label ?label
        FILTER regex(?label, "^(""" + str_escape(re.escape(keyword)) + str_escape("(\s[\[\(].*[\]\)])*") + """)$", "i")
    }
    """
    qres = list(get_disease_ontology().query(query))
    if len(qres) == 0:
        print("no match for", keyword.encode('ascii', 'xmlcharrefreplace'))
    elif len(qres) > 1:
        print("multiple matches for", keyword.encode('ascii', 'xmlcharrefreplace'))
        print(qres)
    return qres


@lrudecorator(1)
def keyword_annotator():
    return(KeywordAnnotator(keywords=get_annotation_keywords()))

def keywords_to_list(keywords):
    seen_keys = []
    keyword_list = []
    for keyword_entity in keywords:
        keyword, uri = keyword_entity
        if keyword in seen_keys:
            continue
        else:
            seen_keys.append(keyword)
            keyword_dict = {
                "keyword": keyword,
                "uri": uri[0].entity.toPython()
            }
            keyword_list.append(keyword_dict)
    return(keyword_list)

def extract_disease_ontology_keywords(article):
    pc_article = pubcrawler.Article(article)
    anno_doc = AnnoDoc(pc_article.body)
    anno_doc.add_tier(keyword_annotator())
    infectious_diseases = [
        (disease.text, resolve_keyword(disease.text))
        for disease in anno_doc.tiers['keywords'].spans
    ]
    disease_ontology_keywords = None if len(infectious_diseases) == 0 else keywords_to_list(infectious_diseases)
    return({
        'keywords':
        {
            'disease-ontology': disease_ontology_keywords
        }
    })


def extract_meta(article):
    pc_article = pubcrawler.Article(article)
    return({
        'meta':
        {
            'article-ids': pc_article.pub_ids(),
            'article-type': pc_article.article_type(),
            # 'pub-dates': pc_article.pub_dates()
            # Need to fix stuff with dates in Mongo
            'keywords': pc_article.keywords()
        }
    })

# This enables us to lazily call geoname_annotator() instead of having an
# object that's instantiated every time the library is loaded.
@lrudecorator(1)
def geoname_annotator():
    return(GeonameAnnotator())

def extract_geonames(article):
    pc_article = pubcrawler.Article(article)
    anno_doc = AnnoDoc(pc_article.body)
    candidate_locations = geoname_annotator().get_candidate_geonames(anno_doc)

    # Generate and score features
    features = geoname_annotator().extract_features(candidate_locations)
    feature_weights = dict(
        population_score=2.0,
        synonymity=1.0,
        num_spans_score=0.4,
        short_span_score=(-5),
        NEs_contained=1.2,
        # Distinctness is probably more effective when combined
        # with other features
        distinctness=1.0,
        max_span_score=1.0,
        # close_locations=0.8,
        # closest_location=0.8,
        # containment_level=0.8,
        cannonical_name_used=0.5,
        feature_code_score=0.6,
    )
    for location, feature in zip(candidate_locations, features):
        location['score'] = feature.score(feature_weights)
    culled_locations = [location
        for location in candidate_locations
        if location['score'] > 50]
    geo_spans = []
    for location in culled_locations:
        # Copy the dict so we don't need to return a custom class.
        location = dict(location)
        for span in location['spans']:
            # TODO: Adjust scores to give geospans that exactly match
            # a corresponding geoname a bonus.
            geo_span = GeoSpan(
                span.start, span.end, anno_doc, location
            )
            geo_spans.append(geo_span)
    culled_geospans = geoname_annotator().cull_geospans(geo_spans)
    # props_to_omit = ['spans', 'alternatenames', 'alternateLocations']
    # for geospan in culled_geospans:
    #     # The while loop removes the properties from the parentLocations.
    #     # There will probably only be one parent location.
    #     cur_location = geospan.geoname
    #     while True:
    #         if all([
    #             prop not in cur_location
    #             for prop in props_to_omit
    #         ]):
    #             break
    #         for prop in props_to_omit:
    #             cur_location.pop(prop)
    #         if 'parentLocation' in cur_location:
    #             cur_location = cur_location['parentLocation']
    #         else:
    #             break

    props_to_omit = ['spans', 'alternateLocations']
    # Get candidate geonameids and feature vectors
    all_geonames = []
    for location, feature in zip(candidate_locations, features):
        geoname_dict = location
        for prop in props_to_omit:
            geoname_dict.pop(prop, None)
#         geoname_dict['geonameid'] = location['geonameid']
        geoname_dict['annie_features'] = feature.to_dict()
        all_geonames.append(geoname_dict)

    culled_geonames = []
    for geospan in culled_geospans:
        geoname = geospan.geoname
        for prop in props_to_omit:
            geoname.pop(prop, None)
        culled_geonames.append(geospan.to_dict())
    return({
        'geonames':
        {
            'all': all_geonames,
            'culled': culled_geonames
        }
    })

def combine_extracted_info(article, extractors):
    extractors = [extractors] if callable(extractors) else extractors
    extracted = {}
    for f in extractors:
        extracted.update(f(article))
    return(extracted)


# query = {}
# if no_reannotation is not None:
#     query = {no_reannotation: {'$exists': False}}
# cursor = collection.find(query, limit=limit)

"""
Notes:
- Takes a cursor and a list of extractors
"""
def extract_and_write_multiple(cursor, extractors):
    for article in cursor:
        to_write = combine_extracted_info(article, extractors)
        cursor.collection.update_one({'_id': article['_id']}, {'$set': to_write})


def strip_article_info(collection):
    collection.update_many({},
        {
        '$unset':
            {
            'meta': "",
            'keywords': "",
            'geonames': ""
            }
        })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mongo_url", default='localhost'
    )
    parser.add_argument(
        "--db_name", default='pmc'
    )
    # parser.add_argument(
    #     "--no_reannotation", default=None
    # )
    args = parser.parse_args()
    db = pymongo.MongoClient(args.mongo_url)[args.db_name]
    keyword_annotator = KeywordAnnotator(keywords=get_annotation_keywords())
    geoname_annotator = GeonameAnnotator()
    articles = db.article
