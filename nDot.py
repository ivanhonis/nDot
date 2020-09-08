# This Python file uses the following encoding: utf-8
import sys
# import os
# import requests

import time
# import json
import mysql.connector
# import sqlite3
import threading
import random
import pandas as pd
import finnhub
import threading

from datetime import datetime, timedelta
from datetime import timedelta
from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTime, QDate
import mplfinance as mpf
import numpy as np
import io
from io import StringIO
from functools import partial
import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class ais_db():
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
    # host = "sql132.main-hosting.eu"
    # user = "u826803502_AIS1"
    # password = "+1zZJqwQ"
    database = "u826803502_ArtIntSol"
    column_names = ""

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

    def execute_simply(self, sqlstr, multiple=False):
        s("db execute simply: " + sqlstr[:150])
        if self.open_close:
            self.open()

        self.cursor.execute(sqlstr)

        if self.open_close:
            self.close()
        return

    def execute_base(self, sqlstr, multiple=False):
        main_widget.progress_action()
        s("db execute: " + sqlstr[:150])
        if self.open_close:
            self.open()

        try:
            self.cursor.execute(sqlstr)
        except mysql.connector.Error as err:
            s("Something went wrong: {}".format(err))
        else:
            if self.cursor.rowcount > 0:
                main_widget.add_log("  inserted rows: " + str(self.cursor.rowcount))
        # self.setcursor()
        if self.open_close:
            self.close()
        return

    def execute_fetchall(self, sqlstr):
        s("execute_fetchall")
        if self.open_close:
            self.open()
        try:
            self.cursor.execute(sqlstr)
        except mysql.connector.Error as err:
            s("Something went wrong: {}".format(err))
            i_result = []
        else:
            if self.cursor.rowcount > 0:
                main_widget.add_log("rows: " + str(self.cursor.rowcount))
                self.column_names = self.cursor.column_names
                self.row_count = self.cursor.rowcount
                i_result = self.cursor.fetchall()
            else:
                self.row_count = 0
                i_result = []
        if self.open_close:
            self.close()
        return i_result

    def is_timeframe_exist(self, isymbol, fromdt, todt):
        # print("is_time", isymbol,fromdt,todt)
        i_sql_string_from = "SELECT * FROM `" + isymbol + "` WHERE `datetime` = '" + fromdt + "'"
        i_sql_string_to = "SELECT * FROM `" + isymbol + "` WHERE `datetime` = '" + todt + "'"
        # print("from",i_sql_string_from)
        # print("to",i_sql_string_to)
        i_result_from = self.execute_fetchall(i_sql_string_from)
        # print(i_result_from)
        i_result_to = self.execute_fetchall(i_sql_string_to)
        return len(i_result_from) > 0 and len(i_result_to) > 0

    def get_timeframe(self, symbol, fromdt, todt):
        s("get_timeframe")
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `datetime`>='" +\
                       fromdt + "' AND `datetime`<='" + todt + "'"
        s(i_sql_string)
        return self.execute_fetchall(i_sql_string)

    def add_instrument(self, symbol):
        s("add symbol to db: " + symbol)
        i_sql_command = "CREATE TABLE IF NOT EXISTS`" + self.database + "`.`" + symbol + \
                        "` ( `i` INT NOT NULL AUTO_INCREMENT , `datetime` DATETIME NOT NULL , " + \
                        "PRIMARY KEY (`i`), UNIQUE `datetime_i` (`datetime`)) ENGINE = InnoDB"
        self.execute_base(i_sql_command)
        # main_widget.progress_action()
        return

    def del_instrument(self, symbol):
        s("del symbol from db: " + symbol)
        i_sql_command = "DROP TABLE IF EXISTS`"+self.database+"`.`" + symbol + "`"
        s(i_sql_command)
        self.execute_base(i_sql_command)
        # main_widget.progress_action()
        return

    def add_instrument_float_property(self, symbol, prop):
        s("add db " + symbol + " float prop: " + prop)
        i_sql_command = "ALTER TABLE `" + symbol + "` ADD IF NOT EXISTS`" + prop + \
                        "` DECIMAL(16,6) NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        # main_widget.progress_action()
        return

    def add_instrument_string_property(self, symbol, prop, plength):
        s("add db " + symbol + " string prop: " + prop)
        i_sql_command = "ALTER TABLE `" + symbol + "` ADD IF NOT EXISTS`" + prop + \
                        "` VARCHAR(" + str(plength) + ") NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        main_widget.progress_action()
        return

    def add_instrument_value(self, instrument, dt, prop, val):
        i_sql_command = "SELECT * FROM `"+instrument+"` WHERE `datetime` = '"+dt+"'"
        if type(val) != str:
            val = str(val)

        if self.execute_fetchall(i_sql_command):
            i_sql_command = "UPDATE `"+instrument+"` SET `"+prop+"`= '"+val+"' WHERE `datetime` = '"+dt+"'"
            self.execute_base(i_sql_command)
        else:
            i_sql_command = "INSERT INTO `"+instrument+"` SET datetime = '"+dt+"', "+prop+" = '"+val+"'"
            self.execute_base(i_sql_command)
        return

    def add_instrument_value_multi(self, instrument, dt_array, prop, val_array):
        s("write to db "+instrument+" - "+prop)


        self.add_instrument(instrument)
        self.add_instrument_float_property(instrument, prop)
        i_dt_array_len = len(dt_array)
        i_elemet_block_size = 32000

        # beszúrom az üreseket, ha még nincsenek és utána minden módosítom
        i_sql_elements_array = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size))]

        for i_i in range(i_dt_array_len):
            i_pos = int(i_i / i_elemet_block_size)
            i_sql_elements_array[i_pos] = i_sql_elements_array[i_pos] + "('" + dt_array[i_i] + "', '" + str(val_array[i_i]) + "'), "

        for i_i in range(len(i_sql_elements_array)):
            i_sql_str = "INSERT INTO `" + instrument + "` " +\
                    "(`datetime` , `" + prop + "` ) VALUES " +\
                    i_sql_elements_array[i_i][:-2] +\
                    " ON DUPLICATE KEY UPDATE `datetime` = VALUES(datetime)"
            self.execute_base(i_sql_str)




        # minden sort lemódosítok
        i_elemet_block_size2 = 32000
        i_sql_elements_array2 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]
        i_sql_elements_array3 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]
        # s("Update create 1")
        # for i_i2 in range(1):
        for i_i2 in range(i_dt_array_len):
            i_pos2 = int(i_i2 / i_elemet_block_size2)
            i_sql_elements_array2[i_pos2] = i_sql_elements_array2[i_pos2] +\
                                          "WHEN `datetime` = '" + dt_array[i_i2] +\
                                            "' THEN '" + str(val_array[i_i2]) + "' "

            i_sql_elements_array3[i_pos2] = i_sql_elements_array3[i_pos2] +\
                                          "'" + dt_array[i_i2] + "',"
        # s("Update create 2")
        for i_i3 in range(len(i_sql_elements_array2)):

            i_sql_str2 = "UPDATE " + instrument + " SET `" + prop + "` = CASE " +\
                    i_sql_elements_array2[i_i3] +\
                    " END WHERE `datetime` IN (" + i_sql_elements_array3[i_i3][:-1] + ")"
            self.execute_simply(i_sql_str2)
        #     print("na")
        #
        # if prop == "o":
        #     self.open()
        #     self.cursor.execute(i_sql_str2)
        #     self.close()
        return


