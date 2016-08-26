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
    
    def article_title(self):
        if self.soup.front.find('article-title') is not None:
            article_title = self.soup.front.find('article-title').get_text
        else:
            article_title = None
        return(article_title)

    def abstract(self):
        if self.soup.abstract is not None:
            abstract = self.soup.abstract.get_text()
        else:
            abstract = None
        return(abstract)

    def body(self):
        if self.soup.body is not None:
            body = self.soup.body.get_text()
        else:
            body = None
        return(body)
