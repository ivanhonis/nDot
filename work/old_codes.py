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


class watchlist():
    wl_df = ""
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

#  chart




    # selected_stock = prices()
    # selected_stock.symbol = isymbol

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
    # df = pd.read_csv(
    #      'C:/Users/honis.ivan/PycharmProjects/plotchart/mplfinance-master/examples/data/yahoofinance-SPY-20080101-20180101.csv',
    #      index_col=0,
    #      parse_dates=True)
    # df.shape
    # df.head(3)
    # df.tail(3)
    #
    # print(df)
    #
    #
    # mpf.plot(df, ax=main_widget.MplWidget.ax1, volume=main_widget.MplWidget.ax2)
    #
    # # print("itt2")
    # # selected_stock.get_stock_candle()
    # # print("itt3")
    # # main_widget.MplWidget.ax1_1.clear()
    # # # main_widget.MplWidget.ax2_1.clear()
    # # main_widget.MplWidget.ax1_1.plot(selected_stock.get_df_column("datetime"), selected_stock.get_df_column("l"))
    # # # main_widget.MplWidget.ax1_1.plot(selected_stock.get_df_column("t"), selected_stock.get_df_column("h"))
    # # # main_widget.MplWidget.ax1_1.fill_between(selected_stock.get_df_column("t"), selected_stock.get_df_column("l"), selected_stock.get_df_column("h"), alpha=0.25)
    # # main_widget.MplWidget.ax2_1.bar(selected_stock.get_df_column("datetime"), selected_stock.get_df_column("v"), label='Volume')
    # # main_widget.MplWidget.ax1_1.margins(x=0)
    # # # main_widget.MplWidget.ax2_1.margins(x=0)
    # #
    # # # main_widget.MplWidget.plot(selected_stock.t[10], selected_stock.o[10], 'o', color='r')
    # #
    # # for xtick in main_widget.MplWidget.ax1_1.get_xticklabels():
    # #     xtick.set_color('none')
    # #
    # # # import matplotlib.dates as mdates
    # # # locator = mdates.AutoDateLocator()
    # # # formatter = mdates.ConciseDateFormatter(locator)
    # # # formatter.formats = ['', '%M', '%H:%M']
    # #
    # # main_widget.MplWidget.ax1_1.set_xticklabels(selected_stock.get_df_column("datetime"), rotation=270, alpha=0.5)
    # # # main_widget.MplWidget.ax1_1.xaxis.set_major_formatter(formatter)
    # #
    # # main_widget.MplWidget.ax2_1.set_xticklabels(selected_stock.get_df_column("datetime"), rotation=270, alpha=0.5)
    # # # main_widget.MplWidget.ax2_1.xaxis.set_major_formatter(formatter)
    # # # main_widget.MplWidget.ax1_1.autoscale()
    # # # main_widget.MplWidget.ax2_1.autoscale()
    # #
    # # # import matplotlib.dates as mdates
    # # # myfmt = mdates.DateFormatter('%M:%S')
    # # # main_widget.MplWidget.ax2_1.xaxis.set_major_formatter(myfmt)
    # # #
    # # # main_widget.MplWidget.canvas.draw_idle()
    # main_widget.MplWidget.canvas.draw()
    # main_widget.add_Log("chart - Ready")
















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

# watchlist_obj = watchlist()
# self.Watch_list.setRowCount(watchlist_obj.wl_rows)
# self.Watch_list.setColumnCount(watchlist_obj.wl_column)
# watchlist_obj=watchlist()
# wlqitems=watchlist_obj.getQItems()
# for x2 in range(watchlist_obj.wl_rows):
#     for y2 in range(watchlist_obj.wl_column):
#         self.Watch_list.setItem(x2,y2,wlqitems[x2][y2])





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

    myfmt = mdates.DateFormatter('%H:%M')
    main_widget.MplWidget.ax1_1.xaxis.set_major_formatter(myfmt)

    main_widget.MplWidget.canvas.draw()
    main_widget.add_log("chart - Ready")


