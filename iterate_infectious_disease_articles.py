"""
Iterate over the PubMED articles that mention infecious diseases from the
disease ontology.
"""
import rdflib
from pylru import lrudecorator
import pubcrawler.article as pubcrawler
from annotator.keyword_annotator import KeywordAnnotator
from annotator.annotator import AnnoDoc
import re
import json
import pymongo

print("Loading disease ontology...")
disease_ontology = rdflib.Graph()
disease_ontology.parse(
    "http://purl.obolibrary.org/obo/doid.owl",
    format="xml"
)
print("disease ontology loaded")

def get_annotation_keywords():
    qres = disease_ontology.query("""
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
    qres = list(disease_ontology.query(query))
    if len(qres) == 0:
        print("no match for", keyword.encode('ascii', 'xmlcharrefreplace'))
    elif len(qres) > 1:
        print("multiple matches for", keyword.encode('ascii', 'xmlcharrefreplace'))
        print(qres)
    return qres

""" This gets the list of tuples returned by the function below and transforms
it into a dict, appropriate for dumping into a Mongo document. """
def annotated_keyword_list_to_dict(keyword_list):
    keyword_dict = {}
    for keyword_entity in keyword_list:
        keyword, uri = keyword_entity
        if keyword in keyword_dict:
            continue
        else:
            keyword_dict[keyword] = uri[0].entity.toPython()
    return(keyword_dict)

"""
Currently, this writes the following set of metadata to the appropriate
mongo document:

- meta
    - article-ids
    - article-type
    - keywords
- annotations
    - disease-ontology-keywords
"""

def write_article_meta_to_mongo(article, collection):
    pc_article = pubcrawler.Article(article)
    anno_doc = AnnoDoc(pc_article.body)
    anno_doc.add_tier(keyword_annotator)
    infectious_diseases = [
        (disease.text, resolve_keyword(disease.text))
        for disease in anno_doc.tiers['keywords'].spans
    ]
    disease_ontology_keywords = None if len(infectious_diseases) == 0 else annotated_keyword_list_to_dict(infectious_diseases)
    collection.update_one({'_id': article['_id']},
        {
        '$set':
            {
            'meta':
                {
                'article-ids': pc_article.pub_ids(),
                'article-type': pc_article.article_type(),
                # 'pub-dates': pc_article.pub_dates()
                # Need to fix stuff with dates in Mongo
                'keywords': pc_article.keywords()
                },
            'annotations':
                {
                'disease-ontology-keywords': disease_ontology_keywords
                }
            },
        })

def iterate_infectious_disease_articles(collection):
    query = {}
    if args.no_reannotation:
        query = {'meta': {'$exists': False}}
    total_articles = collection.count(query)
    processed_articles = 0
    for article in collection.find(query):
        processed_articles += 1
        print("Processing article {} of {} ({:.2}%)...".format(processed_articles, total_articles, processed_articles / total_articles), end="")
        write_article_meta_to_mongo(article, collection=collection)
        print(" Done!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mongo_url", default='localhost'
    )
    parser.add_argument(
        "--db_name", default='pmc'
    )
    parser.add_argument(
        "--no_reannotation", dest="no_reannotation", action="store_true"
    )
    args = parser.parse_args()
    db = pymongo.MongoClient(args.mongo_url)[args.db_name]
    keyword_annotator = KeywordAnnotator(keywords=get_annotation_keywords())
    iterate_infectious_disease_articles(db.articlesubset)
