class MarketData:

    init = False

    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    def run(self):
        self.init = True
        self._securities = list()

    def _check_initialised(self):
        if not self.init:
            raise NotInitialisedError('Call run method first!')

    def add_security(self, ticker):
        self._check_initialised()
        self._securities.append(ticker)

    def get_securities_list(self):
        self._check_initialised()
        return list(self._securities)

    # NOTE(steve): this method will be used to clean up
    # all the dependency e.g. closing of the database
    # after the app is closed
    def close(self):
        self.init = False

class NotInitialisedError(Exception):
    pass