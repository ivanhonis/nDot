# This Python file uses the following encoding: utf-8
import sys
import os
import requests

import time
import json
import mysql.connector
import threading
import random
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.ticker as mticker
# import matplotlib.mlab as mlab
# import matplotlib.pyplot as plt
# import matplotlib.font_manager as font_manager


# import matplotlib.ticker as ticker

# from PySide2.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
# from PySide2.QtCore import QFile
# from PySide2.QtUiTools import QUiLoader
# from mpl_finance import candlestick_ohlc

# from PySide2.QtCore import QDateTime, Qt, QAbstractTableModel
# from PySide2.QtGui import QPainter
# from PySide2.QtWidgets import (QWidget, QHeaderView, QHBoxLayout, QTableView,
#                                QSizePolicy)
# from PySide2.QtCharts import QtCharts

# from table_model import CustomTableModel


from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi

# import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

# from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

# import random



class ais_db():
    aisdb = ""
    cursor = ""
    row_count = 0
    host = "sql132.main-hosting.eu"
    user = "u826803502_AIS1"
    password = "+1zZJqwQ"
    database = "u826803502_ArtIntSol"
    column_names = ""

    # def __init__(self):
    #     self.oppen()

    def open(self):
        self.aisdb = mysql.connector.connect(
         host=self.host,
         user=self.user,
         password=self.password,
         database=self.database,
         connect_timeout=10000
        )
        self.setcursor()

    def setcursor(self):
        self.cursor = self.aisdb.cursor(buffered=False)

    def close(self):
        self.aisdb.commit()
        self.aisdb.close()

    def execute_base(self, sqlstr, multiple=False):
        main_widget.progress_action()
        # print(sqlstr)
        # print("minden ok?",self.aisdb.is_connected())
        if self.aisdb.is_connected():
            try:
                self.cursor.execute(sqlstr, multiple)
                if self.cursor.rowcount > 0:
                    main_widget.add_Log("inserted rows: " + str(self.cursor.rowcount))
                self.setcursor()
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
        else:
            self.open()
            self.cursor.execute(sqlstr, multiple)
            self.setcursor()
            if self.cursor.rowcount > 0:
                main_widget.add_Log("inserted rows: " + str(self.cursor.rowcount))
        return

    def execute_fetchall(self, sqlstr):
        if not self.aisdb.is_connected():
            self.open()

        try:
            # print(sqlstr)
            self.cursor.execute(sqlstr)
            self.column_names = self.cursor.column_names
            # self.setcursor()
            # self.aisdb.commit()
            if self.cursor.rowcount > 0:
                main_widget.add_Log("rows: " + str(self.cursor.rowcount))
                self.row_count = self.cursor.rowcount
                i_result = self.cursor.fetchall()
                self.setcursor()
            else:
                self.row_count = 0
                i_result = self.cursor.fetchall()
                self.setcursor()
                # i_result = []

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            i_result = []
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

    def get_timeframe(self, isymbol, fromdt, todt):
        # print ("get_timeframe")
        i_sql_string = "SELECT * FROM `" + isymbol + "` WHERE `datetime`>='" + fromdt + "' AND `datetime`<='" + todt + "'"
        return self.execute_fetchall(i_sql_string)


    def add_instrument(self, instrument):
        i_sql_command = "CREATE TABLE IF NOT EXISTS`" + self.database + "`.`" + instrument + \
                        "` ( `i` INT NOT NULL AUTO_INCREMENT , `datetime` DATETIME NOT NULL , " + \
                        "PRIMARY KEY (`i`), UNIQUE `datetime_i` (`datetime`)) ENGINE = InnoDB"
        self.execute_base(i_sql_command)
        self.aisdb.commit()
        return

    def del_instrument(self, instrument):
        i_sql_command = "DROP TABLE IF EXISTS`"+self.database+"`.`"+instrument+"`"
        self.execute_base(i_sql_command)
        return

    def add_instrument_float_property(self, instrument, prope):
        i_sql_command = "ALTER TABLE `" + instrument + "` ADD IF NOT EXISTS`" + prope + \
                        "` DECIMAL(13,6) NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        return

    def add_instrument_string_property(self, instrument, prope, plength):
        i_sql_command = "ALTER TABLE `" + instrument + "` ADD IF NOT EXISTS`" + prope + \
                        "` VARCHAR(" + str(plength) +") NULL DEFAULT NULL AFTER `datetime`"
        self.execute_base(i_sql_command)
        return

    def add_instrument_value(self, instrument, dt, prop, val):
        i_sql_command = "SELECT * FROM `"+instrument+"` WHERE `datetime` = '"+dt+"'"
        if type(val) != str:
            val = str(val)

        if self.execute_fetchall(i_sql_command): # ha már létezik
            i_sql_command = "UPDATE `"+instrument+"` SET `"+prop+"`= '"+val+"' WHERE `datetime` = '"+dt+"'"
            self.execute_base(i_sql_command)
        else:
            i_sql_command = "INSERT INTO `"+instrument+"` SET datetime = '"+dt+"', "+prop+" = '"+val+"'"
            self.execute_base(i_sql_command)
        return

    def add_instrument_value_multi(self, instrument, dt_array, prop, val_array):
        # print("ins", instrument,"----------------------------------------------")
        # print("dt_array", dt_array[2])
        # print("prop", prop)
        # print("val_array", val_array)
        # print("add")
        self.add_instrument(instrument)
        self.add_instrument_float_property(instrument, prop)
        i_dt_array_len = len(dt_array)
        i_elemet_block_size = 32000

        # beszúrom az üreseket, ha még nincsenek és utána minden módosítom
        i_sql_elements_array = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size))]
        # print(len(i_sql_elements_array))

        for i_i in range(i_dt_array_len):
            # print(i_i)
            i_pos = int(i_i / i_elemet_block_size)
            # print(i_pos)
            # i_sql_elements_array[0] = " "+ i_sql_elements_array[i_pos]
            # print(i_sql_elements_array)

            i_sql_elements_array[i_pos] = i_sql_elements_array[i_pos] + "('" + dt_array[i_i] + "', '" + str(val_array[i_i]) + "'), "
            # print(i_sql_elements_array[i_pos])

        # print('2')

        for i_i in range(len(i_sql_elements_array)):
            # print('3')
            i_sql_str = "INSERT INTO `" +instrument + "` "+\
                    "(`datetime` , `" + prop + "` ) VALUES " +\
                    i_sql_elements_array[i_i][:-2] +\
                    " ON DUPLICATE KEY UPDATE `datetime` = VALUES(datetime)"
            # print(i_sql_str)
            self.execute_base(i_sql_str, True)
        self.aisdb.commit()

        # minden sort lemódosítok
        i_elemet_block_size2 = 32000
        i_sql_elements_array2 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]
        i_sql_elements_array3 = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size2))]

        for i_i2 in range(i_dt_array_len):
            i_pos2 = int(i_i2 / i_elemet_block_size2)
            i_sql_elements_array2[i_pos2] = i_sql_elements_array2[i_pos2] +\
                                          "WHEN `datetime` = '" + dt_array[i_i2] + "' THEN '" + str(val_array[i_i2]) + "' "

            i_sql_elements_array3[i_pos2] = i_sql_elements_array3[i_pos2] +\
                                          "'" + dt_array[i_i2] + "',"


        for i_i3 in range(len(i_sql_elements_array2)):
            i_sql_str2 = "UPDATE " + instrument + " SET `" + prop + "` = CASE " +\
                    i_sql_elements_array2[i_i3] +\
                    " END WHERE `datetime` IN ("+ i_sql_elements_array3[i_i3][:-1] + ")"
            # print(i_sql_str2)
            self.execute_base(i_sql_str2)
        self.aisdb.commit()
        return