class wl:
    df = ""

    def __init__(self):
        self.df = self.read()
        self.refresh_close()
        self.refresh_news_sentiment()

    def read(self):
        return pd.read_csv('wl.csv', sep=';')

    def write(self):
        self.df.to_csv('wl.csv', sep=';', index=False)
        return

    def refresh_close(self):
        s("Refresh Wl close prices")
        i_md = market_data()
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_quote = i_md.quote(i_symbol)
            self.df.loc[self.df['symbol'] == i_symbol, 'c'] = i_quote['c']
            self.df.loc[self.df['symbol'] == i_symbol, 'pc'] = i_quote['pc']
        self.write()
        return

    def refresh_data(self):
        s("Refresh Wl Data")
        i_md = market_data()
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_company_profile = i_md.company_profile(i_symbol)
            self.df.loc[self.df['symbol'] == i_symbol, 'name'] = i_company_profile['name']
            self.df.loc[self.df['symbol'] == i_symbol, 'profil'] = "Description: " + i_company_profile['description']
        self.write()
        return

    def refresh_news_sentiment(self):
        s("Refresh Wl sentiment")
        i_md = market_data()
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_news_sentiment = i_md.news_sentiment(i_symbol)
            self.df.loc[self.df['symbol'] == i_symbol, 'snt_bearish'] = i_news_sentiment['sentiment']['bearishPercent']
            self.df.loc[self.df['symbol'] == i_symbol, 'snt_bullish'] = i_news_sentiment['sentiment']['bullishPercent']
        self.write()
        return

    def add(self, symbol):
        self.remove(symbol)
        new_row = {'symbol': symbol}
        self.df = self. df.append(new_row, ignore_index=True)
        self.refresh_data()
        self.refresh_close()
        self.refresh_news_sentiment()
        self.write()
        self.referesh_ui()
        self.save_prices(symbol)
        return

    def remove(self, symbol):
        self.df.drop(self.df.loc[self.df['symbol'] == symbol].index, inplace=True)
        self.write()
        self.referesh_ui()
        return

    # def save_prices(self, symbol):
    #     s("Save prices - " + symbol)
    #     i_now = datetime.now() + timedelta(days=1)
    #     i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
    #     i_datetime_series = pd.date_range(start=i_now, periods=7, freq='-62d')
    #     for i_i in range(len(i_datetime_series)-1):
    #         i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i]))
    #         i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
    #         s("get data " + symbol + " - " + str(i_datetime_series[i_i]) + " - " + str(i_datetime_series[i_i+1]))
    #         i_df_stock = pd.DataFrame(None)
    #         i_df_stock = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix)
    #         i_datetime = tools.get_df_column(i_df_stock, "datetime")
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "t", tools.get_df_column(i_df_stock, "t"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "o", tools.get_df_column(i_df_stock, "o"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "h", tools.get_df_column(i_df_stock, "h"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "c", tools.get_df_column(i_df_stock, "c"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "l", tools.get_df_column(i_df_stock, "l"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "ohlc4", tools.get_df_column(i_df_stock, "ohlc4"))
    #         aisdb.add_instrument_value_multi(symbol, i_datetime, "v", tools.get_df_column(i_df_stock, "v"))
    #     return

    def save_prices(self, symbol):
        s("Save prices - " + symbol)
        i_now = datetime.now() + timedelta(days=1)
        i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
        i_datetime_series = pd.date_range(start=i_now, periods=13, freq='-31d')
        for i_i in range(len(i_datetime_series)-1):
            i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i]))
            i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
            s("get data " + symbol + " - " + str(i_datetime_series[i_i]) + " - " + str(i_datetime_series[i_i+1]))
            i_df_stock = pd.DataFrame(None)
            i_df_stock = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix)
            i_datetime = tools.get_df_column(i_df_stock, "datetime")

            db_act1 = ais_db()
            ci1 = tools.get_df_column(i_df_stock, "t")
            db_act1.add_instrument_value_multi(symbol, i_datetime, "t", ci1)

            db_act2 = ais_db()
            ci2 = tools.get_df_column(i_df_stock, "o")
            t2 = threading.Thread(target=db_act2.add_instrument_value_multi, args=(symbol, i_datetime, "o", ci2))

            db_act3 = ais_db()
            ci3 = tools.get_df_column(i_df_stock, "h")
            t3 = threading.Thread(target=db_act3.add_instrument_value_multi, args=(symbol, i_datetime, "h", ci3))

            db_act4 = ais_db()
            ci4 = tools.get_df_column(i_df_stock, "c")
            t4 = threading.Thread(target=db_act4.add_instrument_value_multi, args=(symbol, i_datetime, "c", ci4))

            db_act5 = ais_db()
            ci5 = tools.get_df_column(i_df_stock, "l")
            t5 = threading.Thread(target=db_act5.add_instrument_value_multi, args=(symbol, i_datetime, "l", ci5))

            db_act6 = ais_db()
            ci6 = tools.get_df_column(i_df_stock, "ohlc4")
            t6 = threading.Thread(target=db_act6.add_instrument_value_multi, args=(symbol, i_datetime, "ohlc4", ci6))

            db_act7 = ais_db()
            ci7 = tools.get_df_column(i_df_stock, "v")
            t7 = threading.Thread(target=db_act7.add_instrument_value_multi, args=(symbol, i_datetime, "v", ci7))

            t2.start()
            t3.start()
            t4.start()
            t5.start()
            t6.start()
            t7.start()

            t2.join()
            t3.join()
            t4.join()
            t5.join()
            t6.join()
            t7.join()
        return


    def referesh_ui(self):
        s("Refresh Wl Ui")
        i_wl_frame_object = np.ndarray(8, dtype=object, order='F')
        i_wl_frame_object[0] = main_widget.WL_frame
        i_wl_frame_object[1] = main_widget.WL_frame_2
        i_wl_frame_object[2] = main_widget.WL_frame_3
        i_wl_frame_object[3] = main_widget.WL_frame_4
        i_wl_frame_object[4] = main_widget.WL_frame_5
        i_wl_frame_object[5] = main_widget.WL_frame_6
        i_wl_frame_object[6] = main_widget.WL_frame_7
        i_wl_frame_object[7] = main_widget.WL_frame_8

        i_noid = np.array(['', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9'])

        for i_obj in i_wl_frame_object:
            i_obj.hide()
        i_no = 0
        for index, row in self.df.iterrows():
            i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setText(row['symbol'])
            i_wl_frame_object[i_no].findChild(QLabel, "WL_c"+i_noid[i_no]).setText(str(round(row['c'], 2)))
            if row['c'] > row['pc']:
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▲")
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: green; background: #ffffff;")
            else:
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▼")
                i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: red; background: #ffffff;")

            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_long"+i_noid[i_no]).setText("L:"+str(random.randint(0, 100))+"%")
            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_neutral"+i_noid[i_no]).setText("N:"+str(random.randint(0, 100))+"%")
            i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_short"+i_noid[i_no]).setText("S:"+str(random.randint(0, 100))+"%")
            i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bull"+i_noid[i_no]).setValue(int(row['snt_bullish']*100))
            i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bear"+i_noid[i_no]).setValue(int(row['snt_bearish']*100))
            i_wl_frame_object[i_no].show()
            i_no = i_no + 1
        return


class market_data():
    api_key_finnhubio1 = "bs9c9lvrh5rahoaofmt0"
    finnhub_client = finnhub.Client(api_key=api_key_finnhubio1)

    def get_stock_candles(self, symbol, dt_frame, from_dt, to_dt):
        i_df = pd.DataFrame(self.finnhub_client.stock_candles(symbol, dt_frame, from_dt, to_dt))
        i_df['datetime'] = pd.to_datetime(i_df['t'], unit='s')
        i_df['datetime'] = i_df['datetime'].dt.strftime('%y-%m-%d %h:%I:%s')
        i_df['ohlc4'] = round(((i_df['o'] + i_df['h'] + i_df['l'] + i_df['c'])/4), 6)
        i_df = i_df[['datetime', 't', 'o', 'h', 'l', 'c', 'ohlc4', 'v']]
        i_df.set_index('datetime')
        # return pandas df o h c l v t datetime ohcl4
        return i_df

    def company_profile(self, symbol):
        return self.finnhub_client.company_profile(symbol=symbol)

    def news_sentiment(self, symbol):
        return self.finnhub_client.news_sentiment(symbol=symbol)

    def quote(self, symbol):
        return self.finnhub_client.quote(symbol)


class tools():

    def get_df_column(self, df, col):
        return df[col].to_numpy().tolist()

    def dbdt_to_unixdt(self, datestring):
        dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return str(int(time.mktime(dt2.timetuple())))


class prices():
    symbol = 'AAPL'

    from_year = 2019
    from_month = 10
    from_day = 27
    from_hour = 10
    from_minute = 10
    from_secound = 0
    to_year = 2019
    to_month = 10
    to_day = 28
    to_hour = 10
    to_minute = 10
    to_secound = 0
    c = []
    h = []
    l = []
    o = []
    t = []
    v = []
    df = ""
    ser = ""

    def set_date_time_frame(self):
        s("set_date_time_frame")
        self.from_year = int(main_widget.From_D.selectedDate().toString("yyyy"))
        self.from_month = int(main_widget.From_D.selectedDate().toString("MM"))
        self.from_day = int(main_widget.From_D.selectedDate().toString("dd"))
        self.from_hour = int(main_widget.From_T.dateTime().toString("hh"))
        self.from_minute = int(main_widget.From_T.dateTime().toString("mm"))
        self.from_secound = int(main_widget.From_T.dateTime().toString("ss"))

        self.to_year = int(main_widget.To_D.selectedDate().toString("yyyy"))
        self.to_month = int(main_widget.To_D.selectedDate().toString("MM"))
        self.to_day = int(main_widget.To_D.selectedDate().toString("dd"))
        self.to_hour = int(main_widget.To_T.dateTime().toString("hh"))
        self.to_minute = int(main_widget.To_T.dateTime().toString("mm"))
        self.to_secound = int(main_widget.To_T.dateTime().toString("ss"))
        return

    def set_dt(self,fort,y,mo,d,h,mi,sec):
        if fort == "from":
            self.from_year, self.from_month, self.from_day, self.from_hour, self.from_minute, self.from_secound =\
                y, mo, d, h, mi, sec
        else:
            self.to_year, self.to_month, self.to_day, self.to_hour, self.to_minute, self.to_secound =\
                y, mo, d, h, mi, sec
        return

    def convert_to_unix_dt(self, cyear, cmonth, cday, chour, cminute, csecound):
        dt = datetime(cyear, cmonth, cday, chour, cminute, csecound)
        return str(int(time.mktime(dt.timetuple())))

    def convert_to_db_dt(self, unix_datetime):
        # print("datetime", unix_datetime)
        return str(datetime.fromtimestamp(int(unix_datetime)).strftime('%Y-%m-%d %H:%M:%S'))

    def convert_to_db_dt_multi(self, unix_datetime_array):

        i_result_array = []

        for i_i in range(len(unix_datetime_array)):
            i_value = (datetime.fromtimestamp(int(unix_datetime_array[i_i])))
            i_result_array.append("")
            i_result_array[i_i] = str(i_value.strftime('%Y-%m-%d %H:%M:%S'))
        return (i_result_array)

    def get_unix_dt(self,fort):
        if fort == "from":
            return self.convert_to_unix_dt(self.from_year,self.from_month,self.from_day,
                                    self.from_hour,self.from_minute,self.from_secound)
        else:
            return self.convert_to_unix_dt(self.to_year, self.to_month, self.to_day,
                                    self.to_hour, self.to_minute, self.to_secound)

    def get_df_column(self, col):
        return self.df[col].to_numpy().tolist()

    def get_stock_candle(self):
        s("get_stock_cande")
        self.set_date_time_frame()
        i_db_dt_from = self.convert_to_db_dt(self.get_unix_dt("from"))
        i_db_dt_to = self.convert_to_db_dt(self.get_unix_dt("to"))

        i_res = aisdb.get_timeframe(self.symbol, i_db_dt_from, i_db_dt_to)
        # print(i_res)
        # from pandas import DataFrame
        df = pd.DataFrame(i_res)
        df.columns = aisdb.column_names
        self.df = df
        # print(df)
        # print("df_v", self.get_df_column("v"))
        # print("df_c", self.get_df_column("c"))
        # array_v = df['v'].to_numpy()
        # print('array_v', array_v)
        # sys.exit()
        # df.columns = resoverall.keys()
        return


class iphoenix100(QWidget):
    log_Text = ""
    progress_count = 0

    def __init__(self):
        super(iphoenix100, self).__init__()
        self.load_ui()
        self.Logs_Browser.setText("")
        self.setWindowTitle("nDot")
        i_now = datetime.now()
        self.From_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.From_T.setTime(QTime(i_now.hour, i_now.minute))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))
        # wl.referesh_ui()
        return


    def load_ui(self):
        # loader = QUiLoader()
        # path = os.path.join(os.path.dirname(__file__), "C:/Users/honis.ivan/Documents/IPhoneix120/form.ui")
        # ui_file = QFile(path)
        # ui_file.open(QFile.ReadOnly)
        # self.ui = loader.load(ui_file, self)
        loadUi("C:/Users/honis.ivan/Documents/IPhoneix120/form.ui", self)

        # hozzárendelések
        self.Run_Button.clicked.connect(self.run_button_action)
        self.Command_Line.returnPressed.connect(self.run_button_action)
        self.Command_Line.textChanged.connect(self.command_line_changed)
        # self.WL_btn.clicked.connect(Run_WL_btn)
        self.Datetime_mod1.clicked.connect(partial(self.date_modifier, "hours", 6))
        self.Datetime_mod2.clicked.connect(partial(self.date_modifier, "days", 1))
        self.Datetime_mod3.clicked.connect(partial(self.date_modifier, "days", 2))
        self.Datetime_mod4.clicked.connect(partial(self.date_modifier, "days", 4))
        self.Datetime_mod5.clicked.connect(partial(self.date_modifier, "days", 30))
        self.Datetime_now.clicked.connect(self.date_now)
        # ui_file.close()

    def date_now(self):
        i_now = datetime.now()
        self.To_D.setSelectedDate(QDate(i_now.year, i_now.month, i_now.day))
        self.To_T.setTime(QTime(i_now.hour, i_now.minute))
        return

    def date_modifier(self, interval_type, interval_num):
        i_nowp = datetime.now() - timedelta(**{interval_type: interval_num})
        self.From_D.setSelectedDate(QDate(i_nowp.year, i_nowp.month, i_nowp.day))
        self.From_T.setTime(QTime(i_nowp.hour, i_nowp.minute))
        return

    def progress_action(self):
        # self.progress_count = self.progress_count + 5
        # if self.progress_count > 100:
        #     self.progress_count = 0
        self.Progress_Bar.setValue(random.randint(0, 100))

    def run_button_action(self):
        s("Run button pressed")
        command_text = self.Command_Line.text()
        command_partitioned = command_text.partition(" ")
        command_text_first_word = str.lower(command_partitioned[0])
        param1 = command_partitioned[2]
        # if len(command_partitioned) == 3:
        #     param1 = command_partitioned[2]
        # if len(command_partitioned) == 5:
        #     param1 = command_partitioned[2]
        #     param2 = command_partitioned[4]
        # if len(command_text.partition(' ')) == 7:
        #     param1 = command_partitioned[2]
        #     param2 = command_partitioned[4]
        #     param3 = command_partitioned[6]

        self.Command_Line.setText("")

        d = {
            'getprice': 'getprice_program',
            'chart': 'chart_program',
            'addwl': 'add_wl_program',
            'removewl': 'remove_wl_program',
            'removewldata': 'remove_wl_data_program',
            'test': 'test_program',
            'price.get': 'getprice_program',
            'wl.add': 'add_wl_program',
            'wl.remove': 'remove_wl_program',
            'wl.remove.data': 'remove_wl_data_program',
            'exit': 'exit_program'
            }

        df = pd.Series(d)
        if command_text_first_word in df.index:
            self.add_log("call: " + df[command_text_first_word])
            method = eval(df[command_text_first_word])
            args = [param1]
            kwargs = {}
            method(*args, **kwargs)
        return

    def command_line_changed(self):
        self.Command_Hint.setText("")
        command_text = self.Command_Line.text()
        command_text_first_word = command_text.partition(' ')[0]

        d2 = {
            'getprice': 'getprice_program',
            'chart': 'chart_program',
            'addwl': 'addwl symbol - add new symbol to watchlist',
            'removewl': 'removewl symbol - remove symbol from watchlist',
            'removewldata': 'removewldata sybol - remove symbol from nDot data server',
            'price.get': 'getprice_program',
            'wl.add': 'addwl symbol - add new symbol to watchlist',
            'wl.remove': 'removewl symbol - remove symbol from watchlist',
            'wl.remove.data': 'removewldata sybol - remove symbol from nDot data server',
            'test': 'run test_program param',
            'exit': 'exit'
        }

        df = pd.Series(d2)
        if command_text_first_word in df.index:
            self.Command_Hint.setText(df[command_text_first_word])
        return

    def add_log(self, add_text):
        self.log_Text = time.strftime("%m-%d %H:%M:%S")+" > "+add_text + " \r" + self.log_Text
        self.Logs_Browser.setText(self.log_Text)
        main_widget.update()
        return


