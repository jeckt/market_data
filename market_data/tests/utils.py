from decimal import Decimal
from market_data.data import EquityData

def get_expected_equity_data():
    expected_data = EquityData()
    expected_data.open = Decimal('1898.00')
    expected_data.high = Decimal('1903.79')
    expected_data.low = Decimal('1856.00')
    expected_data.close = Decimal('1889.98')
    expected_data.adj_close = Decimal('1889.98')
    expected_data.volume = int(5718000)
    return expected_data


