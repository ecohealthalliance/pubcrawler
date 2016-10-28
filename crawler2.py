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

import multiprocessing as mp
import time
import sys
import pymongo
# from annotator.keyword_annotator import KeywordAnnotator
# from annotator.geoname_annotator import GeonameAnnotator
import pubcrawler.extractors as ex


def chunk_slices(length, by):
    items = list(range(0, length + 1, by))
    if length % by != 0:
        items.append(length)
    slices = [slice(items[i], items[i+1]) for i in range(0, len(items)-1)]
    return(slices)

def worker(url, db, collection, to_extract, query, index_queue):
    articles = pymongo.MongoClient()[db][collection]
    cursor = articles.find(query)
    print("Cursor count: {}".format(cursor.count()))
    for i in iter(index_queue.get, 'STOP'):
        print("Trying article {}.".format(i))
        try:
            article = cursor[i]
        except IndexError:
            print("Failed lookup for article{}.".format(i))
            continue
        to_write = ex.combine_extracted_info(article, to_extract)
        articles.update_one({'_id': article['_id']}, {'$set': to_write})


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
    print(args)

    if args.x is not None:
        extractor_funs = [eval(x) for x in ['ex.' + x for x in args.x]]
    else:
        print("Please specify at least one extractor function", file=sys.stderr)
        sys.exit(1)

    if args.s is not None:
        query = {args.s: {'$exists': False}}
    else:
        query = {}

    print("Making connection.")
    articles = pymongo.MongoClient(args.u)[args.d][args.c]

    print("About to count.")
    total_for_query = articles.count(query)
    num_to_annotate = args.l if args.l is not None else total_for_query
    num_workers = int(args.w)
    print("Total for query is {}.".format(total_for_query))

    queue = mp.Queue()
    for i in range(num_to_annotate):
        queue.put(i)
    for w in range(num_workers):
        queue.put('STOP')

    # # Chunking, which we don't do any more.
    # queue = mp.Queue()
    # for i in chunk_slices(num_to_annotate, by = 100):
    #     queue.put(i)
    # for w in range(num_workers):
    #     queue.put('STOP')

    worker_args = (
        args.u,
        args.d,
        args.c,
        extractor_funs,
        query,
        queue,
    )

    print("About to start.")

    for w in range(num_workers):
        mp.Process(target=worker, args=worker_args).start()

    # while not queue.empty():
    #     print("Still going...")
    #     # total_for_query_now = articles.count(query)
    #     # done = total_for_query - total_for_query_now
    #     # left = num_to_annotate - done
    #     # print("Annotated {} out of {} articles ({:.2%}). {} remaining.".format(done,
    #         # num_to_annotate, done / num_to_annotate, left))
    #     time.sleep(5)