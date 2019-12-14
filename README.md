A simple application that collects daily financial market data
and allows for retrieval from other applications via an exposed
API.

TO DO
=====

* Update multiple dates for a single security - less scraper calls.
* Create class to deal with passing time series data as opposed to list of tuples
* Create versioning for application. Ready for first release
* Document code
* Release notes
* Deployment (pypy wheel???)
* User guide

Features & Bugs

* Remove securities
* Formatting of equity data output in CLI
* Handle 503 Service Unavailable errors in update market data
