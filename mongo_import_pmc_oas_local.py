#!/usr/bin/env python

"""
If run as a script, crawls the directory tree provided as an argument, and imports all .nxml files in that directory into a Mongo collection.

If imported, provides classes for importing a .nxml file into a Mongo collection.
"""

import os
import pymongo

def mongo_document_from_nxml(file_path):
    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    with open(file_path, 'r') as f:
        nxml = f.read()
    article = {
        '_id': name,
        'nxml': nxml
    }
    return(article)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pmc_path', default='/Volumes/Transcend/pmc-subset'
    )
    args = parser.parse_args()

    articles = pymongo.MongoClient().pmc.articles
    articles.drop()

    for (dirpath, dirnames, filenames) in os.walk(args.pmc_path):
        for name in filenames:
            print(name)
            filepath = os.path.join(dirpath, name)
            if filepath.endswith('nxml'):
                article = mongo_document_from_nxml(filepath)
                articles.insert(article)
    print(articles.count())
