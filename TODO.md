# TODO.md

The goal of this project is to recreate the PubCrawler toponym extractor, but using Annie's `geoname_annotator()`. Benefits of this include:

- More robust Python code
- Better springboard for future features

## Broad Goal

The goal with PubCrawler is to go from a collection of text documents (specifically, the PubMed Central Open Access Subset) to a spatial layer representing the aggregated density of toponyms in those documents.

Another step I took to make that layer appropriate for use in my modeling framework is fitting a sub-model with the weighted publication metric as its outcome, and then running that model's `predict()` function over all grid cells used in the Hotspots model.

In the case of the Hotspots II paper, which is my immediate concern, I also want to devise a reasonable way of subsetting articles about infectious disease (in the terminology of a common keyword ontology, "communicable disease").

To address some of the reviewers' concerns, I also want to compute some metrics to describe the layer, and run a comparison against a gold standard of human-extracted locations.

## Detailed Goals

### Annie

- Refactor Annie's `geoname_annotator()` slightly — at least so that it can return *all* matched Geonames, and feature vectors, before the stepwise culling process.

### Subsetting by Topic

I will likely do this either by doing full-text searches for terms related to infectious disease, or with the `<kwd>` tag in the XML papers.

For the full-text search case, I would probably search for publications containing "infectious" of "communicable" (stemmed).

For the `<kwd>` case, I would want to search for all terms subsidiary to "communicable disease" in the MeSH ontology (Medical Subject Headings).

The latter approach may be more robust, except for inconsistent application of tagging across articles. A more robust approach here would be to train an RNN classifier on tags using tagged articles, then to apply that across *all* articles, and then search on those tags.