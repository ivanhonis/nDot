# This Python file uses the following encoding: utf-8
from datetime import datetime, timedelta
import sys
import websocket
import time
import mysql.connector
from mysql.connector import Error
import random
import pandas as pd
import finnhub
import threading
import numpy as np
from functools import partial
from tkinter import *
# import matplotlib.animation as animation
# import matplotlib.dates as mdates

# from pandasgui.datasets import pokemon, titanic, all_datasets

# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QProgressBar
# from PyQt5.QtCore import *
# from datetime import timedelta
# from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtCore import QTime, QDate
# from PyQt5 import QtGui
# from PyQt5 import



class n_system:
    print_console = False


class data_base():
    open_close = True
    config = {
        'host': 'sql132.main-hosting.eu',
        'user': 'u826803502_AIS1',
        'password': '+1zZJqwQ',
        'database': 'u826803502_ArtIntSol',
        'connect_timeout': 90000,
        'raise_on_warnings': True,
        'use_pure': False
    }
    cnx = ""
    cursor = ""
    row_count = 0
    column_names = ""
    server_version = ""
    db_size = ""
    error = ""

    def open(self):
        # s("nDot db open")
        self.cnx = mysql.connector.connect(**self.config)
        self.cursor = self.cnx.cursor(buffered=True)
        return

    def setcursor(self):
        self.cursor = self.cnx.cursor(buffered=True)
        return

    def close(self):
        # s("nDot db close")
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        return

    def check_connection(self):
        log("db-> check_connection")
        i_return = False
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                i_return = True
                self.server_version = connection.get_server_info()
                cursor = connection.cursor()
                cursor.execute('SELECT table_schema AS "Database", ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" FROM information_schema.TABLES GROUP BY table_schema')
                record = cursor.fetchall()
                i_df = pd.DataFrame(record)
                self.db_size = i_df.iloc[1][1]
                cursor.close()
                connection.close()
        except Error as e:
            i_return = False
            self.error = e
        return i_return

    def execute_simply(self, sqlstr, multiple=False):

        def place_value(number):
            return ("{:,}".format(number))

        log("db-> execute_simply - SQL size:" + place_value(int(len(sqlstr)/1024)) + " KB")
        # pri(datetime.now(), "sql length", len(sqlstr))
        if self.open_close:
            self.open()
        self.cursor.execute(sqlstr)
        # print(datetime.now(), "close")
        if self.cursor.rowcount > 0:
            log("db-> execute_simply row(s) affected: " + str(self.cursor.rowcount))
        if self.open_close:
            self.close()
        return

    def execute_base(self, sqlstr, multiple=False):
        # log("db-> execute_base: " + sqlstr[:100])
        if self.open_close:
            self.open()

        try:
            self.cursor.execute(sqlstr)
        except mysql.connector.Error as err:
            log("db-> execute_base EXCEPT: {}".format(err)+" SQL: "+sqlstr[:150])
        else:
            if self.cursor.rowcount > 0:
                log("db-> execute_base row(s) affected: " + str(self.cursor.rowcount))
        # self.setcursor()
        if self.open_close:
            self.close()
        return

    def execute_fetchall(self, sqlstr):
        # log("db-> execute_fetchall: " + sqlstr[:100])
        if self.open_close:
            self.open()
        try:
            self.cursor.execute(sqlstr)
        except mysql.connector.Error as err:
            log("db-> execute_fetchall EXCEPT: {}".format(err))
            i_result = []
        else:
            if self.cursor.rowcount > 0:
                log("db-> execute_fetchall selected rows: " + str(self.cursor.rowcount))
                self.column_names = self.cursor.column_names
                self.row_count = self.cursor.rowcount
                i_result = self.cursor.fetchall()
            else:
                self.row_count = 0
                i_result = []
        if self.open_close:
            self.close()
        return i_result

    def get_timeframe(self, symbol, fromdt, todt):
        log("db-> get_timeframe " + symbol + " " + str(fromdt) + " - " + str(todt))
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `datetime`>='" +\
                       str(fromdt) + "' AND `datetime`<='" + str(todt) + "'"
        return self.execute_fetchall(i_sql_string)

    def get_timeframe_desc(self, symbol, fromdt, todt):
        log("db-> get_timeframe_desc " + symbol + " " + str(fromdt) + " - " + str(todt))
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `datetime`>='" +\
                       str(fromdt) + "' AND `datetime`<='" + str(todt) + "' ORDER BY `datetime` DESC"
        return self.execute_fetchall(i_sql_string)

    def get_first_m(self, symbol, elem_no):
        log("db-> get_first_m: " + symbol + " "+str(elem_no))
        i_sql_string = "SELECT * FROM `" + symbol + "` ORDER BY `datetime` ASC LIMIT " +str(elem_no)
        return self.execute_fetchall(i_sql_string)

    def get_last_m(self, symbol, elem_no):
        log("db-> get_last_m: " + symbol + " "+str(elem_no))
        i_sql_string = "SELECT * FROM `" + symbol + "` ORDER BY `datetime` DESC LIMIT " +str(elem_no)
        return self.execute_fetchall(i_sql_string)

    def add_symbol(self, symbol):
        log("db-> add_symbol " + symbol)
        i_sql_command = "CREATE TABLE IF NOT EXISTS`" + self.config['database'] + "`.`" + symbol + \
                        "` ( `datetime` DATETIME NOT NULL , UNIQUE `datetime_i` (`datetime`)) ENGINE = InnoDB"
        self.execute_base(i_sql_command)
        i_sql_command = "ALTER TABLE `" + symbol + "` ADD INDEX(`datetime`)"
        self.execute_base(i_sql_command)
        return

    def remove_symbol(self, symbol):
        log("db-> remove_symbol " + symbol)
        i_sql_command = "DROP TABLE IF EXISTS`"+self.config['database']+"`.`" + symbol + "`"
        self.execute_base(i_sql_command)
        return

    def add_symbol_float_property(self, symbol, prop):
        log("db-> add db " + symbol + " float prop: " + prop)
        i_sql_command = "ALTER TABLE `" + symbol + "` ADD IF NOT EXISTS`" + prop + \
                        "` DECIMAL(16,6) NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        return

    def add_symbol_string_property(self, symbol, prop, plength):
        log("db-> add db " + symbol + " string prop: " + prop)
        i_sql_command = "ALTER TABLE `" + symbol + "` ADD IF NOT EXISTS`" + prop + \
                        "` VARCHAR(" + str(plength) + ") NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        return

    # def add_instrument_value(self, instrument, dt, prop, val):
    #     i_sql_command = "SELECT * FROM `"+instrument+"` WHERE `datetime` = '"+dt+"'"
    #     if type(val) != str:
    #         val = str(val)
    #
    #     if self.execute_fetchall(i_sql_command):
    #         i_sql_command = "UPDATE `"+instrument+"` SET `"+prop+"`= '"+val+"' WHERE `datetime` = '"+dt+"'"
    #         self.execute_base(i_sql_command)
    #     else:
    #         i_sql_command = "INSERT INTO `"+instrument+"` SET datetime = '"+dt+"', "+prop+" = '"+val+"'"
    #         self.execute_base(i_sql_command)
    #     return

    def add_symbol_value_multi(self, symbol, dt_array, prop, val_array):
        log("db-> write to db "+symbol+" - "+prop +" estimated rows:" + str(len(dt_array)))
        sql_text = pd.DataFrame()
        sql_text["datetime"] = dt_array
        sql_text["val"] = val_array
        sql_text["val"] = sql_text["val"].apply(str)
        sql_text["when"] = "WHEN `datetime` = '"
        sql_text["then"] = "' THEN '"
        sql_text["then_end"] = "'"
        sql_text["sql_slice"] = sql_text["when"] + sql_text["datetime"] + sql_text["then"] + sql_text["val"] + sql_text["then_end"]
        # sql_text = sql_text.head()
        i_sql_when = ' '.join(sql_text["sql_slice"])
        i_sql_datetime = "','".join(sql_text["datetime"])
        i_sql_datetime = "'" + i_sql_datetime + "'"
        i_full_sql_text = "UPDATE " + symbol + " SET `" + prop + "` = CASE " +\
                    i_sql_when +\
                    " END WHERE `datetime` IN (" +i_sql_datetime + ")"
        self.execute_simply(i_full_sql_text)

    def add_symbol_values(self, instrument, df):
        i_elemet_block_size = 30000
        i_dt_rows = df.shape[0]
        log("db-> add_symbol_values: "+instrument+" estimated rows:" + str(i_dt_rows))
        i_dt_array_len = int(i_dt_rows / i_elemet_block_size)+1
        i_sql_elements_array = ["" for x in range(i_dt_array_len)]
        start_no = 0
        for i_i in range(i_dt_array_len):
            to_no = min(start_no+i_elemet_block_size, i_dt_rows)
            sql_texts = []
            for index, row in df.iloc[start_no:to_no].iterrows():
                sql_texts.append(str(tuple(row.values)))
            i_sql_elements_array[i_i] = ', '.join(sql_texts)
            start_no = start_no+i_elemet_block_size + 1
        for i_i in range(len(i_sql_elements_array)):
            i_sql_str = "INSERT INTO `" + instrument + "` " +\
                    "(`datetime` , `t`, `o`, `h`, `l`, `c`, `ohlc4`, `v`  ) VALUES " + \
                    i_sql_elements_array[i_i] +\
                    " ON DUPLICATE KEY UPDATE `datetime` = VALUES(datetime)"
            self.execute_base(i_sql_str)

    def qcheck(self, symbol):
        log("db-> qcheck: "+symbol)
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `t` is null or `c` is null or `l` is null or `h` is null or `o` is null or `ohlc4` is null or `v` is null"
        self.execute_fetchall(i_sql_string)
        null_count = self.row_count
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `t` = 0 or `c` = 0 or `l` = 0 or `h` = 0 or `o` = 0 or `ohlc4` = 0 or `v` = 0"
        self.execute_fetchall(i_sql_string)
        zero_count = self.row_count
        self.row_count = null_count + zero_count

    # def add_instrument_value_multi_tchk(self, instrument, dt_array, prop, val_array):
    #     s("write to db "+instrument+" - "+prop)
    #     i_dt_array_len = len(dt_array)
    #
    #     if prop == "t":
    #         self.add_instrument(instrument)
    #         self.add_instrument_float_property(instrument, prop)
    #         i_elemet_block_size = 32000
    #
    #         # beszúrom az üreseket, ha még nincsenek és utána minden módosítom
    #         i_sql_elements_array = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size))]
    #
    #         for i_i in range(i_dt_array_len):
    #             i_pos = int(i_i / i_elemet_block_size)
    #             i_sql_elements_array[i_pos] = i_sql_elements_array[i_pos] + "('" + dt_array[i_i] + "', '" + str(val_array[i_i]) + "'), "
    #
    #         for i_i in range(len(i_sql_elements_array)):
    #             i_sql_str = "INSERT INTO `" + instrument + "` " +\
    #                     "(`datetime` , `" + prop + "` ) VALUES " +\
    #                     i_sql_elements_array[i_i][:-2] +\
    #                     " ON DUPLICATE KEY UPDATE `datetime` = VALUES(datetime)"
    #             self.execute_base(i_sql_str)
    #     else:
    #         # minden sort lemódosítok
    #         self.add_instrument_float_property(instrument, prop)
    #         i_elemet_block_size2 = 32000
    #         i_sql_elements_array2 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]
    #         i_sql_elements_array3 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]
    #         # s("Update create 1")
    #         # for i_i2 in range(1):
    #         for i_i2 in range(i_dt_array_len):
    #             i_pos2 = int(i_i2 / i_elemet_block_size2)
    #             i_sql_elements_array2[i_pos2] = i_sql_elements_array2[i_pos2] +\
    #                                           "WHEN `datetime` = '" + dt_array[i_i2] +\
    #                                             "' THEN '" + str(val_array[i_i2]) + "' "
    #
    #             i_sql_elements_array3[i_pos2] = i_sql_elements_array3[i_pos2] +\
    #                                           "'" + dt_array[i_i2] + "',"
    #         # s("Update create 2")
    #         for i_i3 in range(len(i_sql_elements_array2)):
    #             i_sql_str2 = "UPDATE " + instrument + " SET `" + prop + "` = CASE " +\
    #                     i_sql_elements_array2[i_i3] +\
    #                     " END WHERE `datetime` IN (" + i_sql_elements_array3[i_i3][:-1] + ")"
    #             self.execute_simply(i_sql_str2)
    #     return

