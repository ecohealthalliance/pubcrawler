from bs4 import BeautifulSoup
import lxml
from datetime import date

"""
This class provides methods for dealing with journal articles stored as
XML documents using the NLM's Journal Article Tag Suite.

Instantiate by passing the contents of an article's XML as a string.
"""


class Article:
    def __init__(self, xml):
        self.xml = xml
        self.soup = BeautifulSoup(self.xml, "lxml-xml")
        # self._id = article_dict['_id']

    def pub_ids(self):
        pub_ids = {}
        for row in self.soup.front.find_all("article-id"):
            try:
                pub_id_type = row["pub-id-type"]
                pub_id = row.get_text()
                pub_ids[pub_id_type] = pub_id
            except:
                print("Could not find pub_ids for document.")
        return pub_ids

    def pub_dates(self):
        pub_dates = {}
        for row in self.soup.front.find_all("pub-date"):
            pub_type = row["pub-type"]
            year = int(row.year.get_text()) if row.year is not None else 1
            month = int(row.month.get_text()) if row.month is not None else 1
            day = int(row.day.get_text()) if row.day is not None else 1
            pub_dates[pub_type] = date(year, month, day)
        return pub_dates

    def article_title(self):
        if self.soup.front.find("article-title") is not None:
            article_title = self.soup.front.find("article-title").get_text()
        else:
            article_title = None
        return article_title

    def journal_title(self):
        if self.soup.front.find("journal-title") is not None:
            journal_title = self.soup.front.find("journal-title").get_text()
        else:
            journal_title = None
        return journal_title

    """
    The keywords method returns a list of keyword tags in the article. By
    default, it is restricted to keywords in the <front> element, but the
    "containing_tag" argument can be passed "" to search all. In the test set
    of 1000 articles, only 1 had keywords not in front matter. 503 had any
    keywords at.
    """

    def keywords(self, from_tag="front"):
        keyword_tags = self.soup.find(from_tag).find_all("kwd")
        keywords = []
        for tag in keyword_tags:
            keywords.append(tag.get_text())
        return keywords

    def article_type(self):
        article_tag = self.soup.find("article")
        if article_tag is not None:
            article_type = article_tag.get("article-type")
        else:
            article_type = None
        return article_type

    def extract_text(self, from_tag=None, include_tables=False):
        if from_tag is None:
            from_tag = "body" if self.soup.body else "article"
        strings = [string for string in self.soup.find(from_tag).strings]
        text = ""

        last_tag_name = ""
        last_parents = []
        last_parent_names = []
        last_depth = 0

        for i, string in enumerate(strings):
            tag_name = string.parent.name
            parents = list(string.parents)
            parent_names = [parent.name for parent in parents]
            depth = len(parents)
            if string == "\n":
                continue
            elif "table-wrap" in parent_names:
                if not include_tables:
                    if "table-wrap" not in last_parent_names:
                        text += "\n\n[Omitted Table: '" + string.strip(",.") + "']\n\n"\
                            if "label" in parent_names else "\n\n[Omitted Table]\n\n"

                else:
                    if tag_name in ["label", "caption"] or last_tag_name == [
                        "label",
                        "caption",
                    ]:
                        text += "\n\n" + string
                    if any(x in ["tr"] for x in parent_names):
                        tr = [parent for parent in parents if parent.name == "tr"]
                        last_tr = [parent for parent in last_parents if parent.name == "tr"]
                        cell = [parent for parent in parents if parent.name in ["th", "td"]]
                        last_cell = [
                            parent for parent in last_parents if parent.name in ["th", "td"]
                        ]
                        # If we're in a new table row, insert a carriage return.
                        if not all(x in last_tr for x in tr):
                            text += "\n" + string
                        # If we're in a new table cell, insert a tab character
                        elif not all(x in last_cell for x in cell):
                            text += "\t" + string
                        else:
                            text += string
            elif "fig" in parent_names:
                fig = [parent for parent in parents if parent.name == "fig"]
                last_fig = [parent for parent in last_parents if parent.name == "fig"]
                if not all(x in last_fig for x in fig):
                    text += "\n\n" + string
                elif "label" in last_parent_names:
                    text += " " + string
                else:
                    text += string
            elif "disp-formula" in parent_names:
                formula = [
                    parent for parent in parents if parent.name == "disp-formula"
                ]
                last_formula = [
                    parent for parent in last_parents if parent.name == "disp-formula"
                ]
                math = [parent for parent in parents if parent.name == "mml:math"]
                last_math = [
                    parent for parent in last_parents if parent.name == "mml:math"
                ]
                mrow = [parent for parent in parents if parent.name == "mml:mrow"]
                last_mrow = [
                    parent for parent in last_parents if parent.name == "mml:mrow"
                ]
                # If we're in a new formula, mml:math, or mml:mrow, insert new lines.
                if not all(x in last_formula for x in formula):
                    text += "\n\n" + string
                elif not all(x in last_math for x in math):
                    text += "\n" + string
                elif not all(x in last_mrow for x in mrow):
                    text += "\n" + string
                else:
                    text += string
            elif "sup" in parent_names:
                # We have to peek at next parents to do this right.
                next_parents = list(strings[(i + 1) % len(strings)].parents)
                next_parent_names = [parent.name for parent in next_parents]
                if "xref" in parent_names:
                    if "sup" not in last_parent_names:
                        text += " ["
                    text += string
                    if "sup" not in next_parent_names:
                        text += "]"
                elif "sup" not in last_parent_names:
                    text += "^" + string
                else:
                    text += string
            elif "sub" in parent_names and "sub" not in last_parent_names:
                text += "_" + string
            elif any(x in ["p", "title"] for x in parent_names):
                par = [parent for parent in parents if parent.name in ["p", "title"]]
                last_par = [
                    parent for parent in last_parents if parent.name in ["p", "title"]
                ]
                if not all(x in last_par for x in par):
                    # Add more whitespace before titles
                    text += "\n\n" + string if tag_name == "p" else "\n\n\n" + string
                else:
                    text += string
            elif depth == last_depth or tag_name == last_tag_name:
                text += "\n\n" + string
            else:
                text += string

            last_tag_name = tag_name
            last_parents = parents
            last_parent_names = parent_names
            last_depth = depth

        return text
