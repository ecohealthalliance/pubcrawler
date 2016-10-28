from pymongo import MongoClient
import pandas as pd

geonames = MongoClient()['geonames']['allCountries']

spots_and_undersea = []
for geonameid in geonames.find({"feature class": {"$in": ["S", "U"]}},
                               {"_id": 0, "geonameid": 1, "name": 1}):
    spots_and_undersea.append(geonameid)
spots_and_undersea

continents = []
for geonameid in geonames.find({"feature code": "CONT"},
                               {"_id": 0, "geonameid": 1, "name": 1}):
    continents.append(geonameid)
continents

countries = []
for geonameid in geonames.find({"feature code": "PCLI"},
                               {"_id": 0, "geonameid": 1, "name": 1}):
    countries.append(geonameid)
countries

pd.DataFrame(spots_and_undersea).to_csv(path_or_buf="export/blocklists/spots_and_undersea.csv", index=False)
pd.DataFrame(continents).to_csv(path_or_buf="export/blocklists/continents.csv", index=False)
pd.DataFrame(countries).to_csv(path_or_buf="export/blocklists/countries.csv", index=False)