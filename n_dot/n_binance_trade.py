# from binance.spot import Spot
import datetime
import time
from datetime import timedelta
from binance.client import Client
import numpy as np
import pandas as pd


class n_binance_trade():

    def __init__(self, log, s, tools):
        self.log = log
        self.s = s
        self.tools = tools
        self.api_key = "DAqss9T987L0ruIbVEW9rBEFDD2sKxEKBvpvDVUJfdjijzqPqBgD8semkNF2I5Ul"
        self.api_secret = "3C1203CjVU3J0djfqG62QUSA2sFJJwWnHAmd7gd7t87OoOJJbx7NCnFV7PXx4Wpk"
        # self.client_spot = Spot(key=self.api_key, secret=self.api_secret)
        self.binance_client = Client(self.api_key, self.api_secret)
        self.exchange_info = []
        self.crypto = self.get_all_symbols()
        self.pai = self.defa_pair_info()

    def defa_pair_info(self):
        pair_info = {}
        for sx in self.exchange_info['symbols']:
            if sx['status'] == 'TRADING' and "MARKET" in sx['orderTypes']:
                base = sx['baseAsset']
                quot = sx['quoteAsset']
                # if base == "USDT" and quot == "TRY":
                filters = {}
                for fx in sx['filters']:
                    filters[fx['filterType']] = fx

                ticksize = float(filters['PRICE_FILTER']['tickSize'])
                step_size = float(filters['LOT_SIZE']['stepSize'])
                min_qty = float(filters['LOT_SIZE']['minQty'])
                market_minqt = float(filters['MARKET_LOT_SIZE']['minQty'])
                market_stepsize = float(filters['MARKET_LOT_SIZE']['stepSize'])
                minnotional = float(filters['MIN_NOTIONAL']['minNotional'])
                avgpricemins = float(filters['MIN_NOTIONAL']['avgPriceMins'])

                # if sx['filters'][0]['filterType'] == 'PRICE_FILTER':
                #     ticksize = float(sx['filters'][0]['tickSize'])
                # else:
                #     print("Filter hiba. PRICE_FILTER")
                #     sys.exit()
                #
                # if sx['filters'][2]['filterType'] == 'LOT_SIZE':
                #     step_size = float(sx['filters'][2]['stepSize'])
                #     min_qty = float(sx['filters'][2]['minQty'])
                # else:
                #     print("Filter hiba. LOT_SIZE")
                #     sys.exit()
                #
                # if sx['filters'][6]['filterType'] == 'MARKET_LOT_SIZE':
                #     market_minqt = float(sx['filters'][6]['minQty'])
                #     market_stepsize = float(sx['filters'][6]['stepSize'])
                # else:
                #     print("Filter hiba. MARKET_LOT_SIZE")
                #     sys.exit()
                #
                # if sx['filters'][3]['filterType'] == 'MIN_NOTIONAL':
                #     minnotional = float(sx['filters'][3]['minNotional'])
                #     avgpricemins = float(sx['filters'][3]['avgPriceMins'])
                # else:
                #     print("Filter hiba. MIN_NOTIONAL")
                #     sys.exit()

                data_both = {'orig_symbol': sx['symbol'],
                             'stepsize': step_size,
                             'minqty': min_qty,
                             'base': base,
                             'quote': quot,
                             'tick_size': ticksize,
                             'market_minqty': market_minqt,
                             'market_stepsize': market_stepsize,
                             'minnotional': minnotional,
                             'avgpricemins': avgpricemins}

                data_sell = data_both.copy()
                data_buy = data_both.copy()
                data_sell['side'] = 'SELL'
                data_sell['symbol_from'] = sx['baseAsset']
                data_sell['symbol_to'] = sx['quoteAsset']
                data_buy['side'] = 'BUY'
                data_buy['symbol_from'] = sx['quoteAsset']
                data_buy['symbol_to'] = sx['baseAsset']

                pair_info[sx['baseAsset'] + sx['quoteAsset']] = data_sell
                pair_info[sx['quoteAsset'] + sx['baseAsset']] = data_buy

        return pair_info

    def get_all_symbols(self):
        self.exchange_info = self.binance_client.get_exchange_info()
        i_all_pairs = []
        for sy in self.exchange_info['symbols']:
            i_all_pairs.append(sy['symbol'])
        return i_all_pairs

    def print_account(self):
        print(self.binance_client.get_account())

    def print_system_status(self):
        print(self.binance_client.get_system_status())

    def get_historical_trade(self):
        print(self.binance_client.get_historical_trades(symbol='BNBBTC'))

    def get_klines(self, symbol, from_dt, to_dt):
        i_df = pd.DataFrame(None)
        klines = []
        # klines = self.binance_client.get_historical_klines(symbol=symbol,
        #                                                    interval=Client.KLINE_INTERVAL_1MINUTE,
        #                                                    start_str=from_dt,
        #                                                    limit=1002)
        # self.binance_client.close_connection()
        # print(len(klines))
        # return klines
        try:
            klines = self.binance_client.get_historical_klines(symbol=symbol,
                                                               interval=Client.KLINE_INTERVAL_1MINUTE,
                                                               start_str=from_dt,
                                                               limit=1002)
            self.binance_client.close_connection()
        except Exception as e:
            print(e)
            # self.log("Binance exception: " + symbol + " - "
            #          + self.tools.unixdt_to_dbdt(from_dt)
            #          + " - "
            #          + self.tools.unixdt_to_dbdt(to_dt))
            # self.log(str(e))
            # i_df = pd.DataFrame(None)
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


if __name__ == "__main__":
    print(int(datetime.datetime.now().timestamp() * 10))
    b_trade = n_binance_trade()
    # b_trade.print_account()
    # print(b_trade.get_all_symbols())
    years = 1
    i_now = datetime.datetime.now() - timedelta(minutes=1001)
    i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
    i_datetime_series = pd.date_range(start=i_now, periods=10, freq='-1000min')
    for i_i in range(len(i_datetime_series) - 1):
        from_dt = i_datetime_series[i_i]
        print(from_dt)
        from_dt = int(datetime.datetime.timestamp(from_dt) * 1000)
        to_dt = i_datetime_series[i_i + 1]
        to_dt = int(datetime.datetime.timestamp(to_dt) * 1000)

        # from_dt = datetime.datetime.strftime(from_dt, '%d %b, %Y')
        # to_dt = datetime.datetime.strftime(to_dt, '%d %b, %Y')
        # print(from_dt, to_dt)
        result = ""
        result = b_trade.get_klines("ETHBTC", from_dt, to_dt).copy()
        print(result)
        # print('  első', datetime.datetime.fromtimestamp(int(result[0][0]) / 1000))
        # print('  utolsó', datetime.datetime.fromtimestamp(int(result[-1][0]) / 1000))
        # for x, r in enumerate(res):
        #     print(x, 'utolsó', datetime.datetime.fromtimestamp(int(r[0]) / 1000))
        #     time.sleep(0.25)
        # time.sleep(2)
        # print('első', datetime.datetime.fromtimestamp(int(res[0][0]) / 1000))
