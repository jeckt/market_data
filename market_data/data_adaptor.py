import os
import json

class DataAdaptor:

    test_database = 'testdb.txt'

    @classmethod
    def create_test_database(cls):
        if os.path.isfile(cls.test_database):
            raise DatabaseExistsError(cls.test_database)

        with open(cls.test_database, 'w') as db:
            import json
            json.dump(list(), db)

    @classmethod
    def delete_test_database(cls):
        if not os.path.isfile(cls.test_database):
            raise DatabaseNotFoundError(cls.test_database)

        os.remove(cls.test_database)

class DatabaseExistsError(Exception):
    pass

class DatabaseNotFoundError(Exception):
    pass
