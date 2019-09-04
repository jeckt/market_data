import datetime
import urllib.request
from bs4 import BeautifulSoup

from market_data.data import EquityData
from market_data.data import InvalidTickerError, InvalidDateError

class Scraper:

    def __init__(self, source):
        if not source == 'yahoo':
            raise InvalidSourceError(source)
        self.source = source

    def scrape_equity_data(self, ticker, date):
        url = r'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}'
        req = urllib.request.Request(url.replace('{ticker}', ticker))
        with urllib.request.urlopen(req) as response:
            page = response.read().decode('utf-8')

        # NOTE(steve): parse the html page and find the table
        # of historical price data based on table attributes
        # to make it slightly more robust to changes in the webpage
        # NOTE(steve): we use a try/except here to capture any errors in 
        # finding the historical prices table as it hides more of the
        # implementation.
        try:
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
        except:
            raise InvalidTickerError(ticker)

        raise InvalidDateError(f'{ticker}: {date}')

class InvalidSourceError(Exception):
    pass
