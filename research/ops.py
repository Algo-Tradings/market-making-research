import pandas as pd
# pd.set_option('display.float_format', lambda x: '%.8f' % x)
pd.set_option('display.precision', 9)


class Operations:
    def __init__(self, prices):
        self.__original_df = prices.dataframe.astype(float)
        self.cleaned_df = pd.DataFrame()
        self.spreaded_df = pd.DataFrame()
        self.usd_volume_df = pd.DataFrame()

    def clean_dataframe(self):
        """Cleans the dataframe."""
        df = self.__original_df.dropna()
        self.cleaned_df = df[(df != 0.0).all(axis=1)]
        pd.options.mode.chained_assignment = None
        self.cleaned_df['baseVolume24h'] = self.cleaned_df['baseVolume24h'].apply("{:.0f}".format).astype('int64')
        pd.options.mode.chained_assignment = 'warn'

    def get_by_bid_ask_spread(self, min_pct_spread):
        """Calculates the bid ask spread for all exchanges. Filtering by min spread percentage."""
        print('Calculating bid ask spread...')
        self.cleaned_df['spread'] = ((self.cleaned_df['ask'] - self.cleaned_df['bid']
                                      ) / self.cleaned_df['bid'] * 100).astype(float).round(2)

        self.spreaded_df = self.cleaned_df[self.cleaned_df['spread'] > min_pct_spread]
        print('Done calculating bid ask spread...')

    def get_usd_volume(self, usd_24h):
        """Calculates the USD volume for all exchanges. Filtering by min volume."""
        pd.options.mode.chained_assignment = None
        self.spreaded_df['usd_volume24h'] = self.spreaded_df.apply(self.__calculate_usd_volume, axis=1).round(2)
        pd.options.mode.chained_assignment = 'warn'
        self.usd_volume_df = self.spreaded_df[self.spreaded_df['usd_volume24h'] > usd_24h]

    def __calculate_usd_volume(self, row):
        """Calculates the USD volume for a row."""
        try:
            exchange = row.name[0]
            symbol = row.name[1]
            coin = symbol.split("/")[0]
            stablecoin = symbol.split("/")[1]
            base_volume = row['baseVolume24h']
            last_price = row['last']

            if 'USD' in symbol.upper():
                return base_volume * last_price

            elif (exchange, f'{coin}/USDT') in self.__original_df.index:
                return base_volume * self.__get_usd_price(exchange, coin)

            elif (exchange, f'{coin}/USD') in self.__original_df.index:
                return base_volume * self.__get_usd_price(exchange, coin, usd='USD')

            elif (exchange, f'{stablecoin}/USDT') in self.__original_df.index:
                return base_volume * last_price / self.__get_stablecoin_price(exchange, stablecoin)

            elif (exchange, f'{stablecoin}/USD') in self.__original_df.index:
                return base_volume * last_price / self.__get_stablecoin_price(exchange, stablecoin, usd='USD')

            else:
                print(f"Failed to convert {symbol} to USD")
                return 0.0

        except Exception as e:
            print(f"Failed to convert {symbol} to USD from {exchange}")
            # print(e)
            return 0.0

    def __get_usd_price(self, exchange, coin, usd='USDT'):
        """Converts the volume to USDT."""
        return self.__original_df.loc[(exchange, f'{coin}/{usd}'), 'last']

    def __get_stablecoin_price(self, exchange, stablecoin, usd='USDT'):
        """Converts the volume to USDT."""
        return self.__original_df.loc[(exchange, f'{stablecoin}/{usd}'), 'last']
