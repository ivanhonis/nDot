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