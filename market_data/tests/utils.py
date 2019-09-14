import json
import datetime
from decimal import Decimal
from market_data.data import EquityData

def load_test_data():
    with open('market_data/tests/test_data.json', 'r') as db:
        test_data = json.load(db)
    return test_data

def get_test_data(test_data, ticker, dt):
    data = test_data[ticker]
    date_string = dt.strftime('%d-%b-%Y')
    equity_data = EquityData(
        open=data[date_string]["open"],
        high=data[date_string]["high"],
        low=data[date_string]["low"],
        close=data[date_string]["close"],
        adj_close=data[date_string]["adj_close"],
        volume=data[date_string]["volume"]
    )
    return equity_data

def get_expected_equity_data():
    ticker = 'AMZN'
    dt = datetime.datetime(2019, 5, 10)
    expected_data = EquityData()
    expected_data.open = Decimal('1898.00')
    expected_data.high = Decimal('1903.79')
    expected_data.low = Decimal('1856.00')
    expected_data.close = Decimal('1889.98')
    expected_data.adj_close = Decimal('1889.98')
    expected_data.volume = int(5718000)
    return ticker, dt, expected_data