# i_now = datetime.now() + timedelta(days=1)
# i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
# i_datetime_series = pd.date_range(start=i_now, periods=13, freq='-33d')
# for i_i in range(len(i_datetime_series)-1):
#     i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=2)))
#     i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
#     s("get data " + symbol + " - " + str(i_datetime_series[i_i] + timedelta(days=2)) + " - " + str(i_datetime_series[i_i+1]))
#     i_df_stock = pd.DataFrame(None)
#     i_df_stock = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix)
#     i_datetime = tools.get_df_column(i_df_stock, "datetime")
#
#     db_act1 = ais_db()
#     ci1 = tools.get_df_column(i_df_stock, "t")
#     db_act1.add_instrument_value_multi_tchk(symbol, i_datetime, "t", ci1)
#
#     db_act2 = ais_db()
#     ci2 = tools.get_df_column(i_df_stock, "o")
#     t2 = threading.Thread(target=db_act2.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "o", ci2))
#
#     db_act3 = ais_db()
#     ci3 = tools.get_df_column(i_df_stock, "h")
#     t3 = threading.Thread(target=db_act3.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "h", ci3))
#
#     db_act4 = ais_db()
#     ci4 = tools.get_df_column(i_df_stock, "c")
#     t4 = threading.Thread(target=db_act4.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "c", ci4))
#
#     db_act5 = ais_db()
#     ci5 = tools.get_df_column(i_df_stock, "l")
#     t5 = threading.Thread(target=db_act5.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "l", ci5))
#
#     db_act6 = ais_db()
#     ci6 = tools.get_df_column(i_df_stock, "ohlc4")
#     t6 = threading.Thread(target=db_act6.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "ohlc4", ci6))
#
#     db_act7 = ais_db()
#     ci7 = tools.get_df_column(i_df_stock, "v")
#     t7 = threading.Thread(target=db_act7.add_instrument_value_multi_tchk, args=(symbol, i_datetime, "v", ci7))
#
#     t2.start()
#     time.sleep(1)
#     t3.start()
#     time.sleep(1)
#     t4.start()
#     time.sleep(1)
#     t5.start()
#     time.sleep(1)
#     t6.start()
#     time.sleep(1)
#     t7.start()
#
#     t2.join()
#     t3.join()
#     t4.join()
#     t5.join()
#     t6.join()
#     t7.join()
#
#     # "SELECT * FROM `APA` WHERE `v` is null or `ohlc4` is null or `l` is null or `c` is null or `h` is null or `o` is null"

return

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

# def referesh_ui(self):
#     s("Refresh Wl Ui")
#     i_wl_frame_object = np.ndarray(8, dtype=object, order='F')
#     i_wl_frame_object[0] = gui.WL_frame
#     i_wl_frame_object[1] = gui.WL_frame_2
#     i_wl_frame_object[2] = gui.WL_frame_3
#     i_wl_frame_object[3] = gui.WL_frame_4
#     i_wl_frame_object[4] = gui.WL_frame_5
#     i_wl_frame_object[5] = gui.WL_frame_6
#     i_wl_frame_object[6] = gui.WL_frame_7
#     i_wl_frame_object[7] = gui.WL_frame_8
#
#     i_noid = np.array(['', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9'])
#
#     for i_obj in i_wl_frame_object:
#         i_obj.hide()
#     i_no = 0
#     for index, row in self.df.iterrows():
#         i_wl_frame_object[i_no].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setText(row['symbol'])
#         i_wl_frame_object[i_no].findChild(QLabel, "WL_c"+i_noid[i_no]).setText(str(round(row['c'], 2)))
#         if row['c'] > row['pc']:
#             i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▲")
#             i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: green; background: #ffffff;")
#         else:
#             i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setText("▼")
#             i_wl_frame_object[i_no].findChild(QLabel, "WL_arrow"+i_noid[i_no]).setStyleSheet("color: red; background: #ffffff;")
#
#         i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_long"+i_noid[i_no]).setText("L:"+str(random.randint(0, 100))+"%")
#         i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_neutral"+i_noid[i_no]).setText("N:"+str(random.randint(0, 100))+"%")
#         i_wl_frame_object[i_no].findChild(QLabel, "WL_nn_short"+i_noid[i_no]).setText("S:"+str(random.randint(0, 100))+"%")
#         i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bull"+i_noid[i_no]).setValue(int(row['snt_bullish']*100))
#         i_wl_frame_object[i_no].findChild(QProgressBar, "WL_bear"+i_noid[i_no]).setValue(int(row['snt_bearish']*100))
#         i_wl_frame_object[i_no].show()
#         i_no = i_no + 1
#     return

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

