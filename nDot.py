# This Python file uses the following encoding: utf-8
import alpaca_trade_api as tradeapi
import pandas as pd
import threading

from datetime import datetime, timedelta
import sys
import websocket
import os
import psutil
import time
# import mysql.connector
# from mysql.connector import Error
import random
import pandas as pd
from pandas import DataFrame
import pandas_ta as ta
import finnhub
import threading
import numpy as np
from functools import partial
from tkinter import *
import tables
import alpaca_trade_api as tradeapi
# import matplotlib.animation as animation
# import matplotlib.dates as mdates

# from pandasgui.datasets import pokemon, titanic, all_datasets

# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QProgressBar, QToolButton
# from PyQt5.QtCore import *
# from datetime import timedelta
# from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtCore import QTime, QDate
# from PyQt5 import QtGui
# from PyQt5 import

import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib
matplotlib.rcParams["toolbar"] = "toolmanager"
from matplotlib.backend_tools import ToolBase


class n_system:
    print_console = False


class market_data():
    api_key_finnhubio1 = "bs9c9lvrh5rahoaofmt0"
    finnhub_client = ""

    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key=self.api_key_finnhubio1)
        self.finnhub_client.DEFAULT_TIMEOUT = 100

    def check_finnhub_connection(self, symbol="AAPL"):
        log("md-> check_finnhub_connection: " + symbol)
        i_return = False
        try:
            i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, 'D', 1590988249, 1591852249))
        except:
            log("Error while connecting to FinnHub.")
            i_return = False
        else:
            if i_df.iloc[0]['s'] == "ok":
                i_return = True
            else:
                i_return = False
        return i_return

    def get_stock_candles(self, symbol, resolution, from_dt, to_dt, rename=False):
        log("md-> get_stock_candles: " + symbol + " - " + tools.unixdt_to_dbdt(from_dt) + " - " +
            tools.unixdt_to_dbdt(to_dt))
        try:
            i_result = self.finnhub_client.technical_indicator(symbol=symbol, resolution=resolution, _from=from_dt, to=to_dt, indicator='rsi', indicator_fields={"timeperiod": 3})
        except:
            log("Finnhub exception.")
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
                i_df = i_df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close",
                             "v": "Volume"}, errors="raise")
            # return pandas df -> o h c l v t datetime ohcl4
        return i_df

    def company_profile(self, symbol):
        return self.finnhub_client.company_profile(symbol=symbol)

    def news_sentiment(self, symbol):
        return self.finnhub_client.news_sentiment(symbol=symbol)

    def quote(self, symbol):
        return self.finnhub_client.quote(symbol)

    def technical_indicator_rsi(self, symbol, resolution, from_dt, to_dt):
        log("md-> technical_indicator_rsi:" + symbol + " - " + tools.unixdt_to_dbdt(from_dt) + " - " +
            tools.unixdt_to_dbdt(to_dt))
        i_df = pd.DataFrame(self.finnhub_client.technical_indicator(symbol=symbol, resolution=resolution, _from=from_dt, to=to_dt, indicator='rsi', indicator_fields={"timeperiod": 3}))
        i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
        i_df['datetime'] = i_df['datetime'] + pd.Timedelta(hours=2)
        i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
        i_df = i_df[['datetime', 't', 'rsi']]
        i_df = i_df.round({'rsi': 6})
        i_df.set_index('datetime')
        return i_df


class trade():

    def __init__(self):

        self.request_count = {}
        self.trade_api = tradeapi.REST('PKSJI4DQMLN4IQ8L6KFT',
                                       '8CUv1fVN3s9Vl5hkxojTuDChZiXIe7E3qvbC147F',
                                       base_url='https://paper-api.alpaca.markets')

        # self.account = ""
        # self.account = self.call_alphaca("get_account")
        # self.account = self.trade_api.get_account()

        # result by last get orders in apaca object
        self.orders = []
        # result by last get position in apaca object
        self.positions = []

        # target position data frame
        self.tp_df = pd.DataFrame(None)
        # decision matrix data frame
        self.dm_df = pd.DataFrame(None)

        # current position data frame
        self.cp_df = pd.DataFrame(None)

        self.broker_thread = ""
        self.broker_refresh_rate = 25
        self.broker_is_working = False

        self.monitor_thread = ""
        self.monitor_refresh_rate = 25
        self.monitor_is_working = False
        self.monitor_break = False

        # self.last_time_get_account = 0
        # self.account_refresh_time = 60  # sec

        self.config = {
            'time_zone': 'UTC+2',
            'nyse_open': '15:30',
            'nyse_close': '22:00',
            'trade_from': '16:00',
            'trade_to': '22:00',
            'stop_margin': 5,
            'stop_margin_measure': 'Percent',
            'trade_block_size': 500,
            'trade_block_size_currency': 'USD',
        }

        self.order = {
            'symbol': '',
            'position': '',
            'qt': 0,
            'limit_price': 0.0,
            'stop_price': 0.0,
        }

        self.usd_huf = 312.12

    def call_alphaca(self, function_name, args=[], kwargs={}):
        i_now = time.gmtime()
        i_now_str = f"{int(i_now.tm_hour)}:{int(i_now.tm_min)}"
        if i_now_str in self.request_count.keys():
            self.request_count[i_now_str] += 1
        else:
            self.request_count[i_now_str] = 1

        obj = self.trade_api
        return getattr(obj, function_name)(*args, **kwargs)

    def create_decision_matrix(self):
        # add target position to decision matrix: dm_df
        self.dm_df = self.tp_df

        # add actual position to decision matrix: dm_df
        i_positions = self.get_all_positions()
        for i_p in i_positions:
            if i_p.symbol in trade.dm_df.index:
                self.dm_df.loc[i_p.symbol, 'position'] = int(i_p.qty)
            else:
                self.dm_df.loc[i_p.symbol, 'position'] = int(i_p.qty)
                self.dm_df.loc[i_p.symbol, 'trading'] = True

        # add orders to decision matrix: dm_df
        i_orders_market, i_orders_trailing, i_orders_other = self.get_all_sum_orders()
        self.dm_df = self.dm_df.join(pd.Series(i_orders_market).to_frame('order_market'), how='outer')
        self.dm_df = self.dm_df.join(pd.Series(i_orders_trailing).to_frame('order_trailing'), how='outer')
        self.dm_df = self.dm_df.join(pd.Series(i_orders_other).to_frame('order_other'), how='outer')

        # fixing dm_df
        self.dm_df = self.dm_df.fillna(0)
        self.dm_df['position'] = pd.to_numeric(self.dm_df['position'])
        self.dm_df['target_position'] = pd.to_numeric(self.dm_df['target_position'])
        self.dm_df['order_market'] = pd.to_numeric(self.dm_df['order_market'])
        self.dm_df['order_trailing'] = pd.to_numeric(self.dm_df['order_trailing'])
        self.dm_df['order_other'] = pd.to_numeric(self.dm_df['order_other'])

        # 1 szint eldönti, hogy mennyi stop illetve trading pozíció
        self.dm_df['total_trade'] = self.dm_df['target_position'] - self.dm_df['position']
        self.dm_df['stop_trade'] = 0
        self.dm_df['position_trade'] = 0
        self.dm_df['trade_chk_ok'] = False
        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'target_position'] == self.dm_df.loc[i_index, 'position']:
                self.dm_df.loc[i_index, 'stop_trade'] = 0
                self.dm_df.loc[i_index, 'position_trade'] = 0
            else:
                ix_tp = self.dm_df.loc[i_index, 'target_position']
                ix_p = self.dm_df.loc[i_index, 'position']
                ix_tt = self.dm_df.loc[i_index, 'total_trade']
                if (ix_tp > 0 and ix_p < 0) or (ix_tp < 0 and ix_p > 0) or (ix_tp == 0):
                    self.dm_df.loc[i_index, 'stop_trade'] = ix_tt - ix_tp
                    self.dm_df.loc[i_index, 'position_trade'] = ix_tt - (ix_tt - ix_tp)
                else:
                    self.dm_df.loc[i_index, 'stop_trade'] = 0
                    self.dm_df.loc[i_index, 'position_trade'] = ix_tp - ix_p

        # ellenőrzi, hogy a szétosztás megfelelőe, ez gyakorlatilag nem lehet soha hibás
        self.dm_df['trade_chk_ok'] = self.dm_df['target_position'] == (self.dm_df['position']
                                                                       + self.dm_df['stop_trade']
                                                                       + self.dm_df['position_trade'])

        # 2.szint
        # felépíti a to_do -t
        # kiválasztja, hogy mit kell csinálni most, TO DO stop vagy trade pozíciót vesz fel, vagy vár

        self.dm_df['to_do'] = ""
        self.dm_df['to_do_type'] = ""
        self.dm_df['to_do_qty'] = 0

        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'trade_chk_ok']:
                if self.dm_df.loc[i_index, 'stop_trade'] != 0:
                    if self.dm_df.loc[i_index, 'stop_trade'] < 0:
                        self.dm_df.loc[i_index, 'to_do'] = "sell"
                    else:
                        self.dm_df.loc[i_index, 'to_do'] = "buy"
                    self.dm_df.loc[i_index, 'to_do_type'] = "stop"
                    self.dm_df.loc[i_index, 'to_do_qty'] = abs(self.dm_df.loc[i_index, 'stop_trade'])
                elif self.dm_df.loc[i_index, 'position_trade'] != 0:
                    if self.dm_df.loc[i_index, 'position_trade'] < 0:
                        self.dm_df.loc[i_index, 'to_do'] = "sell"
                    else:
                        self.dm_df.loc[i_index, 'to_do'] = "buy"
                    self.dm_df.loc[i_index, 'to_do_type'] = "trade"
                    self.dm_df.loc[i_index, 'to_do_qty'] = abs(self.dm_df.loc[i_index, 'position_trade'])
                else:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
            else:
                # nem tudta a target_pozícióból és pozícióból elödnteni mit kell tenni
                # Ez elméletileg nem fodulhat elő, de ha mégis akkor nagy a BAJ!!!!
                self.dm_df.loc[i_index, 'to_do'] = "error"
                self.dm_df.loc[i_index, 'to_do_type'] = ""
                self.dm_df.loc[i_index, 'to_do_qty'] = 0

        # 3. szint
        # lehet, hogy a szükséges döntés már megszületett előzőleg és az orderek ki lettek adva
        #  - ha az orderek száma rendben akkor vár
        #  - ha nincs rendben akkor order törlést beállítja
        #  ezt broker megteszi az orderek behelyezése előtt

        self.dm_df['to_do_order_clear'] = False

        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'to_do'] == "buy":
                if self.dm_df.loc[i_index, 'order_market'] == self.dm_df.loc[i_index, 'to_do_qty']:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
                else:
                    if self.dm_df.loc[i_index, 'order_market'] == 0:
                        self.dm_df['to_do_order_clear'] = False
                    else:
                        self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "sell":
                if self.dm_df.loc[i_index, 'order_market'] == -1 * self.dm_df.loc[i_index, 'to_do_qty']:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
                else:
                    if self.dm_df.loc[i_index, 'order_market'] == 0:
                        self.dm_df['to_do_order_clear'] = False
                    else:
                        self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "wait":
                # ha "wait" -tal érkezik ide, akkor annak az az oka, hogy a pozíció és a target megegyezik, azaz
                # nincs tennivaló, ha valamirét mégis van market order, akkor azt törölni kell
                # order_cleart igazra állítom és bóker majd törli
                if self.dm_df.loc[i_index, 'order_market'] == 0:
                    self.dm_df['to_do_order_clear'] = False
                else:
                    self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "error":
                # ha ide error-al érkezik akkor nagy a BAJ
                print("!! ERROR !!")
        return self.dm_df

