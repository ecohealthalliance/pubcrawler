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

# What I need to do is make a class "article identifier" and have it initialize
# with a string, and it has functions to guess that type of string and methods
# to produce other identifiers using lookup. Or, even better, when it
# initializes, it cross-references them. Maybe using the web service. Or it
# guesses the ID type and uses the web service to look up the XML article
# information. If I can guess the ID type, why even bother with more. :)

def make_oai_id(pmcid):
    numeric_portion = sub(r'[A-Za-z]', '', pmcid)
    identifier_base = 'oai:pubmedcentral.nih.gov:'
    return identifier_base + numeric_portion

def get_xml_from_oai(oai_id):
    url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
    params = {'verb': 'GetRecord',
              'identifier': oai_identifier,
              'metadataPrefix': 'pmc'}
    return requests.post(url, params)