class watchlist():
    wl_rows = 3
    wl_column = 5
    saved_items = []

    def get_wl_df(self):
        print('wl itt')
        i_df = pd.read_csv('wl.csv', sep=';')
        i_df.set_index('symbol')
        print(i_df.loc[i_df['symbol'] == 'MSFT',['name']])
        print(i_df.iloc[:, 0])
        for index, row in i_df.iterrows():
            print(row['name'], row['profil'])

        new_row = {'symbol': 'Geo', 'name': 'GEO corp', 'profil': 'geoprofil', 'last_price': 97}
        # append row to the dataframe
        i_df = i_df.append(new_row, ignore_index=True)
        print(i_df)
        i_df.to_csv('wl.csv', sep=';', index=False)
        i_df.drop(i_df.loc[i_df['symbol'] == 'Geo'].index, inplace=True)
        datetime_series = pd.date_range(start='2020-08-10 00:00', periods=12, freq='-1M', closed=None)
        for i_i in range(len(datetime_series)-1):
            print(datetime_series[i_i], " ", datetime_series[i_i+1])
        return i_df

    def __init__(self):
        self.saved_items.append(["MSFT", self.getCompanyProfile2("MSFT"), "113.25", "10:25", "sell"])
        self.saved_items.append(["APA", self.getCompanyProfile2("APA"), "113.25", "10:25", "hold"])
        self.saved_items.append(["AAPL", self.getCompanyProfile2("AAPL"), "113.25", "10:25", "hold"])

    def getWLItems(self):
        return self.saved_items

    def getCompanyProfile2(self, symbol):
        # request_url = 'https://finnhub.io/api/v1/stock/profile2?symbol='+symbol+'&token=bs9c9lvrh5rahoaofmt0'
        # print(request_url)
        # r = requests.get(request_url)
        # json_data = json.loads(r.text)
        # print(json_data)
        name = "a" # json_data["name"]
        logo = "a" # json_data["logo"]
        return name

    def getQItems(self):
       ritems = [[0 for x in range(self.wl_column)] for y in range(self.wl_rows)]
       for x2 in range(self.wl_rows):
           for y2 in range(self.wl_column):
               ritems[x2][y2]=QTableWidgetItem(self.saved_items[x2][y2])
       return ritems


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
    t = []
    v = []
    df = ""

    def set_date_time_frame(self):
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
        print("get_stock_cande")
        self.set_date_time_frame()
        i_db_dt_from = self.convert_to_db_dt(self.get_unix_dt("from"))
        i_db_dt_to = self.convert_to_db_dt(self.get_unix_dt("to"))

        # print("bbbbb", aisdb.is_timeframe_exist("MSFT", "2020-08-03 00:00:00", "2021-08-03 12:00:00"))
        # print(self.symbol,i_db_dt_from,i_db_dt_to)
        i_exist_time_frame = aisdb.is_timeframe_exist(self.symbol, i_db_dt_from, i_db_dt_to)
        # print(i_exist_time_frame)
        # print(self.symbol, self.convert_to_db_dt(self.get_unix_dt("from")), self.convert_to_db_dt(self.get_unix_dt("to")))
        if i_exist_time_frame:
            print("van tf")
            i_res = aisdb.get_timeframe(self.symbol, i_db_dt_from, i_db_dt_to)
            # print(i_res)
            # from pandas import DataFrame
            df = pd.DataFrame(i_res)
            df.columns = aisdb.column_names
            df.set_index('datetime')
            self.df = df
            # print(df)
            # print("df_v", self.get_df_column("v"))
            # print("df_c", self.get_df_column("c"))
            # array_v = df['v'].to_numpy()
            # print('array_v', array_v)
            # sys.exit()
            # df.columns = resoverall.keys()
        else:
            print("nincs tf")
            i_request_url = 'https://finnhub.io/api/v1/stock/candle?symbol='+self.symbol+'&resolution=1&from='+self.get_unix_dt("from")+'&to='+self.get_unix_dt("to")+'&token=bs9c9lvrh5rahoaofmt0'
            print(i_request_url)
            i_r = requests.get(i_request_url)
            i_json_data = json.loads(i_r.text)
            df2 = pd.DataFrame(i_json_data)
            df2['datetime'] = self.convert_to_db_dt_multi(i_json_data["t"])
            df2 = df2.drop('s', 1)
            df2.set_index('datetime')
            print(df2)
            self.df = df2
            # print("df_v", self.get_df_column("v"))
            # print("df_c", self.get_df_column("c"))
            i_converted_t = self.convert_to_db_dt_multi(self.get_df_column("t"))
            aisdb.add_instrument_value_multi(self.symbol, i_converted_t, "c", self.get_df_column("c"))
            aisdb.add_instrument_value_multi(self.symbol, i_converted_t, "o", self.get_df_column("o"))
            aisdb.add_instrument_value_multi(self.symbol, i_converted_t, "h", self.get_df_column("h"))
            aisdb.add_instrument_value_multi(self.symbol, i_converted_t, "l", self.get_df_column("l"))
            aisdb.add_instrument_value_multi(self.symbol, i_converted_t, "v", self.get_df_column("v"))
            print("kiírtam")
            # sys.exit()
            # if i_json_data["s"] == "ok":
            #     self.c = i_json_data["c"]
            #     self.o = i_json_data["o"]
            #     self.l = i_json_data["l"]
            #     self.h = i_json_data["h"]
            #     self.v = i_json_data["v"]
            #     print(self.v)
            #     self.t = self.convert_to_db_dt_multi(i_json_data["t"])
            #     i_result = i_r.json()

        return


