import datetime
import urllib.request
from bs4 import BeautifulSoup

from market_data.data import EquityData, EmptyDateListError
from market_data.data import InvalidTickerError, InvalidDateError

class Scraper:

    def __init__(self, source):
        if not source == 'yahoo':
            raise InvalidSourceError(source)
        self.source = source

    def scrape_equity_data(self, ticker, date):
        # NOTE(steve): this allows the scrape equity data to accept
        # both datetime and date objects. It only needs to the date.
        try:
            date_only = date.date()
        except AttributeError:
            date_only = date

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

                dt = datetime.datetime.strptime(values[0], '%b %d, %Y')
                values[0] = dt.date()
                if values[0] == date_only:
                    d = EquityData(*(v.replace(',', '') for v in values[1:]))
                    return d
        except:
            raise InvalidTickerError(ticker)

        raise InvalidDateError(f'{ticker}: {date}')

    def scrape_eq_multiple_dates(self, ticker, date_list):
        if date_list is None or len(date_list) == 0:
            raise EmptyDateListError(ticker)

        res = self.scrape_equity_data(ticker, date_list[0])
        return [(date_list[0], res)], None

        raise InvalidTickerError(ticker)

class InvalidSourceError(Exception):
    pass
