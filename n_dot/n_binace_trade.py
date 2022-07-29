from binance.spot import Spot
from binance.client import Client

import numpy as np
import pandas as pd


class n_binace_trade:

    def __init__(self, log, s, tools):
        self.log = log
        self.s = s
        self.tools = tools
        self.api_key = "DAqss9T987L0ruIbVEW9rBEFDD2sKxEKBvpvDVUJfdjijzqPqBgD8semkNF2I5Ul"
        self.api_secret = "3C1203CjVU3J0djfqG62QUSA2sFJJwWnHAmd7gd7t87OoOJJbx7NCnFV7PXx4Wpk"
        self.client_spot = Spot(key=self.api_key, secret=self.api_secret)
        self.client_rest = Client(self.api_key, self.api_secret)
        self.alt_symbols = []

    def print_account(self):
        print(self.client_spot.account())

    def print_system_status(self):
        print(self.client_rest.get_system_status())

    def get_historical_trade(self):
        print(self.client_rest.get_historical_trades(symbol='BNBBTC'))

    def get_klines(self, symbol, from_dt, to_dt):
        try:
            # print("indul")
            klines = self.client_rest.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, from_dt, to_dt, limit=1000)
            # print(klines[:100])
        except Exception as e:
            self.log("Binance exception: " + symbol + " - "
                     + self.tools.unixdt_to_dbdt(from_dt)
                     + " - "
                     + self.tools.unixdt_to_dbdt(to_dt))
            self.log(str(e))
            i_df = pd.DataFrame(None)
        else:
            i_df = pd.DataFrame(klines, columns=('Open Time',
                                                 'Open',
                                                 'High',
                                                 'Low',
                                                 'Close',
                                                 'Volume',
                                                 'Close time',
                                                 'Quote asset volume',
                                                 'Number of trades',
                                                 'Taker buy base asset volume',
                                                 'Taker buy quote asset volume',
                                                 'Ignore'))

            i_df = i_df[['Open Time',
                         'Open',
                         'High',
                         'Low',
                         'Close',
                         'Volume']]
            i_df = i_df.rename(columns={"Open Time": "Date"},
                               errors="ignore")

            i_df['Date'] = i_df['Date'].astype(np.int64)
            i_df['Date'] = i_df['Date'] / 1000
            i_df['Date'] = i_df['Date'].astype(int)
            i_df['t'] = i_df['Date']

            i_df['Open'] = i_df['Open'].astype(float)
            i_df['High'] = i_df['High'].astype(float)
            i_df['Low'] = i_df['Low'].astype(float)
            i_df['Close'] = i_df['Close'].astype(float)
            i_df['Volume'] = i_df['Volume'].astype(float)

            i_df['Date'] = pd.to_datetime(i_df.Date, unit='s')
            i_df['ohlc4'] = round(((i_df['Open'] + i_df['High'] + i_df['Low'] + i_df['Close']) / 4), 8)

        # print("-" * 80)
        # print(i_df.T)
        # print("-" * 80)
        return i_df

    def get_alt_symbols(self):
        exchange_info = self.client_rest.get_exchange_info()
        for s in exchange_info['symbols']:
            self.alt_symbols.append(s['symbol'])
        return self.alt_symbols


if __name__ == "__main__":
    b_trade = n_binace_trade()
    # b_trade.print_account()
    # b_trade.print_system_status()
    # b_trade.get_historical_trade()
    b_trade.get_klines()

