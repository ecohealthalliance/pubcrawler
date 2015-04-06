import requests

from bs4 import BeautifulSoup

# Playing with the OA service

paper_url = 'http://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC13901'


r = requests.get(paper_url)



# BeautifulSoup(markup, ["lxml", "xml"]) BeautifulSoup(markup, "xml")

s = BeautifulSoup(r.text, 'xml')

nxml_url = s.find('link', format='tgz')['href']


# Trying the OAI service

def make_oai_identifier(pmcid):
    from re import sub
    numeric_portion = sub(r'[A-Za-z]', '', pmcid)
    identifier_base = 'oai:pubmedcentral.nih.gov:'
    return identifier_base + numeric_portion


def get_xml_from_oai(pmcid):
    import requests
    oai_identifier = make_oai_identifier(pmcid)
    url = 'http://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?'
    params = {'verb': 'GetRecord',
              'identifier': oai_identifier,
              'metadataPrefix': 'pmc'}
    return requests.post(url, params)


pmcid = 'PMC13901'

r = get_xml_from_oai(pmcid)
r.encoding = 'utf-8-sig'

s = BeautifulSoup(r.text, 'xml')


requested_id = 'PMC13901'