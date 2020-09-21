# This Python file uses the following encoding: utf-8
import sys
import os
import time
import requests
import datetime
import json
import mysql.connector

from PySide2.QtWidgets import  QApplication,QWidget, QTableWidget, QTableWidgetItem
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
import threading


class dB():

    dBcursor = ""
    dBsesult = ""
    def dBoppen(self):
        mydb = mysql.connector.connect(
          host="localhost",
          user="yourusername",
          password="yourpassword",
          database="mydatabase"
        )

    def dBclose(self):
    def dBexecute(self,sqlstr):
        self.mycursor = mydb.cursor()
        mycursor.execute(sqlstr)
        # mycursor.execute("SELECT * FROM customers")
        return (dBcursor.fetchall())

class watchlist():
    wl_rows = 3
    wl_column = 5
    saved_items=[]

    def __init__(self):
        self.saved_items.append(["MSFT",self.getCompanyProfile2("MSFT"),"113.25","10:25","sell"])
        self.saved_items.append(["APA",self.getCompanyProfile2("APA"),"113.25","10:25","hold"])
        self.saved_items.append(["AAPL",self.getCompanyProfile2("AAPL"),"113.25","10:25","hold"])

    def getWLItems(self):
        return self.saved_items

    def getCompanyProfile2(self,symbol):
        request_url = 'https://finnhub.io/api/v1/stock/profile2?symbol='+symbol+'&token=bs9c9lvrh5rahoaofmt0'
        # print(request_url)
        r = requests.get(request_url)
        json_data = json.loads(r.text)
        name=json_data["name"]
        logo=json_data["logo"]
        return(name)

    def getQItems(self):
       ritems = [[0 for x in range(self.wl_column)] for y in range(self.wl_rows)]
       for x2 in range(self.wl_rows):
           for y2 in range(self.wl_column):
               ritems[x2][y2]=QTableWidgetItem(self.saved_items[x2][y2])
       return ritems


class prices():
    symbol='AAPL'

    from_year=2019
    from_month=10
    from_day=27
    from_hour = 10
    from_minute = 10
    from_secound = 0

    to_year=2019
    to_month=10
    to_day=28
    to_hour = 10
    to_minute = 10
    to_secound = 0

    close,c = [],[]
    heigh,h  = [],[]
    low,l  = [],[]
    open,o  = [],[]
    time,t  = [],[]

    def getUnixDT(self, cyear, cmonth, cday, chour, cminute, csecound):
        dt = datetime.datetime(cyear, cmonth, cday, chour, cminute, csecound)
        return(str(int(time.mktime(dt.timetuple()))))

    def getFromUnixDT(self):
        return self.getUnixDT(self.from_year,self.from_month,self.from_day,self.from_hour,self.from_minute,self.from_secound)

    def getToUnixDT(self):
        return self.getUnixDT(self.to_year,self.to_month,self.to_day,self.to_hour,self.to_minute,self.to_secound)

    def getStockCandle(self):
        request_url = 'https://finnhub.io/api/v1/stock/candle?symbol='+self.symbol+'&resolution=1&from='+self.getFromUnixDT()+'&to='+self.getToUnixDT()+'&token=bs9c9lvrh5rahoaofmt0'
        # print(request_url)
        r = requests.get(request_url)
        json_data = json.loads(r.text)
        self.close = json_data["c"]
        self.c = self.close
        self.open = json_data["o"]
        self.o = self.open
        self.low = json_data["l"]
        self.l = self.low
        self.high = json_data["h"]
        self.h = self.high
        self.time = json_data["t"]
        self.t = self.time
        return(r.json())


