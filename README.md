# PubCrawler

Rewrite of Pub Crawler. Pub Crawler extends Annie to perform toponym recognition on PubMed Open Access Subset NXML files

PubCrawler is a tool for conducting GeoName extraction (a.k.a. toponym resolution) and aggregation on the PubMed Central Open-Access Subset (PMCOAS).

PubCrawler comprises a set of scripts in Python and R.

## Setting Up

This assumes you have a virtualenv named `pubcrawler` containing Python 3.5.2, and have installed `requirements.txt` into it.

It also assumes you're running MonboDB version 3.2.7, and have started `mongod` pointing at your desired `dbpath`.

To import the PubMed Central Open Access Subset into a database, run `mongo_import_pmc_oas_local.py`. This script requires that you have downloaded the selection of .nxml files you wish to import into a directory. Use the argument `--pmc_path` to locate the directory.

The script will drop the collection `articles` in the database `pmc` and replace it with every .nxml file in every subdirectory of the specified directory, using the file basename as the `_id` and the file contents as the `nxml` property.

The `dump/pmc/` directory contains a mongodump of the subset of 1000 articles which I'm going to use as I'm building the package. **TODO: Move this to an S3 bucket.**

### Annie

Use the `python3` branch of Annie. Install by navigating to Annie's root directory and running `python setup.py install` with the `pubcrawler` virtualenv active.

As of 2016-09-02, Annie's TokenAnnotator won't work with its default regular expression. I'm using `token_annotator.TokenAnnotator(tokenizer=nltk.tokenize.RegexpTokenizer('\w+|[^\w\s]+'))` instead, which removes the ability to tokenize whole http words.

Annie's `POSAnnotator()` requires that you've run `nltk.download()`.