class iphoenix100(QWidget):
    log_Text = ""
    progress_count = 0

    def __init__(self):
        super(iphoenix100, self).__init__()
        self.load_ui()
        self.Logs_Browser.setText("")
        self.setWindowTitle("iPhoenix100")

        watchlist_obj=watchlist()
        self.Watch_list.setRowCount(watchlist_obj.wl_rows)
        self.Watch_list.setColumnCount(watchlist_obj.wl_column)
        watchlist_obj=watchlist()
        wlqitems=watchlist_obj.getQItems()
        for x2 in range(watchlist_obj.wl_rows):
            for y2 in range(watchlist_obj.wl_column):
                self.Watch_list.setItem(x2,y2,wlqitems[x2][y2])

    def load_ui(self):
        # loader = QUiLoader()
        # path = os.path.join(os.path.dirname(__file__), "C:/Users/honis.ivan/Documents/IPhoneix120/form.ui")
        # ui_file = QFile(path)
        # ui_file.open(QFile.ReadOnly)
        # self.ui = loader.load(ui_file, self)
        loadUi("C:/Users/honis.ivan/Documents/IPhoneix120/form.ui", self)

        # hozzárendelések
        self.Run_Button.clicked.connect(self.Run_Button_Action)
        self.Command_Line.returnPressed.connect(self.Run_Button_Action)
        self.Command_Line.textChanged.connect(self.Command_Line_Changed)
        self.WL_Btn.clicked.connect(Run_WL_btn2)
        # ui_file.close()

    def progress_action(self):
        # self.progress_count = self.progress_count + 5
        # if self.progress_count > 100:
        #     self.progress_count = 0
        self.Progress_Bar.setValue(random.randint(0, 100))

    def Run_Button_Action(self):
        command_text = self.Command_Line.text()
        command_partitioned = command_text.partition(" ")
        command_text_first_word = command_partitioned[0]
        if len(command_partitioned) == 3:
            param1 = command_partitioned[2]
        if len(command_partitioned) == 5:
            param1 = command_partitioned[2]
            param2 = command_partitioned[4]
        if len(command_text.partition(' ')) == 7:
            param1 = command_partitioned[2]
            param2 = command_partitioned[4]
            param3 = command_partitioned[6]

        self.add_Log("call "+command_text)
        self.Command_Line.setText("")

        if command_text_first_word == "getprice" or command_text_first_word == "getPrice":
            getprice_program(param1)

        if command_text_first_word == "test":
            self.progress_action()

        if command_text_first_word == "chart":
            chart_program(param1)

        if command_text_first_word == "addwl":
            add_wl_program(param1)

        if command_text_first_word == "close":
            self.close()

        if command_text_first_word == "exit":
            self.close()

    def Command_Line_Changed(self):
        self.Command_Hint.setText("")
        command_text = self.Command_Line.text()
        command_text_first_word = command_text.partition(' ')[0]

        if command_text_first_word == "test":
            self.Command_Hint.setText("test")

        if command_text_first_word == "chart":
            self.Command_Hint.setText("chart symbol")

        if command_text_first_word == "getprice":
            self.Command_Hint.setText("getprice symbol")

        if command_text_first_word == "addwl":
            self.Command_Hint.setText("addwl sybol")


    def add_Log( self,add_text ):
        self.log_Text = time.strftime( "%d %B, %Y %H:%M:%S" )+" > "+add_text + " \r" + self.log_Text
        self.Logs_Browser.setText(self.log_Text)


