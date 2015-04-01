#!/usr/bin/env python
"""An annie loader creates an AnnoDoc from a source such as a file or database.
The loader should perform as much annotation as is necessary to preserve parts
of document structure that would otherwise be lost. For example, if there is a
document header, it might be parsed and metadata stored in the AnnoDoc.properties.
If HTML tags are removed, certain tags might be transferred to an AnnoTier.
"""

from annotator.annotator import AnnoDoc
from annotator.loader import Loader

class NXMLFileLoader(Loader):
    """Loader for an NXML file"""

    def load(self, filename, tagset=None):
        """Create an AnnoDoc from an NXML file, with a tier for tags in tagset"""

        if tagset is None:
            tagset = []

        with open(filename, 'r') as f:
            text = f.read()

        doc = AnnoDoc(text)
        html_tag_annotator = HTMLTagAnnotator(tagset=tagset)
        doc.add_tier(html_tag_annotator)

        return doc


class HTMLFileLoader(Loader):
    """Loader for an HTML file"""

    def load(self, filename, tagset=None):
        """Create an AnnoDoc from an HTML file, with a tier for tags in tagset"""

        if tagset is None:
            tagset = []

        with open(filename, 'r') as f:
            text = f.read()

        doc = AnnoDoc(text)
        html_tag_annotator = HTMLTagAnnotator(tagset=tagset)
        doc.add_tier(html_tag_annotator)

        return doc
