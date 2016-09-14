"""
Iterate over the PubMED articles that mention infecious diseases from the
disease ontology in their abstracts.
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
    return [str(r[1]) for r in qres]

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

def iterate_infectious_disease_articles(collection):
    keyword_annotator = KeywordAnnotator(keywords=get_annotation_keywords())
    for article in collection.find():
        abstract = pubcrawler.Article(article).get_text_from_tags('abstract')
        anno_doc = AnnoDoc(abstract)
        anno_doc.add_tier(keyword_annotator)
        infectious_diseases = [
            (disease.text, resolve_keyword(disease.text))
            for disease in anno_doc.tiers['keywords'].spans
        ]
        if len(infectious_diseases) > 0:
            yield article, infectious_diseases

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mongo_url", default='localhost'
    )
    parser.add_argument(
        "--db_name", default='pmc'
    )
    args = parser.parse_args()
    db = pymongo.MongoClient(args.mongo_url)[args.db_name]
    for article, infectious_diseases in iterate_infectious_disease_articles(db.articlesubset):
        print(article['_id'], infectious_diseases)
