# This Python file uses the following encoding: utf-8
import sys
import os
import time
import requests
import datetime
import json
import mysql.connector
import numpy as np

from PySide2.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
import threading


class ais_db():
    aisdb = ""
    cursor = ""
    host = "sql132.main-hosting.eu"
    user = "u826803502_AIS1"
    password = "+1zZJqwQ"
    database = "u826803502_ArtIntSol"

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
        # print(sqlstr)
        print("minden ok?",self.aisdb.is_connected())
        if self.aisdb.is_connected():
            try:
                self.cursor.execute(sqlstr, multiple)
                print(self.cursor.rowcount, "inserted row")
                self.setcursor()
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
        else:
            self.open()
            self.cursor.execute(sqlstr, multiple)
            self.setcursor()
            print(self.cursor.rowcount, "inserted row")
        return

    def execute_fetchall(self, sqlstr):
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.setcursor()
        return self.cursor.fetchall()

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
        print("ins", instrument,"----------------------------------------------")
        print(dt_array)
        print(prop)
        print(val_array)
        print("add")
        self.add_instrument(instrument)
        self.add_instrument_float_property(instrument, prop)
        i_dt_array_len = len(dt_array)
        i_elemet_block_size = 32000

        # beszúrom az üreseket, ha még nincsenek és utána minden módosítom
        i_sql_elements_array = ["" for x in range(1+int(i_dt_array_len / i_elemet_block_size))]

        for i_i in range(i_dt_array_len):
            i_pos = int(i_i / i_elemet_block_size)
            i_sql_elements_array[i_pos] = i_sql_elements_array[i_pos] + "('" + dt_array[i_i] + "', '"+ str(val_array[i_i]) +"'), "

        for i_i in range(len(i_sql_elements_array)):
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
    close, c = [], []
    heigh, h = [], []
    low, l = [], []
    open, o = [], []
    time, t = [], []

    def set_dt(self,fort,y,mo,d,h,mi,sec):
        if fort == "from":
            self.from_year, self.from_month, self.from_day, self.from_hour, self.from_minute, self.from_secound =\
                y, mo, d, h, mi, sec
        else:
            self.to_year, self.to_month, self.to_day, self.to_hour, self.to_minute, self.to_secound =\
                y, mo, d, h, mi, sec
        return

    def convert_to_unix_dt(self, cyear, cmonth, cday, chour, cminute, csecound):
        dt = datetime.datetime(cyear, cmonth, cday, chour, cminute, csecound)
        return str(int(time.mktime(dt.timetuple())))

    def convert_to_db_dt(self, unix_datetime):
        i_value = datetime.datetime.fromtimestamp(unix_datetime)
        return (f"{i_value:%Y-%m-%d %H:%M:%S}")

    def convert_to_db_dt_multi(self, unix_datetime_array):

        i_result_array = []

        for i_i in range(len(unix_datetime_array)):
            i_value = (datetime.datetime.fromtimestamp(unix_datetime_array[i_i]))
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

    def get_stock_candle(self):
        i_request_url = 'https://finnhub.io/api/v1/stock/candle?symbol='+self.symbol+'&resolution=1&from='+self.get_unix_dt("from")+'&to='+self.get_unix_dt("to")+'&token=bs9c9lvrh5rahoaofmt0'
        i_r = requests.get(i_request_url)
        i_json_data = json.loads(i_r.text)
        if i_json_data["s"] == "ok":
            self.close = i_json_data["c"]
            self.c = self.close
            self.open = i_json_data["o"]
            self.o = self.open
            self.low = i_json_data["l"]
            self.l = self.low
            self.high = i_json_data["h"]
            self.h = self.high
            self.time = self.convert_to_db_dt_multi(i_json_data["t"])
            self.t = self.time

        return i_r.json()


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
        path = os.path.join(os.path.dirname(__file__), "C:/Users/honis.ivan/Documents/IPhoneix120/form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)

        # hozzárendelések
        self.ui.Run_Button.clicked.connect(self.Run_Button_Action)
        self.ui.Command_Line.returnPressed.connect(self.Run_Button_Action)
        self.ui.Command_Line.textChanged.connect(self.Command_Line_Changed)
        ui_file.close()

    def getUi(self):
        return self.ui

    def Run_Button_Action(self):
        command_text = self.ui.Command_Line.text()
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

    def Command_Line_Changed( self ):
        self.ui.Command_Hint.setText( "" )
        command_text= self.ui.Command_Line.text()
        command_text_first_word = command_text.partition(' ')[0]

        if command_text_first_word == "test":
            self.ui.Command_Hint.setText("test")

        if command_text_first_word == "chart":
            self.ui.Command_Hint.setText("chart stock")

        if command_text_first_word == "getPrice" or command_text_first_word == "getprice":
            self.ui.Command_Hint.setText("getPrice")


    def add_Log( self,add_text ):
        self.log_Text=time.strftime( "%d %B, %Y %H:%M:%S" )+" > "+add_text + " \r" + self.log_Text
        self.ui.Logs_Browser.setText( self.log_Text )


def getprice_program(isymbol):
    main_widget.add_Log( "run getPrice "+isymbol )

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
    selected_stock.get_stock_candle()
    aisdb.add_instrument_value_multi(isymbol, selected_stock.t, "c", selected_stock.c)
    aisdb.add_instrument_value_multi(isymbol, selected_stock.t, "o", selected_stock.o)
    aisdb.add_instrument_value_multi(isymbol, selected_stock.t, "h", selected_stock.h)
    aisdb.add_instrument_value_multi(isymbol, selected_stock.t, "l", selected_stock.h)

def test_program():
    main_widget.add_Log("run test_program")
    print("test")

def chart_program():
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
class back_processes(object):
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
    aisdb = ais_db() # Art Int Sol adatbázis kapcsolat létrehozása
    aisdb.open()
    aisdb.close()
    aisdb.open()
    bp = back_processes() # háttér cron job szerű futásindítás 60 másodpercenkénti futás
    app = QApplication([])

    main_widget = iphoenix100()
    #main_widget.showFullScreen()

    # teszt dolgok ide jönnek
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
    print("start")
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:47:00", "c", 123456)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:47:00", "c", 12345.78)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "c", 12345.12345)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "c", 12345.88)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "o", 12345.88)
    # aisdb.add_instrument_value("MSFT", "2020-08-12 16:48:00", "h", 12345.88)
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:48:00", "l", 123456.123456)
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:48:00", "note", "note")
    # aisdb.add_instrument_value("AAPL", "2020-08-12 16:49:00", "note", 1245)
    print("stop")
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