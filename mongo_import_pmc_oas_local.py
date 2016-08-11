#!/usr/bin/env python

"""
If run as a script, crawls the directory tree provided as an argument, and imports all .nxml files in that directory into a Mongo collection.

If imported, provides classes for importing a .nxml file into a Mongo collection.
"""

import sys
from pymongo import MongoClient
import time

db = MongoClient()