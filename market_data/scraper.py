import datetime
import urllib.request
from decimal import Decimal

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

    def __init__(self, open=0, high=0, low=0, close=0,
                adj_close=0, volume=0):
        self.open = Decimal(open)
        self.high = Decimal(high)
        self.low = Decimal(low)
        self.close = Decimal(close)
        self.adj_close = Decimal(adj_close)
        self.volume = int(volume)

class InvalidSourceError(Exception):
    pass

class InvalidTickerError(Exception):
    pass
