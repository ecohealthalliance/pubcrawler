"""

This script iterates over a specified collection of nxml articles and extracts a
specified set of data from them.

You can specify the url for the Mongo server, as well as the name of the
database and collection.

You *must* also specify one or more of the extractor functions from the
pubcrawler.extractors module. But specify them by just their name; this package
adds the correct suffix automatically. This should be fixed in a later version,
but it was the only good way to allow an argument from the command line.

You can also specify a -skip_field. You don't have to do this, but it's best to,
because this is what's used to report progress (because of ugly multiprocess
stuff, and because python's Queue.qsize() method is not implemented on macOS).

You can also specify a limit, as well as the number of worker processes you
want.

"""

import time
import sys
import pymongo
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
    parser.add_argument(
        "-x", "-extract", action="append", default=None, dest = "x"
    )
    parser.add_argument(
        "-s", "-skip_field", default=None, dest = "s"
    )
    parser.add_argument(
        "-w", "-workers", default=4, dest = "w"
    )
    parser.add_argument(
        "-l", "-limit", default=None, dest = "l"
    )
    args = parser.parse_args()

    if args.s is not None:
        query = {args.s: {'$exists': False}}
    else:
        query = {}

    print("Making connection.")
    articles = pymongo.MongoClient(args.u)[args.d][args.c]
    print(len(query))
    print("About to count.")
    total_for_query = articles.count(query)

    while total_for_query != 0:
        total_for_query = articles.count(query)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print("At time {}, query {} matches {} articles.".format(now, query, total_for_query))
        time.sleep(5)