def s(msg_str):
    main_widget.Status.setText("Status: "+msg_str)
    print(time.strftime("%m-%d %H:%M:%S")+" > "+"Status: "+msg_str)
    main_widget.update()
    main_widget.repaint()
    return


def test_program(param=""):
    s("TEST........ " + param)
    return


def exit_program(param=""):
    main_widget.close()
    return


def add_wl_program(isymbol=""):
    main_widget.add_log("run addwl " + isymbol)
    wl.add(isymbol)
    main_widget.add_log("addwl - Ready")


def remove_wl_program(isymbol=""):
    main_widget.add_log("run removewl " + isymbol)
    wl.remove(isymbol)
    main_widget.add_log("removewl - Ready")


def remove_wl_data_program(isymbol=""):
    main_widget.add_log("run removewldata " + isymbol)
    aisdb.del_instrument(isymbol)
    main_widget.add_log("removewldata - Ready")


def getprice_program(symbol):
    main_widget.add_log("run getPrice " + symbol)
    main_widget.add_log("getPrice - Ready")


def Run_WL_btn():
    print("Run_WL_btn")
    main_widget.add_log("run Run_WL_btn")

    idf = pd.read_csv(
        'C:/Users/honis.ivan/PycharmProjects/plotchart/mplfinance-master/examples/data/SPY_20110701_20120630_Bollinger.csv',
        index_col=0, parse_dates=True)

    df = idf.loc['2011-07-01':'2011-12-30', :]

    df = df.drop(['UpperB', 'LowerB', 'PercentB'], axis=1)
    mpf.plot(df, type='candle', volume=True)
    print(df)
    # pkwargs = dict(type='candle', mav=(10, 20))
    #
    # fig, axes = mpf.plot(df.iloc[0:50], returnfig=True, volume=True,
    #                      figsize=(11, 8), panel_ratios=(2, 1),
    #                      title='\n\nS&P 500 ETF', **pkwargs)
    # ax1 = axes[0]
    # ax2 = axes[2]
    #
    # def animate(ival):
    #     if (50 + ival) > len(df):
    #         print('no more data to plot')
    #         ani.event_source.interval *= 3
    #         if ani.event_source.interval > 12000:
    #             exit()
    #         return
    #     data = df.iloc[(0+ival):(50 + ival)]
    #     ax1.clear()
    #     ax2.clear()
    #     mpf.plot(data, ax=ax1, volume=ax2, **pkwargs)
    #
    # ani = animation.FuncAnimation(fig, animate, interval=20)

    mpf.show()
    return


