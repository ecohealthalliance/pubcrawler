# PubCrawler

Rewrite of Pub Crawler. Pub Crawler extends Annie to perform toponym recognition on PubMed Open Access Subset NXML files

PubCrawler is a tool for conducting GeoName extraction (a.k.a. toponym resolution) and aggregation on the PubMed Central Open-Access Subset (PMCOAS).

PubCrawler comprises a set of scripts in Python and R.

## Setting Up

This assumes you have a virtualenv named `pubcrawler` containing Python 3.5.2, and have installed `requirements.txt` into it.

It also assumes you're running MonboDB version 3.2.7, and have started `mongod` pointing at your desired `dbpath`.

To import the PubMed Central Open Access Subset into a database, run `mongo_import_pmc_oas_local.py`. This script requires that you have downloaded the selection of .nxml files you wish to import into a directory. Use the argument `--pmc_path` to locate the directory.

The script will drop the collection `articles` in the database `pmc` and replace it with every .nxml file in every subdirectory of the specified directory, using the file basename as the `_id` and the file contents as the `nxml` property.

The `data/` directory isn't under version control. Find it at the Dropbox link below.

The `data/dump/pmc/` directory contains a mongodump of the subset of 10000 articles which I'm going to use as I'm building the package.

Since that directory isn't being tracked, for now, it's available at this [Dropbox link](https://www.dropbox.com/sh/euraoigy8i17j32/AABEr6tmXamHcP22a6SpgMhpa?dl=0)

There is a copy of it available in our pubcrawler bucket which can be downloaded via the command `aws s3 cp s3://pubcrawler/data.zip .`.

```
mongodump --db pmc --collection articlesubset --gzip
```
Restore this to a local database.

Download the Disease Ontology OWL file: `curl http://www.berkeleybop.org/ontologies/doid.owl > doid.owl`

### Geonames

Use the `mongo_import_geonames.py` script to import Geonames's allCountries csv into a Mongo collection. Follow up by creating an index on `geonameid`.

### Annie

Use the `python3` branch of Annie. Install by navigating to Annie's root directory and running `python setup.py install` with the `pubcrawler` virtualenv active.

Annie uses some nltk components that require running the following command in the virtualenv to install:

```
python -c "import nltk; nltk.download('maxent_ne_chunker', 'maxent_treebank_pos_tagger', 'words', 'punkt', 'averaged_perceptron_tagger')"
```

### Running on Aegypti.

I'm going to start mongod with `mongod --fork --logpath ~/pubcrawler/mongodb.log --dbpath ~/data/db`.
I'll shut it down with `mongod --shutdown`

Mongo often throws an error number 14. To fix that:
```
sudo chown `whoami` /tmp/mongodb-27017.sock
```

`crawler.py -x extract_disease_ontology_keywords -s meta -w 8 -c articlesubset`

First I'll try:

`cd pubcrawler` (The `dump` is there alongside `annie` and `pubcrawler`)
`nohup mongorestore --gzip &`

The final command I used was:
`nohup python crawler_batches.py -c articles -x extract_meta -x extract_disease_ontology_keywords -x extract_geonames -s index.meta -w 18 -b 10000 &`

Remaining articles were checked with this command:
`python crawler_count.py -c articles -s index.meta`