def add_wl_program(isymbol=""):
    main_widget.add_Log("run addwl "+isymbol)
    wl = watchlist()
    print(wl.get_wl_df())
    main_widget.add_Log("addwl - Ready")

def getprice_program(isymbol):
    main_widget.add_Log( "run getPrice "+isymbol )

    selected_stock = prices()
    selected_stock.symbol = isymbol
    selected_stock.get_stock_candle()

    # main_widget.update_graph(selected_stock.t,selected_stock.o,selected_stock.c)
    main_widget.add_Log("getPrice - Ready")

def test_program():
    main_widget.add_Log("run test_program")
    print("test")


def Run_WL_btn2():
    isymbol = "MSFT"
    print("itt", isymbol)
    main_widget.add_Log("run chart "+isymbol)

    selected_stock = prices()
    selected_stock.symbol = isymbol

    # selected_stock.from_year = int(main_widget.From_DT.dateTime().toString("yyyy"))
    # selected_stock.from_month = int(main_widget.From_DT.dateTime().toString("MM"))
    # selected_stock.from_day = int(main_widget.From_DT.dateTime().toString("dd"))
    # selected_stock.from_hour = int(main_widget.From_DT.dateTime().toString("hh"))
    # selected_stock.from_minute = int(main_widget.From_DT.dateTime().toString("mm"))
    # selected_stock.from_secound = int(main_widget.From_DT.dateTime().toString("mm"))
    #
    # selected_stock.to_year = int(main_widget.To_DT.dateTime().toString("yyyy"))
    # selected_stock.to_month = int(main_widget.To_DT.dateTime().toString("MM"))
    # selected_stock.to_day = int(main_widget.To_DT.dateTime().toString("dd"))
    # selected_stock.to_hour = int(main_widget.To_DT.dateTime().toString("hh"))
    # selected_stock.to_minute = int(main_widget.To_DT.dateTime().toString("mm"))
    # selected_stock.to_secound = int(main_widget.To_DT.dateTime().toString("mm"))
    import pandas as pd
    import mplfinance as mpf
    df = pd.read_csv(
         'C:/Users/honis.ivan/PycharmProjects/plotchart/mplfinance-master/examples/data/yahoofinance-SPY-20080101-20180101.csv',
         index_col=0,
         parse_dates=True)
    df.shape
    df.head(3)
    df.tail(3)

    print(df)


    mpf.plot(df, ax=main_widget.MplWidget.ax1, volume=main_widget.MplWidget.ax2)

    # print("itt2")
    # selected_stock.get_stock_candle()
    # print("itt3")
    # main_widget.MplWidget.ax1_1.clear()
    # # main_widget.MplWidget.ax2_1.clear()
    # main_widget.MplWidget.ax1_1.plot(selected_stock.get_df_column("datetime"), selected_stock.get_df_column("l"))
    # # main_widget.MplWidget.ax1_1.plot(selected_stock.get_df_column("t"), selected_stock.get_df_column("h"))
    # # main_widget.MplWidget.ax1_1.fill_between(selected_stock.get_df_column("t"), selected_stock.get_df_column("l"), selected_stock.get_df_column("h"), alpha=0.25)
    # main_widget.MplWidget.ax2_1.bar(selected_stock.get_df_column("datetime"), selected_stock.get_df_column("v"), label='Volume')
    # main_widget.MplWidget.ax1_1.margins(x=0)
    # # main_widget.MplWidget.ax2_1.margins(x=0)
    #
    # # main_widget.MplWidget.plot(selected_stock.t[10], selected_stock.o[10], 'o', color='r')
    #
    # for xtick in main_widget.MplWidget.ax1_1.get_xticklabels():
    #     xtick.set_color('none')
    #
    # # import matplotlib.dates as mdates
    # # locator = mdates.AutoDateLocator()
    # # formatter = mdates.ConciseDateFormatter(locator)
    # # formatter.formats = ['', '%M', '%H:%M']
    #
    # main_widget.MplWidget.ax1_1.set_xticklabels(selected_stock.get_df_column("datetime"), rotation=270, alpha=0.5)
    # # main_widget.MplWidget.ax1_1.xaxis.set_major_formatter(formatter)
    #
    # main_widget.MplWidget.ax2_1.set_xticklabels(selected_stock.get_df_column("datetime"), rotation=270, alpha=0.5)
    # # main_widget.MplWidget.ax2_1.xaxis.set_major_formatter(formatter)
    # # main_widget.MplWidget.ax1_1.autoscale()
    # # main_widget.MplWidget.ax2_1.autoscale()
    #
    # # import matplotlib.dates as mdates
    # # myfmt = mdates.DateFormatter('%M:%S')
    # # main_widget.MplWidget.ax2_1.xaxis.set_major_formatter(myfmt)
    # #
    # # main_widget.MplWidget.canvas.draw_idle()
    main_widget.MplWidget.canvas.draw()
    main_widget.add_Log("chart - Ready")