# monitor methods

    def monitor_run(self):
        if not self.monitor_is_working:
            self.monitor_is_working = True
            self.monitor_thread = threading.Thread(target=self.monitor_while)
            self.monitor_thread.start()

    def monitor_stop(self):
        self.monitor_break = True

    def monitor_while(self):
        while not self.monitor_break:
            self.monitor_action()
            time.sleep(self.monitor_refresh_rate)
        self.monitor_break = False
        self.monitor_is_working = False

    def monitor_action(self):
        i_positions = self.get_all_positions()
        for i_p in i_positions:
            self.cp_df.loc[i_p.symbol, 'qty'] = int(i_p.qty)
            self.cp_df.loc[i_p.symbol, 'current_price'] = float(i_p.current_price)
            self.cp_df.loc[i_p.symbol, 'cost_basis'] = float(i_p.cost_basis)
            self.cp_df.loc[i_p.symbol, 'market_value'] = float(i_p.market_value)
            self.cp_df.loc[i_p.symbol, 'unrealized_pl'] = float(i_p.unrealized_pl)
        gui.refresh_ui()
        print(i_positions)

    def get_monitor_info_by_symbol(self, symbol):
        if symbol in self.cp_df.index:
            i_q = int(self.cp_df.loc[symbol, "qty"])
            i_p = float(self.cp_df.loc[symbol, "current_price"])
            i_v = float(self.cp_df.loc[symbol, "market_value"])
            i_return = f"q: {i_q}\np: {i_p}$\nv: {i_v}$"
        else:
            i_return = ":)"
        return i_return

    def get_pl_by_symbol(self, symbol):
        if symbol in self.cp_df.index:
            i_p = float(self.cp_df.loc[symbol, "unrealized_pl"])
            i_return = f"STOP {i_p}$"
        else:
            i_return = "STOP"
        return i_return