class market_data():
    api_key_finnhubio1 = "bs9c9lvrh5rahoaofmt0"
    finnhub_client = ""

    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key=self.api_key_finnhubio1)
        self.finnhub_client.DEFAULT_TIMEOUT = 100

    def check_finnhub_connection(self, symbol="AAPL"):
        log("md-> check_finnhub_connection")
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

    def get_stock_candles(self, symbol, resolution, from_dt, to_dt):
        log("md-> get_stock_candles: " + symbol + " - " + tools.unixdt_to_dbdt(from_dt) + " - " +
            tools.unixdt_to_dbdt(to_dt))
        i_df = pd.DataFrame(self.finnhub_client.technical_indicator(symbol=symbol, resolution=resolution, _from=from_dt, to=to_dt, indicator='rsi', indicator_fields={"timeperiod": 3}))
        # i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, resolution, from_dt, to_dt))
        i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
        i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
        i_df['ohlc4'] = round(((i_df['o'] + i_df['h'] + i_df['l'] + i_df['c'])/4), 6)
        i_df = i_df[['datetime', 't', 'o', 'h', 'l', 'c', 'ohlc4', 'v']]
        i_df = i_df.round({'t': 6, 'o': 6, 'h': 6, 'l': 6, 'c': 6, 'ohlc4': 6})
        i_df.set_index('datetime')
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
        i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
        i_df = i_df[['datetime', 't', 'rsi']]
        i_df = i_df.round({'rsi': 6})
        i_df.set_index('datetime')
        return i_df