# def save_prices_block(self, symbol, fromdt, todt):
#     s("Save prices block - " + symbol)
#
#     # i_tounix = tools.dbdt_to_unixdt(str(fromdt))
#     # i_fromunix = tools.dbdt_to_unixdt(str(todt))
#     s("get data " + symbol + " - " + str(fromdt) + " - " + str(todt))
#     i_df_stock = md.get_stock_candles(symbol, "1", fromdt, todt)
#     print(i_df_stock)
#     i_df_rsi = md.technical_indicator_rsi(symbol, "1", fromdt, todt)
#     print(i_df_rsi)
#     i_datetime = tools.get_df_column(i_df_stock, "datetime")
#
#     db_act1 = data_base()
#     ci1 = tools.get_df_column(i_df_stock, "t")
#     db_act1.add_instrument_value_multi(symbol, i_datetime, "t", ci1)
#
#     db_act2 = data_base()
#     ci2 = tools.get_df_column(i_df_stock, "o")
#     t2 = threading.Thread(target=db_act2.add_instrument_value_multi, args=(symbol, i_datetime, "o", ci2))
#
#     db_act3 = data_base()
#     ci3 = tools.get_df_column(i_df_stock, "h")
#     t3 = threading.Thread(target=db_act3.add_instrument_value_multi, args=(symbol, i_datetime, "h", ci3))
#
#     db_act4 = data_base()
#     ci4 = tools.get_df_column(i_df_stock, "c")
#     t4 = threading.Thread(target=db_act4.add_instrument_value_multi, args=(symbol, i_datetime, "c", ci4))
#
#     db_act5 = data_base()
#     ci5 = tools.get_df_column(i_df_stock, "l")
#     t5 = threading.Thread(target=db_act5.add_instrument_value_multi, args=(symbol, i_datetime, "l", ci5))
#
#     db_act6 = data_base()
#     ci6 = tools.get_df_column(i_df_stock, "ohlc4")
#     t6 = threading.Thread(target=db_act6.add_instrument_value_multi, args=(symbol, i_datetime, "ohlc4", ci6))
#
#     db_act7 = data_base()
#     ci7 = tools.get_df_column(i_df_stock, "v")
#     t7 = threading.Thread(target=db_act7.add_instrument_value_multi, args=(symbol, i_datetime, "v", ci7))
#
#     t2.start()
#     t3.start()
#     t4.start()
#     t5.start()
#     t6.start()
#     t7.start()
#
#     t2.join()
#     t3.join()
#     t4.join()
#     t5.join()
#     t6.join()
#     t7.join()
#     return


def refresh_wl_data_program(isymbol=""):
    log("run refresh_wl_data_program " + isymbol)
    i_from_unix = tools.get_ui_date_unix("from")
    i_to_unix = tools.get_ui_date_unix("to")
    wl.save_prices_block(isymbol, i_from_unix, i_to_unix)
    log("refresh_wl_data_program - Ready")

    class prices():

        df = ""
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
            self.from_year = int(gui.From_D.selectedDate().toString("yyyy"))
            self.from_month = int(gui.From_D.selectedDate().toString("MM"))
            self.from_day = int(gui.From_D.selectedDate().toString("dd"))
            self.from_hour = int(gui.From_T.dateTime().toString("hh"))
            self.from_minute = int(gui.From_T.dateTime().toString("mm"))
            self.from_secound = int(gui.From_T.dateTime().toString("ss"))

            self.to_year = int(gui.To_D.selectedDate().toString("yyyy"))
            self.to_month = int(gui.To_D.selectedDate().toString("MM"))
            self.to_day = int(gui.To_D.selectedDate().toString("dd"))
            self.to_hour = int(gui.To_T.dateTime().toString("hh"))
            self.to_minute = int(gui.To_T.dateTime().toString("mm"))
            self.to_secound = int(gui.To_T.dateTime().toString("ss"))
            return

        def set_dt(self, fort, y, mo, d, h, mi, sec):
            if fort == "from":
                self.from_year, self.from_month, self.from_day, self.from_hour, self.from_minute, self.from_secound = \
                    y, mo, d, h, mi, sec
            else:
                self.to_year, self.to_month, self.to_day, self.to_hour, self.to_minute, self.to_secound = \
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

        def get_unix_dt(self, fort):
            if fort == "from":
                return self.convert_to_unix_dt(self.from_year, self.from_month, self.from_day,
                                               self.from_hour, self.from_minute, self.from_secound)
            else:
                return self.convert_to_unix_dt(self.to_year, self.to_month, self.to_day,
                                               self.to_hour, self.to_minute, self.to_secound)

        def get_df_column(self, col):
            return self.df[col].to_numpy().tolist()