# broker methods

    def broker_run(self):
        if not self.broker_is_working:
            self.broker_is_working = True
            self.broker_thread = threading.Thread(target=self.broker_while)
            self.broker_thread.start()

    def broker_while(self):
        is_broker_action = True
        while is_broker_action:
            is_broker_action = self.broker_action()
            time.sleep(self.broker_refresh_rate)
        self.broker_is_working = False

    def broker_action(self):
        self.create_decision_matrix()
        if not self.is_trading_blocked():
            for i_index in self.dm_df.index:

                # 1. szint
                # végrehajtja az utasítáokat

                if self.dm_df.loc[i_index, 'trading']:

                    if self.dm_df.loc[i_index, 'to_do_order_clear']:
                        i_is_canceled = self.cancel_orders_by_symbol(i_index)
                        while not i_is_canceled:
                            i_is_canceled = self.cancel_orders_by_symbol(i_index)

                    if self.dm_df.loc[i_index, 'to_do'] == "buy" or self.dm_df.loc[i_index, 'to_do'] == "sell":
                        i_qty = abs(self.dm_df.loc[i_index, 'to_do_qty'])
                        i_side = self.dm_df.loc[i_index, 'to_do']
                        if self.dm_df.loc[i_index, 'to_do_type'] == "stop":
                            # stop hoz market ordert használok
                            self.order_market(i_index, i_side, i_qty)
                        else:
                            # trade hez is market ordert használok
                            # majd ehhez kell hozzá kapcsolni a OTO -
                            self.order_market(i_index, i_side, i_qty)
                    elif self.dm_df.loc[i_index, 'to_do'] == "wait":
                        # 2. sint
                        # megvizsgálja, hogy a target állpot beállt-e, aza position == tartget position
                        # és nincsenek orderek bent ha minden ok, akkor befejeződött a trading iteráció
                        i_x = (self.dm_df.loc[i_index, 'target_position'] - self.dm_df.loc[
                            i_index, 'position']) == 0
                        i_ox = self.dm_df.loc[i_index, 'order_market'] == 0
                        if i_x and i_ox:
                            self.set_tp_done(i_index)
                    elif self.dm_df.loc[i_index, 'to_do'] == "error":
                        # ha a bróker egy pozícióra errort kap
                        print("Broker error")
            # ha van legalább egy trading true, akkor true val tér vissza
            # azaz legalább 1 olyan symbol van amivel még foglalkozni kell addig nem fog lállni a broker_wait
        else:
            print("Trading blocked")
        i_return = trade.dm_df["trading"].sum() > 0
        return i_return

    # Ordering methods

    def order_market(self, symbol, side, qty):
        print(f'Submit market order: {symbol} , {side}, {int(qty)}')
        # self.trade_api.submit_order(
        #     symbol=symbol,
        #     qty=int(qty),
        #     side=side,
        #     type='market',
        #     time_in_force='gtc'
        # )

        self.call_alphaca("submit_order",
                          [],
                          {"symbol": symbol,
                           "qty": int(qty),
                           "side": side,
                           "type": 'market',
                           "time_in_force": 'gtc'
                           }
                          )

    def order_trailing_stop(self, symbol, side, qty):
        print(f'Submit trailing stop order: {symbol} , {side}, {int(qty)}')
        # self.trade_api.submit_order(
        #     side=side,
        #     symbol=symbol,
        #     type="trailing_stop",
        #     qty=int(qty),
        #     time_in_force="day",
        #     trail_percent="10"
        # )

        self.call_alphaca("submit_order",
                          [],
                          {"side": side,
                           "symbol": symbol,
                           "type": "trailing_stop",
                           "qty": int(qty),
                           "time_in_force": "day",
                           "trail_percent": "10"
                           }
                          )

    # Target position methods

    def set_tp_position(self, symbol, qty):
        self.tp_df.loc[symbol, 'target_position'] = int(qty)
        self.tp_df.loc[symbol, 'trading'] = True

    def drop_tp_symbol(self, symbol):
        self.tp_df = self.tp_df.drop([symbol], errors='ignore')

    def set_tp_done(self, symbol):
        self.tp_df.loc[symbol, 'trading'] = False

    def get_tp_position(self, symbol):
        return self.tp_df.loc[symbol, 'target_position']

    def is_tp_done(self, symbol):
        return self.tp_df.loc[symbol, 'target_position']

    # def check_position(self):
    #
    #     # def trade_maker(tp, p, o):
    #     #     i_corr = tp - p
    #     #     if i_corr == 0 and o != 0:
    #     #         print ("clear orders")
    #     #     else:
    #     #         # átmenő akkor kell stop
    #     #         # különben
    #     #     i_stop = i_corr - self.target_positions[i_p2]
    #     #     i_new_pos = i_corr - i_stop
    #     #     print(f" -> Correction needed. stop: {i_stop} new: {i_new_pos} ")
    #
    #
    #     i_positions = self.get_all_positions()
    #     i_checked_symbol = {}
    #     for i_p in i_positions:
    #         i_target_position = int(self.get_target_position_by_symbol(i_p.symbol))
    #         i_order_sum_qty = int(self.get_sum_order_by_symbol(i_p.symbol))
    #         print("Symbol: ", i_p.symbol, "TP: ", i_target_position, "P: ", i_p.qty, "O: ", i_order_sum_qty)
    #         if int(i_p.qty) + i_order_sum_qty != i_target_position:
    #             print("  Trade bug (correction needed): ", (i_target_position-int(i_p.qty)))
    #         i_checked_symbol[i_p.symbol] = 0
    #     for i_p2 in self.target_positions:
    #         if i_p2 not in i_checked_symbol:
    #             i_order_sum_qty2 = int(self.get_sum_order_by_symbol(i_p2))
    #             print("Symbol: ", i_p2, "TP: ", self.target_positions[i_p2], "P: ", 0, "O: ", i_order_sum_qty2)
    #             i_corr = self.target_positions[i_p2] - i_order_sum_qty2
    #             i_stop = i_corr - self.target_positions[i_p2]
    #             i_new_pos = i_corr - i_stop
    #             print(f" -> Correction needed. stop: {i_stop} new: {i_new_pos} ")

    # orders method

    def get_all_sum_orders(self):
        order_list_market = {}
        order_list_trailing_stop = {}
        order_list_other = {}
        i_orders = self.get_all_open_orders()
        for i_o in i_orders:
            if i_o.order_type == 'market':
                if i_o.symbol in order_list_market:
                    if i_o.side == "buy":
                        order_list_market[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_market[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_market[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_market[i_o.symbol] = int(i_o.qty) * -1
            elif i_o.order_type == 'trailing_stop':
                if i_o.symbol in order_list_trailing_stop:
                    if i_o.side == "buy":
                        order_list_trailing_stop[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_trailing_stop[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_trailing_stop[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_trailing_stop[i_o.symbol] = int(i_o.qty) * -1
            else:
                if i_o.symbol in order_list_other:
                    if i_o.side == "buy":
                        order_list_other[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_other[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_other[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_other[i_o.symbol] = int(i_o.qty) * -1
        return order_list_market, order_list_trailing_stop, order_list_other

    # def get_sum_order_by_symbol(self, symbol):
    #     orders_qty_list = {}
    #     i_orders = trade.get_all_open_orders()
    #
    #     for i_o in i_orders:
    #         if i_o.symbol in orders_qty_list:
    #             if i_o.side == "buy":
    #                 orders_qty_list[i_o.symbol] += int(i_o.qty)
    #             else:
    #                 orders_qty_list[i_o.symbol] -= int(i_o.qty)
    #         else:
    #             if i_o.side == "buy":
    #                 orders_qty_list[i_o.symbol] = int(i_o.qty)
    #             else:
    #                 orders_qty_list[i_o.symbol] = int(i_o.qty) * -1
    #
    #     if symbol in orders_qty_list:
    #         i_return = orders_qty_list[symbol]
    #     else:
    #         i_return = 0
    #     return i_return

    def get_all_open_orders(self):
        # i_orders = self.trade_api.list_orders(
        #     status='open',
        #     limit=500,
        #     nested=True
        # )

        i_orders = self.call_alphaca("list_orders",
                                     [],
                                     {"status": 'open',
                                      "limit": 500,
                                      "nested": True}
                                     )
        self.orders = i_orders
        return i_orders

    def get_open_orders_by_symbol(self, symbol):
        i_orders = self.get_all_open_orders()
        i_symbol_orders = [o for o in i_orders if o.symbol == symbol]
        return i_symbol_orders

    def cancel_orders_by_symbol(self, symbol):
        i_orders = self.get_open_orders_by_symbol(symbol)
        for i_o in i_orders:
            self.cancel_order_by_id(i_o.id)
        i_orders2 = self.get_open_orders_by_symbol(symbol)
        if len(i_orders2) == 0:
            i_return = True
        else:
            i_return = False
        return i_return

    def cancel_order_by_id(self, order_id):
        try:
            # self.trade_api.cancel_order(order_id)
            self.call_alphaca("cancel_order", [order_id], {})
        except:
            i_all_open_orders = self.get_all_open_orders()
            if order_id in i_all_open_orders:
                i_return = False
            else:
                i_return = True
        else:
            i_return = True
        return i_return

    # account informations

    def get_account_now(self):
        # self.account = self.trade_api.get_account()
        self.account = self.call_alphaca("get_account", [], {})

    # def get_account(self):
    #     if self.last_time_get_account > 0:
    #         i_now = time.time()
    #         i_last = self.last_time_get_account
    #         i_time_dif = int(i_now - i_last)
    #         if i_time_dif > self.account_refresh_time:
    #             self.account = self.trade_api.get_account()
    #             self.last_time_get_account = time.time()
    #     else:
    #         self.account = self.trade_api.get_account()
    #         self.last_time_get_account = time.time()
    #     return self.account

    def get_buying_power(self):
        self.get_account_now()
        return self.account.buying_power

    def is_trading_blocked(self):
        self.get_account_now()
        return self.account.trading_blocked

    # symbol checks

    def is_tradable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alphaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.tradable:
                i_return = True
            else:
                i_return = False
        return i_return

    def is_shortable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alphaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.shortable:
                i_return = True
            else:
                i_return = False
        return i_return

    def is_marginable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alphaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.marginable:
                i_return = True
            else:
                i_return = False
        return i_return

    def get_symbol(self, symbol):
        return self.call_alphaca("get_asset", [symbol], {})

    # market infos

    def is_market_open(self):
        # i_clock = self.trade_api.get_clock()
        i_clock = self.call_alphaca("get_clock", [], {})
        return i_clock.is_open

    # position methods

    def get_all_positions(self):
        # i_positions = self.trade_api.list_positions()
        i_positions = self.call_alphaca("list_positions", [], {})
        self.positions = i_positions
        return i_positions

    def get_position_by_symbol(self, symbol):
        try:
            # i_position = self.trade_api.get_position(symbol)
            i_position = self.call_alphaca("get_position", [symbol], {})
        except:
            i_position = []
            self.positions = []
        else:
            self.positions = i_position
        return i_position

    def time_filter(self, df):
        # self.config['nyse_open']
        i_intime = df.between_time(self.config['nyse_open'], self.config['nyse_close'])
        i_outtime = df.between_time(self.config['nyse_close'], self.config['nyse_open'])
        return i_intime, i_outtime


class nd_db:

    def __init__(self):
        self.store = pd.HDFStore('nDot_db.h5', "a")
        for i_key in self.get_keys():
            self.read(i_key, True)
        self.close()

    def get_size(self):
        return int(os.path.getsize('nDot_db.h5')/1024)

    def get_keys(self):
        self.open()
        i_keys = self.store.keys()
        i_return = []
        for i_key in i_keys:
            i_return.append(i_key[1:])
        self.close()
        return i_return

    def write(self, symbol):
        log("nd_db-> write:" + symbol)
        self.open()
        self.store.put(symbol, nddf[symbol], format='table')
        self.close()

    def read(self, symbol, for_init=False):
        if not for_init:
            log("nd_db-> read:" + symbol)
        self.open()
        nddf[symbol] = self.store.get(symbol)
        self.close()

    def remove(self, symbol):
        log("nd_db-> remove:" + symbol)
        i_return = ""
        if symbol in self.get_keys():
            self.open()
            i_return = self.store.remove(symbol)
            self.close()
        return i_return

    def open(self):
        self.store.open("a")

    def close(self):
        self.store.close()

    def info(self):
        self.open()
        i_nfo = self.store.info()
        self.close()
        return i_nfo


class n_date_frame2():

    def __init__(self):
        self.indicators = pd.DataFrame(None)
        self.load_indicators()

    def set_dt_order(self, symbol, ascending=True):
        nddf[symbol]['Date'] = pd.to_datetime(nddf[symbol]['Date'])
        nddf[symbol].sort_values(by=['Date'], inplace=True, ascending=True)
        # nddf[symbol].sort_index(inplace=True)
        nddf[symbol].drop_duplicates(inplace=True)
        nddf[symbol].set_index('Date')

    def add(self, symbol):
        log("ndf2-> add " + symbol)
        i_now = datetime.now() + timedelta(days=1)
        i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
        i_datetime_series = pd.date_range(start=i_now, periods=7, freq='-93d')
        nddf[symbol] = pd.DataFrame()
        for i_i in range(len(i_datetime_series)-1):
            i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=4)))
            i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
            nddf[symbol] = nddf[symbol].append(md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True))
        self.set_dt_order(symbol)
        log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        log("Number of rows: " + str(nddf[symbol].shape[0]))
        nddb.write(symbol)

    def load_indicators(self):
        i_i = [
            ['SMA30', ['SMA_30']],
            ['SMA60', ['SMA_60']],
            ['SMA90', ['SMA_90']],
            ['ADX', ['ADX_90']],
            ['ICHIMOKU', ['ISA_9',      'ISB_26',    'ITS_9',           'IKS_26',    'ICS_26']]
        #   ['ICHIMOKU', ['ICHI_LEAD1', ICHI_LEAD2', 'ICHI_CONVERSION', 'ICHI_BASE', 'ICHI_LAGGING']]
        ]
        self.indicators = pd.DataFrame(i_i)
        self.indicators.columns = ['indicator', 'fields']
        self.indicators.set_index('indicator')

    def get_added_indicators(self, symbol):
        i_detectd_indicators = {}
        for i_col in nddf[symbol].columns:
            for i_index, i_row in self.indicators.iterrows():
                if i_col in i_row['fields']:
                    i_detectd_indicators[i_row['indicator']] = 1
        return(tuple(i_detectd_indicators.keys()))

    def is_indicator(self, tech_indicator):
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if len(i_search) > 0:
            i_found = True
        else:
            i_found = False
        return i_found

    def tech_remove(self, symbol, tech_indicator):
        log("ndf2-> remove_tech " + symbol + " - " + str(tech_indicator))
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if self.is_indicator(tech_indicator):
            i_fields = eval(str(i_search["fields"].iloc[0]))
            for i_drop_c in i_fields:
                if i_drop_c in nddf[symbol].columns:
                    nddf[symbol].drop(i_drop_c, axis=1, inplace=True)
            nddb.write(symbol)
        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

    def add_tech(self, symbol, tech_indicator="SMA60"):

        def case_set_back(symbol):
            # a pandas ta elállítgatja a neveket, ezért minden
            # hívás után szépen vissza állítom a neveket :)
            nddf[symbol] = nddf[symbol].rename(columns={"open": "Open",
                                         "close": "Close",
                                         "low": "Low",
                                         "high": "High",
                                         "volume": "Volume"
                                         })

        log("ndf2-> add_tech " + symbol + " - " + str(tech_indicator))

        if self.is_indicator(tech_indicator):

            if tech_indicator == "SMA30":
                nddf[symbol].ta.sma(length=30, append=True)
            elif tech_indicator == "SMA60":
                nddf[symbol].ta.sma(length=60, append=True)
            elif tech_indicator == "SMA90":
                nddf[symbol].ta.sma(length=90, append=True)
            elif tech_indicator == "ICHIMOKU":
                nddf[symbol].ta.ichimoku(append=True)
            elif tech_indicator == "ADX":
                nddf[symbol].ta.adx(length=8, append=True)

            case_set_back(symbol)
            nddb.write(symbol)

        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

    def remove(self, symbol):
        log("ndf2-> remove " + symbol)
        if symbol in nddf:
            del nddf[symbol]
        i_log = nddb.remove(symbol)

    def refresh(self, symbol):
        log("ndf2-> refresh " + symbol)
        log("Time frame (before refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        log("Number of rows (before refresh): " + str(nddf[symbol].shape[0]))
        to_dbdt = datetime.now() + timedelta(days=1)
        to_dbdt = to_dbdt.strftime('%Y-%m-%d %H:%M:%S')
        from_dbdt = str(nddf[symbol]["Date"].max())
        i_tounix = tools.dbdt_to_unixdt(to_dbdt)
        i_fromunix = tools.dbdt_to_unixdt(from_dbdt)
        nddf[symbol] = nddf[symbol].append(md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True))
        self.set_dt_order(symbol)
        log("Time frame (after refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        log("Number of rows (after refresh): " + str(nddf[symbol].shape[0]))
        nddb.write(symbol)


class watch_list:
    df = ""

    def __init__(self):
        self.df = self.read()
        # self.refresh_close()
        # self.refresh_sentiment()


    def read(self):
        return pd.read_csv('wl.csv', sep=';')

    def write(self):
        self.df.to_csv('wl.csv', sep=';', index=False)
        self.df = self.read()
        return

    def refresh_close(self):
        s("wl.refresh.close " + time.strftime("%H:%M:%S"))
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_quote = md.quote(i_symbol)
            self.df.loc[self.df['symbol'] == i_symbol, 'c'] = i_quote['c']
            self.df.loc[self.df['symbol'] == i_symbol, 'pc'] = i_quote['pc']
        self.write()
        return

    def refresh_profile(self):
        s("Refresh Wl Data")
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_company_profile = md.company_profile(i_symbol)
            if len(i_company_profile.keys()) == 0:
                self.df.loc[self.df['symbol'] == i_symbol, 'name'] = i_symbol
                self.df.loc[self.df['symbol'] == i_symbol, 'profil'] = i_symbol
            else:
                self.df.loc[self.df['symbol'] == i_symbol, 'name'] = i_company_profile['name']
                self.df.loc[self.df['symbol'] == i_symbol, 'profil'] = "Description: " + i_company_profile['description']
        self.write()
        return

    def refresh_sentiment(self):
        s("Refresh Wl sentiment")
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_news_sentiment = md.news_sentiment(i_symbol)
            if i_news_sentiment['sentiment']:
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bearish'] = i_news_sentiment['sentiment']['bearishPercent']
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bullish'] = i_news_sentiment['sentiment']['bullishPercent']
            else:
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bearish'] = 0
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bullish'] = 0

        self.write()
        return

    def add(self, symbol):
        self.remove(symbol)
        new_row = {'symbol': symbol}
        self.df = self.df.append(new_row, ignore_index=True)
        self.refresh_profile()
        self.refresh_close()
        self.refresh_sentiment()
        self.write()
        gui.refresh_ui()
        ndf2.add(symbol)
        return

    def remove(self, symbol):
        self.df.drop(self.df.loc[self.df['symbol'] == symbol].index, inplace=True)
        self.write()
        return


class tools():

    def get_df_column(self, df, col):
        return df[col].to_numpy().tolist()

    def dbdt_to_unixdt(self, datestring):
        dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        # print(dt2)
        i_return = str(int(time.mktime(dt2.timetuple())))
        return i_return

    def unixdt_to_dbdt(self, unix_datetime):
        # print("datetime", unix_datetime)
        return str(datetime.fromtimestamp(int(unix_datetime)).strftime('%Y-%m-%d %H:%M:%S'))

    def get_ui_date_unix(self, fort):

        def convert_to_unix_dt(cyear, cmonth, cday, chour, cminute, csecound):
            dt = datetime(cyear, cmonth, cday, chour, cminute, csecound)
            return str(int(time.mktime(dt.timetuple())))

        i_from_year = int(gui.From_D.selectedDate().toString("yyyy"))
        i_from_month = int(gui.From_D.selectedDate().toString("MM"))
        i_from_day = int(gui.From_D.selectedDate().toString("dd"))
        i_from_hour = int(gui.From_T.dateTime().toString("hh"))
        i_from_minute = int(gui.From_T.dateTime().toString("mm"))
        i_from_secound = int(gui.From_T.dateTime().toString("ss"))

        i_to_year = int(gui.To_D.selectedDate().toString("yyyy"))
        i_to_month = int(gui.To_D.selectedDate().toString("MM"))
        i_to_day = int(gui.To_D.selectedDate().toString("dd"))
        i_to_hour = int(gui.To_T.dateTime().toString("hh"))
        i_to_minute = int(gui.To_T.dateTime().toString("mm"))
        i_to_secound = int(gui.To_T.dateTime().toString("ss"))
        if fort == "from":
            i_return = convert_to_unix_dt(i_from_year, i_from_month, i_from_day,
                                           i_from_hour, i_from_minute, i_from_secound)
        else:
            i_return = convert_to_unix_dt(i_to_year, i_to_month, i_to_day,
                                           i_to_hour, i_to_minute, i_to_secound)
        return i_return

    def get_ui_date_dbdt(self, fort):

        def convert_to_unix_dt(cyear, cmonth, cday, chour, cminute, csecound):
            dt = datetime(cyear, cmonth, cday, chour, cminute, csecound)
            return str(int(time.mktime(dt.timetuple())))

        if fort == "from":
            i_return = self.unixdt_to_dbdt(self.get_ui_date_unix("from"))
        else:
            i_return = self.unixdt_to_dbdt(self.get_ui_date_unix("to"))
        return i_return

    def convert_df_to_csvdf(self, i_df):
        import io
        from io import StringIO
        su = io.StringIO()
        i_df.to_csv(su, index=False)
        i_return = pd.read_csv(StringIO(su.getvalue()), sep=",", index_col=0, parse_dates=True)
        return i_return


class gui(QWidget):
    # progress_count = 0

    def __init__(self):
        super(gui, self).__init__()
        self.load_ui()
        self.commands = pd.DataFrame(None)
        self.load_commands()
        self.pause_trader_frame_calculation = True
        # self.thread = ListenWebsocket()
        # self.thread.start()
        return

    def load_commands(self):
        c = [
            ['help', 'help2', 'help - List of all commands!', 0],
            ['do', 'do', 'do', 0],
            ['test', 'test', 'test <p1 / optional> <p2 / optional> <p3 / optional>', 0],
            ['sys.print', 'sys_print', 'sys.print <True/False>', 1],
            ['wl.add', 'wl_add', 'wl.add <symbol>', 0],
            ['wl.remove', 'wl_remove', 'wl.remove <symbol> ', 1],
            # ['wl.refresh.close', 'wl_refresh_close', 'wl.refresh.close <> ', 0],
            ['wl.refresh.profile', 'wl_refresh_profile', 'wl.refresh.profile', 0],
            ['wl.refresh.sentiment', 'wl_refresh_sentiment', 'wl.refresh.sentiment', 0],
            # ['wl.refresh.all', 'wl_refresh_all', 'wl.refresh.all <> ', 0],
            # ['ndf.add', 'ndf_add', 'ndf.add <symbol>', 1],
            ['ndf2.add', 'ndf2_add', 'ndf2.add <symbol>', 1],
            ['ndf2.tech', 'ndf2_tech', 'ndf2.tech <symbol> <technical indicator>', 2],
            ['ndf2.tech.remove', 'ndf2_tech_remove', 'ndf2.tech.remove <symbol> <technical indicator>', 2],
            ['ndf2.tech.refresh', 'ndf2_tech_refresh', 'ndf2.tech.refresh <symbol>', 1],
            ['ndf2.tech.refresh.all', 'ndf2_tech_refresh_all', 'ndf2.tech.refresh.all', 0],
            ['ndf2.remove', 'ndf2_remove', 'ndf2.remove <symbol>', 1],
            ['ndf2.refresh', 'ndf2_refresh', 'ndf2.refresh <symbol>', 1],
            ['ndf2.info', 'ndf2_info', 'ndf2.info', 0],
            ['ndf2.columns', 'ndf2_columns', 'ndf2.columns', 0],
            ['ndf2.show.last', 'ndf2_show_last', 'ndf2.show.last <symbol> <numbers / optional>', 1],

            # ['ndf.refresh', 'ndf_refresh', 'ndf.refresh <symbol>', 1],
            # ['ndf.remove', 'ndf_remove', 'ndf.remove <symbol>', 1],
            # ['ndf.check', 'ndf_check', 'ndf.check <symbol>', 1],
            # ['ndf.chart', 'ndf_chart', 'ndf.chart <symbol> UI date time', 1],
            # ['ndf.chart.last', 'ndf_chart_last', 'ndf.chart.last <symbol> <numbers / optional>', 1],
            # ['ndf.show.last', 'ndf_show_last', 'ndf.show.last <symbol> <numbers / optional>', 1],
            # ['ndf.tech', 'ndf_tech', 'ndf.tech <symbol> <technical indicator>', 2],
            # ['ndf.tech.refresh', 'ndf_tech_refresh', 'ndf.tech.refresh <symbol>', 1],
            ['md.check', 'md_check', 'md.check <symbol>', 0],
            # ['bp.start', 'bp_start', 'bp.start <> ', 0],
            # ['bp.stop', 'bp_stop', 'bp.stop <> ', 0],
            ['exit', 'exit', 'exit', 0]
        ]
        self.commands = pd.DataFrame(c)
        self.commands.columns = ['command', 'program', 'hint', 'params']
        self.commands.set_index('command')
        return

    def print_command(self):
        log("Commands:")
        for i_index, i_row in self.commands.iterrows():
            log(" - " + i_row["hint"])
        QApplication.processEvents()

    def set_trade_frame(self):
        self.pause_trader_frame_calculation = True
        self.Tr_symbol.setText(trade.order["symbol"])
        if trade.order["position"] == "SHORT":
            self.Tr_position.setStyleSheet('background-color: #ffffff; ' + \
                                           'border-bottom-left-radius: 15px;' + \
                                           'color: #ff3333;')
            self.Tr_set_order.setText("SET\nSHORT")
        else:
            self.Tr_position.setStyleSheet('background-color: #ffffff; ' + \
                                           'border-bottom-left-radius: 15px;' + \
                                           'color: #078F12;')
            self.Tr_set_order.setText("SET\nLONG")

        self.Tr_position.setText(trade.order["position"])
        self.Tr_limit_price.setValue(trade.order["limit_price"])
        self.Tr_stop_price.setValue(trade.order["stop_price"])
        self.Tr_qt.setValue(trade.order["qt"])
        self.pause_trader_frame_calculation = False
        self.tr_change_data()
        self.Tr_frame.show()
        QApplication.processEvents()

    def get_command(self, command):
        i_search = self.commands.loc[self.commands['command'] == command, 'program']
        if len(i_search) > 0:
            i_found = True
            i_program = self.commands.loc[self.commands['command'] == command, 'program'].iloc[0]
            i_hint = self.commands.loc[self.commands['command'] == command, 'hint'].iloc[0]
            i_params = self.commands.loc[self.commands['command'] == command, 'params'].iloc[0]
        else:
            i_found = False
            i_program = ""
            i_hint = ""
            i_params = ""
        return i_found, i_program, i_hint, i_params

    def load_ui(self):
        loadUi("./qt_ui/form.ui", self)
        # hozzárendelések ------------------------------------------------------------------
        self.Command_Line.setText("")
        self.Run_Button.clicked.connect(self.run_button_action)
        self.Command_Line.returnPressed.connect(self.run_button_action)
        self.Command_Line.textChanged.connect(self.command_line_changed)
        self.WL_btn_chart.clicked.connect(partial(wl_btn_chart, 1))
        self.WL_btn_chart_2.clicked.connect(partial(wl_btn_chart, 2))
        self.WL_btn_chart_3.clicked.connect(partial(wl_btn_chart, 3))
        self.WL_btn_chart_4.clicked.connect(partial(wl_btn_chart, 4))
        self.WL_btn_chart_5.clicked.connect(partial(wl_btn_chart, 5))
        self.WL_btn_chart_6.clicked.connect(partial(wl_btn_chart, 6))
        self.WL_btn_chart_7.clicked.connect(partial(wl_btn_chart, 7))
        self.WL_btn_chart_8.clicked.connect(partial(wl_btn_chart, 8))
        self.WL_btn_chart_9.clicked.connect(partial(wl_btn_chart, 9))
        self.WL_btn_chart_10.clicked.connect(partial(wl_btn_chart, 10))
        self.WL_btn_chart_11.clicked.connect(partial(wl_btn_chart, 11))
        self.WL_btn_chart_12.clicked.connect(partial(wl_btn_chart, 12))
        self.WL_btn_show.clicked.connect(partial(wl_btn_show, 1))
        self.WL_btn_show_2.clicked.connect(partial(wl_btn_show, 2))
        self.WL_btn_show_3.clicked.connect(partial(wl_btn_show, 3))
        self.WL_btn_show_4.clicked.connect(partial(wl_btn_show, 4))
        self.WL_btn_show_5.clicked.connect(partial(wl_btn_show, 5))
        self.WL_btn_show_6.clicked.connect(partial(wl_btn_show, 6))
        self.WL_btn_show_7.clicked.connect(partial(wl_btn_show, 7))
        self.WL_btn_show_8.clicked.connect(partial(wl_btn_show, 8))
        self.WL_btn_show_9.clicked.connect(partial(wl_btn_show, 9))
        self.WL_btn_show_10.clicked.connect(partial(wl_btn_show, 10))
        self.WL_btn_show_11.clicked.connect(partial(wl_btn_show, 11))
        self.WL_btn_show_12.clicked.connect(partial(wl_btn_show, 12))
        # Trade frame ----------------------------------------
        self.Tr_cancel.clicked.connect(tr_cancel)
        self.WL_trade_short.clicked.connect(partial(wl_trade_short, 1))
        self.WL_trade_short_2.clicked.connect(partial(wl_trade_short, 2))
        self.WL_trade_short_3.clicked.connect(partial(wl_trade_short, 3))
        self.WL_trade_short_4.clicked.connect(partial(wl_trade_short, 4))

        self.WL_trade_long.clicked.connect(partial(wl_trade_long, 1))
        self.WL_trade_long_2.clicked.connect(partial(wl_trade_long, 2))
        self.WL_trade_long_3.clicked.connect(partial(wl_trade_long, 3))
        self.WL_trade_long_4.clicked.connect(partial(wl_trade_long, 4))

        self.Tr_limit_price.valueChanged.connect(self.tr_change_data)
        self.Tr_stop_price.valueChanged.connect(self.tr_change_data)
        self.Tr_qt.valueChanged.connect(self.tr_change_data)
        self.Tr_portfolio_monitor.stateChanged.connect(tr_portfolio_monitor)

        self.WL_refresh.clicked.connect(wl_refresh_close)
        self.Datetime_mod1.clicked.connect(partial(self.date_modifier, "hours", 6))
        self.Datetime_mod2.clicked.connect(partial(self.date_modifier, "days", 1))
        self.Datetime_mod3.clicked.connect(partial(self.date_modifier, "days", 2))
        self.Datetime_mod4.clicked.connect(partial(self.date_modifier, "days", 4))
        self.Datetime_mod5.clicked.connect(partial(self.date_modifier, "days", 30))
        self.Datetime_now.clicked.connect(self.date_now)
        # induló értékek ------------------------------------------------------------------
        self.setWindowTitle("   nDot")
        app_icon = QtGui.QIcon()
        app_icon.addFile('./images/ndot_icon_x2.png', QtCore.QSize(16, 16))
        app.setWindowIcon(app_icon)
        i_now = datetime.now()
        self.From_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
        self.From_T.setTime(QTime(i_now.hour, i_now.minute))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))
        self.Tr_frame.hide()

    def tr_change_data(self):
        if not self.pause_trader_frame_calculation:
            trade.order["limit_price"] = round(self.Tr_limit_price.value(), 2)
            trade.order["stop_price"] = round(self.Tr_stop_price.value(), 2)
            trade.order["qt"] = int(self.Tr_qt.value())
            i_value_usd = round(trade.order["qt"] * trade.order["limit_price"], 2)
            i_value_huf = round(i_value_usd * trade.usd_huf, 2)
            i_value_text = '{0:,.2f}'.format(i_value_usd) + " USD\n" + '{0:,.2f}'.format(i_value_huf) + " HUF"
            self.Tr_value.setText(i_value_text)
            QApplication.processEvents()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            trade.monitor_stop()
            print("Status: GUI Closed")
            # self.thread.ws.close()
            self.close()

    def refresh_ui(self):
        i_wl_frame_object = np.ndarray(12, dtype=object, order='F')
        i_wl_frame_object[0] = gui.WL_frame
        i_wl_frame_object[1] = gui.WL_frame_2
        i_wl_frame_object[2] = gui.WL_frame_3
        i_wl_frame_object[3] = gui.WL_frame_4
        i_wl_frame_object[4] = gui.WL_frame_5
        i_wl_frame_object[5] = gui.WL_frame_6
        i_wl_frame_object[6] = gui.WL_frame_7
        i_wl_frame_object[7] = gui.WL_frame_8
        i_wl_frame_object[8] = gui.WL_frame_9
        i_wl_frame_object[9] = gui.WL_frame_10
        i_wl_frame_object[10] = gui.WL_frame_11
        i_wl_frame_object[11] = gui.WL_frame_12

        i_noid = np.array(['', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12'])
        # i_noid = np.array(['', '_2', '_3', '_4', '_5', '_6', '_7', '_8'])

        for i_obj in i_wl_frame_object:
            i_obj.hide()
        i_no = 0
        for index, row in wl.df.iterrows():
            i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setText(row['symbol'])
            i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setToolTip(row['profil'])
            i_symbol = row['symbol']
            i_info = trade.get_monitor_info_by_symbol(i_symbol)
            i_wl_frame_object[i_no].findChild(QLabel, "WL_info"+i_noid[i_no]).setText(i_info)
            i_pl = trade.get_pl_by_symbol(i_symbol)
            i_wl_frame_object[i_no].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).setText(i_pl)
            # if row['c'] > row['pc']:
            #     i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▲")
            #     i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: green; background: #ffffff;")
            # else:
            #     i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▼")
            #     i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: red; background: #ffffff;")

            # nn_drop1 = random.randint(0, 50)
            # nn_drop2 = random.randint(0, 50)
            # nn_drop3 = 100 - nn_drop1 - nn_drop2
            #
            # i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_long"+i_noid[i_no]).setText("L:"+str(nn_drop1) + "%")
            # i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_neutral"+i_noid[i_no]).setText("N:"+str(nn_drop3) + "%")
            # i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_short"+i_noid[i_no]).setText("S:"+str(nn_drop2) + "%")
            # i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bull"+i_noid[i_no]).setValue(int(row['snt_bullish']*100))
            i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bear"+i_noid[i_no]).setValue(int(row['snt_bearish']*100))
            i_wl_frame_object[i_no].show()
            i_no = i_no + 1
            QApplication.processEvents()

    def date_now(self):
        i_now = datetime.now()
        self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))

    def date_modifier(self, interval_type, interval_num):
        i_nowp = datetime.now() - timedelta(**{interval_type: interval_num})
        self.From_D.setDate(QDate(i_nowp.year, i_nowp.month, i_nowp.day))
        self.From_T.setTime(QTime(i_nowp.hour, i_nowp.minute))

    def progress_action(self):
        # self.progress_count = self.progress_count + 5
        # if self.progress_count > 100:
        #     self.progress_count = 0
        self.Progress_Bar.setValue(random.randint(0, 100))

    # def is_command(self, command):
    #     i_search = self.commands.loc[self.commands['command'] == command]
    #     if len(i_search) > 0:
    #         i_found = True
    #     else:
    #         i_found = False
    #     return i_found

    def mark_command_line(self, message, bug=True):
        if bug:
            self.Command_Line.setStyleSheet('background-color: #ffaaaa; ' + \
                                            'border-top-left-radius: 15px;' + \
                                            'border-top-right-radius: 0px;' + \
                                            'border-bottom-right-radius: 0px;' + \
                                            'border-bottom-left-radius: 0px;' + \
                                            'border-bottom: 1px solid #eeeeee;' + \
                                            'padding-left: 10px;')
            self.Command_Hint.setText(message)
            QApplication.processEvents()
        else:
            self.Command_Line.setStyleSheet('background-color: #ffffff; ' + \
                                            'border-top-left-radius: 15px;' + \
                                            'border-top-right-radius: 0px;' + \
                                            'border-bottom-right-radius: 0px;' + \
                                            'border-bottom-left-radius: 0px;' + \
                                            'border-bottom: 1px solid #eeeeee;' + \
                                            'padding-left: 10px;')
            self.Command_Hint.setText(message)
            QApplication.processEvents()

    def run_button_action(self):

        def run_method(i_program, args):
            method = eval(i_program)
            kwargs = {}
            args_str = ', '.join(map(str, args))
            i_start = datetime.now()
            log("Start: " + command_text_first_word + " <" + args_str + ">", True, False)
            method(*args, **kwargs)
            log("Ready.", False, False)
            log("Runtime:" + str(datetime.now()-i_start), False, False)
            self.Command_Line.setText("")

        command_text = self.Command_Line.text()
        command_partitioned = command_text.split()
        command_text_first_word = str.lower(command_partitioned[0])

        i_found, i_program, i_hint, i_params = self.get_command(command_text_first_word)
        args = []

        if i_found:
            if len(command_partitioned) == 2:
                args = [command_partitioned[1]]
            if len(command_partitioned) == 3:
                args = [command_partitioned[1], command_partitioned[2]]
            if len(command_partitioned) == 4:
                args = [command_partitioned[1], command_partitioned[2], command_partitioned[3]]

            if i_params >= 1:
                if len(command_partitioned) - 1 >= i_params:
                    if (len(wl.df.loc[wl.df['symbol'] == command_partitioned[1]]) > 0):
                        run_method(i_program, args)
                    else:
                        self.mark_command_line("Non listed Symbol!")
                else:
                    self.mark_command_line("Missing parameter(s)!")
            else:
                run_method(i_program, args)
        else:
            self.mark_command_line("Command does not exist!")
            self.print_command()


    def command_line_changed(self):
        command_text = self.Command_Line.text()
        command_text_first_word = str.lower(command_text.partition(' ')[0])
        i_found, i_program, i_hint, i_params = self.get_command(command_text_first_word)
        if i_found:
            self.mark_command_line(i_hint, False)
        else:
            self.mark_command_line("", False)


# PROGRAMS ----------------------------------------------------------------------------

def help2(p1="", p2="", p3=""):
    gui.print_command()


def do(symbol="", p2="", p3=""):

    print(nddf['MSFT'])
    # stock = n_date_frame()
    # stock.add_last(symbol, 1)

    stock = n_date_frame()
    stock.get_time_frame(symbol)
    log("ndf_chart-> plot chart")
    i_chart_df = stock.df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close",
                                                "v": "Volume"},errors="raise")
    df = tools.convert_df_to_csvdf(i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']])

    import mplfinance as mpf
    # import pandas as pd
    # import matplotlib.pyplot as plt

    # Tenkan Sen
    # conversionLine
    tenkan_max = df['High'].rolling(window=9, min_periods=0).max()
    tenkan_min = df['Low'].rolling(window=9, min_periods=0).min()
    df['tenkan_avg'] = (tenkan_max + tenkan_min) / 2

    # Kijun Sen
    # baseLine
    kijun_max = df['High'].rolling(window=26, min_periods=0).max()
    kijun_min = df['Low'].rolling(window=26, min_periods=0).min()
    df['kijun_avg'] = (kijun_max + kijun_min) / 2

    # Senkou Span A
    # Lead1
    # (Kijun + Tenkan) / 2 Shifted ahead by 26 periods
    df['senkou_a'] = ((df['kijun_avg'] + df['tenkan_avg']) / 2).shift(26)

    # Senkou Span B
    # Lead1
    # 52 period High + Low / 2
    senkou_b_max = df['High'].rolling(window=52, min_periods=0).max()
    senkou_b_min = df['Low'].rolling(window=52, min_periods=0).min()
    df['senkou_b'] = ((senkou_b_max + senkou_b_min) / 2).shift(52)

    # Chikou Span
    # Current close shifted -26
    # Lagging
    df['chikou'] = (df['Close']).shift(-26)

    # Plotting Ichimoku

    # m_plots = ['kijun_avg', 'tenkan_avg',df[df.columns[5:]][-250:] ]

    add_plots = [
        mpf.make_addplot(df['kijun_avg'][-250:]),
        mpf.make_addplot(df['tenkan_avg'][-250:]),
        mpf.make_addplot(df['chikou'][-250:]),
        mpf.make_addplot(df['senkou_a'][-250:]),
        mpf.make_addplot(df['senkou_b'][-250:])
    ]
    mpf.plot(df[-250:], type='candle', mav=200, volume=True, ylabel="Price", ylabel_lower='Volume', style='nightclouds',
              figratio=(15, 10), figscale=1.5, addplot=add_plots, title=symbol,
             fill_between=dict(y1=df['senkou_a'].values, y2=df['senkou_b'].values, color='#f2ad73', alpha=0.20))
    pass


def s(msg_str):
    gui.Status.setText("Status: " + msg_str)
    QApplication.processEvents()
    if nsys.print_console:
        print(time.strftime("%m-%d %H:%M:%S")+" > "+"Status: "+msg_str)


def log(add_text, line=False, indent=True):
    if indent:
        i_ind = "│  "
    else:
        i_ind = ""

    if line:
        i_log_text = gui.Logs_Browser.toPlainText() + "─" * 65 + "\r"
        gui.Logs_Browser.setText(i_log_text)

    lines = add_text.splitlines()

    for one_line in lines:
        i_log_text = gui.Logs_Browser.toPlainText() + time.strftime("%m-%d %H:%M:%S") + " > " + i_ind + one_line + " \r"
        gui.Logs_Browser.setText(i_log_text)
        gui.Logs_Browser.moveCursor(QtGui.QTextCursor.End)
        QApplication.processEvents()


def tlog(add_text, line=False, indent=True, color="normal" ):

    if color == "long":
        i_web_color = "#078f12"
    elif color == "short":
        i_web_color = "#ff3333"
    elif color == "stop":
        i_web_color = "#ff9100"
    else:
        i_web_color = "#0000"

    if indent:
        i_ind = "│  "
    else:
        i_ind = ""

    if line:
        i_log_text = gui.Logs_Trade.toPlainText() \
                     + " <font color='#000000'>" \
                     + "─" * 65 \
                     + "</font>" \
                     + "\r"
        gui.Logs_Trade.setText(i_log_text)

    lines = add_text.splitlines()

    for one_line in lines:
        i_log_text = gui.Logs_Trade.toHtml() \
                     + " <font color='#000000'>" \
                     + time.strftime("%m-%d %H:%M:%S") + " > "\
                     + i_ind \
                     + "</font>" \
                     + " <font color='" + i_web_color + "'>"\
                     + one_line \
                     + "</font>" \
                     + " \r"
        gui.Logs_Trade.setText(i_log_text)
        gui.Logs_Trade.moveCursor(QtGui.QTextCursor.End)
        QApplication.processEvents()


def test(p1="", p2="", p3=""):
    log("2/1. This is a test log message.")
    log("2/2. This is a test log message.")
    s("This is a test status message")

    # if db.check_connection():
    #     log("  Server version: " + db.server_version)
    #     log("  Data base size: " + str(db.db_size) + " MB")
    # else:
    #     log("  Error: " + str(db.error.msg))

    if md.check_finnhub_connection():
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")

    ndf2_info()

    process = psutil.Process(os.getpid())
    log("Memory usage: " + str(round(process.memory_percent(),2)) + " %")
    i_disk_usage = psutil.disk_usage('/')
    log("Disk usage: " + str(i_disk_usage.percent) + " %")


def sys_print(set_p="1", p2="", p3=""):
    if set_p == "1":
        nsys.print_console = True
    else:
        nsys.print_console = False
    if nsys.print_console:
        log("sys.print is True")
    else:
        log("sys.print is False")


def exit_program(p1="", p2="", p3=""):
    gui.close()


# ndf programs  ----------------------------------------------------------------------------


def ndf2_add(symbol="", p2="", p3=""):
    ndf2.add(symbol)


def ndf2_tech(symbol, tech_indicator, p3=""):
    ndf2.add_tech(symbol, tech_indicator)


def ndf2_tech_remove(symbol, tech_indicator, p3=""):
    ndf2.tech_remove(symbol, tech_indicator)


def ndf2_tech_refresh(symbol, p2="", p3=""):
    i_indicators = ndf2.get_added_indicators(symbol)
    print(i_indicators)
    for i_i in i_indicators:
        ndf2.add_tech(symbol, i_i)

def ndf2_tech_refresh_all(p1="", p2="", p3=""):
    i_symbols = tuple(nddf.keys())
    for i_s in i_symbols:
        log("Refresh indicators in dataframe: " + i_s)
        i_indicators = ndf2.get_added_indicators(i_s)
        for i_i in i_indicators:
            ndf2.add_tech(i_s, i_i)


def ndf2_remove(symbol="", p2="", p3=""):
    ndf2.remove(symbol)


def ndf2_refresh(symbol="", p2="", p3=""):
    ndf2.refresh(symbol)


def ndf2_info(p1="", p2="", p3=""):
    log(nddb.info())
    log("nDot db size: " + str(nddb.get_size()) + " KB")
    i_nddf_size = sys.getsizeof(nddf)
    for key in nddf:
        i_nddf_size += nddf[key].memory_usage(deep=True).sum()
    log("nddf size in memory: " + str(int(i_nddf_size/1024)) + " KB")

def ndf2_columns(p1="", p2="", p3=""):
    i_cols = tuple(nddf.keys())
    log("Data Frame columns by symbols:")
    for i_c in i_cols:
        log(i_c)
        log(str(tuple(nddf[i_c].columns)))


def ndf2_show_last(symbol="", xminute="60", p3=""):
    if symbol in nddf:

        from pandastable import Table, TableModel, config

        class TestApp(Frame):
            """Basic test frame for the table"""

            def __init__(self, parent=None):
                self.parent = parent
                Frame.__init__(self)
                self.main = self.master
                self.main.geometry('1200x600+100+100')
                self.main.title(symbol)
                f = Frame(self.main)
                f.pack(fill=BOTH, expand=1)

                self.table = pt = Table(f, dataframe=nddf[symbol].iloc[::-1],
                                        showtoolbar=True, showstatusbar=True)
                options = {'align': 'w',
                         'cellbackgr': '#F4F4F3',
                         'cellwidth': 80,
                         'colheadercolor': '#535b71',
                         'floatprecision': 2,
                         'font': 'Arial',
                         'fontsize': 9,
                         'fontstyle': '',
                         'grid_color': '#AAAAAA',
                         'linewidth': 1,
                         'rowheight': 18,
                         'rowselectedcolor': '#E4DED4',
                         'textcolor': 'black'}
                config.apply_options(options, self.table)
                pt.show()
                return

        app = TestApp()
        app.mainloop()
    else:
        log("nddf key not exist: " + symbol)




def ndf_chart(symbol, p2="", p3=""):
    stock = n_date_frame()
    stock.get_time_frame(symbol)
    if db.row_count > 0:
        log("ndf_chart-> plot chart")
        i_chart_df = stock.df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close",
                                                "v": "Volume"},errors="raise")
        quote = tools.convert_df_to_csvdf(i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']])
        import matplotlib.pyplot as plt
        import mplfinance as mpf
        mpf.plot(quote, type='line', volume=True, mav=(20, 40))
        # fig = mpf.figure(style='yahoo', figsize=(20, 10), dpi=60, facecolor='white', edgecolor='k', tight_layout=True,
        #                  num=symbol)
        # ax1 = fig.add_subplot(4, 1, (1, 3))
        # ax2 = fig.add_subplot(4, 1, 4, sharex=ax1)
        # # plt.subplots_adjust(hspace=.001)
        # mpf.plot(quote, ax=ax1, volume=ax2, axtitle='')
        mpf.show()
    else:
        log("no data found in df")


class NewTool1(ToolBase):
    image = r"./images/ndot_icon_x2.png"

    def trigger(self, sender, event, data=None):
        # print(nddf[nchart.symbol]["Close"].iloc[nchart.window_from:nchart.window_to])
        for i_i in range(1, 5):
            for ax in nchart.axes:
                ax.clear()
            nchart.window_minus(3)
            ap = [mpf.make_addplot(nchart.df.iloc[nchart.window_from:nchart.window_to],
                                   type='candle',
                                   ax=nchart.ax2,
                                   ylabel='OHLC Price')
                  # mpf.make_addplot(nddf[self.symbol].iloc[self.window_from:self.window_to][['Low', 'High']], ax=ax1)
                  ]

            mpf.plot(nchart.df.iloc[nchart.window_from:nchart.window_to],
                     type='candle',
                     ax=nchart.ax1,
                     volume=nchart.ax3,
                     addplot=ap,
                     tight_layout=True)

            for ax in nchart.axes[:-1]:
                plt.setp(ax.get_xticklabels(), visible=False)

            nchart.fig.canvas.draw()
            QApplication.processEvents()


class NewTool2(ToolBase):
    image = r"./images/ndot_icon_x2.png"

    def trigger(self, sender, event, data=None):

        for i_i in range(1, 5):
            for ax in nchart.axes:
                ax.clear()
            nchart.window_plus(3)

            ap = [mpf.make_addplot(nchart.df.iloc[nchart.window_from:nchart.window_to],
                                   type='candle',
                                   ax=nchart.ax2,
                                   ylabel='OHLC Price')
                  # mpf.make_addplot(nddf[self.symbol].iloc[self.window_from:self.window_to][['Low', 'High']], ax=ax1)
                  ]
            mpf.plot(nchart.df.iloc[nchart.window_from:nchart.window_to],
                     type='candle',
                     ax=nchart.ax1,
                     volume=nchart.ax3,
                     addplot=ap,
                     tight_layout=True)
            nchart.fig.subplots_adjust(hspace=0.001, wspace=0, left=0.07)

            for ax in nchart.axes[:-1]:
                plt.setp(ax.get_xticklabels(), visible=False)

            nchart.fig.canvas.draw()
            QApplication.processEvents()


class nchart_last():

    def __init__(self):
        self.symbol = ""
        self.row_count = 0
        self.window_size = 120
        self.window_to = 0
        self.window_from = 0
        self.fig = ""
        self.axes = ""
        self.last_block_count = 2
        self.df = pd.DataFrame(None)
        self.add_plots = []
        self.ax1 = ""
        self.ax2 = ""
        self.ax3 = ""

    def show(self):
        print(self.symbol)
        self.df = pd.DataFrame(None)
        print(nddf[self.symbol])
        self.df = nddf[self.symbol]
        self.df = self.df.set_index("date")
        self.row_count = self.df.shape[0]
        self.window_to = self.row_count
        self.window_from = self.row_count - self.window_size
        print(self.df)

        self.fig = mpf.figure(style='yahoo',
                              figsize=(16, 8),
                              tight_layout=False,
                              dpi=80)

        self.fig.subplots_adjust(hspace=0.001, wspace=0, left=0.07)
        self.fig.patch.set_facecolor('#d8d5ca')
        self.fig.suptitle(self.symbol, fontsize=16)

        self.ax1 = self.fig.add_subplot(6, 1, (1, 4))
        self.ax1.set_facecolor('#ffffff')
        self.ax1.patch.set_edgecolor('black')
        self.ax1.patch.set_linewidth('1')

        self.ax2 = self.fig.add_subplot(6, 1, 5, sharex=self.ax1)
        self.ax2.set_facecolor('#efefef')
        self.ax2.patch.set_edgecolor('black')
        self.ax2.patch.set_linewidth('1')

        self.ax3 = self.fig.add_subplot(6, 1, 6, sharex=self.ax1)
        self.ax3.set_facecolor('#ffffff')
        self.ax3.patch.set_edgecolor('#000000')
        self.ax3.patch.set_linewidth('1')

        ap = [mpf.make_addplot(self.df.iloc[self.window_from:self.window_to],
                               type='candle',
                               ax=self.ax2,
                               ylabel='OHLC Price')
              # mpf.make_addplot(nddf[self.symbol].iloc[self.window_from:self.window_to][['Low', 'High']], ax=ax1)
              ]

        mpf.plot(self.df.iloc[self.window_from:self.window_to],
                 ax=self.ax1,
                 volume=self.ax3,
                 addplot=ap,
                 xrotation=10,
                 type='candle')
        # fill_between=dict(y1=df['senkou_a'].values, y2=df['senkou_b'].values,
        #                   color='#f2ad73', alpha=0.20),

        tm = self.fig.canvas.manager.toolmanager
        tm.add_tool("<-", NewTool1)
        tm = self.fig.canvas.manager.toolmanager
        tm.add_tool("->", NewTool2)
        self.fig.canvas.manager.toolbar.add_tool(tm.get_tool("<-"), "toolgroup")
        self.fig.canvas.manager.toolbar.add_tool(tm.get_tool("->"), "toolgroup")

        self.axes = self.fig.axes
        self.fig.show()

    def window_minus(self, step):
        self.window_to = self.window_to - step
        self.window_from = self.window_to - self.window_size
        if self.window_from <= 0:
            self.window_from = 0
            self.window_to = self.window_from + self.window_size

    def window_plus(self, step):
        self.window_to = self.window_to + step
        if self.window_to > self.row_count:
            self.window_to = self.row_count
        self.window_from = self.window_to - self.window_size




# class nchart_last():
#
#     def __init__(self):
#         self.symbol = ""
#         self.df = pd.DataFrame(None)
#         self.row_count = 0
#         self.window_size = 120
#         self.window_to = 0
#         self.window_from = 0
#         self.fig = ""
#         self.axes = ""
#         self.last_block_count = 2
#         self.stock = n_date_frame()
#
#     def show(self):
#         self.stock.get_last_m(self.symbol, str(self.window_size * self.last_block_count))
#         if db.row_count > 0:
#             i_chart_df = self.stock.df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, errors="raise")
#             self.df = tools.convert_df_to_csvdf(i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']])
#             i_in_time, i_out_time = trade.time_filter(self.df)
#             self.df = i_in_time
#             # self.ap = [mpf.make_addplot(self.df['Close'], panel=2, type='line', ylabel='Line', mav=(5, 10)),
#             #       mpf.make_addplot(self.df['Open'], panel=3, type='bar', ylabel='Line2')]
#             # self.fig, self.axes = mpf.plot(self.df, mav=10, type='candle', ylabel='Candle', addplot=self.ap, panel_ratios=(3, 1, 1, 1), figratio=(11, 5),
#             #          figscale=1, volume=True, tight_layout=True, title=self.symbol, returnfig=True)
#
#             self.row_count = self.df.shape[0]
#             self.window_to = self.row_count
#             self.window_from = self.row_count - self.window_size
#             self.fig, self.axes = mpf.plot(self.df.iloc[self.window_from:self.window_to], type='candle', figratio=(17, 6), figscale=.8,
#                                            volume=True, show_nontrading=True, tight_layout=True, title=self.symbol, returnfig=True)
#             tm = self.fig.canvas.manager.toolmanager
#             tm.add_tool("<-", NewTool1)
#             tm = self.fig.canvas.manager.toolmanager
#             tm.add_tool("->", NewTool2)
#             self.fig.canvas.manager.toolbar.add_tool(tm.get_tool("<-"), "toolgroup")
#             self.fig.canvas.manager.toolbar.add_tool(tm.get_tool("->"), "toolgroup")
#
#             self.ax_main = self.axes[0]
#             self.ax_volu = self.axes[2]
#
#             self.fig.show()
#
#         else:
#             log("no data found in df")
#
#     def window_minus(self, step):
#         self.window_to = self.window_to - step
#         self.window_from = self.window_to - self.window_size
#         if self.window_from < ((step*2)+1):
#             log("start: db.get_last_m for chart " + self.symbol, True, False)
#             old_row_count = self.row_count
#             self.last_block_count += 1
#             self.stock.get_last_m(self.symbol, str(self.window_size * self.last_block_count))
#             if db.row_count > 0:
#
#                 i_chart_df = self.stock.df.rename(
#                     columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"},
#                     errors="raise")
#                 self.df = tools.convert_df_to_csvdf(i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']])
#                 i_in_time, i_out_time = trade.time_filter(self.df)
#                 self.df = i_in_time
#                 self.row_count = self.df.shape[0]
#                 groving = self.row_count - old_row_count
#                 self.window_from = self.window_from + groving
#                 self.window_to = self.window_to + groving
#             log("ready.", False, False)
#
#
#     def window_plus(self, step):
#         self.window_to = self.window_to + step
#         if self.window_to > self.row_count:
#             self.window_to = self.row_count
#         self.window_from = self.window_to - self.window_size




def ndf_chart_last(symbol="", xminute="60", p3=""):
    nchart.symbol = symbol
    nchart.show()


# md programs -------------------------------------------------------------------------------------------------------


def md_check(symbol="", p2="", p3=""):
    if md.check_finnhub_connection(symbol):
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")


# wl programs -------------------------------------------------------------------------------------------------------


def wl_add(symbol="", p2="", p3=""):
    wl.add(symbol)
    # ndf.check(symbol)
    gui.refresh_ui()


def wl_remove(symbol="", p2="", p3=""):
    wl.remove(symbol)
    gui.refresh_ui()


def wl_refresh_close(p1="", p2="", p3=""):
    wl.refresh_close()
    gui.refresh_ui()


def wl_refresh_profile(p1="", p2="", p3=""):
    wl.refresh_profile()
    gui.refresh_ui()


def wl_refresh_sentiment(p1="", p2="", p3=""):
    wl.refresh_sentiment()
    gui.refresh_ui()


def bp_start(p1="", p2="", p3=""):
    # bp.start()
    return


def bp_stop(p1="", p2="", p3=""):
    # bp.stop()
    return


# PROGRAMS fo wl buttons----------------------------------------------------------------------------


def wl_trade_short(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    trade.order['symbol'] = symbol
    trade.order['position'] = "SHORT"
    trade.order['limit_price'] = 123.123
    trade.order['qt'] = int(trade.config["trade_block_size"] / trade.order['limit_price'])
    i_stop_margin = round(trade.order['limit_price'] * (trade.config["stop_margin"] / 100), 2)
    trade.order['stop_price'] = trade.order['limit_price'] + i_stop_margin
    gui.set_trade_frame()


def wl_trade_long(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    trade.order['symbol'] = symbol
    trade.order['position'] = "LONG"
    trade.order['limit_price'] = 123.123
    trade.order['qt'] = int(trade.config["trade_block_size"] / trade.order['limit_price'])
    i_stop_margin = round(trade.order['limit_price'] * (trade.config["stop_margin"] / 100), 2)
    trade.order['stop_price'] = trade.order['limit_price'] - i_stop_margin
    gui.set_trade_frame()


def wl_btn_chart(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: ndf.chart.last " + symbol, True, False)
    ndf_chart_last(symbol)
    log("ready.", False, False)


def wl_btn_show(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: ndf2.show.last " + symbol, True, False)
    ndf2_show_last(symbol)
    log("ready.", False, False)

# PROGRAMS fo Tr buttons----------------------------------------------------------------------------


def tr_cancel():
    gui.Tr_frame.hide()


def tr_portfolio_monitor():
    if gui.Tr_portfolio_monitor.checkState():
        trade.monitor_run()
    else:
        trade.monitor_stop()

# Back_processes -----------------------------------------------------


class back_processes(object):
    def __init__(self, interval=60):
        self.interval = interval
        self.kill = False
        self.runnig = False
        self.start()

    def stop(self):
        self.kill = True
        log("bp-> stopped")

    def start(self):
        if self.runnig:
            log("bp-> already running...")
        else:
            log("bp-> started")
            self.kill = False
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            self.runnig = True
            thread.start()
        return

    def run(self):
        while True:
            # More statements comes here
            # print(datetime.now().__str__() + ' : Start task in the background')
            wl.refresh_close()
            gui.refresh_ui()
            time.sleep(self.interval)
            if self.kill:
                self.runnig = False
                break

# Socket ----------------------------------------------------


class ListenWebsocket(QtCore.QThread):
    def __init__(self, parent=None):
        super(ListenWebsocket, self).__init__(parent)
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=bs9c9lvrh5rahoaofmt0",
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close
                                        )
        self.cdx = 1
        self.cont_datetime = datetime.now()

    def on_message(self, message):
        # print(message)
        # print(datetime.now(), self.cont_datetime)
        duration = datetime.now() - self.cont_datetime
        duration_in_s = int(duration.total_seconds())
        # print(duration_in_s)
        # print(duration_in_s)
        if duration_in_s > 15:
            s(message)
            # print("segg")
            # print(datetime.now())
            # print(self.cont_datetime)
            self.cont_datetime = datetime.now()

    def on_error(self, error):
        print("error" + error)

    def on_close(self):
        print("Status: FinnHub socket closed")

    def on_open(self):

        self.ws.send('{"type":"subscribe","symbol":"AAPL"}')
        # self.ws.send('{"type":"subscribe","symbol":"AMZN"}')
        self.ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
        # self.ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')
        print("Status: FinnHub socket opened")

    def run(self):
        self.ws.on_open = self.on_open
        self.ws.run_forever()


if __name__ == "__main__":

    # 1.
    # Create a DataFrame so 'ta' can be used.
    # df = pd.DataFrame()
    # List of all indicators
    # df.ta.indicators()
    # help(ta.sma)



    print("Status: Reading nDot data frame")
    nddf = {}
    nddb = nd_db()
    ndf2 = n_date_frame2()
    trade = trade()
    print("Status: GUI Load")
    app = QApplication([])
    gui = gui()
    nsys = n_system
    # db = data_base()
    md = market_data()
    wl = watch_list()
    gui.refresh_ui()
    # gui.showFullScreen()
    gui.showMaximized()
    tools = tools()
    # ndf = n_date_frame()
    nchart = nchart_last()

    tlog("MSFT SET LONG", line=True, indent=False, color="long")
    tlog("MSFT LONG Qt:15000 Limit price: 253.12 Stop price: 260.12", line=False, indent=True, color="stop")
    tlog("MSFT LONG Qt:15000 Limit price: 253.12 Stop price: 260.12", line=False, indent=True, color="normal")
    tlog("MSFT LONG Qt:15000 Limit price: 253.12 Stop price: 260.12", line=False, indent=True, color="long")
    tlog("MSFT LONG Qt:15000 Limit price: 253.12 Stop price: 260.12", line=False, indent=True, color="short")
    tlog("MSFT LONG Qt:15000 Limit price: 253.12 Stop price: 260.12", line=False, indent=True, color="stop")
    # gui.show()
    print("Status: GUI is running")
    # ws.on_open = on_open
    # ws.run_forever()
    # threadpool = QThreadPool()
    # worker = ws.run_forever
    # threadpool.start(worker)


    # wst = threading.Thread(worker)
    # wst.daemon = True
    # wst.start()
    # 3. háttér futásindítás 60 másodpercenkénti futás
    # bp = back_processes()

    sys.exit(app.exec_())
# # TensorFlow CNN model training example
# # based on https://www.tensorflow.org/tutorials/images/cnn
# from __future__ import absolute_import, division, print_function, unicode_literals
#
# from random import randrange
# import tensorflow as tf
#
#
# from tensorflow.keras import datasets, layers, models
# import matplotlib.pyplot as plt
#
# from tensorflow.keras.models import load_model
# import numpy as np
# import sys
#
#
#
#
# (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
#
#
# # train_images_one_layer = (0.2989*train_images[:,:,:,0]+0.5870*train_images[:,:,:,1]+0.1140*train_images[:,:,:,2])
# # test_images_one_layer = (0.2989*test_images[:,:,:,0]+0.5870*test_images[:,:,:,1]+0.1140*test_images[:,:,:,2])
# # train_images_one_layer, test_images_one_layer = train_images_one_layer / 255.0, test_images_one_layer / 255.0
#
# #
# # print (train_images_one_layer)
# #
# # # Normalize pixel values to be between 0 and 1
# train_images, test_images = train_images / 255.0, test_images / 255.0
# #
# class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
#                'dog', 'frog', 'horse', 'ship', 'truck']
#
# # plt.figure(figsize=(10,10))
# # for i in range(100):
# #     plt.subplot(10,10,i+1)
# #     plt.xticks([])
# #     plt.yticks([])
# #     plt.grid(False)
# #     plt.imshow(train_images_one_layer[i], cmap=plt.cm.binary)
# #     # The CIFAR labels happen to be arrays,
# #     # which is why you need the extra index
# #     plt.xlabel(class_names[train_labels[i][0]])
# # plt.show()
#
# # sys.exit()
#


# model = models.Sequential()
# model.add(layers.InputLayer(input_shape=(32, 32,3)))
# # model.add(layers.Conv2D(32, (3, 3), activation='relu'))
# # model.add(layers.MaxPooling2D((2, 2)))
# # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# # model.add(layers.MaxPooling2D((2, 2)))
# # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# model.add(layers.Flatten())
# model.add(layers.Dense(2048, activation='relu'))
# model.add(layers.Dense(1024, activation='relu'))
# model.add(layers.Dense(512, activation='relu'))
# model.add(layers.Dense(256, activation='relu'))
# model.add(layers.Dense(128, activation='relu'))
#
# # model.add(layers.Dense(256, activation='relu'))
# # model.add(layers.Dense(128, activation='relu'))
# model.add(layers.Dense(10, activation='softmax'))
# model.summary()
#
# model.compile(optimizer='Adamax',
#               loss='sparse_categorical_crossentropy',
#               metrics=['accuracy'])
#
# history = model.fit(train_images, train_labels, epochs=25,
#                     validation_data=(test_images, test_labels))
#
# model.save('my_model.h5')
#
# # print("itt")
# # print (history.history)
# #
# # plt.plot(history.history['accuracy'], label='accuracy')
# # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
# # plt.xlabel('Epoch')
# # plt.ylabel('Accuracy')
# # plt.ylim([0, 2])
# # plt.legend(loc='lower right')
# # plt.show()
# #
# # test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
# # print(test_acc)
# #
# #
#
#
# model = load_model('my_model.h5')
#
# (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
#
# # train_images_one_layer = (0.2989*train_images[:,:,:,0]+0.5870*train_images[:,:,:,1]+0.1140*train_images[:,:,:,2])
# # test_images_one_layer = (0.2989*test_images[:,:,:,0]+0.5870*test_images[:,:,:,1]+0.1140*test_images[:,:,:,2])
# # train_images, test_images = train_images_one_layer / 255.0, test_images_one_layer / 255.0
#
#
#
# # Normalize pixel values to be between 0 and 1
# train_images, test_images = train_images / 255.0, test_images / 255.0
#
# class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
#                'dog', 'frog', 'horse', 'ship', 'truck']
#
# def plot_image(i, predictions_array, true_label, img):
#   predictions_array, true_label, img = predictions_array, true_label[i][0], img[i]
#   plt.grid(False)
#   plt.xticks([])
#   plt.yticks([])
#
#   plt.imshow(img, cmap=plt.cm.binary)
#
#   predicted_label = np.argmax(predictions_array)
#   if predicted_label == true_label:
#     color = 'blue'
#   else:
#     color = 'red'
#
#   plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
#                                 100*np.max(predictions_array),
#                                 class_names[true_label]),
#                                 color=color)
#
# def plot_value_array(i, predictions_array, true_label):
#   predictions_array, true_label = predictions_array, true_label[i][0]
#   plt.grid(False)
#   plt.xticks(range(10))
#   plt.yticks([])
#   thisplot = plt.bar(range(10), predictions_array, color="#777777")
#   plt.ylim([0, 1])
#   predicted_label = np.argmax(predictions_array)
#
#   thisplot[predicted_label].set_color('red')
#   thisplot[true_label].set_color('blue')
#
#
# for ix in range(10):
#     i = randrange(50)
#     predictions = model.predict(train_images[i:i+1])
#     print(predictions)
#
#     plt.figure(figsize=(6,3))
#     plt.subplot(1,2,1)
#     plot_image(i, predictions[0], train_labels, train_images)
#     plt.subplot(1,2,2)
#     plot_value_array(i, predictions[0],  train_labels)
#     plt.show()
#
# for ix in range(10):
#     i = randrange(50)
#     predictions = model.predict(test_images[i:i+1])
#     print(predictions/10)
#
#     plt.figure(figsize=(6,3))
#     plt.subplot(1,2,1)
#     plot_image(i, predictions[0], test_labels, test_images)
#     plt.subplot(1,2,2)
#     plot_value_array(i, predictions[0],  test_labels)
#     plt.show()
