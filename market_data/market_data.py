class MarketData:

    init = False

    # NOTE(steve): this method will be used to 
    # initialise all the dependencies before
    # the user can use the application
    # this is where we will throw 
    # dependency errors as well
    def run(self):
        self.init = True

    def get_securities_list(self):
        if not self.init:
            raise NotInitialisedError('Call run method first!')

        return ['AMZN', 'GOOG', 'TLS.AX']

class NotInitialisedError(Exception):
    pass
