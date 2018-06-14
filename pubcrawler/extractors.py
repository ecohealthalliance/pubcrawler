"""
Iterate over the PubMED articles that mention infecious diseases from the
disease ontology.
"""
from pylru import lrudecorator
import pubcrawler.article as pubcrawler
from epitator.resolved_keyword_annotator import ResolvedKeywordAnnotator
from epitator.geoname_annotator import GeonameAnnotator, GEONAME_ATTRS
from epitator.geoname_annotator import GeoSpan
from epitator.annotator import AnnoDoc


@lrudecorator(1)
def keyword_annotator():
    return(ResolvedKeywordAnnotator())


def extract_disease_ontology_keywords(article):
    pc_article = pubcrawler.Article(article)
    anno_doc = AnnoDoc(pc_article.body)
    resolved_keyword_tier = anno_doc.require_tiers('resolved_keywords', via=keyword_annotator)
    disease_ontology_keyword_dict = {}
    for span in resolved_keyword_tier:
        for resolution in span.metadata['resolutions']:
            entity = resolution['entity']
            if entity['type'] == 'disease':
                disease_ontology_keyword_dict[entity['id']] = {
                    "keyword": entity['label'],
                    "uri": entity['id']
                }
    return({
        'index.keywords': 1,
        'keywords': {
            'disease-ontology': list(disease_ontology_keyword_dict.values())
        }
    })


def extract_meta(article):
    pc_article = pubcrawler.Article(article)
    return({
        'index.meta': 1,
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


def extract_geonames(article, store_all=False):
    pc_article = pubcrawler.Article(article)
    anno_doc = AnnoDoc(pc_article.body)
    geoname_tier = anno_doc.require_tiers('geonames', via=geoname_annotator)
    geoname_dicts = {}
    for span in geoname_tier:
        geoname = span.metadata['geoname']
        result = {}
        if store_all:
            for key in GEONAME_ATTRS + ['score']:
                result[key] = geoname[key]
        else:
            result['geonameid'] = geoname['geonameid']
        geoname_dicts[result['geonameid']] = result
    return({
        'index.geonames': 1,
        'geonames': {
            'culled': list(geoname_dicts.values())
        }
    })


def combine_extracted_info(article, extractors):
    extractors = [extractors] if callable(extractors) else extractors
    extracted = {}
    for f in extractors:
        extracted.update(f(article))
    return(extracted)


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
            'index': "",
            'meta': "",
            'keywords': "",
            'geonames': ""
            }
        })

