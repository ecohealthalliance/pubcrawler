from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import future
import builtins
import past
import six

from builtins import int
from builtins import dict # for key in dict.values().
from builtins import range # for i in range(10**8)
from builtins import map # list(map(f, myoldlist))
    # Alternatively from future.utils import lmap

from future.utils import viewitems # for (key, value) viewitems(dict).

from io import open

# Playing with the OA service

paper_url = 'http://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC13901'

import requests
r = requests.get(paper_url)


from bs4 import BeautifulSoup
# BeautifulSoup(markup, ["lxml", "xml"]) BeautifulSoup(markup, "xml")

s = BeautifulSoup(r.text, 'xml')

nxml_url = s.find('link', format='tgz')['href']


# Trying the OAI service

pmcid = 'PMC13901'

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

t = r.text.encode('utf-8-sig', 'replace') # These lines should remove the BOM characters.
t = t.decode('utf-8-sig', 'replace')

s = BeautifulSoup(t, 'xml')
s = BeautifulSoup(t, 'xml', from_encoding='utf-8')

from bs4 import UnicodeDammit
dammit = UnicodeDammit(t, 'utf-8')
s = BeautifulSoup(dammit.unicode_markup)

# Things to try:
# 1. Pass it in as ascii, because that's what lxml wants.
# 2. Try manually doing something with lxml.

# This works. -.- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



from bs4 import BeautifulSoup
s = BeautifulSoup(r.text, 'xml', from_encoding='utf-8')

r.text.encode('ascii', 'ignore')

r.text.encode()
s = BeautifulSoup(r.text.encode('utf-8', 'ignore'), 'xml')

from bs4 import UnicodeDammit
dammit = UnicodeDammit(r.text, 'utf-8')