class n_date_frame():
    df = pd.DataFrame(None)

    def add(self, symbol):
        log("ndf-> add " + symbol)
        i_now = datetime.now() + timedelta(days=1)
        i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
        i_datetime_series = pd.date_range(start=i_now, periods=7, freq='-63d')
        db.add_symbol(symbol)
        db.add_symbol_float_property(symbol, "v")
        db.add_symbol_float_property(symbol, "ohlc4")
        db.add_symbol_float_property(symbol, "o")
        db.add_symbol_float_property(symbol, "h")
        db.add_symbol_float_property(symbol, "l")
        db.add_symbol_float_property(symbol, "c")
        db.add_symbol_float_property(symbol, "t")
        for i_i in range(len(i_datetime_series)-1):
            i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=4)))
            i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
            i_df_stock = pd.DataFrame(None)
            i_df_stock = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix)
            db.add_symbol_values(symbol, i_df_stock)
        return

    def add_sma(self, symbol, window_size):

        def sma(i_df, window_size):
            i_c1_name = "SMA_" + str(window_size)
            i_df[i_c1_name] = i_df.iloc[:, i_df.columns.get_loc("ohlc4")].rolling(window=int(window_size)).mean()
            i_df[i_c1_name] = i_df[i_c1_name].fillna(0.123456)
            i_df[i_c1_name] = round(i_df[i_c1_name], 6)
            i_df['datetime'] = i_df["datetime"].astype(str)
            i_prop_array = [i_c1_name]
            return i_prop_array, i_df

        log("ndf-> add_rsi " + symbol + " - " + str(window_size))
        i_res = db.get_last_m(symbol, 1)
        i_df = pd.DataFrame(i_res)
        i_df.columns = db.column_names
        last_dbdt = str(i_df.iloc[0]['datetime'])

        i_res = db.get_first_m(symbol, 1)
        i_df = pd.DataFrame(i_res)
        i_df.columns = db.column_names
        first_dbdt = str(i_df.iloc[0]['datetime'])

        i_datetime_series = pd.DataFrame(pd.date_range(start=last_dbdt, end=first_dbdt, freq='-65d'))
        new_row = {0: first_dbdt}
        i_datetime_series = i_datetime_series.append(new_row, ignore_index=True)

        for i_i in range(len(i_datetime_series[0])-1):
            i_select_from = i_datetime_series.loc[i_i+1][0]
            i_select_to = i_datetime_series.loc[i_i][0] + timedelta(days=3)
            i_df = pd.DataFrame(None)
            i_df = pd.DataFrame(db.get_timeframe_desc(symbol, i_select_from, i_select_to))
            i_df = i_df.iloc[::-1]
            i_df.columns = db.column_names
            # print(db.column_names)
            # if "t" in db.column_names:
            #     print("t benne van")
            # if "SMA_70" in db.column_names:
            #     print("SMA_70 benne van")
            # else:
            #     print("SMA_70 NINCS benne")
            i_new_prop_array, i_df = sma(i_df, window_size)
            # print("prop array", i_new_prop_array)
            # print(i_df.head())
            for i_new_prop in i_new_prop_array:
                # print(i_new_prop)
                i_datetime = tools.get_df_column(i_df, "datetime")
                i_values = tools.get_df_column(i_df, i_new_prop)
                if i_new_prop not in db.column_names:
                    db.add_symbol_float_property(symbol, i_new_prop)
                db.add_symbol_value_multi(symbol, i_datetime, i_new_prop, i_values)
        return

    def refresh(self, symbol):
        log("ndf-> refresh " + symbol)
        to_dbdt = datetime.now() + timedelta(days=1)
        to_dbdt = to_dbdt.strftime('%Y-%m-%d %H:%M:%S')
        i_res = db.get_last_m(symbol, 1)
        i_df = pd.DataFrame(i_res)
        i_df.columns = db.column_names
        from_dbdt = str(i_df.iloc[0]['datetime'])
        i_tounix = tools.dbdt_to_unixdt(to_dbdt)
        i_fromunix = tools.dbdt_to_unixdt(from_dbdt)
        i_df_stock = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix)
        db.add_symbol_values(symbol, i_df_stock)
        return

    def get_last_m(self, symbol, xm):
        log("ndf-> get " + symbol + " last " + xm + " minutes")
        i_res = db.get_last_m(symbol, xm)
        if db.row_count > 0:
            df = pd.DataFrame(i_res)
            df.columns = db.column_names
            self.df = df.iloc[::-1]
        else:
            self.df = pd.DataFrame(None)
        return

    def get_time_frame(self, symbol):
        log("ndf-> get_time_frame " + symbol + " use gui date time")
        i_db_dt_from = tools.get_ui_date_dbdt("from")
        i_db_dt_to = tools.get_ui_date_dbdt("to")
        i_res = db.get_timeframe(symbol, i_db_dt_from, i_db_dt_to)
        if db.row_count > 0:
            df = pd.DataFrame(i_res)
            df.columns = db.column_names
            self.df = df
        else:
            self.df = pd.DataFrame(None)
        return

    def check(self, symbol):
        log("ndf-> check " + symbol)
        db.qcheck(symbol)
        if db.row_count > 0:
            log("  Data quality ERROR: " + symbol)
        else:
            log("  Data quality OK: " + symbol)
        return


