A simple application that collects daily financial market data
and allows for retrieval from other applications via an exposed
API.

Design Thoughts
===============

* Should the scraper module be abstracted way from the rest of the app and
  accessed as a data source which would allow the app tests to be agnostic to
  the changes in the data source e.g. from web scrape to web API.
