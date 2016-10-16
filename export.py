from pymongo import MongoClient
import pandas as pd
import time
import os

def geoname_dataframe(article, projection=None):
    if projection is None:
        projection = {'_id': 0, 'geonameid': 1, 'name': 1, 'latitude': 1, 'longitude': 1, 'population': 1}
    df = pd.DataFrame()
    if len(article['geonames']['culled']) == 0: # In the future, this should raise an error
        return(df)
    for loc in article['geonames']['culled']:
        row = geonames.find_one({'geonameid': loc['geonameid']}, projection)
        df = df.append(row, ignore_index=True)
    # Count multiple mentions and add a column for that, then drop duplicates.
    df['count'] = df.groupby('geonameid')['geonameid'].transform(pd.Series.value_counts)
    df = df.drop_duplicates()
    # Have a column to ID.
    df['article_id'] = article['_id']
    return(df)

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--mongo_url", default="localhost", dest="u"
    )
    parser.add_argument(
        "-d", "--mongo_db", default="pmc", dest="d"
    )
    parser.add_argument(
        "-c", "--mongo_collection", default="articles", dest="c"
    )
    args = parser.parse_args()

    # In the future, these should probably be arguments.
    query = {"index.infectious": 1, "index.research": 1}
    export_dir = 'export/' + time.strftime("%Y-%m-%d_%H-%M-%S") + "/"

    articles = MongoClient(args.u)[args.d][args.c]
    geonames = MongoClient(args.u)['geonames']['allCountries']

    # print("Counting...")
    # print("About to start work on {} articles".format(articles.count(query)))
    cursor = articles.find(query)

    for i, article in enumerate(cursor):
        df = geoname_dataframe(article)
        subdir = str(i // 10000 + 1) + '/'
        csvfile = export_dir + subdir + article['_id'] + '.csv'
        ensure_dir(csvfile)
        print(csvfile)
        df.to_csv(csvfile)
