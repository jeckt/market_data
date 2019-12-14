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

    # NOTE(steve): this allows the scrape equity data to accept
    # both datetime and date objects. It only needs to the date.
    @staticmethod
    def _normalise_datetime(date):
        try:
            return date.date()
        except AttributeError:
            return date

    @staticmethod
    def _get_web_page(ticker):
        url = r'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}'
        req = urllib.request.Request(url.replace('{ticker}', ticker))
        with urllib.request.urlopen(req) as response:
            page = response.read().decode('utf-8')

        return page

    @staticmethod
    def _get_hist_price_data_table(page, ticker):
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

            return data_table
        except:
            raise InvalidTickerError(ticker)

    def scrape_equity_data(self, ticker, date):
        date_only = Scraper._normalise_datetime(date)
        page = Scraper._get_web_page(ticker)
        data_table = Scraper._get_hist_price_data_table(page, ticker)

        for row in data_table.children:
            values = [col.next_element.text for col in
                      row.children if col.find('span')]

            dt = datetime.datetime.strptime(values[0], '%b %d, %Y')
            values[0] = dt.date()
            if values[0] == date_only:
                d = EquityData(*(v.replace(',', '') for v in values[1:]))
                return d

        raise InvalidDateError(f'{ticker}: {date}')

    def scrape_eq_multiple_dates(self, ticker, date_list):
        if date_list is None or len(date_list) == 0:
            raise EmptyDateListError(ticker)

        clean_date_list = [Scraper._normalise_datetime(dt) for dt in date_list]
        page = Scraper._get_web_page(ticker)
        data_table = Scraper._get_hist_price_data_table(page, ticker)

        data = {}
        for row in data_table.children:
            values = [col.next_element.text for col in
                      row.children if col.find('span')]

            dt = datetime.datetime.strptime(values[0], '%b %d, %Y')
            values[0] = dt.date()
            if values[0] in clean_date_list:
                d = EquityData(*(v.replace(',', '') for v in values[1:]))
                data[values[0]] = (values[0], d)

            if len(data) == len(date_list):
                break

        # NOTE(steve): we need to order the data based on the
        # order provided in the input date list
        ordered_data = []
        errors = []
        for date in clean_date_list:
            if date in data:
                ordered_data.append(data[date])
            else:
                errors.append(InvalidDateError(date))

        return ordered_data, errors

class InvalidSourceError(Exception):
    pass
