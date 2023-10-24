import ccxt
import pandas as pd


class SyncConnection:
    """Class for interacting with exchanges."""
    def __init__(self):

        self.exchanges = list()
        self.all_markets = dict()
        self.type = list()
        self.dataframe = pd.DataFrame()

    @staticmethod
    def __get_exchange(exchange_name):
        """Returns an exchange object from ccxt."""
        return getattr(ccxt, exchange_name)()

    def add_exchanges(self, type=('spot', 'future', 'swap'), blacklist=(), whitelist=ccxt.exchanges):
        """Adds exchanges to the exchanges list.
        :param type: e.g. ('spot', 'future', 'swap')
        :type: tuple['str']

        :param blacklist: e.g. ['alpaca',]
        :type: list['str']

        :param whitelist: e.g. ['binance',]
        :type: list['str']
        """

        self.type = type
        [self.__add_exchange(exchange_name) for exchange_name in whitelist if exchange_name not in blacklist]
        self.dataframe = pd.DataFrame(self.exchanges, columns=['Exchange'])

    def __add_exchange(self, exchange_name):
        """Adds an exchange to the exchanges list."""
        self.exchanges.append(self.__get_exchange(exchange_name))

    def load_markets(self):
        """Loads the markets for all exchanges."""
        print('Loading markets...')
        [self.__load_markets(exchange) for exchange in self.exchanges]
        print('Done loading markets...')

    def __load_markets(self, exchange):
        """Loads the markets for each exchange."""
        try:
            market = exchange.load_markets()
            self.all_markets[exchange.name.lower()] = market

        except Exception as e:
            print(f"Failed to load markets for {exchange.name}")
            # print(e)


