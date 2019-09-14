import os
import json
import datetime

from market_data.data import EquityData, InvalidTickerError, InvalidDateError

# TODO(steve): should we turn the DataAdapter into a 
# abstract class to provide an interface for the rest
# of the app??
class DataAdapter:

    test_database = 'testdb.txt'
    prod_database = 'productiondb.txt'

    @classmethod
    def create_test_database(cls):
        if os.path.isfile(cls.test_database):
            raise DatabaseExistsError(cls.test_database)

        cls._create_database(cls.test_database)

    @classmethod
    def delete_test_database(cls):
        if not os.path.isfile(cls.test_database):
            raise DatabaseNotFoundError(cls.test_database)

        os.remove(cls.test_database)

    @classmethod
    def connect(cls, conn_string=None):
        if conn_string is None:
            conn_string = cls.prod_database
            if not os.path.isfile(conn_string):
                cls._create_database(conn_string)

        if not os.path.isfile(conn_string):
            raise DatabaseNotFoundError(conn_string)

        return cls(conn_string)

    @classmethod
    def _create_database(cls, database):
        cls._save_data(database, TextDataModel())

    @classmethod
    def _load_data(cls, conn_string):
        with open(conn_string, 'r') as db:
            data = json.load(db, object_hook=TextDataModel.json_decoder)
        return data

    @classmethod
    def _save_data(cls, conn_string, data):
        with open(conn_string, 'w') as db:
            json.dump(data, db, default=TextDataModel.json_encoder)

    def __init__(self, conn_string):
        self.conn_string = conn_string

    # NOTE(steve): this method will close the connection
    # to the database. For the json implementation
    # nothing needs to be done here.
    def close(self):
        pass

    def get_securities_list(self):
        return DataAdapter._load_data(self.conn_string).securities

    # TODO(steve): we need to check with this creates 
    # a race condition?!?! I'm confident that it does
    def insert_securities(self, securities_to_add):
        data = DataAdapter._load_data(self.conn_string)
        data.securities = list(set(data.securities + securities_to_add))
        for sec in securities_to_add:
            if not sec in data.equity_data:
                data.equity_data[sec] = {}

        DataAdapter._save_data(self.conn_string, data)

    def update_market_data(self, security, equity_data):
        securities = self.get_securities_list()
        if security in securities:
            data = DataAdapter._load_data(self.conn_string)
            if security not in data.equity_data:
                data.equity_data[security] = {}

            dt_key = equity_data[0].strftime('%d-%b-%Y')
            data.equity_data[security][dt_key] = equity_data[1]

            DataAdapter._save_data(self.conn_string, data)
        else:
            raise InvalidTickerError

    def get_equity_data(self, security, dt):
        if security in self.get_securities_list():
            data = DataAdapter._load_data(self.conn_string)

            dt_key = dt.strftime('%d-%b-%Y')
            if dt_key in data.equity_data[security]:
                return data.equity_data[security][dt_key]
            else:
                raise InvalidDateError(dt)
        else:
            raise InvalidTickerError(security)

class TextDataModel:

    def __init__(self):
        self.securities = list()
        self.equity_data = {}

    @classmethod
    def json_encoder(cls, o):
        if isinstance(o, TextDataModel):
            return o._to_dict()
        else:
            raise TypeError(f'{repr(o)} is not JSON serialized')

    @classmethod
    def json_decoder(cls, o):
        try:
            return TextDataModel._from_dict(o)
        except:
            return o

    @classmethod
    def _from_dict(cls, dict_data):
        data = cls()

        data.securities = dict_data['securities']
        data.equity_data = {}
        for sec in data.securities:
            if sec in dict_data:
                data.equity_data[sec] = {}
                for dt, equity_data in dict_data[sec].items():
                    data.equity_data[sec][dt] = EquityData(
                        open=equity_data['open'],
                        high=equity_data['high'],
                        low=equity_data['low'],
                        close=equity_data['close'],
                        adj_close=equity_data['adj_close'],
                        volume=equity_data['volume']
                    )

        return data

    def _to_dict(self):
        d = {}

        d['securities'] = self.securities
        for sec in self.securities:
            if sec in self.equity_data:
                d[sec] = {}
                for dt, equity_data in self.equity_data[sec].items():
                    d[sec][dt] = {
                        'open': str(equity_data.open),
                        'high': str(equity_data.high),
                        'low': str(equity_data.low),
                        'close': str(equity_data.close),
                        'adj_close': str(equity_data.adj_close),
                        'volume': equity_data.volume
                    }

        return d

    def __eq__(self, other):
        return (self.securities == other.securities and
                self.equity_data == other.equity_data)

class DatabaseExistsError(Exception):
    pass

class DatabaseNotFoundError(Exception):
    pass
