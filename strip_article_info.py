import sys
import pubcrawler.extractors as ex
import argparse
import pymongo
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
parser.add_argument(
    "-s", "--strip", action="append", default=None, dest = "x"
)
args = parser.parse_args()

articles = pymongo.MongoClient(args.u)[args.d][args.c]
ex.strip_article_info(articles)