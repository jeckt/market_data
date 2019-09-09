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
    def _create_database(cls, database):
        with open(database, 'w') as db:
            import json
            json.dump(TextDataModel().to_dict(), db)

    @classmethod
    def connect(cls, conn_string=None):
        if conn_string is None:
            conn_string = cls.prod_database
            if not os.path.isfile(conn_string):
                cls._create_database(conn_string)

        if not os.path.isfile(conn_string):
            raise DatabaseNotFoundError(conn_string)

        return cls(conn_string)

    def __init__(self, conn_string):
        self.conn_string = conn_string

    # NOTE(steve): this method will close the connection
    # to the database. For the json implementation
    # nothing needs to be done here.
    def close(self):
        pass

    def get_securities_list(self):
        with open(self.conn_string, 'r') as db:
            data = TextDataModel.from_dict(json.load(db))
            return data.securities

    # TODO(steve): we need to check with this creates 
    # a race condition?!?! I'm confident that it does
    def insert_securities(self, securities_to_add):
        securities = self.get_securities_list()
        securities += securities_to_add
        with open(self.conn_string, 'w') as db:
            data = TextDataModel()
            data.securities = list(set(securities))
            json.dump(data.to_dict(), db)

    def update_market_data(self, security, equity_data_series):
        securities = self.get_securities_list()
        if security in securities:
            with open(self.conn_string, 'w') as db:
                data = TextDataModel()
                data.securities = list(set(securities))
                data.date = equity_data_series[0]
                data.equity_data = equity_data_series[1]
                json.dump(data.to_dict(), db)
        else:
            raise InvalidTickerError

    def get_equity_data(self, security, dt):
        if security in self.get_securities_list():
            with open(self.conn_string, 'r') as db:
                data = TextDataModel.from_dict(json.load(db))
                if data.date == dt:
                    return data.equity_data
                else:
                    raise InvalidDateError(dt)
        else:
            raise InvalidTickerError(security)

class TextDataModel:

    def __init__(self):
        self.securities = list()
        self.date = None
        self.equity_data = EquityData()

    @classmethod
    def from_dict(cls, dict_data):
        data = cls()

        data.securities = dict_data['securities']
        data.equity_data = EquityData.from_dict(dict_data['equity_data'])
        if 'date' in dict_data:
            data.date = datetime.datetime.strptime(dict_data['date'],
                                                   '%d-%b-%Y')

        return data

    def to_dict(self):
        d = {}

        d['securities'] = self.securities
        d['equity_data'] = self.equity_data.to_dict()
        if self.date:
            d['date'] = self.date.strftime('%d-%b-%Y')

        return d

    def __eq__(self, other):
        return (self.securities == other.securities and
                self.equity_data == other.equity_data and
                self.date == other.date)

class DatabaseExistsError(Exception):
    pass

class DatabaseNotFoundError(Exception):
    pass
