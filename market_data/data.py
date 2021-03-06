from decimal import Decimal

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

class InvalidTickerError(Exception):
    pass

class InvalidDateError(Exception):
    pass

class EmptyDateListError(Exception):
    pass

# TODO(steve): should error be here or market_data.py???
class NoDataError(Exception):
    pass
