from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum
import market_data

# NOTE(steve): a factory method to return a type of data adapter based on
# source
def get_adapter(source):
    if source == DataAdapterSource.JSON:
        return market_data.json_data_adapter.JsonDataAdapter
    elif source == DataAdapterSource.SQLITE3:
        return market_data.sqlite3_data_adapter.Sqlite3DataAdapter
    else:
        raise InvalidDataAdapterSourceError(source)

class DataAdapterSource(Enum):
    JSON = 1
    SQLITE3 = 2

class DataAdapter(metaclass=ABCMeta):

    @abstractproperty
    def test_database(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_test_database(cls):
        pass

    @classmethod
    @abstractmethod
    def delete_test_database(cls):
        pass

    @classmethod
    @abstractmethod
    def create_database(cls, database):
        pass

    @classmethod
    @abstractmethod
    def connect(cls, conn_string):
        pass

    @classmethod
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_securities_list(self):
        pass

    @abstractmethod
    def insert_securities(self, securities_to_add):
        pass

    @abstractmethod
    def update_market_data(self, security, equity_data):
        pass

    @abstractmethod
    def get_equity_data(self, security, dt):
        pass

    @abstractmethod
    def get_equity_data_series(self, security):
        """Returns equity data series sorted by date (newest to oldest)"""
        pass

class InvalidDataAdapterSourceError(Exception):
    pass

class DatabaseExistsError(Exception):
    pass

class DatabaseNotFoundError(Exception):
    pass
