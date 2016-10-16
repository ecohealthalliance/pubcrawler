from pymongo import MongoClient
# from annotator.keyword_annotator import KeywordAnnotator
# from annotator.geoname_annotator import GeonameAnnotator

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--mongo_url", default="localhost", dest = "u"
    )
    parser.add_argument(
        "-d", "--mongo_db", default="pmc", dest = "d"
    )
    parser.add_argument(
        "-c", "--mongo_collection", default="articlesubset", dest = "c"
    )
    args = parser.parse_args()
    print("Making connection.")
    articles = MongoClient(args.u)[args.d][args.c]
    print("Writing index field...")
    articles.update_many({'meta.article-type': 'research-article'},
                         {'$set': {'index.research': 1}})
    print("Creating index...")
    articles.create_index("index.research")
    print("Done.")