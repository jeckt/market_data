import datetime
import urllib.request
from decimal import Decimal
from bs4 import BeautifulSoup

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
            page = response.read().decode('utf-8')

        # NOTE(steve): parse the html page and find the table
        # of historical price data based on table attributes
        # to make it slightly more robust to changes in the webpage
        parsed_html = BeautifulSoup(page, features='html.parser')
        data_table = parsed_html.body.find('table',
                            attrs={'data-test':'historical-prices'})
        data_table = data_table.find('tbody')

        for row in data_table.children:
            values = [col.next_element.text for col in
                      row.children if col.find('span')]
            values[0] = datetime.datetime.strptime(values[0], '%b %d, %Y')
            if values[0] == date:
                d = EquityData(*(v.replace(',', '') for v in values[1:]))
                return d

        raise InvalidDateError(f'{ticker}: {date}')

# TODO(steve): make the equity data class more robust
# by disabling the ability for callers to access the
# direct fields stored but must use getters/setters
# so that we can ensure the data type is enforced
# NOTE(steve): maybe it's better to use static typing
# library like mypy??? No? because we need to enforce
# non negative numbers???
class EquityData:

    def __init__(self, open=0, high=0, low=0, close=0,
                adj_close=0, volume=0):
        self.open = Decimal(open)
        self.high = Decimal(high)
        self.low = Decimal(low)
        self.close = Decimal(close)
        self.adj_close = Decimal(adj_close)
        self.volume = int(volume)

    def __eq__(self, other):
        d1 = [self.open, self.high, self.low,
              self.close, self.adj_close, self.volume]
        d2 = [other.open, other.high, other.low,
              other.close, other.adj_close, other.volume]
        results = (v1 == v2 for v1, v2 in zip(d1, d2))
        return all(results)

    def __str__(self):
        s = f'[open={self.open}, '
        s += f'high={self.high}, '
        s += f'low={self.low}, '
        s += f'close={self.close}, '
        s += f'adj_close={self.adj_close}, '
        s += f'volume={self.volume}]'
        return s

class InvalidSourceError(Exception):
    pass

class InvalidTickerError(Exception):
    pass

class InvalidDateError(Exception):
    pass
