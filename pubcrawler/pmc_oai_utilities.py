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


class PMCXMLDownloader():
    """Class containing methods for PMC Open Access Subset XML
    files. This one contains functions as staticmethods.
    It stores all document IDs in a dict: self.ids['doi']"""

    @staticmethod
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

    @staticmethod
    # Get all available IDs for this document.
    def is_oaiid(requested_id):
        if str(requested_id[0:26]) == 'oai:pubmedcentral.nih.gov:':
            return True
        else:
            return False

    @staticmethod
    def get_record(requested_id):
        if PMCXMLDownloader.is_oaiid(requested_id):
            oaiid = requested_id
        else:
            oaiid = PMCXMLDownloader.fetch_document_ids(requested_id)['oaiid']

        #OR
        # oaiid = PMCXMLDownloader.fetch_document_ids(requested_id)['oaiid']

        url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
        params = {'verb': 'GetRecord',
                  'identifier': oaiid,
                  'metadataPrefix': 'pmc'}

        record = requests.post(url, params)

        return record.text


def main():
    test_id =  'PMC176546'
    print("Proceeding using test ID {}.".format(test_id))
    print(PMCXMLDownloader.get_record(test_id))

    # With the first verison.


if __name__ == '__main__':
    main()