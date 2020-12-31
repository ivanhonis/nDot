import finnhub
import pandas as pd


class market_data():
    api_key_finnhubio1 = "bs9c9lvrh5rahoaofmt0"
    finnhub_client = ""

    def __init__(self, log, s, tools):
        self.log = log
        self.s = s
        self.tools = tools
        self.finnhub_client = finnhub.Client(api_key=self.api_key_finnhubio1)
        self.finnhub_client.DEFAULT_TIMEOUT = 100

    def check_finnhub_connection(self, symbol="AAPL"):
        self.log("md-> check_finnhub_connection: " + symbol)
        i_return = False
        try:
            i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, 'D', 1590988249, 1591852249))
        except:
            self.log("Error while connecting to FinnHub.")
            i_return = False
        else:
            if i_df.iloc[0]['s'] == "ok":
                i_return = True
            else:
                i_return = False
        return i_return

    def get_usdhuf(self):
        # self.log("md-> get_usdhuf")
        try:
            i_result = self.finnhub_client.forex_rates(base='USD')
        except:
            self.log("Finnhub exception.")
            i_return = 0
        else:
            i_usd_price = {}
            i_usd_price = i_result["quote"]
            i_return = round(i_usd_price["HUF"], 4)
        return i_return

    def get_stock_candles(self, symbol, resolution, from_dt, to_dt, rename=False):
        self.log("md-> get_stock_candles: " + symbol + " - "
                 + self.tools.unixdt_to_dbdt(from_dt)
                 + " - "
                 + self.tools.unixdt_to_dbdt(to_dt))
        try:
            i_result = self.finnhub_client.technical_indicator(symbol=symbol,
                                                               resolution=resolution,
                                                               _from=from_dt, to=to_dt,
                                                               indicator='rsi',
                                                               indicator_fields={"timeperiod": 3})
        except:
            self.log("Finnhub exception.")
            i_df = pd.DataFrame(None)
        else:
            i_df = pd.DataFrame(i_result)
            # i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, resolution, from_dt, to_dt))
            i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
            # a finnhub idejét Európa/Budapest időre konvertálom
            i_df['datetime'] = i_df['datetime'] + pd.Timedelta(hours=2)
            i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
            i_df['ohlc4'] = round(((i_df['o'] + i_df['h'] + i_df['l'] + i_df['c'])/4), 6)
            i_df = i_df[['datetime', 't', 'o', 'h', 'l', 'c', 'ohlc4', 'v']]
            i_df = i_df.round({'t': 6, 'o': 6, 'h': 6, 'l': 6, 'c': 6, 'ohlc4': 6})
            i_df.set_index('datetime')
            if rename:
                i_df = i_df.rename(columns={"datetime": "Date",
                                            "o": "Open",
                                            "h": "High",
                                            "l": "Low",
                                            "c": "Close",
                                            "v": "Volume"},
                                   errors="raise")
            # return pandas df -> o h c l v t datetime ohcl4
        return i_df

    def company_profile(self, symbol):
        try:
            i_return = self.finnhub_client.company_profile2(symbol=symbol)
        except:
            i_return = {}
            i_return['name'] = symbol
            i_return['description'] = "No data :("
        return i_return

    def news_sentiment(self, symbol):
        return self.finnhub_client.news_sentiment(symbol=symbol)

    def quote(self, symbol):
        return self.finnhub_client.quote(symbol)

    def technical_indicator_rsi(self, symbol, resolution, from_dt, to_dt):
        self.log("md-> technical_indicator_rsi:" + symbol +
                 " - " + self.tools.unixdt_to_dbdt(from_dt) + " - " + self.tools.unixdt_to_dbdt(to_dt))
        i_df = pd.DataFrame(self.finnhub_client.technical_indicator(symbol=symbol,
                                                                    resolution=resolution,
                                                                    _from=from_dt, to=to_dt,
                                                                    indicator='rsi',
                                                                    indicator_fields={"timeperiod": 3}))
        i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
        i_df['datetime'] = i_df['datetime'] + pd.Timedelta(hours=2)
        i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
        i_df = i_df[['datetime', 't', 'rsi']]
        i_df = i_df.round({'rsi': 6})
        i_df.set_index('datetime')
        return i_df
