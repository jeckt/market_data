A simple application that collects daily financial market data
and allows for retrieval from other applications via an exposed
API.

TO DO
=====

* Create class to deal with passing time series data as opposed to list of tuples
* Create versioning for application. Ready for first release
* Document code
* Release notes
* Deployment (pypy wheel???)
* User guide

Features & Bugs

* FGG.ax ticker is only collecting data for one date
* Remove securities
* CLI data output - reduce number of dates shown for readability.
* Handle 503 Service Unavailable errors in update market data (rare bug - happened once)
