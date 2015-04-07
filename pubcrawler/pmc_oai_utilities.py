#!/usr/bin/env python
""" The PubMed Central OAI-PMH service (PMC-OAI, documented at
http://www.ncbi.nlm.nih.gov/pmc/tools/oai/) implements the Open Archives
Initiative Protocol for Metadata Harvesting for PubMed Central records. Much of
the service's functionality is beyond the scope of Pub Crawler's functionality,
but these functions simplify interaction with the service, fetching the NXML
content for an article with a given PubMed Central ID number or DOI (latter not
yet implemented). """

import requests
from re import sub
import json

# What I need to do is make a class "article identifier" and have it initialize
# with a string, and it has functions to guess that type of string and methods
# to produce other identifiers using lookup. Or, even better, when it
# initializes, it cross-references them. Maybe using the web service. Or it
# guesses the ID type and uses the web service to look up the XML article
# information. If I can guess the ID type, why even bother with more. :)

# def get_xml_from_oai(oaiid):
#     url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
#     params = {'verb': 'GetRecord',
#               'identifier': oaiid,
#               'metadataPrefix': 'pmc'}
#     return requests.post(url, params)


class PMCIDConverter():
    """Uses PMC's ID Converter API to get all IDs for a requested ID"""

    # Fetch IDs that the PMC ID Converter returns.
    def __init__(self, requested_id):
        url = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
        params = {'tool': 'IDConverter',
                  'email': 'toph.allen@gmail.com',
                  'format': 'json',
                  'ids': requested_id}
        r = requests.post(url, params)
        j = r.json()['records'][0]

        # Set them as attributes
        for key in j:
            setattr(self, key, j[key])

        # If we have a PMCID, we also want an OAIID for the XML API.
        try:
            self.oaiid = self.__make_oaiid(self.pmcid)
        except AttributeError:
            print("No PMCID found. Cannot create OAI identifier.")

    def __make_oaiid(self, pmcid):
        numeric_portion = sub(r'[A-Za-z]', '', pmcid)
        identifier_base = 'oai:pubmedcentral.nih.gov:'
        return identifier_base + numeric_portion


class PMCXMLDownloader():
    """Downloader for PMC Open Access Subset XML files.
    This one uses the PMCIDConverter class.
    It stores all document IDs as attributes: self.ids.doi"""

    # Get all available IDs for this document.
    def __init__(self, requested_id):
        self.ids = PMCIDConverter(requested_id)
        r = self.__request_xml_from_oai(self.ids.oaiid)
        self.text = r.text

    # Use the OAIID to fetch the document's XML from PMC's OAI service.
    def __request_xml_from_oai(self, oaiid):
        url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
        params = {'verb': 'GetRecord',
                  'identifier': oaiid,
                  'metadataPrefix': 'pmc'}
        return requests.post(url, params)


################################
"""Alternate version follows!"""
################################


def fetch_document_ids(requested_id):
    url = 'http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
    params = {'tool': 'IDConverter',
              'email': 'toph.allen@gmail.com',
              'format': 'json',
              'ids': requested_id}
    r = requests.post(url, params)
    ids = r.json()['records'][0]

    try:
        numeric_portion = sub(r'[A-Za-z]', '', ids['pmcid'])
        identifier_base = 'oai:pubmedcentral.nih.gov:'
        ids['oaiid'] = identifier_base + numeric_portion
    except AttributeError:
        print("No PMCID found. Cannot create OAI identifier.")

    return ids


class AlternativePMCXMLDownloader():
    """Downloader for PMC Open Access Subset XML files.
    This one the fetch_document_ids function.
    It stores all document IDs in a dict: self.ids['doi']"""

    # Get all available IDs for this document.
    def __init__(self, requested_id):
        self.ids = fetch_document_ids(requested_id)
        r = self.__request_xml_from_oai(self.ids['oaiid'])
        self.text = r.text

    # Use the OAIID to fetch the document's XML from PMC's OAI service.
    def __request_xml_from_oai(self, oaiid):
        url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
        params = {'verb': 'GetRecord',
                  'identifier': oaiid,
                  'metadataPrefix': 'pmc'}
        return requests.post(url, params)


def main():
    test_id =  'PMC176546'
    print("Proceeding using test ID {}.".format(test_id))

    # With the first verison.
    foo = PMCXMLDownloader(test_id)
    print(foo.ids.pmcid)
    print(foo.ids.__dict__)
    print(foo.text[0:50])

    # With the alternative version.
    foo = AlternativePMCXMLDownloader(test_id)
    print(foo.ids['pmcid'])
    print(foo.ids)
    print(foo.text[0:50])


if __name__ == '__main__':
    main()