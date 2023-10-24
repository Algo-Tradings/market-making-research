import pandas as pd
import asyncio
import nest_asyncio

nest_asyncio.apply()


class AsyncPrices:
    """Class for interacting with exchanges."""
    def __init__(self, connection):
        self.conn = connection
        self.bid_ask_volume = dict()
        self.dataframe = pd.DataFrame()

    def load_bid_ask_volume(self):
        """Loads the bid and ask prices for all exchanges."""
        print('Loading prices from all currencies...')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__load_bid_ask_volume(loop))
        # loop.close()

        self.dataframe = pd.DataFrame(self.__generate_new_frame()).T
        self.dataframe.astype(float).round(8)
        pd.options.mode.chained_assignment = None
        self.dataframe['baseVolume24h'] = self.dataframe['baseVolume24h'].apply("{:.0f}".format).astype('int64')
        pd.options.mode.chained_assignment = 'warn'

        print('Done loading prices from all currencies...')

    def __generate_new_frame(self):
        """Generates a new dataframe from the bid_ask_volume dictionary."""
        return {(exchange_name, symbol): prices for exchange_name, ticker in self.bid_ask_volume.items()
                for symbol, prices in ticker.items()}

    async def __load_bid_ask_volume(self, loop):
        """Loads the bid and ask prices for all exchanges."""

        max_concurrency = 10
        tasks = set()

        for exchange in self.conn.exchanges:
            if exchange.name.lower() in self.conn.all_markets:
                if len(tasks) >= max_concurrency:
                    _done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                if exchange.has['fetchTickers']:
                    self.bid_ask_volume[exchange.name.lower()] = dict()
                    tasks.add(loop.create_task(self.__get_tickers(exchange))) \
                        if exchange.name.lower() in self.conn.all_markets else None

                elif exchange.has['fetchTicker']:
                    self.bid_ask_volume[exchange.name.lower()] = dict()
                    self.tickers = dict()
                    symbols = [symbol for symbol in self.conn.all_markets[exchange.name.lower()].keys()
                               if self.conn.all_markets[exchange.name.lower()][symbol]['type'] in self.conn.type]

                    for symbol in symbols:
                        tasks.add(loop.create_task(self.__get_ticker(exchange, symbol))) \
                            if exchange.name.lower() in self.conn.all_markets else None

                    self.__add_tickers(exchange, self.tickers)

                else:
                    self.__no_ticker_support(exchange)

        await asyncio.wait(tasks)

    async def __get_tickers(self, exchange):
        """Gets all tickers for an exchange."""
        try:
            tickers = await exchange.fetch_tickers()
            self.__add_tickers(exchange, tickers)
            # print(f"Done to get tickers from {exchange.name}")

        except Exception as e:
            # print(f"Failed to get tickers for {exchange.name}")
            # print(e)
            return

    async def __get_ticker(self, exchange, symbol):
        """Gets a ticker for an exchange."""
        try:
            self.tickers[symbol] = await exchange.fetch_ticker(symbol)
            # print(f"Done to get ticker from {exchange.name} {symbol}")

        except Exception as e:
            # print(f"Failed to get ticker for {exchange.name} {symbol}")
            # print(e)
            return

    @staticmethod
    def __no_ticker_support(exchange):
        """Handles exchanges that do not support fetching tickers or ticker."""
        # print(f"Failed to load bid and ask prices for {exchange.name}")
        print(f"{exchange.name} does not support fetching tickers or ticker.")

    def __add_tickers(self, exchange, tickers):
        """Adds tickers to class variable."""
        [self.__add_ticker(exchange.name.lower(), symbol, ticker) for symbol, ticker in tickers.items()]
        print(f"Done loading prices from {exchange.name}...")

    def __add_ticker(self, exchange_name, symbol, ticker):
        """Adds d single symbol to class variable."""
        self.bid_ask_volume[exchange_name][symbol] = {'ask': round(ticker['ask'], 9),
                                                      'last': round(ticker['last'], 9),
                                                      'bid': round(ticker['bid'], 9),
                                                      # quoteVolume is not supported by all exchanges
                                                      'baseVolume24h': round(ticker['baseVolume'], 0)}