#### NDF111111111111111111111111111111111111111111

class n_date_frame():

    def __init__(self):
        self.df = pd.DataFrame(None)
        self.indicators = pd.DataFrame(None)
        self.load_indicators()

    def load_indicators(self):
        i_indicators = [
            ['SMA30'],
            ['SMA60'],
            ['ICHIMOKU'],
            ['RSI']
        ]
        self.indicators = pd.DataFrame(i_indicators)
        self.indicators.columns = ['indicator']
        self.indicators.set_index('indicator')

    def is_indicator(self, tech_indicator):
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if len(i_search) > 0:
            i_found = True
        else:
            i_found = False
        return i_found

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

    def add_tech(self, symbol, tech_indicator="SMA60", refresh=False):

        def sma(i_df, window_size, refresh=False):
            i_c1_name = "SMA" + str(window_size)
            i_df[i_c1_name] = i_df.iloc[:, i_df.columns.get_loc("ohlc4")].rolling(window=int(window_size)).mean()
            i_df[i_c1_name] = i_df[i_c1_name].fillna(0.123456)

            if refresh:
                i_df_drops = i_df[i_df[i_c1_name] == 0.123456]
                i_df = i_df.drop(i_df_drops.index, axis=0)

            i_df[i_c1_name] = round(i_df[i_c1_name], 6)
            i_df['datetime'] = i_df["datetime"].astype(str)
            i_prop_array = [i_c1_name]
            return i_prop_array, i_df

        log("ndf-> add_tech " + symbol + " - " + str(tech_indicator))

        if self.is_indicator(tech_indicator):

            i_res = db.get_last_m(symbol, 1)
            i_df = pd.DataFrame(i_res)
            i_df.columns = db.column_names
            last_dbdt = str(i_df.iloc[0]['datetime'])

            if refresh:
                i_res = db.get_first_null(symbol, tech_indicator)
                if db.row_count == 0:
                    log("ndf-> add_tech:" + tech_indicator + " is correct.")
                    return
                i_df = pd.DataFrame(i_res)
                i_df.columns = db.column_names
                first_dbdt = str(i_df.iloc[0]['datetime'] - timedelta(days=1))
            else:
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

                i_new_prop_array = []
                if tech_indicator == "SMA60":
                    i_new_prop_array, i_df = sma(i_df, 60, refresh)
                if tech_indicator == "SMA30":
                    i_new_prop_array, i_df = sma(i_df, 30, refresh)
                if tech_indicator == "RSI":
                    i_new_prop_array, i_df = sma(i_df, 60, refresh)

                # print("prop array", i_new_prop_array)
                # print(i_df.head())
                for i_new_prop in i_new_prop_array:
                    # print(i_new_prop)
                    i_datetime = tools.get_df_column(i_df, "datetime")
                    i_values = tools.get_df_column(i_df, i_new_prop)
                    if i_new_prop not in db.column_names:
                        db.add_symbol_float_property(symbol, i_new_prop)
                    db.add_symbol_value_multi(symbol, i_datetime, i_new_prop, i_values)
        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

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

