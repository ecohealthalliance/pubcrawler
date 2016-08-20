# PubCrawler

Rewrite of Pub Crawler. Pub Crawler extends Annie to perform toponym recognition on PubMed Open Access Subset NXML files

PubCrawler is a tool for conducting GeoName extraction (a.k.a. toponym resolution) and aggregation on the PubMed Central Open-Access Subset (PMCOAS).

PubCrawler comprises a set of scripts in Python and R.

## Setting Up

This assumes you have a virtualenv named `pubcrawler` containing Python 3.5.2, and have installed `requirements.txt` into it.

It also assumes you're running MonboDB version 3.2.7, and have started `mongod` pointing at your desired `dbpath`.

To import the PubMed Central Open Access Subset into a database, run `mongo_import_pmc_oas_local.py`. This script requires that you have downloaded the selection of .nxml files you wish to import into a directory. Use the argument `--pmc_path` to locate the directory.

The script will drop the collection `articles` in the database `pmc` and replace it with every .nxml file in every subdirectory of the specified directory, using the file basename as the `_id` and the file contents as the `nxml` property.