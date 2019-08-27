import datetime

class Scraper:

    def __init__(self, source):
        if not source == 'yahoo':
            raise InvalidSourceError(source)
        self.source = source

    def scrape_equity_data(self, ticker, date):
        return EquityData()

class EquityData:
    pass

class InvalidSourceError(Exception):
    pass
