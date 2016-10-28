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
        "-c", "--mongo_collection", default="articles", dest = "c"
    )
    args = parser.parse_args()


    print("Making connection.")
    articles = pymongo.MongoClient(args.u)[args.d][args.c]

    # articles.create_index("index.meta")
    # articles.create_index("index.keywords")
    # articles.create_index("index.geonames")
    articles.create_index("index")