def chart_program(symbol):
    main_widget.add_log("run chart " + symbol)
    stock = prices()
    stock.symbol = symbol
    stock.get_stock_candle()
    # print(stock.df)
    i_chart_df = stock.df.rename(columns={"datetime": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, errors="raise")
    # i_chart_df = i_chart_df.drop(['i', 't', 'ohlc4'], axis=1)
    #
    # # i_chart_df['Adj Close'] = i_chart_df['Close']
    # i_chart_df['Volume'] = i_chart_df['Volume'].astype(int)
    #
    i_chart_df = i_chart_df[['Date', 'Open', 'Close', 'High', 'Low', 'Volume']]
    su = io.StringIO()
    i_chart_df.to_csv(su, index=False)
    quote = pd.read_csv(StringIO(su.getvalue()), sep=",", index_col=0, parse_dates=True)
    mpf.available_styles()
    mpf.plot(quote, type='candle', volume=True, style='binance', figratio=(19, 10), figscale=.9, tight_layout=True)
    mpf.show()
    main_widget.add_log("chart - Ready")
    return

# időzítő
class back_processes(object):
    def __init__(self, interval=60):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # More statements comes here
            print(datetime.now().__str__() + ' : Start task in the background')
            time.sleep(self.interval)

if __name__ == "__main__":

    # 1.
    print("Status: Load GUI")
    app = QApplication([])
    main_widget = iphoenix100()
    main_widget.show()
    # main_widget.showFullScreen()
    print("Status: GUI Ready")

    # 2.
    aisdb = ais_db()
    wl = wl()
    wl.referesh_ui()
    md = market_data()
    tools = tools()

    # 3. háttér futásindítás 60 másodpercenkénti futás
    # bp = back_processes()

    s("ok")
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