class iphoenix100(QWidget):
    def __init__(self):
        super(iphoenix100, self).__init__()
        self.load_ui()
        self.ui.Logs_Browser.setText("")
        self.setWindowTitle("iPhoenix100")


        watchlist_obj=watchlist()
        self.ui.Watch_list.setRowCount(watchlist_obj.wl_rows)
        self.ui.Watch_list.setColumnCount(watchlist_obj.wl_column)
        watchlist_obj=watchlist()
        wlqitems=watchlist_obj.getQItems()
        for x2 in range(watchlist_obj.wl_rows):
            for y2 in range(watchlist_obj.wl_column):
                self.ui.Watch_list.setItem(x2,y2,wlqitems[x2][y2])

    log_Text = ""

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)

        # hozzárendelések
        self.ui.Run_Button.clicked.connect(self.Run_Button_Action)
        self.ui.Command_Line.returnPressed.connect(self.Run_Button_Action)
        self.ui.Command_Line.textChanged.connect(self.Command_Line_Changed)
        ui_file.close()


    def getUi():
        return self.ui


    def Run_Button_Action(self):
        command_text = self.ui.Command_Line.text()
        command_partitioned = command_text.partition(" ")
        command_text_first_word = command_partitioned[0]
        if len(command_partitioned) == 3:
            param1=command_partitioned[2]
        if len(command_partitioned) == 5:
            param1=command_partitioned[2]
            param2=command_partitioned[4]
        if len(command_text.partition(' ')) == 7:
            param1=command_partitioned[2]
            param2=command_partitioned[4]
            param3=command_partitioned[6]

        self.add_Log("call "+command_text)
        self.ui.Command_Line.setText("")

        if command_text_first_word == "getprice" or command_text_first_word == "getPrice":
            getprice_program(param1)

        if command_text_first_word == "test":
            test_program('test')

        if command_text_first_word == "chart":
            chart_program('')

        if command_text_first_word == "close":
            self.close()

        if command_text_first_word == "exit":
            self.close()

    def Command_Line_Changed(self):
        self.ui.Command_Hint.setText("")
        command_text= self.ui.Command_Line.text()
        command_text_first_word = command_text.partition(' ')[0]

        if command_text_first_word == "test":
            self.ui.Command_Hint.setText("test")

        if command_text_first_word == "chart":
            self.ui.Command_Hint.setText("chart stock")

        if command_text_first_word == "getPrice" or command_text_first_word == "getprice":
            self.ui.Command_Hint.setText("getPrice")


    def add_Log(self,add_text):
        self.log_Text=time.strftime("%d %B, %Y %H:%M:%S")+" > "+add_text + " \r" + self.log_Text
        self.ui.Logs_Browser.setText(self.log_Text)

def getprice_program(isymbol):
    main_widget.add_Log("run getPrice "+isymbol)

    selected_stock = prices()
    selected_stock.symbol = isymbol

    selected_stock.from_year = int(main_widget.ui.From_DT.dateTime().toString("yyyy"))
    selected_stock.from_month = int(main_widget.ui.From_DT.dateTime().toString("MM"))
    selected_stock.from_day = int(main_widget.ui.From_DT.dateTime().toString("dd"))
    selected_stock.from_hour = int(main_widget.ui.From_DT.dateTime().toString("hh"))
    selected_stock.from_minute = int(main_widget.ui.From_DT.dateTime().toString("mm"))
    selected_stock.from_secound = int(main_widget.ui.From_DT.dateTime().toString("mm"))

    selected_stock.to_year = int(main_widget.ui.To_DT.dateTime().toString("yyyy"))
    selected_stock.to_month = int(main_widget.ui.To_DT.dateTime().toString("MM"))
    selected_stock.to_day = int(main_widget.ui.To_DT.dateTime().toString("dd"))
    selected_stock.to_hour = int(main_widget.ui.To_DT.dateTime().toString("hh"))
    selected_stock.to_minute = int(main_widget.ui.To_DT.dateTime().toString("mm"))
    selected_stock.to_secound = int(main_widget.ui.To_DT.dateTime().toString("mm"))
    selected_stock.getStockCandle()
    main_widget.add_Log(str(selected_stock.c))


def test_program(atr):
    main_widget.add_Log("run test_program")
    print("test")

def chart_program(atr):
    main_widget.add_Log("run chart_program")
    import numpy as np
    import matplotlib.pyplot as plt


    fig, (ax1, ax2) = plt.subplots(2, 1)
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)

    dt = 0.01
    t = np.arange(0, 30, dt)

    # Fixing random state for reproducibility
    np.random.seed(19680801)


    nse1 = np.random.randn(len(t))                 # white noise 1
    nse2 = np.random.randn(len(t))                 # white noise 2
    r = np.exp(-t / 0.05)

    cnse1 = np.convolve(nse1, r, mode='same') * dt   # colored noise 1
    cnse2 = np.convolve(nse2, r, mode='same') * dt   # colored noise 2

    # two signals with a coherent part and a random part
    s1 = 0.01 * np.sin(2 * np.pi * 10 * t) + cnse1
    s2 = 0.01 * np.sin(2 * np.pi * 10 * t) + cnse2

    ax1.plot(t, s1, t, s2)
    ax1.set_xlim(0, 5)
    ax1.set_xlabel('time')
    ax1.set_ylabel('s1 and s2')
    ax1.grid(True)

    cxy, f = ax2.csd(s1, s2, 256, 1. / dt)
    ax2.set_ylabel('CSD (db)')
    plt.show()

# időzítő
class TestThreading(object):
    def __init__(self, interval=60):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # More statements comes here
            print(datetime.datetime.now().__str__() + ' : Start task in the background')
            time.sleep(self.interval)

if __name__ == "__main__":
    tr = TestThreading()
    app = QApplication([])
    main_widget = iphoenix100()

    #main_widget.showFullScreen()
    main_widget.show()
    sys.exit(app.exec_())