# class n_strategy():
#     n = ""
#
#     def add_rsi(self, symbol):
#         s("add RSI - " + symbol)
#         i_now = datetime.now() + timedelta(days=1)
#         i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
#         i_datetime_series = pd.date_range(start=i_now, periods=7, freq='-63d')
#         for i_i in range(len(i_datetime_series)-1):
#             i_tounix = tools.dbdt_to_unixdt(str((i_datetime_series[i_i] + timedelta(days=4))))
#             i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
#             s("get data RSI " + symbol + " - " + str(i_datetime_series[i_i] + timedelta(days=4)) + " - " + str(i_datetime_series[i_i+1]))
#             i_df_stock = pd.DataFrame(None)
#             i_df_stock = md.technical_indicator_rsi(symbol, "1", i_fromunix, i_tounix)
#             i_datetime = tools.get_df_column(i_df_stock, "datetime")
#
#             db_act1 = data_base()
#             ci1 = tools.get_df_column(i_df_stock, "rsi")
#             db_act1.add_symbol_value_multi(symbol, i_datetime, "rsi", ci1)
#         return


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
        ndf.add(symbol)
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
    progress_count = 0
    commands = ""
    sx = datetime.now()

    def __init__(self):
        super(gui, self).__init__()
        self.load_ui()
        self.load_commands()
        # self.thread = ListenWebsocket()
        # self.thread.start()
        return

    def load_commands(self):
        c = [
            ['do', 'do', 'Do what you want', 0],
            ['test', 'test', 'test <p1 (optional), p2 (optional), p3 (optional)>', 0],
            ['sys.print', 'sys_print', 'sys.print <True/False> ', 1],
            ['wl.add', 'wl_add', 'wl.add <symbol> ', 1],
            ['wl.remove', 'wl_remove', 'wl.remove <symbol> ', 1],
            # ['wl.refresh.close', 'wl_refresh_close', 'wl.refresh.close <> ', 0],
            ['wl.refresh.profile', 'wl_refresh_profile', 'wl.refresh.profile <> ', 0],
            ['wl.refresh.sentiment', 'wl_refresh_sentiment', 'wl.refresh.sentiment <> ', 0],
            # ['wl.refresh.all', 'wl_refresh_all', 'wl.refresh.all <> ', 0],
            ['ndf.add', 'ndf_add', 'ndf.add <symbol> ', 1],
            ['ndf.refresh', 'ndf_refresh', 'ndf.refresh <symbol> ', 1],
            ['ndf.remove', 'ndf_remove', 'ndf.remove <symbol> ', 1],
            ['ndf.check', 'ndf_check', 'ndf.check <symbol> ', 1],
            ['ndf.chart', 'ndf_chart', 'ndf.chart <symbol> ui date time', 1],
            ['ndf.chart.last', 'ndf_chart_last', 'ndf.chart.last <symbol, numbers (optional)> ', 1],
            ['ndf.show.last', 'ndf_show_last', 'ndf.show.last <symbol, numbers (optional)> ', 1],
            ['ndf.tech', 'ndf_tech', 'ndf.tech <symbol, <technical indicator> ', 2],
            ['md.check', 'md_check', 'md.check <symbol> ', 1],
            # ['bp.start', 'bp_start', 'bp.start <> ', 0],
            # ['bp.stop', 'bp_stop', 'bp.stop <> ', 0],
            ['exit', 'exit', 'exit <> ', 0]
        ]
        self.commands = pd.DataFrame(c)
        self.commands.columns = ['command', 'program', 'hint', 'params']
        self.commands.set_index('command')
        return

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
        self.Command_Line.setText("ndf.tech PENN SMA")
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
        self.From_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.From_T.setTime(QTime(i_now.hour, i_now.minute))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
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

        for i_obj in i_wl_frame_object:
            i_obj.hide()
        i_no = 0
        for index, row in wl.df.iterrows():
            i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setText(row['symbol'])
            i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setToolTip(row['profil'])
            i_wl_frame_object[i_no].findChild(QLabel, "WL_c"+i_noid[i_no]).setText(str(round(row['c'], 2)))
            if row['c'] > row['pc']:
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▲")
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: green; background: #ffffff;")
            else:
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▼")
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: red; background: #ffffff;")

            nn_drop1 = random.randint(0, 50)
            nn_drop2 = random.randint(0, 50)
            nn_drop3 = 100 - nn_drop1 - nn_drop2

            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_long"+i_noid[i_no]).setText("L:"+str(nn_drop1) + "%")
            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_neutral"+i_noid[i_no]).setText("N:"+str(nn_drop3) + "%")
            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_short"+i_noid[i_no]).setText("S:"+str(nn_drop2) + "%")
            i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bull"+i_noid[i_no]).setValue(int(row['snt_bullish']*100))
            i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bear"+i_noid[i_no]).setValue(int(row['snt_bearish']*100))
            i_wl_frame_object[i_no].show()
            i_no = i_no + 1

    def date_now(self):
        i_now = datetime.now()
        self.To_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))

    def date_modifier(self, interval_type, interval_num):
        i_nowp = datetime.now() - timedelta(**{interval_type: interval_num})
        self.From_D.setSelectedDate(QDate(i_nowp.year, i_nowp.month, i_nowp.day))
        self.From_T.setTime(QTime(i_nowp.hour, i_nowp.minute))

    def progress_action(self):
        # self.progress_count = self.progress_count + 5
        # if self.progress_count > 100:
        #     self.progress_count = 0
        self.Progress_Bar.setValue(random.randint(0, 100))

    def run_button_action(self):
        command_text = self.Command_Line.text()
        command_partitioned = command_text.split()
        command_text_first_word = str.lower(command_partitioned[0])
        args = []
        if len(command_partitioned) == 2:
            args = [command_partitioned[1]]
        if len(command_partitioned) == 3:
            args = [command_partitioned[1], command_partitioned[2]]
        if len(command_partitioned) == 4:
            args = [command_partitioned[1], command_partitioned[2], command_partitioned[3]]

        i_found, i_program, i_hint, i_params = self.get_command(command_text_first_word)
        if i_found and i_params < len(command_partitioned):
            method = eval(i_program)
            kwargs = {}
            args_str = ', '.join(map(str, args))
            log("start: " + command_text_first_word + " <" + args_str + ">", True, False)
            method(*args, **kwargs)
            log("ready.", False, False)
            self.Command_Line.setText("")
        else:
            if i_found and i_params > len(command_partitioned):
                self.Command_Hint.setText(self.Command_Hint.text() + " Missing parameter(s)!")
            self.Command_Line.setStyleSheet('background-color: #ffaaaa; ' +\
                                            'border-top-left-radius: 15px;' +\
                                            'border-top-right-radius: 0px;' +\
                                            'border-bottom-right-radius: 0px;' +\
                                            'border-bottom-left-radius: 0px;' +\
                                            'border-bottom: 1px solid #eeeeee;' +\
                                            'padding-left: 10px;')

    def command_line_changed(self):
        self.Command_Line.setStyleSheet('background-color: #ffffff; ' + \
                                        'border-top-left-radius: 15px;' + \
                                        'border-top-right-radius: 0px;' + \
                                        'border-bottom-right-radius: 0px;' + \
                                        'border-bottom-left-radius: 0px;' + \
                                        'border-bottom: 1px solid #eeeeee;' + \
                                        'padding-left: 10px;')
        command_text = self.Command_Line.text()
        command_text_first_word = command_text.partition(' ')[0]
        i_found, i_program, i_hint, i_params = self.get_command(command_text_first_word)
        if i_found:
            self.Command_Hint.setText(i_hint)
        else:
            self.Command_Hint.setText("")


