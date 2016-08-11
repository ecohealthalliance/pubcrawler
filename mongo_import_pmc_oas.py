#!/usr/bin/env python
from ftplib import FTP
import tarfile
import os






if __name__ == '__main__':

    filenames = [] # Create a list of filenames.
    for x in ["A-B", "C-H", "I-N", "O-Z"]:
        filenames.append("articles.{}.tar.gz".format(x))

    # filenames = [] # Create a list of filenames.
    # for x in ["A-B"]:
    #     filenames.append("articles.{}.tar.gz".format(x))

    # Log into FTP server; login; change directory.
    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    ftp.cwd('pub/pmc')

    for filename in filenames:
        filename = "articles.{}.tar.gz".format(x)
        localfile = open(filename, 'wb')
        ftp.retrbinary(cmd='RETR {}'.format(filename), callback=localfile.write)

    ftp.close()

    for tar in 
        tar = tarfile.open("sample.tar.gz")
        tar.extractall()
        tar.close()