import datetime
import urllib.request

class Scraper:

    def __init__(self, source):
        if not source == 'yahoo':
            raise InvalidSourceError(source)
        self.source = source

    def scrape_equity_data(self, ticker, date):
        url = r'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}'
        req = urllib.request.Request(url.replace('{ticker}', ticker))
        with urllib.request.urlopen(req) as response:
            if response.status == 404:
                raise InvalidTickerError(ticker)

        return EquityData()

class EquityData:
    pass

class InvalidSourceError(Exception):
    pass

class InvalidTickerError(Exception):
    pass
