class MarketData:

    init = False

    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    def run(self):
        self.init = True
        self._securities = list()

    def add_security(self, ticker):
        self._securities.append(ticker)

    def get_securities_list(self):
        if not self.init:
            raise NotInitialisedError('Call run method first!')

        return list(self._securities)

class NotInitialisedError(Exception):
    pass