# PROGRAMS ----------------------------------------------------------------------------


def do(symbol="", p2="", p3=""):
    # stock = n_date_frame()
    # stock.add_last(symbol, 1)
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
        i_log_text = gui.Logs_Browser.toPlainText() + "─" * 82 + "\r"
        gui.Logs_Browser.setText(i_log_text)
    i_log_text = gui.Logs_Browser.toPlainText() + time.strftime("%m-%d %H:%M:%S") + " > " + i_ind + add_text + " \r"
    gui.Logs_Browser.setText(i_log_text)
    gui.Logs_Browser.moveCursor(QtGui.QTextCursor.End)
    QApplication.processEvents()


def test(p1="", p2="", p3=""):
    log("2/1. This is a test log message.")
    log("2/2. This is a test log message.")
    s("This is a test status message")

    if db.check_connection():
        log("  Server version: " + db.server_version)
        log("  Data base size: " + str(db.db_size) + " MB")
    else:
        log("  Error: " + str(db.error.msg))

    if md.check_finnhub_connection():
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")


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


def ndf_add(symbol="", p2="", p3=""):
    ndf.add(symbol)
    ndf.check(symbol)


def ndf_tech(symbol, tech_indicator, p3=""):
    ndf.add_sma(symbol, 60)


def ndf_refresh(symbol="", p2="", p3=""):
    ndf.refresh(symbol)
    # ndf.check(symbol)
    # gui.refresh_ui()


