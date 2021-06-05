import finnhub
import pandas as pd
# for streaming ---------------------------------------
import threading
from time import sleep, strftime


class market_data:

    api_key_finnhubio1 = "c28o33iad3if6b4c0ong"
    finnhub_client = ""

    def __init__(self, log, s, tools, ndf, stream_last_refresh):
        self.log = log
        self.s = s
        self.tools = tools
        self.stream_last_refresh = stream_last_refresh
        self.ndf = ndf
        self.finnhub_client = finnhub.Client(api_key=self.api_key_finnhubio1)
        self.finnhub_client.DEFAULT_TIMEOUT = 100

        # for straming
        self.stream_is_working = False
        self.stream_thread = ""
        self.stream_break = False
        self.stream_refresh_rate = 60

        self.request_count = 0

    def check_finnhub_connection(self, symbol="AAPL"):
        self.log("md-> check_finnhub_connection: " + symbol)
        try:
            i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, 'D', 1590988249, 1591852249))
        except:
            self.log("Error while connecting to FinnHub.")
            return False
        else:
            if i_df.iloc[0]['s'] == "ok":
                return True
            else:
                return False

    def get_usdhuf(self):
        # self.log("md-> get_usdhuf")
        try:
            i_result = self.finnhub_client.forex_rates(base='USD')
        except:
            self.log("Finnhub exception.")
            return 0
        else:
            i_usd_price = {}
            i_usd_price = i_result["quote"]
            return round(i_usd_price["HUF"], 4)

    def get_stock_candles(self, symbol, resolution, from_dt, to_dt, rename=False, log_off=False):
        if not log_off:
            self.log("md-> get_stock_candles: " + symbol + " - "
                     + self.tools.unixdt_to_dbdt(from_dt)
                     + " - "
                     + self.tools.unixdt_to_dbdt(to_dt))

        try:
            i_result = self.finnhub_client.stock_candles(symbol=symbol,
                                                         resolution=resolution,
                                                         _from=from_dt,
                                                         to=to_dt)
        except Exception as e:
            self.log("Finnhub exception: " + symbol + " - "
                     + self.tools.unixdt_to_dbdt(from_dt)
                     + " - "
                     + self.tools.unixdt_to_dbdt(to_dt))
            i_df = pd.DataFrame(None)
        else:
            if i_result['s'] == 'ok':
                i_df = pd.DataFrame(i_result)
                i_df['Date'] = pd.to_datetime(i_df['t'], unit='s')
                # a finnhub idejét Európa/Budapest időre konvertálom
                i_df['ohlc4'] = round(((i_df['o'] + i_df['h'] + i_df['l'] + i_df['c'])/4), 6)
                i_df = i_df[['Date', 't', 'o', 'h', 'l', 'c', 'ohlc4', 'v']]
                i_df = i_df.round({'t': 6, 'o': 6, 'h': 6, 'l': 6, 'c': 6, 'ohlc4': 6})
                if rename:
                    i_df = i_df.rename(columns={"o": "Open",
                                                "h": "High",
                                                "l": "Low",
                                                "c": "Close",
                                                "v": "Volume"},
                                       errors="ignore")
                i_df = self.ndf.i_df_dt_order(i_df)
            else:
                if not log_off:
                    self.log("Empty result for this time period: " +
                             str(self.tools.unixdt_to_dbdt(from_dt)) +
                             " - " + str(self.tools.unixdt_to_dbdt(to_dt)))
                i_df = pd.DataFrame(None)
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

    # def quote(self, symbol):
    #     return self.finnhub_client.quote(symbol)

    # def technical_indicator_rsi(self, symbol, resolution, from_dt, to_dt):
    #     self.log("md-> technical_indicator_rsi:" + symbol +
    #              " - " + self.tools.unixdt_to_dbdt(from_dt) + " - " + self.tools.unixdt_to_dbdt(to_dt))
    #     i_df = pd.DataFrame(self.finnhub_client.technical_indicator(symbol=symbol,
    #                                                                 resolution=resolution,
    #                                                                 _from=from_dt, to=to_dt,
    #                                                                 indicator='rsi',
    #                                                                 indicator_fields={"timeperiod": 3}))
    #     i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
    #     i_df['datetime'] = i_df['datetime'] + pd.Timedelta(hours=2)
    #     i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
    #     i_df = i_df[['datetime', 't', 'rsi']]
    #     i_df = i_df.round({'rsi': 6})
    #     i_df.set_index('datetime')
    #     return i_df

    def stock_symbols(self, market="US"):
        self.log("md-> stock_symbols: " + str(market))
        return self.finnhub_client.stock_symbols(market)

    def stream_run(self):
        if not self.stream_is_working:
            self.stream_is_working = True
            self.stream_thread = threading.Thread(target=self.stream_while)
            self.stream_thread.start()
            # self.refresh_tr_info()

    def stream_stop(self):
        self.stream_break = True

    def stream_while(self):
        i_wait_sec = self.stream_refresh_rate
        while not self.stream_break:
            self.stream_action()
            # várakozik egy adott ideig de ki tud belőle szállni menet közben is így esc re azonnal leáll
            i_wait_no = 0
            while i_wait_no < i_wait_sec and not self.stream_break:
                sleep(1)
                i_wait_no += 1
        if self.stream_break:
            print("Status: Data streaming is stopped!")
        self.stream_break = False
        self.stream_is_working = False
        # self.refresh_tr_info()

    def stream_action(self):
        # print("hello :)")
        i_new_row_count = self.ndf.get_allrow_count()
        for smb in self.ndf.get_all_symbol():
            self.ndf.refresh(smb, log_off=True)
        i_new_row_count = self.ndf.get_allrow_count() - i_new_row_count
        if i_new_row_count > 0:  # csak akkor frissítünk ha van új sor
            self.stream_last_refresh(strftime("%H:%M"))
