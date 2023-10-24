import pandas as pd


class SyncPrices:
    """Class for interacting with exchanges."""
    def __init__(self, connection):
        self.conn = connection
        self.bid_ask_volume = dict()
        self.dataframe = pd.DataFrame()

    def load_bid_ask_volume(self):
        """Loads the bid and ask prices for all exchanges."""
        print('Loading bid and ask prices...')

        self.__load_bid_ask_volume()

        self.dataframe = pd.DataFrame(self.__generate_new_frame()).T
        self.dataframe.astype(float)

        print('Done loading bid and ask prices...')

    def __generate_new_frame(self):
        """Generates a new dataframe from the bid_ask_volume dictionary."""
        return {(exchange_name, symbol): prices for exchange_name, ticker in self.bid_ask_volume.items()
                for symbol, prices in ticker.items()}

    def __load_bid_ask_volume(self):
        """Loads the bid and ask prices for all exchanges."""
        [self.__load_tickers(exchange) for exchange in self.conn.exchanges
         if exchange.name.lower() in self.conn.all_markets]

    def __load_tickers(self, exchange):
        """Loads the bid and ask prices for an exchange."""
        self.bid_ask_volume[exchange.name.lower()] = dict()
        tickers = self.__get_tickers(exchange) if exchange.has['fetchTickers'] else \
            self.__get_all_ticker(exchange) if exchange.has['fetchTicker'] else None

        self.__add_tickers(exchange, tickers) if tickers else self.__no_ticker_support(exchange)

    @staticmethod
    def __get_tickers(exchange):
        """Gets all tickers for an exchange."""
        try:
            return exchange.fetch_tickers()
        except Exception as e:
            print(f"Failed to get tickers for {exchange.name}")
            print(e)
            return

    def __get_all_ticker(self, exchange):
        """Gets all ticker for an exchange."""
        self.tickers = dict()
        symbols = [symbol for symbol in self.conn.all_markets[exchange.name.lower()].keys()
                   if self.conn.all_markets[exchange.name.lower()][symbol]['type'] in self.conn.type]

        [self.__get_ticker(exchange, symbol) for symbol in symbols]
        return self.tickers

    def __get_ticker(self, exchange, symbol):
        """Gets a ticker for an exchange."""
        try:
            self.tickers[symbol] = exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"Failed to get ticker for {exchange.name} {symbol}")
            print(e)
            return

    @staticmethod
    def __no_ticker_support(exchange):
        """Handles exchanges that do not support fetching tickers or ticker."""
        print(f"Failed to load bid and ask prices for {exchange.name}")
        print(f"{exchange.name} does not support fetching tickers or ticker.")

    def __add_tickers(self, exchange, tickers):
        """Adds tickers to class variable."""
        [self.__add_ticker(exchange.name.lower(), symbol, ticker) for symbol, ticker in tickers.items()]

    def __add_ticker(self, exchange_name, symbol, ticker):
        """Adds d single symbol to class variable."""
        self.bid_ask_volume[exchange_name][symbol] = {'ask': ticker['ask'],
                                                      'last': ticker['last'],
                                                      'bid': ticker['bid'],
                                                      # quoteVolume is not supported by all exchanges
                                                      'baseVolume24h': ticker['baseVolume']}