def chart_program(isymbol):

    main_widget.add_Log("run chart "+isymbol)

    selected_stock = prices()
    selected_stock.symbol = isymbol
    selected_stock.get_stock_candle()

    main_widget.MplWidget.ax1_1.clear()
    main_widget.MplWidget.ax2_1.clear()
    main_widget.MplWidget.ax1_1.plot(selected_stock.t, selected_stock.l)
    main_widget.MplWidget.ax1_1.plot(selected_stock.t, selected_stock.h)
    main_widget.MplWidget.ax1_1.fill_between(selected_stock.t, selected_stock.l, selected_stock.h, alpha=0.25)
    main_widget.MplWidget.ax2_1.bar(selected_stock.t, selected_stock.v, label='Volume')
    main_widget.MplWidget.ax1_1.margins(x=0)
    main_widget.MplWidget.ax2_1.margins(x=0)

    # main_widget.MplWidget.plot(selected_stock.t[10], selected_stock.o[10], 'o', color='r')

    for xtick in main_widget.MplWidget.ax1_1.get_xticklabels():
        xtick.set_color('none')

    main_widget.MplWidget.ax2_1.set_xticklabels(selected_stock.t, rotation=270, alpha=0.5)
    main_widget.MplWidget.ax1_1.autoscale()
    main_widget.MplWidget.ax1_1.autoscale()

    import matplotlib.dates as mdates
    myfmt = mdates.DateFormatter('%H:%M')
    main_widget.MplWidget.ax1_1.xaxis.set_major_formatter(myfmt)

    main_widget.MplWidget.canvas.draw()
    main_widget.add_Log("chart - Ready")

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
    # print(
    #     datetime.fromtimestamp(
    #         int("1284105682")
    #     ).strftime('%Y-%m-%d %H:%M:%S')
    # )

    # 1. Art Int Sol adatbázis kapcsolat létrehozása
    aisdb = ais_db()
    aisdb.open()

    # 2. háttér futásindítás 60 másodpercenkénti futás
    # bp = back_processes()

    # 3. UI indítás
    app = QApplication([])
    main_widget = iphoenix100()
    #main_widget.showFullScreen()

    # teszt dolgok ide jönnek
    # print(int(main_widget.From_T.dateTime().toString("hh")))
    # print(int(main_widget.To_T.dateTime().toString("hh")))
    # print("nAAAAAAAa", aisdb.is_timeframe_exist("MSFT", "2020-08-03 15:30:00", "2020-08-03 15:32:00"))
    # print("nAAAAAAAa", aisdb.is_timeframe_exist("MSFT", "2020-08-03 15:33:00", "2021-08-03 00:00:00"))
    # print("nAAAAAAAa", aisdb.is_timeframe_exist("MSFT", "2020-08-03 00:00:00", "2021-08-03 12:00:00"))
    # aisdb.del_instrument("MSFT")
    # aisdb.del_instrument("AAPL")
    # aisdb.add_instrument("SHELL")
    # aisdb.add_instrument("AAPL")
    # aisdb.add_instrument_float_property("MSFT","c")
    # aisdb.add_instrument_float_property("MSFT","o")
    # aisdb.add_instrument_float_property("MSFT","h")
    # aisdb.add_instrument_float_property("MSFT","l")
    # aisdb.add_instrument_float_property("AAPL","c")
    # aisdb.execute_base("INSERT INTO `MSFT` (`datetime`) VALUES ('2020-08-04 23:59:00') ON DUPLICATE KEY UPDATE `datetime` = VALUES(datetime)")
    # aisdb.add_instrument_float_property("AAPL","o")
    # aisdb.add_instrument_float_property("AAPL","h")
    # aisdb.add_instrument_float_property("AAPL","l")
    # aisdb.add_instrument_string_property("AAPL", "note", 256)
    # print("start")
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:47:00", "c", 123456)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:47:00", "c", 12345.78)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "c", 12345.12345)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "c", 12345.88)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "o", 12345.88)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "h", 12345.88)
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:48:00", "l", 123456.123456)
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:48:00", "note", "note")
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:49:00", "note", 1245)
    # print("stop")
    # -------------------------

    main_widget.show()
    aisdb.close()
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