class n_date_frame():

    def __init__(self):
        self.df = pd.DataFrame(None)
        self.indicators = pd.DataFrame(None)
        self.load_indicators()

    def load_indicators(self):
        i_indicators = [
            ['SMA30'],
            ['SMA60'],
            ['ICHIMOKU'],
            ['RSI']
        ]
        self.indicators = pd.DataFrame(i_indicators)
        self.indicators.columns = ['indicator']
        self.indicators.set_index('indicator')

    def is_indicator(self, tech_indicator):
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if len(i_search) > 0:
            i_found = True
        else:
            i_found = False
        return i_found

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

    def add_tech(self, symbol, tech_indicator="SMA60", refresh=False):

        def sma(i_df, window_size, refresh=False):
            i_c1_name = "SMA" + str(window_size)
            i_df[i_c1_name] = i_df.iloc[:, i_df.columns.get_loc("ohlc4")].rolling(window=int(window_size)).mean()
            i_df[i_c1_name] = i_df[i_c1_name].fillna(0.123456)

            if refresh:
                i_df_drops = i_df[i_df[i_c1_name] == 0.123456]
                i_df = i_df.drop(i_df_drops.index, axis=0)

            i_df[i_c1_name] = round(i_df[i_c1_name], 6)
            i_df['datetime'] = i_df["datetime"].astype(str)
            i_prop_array = [i_c1_name]
            return i_prop_array, i_df

        log("ndf-> add_tech " + symbol + " - " + str(tech_indicator))

        if self.is_indicator(tech_indicator):

            i_res = db.get_last_m(symbol, 1)
            i_df = pd.DataFrame(i_res)
            i_df.columns = db.column_names
            last_dbdt = str(i_df.iloc[0]['datetime'])

            if refresh:
                i_res = db.get_first_null(symbol, tech_indicator)
                if db.row_count == 0:
                    log("ndf-> add_tech:" + tech_indicator + " is correct.")
                    return
                i_df = pd.DataFrame(i_res)
                i_df.columns = db.column_names
                first_dbdt = str(i_df.iloc[0]['datetime'] - timedelta(days=1))
            else:
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

                i_new_prop_array = []
                if tech_indicator == "SMA60":
                    i_new_prop_array, i_df = sma(i_df, 60, refresh)
                if tech_indicator == "SMA30":
                    i_new_prop_array, i_df = sma(i_df, 30, refresh)
                if tech_indicator == "RSI":
                    i_new_prop_array, i_df = sma(i_df, 60, refresh)

                # print("prop array", i_new_prop_array)
                # print(i_df.head())
                for i_new_prop in i_new_prop_array:
                    # print(i_new_prop)
                    i_datetime = tools.get_df_column(i_df, "datetime")
                    i_values = tools.get_df_column(i_df, i_new_prop)
                    if i_new_prop not in db.column_names:
                        db.add_symbol_float_property(symbol, i_new_prop)
                    db.add_symbol_value_multi(symbol, i_datetime, i_new_prop, i_values)
        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

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

    def get_first_null(self, symbol, column):
        log("db-> get_first_null: " + symbol + " - "+str(column))
        i_sql_string = "SELECT * FROM `" + symbol + "` WHERE `" + column + "` IS NULL ORDER BY `datetime` LIMIT 1"
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


# def ndf_add(symbol="", p2="", p3=""):
#     ndf.add(symbol)
#     ndf.check(symbol)


# def ndf_tech(symbol, tech_indicator, p3=""):
#     ndf.add_tech(symbol, tech_indicator)


# def ndf_tech_refresh(symbol, p2="", p3=""):
#     i_sahdow = db.get_first_m(symbol, 1)
#     # Csak az oszlop nevek miatt kell
#     for i_c_name in db.column_names:
#         if ndf.is_indicator(i_c_name):
#             ndf.add_tech(symbol, i_c_name, True)


# def ndf_refresh(symbol="", p2="", p3=""):
#     ndf.refresh(symbol)
#     # ndf.check(symbol)
#     # gui.refresh_ui()


# def ndf_remove(symbol="", p2="", p3=""):
#     db.remove_symbol(symbol)


# def ndf_check(symbol="", p2="", p3=""):
#     ndf.check(symbol)
