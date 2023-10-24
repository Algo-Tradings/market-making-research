import ccxt.async_support as ccxtpro
import asyncio
import pandas as pd


class AsyncConnection:
    """Class for interacting with exchanges."""
    def __init__(self):
        self.exchanges = list()
        self.all_markets = dict()
        self.type = list()
        self.dataframe = pd.DataFrame()

    @staticmethod
    def __get_exchange(exchange_name):
        """Returns an exchange object from ccxt."""
        return getattr(ccxtpro, exchange_name)()

    def add_exchanges(self, type=('spot', 'future', 'swap'), blacklist=(), whitelist=ccxtpro.exchanges):
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
        print('Loading all markets...')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__markets_loop(loop))
        print('Done loading all markets...')

    async def __markets_loop(self, loop):

        max_concurrency = 10
        tasks = set()

        for exchange in self.exchanges:
            if len(tasks) >= max_concurrency:
                _done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks.add(loop.create_task(self.__load_markets(exchange)))

        await asyncio.wait(tasks)

    async def __load_markets(self, exchange):
        """Loads the markets for all exchanges."""
        try:
            market = await exchange.load_markets()
            self.all_markets[exchange.name.lower()] = market
            print('Done loading markets for', exchange.name)

        except Exception as e:
            print(f"Failed to load markets for {exchange.name}")