def ndf_remove(symbol="", p2="", p3=""):
    db.remove_symbol(symbol)


def ndf_check(symbol="", p2="", p3=""):
    ndf.check(symbol)


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
        fig = mpf.figure(style='yahoo', figsize=(20, 10), dpi=60, facecolor='white', edgecolor='k', tight_layout=True,
                         num=symbol)
        ax1 = fig.add_subplot(4, 1, (1, 3))
        ax2 = fig.add_subplot(4, 1, 4, sharex=ax1)
        plt.subplots_adjust(hspace=.001)
        mpf.plot(quote, ax=ax1, volume=ax2, axtitle='')
        mpf.show()
    else:
        log("no data found in df")


def ndf_chart_last(symbol="", xminute="60", p3=""):
    stock = n_date_frame()
    stock.get_last_m(symbol, xminute)
    if db.row_count > 0:
        log("ndf_chart_last-> plot chart")
        i_chart_df = stock.df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"},errors="raise")
        quote = tools.convert_df_to_csvdf(i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']])
        import matplotlib.pyplot as plt
        import mplfinance as mpf
        fig = mpf.figure(style='yahoo', figsize=(20, 10), dpi=60, facecolor='white', edgecolor='k', tight_layout=True,
                         num=symbol)
        ax1 = fig.add_subplot(4, 1, (1, 3))
        ax2 = fig.add_subplot(4, 1, 4, sharex=ax1)
        plt.subplots_adjust(hspace=.001)
        mpf.plot(quote, ax=ax1, volume=ax2, axtitle='')
        mpf.show()
    else:
        log("no data found in df")


def ndf_show_last(symbol="", xminute="60", p3=""):
    stock = n_date_frame()
    stock.get_last_m(symbol, xminute)
    if db.row_count > 0:
        # i_df_s = pd.DataFrame(None)
        # stock.df['o'] = stock.df['o'].astype(float)
        # stock.df['h'] = stock.df['h'].astype(float)
        # stock.df['l'] = stock.df['l'].astype(float)
        # stock.df['c'] = stock.df['c'].astype(float)
        # i_df_s['ohlc4'] = stock.df['ohlc4'].astype(float)
        # i_df_s['v'] = stock.df['v'].astype(int)
        # # i_df = i_df.round({'o': 6, 'h': 6, 'l': 6, 'c': 6, 'ohlc4': 6, 'v': 0})
        # i_df_s.set_index('datetime')


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

                self.table = pt = Table(f, dataframe=stock.df,
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
        log("no data found in df")


# md programs -------------------------------------------------------------------------------------------------------


def md_check(symbol="", p2="", p3=""):
    if md.check_finnhub_connection(symbol):
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")



# wl programs -------------------------------------------------------------------------------------------------------


def wl_add(symbol="", p2="", p3=""):
    wl.add(symbol)
    ndf.check(symbol)
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


def wl_btn_chart(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: ndf.chart.last " + symbol, True, False)
    ndf_chart_last(symbol)
    log("ready.", False, False)


def wl_btn_show(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: ndf.show.last " + symbol, True, False)
    ndf_show_last(symbol)
    log("ready.", False, False)

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
    print("Status: GUI Load")
    app = QApplication([])
    gui = gui()

    nsys = n_system
    db = data_base()
    md = market_data()
    wl = watch_list()
    gui.refresh_ui()
    # gui.showFullScreen()
    gui.showMaximized()
    tools = tools()
    ndf = n_date_frame()

    # nsrg = strategy()
    # nsrg.add_rsi("APA")

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
