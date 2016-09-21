from bs4 import BeautifulSoup
import lxml
from datetime import date
from annotator import annotator, geoname_annotator, ngram_annotator, token_annotator, ne_annotator
import nltk

""" This class represents an article or publication from PubMed Central. To
instantiate, pass a dict containing the elements `_id` and `nxml`, the latter
being the contents of the .nxml file from the PMC OAS. Conveniently, this is
what you get when you read an article out of the Mongo database created by the
`mongo_import_pmc_oas_local.py` script. 

This class is going to serve as a base class. Subclasses will provide
different methods to extract GeoNames from this."""
class Article:
    
    def __init__(self, article_dict):
        self._id = article_dict['_id']
        self.nxml = article_dict['nxml']
        self.soup = BeautifulSoup(self.nxml, 'lxml-xml')

    def __getattr__(self, name):
        return(self.get_text_from_tags(name))
        
    def get_text_from_tags(self, tag_name):
        tags = self.soup.find_all(tag_name)
        if tags is not None:
            tags_text = []
            for tag in tags:
                tags_text.append(tag.get_text())
            text = "\n\n".join(tags_text)
        else:
            text = None
        return(text)

    def pub_ids(self):
        pub_ids = {}
        for row in self.soup.front.find_all('article-id'):
            pub_id_type = row['pub-id-type']
            pub_id = row.get_text()
            pub_ids[pub_id_type] = pub_id
        return(pub_ids)

    def pub_dates(self):
        pub_dates = {}
        for row in self.soup.front.find_all('pub-date'):
            pub_type = row['pub-type']
            year = int(row.year.get_text()) if row.year is not None else 1
            month = int(row.month.get_text()) if row.month is not None else 1
            day = int(row.day.get_text()) if row.day is not None else 1
            # pub_date = date(year, month, day)
            pub_dates[pub_type] = date(year, month, day)
        return(pub_dates)

    """
    This is an assigned attribute because there are sometimes many article-title tags, but only the one in the front mater is relevant for us.
    """
    def article_title(self):
        if self.soup.front.find('article-title') is not None:
            article_title = self.soup.front.find('article-title').get_text
        else:
            article_title = None
        return(article_title)

    """
    The keywords method returns a list of keyword tags in the article. By default, it is restricted to keywords in the <front> element, but the "containing_tag" argument can be passed "" to search all. In the test set of 1000 articles, only 1 had keywords not in front matter. 503 had keywords at all. There seem to be 0 about infectious disease.
    """
    def keywords(self, containing_tag="front"):
        keyword_tags = self.soup.find(containing_tag).find_all("kwd")
        keywords = []
        for tag in keyword_tags:
            keywords.append(tag.get_text())
        return(keywords)

    def article_type(self):
        article_tag = self.soup.find("article")
        if article_tag is not None:
            article_type = article_tag.get("article-type")
        else:
            article_type = None
        return(article_type)