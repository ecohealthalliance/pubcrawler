#!/usr/bin/env python

from ftplib import FTP

# Log into FTP server; login; change directory.
ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login()
ftp.cwd('pub/pmc')

for x in ["A-B", "C-H", "I-N", "O-Z"]:
    filename = "articles.{}.tar.gz".format(x)
    localfile = open(filename, 'wb')
    ftp.retrbinary(cmd='RETR {}'.format(filename), callback=localfile.write)

ftp.close()