# detect is it a local running environment or a cloud running environment
print("Status: Checking environment.")
try:
    with open('local_run.txt') as f:
        print("Status: Local run.")
        LocalRUN = True
        LogTo = "Gui"
        f.close()
except IOError:
    LocalRUN = False
    print("Status: Cloud run.")
    LogTo = "Screen"

if LocalRUN:
    # This Python file uses the following encoding: utf-8
    # GUI -----------------------------------------------
    # from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QScrollArea, QProgressBar, QToolButton, QMessageBox, \
    #     QFrame
    from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QProgressBar, QToolButton, QMessageBox, QFrame
    # from PyQt5 import QtGui, QtCore, QtWebEngineWidgets, uic
    from PyQt5 import QtGui, QtCore, uic
    from PyQt5.QtCore import QTime, QDate

    from tkinter import *  # ez a show table hoz kell.

    import psutil  # for test command
    from functools import partial  # a kattintás hozzá rendeléséhez használom

# other checked ----------------------------------------------------
import pandas as pd
import numpy as np
import os  # for test command
import pandas_ta as ta  # technical indicators for ndf.tech
from datetime import datetime, timedelta, time as dt_time  # a log ban használom
import time
import sys  # a test parancs használja hdd szabad hely kiíratására
# from multiprocessing import Process
import threading  # info párhuzamosítva van illetve ndf.add
import random  # a image előállításához kell random mintavétel
import pickle
import json  # dataset config beolvasóhoz kell
import re  # dataset config beolvasóhoz kell
import pathlib  # dataset config beolvasóhoz kell

# User classes ------------------------------------------------------
from classes.trade import trade
from classes.market_data import market_data
from classes.nd_db import nd_db
from classes.nchart import nchart
from classes.n_datasets import n_dataset
from classes.n_data_frame_meta import n_date_frame_meta
from classes.tools import tools

# import websocket

if LocalRUN:
    class gui(QWidget, object):
        # start_command = "ndf.images PLAY ICX1"

        def __init__(self):
            super(gui, self).__init__()
            self.load_ui()
            self.usd_huf = 0
            # self.show_dialog_return = False
            self.commands = self.load_commands()
            # első alkalommal amikor megjelenik a trade frame akkor is újra kalkulálni
            self.pause_trader_frame_calculation = True
            # refresh_info párhuzamosítva van hogy ne kelljen várni a frissülésére--
            # self.refresh_info_thread = ""
            self.refresh_info_string = ""
            self.command_line_history = []
            self.command_line_history_position = 0
            self.load_command_line_history()

            # ablak beállítások ----------------------------------------------------
            self.setWindowTitle("   nDot")
            app_icon = QtGui.QIcon()
            app_icon.addFile('./images/ndot_icon_x2.png', QtCore.QSize(16, 16))
            app.setWindowIcon(app_icon)

        def closeEvent(self, event):
            trade.monitor_stop()
            trade.broker_stop()
            md.stream_stop()
            nddb.close()
            print("Status: GUI Closed")

        def keyPressEvent(self, e):
            if e.key() == QtCore.Qt.Key_Escape:
                self.close()
            elif e.key() == QtCore.Qt.Key_Up:
                self.command_line_history_position -= 1
                self.command_line_history_position = max(0, self.command_line_history_position)
                self.Command_Line.setText(self.command_line_history[self.command_line_history_position])
            elif e.key() == QtCore.Qt.Key_Down:
                self.command_line_history_position += 1
                i_last_position = len(self.command_line_history)
                self.command_line_history_position = min(i_last_position - 1, self.command_line_history_position)
                self.Command_Line.setText(self.command_line_history[self.command_line_history_position])

        def save_command_line_history(self):
            with open('command_line_history.pickle', 'wb') as f:
                pickle.dump(self.command_line_history, f)

        def load_command_line_history(self):
            try:
                with open('command_line_history.pickle', 'rb') as f:
                    self.command_line_history = pickle.load(f)
            except:
                self.command_line_history = []

        # GUI - Setup --------------------------------------------------------------------------------------

        def load_ui(self):

            def get_similar_object_list(prefix, object_group_name):
                wl_btn_list = {}
                i_n = prefix + "1"
                wl_btn_list[i_n] = self.findChild(QToolButton, object_group_name)
                for i_i in range(2, 13):
                    i_n = prefix + str(i_i)
                    i_src = object_group_name + "_" + str(i_i)
                    wl_btn_list[i_n] = self.findChild(QToolButton, i_src)
                return wl_btn_list

            def connect_similar_object_list(object_group, connect_function):
                for i, i_o in enumerate(object_group):
                    if connect_function == "wl_btn_chart":
                        object_group[i_o].clicked.connect(partial(wl_btn_chart, i + 1))
                    elif connect_function == "wl_btn_show":
                        object_group[i_o].clicked.connect(partial(wl_btn_show, i + 1))
                    elif connect_function == "wl_trade_short":
                        object_group[i_o].clicked.connect(partial(wl_trade_short, i + 1))
                    elif connect_function == "wl_trade_long":
                        object_group[i_o].clicked.connect(partial(wl_trade_long, i + 1))
                    elif connect_function == "tr_stop":
                        object_group[i_o].clicked.connect(partial(tr_stop, i + 1))

            uic.loadUi("./qt_ui/form.ui", self)
            # self.Command_Line.setText(self.start_command)

            # Csoportos hozzárendelések ----------------------------------------------------------

            wl_btn_chart_list = get_similar_object_list("wlc", "WL_btn_chart")
            connect_similar_object_list(wl_btn_chart_list, "wl_btn_chart")

            wl_btn_show_list = get_similar_object_list("wls", "WL_btn_show")
            connect_similar_object_list(wl_btn_show_list, "wl_btn_show")

            wl_trade_short_list = get_similar_object_list("wlsl", "WL_trade_short")
            connect_similar_object_list(wl_trade_short_list, "wl_trade_short")

            wl_trade_long_list = get_similar_object_list("wlll", "WL_trade_long")
            connect_similar_object_list(wl_trade_long_list, "wl_trade_long")

            wl_trade_stop_list = get_similar_object_list("wlst", "WL_trade_stop")
            connect_similar_object_list(wl_trade_stop_list, "tr_stop")

            # Command hozzárendelések ---------------------------------------------

            self.Run_Button.clicked.connect(self.run_button_action)
            self.Command_Line.returnPressed.connect(self.run_button_action)
            self.Command_Line.textChanged.connect(self.command_line_changed)

            # Trade frame hozzárendelések ----------------------------------------
            self.Tr_cancel.clicked.connect(self.tr_cancel)
            self.Tr_qty.valueChanged.connect(self.tr_change_data)
            self.Tr_set_order.clicked.connect(tr_set_order)
            self.Tr_stop_all.clicked.connect(tr_stop_all)
            self.Tr_frame.hide()

            # watch list up area -------------------------------------------------
            self.Tr_portfolio_monitor.stateChanged.connect(tr_portfolio_monitor)
            self.Ndf_stream.stateChanged.connect(ndf_stream)
            self.Tr_info_refresh.clicked.connect(tr_info_refresh)

            # Date time setter ----------------------------------------
            i_now = datetime.now()
            self.From_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
            self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
            self.From_T.setTime(QTime(i_now.hour, i_now.minute))
            self.To_T.setTime(QTime(i_now.hour, i_now.minute))
            self.Datetime_mod1.clicked.connect(partial(self.date_modifier, "hours", 6))
            self.Datetime_mod2.clicked.connect(partial(self.date_modifier, "days", 1))
            self.Datetime_mod3.clicked.connect(partial(self.date_modifier, "days", 2))
            self.Datetime_mod4.clicked.connect(partial(self.date_modifier, "days", 4))
            self.Datetime_mod5.clicked.connect(partial(self.date_modifier, "days", 30))
            self.Datetime_now.clicked.connect(self.date_now)

        def refresh_ui(self, mode="full"):

            def get_frame_objects_list(prefix, object_group_name):
                wl_frame_list = {}
                i_n = prefix + "1"
                wl_frame_list[i_n] = self.findChild(QFrame, object_group_name)
                for i_i in range(2, 13):
                    i_n = prefix + str(i_i)
                    i_src = object_group_name + "_" + str(i_i)
                    wl_frame_list[i_n] = self.findChild(QFrame, i_src)
                return wl_frame_list

            i_noid = ['', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12']
            if mode == "full":
                i_wl_frame_list = get_frame_objects_list("fr", "WL_frame")
                for i_obj in i_wl_frame_list:
                    i_wl_frame_list[i_obj].hide()
                i_no = 0
                for index, row in wl.df.iterrows():
                    i_symbol = row['symbol']
                    f_id = "fr" + str(i_no + 1)
                    i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol" + i_noid[i_no]).setText(i_symbol)
                    i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol" + i_noid[i_no]).setToolTip(row['profil'])
                    i_info = self.get_monitor_info_by_symbol(i_symbol)
                    i_wl_frame_list[f_id].findChild(QLabel, "WL_info" + i_noid[i_no]).setText(i_info)
                    i_pl = self.get_pl_by_symbol(i_symbol)
                    i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setText(i_pl)
                    i_wl_frame_list[f_id].findChild(QProgressBar, "WL_bear" + i_noid[i_no]).setValue(
                        int(row['snt_bearish'] * 100))
                    i_wl_frame_list[f_id].show()
                    i_no = i_no + 1
            elif mode == "info":
                i_wl_frame_list = get_frame_objects_list("fr", "WL_frame")
                i_no = 0
                for index, row in wl.df.iterrows():
                    i_symbol = row['symbol']
                    f_id = "fr" + str(i_no + 1)

                    # akkor frissítek ha volt változás
                    i_info = self.get_monitor_info_by_symbol(i_symbol)
                    i_info_now = i_wl_frame_list[f_id].findChild(QLabel, "WL_info" + i_noid[i_no]).text()
                    if i_info != i_info_now:
                        i_wl_frame_list[f_id].findChild(QLabel, "WL_info" + i_noid[i_no]).setText(i_info)
                        QApplication.processEvents()

                    # akkor frissítek ha volt változás
                    i_pl = self.get_pl_by_symbol(i_symbol)
                    i_pl_now = i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).text()
                    if i_pl != i_pl_now:
                        if i_symbol in tuple(trade.cp_df.index):
                            if float(trade.cp_df.loc[i_symbol, "unrealized_pl"]) > 0:
                                i_wl_frame_list[f_id].findChild(QToolButton,
                                                                "WL_trade_stop" + i_noid[i_no]).setStyleSheet(
                                    'color: #ffffff; background: #ff9100')
                            else:
                                i_wl_frame_list[f_id].findChild(QToolButton,
                                                                "WL_trade_stop" + i_noid[i_no]).setStyleSheet(
                                    'color: #000000; background: #ff9100')
                        else:
                            i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setStyleSheet(
                                'color: #ffffff; background: #ff9100')
                        i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setText(i_pl)
                        QApplication.processEvents()
                    i_no = i_no + 1

        # GUI - Trader Frame ----------------------------------------------------------------------------------------

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
            self.Tr_market_price.setText(str(trade.order["market_price"]))
            # self.Tr_trailing_stop.setValue(True)
            self.Tr_qty.setValue(trade.order["qty"])
            self.pause_trader_frame_calculation = False
            self.tr_change_data()
            self.Tr_frame.show()
            QApplication.processEvents()

        def tr_cancel(self):
            self.Tr_frame.hide()

        def tr_change_data(self):
            if not self.pause_trader_frame_calculation:
                if self.usd_huf == 0:
                    self.usd_huf = md.get_usdhuf()
                trade.order["qty"] = int(self.Tr_qty.value())
                i_value_usd = round(trade.order["qty"] * trade.order["market_price"], 2)
                i_value_huf = round(i_value_usd * self.usd_huf, 2)
                i_value_text = '{0:,.2f}'.format(i_value_usd) + " USD\n" + '{0:,.2f}'.format(i_value_huf) + " HUF"
                self.Tr_value.setText(i_value_text)
                QApplication.processEvents()

        # GUI - DateTime Block  -----------------------------------------------------------

        def date_now(self):
            i_now = datetime.now()
            self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
            self.To_T.setTime(QTime(i_now.hour, i_now.minute))

        def date_modifier(self, interval_type, interval_num):
            i_nowp = datetime.now() - timedelta(**{interval_type: interval_num})
            self.From_D.setDate(QDate(i_nowp.year, i_nowp.month, i_nowp.day))
            self.From_T.setTime(QTime(i_nowp.hour, i_nowp.minute))

        # GUI - Commands -----------------------------------------------------------

        def load_commands(self):
            i_return = [
                ['help', 'help2', 'help - List of all commands!', 0],
                ['do', 'do', 'do', 0],
                ['test', 'test', 'test <p1 / optional> <p2 / optional> <p3 / optional>', 0],
                ['wl.add', 'wl_add', 'wl.add <symbol> <year(s)>', 0],
                ['wl.remove', 'wl_remove', 'wl.remove <symbol> ', 1],
                # ['wl.refresh.close', 'wl_refresh_close', 'wl.refresh.close <> ', 0],
                ['wl.refresh.profile', 'wl_refresh_profile', 'wl.refresh.profile', 0],
                ['wl.refresh.sentiment', 'wl_refresh_sentiment', 'wl.refresh.sentiment', 0],
                # ['wl.refresh.all', 'wl_refresh_all', 'wl.refresh.all <> ', 0],
                # ['ndf.add', 'ndf_add', 'ndf.add <symbol>', 1],
                ['ndf.add', 'ndf_add', 'ndf.add <symbol> <year(s)>', 1],
                ['ndf.tech', 'ndf_tech', 'ndf.tech <symbol> <technical indicator>', 2],
                ['ndf.tech.remove', 'ndf_tech_remove', 'ndf.tech.remove <symbol> <technical indicator>', 2],
                ['ndf.tech.refresh', 'ndf_tech_refresh', 'ndf.tech.refresh <symbol>', 1],
                ['ndf.tech.refresh.all', 'ndf_tech_refresh_all', 'ndf.tech.refresh.all', 0],
                ['ndf.tech.info', 'ndf_tech_info', 'ndf.tech.info', 0],
                # ['ndf.images', 'ndf_images', 'ndf.images <symbol> <image> <contras: [symbol,symbol]>', 1],
                ['ndf.dataset', 'ndf_dataset', 'ndf.dataset <symbol> <config_file>', 1],
                ['ndf.remove', 'ndf_remove', 'ndf.remove <symbol>', 1],
                ['ndf.refresh', 'ndf_refresh', 'ndf.refresh <symbol>', 1],
                ['ndf.refresh.all', 'ndf_refresh_all', 'ndf.refresh.all', 0],
                ['ndf.info', 'ndf_info', 'ndf.info', 0],
                ['ndf.columns', 'ndf_columns', 'ndf.columns', 0],
                ['ndf.show.last', 'ndf_show_last', 'ndf.show.last <symbol> <numbers / optional>', 1],
                # ['ndf.refresh', 'ndf_refresh', 'ndf.refresh <symbol>', 1],
                # ['ndf.remove', 'ndf_remove', 'ndf.remove <symbol>', 1],
                # ['ndf.check', 'ndf_check', 'ndf.check <symbol>', 1],
                # ['ndf.chart', 'ndf_chart', 'ndf.chart <symbol> UI date time', 1],
                # ['ndf.chart.last', 'ndf_chart_last', 'ndf.chart.last <symbol> <numbers / optional>', 1],
                # ['ndf.show.last', 'ndf_show_last', 'ndf.show.last <symbol> <numbers / optional>', 1],
                # ['ndf.tech', 'ndf_tech', 'ndf.tech <symbol> <technical indicator>', 2],
                # ['ndf.tech.refresh', 'ndf_tech_refresh', 'ndf.tech.refresh <symbol>', 1],
                ['md.check', 'md_check', 'md.check <symbol>', 0],
                ['md.symbols', 'md_symbols', 'md.symbols <market>', 0],
                # ['bp.start', 'bp_start', 'bp.start <> ', 0],
                # ['bp.stop', 'bp_stop', 'bp.stop <> ', 0],
                ['exit', 'exit', 'exit', 0]
            ]
            i_return = pd.DataFrame(i_return)
            i_return.columns = ['command', 'program', 'hint', 'params']
            i_return.set_index('command')
            return i_return

        def run_button_action(self):
            def run_method(i_program, args):
                # Save command ---------------------------------------
                if self.command_line_history[0] != self.Command_Line.text():
                    self.command_line_history.insert(0, self.Command_Line.text())
                    self.command_line_history = self.command_line_history[:25]
                    self.command_line_history_position = 0
                    self.save_command_line_history()
                # Run command -------------------------------------------
                method = eval(i_program)
                kwargs = {}
                args_str = ', '.join(map(str, args))
                i_start = datetime.now()
                log("Start: " + command_text_first_word + " <" + args_str + ">", True, False)
                method(*args, **kwargs)
                log("Ready.", False, False)
                log("Runtime:" + str(datetime.now() - i_start), False, False)
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
                        if len(wl.df.loc[wl.df['symbol'] == command_partitioned[1]]) > 0:
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

        def print_command(self):
            log("Commands:")
            for i_row in tuple(self.commands["hint"]):
                log(" - " + i_row)

        def command_line_changed(self):
            command_text = self.Command_Line.text()
            command_text_first_word = str.lower(command_text.partition(' ')[0])
            i_found, i_program, i_hint, i_params = self.get_command(command_text_first_word)
            if i_found:
                self.mark_command_line(i_hint, False)
            else:
                self.mark_command_line("", False)

        def mark_command_line(self, message, bug=True):
            if bug:
                self.Command_Line.setStyleSheet('''background-color: #ffaaaa;
                                                border-top-left-radius: 15px;
                                                border-top-right-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                border-bottom-left-radius: 0px;
                                                border-bottom: 1px solid #eeeeee;
                                                padding-left: 10px;
                                                border-top: 1px solid #888888;
                                                border-left: 1px solid #888888;
                                                ''')
                self.Command_Hint.setText(message)
                QApplication.processEvents()
            else:
                self.Command_Line.setStyleSheet('''background-color: #ffffff;
                                                border-top-left-radius: 15px;
                                                border-top-right-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                border-bottom-left-radius: 0px;
                                                border-bottom: 1px solid #eeeeee;
                                                padding-left: 10px;
                                                border-top: 1px solid #888888;
                                                border-left: 1px solid #888888;
                                                ''')

                self.Command_Hint.setText(message)
                QApplication.processEvents()

        # GUI - Info text creators ------------------------------------------------

        def get_pl_by_symbol(self, symbol):
            if symbol in trade.cp_df.index:
                i_p = float(trade.cp_df.loc[symbol, "unrealized_pl"])
                i_return = f"STOP {i_p}$"
            else:
                i_return = "-"
            return i_return

        def create_tr_info_string(self):

            def nbs(no):
                return "&nbsp;" * no

            def bnb(blocked):
                if blocked:
                    i_return = "<b><font color='#ffffff'>Blocked</font></b>"
                else:
                    i_return = "<b><font color='#999999'>Ready</font></b>"
                return i_return

            def yn(yes_no):
                if yes_no:
                    i_return = "<b><font color='#ffffff'>Yes</font></b>"
                else:
                    i_return = "<b><font color='#999999'>No</font></b>"
                return i_return

            def onf(on_off):
                if on_off:
                    i_return = "<b><font color='#ffffff'>On</font></b>"
                else:
                    i_return = "<b><font color='#999999'>Off</font></b>"
                return i_return

            def oc(open_close):
                if open_close:
                    i_return = "<b><font color='#ffffff'>Open</font></b>"
                else:
                    i_return = "<b><font color='#999999'>Closed</font></b>"
                return i_return

            def rq():
                i_max_key = max(trade.request_count.keys())
                return trade.request_count[i_max_key]

            def get_dt(date_time_str):
                date_time_str = date_time_str[:19]
                hours_added = timedelta(hours=6)
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                date_time_obj = date_time_obj + hours_added
                return date_time_obj.strftime("%Y.%m.%d %H:%M:%S")

            def ntofs(numb):
                i_return = int(float(numb))
                i_return = f"{i_return:,}"
                return i_return

            i_a = trade.get_account()
            i_c = trade.get_clock()
            if i_c.is_open:
                i_cst = "Close:"
                i_cs = get_dt(str(i_c.next_close))
            else:
                i_cst = "Open:"
                i_cs = get_dt(str(i_c.next_open))

            if self.usd_huf == 0:
                self.usd_huf = md.get_usdhuf()

            s = 10
            i_return = f"""
            <html><head/><body>
            <table border="0" cellspacing="5" cellpadding="0">
                <tr>
                    <td>Monitor: </td><td>{onf(trade.monitor_is_working)} - {trade.monitor_refresh_rate}</td><td>{nbs(s)}</td><td>Equity:</td><td>{ntofs(i_a.equity)} USD</td><td>{nbs(s)}</td><td>Market:</td><td>{oc(i_c.is_open)}</td>
                </tr>
                <tr>
                    <td>Broker:</td><td>{onf(trade.broker_is_working)}  - {trade.broker_refresh_rate}</td><td>{nbs(s)}</td><td>USD/HUF:</td><td>{self.usd_huf} HUF</td><td>{nbs(s)}</td><td>{i_cst}</td><td>{i_cs}</td>
                </tr>
                <tr>
                    <td>Reguests:</td><td>{rq()}/{trade.request_count_max}</td><td>{nbs(s)}</td><td>Cash / power:</td><td>{ntofs(i_a.cash)} / {ntofs(i_a.buying_power)} USD</td><td>{nbs(s)}</td><td>Status:</td><td>{bnb(i_a.trading_blocked)} - {i_a.status}</td>
                </tr>
                <tr>
                    <td></td><td></td><td>{nbs(s)}</td><td>Block size:</td><td>{int(trade.config["trade_block_size"])} USD</td><td>{nbs(s)}</td><td></td><td></td>
                </tr>
            </table>
            </body></html>
            """
            return i_return

        def get_monitor_info_by_symbol(self, symbol):
            # print("get_monitor_info_by_symbol\n", symbol)
            # print("get_monitor_info_by_symbol\n", trade.tp_df)
            if symbol in trade.tp_df.index:
                i_qt = int(trade.tp_df.loc[symbol, "target_position"])
            else:
                i_qt = 0
            # print("get_monitor_info_by_symbol\n", trade.cp_df)
            if symbol in trade.cp_df.index:
                i_qc = int(trade.cp_df.loc[symbol, "qty"])
                i_p = float(trade.cp_df.loc[symbol, "current_price"])
                i_v = float(trade.cp_df.loc[symbol, "market_value"])
            else:
                i_qc = 0
                i_p = 0
                i_v = 0
            i_return = f"q: {i_qt} / {i_qc}\np: {i_p}$\nv: {i_v}$"
            # print(i_return,"\n\n")
            return i_return

        def tlog(self, add_text, line=False, indent=True, color="normal"):
            i_for_cut = "<html>\n<head/>\n<body>\n<br/>\n<p>\n</p>\n</body>\n</html>"
            i_for_cut = i_for_cut.splitlines()
            i_cut_html = self.Logs_Trade.text()
            for i_c in i_for_cut:
                i_cut_html = i_cut_html.replace(i_c, "")

            i_colors = {'long': "#078F12",
                        'short': "#ff3333",
                        'stop': "#ff9100",
                        'normal': "#333333"}
            i_web_color = i_colors[color]

            if indent:
                i_ind = "│  "
            else:
                i_ind = ""
            i_log_text = "<html><head/><body>" + i_cut_html
            if line:
                i_log_text = i_log_text \
                             + "<font color='#000000'>" \
                             + "─" * 65 \
                             + "</font>" \
                             + "<br>"

            lines = add_text.splitlines()

            for one_line in lines:
                i_log_text = i_log_text \
                             + "<font color='#000000'>" \
                             + time.strftime("%m-%d %H:%M:%S") + " > " \
                             + i_ind \
                             + "</font>" \
                             + "<font color='" + i_web_color + "'>" \
                             + one_line \
                             + "</font>" \
                             + "<br>"
            i_log_text = i_log_text + "</body></html>"
            self.Logs_Trade.setText(i_log_text)
            i_vbar = self.LT_scrollArea.verticalScrollBar()
            i_vbar.setValue(i_vbar.maximum())
            QApplication.processEvents()

        # GUI - Tools ---------------------------------------------

        def confirm(self, title, message):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("\n\t\t" + message + "\t\t\t\t\n")
            # msg.setInformativeText("This is additional information")
            msg.setWindowTitle(title)
            # msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            bttn = msg.exec_()
            if bttn == QMessageBox.Yes:
                i_return = True
            else:
                i_return = False
            return i_return


class n_date_frame2:
    def __init__(self):
        self.indicators = pd.DataFrame(None)
        self.load_indicators()

    def get_dataset_config(self, file_name):
        log("ndf-> get_dataset_config " + file_name + ".txt")

        # ez nem vizsgálja, hogy létezik e file, ezt hívás előtt kell

        def clear_string(contents, space=True):
            if space:
                contents = contents.replace(" ", "")
            contents = contents.replace('\n', '').replace('\r', '')
            contents = re.sub('<.*?>', '', contents)
            return contents

        with open(file_name + '.txt') as f:
            contents = f.read()
        contents = contents.split(";")
        description = clear_string(contents[0], space=False)
        dataset_config = json.loads(clear_string(contents[1]))
        original_fields = json.loads(clear_string(contents[2]))
        try:
            contras = json.loads(clear_string(contents[3]))
        except:
            contras = []
        return description, dataset_config, original_fields, contras

    def get_all_symbol(self):
        return nddf.keys()

    def get_allrow_count(self):
        i_count = 0
        for smb in nddf:
            i_count += nddf[smb].shape[0]
        return i_count

    def case_set_back(self, symbol):
        # a pandas ta elállítgatja a neveket, ezért minden
        # hívás után szépen vissza állítom a neveket :)
        nddf[symbol] = nddf[symbol].rename(columns={"open": "Open",
                                                    "close": "Close",
                                                    "low": "Low",
                                                    "high": "High",
                                                    "volume": "Volume",
                                                    "date": "Date"
                                                    }, errors='ignore')

    def set_dt_order(self, symbol):
        ''' rendezi időben az index oszlopot újra íraja kiszűri a duplikációt'''
        self.case_set_back(symbol)
        nddf[symbol] = self.i_df_dt_order(nddf[symbol])
        if not self.is_datetime_ordered(symbol):
            log("nddf->set_dt_order : Datetime order ERROR", False, True, "red")

    # if not sum(tuple(nddf[symbol].isnull().sum())) == 0:
    #     log("nddf->set_dt_order : isnull() ERROR", False, True, "red")
    # if not sum(tuple(nddf[symbol].isna().sum())) == 0:
    #     log("nddf->set_dt_order : isna() ERROR", False, True, "red")

    def i_df_dt_order(self, df):
        if not str(df.index.name) == "None":
            df.reset_index(drop=False, inplace=True)
        df.drop_duplicates('Date', keep='last', inplace=True)
        df.sort_values(by=['Date'], inplace=True, ascending=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def is_datetime_ordered(self, symbol):
        i_df = nddf[symbol].copy()
        i_df = i_df.set_index("Date")
        return i_df.index[0] < i_df.index[-1]

    def add(self, symbol, years=3):
        years = int(years)
        i_results_md = [None] * 300
        i_rcu = 0

        def threat_function(symbol, i_fromunix, i_tounix, i_paralel_req):
            nonlocal i_results_md, i_rcu
            # i_rcu += 1
            # i_sleep_time = int(i_rcu / 1)
            # # print("i_rcu", i_rcu, i_sleep_time)
            # time.sleep(i_sleep_time*.5)
            # # print(time.gmtime().tm_sec)
            i_results_md[i_paralel_req] = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True, True)

        ''' új nddf et hoz létre letölti a részvény árakat'''

        i_now = datetime.now() + timedelta(days=1)
        i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
        i_datetime_series = pd.date_range(start=i_now, periods=(years * 12) + years + 1, freq='-28d')

        log("ndf-> add (paralell requests): " + symbol + " - " + str(
            i_datetime_series[len(i_datetime_series) - 1]) + " - " + str(i_datetime_series[0]))

        i_paralel_req = 0
        threads = list()
        for i_i in range(len(i_datetime_series) - 1):
            i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=1)))
            i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i + 1] - timedelta(days=1)))
            # i_res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True)
            x = threading.Thread(target=threat_function, args=(symbol, i_fromunix, i_tounix, i_paralel_req))
            threads.append(x)
            i_paralel_req += 1

        for i_t, th in enumerate(threads):
            th.start()

        for th in threads:
            th.join()

        nddf[symbol] = pd.DataFrame(None)
        for xi, irm in enumerate(i_results_md):
            if irm is not None:
                nddf[symbol] = nddf[symbol].append(irm, ignore_index=True)
            # print(irm)

        self.set_dt_order(symbol)

        if nddf[symbol].shape[0] > 0:
            self.set_dt_order(symbol)
            log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        log("Number of rows: " + str(nddf[symbol].shape[0]))
        nddb.write(symbol)

    # def add(self, symbol):
    #     ''' új nddf et hoz létre letölti a részvény árakat'''
    #     log("ndf-> add " + symbol)
    #     i_now = datetime.now() + timedelta(days=1)
    #     i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
    #     i_datetime_series = pd.date_range(start=i_now, periods=1017, freq='-30d')
    #     nddf[symbol] = pd.DataFrame(None)
    #     for i_i in range(len(i_datetime_series)-1):
    #         i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=4)))
    #         i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
    #         i_res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True)
    #         nddf[symbol] = nddf[symbol].append(i_res, ignore_index=True)
    #     if nddf[symbol].shape[0] > 0:
    #         self.set_dt_order(symbol)
    #         log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
    #
    #     log("Number of rows: " + str(nddf[symbol].shape[0]))
    #     nddb.write(symbol)

    def load_indicators(self):
        i_i = [
            ['SMA30', ['SMA_30']],
            ['SMA60', ['SMA_60']],
            ['SMA90', ['SMA_90']],
            ['SMA5813', ['SMA_5', 'SMA_8', 'SMA_13',
                         'SIG_SMA5813_LONG_ALL', 'SIG_SMA5813_SHORT_ALL',
                         'SIG_SMA5813_LONG_FIRST', 'SIG_SMA5813_SHORT_ALL_FIRST',
                         'SIG_QFY_SMA5813_LONG', 'SIG_QFY_SMA5813_ALL_SHORT']],
            ['PRICE_DIFF', ['LOW_DIFF', 'HIGH_DIFF',
                            'OPEN_DIFF', 'CLOSE_DIFF',
                            'OHLC4_DIFF']],
            ['RSI14', ['RSI_14']],
            ['MACD', ['MACD_12_2', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9']],
            ['BREAKOUT', ['SIG_QFY_BREAKOUT_LONG', 'SIG_QFY_BREAKOUT_SHORT',
                          'SIG_BREAKOUT_LONG_ALL', 'SIG_BREAKOUT_SHORT_ALL']],
            ['ADX8', ['ADX_8', 'DMP_8', 'DMN_8', 'ADX_8_ONE']],
            ['ICHIMOKU', ['ISA_9', 'ISB_26', 'ITS_9', 'IKS_26', 'ICS_26',
                          'SIG_ICHI_LONG_ALL', 'SIG_ICHI_LONG_FIRST',
                          'SIG_ICHI_SHORT_ALL', 'SIG_ICHI_SHORT_FIRST',
                          'SIG_QFY_ICHI_LONG', 'SIG_QFY_ICHI_SHORT']]
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
        return (tuple(i_detectd_indicators.keys()))

    def is_contra(self, contra):
        contra_sep_pre = contra.split('_')
        contra_sep = []
        if len(contra_sep_pre) > 2:
            contra_sep.append(contra_sep_pre[0])
            s = "_"
            contra_sep.append(s.join(contra_sep_pre[1:]))
        else:
            contra_sep = contra_sep_pre

        i_return = False
        if contra_sep[0] in nddf:
            if contra_sep[1] in nddf[contra_sep[0]].columns:
                i_return = True
            else:
                log("Field is missing:" + str(contra_sep[0]) + " - " + str(contra_sep[1]))
        return i_return

    def is_field_exist(self, symbol, field):
        if symbol in nddf:
            if field in nddf[symbol].columns:
                i_return = True
            else:
                log("Field is missing:" + str(symbol) + " - " + str(field))
                i_return = False
        else:
            i_return = False
        return i_return

    def is_indicator(self, tech_indicator):
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if len(i_search) > 0:
            i_found = True
        else:
            i_found = False
        return i_found

    def tech_remove(self, symbol, tech_indicator):
        log("ndf-> remove_tech " + symbol + " - " + str(tech_indicator))
        i_search = self.indicators.loc[self.indicators['indicator'] == tech_indicator]
        if self.is_indicator(tech_indicator):
            i_fields = eval(str(i_search["fields"].iloc[0]))
            for i_drop_c in i_fields:
                if i_drop_c in nddf[symbol].columns:
                    nddf[symbol].drop(i_drop_c, axis=1, inplace=True, errors='ignore')
            nddb.write(symbol)
        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

    def check_indicators(self, symbol, needed_indicators):
        i_return = True
        i_indicators = self.get_added_indicators(symbol)
        for i_ni in needed_indicators:
            if i_ni not in i_indicators:
                log('Missing indicator: ' + i_ni)
                i_return = False
        return i_return

    def create_dataset(self, symbol, config_file):

        config_file_path = "dataset_configs/" + config_file
        file = pathlib.Path(config_file_path + ".txt")
        if file.exists():

            description, dataset_config, original_fields, contras = ndf.get_dataset_config(config_file_path)
            field_ok_basic1 = ndf.is_field_exist(symbol, dataset_config['good_long_field'])
            field_ok_basic2 = ndf.is_field_exist(symbol, dataset_config['good_short_field'])
            field_ok_basic3 = ndf.is_field_exist(symbol, dataset_config['bad_long_field'])
            field_ok_basic4 = ndf.is_field_exist(symbol, dataset_config['bad_short_field'])
            field_ok_basic = field_ok_basic1 and field_ok_basic2 and field_ok_basic3 and field_ok_basic4

            field_ok_original_fields = True
            for o_f in original_fields:
                field_ok_original_fields = field_ok_original_fields and ndf.is_field_exist(symbol, o_f)

            field_ok_contras = True
            for c in contras:
                field_ok_contras = field_ok_contras and ndf.is_contra(c)

            if field_ok_basic and field_ok_original_fields and field_ok_contras:
                time_frame_size = dataset_config[
                    "time_frame_size"]  # a indikátortól visszafelé hány percet tegyen az image-ba

                # image fej megcsinálása, minden image nél ugyan az
                # n_dataset = ""
                nd_dset = n_dataset(log)
                nd_dset.set_symbol(symbol)

                nd_dset.set_source("nDot.py->n_data_frame2->create_dataset")
                nd_dset.set_name("nDot_DATASET_" + config_file)

                def array_diff(from_array, this_array):  # from arrayból eltávolitja a this_arrayt
                    for i_nx in this_array:
                        if i_nx in from_array:
                            from_array.remove(i_nx)
                    return from_array

                def array_random_select(from_array, no):
                    no = min(no, len(from_array))
                    return random.choices(from_array, k=no)

                def images_constructor(symbol, indexes, time_frame_size, q):

                    for i_il in indexes:
                        i_int_to = int(i_il)
                        i_int_from = i_int_to - time_frame_size + 1

                        if i_int_from > 0:
                            i_data_array = np.array([])
                            if len(original_fields) > 0:
                                for i_of in original_fields:
                                    i_add = np.array(nddf[symbol].loc[i_int_from:i_int_to, i_of])
                                    i_data_array = np.append(i_data_array, i_add)

                            if len(contras) > 0:
                                for i_con in contras:
                                    contra_sep_pre = i_con.split('_')
                                    con_sep = []
                                    if len(contra_sep_pre) > 2:
                                        con_sep.append(contra_sep_pre[0])
                                        s = "_"
                                        con_sep.append(s.join(contra_sep_pre[1:]))
                                    else:
                                        con_sep = contra_sep_pre

                                    con_symbol = con_sep[0]
                                    con_field = con_sep[1]
                                    i_new = np.array(nddf[con_symbol].loc[i_int_from:i_int_to, con_field])
                                    i_data_array = np.append(i_data_array, i_new)
                            nd_dset.add_X(i_data_array)
                            nd_dset.add_y(q)
                            nd_dset.set_window_size(time_frame_size)

                nd_dset.set_description(description)

                y_names = {'0': "Good LONG signal",
                           '1': "Good SHORT signal",
                           '2': "Bad LONG signal",
                           '3': "Bad SHORT signal"
                           }

                nd_dset.add_y_names(y_names)
                #  beteszem a 'good' signálokat -----------------------------------------
                i_index_good_long = (tuple(nddf[symbol].loc[nddf[symbol][dataset_config['good_long_field']]].index))
                i_index_good_short = (tuple(nddf[symbol].loc[nddf[symbol][dataset_config['good_short_field']]].index))

                max_signals = min(len(i_index_good_long), len(i_index_good_short))
                i_index_good_long = i_index_good_long[0:max_signals]
                i_index_good_short = i_index_good_short[0:max_signals]

                images_constructor(symbol, i_index_good_long, time_frame_size, 0)
                images_constructor(symbol, i_index_good_short, time_frame_size, 1)

                max_signals = int(max_signals * dataset_config['bad_over_weight'])  # szorzó

                #  beteszem a 'bad' signálokat -----------------------------------------
                i_index_bad_long = (tuple(nddf[symbol].loc[nddf[symbol][dataset_config['bad_long_field']]].index))
                i_index_bad_short = (tuple(nddf[symbol].loc[nddf[symbol][dataset_config['bad_short_field']]].index))

                i_index_bad_long = i_index_bad_long[0:max_signals]
                i_index_bad_short = i_index_bad_short[0:max_signals]

                print(max_signals)

                images_constructor(symbol, i_index_bad_long, time_frame_size, 2)
                images_constructor(symbol, i_index_bad_short, time_frame_size, 3)

                # #  beteszem a 'bad' Longokat -----------------------------------------
                # average_element_no = int((len(i_index_long) + len(i_index_short)) / 2)
                # i_index_long_first_m = (list(nddf[symbol].loc[nddf[symbol][dataset_config['bad_long_field']]].index))
                # i_index_long_first_m = array_diff(i_index_long_first_m, i_index_long)  # kiveszem a qualified elemeket
                # #
                # i_index_long_first_m = array_random_select(i_index_long_first_m,
                #                                            int(average_element_no * bad_over_weight))
                # images_constructor(symbol, i_index_long_first_m, time_frame_size, 2)
                #
                # #  beteszem a 'bad' Shortokat -----------------------------------------
                # i_index_short_first_m = (list(nddf[symbol].loc[nddf[symbol][dataset_config['bad_short_field']]].index))
                # i_index_short_first_m = array_diff(i_index_short_first_m,
                #                                    i_index_short)  # kiveszem a qualified elemeket
                # i_index_short_first_m = array_random_select(i_index_short_first_m,
                #                                             int(average_element_no * bad_over_weight))
                # images_constructor(symbol, i_index_short_first_m, time_frame_size, 3)

                # historic max ---------------------------------

                i_historic_max = np.array([])
                i_historic_min = np.array([])
                if len(original_fields) > 0:
                    for i_of in original_fields:
                        nd_dset.add_field(i_of)
                        i_conc = float(np.nanmax(tuple(nddf[symbol][i_of])))
                        i_conc = np.full(time_frame_size, i_conc)
                        i_historic_max = np.concatenate((i_historic_max, i_conc))

                        i_conc = float(np.nanmin(tuple(nddf[symbol][i_of])))
                        i_conc = np.full(time_frame_size, i_conc)
                        i_historic_min = np.concatenate((i_historic_min, i_conc))

                for i_con in contras:
                    nd_dset.add_field(i_con)
                    contra_sep_pre = i_con.split('_')
                    con_sep = []
                    if len(contra_sep_pre) > 2:
                        con_sep.append(contra_sep_pre[0])
                        s = "_"
                        con_sep.append(s.join(contra_sep_pre[1:]))
                    else:
                        con_sep = contra_sep_pre

                    con_symbol = con_sep[0]
                    con_field = con_sep[1]
                    i_conc = float(np.nanmax(tuple(nddf[con_symbol][con_field])))
                    i_conc = np.full(time_frame_size, i_conc)
                    i_historic_max = np.concatenate((i_historic_max, i_conc))

                    i_conc = float(np.nanmin(tuple(nddf[con_symbol][con_field])))
                    i_conc = np.full(time_frame_size, i_conc)
                    i_historic_min = np.concatenate((i_historic_min, i_conc))

                nd_dset.set_historic_max(i_historic_max)
                nd_dset.set_historic_min(i_historic_min)

                nd_dset.set_meta(ndf_meta.get_all_meta_key(symbol))
                nd_dset.save()
                del nd_dset
            else:
                if not field_ok_basic:
                    log("Config file, basic parameter(s) is missing.")
                if not field_ok_original_fields:
                    log("Config file, Orifinal field(s) is missing.")
                if not field_ok_contras:
                    log("Config file, Contra field(s) is missing.")
        else:
            log("config file is missing:" + str(config_file))

    def get_first_signal(self, symbol, long_field, short_field, long_field_first, short_field_first):
        nddf[symbol][long_field_first] = ~(nddf[symbol][long_field] == nddf[symbol][long_field].shift(1)) & \
                                         nddf[symbol][long_field]
        nddf[symbol][short_field_first] = ~(nddf[symbol][short_field] == nddf[symbol][short_field].shift(1)) & \
                                          nddf[symbol][short_field]
        return long_field_first, short_field_first

    def vector_qualify(self,
                       symbol,
                       long_field, short_field,
                       stock_size,
                       min_profit, min_step_profit,
                       stop,
                       steps, overlay_steps,
                       exit_field_prefix):
        """
        :param symbol:
        :param long_field: Long signals for qfy
        :param short_field: Short signals for qfy
        :param stock_size: invested stock size in USD
        :param min_profit: minimum profit in USD
        :param min_step_profit: protect against outlier, if profit comes too fast
        :param stop: stop loss in USD
        :param steps: maximum steps for profit takeing
        :param overlay_steps: signal overlay, the next qfy signal must be out of overlay_steps
        :param exit_field_prefix: exit is 4  column Good long good short bad long bad short
        :return: no return auto update nddf
        """

        # # save originalfields
        # original_df = pd.DataFrame(None)
        # original_df = nddf[symbol][[long_field, short_field]].copy()

        log(f"ndf->vector_qualify: {stock_size} USD p/s:" +
            f"{min_profit}/{stop} steps:{steps} overlay steps:{overlay_steps}")
        
        s2(True, 15)

        def qfy_bad_cross(symbol, ori_field, envi_fileld, overlay_steps):
            
            s2()    
            
            # nem lehet utána qfy short
            i_remove = []
            for i_dif in range(1, overlay_steps + 2):
                c_name = "SXQF" + str(i_dif)
                i_remove.append(c_name)
                nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif - 1)
            # s(str(i_vs) + "%")
            # i_vs += i_vs_p

            i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
            i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

            nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
            nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
            i_remove.append('SXQFMAX')
            self.remove_columns(symbol, i_remove)

            # nem lehet utána qfy short
            i_remove = []
            for i_dif in range(1, overlay_steps + 2):
                c_name = "SXQF" + str(i_dif)
                i_remove.append(c_name)
                nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(-(i_dif - 1))
            # s(str(i_vs) + "%")
            # i_vs += i_vs_p

            i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
            i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

            nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
            nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
            i_remove.append('SXQFMAX')
            self.remove_columns(symbol, i_remove)

        def qfy_bad_cross_rnd(symbol, ori_field, envi_fileld, overlay_steps):
            
            s2()
            
            nddf[symbol]['XRND'] = np.random.randint(2, size=nddf[symbol].shape[0])
            # nem lehet utána qfy short
            i_remove = []
            for i_dif in range(1, overlay_steps + 2):
                c_name = "SXQF" + str(i_dif)
                i_remove.append(c_name)
                nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif - 1)

            i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
            i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

            nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
            nddf[symbol][ori_field] = (nddf[symbol][ori_field] & \
                                       (nddf[symbol]["SXQFMAX"] == 0)) | \
                                      (nddf[symbol][ori_field] & \
                                       (nddf[symbol]["XRND"] == 0))
            i_remove.append('SXQFMAX')
            self.remove_columns(symbol, i_remove)

            # nem lehet utána qfy short
            i_remove = []
            for i_dif in range(1, overlay_steps + 2):
                c_name = "SXQF" + str(i_dif)
                i_remove.append(c_name)
                nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(-(i_dif - 1))

            i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
            i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

            nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)

            nddf[symbol][ori_field] = (nddf[symbol][ori_field] &
                                       (nddf[symbol]["SXQFMAX"] == 0)) | \
                                      (nddf[symbol][ori_field] &
                                       (nddf[symbol]["XRND"] == 0))

            i_remove.append('SXQFMAX')
            i_remove.append('XRND')
            self.remove_columns(symbol, i_remove)

        def qfy_bad_befo(symbol, ori_field, overlay_steps):
            
            s2()
            
            # nem lehet utána qfy short
            i_remove = []
            for i_dif in range(1, overlay_steps + 1):
                c_name = "SXQF" + str(i_dif)
                i_remove.append(c_name)
                nddf[symbol][c_name] = nddf[symbol][ori_field].shift(i_dif)

            i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
            i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

            nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
            nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
            i_remove.append('SXQFMAX')
            self.remove_columns(symbol, i_remove)
        
        # adott stepen belül kiválasztoma maiximum és a minimum értékeket
        i_remove = []
        for i_dif in range(1, steps + 1):
            c_name = "X" + str(i_dif)
            i_remove.append(c_name)
            nddf[symbol][c_name] = ((nddf[symbol].ohlc4.shift(-i_dif) / nddf[symbol].ohlc4) - 1) * 100

        i_pos_first = nddf[symbol].columns.get_loc("X1")
        i_ser = list(range(i_pos_first, i_pos_first + steps))

        nddf[symbol]["XMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        nddf[symbol]["XMIN"] = nddf[symbol].iloc[:, i_ser].min(axis=1)
        nddf[symbol]["XMAX_USD"] = nddf[symbol]["XMAX"] * stock_size / 100
        nddf[symbol]["XMIN_USD"] = nddf[symbol]["XMIN"] * stock_size / 100

        s2()

        nddf[symbol]["XMAX_POS"] = nddf[symbol].iloc[:, i_ser].idxmax(axis=1)
        nddf[symbol]["XMIN_POS"] = nddf[symbol].iloc[:, i_ser].idxmin(axis=1)

        i_remove.append('XMAX')
        i_remove.append("XMIN")
        self.remove_columns(symbol, i_remove)

        nddf[symbol]["XMAX_POS"] = nddf[symbol]["XMAX_POS"].str.replace('X', '')
        nddf[symbol]["XMAX_POS"] = pd.to_numeric(nddf[symbol]["XMAX_POS"])

        nddf[symbol]["XMIN_POS"] = nddf[symbol]["XMIN_POS"].str.replace('X', '')
        nddf[symbol]["XMIN_POS"] = pd.to_numeric(nddf[symbol]["XMIN_POS"])
        
        s2()

        # Qualify long positons
        qfy_long_field = "SIG_QFY_" + exit_field_prefix + "_GOOD_LONG"
        nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMAX_USD"] > min_profit) & \
                                        (nddf[symbol]["XMAX_POS"] > min_step_profit)

        nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMIN_USD"] < stop
        nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] > nddf[symbol]["XMAX_POS"]
        nddf[symbol][qfy_long_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
                                       ((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
                                        (~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
                                         ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"]))

        nddf[symbol][qfy_long_field] = nddf[symbol][qfy_long_field] & nddf[symbol][long_field]
        
        s2()

        i_remove = []
        for i_dif in range(1, overlay_steps + 1):
            c_name = "LQ" + str(i_dif)
            i_remove.append(c_name)
            nddf[symbol][c_name] = nddf[symbol][qfy_long_field].shift(i_dif)

        s2()

        i_pos_first = nddf[symbol].columns.get_loc("LQ1")
        i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

        nddf[symbol]["LQMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        nddf[symbol][qfy_long_field] = nddf[symbol][qfy_long_field] & (nddf[symbol]["LQMAX"] == 0)

        i_remove.append('LQMAX')
        i_remove.append('MIN_PROFIT_OK')
        i_remove.append('LOSS_OVER_STOP_LIMIT')
        i_remove.append('STOP_POS_AFTER_PROFIT_POS')
        self.remove_columns(symbol, i_remove)

        s2()

        # Qualify SHORT positons
        qfy_short_field = "SIG_QFY_" + exit_field_prefix + "_GOOD_SHORT"
        nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMIN_USD"] < -min_profit) & \
                                        (nddf[symbol]["XMIN_POS"] > min_step_profit)

        nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMAX_USD"] > -stop
        nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] < nddf[symbol]["XMAX_POS"]
        nddf[symbol][qfy_short_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
                                        ((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
                                         (~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
                                          ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"]))

        nddf[symbol][qfy_short_field] = nddf[symbol][qfy_short_field] & nddf[symbol][short_field]
        #
        i_remove = []
        for i_dif in range(1, overlay_steps + 1):
            c_name = "SQ" + str(i_dif)
            i_remove.append(c_name)
            nddf[symbol][c_name] = nddf[symbol][qfy_short_field].shift(i_dif)

        s2()

        i_pos_first = nddf[symbol].columns.get_loc("SQ1")
        i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

        nddf[symbol]["SQMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        nddf[symbol][qfy_short_field] = nddf[symbol][qfy_short_field] & (nddf[symbol]["SQMAX"] == 0)
        i_remove.append('SQMAX')
        self.remove_columns(symbol, i_remove)

        i_remove = ['XMAX_USD', 'XMIN_USD',
                    'XMAX_POS', 'XMIN_POS',
                    'MIN_PROFIT_OK', 'LOSS_OVER_STOP_LIMIT', 'STOP_POS_AFTER_PROFIT_POS']
        self.remove_columns(symbol, i_remove)

        s2()

        long_field_first = "SIG_QFY_" + exit_field_prefix + "_BAD_LONG"
        short_field_first = "SIG_QFY_" + exit_field_prefix + "_BAD_SHORT"
        self.get_first_signal(symbol, long_field, short_field, long_field_first, short_field_first)

        qfy_bad_cross(symbol, long_field_first, qfy_long_field, overlay_steps)
        qfy_bad_cross(symbol, long_field_first, qfy_short_field, overlay_steps)
        qfy_bad_cross(symbol, short_field_first, qfy_long_field, overlay_steps)
        qfy_bad_cross(symbol, short_field_first, qfy_short_field, overlay_steps)

        qfy_bad_befo(symbol, long_field_first, overlay_steps)
        qfy_bad_befo(symbol, short_field_first, overlay_steps)
        qfy_bad_cross_rnd(symbol, long_field_first, short_field_first, overlay_steps)
        qfy_bad_cross(symbol, short_field_first, long_field_first, overlay_steps)

        long_field_first2 = "SIG_" + exit_field_prefix + "_LONG_FIRST"
        short_field_first2 = "SIG_" + exit_field_prefix + "_SHORT_FIRST"
        self.get_first_signal(symbol, long_field, short_field, long_field_first2, short_field_first2)

        s2()

        # ----------------------------------------------------------------------------------
        i_signals = nddf[symbol][qfy_long_field].sum()
        log(f"GOOD LONG result: {i_signals}")
        i_signals = nddf[symbol][qfy_short_field].sum()
        log(f"GOOD SHORT result: {i_signals}")
        i_signals = nddf[symbol][long_field_first].sum()
        log(f"BAD LONG result: {i_signals}")
        i_signals = nddf[symbol][short_field_first].sum()
        log(f"BAD SHORT result: {i_signals}")
        log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        s("")

        # def vector_qualify(self,
        #                    symbol,
        #                    long_field, short_field,
        #                    stock_size,
        #                    min_profit, min_step_profit,
        #                    stop,
        #                    steps, overlay_steps,
        #                    qfy_long_field, qfy_short_field):
        #     """
        #     :param symbol:
        #     :param long_field: Long signals for qfy
        #     :param short_field: Short signals for qfy
        #     :param stock_size: invested stock size in USD
        #     :param min_profit: minimum profit in USD
        #     :param min_step_profit: protect against outlier, if profit comes too fast
        #     :param stop: stop loss in USD
        #     :param steps: maximum steps for profit takeing
        #     :param overlay_steps: signal overlay, the next qfy signal must be out of overlay_steps
        #     :return: no return auto update nddf
        #     :param qfy_long_field: return to qualified long signals
        #     :param qfy_short_field:  return to qualified short positions
        #     """
        #
        #     # save originalfields
        #     original_df = pd.DataFrame(None)
        #     original_df = nddf[symbol][[long_field, short_field]].copy()
        #
        #     log(f"ndf->vector_qualify: {stock_size} USD p/s:" +
        #         f"{min_profit}/{stop} steps:{steps} overlay steps:{overlay_steps}")
        #
        #     # ---------------------------------
        #     def qfy_bad_cross(symbol, ori_field, envi_fileld, overlay_steps):
        #         # nem lehet utána qfy short
        #         i_remove = []
        #         for i_dif in range(1, overlay_steps + 2):
        #             c_name = "SXQF" + str(i_dif)
        #             i_remove.append(c_name)
        #             nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif - 1)
        #         # s(str(i_vs) + "%")
        #         # i_vs += i_vs_p
        #
        #         i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
        #         i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #         nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #         nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
        #         i_remove.append('SXQFMAX')
        #         self.remove_columns(symbol, i_remove)
        #
        #         # nem lehet utána qfy short
        #         i_remove = []
        #         for i_dif in range(1, overlay_steps + 2):
        #             c_name = "SXQF" + str(i_dif)
        #             i_remove.append(c_name)
        #             nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(-(i_dif - 1))
        #         # s(str(i_vs) + "%")
        #         # i_vs += i_vs_p
        #
        #         i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
        #         i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #         nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #         nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
        #         i_remove.append('SXQFMAX')
        #         self.remove_columns(symbol, i_remove)
        #
        #     def qfy_bad_cross_rnd(symbol, ori_field, envi_fileld, overlay_steps):
        #         nddf[symbol]['XRND'] = np.random.randint(2, size=nddf[symbol].shape[0])
        #         # nem lehet utána qfy short
        #         i_remove = []
        #         for i_dif in range(1, overlay_steps + 2):
        #             c_name = "SXQF" + str(i_dif)
        #             i_remove.append(c_name)
        #             nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif - 1)
        #
        #         i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
        #         i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #         nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #         nddf[symbol][ori_field] = (nddf[symbol][ori_field] & \
        #                                    (nddf[symbol]["SXQFMAX"] == 0)) | \
        #                                   (nddf[symbol][ori_field] & \
        #                                    (nddf[symbol]["XRND"] == 0))
        #         i_remove.append('SXQFMAX')
        #         self.remove_columns(symbol, i_remove)
        #
        #         # nem lehet utána qfy short
        #         i_remove = []
        #         for i_dif in range(1, overlay_steps + 2):
        #             c_name = "SXQF" + str(i_dif)
        #             i_remove.append(c_name)
        #             nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(-(i_dif - 1))
        #
        #         i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
        #         i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #         nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #
        #         nddf[symbol][ori_field] = (nddf[symbol][ori_field] &
        #                                    (nddf[symbol]["SXQFMAX"] == 0)) | \
        #                                   (nddf[symbol][ori_field] &
        #                                    (nddf[symbol]["XRND"] == 0))
        #
        #         i_remove.append('SXQFMAX')
        #         i_remove.append('XRND')
        #         self.remove_columns(symbol, i_remove)
        #
        #     def qfy_bad_befo(symbol, ori_field, overlay_steps):
        #         # nem lehet utána qfy short
        #         i_remove = []
        #         for i_dif in range(1, overlay_steps + 1):
        #             c_name = "SXQF" + str(i_dif)
        #             i_remove.append(c_name)
        #             nddf[symbol][c_name] = nddf[symbol][ori_field].shift(i_dif)
        #
        #         i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
        #         i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #         nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #         nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
        #         i_remove.append('SXQFMAX')
        #         self.remove_columns(symbol, i_remove)
        #
        #     i_vs = 1
        #     i_vs_p = 10.8
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #     i_remove = []
        #     for i_dif in range(1, steps + 1):
        #         c_name = "X" + str(i_dif)
        #         i_remove.append(c_name)
        #         nddf[symbol][c_name] = ((nddf[symbol].ohlc4.shift(-i_dif) / nddf[symbol].ohlc4) - 1) * 100
        #
        #     i_pos_first = nddf[symbol].columns.get_loc("X1")
        #     i_ser = list(range(i_pos_first, i_pos_first + steps))
        #
        #     nddf[symbol]["XMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #     nddf[symbol]["XMIN"] = nddf[symbol].iloc[:, i_ser].min(axis=1)
        #     nddf[symbol]["XMAX_USD"] = nddf[symbol]["XMAX"] * stock_size / 100
        #     nddf[symbol]["XMIN_USD"] = nddf[symbol]["XMIN"] * stock_size / 100
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     nddf[symbol]["XMAX_POS"] = nddf[symbol].iloc[:, i_ser].idxmax(axis=1)
        #     nddf[symbol]["XMIN_POS"] = nddf[symbol].iloc[:, i_ser].idxmin(axis=1)
        #
        #     i_remove.append('XMAX')
        #     i_remove.append("XMIN")
        #     self.remove_columns(symbol, i_remove)
        #
        #     nddf[symbol]["XMAX_POS"] = nddf[symbol]["XMAX_POS"].str.replace('X', '')
        #     nddf[symbol]["XMAX_POS"] = pd.to_numeric(nddf[symbol]["XMAX_POS"])
        #
        #     nddf[symbol]["XMIN_POS"] = nddf[symbol]["XMIN_POS"].str.replace('X', '')
        #     nddf[symbol]["XMIN_POS"] = pd.to_numeric(nddf[symbol]["XMIN_POS"])
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     # Qualify long positons
        #     nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMAX_USD"] > min_profit) & \
        #                                     (nddf[symbol]["XMAX_POS"] > min_step_profit)
        #
        #     nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMIN_USD"] < stop
        #     nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] > nddf[symbol]["XMAX_POS"]
        #     nddf[symbol][qfy_long_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
        #                                    ((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
        #                                     (~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
        #                                      ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"]))
        #
        #     nddf[symbol][qfy_long_field] = nddf[symbol][qfy_long_field] & nddf[symbol][long_field]
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     i_remove = []
        #     for i_dif in range(1, overlay_steps + 1):
        #         c_name = "LQ" + str(i_dif)
        #         i_remove.append(c_name)
        #         nddf[symbol][c_name] = nddf[symbol][qfy_long_field].shift(i_dif)
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     i_pos_first = nddf[symbol].columns.get_loc("LQ1")
        #     i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #     nddf[symbol]["LQMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #     nddf[symbol][qfy_long_field] = nddf[symbol][qfy_long_field] & (nddf[symbol]["LQMAX"] == 0)
        #
        #     i_remove.append('LQMAX')
        #     i_remove.append('MIN_PROFIT_OK')
        #     i_remove.append('LOSS_OVER_STOP_LIMIT')
        #     i_remove.append('STOP_POS_AFTER_PROFIT_POS')
        #     self.remove_columns(symbol, i_remove)
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     # Qualify SHORT positons
        #     nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMIN_USD"] < -min_profit) & \
        #                                     (nddf[symbol]["XMIN_POS"] > min_step_profit)
        #
        #     nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMAX_USD"] > -stop
        #     nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] < nddf[symbol]["XMAX_POS"]
        #     nddf[symbol][qfy_short_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
        #                                     ((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
        #                                      (~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
        #                                       ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"]))
        #
        #     nddf[symbol][qfy_short_field] = nddf[symbol][qfy_short_field] & nddf[symbol][short_field]
        #     #
        #     i_remove = []
        #     for i_dif in range(1, overlay_steps + 1):
        #         c_name = "SQ" + str(i_dif)
        #         i_remove.append(c_name)
        #         nddf[symbol][c_name] = nddf[symbol][qfy_short_field].shift(i_dif)
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     i_pos_first = nddf[symbol].columns.get_loc("SQ1")
        #     i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
        #
        #     nddf[symbol]["SQMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
        #     nddf[symbol][qfy_short_field] = nddf[symbol][qfy_short_field] & (nddf[symbol]["SQMAX"] == 0)
        #     i_remove.append('SQMAX')
        #     self.remove_columns(symbol, i_remove)
        #
        #     i_remove = ['XMAX_USD', 'XMIN_USD',
        #                 'XMAX_POS', 'XMIN_POS',
        #                 'MIN_PROFIT_OK', 'LOSS_OVER_STOP_LIMIT', 'STOP_POS_AFTER_PROFIT_POS']
        #     self.remove_columns(symbol, i_remove)
        #
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     long_field_first = long_field + "_FIRST"
        #     short_field_first = short_field + "_FIRST"
        #     self.get_first_signal(symbol, long_field, short_field, long_field_first, short_field_first)
        #
        #     qfy_bad_cross(symbol, long_field_first, qfy_long_field, overlay_steps)
        #     qfy_bad_cross(symbol, long_field_first, qfy_short_field, overlay_steps)
        #     qfy_bad_cross(symbol, short_field_first, qfy_long_field, overlay_steps)
        #     qfy_bad_cross(symbol, short_field_first, qfy_short_field, overlay_steps)
        #
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     qfy_bad_befo(symbol, long_field_first, overlay_steps)
        #     qfy_bad_befo(symbol, short_field_first, overlay_steps)
        #     qfy_bad_cross_rnd(symbol, long_field_first, short_field_first, overlay_steps)
        #     qfy_bad_cross(symbol, short_field_first, long_field_first, overlay_steps)
        #
        #     nddf[symbol][long_field] = original_df[long_field]
        #     nddf[symbol][short_field] = original_df[short_field]
        #
        #     s(str(i_vs) + "%")
        #     i_vs += i_vs_p
        #
        #     # ----------------------------------------------------------------------------------
        #     i_signals = nddf[symbol][qfy_long_field].sum()
        #     log(f"GOOD LONG result: {i_signals}")
        #     i_signals = nddf[symbol][qfy_short_field].sum()
        #     log(f"GOOD SHORT result: {i_signals}")
        #     i_signals = nddf[symbol][long_field_first].sum()
        #     log(f"BAD LONG result: all/good: {i_signals}")
        #     i_signals = nddf[symbol][short_field_first].sum()
        #     log(f"BAD SHORT result: all/good: {i_signals}")
        #     log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        #     s("")

    def add_tech(self, symbol, tech_indicator="SMA60"):

        log("ndf-> add_tech " + symbol + " - " + str(tech_indicator))

        if self.is_indicator(tech_indicator):

            if tech_indicator == "PRICE_DIFF":
                self.case_set_back(symbol)
                nddf[symbol]["LOW_DIFF"] = (nddf[symbol]["Low"] / nddf[symbol]["Low"].shift(1)) - 1
                nddf[symbol]["HIGH_DIFF"] = (nddf[symbol]["High"] / nddf[symbol]["High"].shift(1)) - 1
                nddf[symbol]["OPEN_DIFF"] = (nddf[symbol]["Open"] / nddf[symbol]["Open"].shift(1)) - 1
                nddf[symbol]["CLOSE_DIFF"] = (nddf[symbol]["Close"] / nddf[symbol]["Close"].shift(1)) - 1
                nddf[symbol]["OHLC4_DIFF"] = (nddf[symbol]["ohlc4"] / nddf[symbol]["ohlc4"].shift(1)) - 1
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            if tech_indicator == "SMA30":
                nddf[symbol].ta.sma(length=30, append=True)
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "SMA60":
                nddf[symbol].ta.sma(length=60, append=True)
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "SMA90":
                nddf[symbol].ta.sma(length=90, append=True)
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "MACD":
                nddf[symbol].ta.macd(append=True)
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "SMA5813":
                nddf[symbol].ta.sma(length=5, append=True)
                nddf[symbol].ta.sma(length=8, append=True)
                nddf[symbol].ta.sma(length=13, append=True)

                nddf[symbol]["long_set_tec1"] = nddf[symbol]['SMA_5'] > nddf[symbol]['SMA_8']
                nddf[symbol]["long_set_tec2"] = nddf[symbol]['SMA_8'] > nddf[symbol]['SMA_13']
                nddf[symbol]["SIG_SMA5813_LONG_ALL"] = nddf[symbol]['long_set_tec1'] & nddf[symbol]['long_set_tec2']

                nddf[symbol]["short_set_tec1"] = nddf[symbol]['SMA_5'] < nddf[symbol]['SMA_8']
                nddf[symbol]["short_set_tec2"] = nddf[symbol]['SMA_8'] < nddf[symbol]['SMA_13']
                nddf[symbol]["SIG_SMA5813_SHORT_ALL"] = nddf[symbol]['short_set_tec1'] & nddf[symbol]['short_set_tec2']

                i_remove = ['long_set_tec1', 'long_set_tec2',
                            'short_set_tec1', 'short_set_tec2']
                self.remove_columns(symbol, i_remove)

                self.case_set_back(symbol)
                nddf[symbol].set_index('Date', inplace=True)
                mask = nddf[symbol].between_time('21:30', '16:00').index
                nddf[symbol].loc[mask, 'SIG_SMA5813_LONG_ALL'] = False
                nddf[symbol].loc[mask, 'SIG_SMA5813_SHORT_ALL'] = False

                nddf[symbol]['INDX_SMA5813'] = 0
                nddf[symbol]['INDX_SMA5813'].values[nddf[symbol]['SIG_SMA5813_LONG_ALL']] = 1
                nddf[symbol]['INDX_SMA5813'].values[nddf[symbol]['SIG_SMA5813_SHORT_ALL']] = 2
                nddf[symbol]['INDX_SMA5813_SHIFT'] = nddf[symbol]['INDX_SMA5813'] != nddf[symbol]['INDX_SMA5813'].shift(1)
                nddf[symbol]['IND_SMA5813'] = nddf[symbol]['INDX_SMA5813_SHIFT'] * nddf[symbol]['INDX_SMA5813']

                i_remove = ['INDX_SMA5813', 'INDX_SMA5813_SHIFT', 'SIG_SMA5813_LONG_ALL', 'SIG_SMA5813_SHORT_ALL']
                self.remove_columns(symbol, i_remove)

                self.set_dt_order(symbol)

                ndf.vector_qualify(symbol,
                                   long_field="SIG_SMA5813_LONG_ALL",
                                   short_field="SIG_SMA5813_SHORT_ALL",
                                   stock_size=10000,
                                   min_profit=75,
                                   min_step_profit=5,
                                   stop=-5,
                                   steps=30,
                                   overlay_steps=30,
                                   exit_field_prefix="SMA5813")

                self.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "RSI14":
                nddf[symbol].ta.rsi(append=True)
                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            # elif tech_indicator == "ICHIMOKU":
            #     nddf[symbol].ta.ichimoku(append=True)
            #     self.case_set_back(symbol)
            #
            #     nddf[symbol]["conv_over_base"] = nddf[symbol]["ITS_9"] > nddf[symbol]["IKS_26"]
            #     nddf[symbol]["conv_under_base"] = nddf[symbol]["ITS_9"] < nddf[symbol]["IKS_26"]
            #     nddf[symbol]["cloud_top"] = nddf[symbol][['ISA_9', 'ISB_26']].max(axis=1)
            #     nddf[symbol]["cloud_bottom"] = nddf[symbol][['ISA_9', 'ISB_26']].min(axis=1)
            #     nddf[symbol]["ohlc4_over_cloud"] = nddf[symbol]["ohlc4"] > nddf[symbol]["cloud_top"]
            #     nddf[symbol]["ohlc4_under_cloud"] = nddf[symbol]["ohlc4"] < nddf[symbol]["cloud_bottom"]
            #
            #     # TODO: lagging linét megcsinálni, hogy a 26 percel előbbi állapotot nézze
            #     # nddf[symbol]["lagging_over_cloud"] = nddf[symbol]["ICS_26"] > nddf[symbol]["cloud_top"]
            #     # nddf[symbol]["lagging_under_cloud"] = nddf[symbol]["ICS_26"] < nddf[symbol]["cloud_bottom"]
            #
            #     # LONG SIGNALS -----------------------------------------------------------------
            #     # A szignálokat csak intime ban csinálom meg
            #     nddfx_intime, nddfx_outtime = trade.time_filter(nddf[symbol], "17:30", "21:00")
            #     nddfx_intime["SIG_ICHI_LONG_ALL"] = nddfx_intime["conv_over_base"] \
            #                                         & nddfx_intime["ohlc4_over_cloud"]
            #                                         # & nddf[symbol]["lagging_over_cloud"]
            #     add_to_nddf(symbol, nddfx_intime, 'SIG_ICHI_LONG_ALL')
            #     find_first_signal(symbol, 'SIG_ICHI_LONG_ALL', 'SIG_ICHI_LONG_FIRST', 6)
            #
            #     # SHORT SIGNALS -----------------------------------------------------------------
            #     nddfx_intime["SIG_ICHI_SHORT_ALL"] = nddfx_intime["conv_under_base"] \
            #                                          & nddfx_intime["ohlc4_under_cloud"]
            #                                          # & nddf[symbol]["lagging_under_cloud"]
            #     add_to_nddf(symbol, nddfx_intime, 'SIG_ICHI_SHORT_ALL')
            #     find_first_signal(symbol, 'SIG_ICHI_SHORT_ALL', 'SIG_ICHI_SHORT_FIRST', 6)
            #
            #     ndf_meta.add_meta_key(symbol, "ICHIMOKU_find_first_signal_wait", "6")
            #
            #     i_remove = [
            #         'conv_over_base', 'conv_under_base',
            #         'cloud_top', 'cloud_bottom',
            #         'ohlc4_over_cloud', 'ohlc4_under_cloud',
            #         'lagging_over_cloud', 'lagging_under_cloud'
            #     ]
            #     self.remove_columns(symbol, i_remove)
            #
            #
            #     # Qualifying  -----------------------------------------------------------------
            #
            #     qualify_config = {}
            #     qualify_config['tech_qualify_block_size'] = 10000  # one deal is 10.000 USD
            #     qualify_config['tech_qualify_min_profit'] = 300  # profit on one deal
            #     qualify_config['tech_qualify_stop'] = -50  # stop loss
            #     qualify_config['tech_qualify_max_steps'] = 90
            #
            #     qualify_signal(symbol, 'SIG_ICHI_LONG_FIRST', 'SIG_QFY_ICHI_LONG', 'LONG', qualify_config)
            #     qualify_signal(symbol, 'SIG_ICHI_SHORT_FIRST', 'SIG_QFY_ICHI_SHORT', 'SHORT', qualify_config)
            #
            #     check_signal_overlay(symbol, "SIG_ICHI_LONG_FIRST", overlay_window=45)
            #     check_signal_overlay(symbol, "SIG_ICHI_SHORT_FIRST", overlay_window=45)
            #
            #     check_signal_overlay(symbol, "SIG_QFY_ICHI_LONG", overlay_window=45)
            #     check_signal_overlay(symbol, "SIG_QFY_ICHI_SHORT", overlay_window=45)
            #
            #     ndf.set_dt_order(symbol)
            #     nddb.write(symbol)

            elif tech_indicator == "ADX8":
                nddf[symbol].ta.adx(length=8, append=True)
                nddf[symbol]["adx_inc"] = nddf[symbol]["DMN_8"] < nddf[symbol]["DMP_8"]
                nddf[symbol]["ADX_8_ONE"] = 0

                def set_adx8_one(row):
                    if row["adx_inc"]:
                        return row["ADX_8"]
                    else:
                        return row["ADX_8"] * -1

                nddf[symbol] = nddf[symbol].assign(ADX_8_ONE=nddf[symbol].apply(set_adx8_one, axis=1))
                nddf[symbol] = nddf[symbol].drop(
                    ['adx_inc'
                     ], axis=1, errors='ignore')

                ndf.set_dt_order(symbol)
                nddb.write(symbol)

            elif tech_indicator == "BREAKOUT":
                nddf[symbol]['SIG_BREAKOUT_LONG_ALL'] = (nddf[symbol].ohlc4 < nddf[symbol].ohlc4.shift(1)) & (
                        nddf[symbol].ohlc4 < nddf[symbol].ohlc4.shift(-1))
                nddf[symbol]['SIG_BREAKOUT_SHORT_ALL'] = (nddf[symbol].ohlc4 > nddf[symbol].ohlc4.shift(1)) & (
                        nddf[symbol].ohlc4 > nddf[symbol].ohlc4.shift(-1))

                nddf[symbol].set_index('Date', inplace=True)
                mask = nddf[symbol].between_time('21:30', '16:00').index
                nddf[symbol].loc[mask, 'SIG_BREAKOUT_LONG_ALL'] = False
                nddf[symbol].loc[mask, 'SIG_BREAKOUT_SHORT_ALL'] = False
                ndf.set_dt_order(symbol)
                ndf.vector_qualify(symbol,
                                   long_field="SIG_BREAKOUT_LONG_ALL",
                                   short_field="SIG_BREAKOUT_SHORT_ALL",
                                   stock_size=10000,
                                   min_profit=30,
                                   min_step_profit=5,
                                   stop=-5,
                                   steps=30,
                                   overlay_steps=30,
                                   exit_field_prefix="BREAKOUT"
                                   )

                ndf.set_dt_order(symbol)
                nddb.write(symbol)

        else:
            log(tech_indicator + " - " + "technical indicator does not exist!")
            tech_indictor_tuple = tuple(self.indicators["indicator"])
            tech_indictor_str = ', '.join(tech_indictor_tuple)
            log("Indicators: " + tech_indictor_str)

    def remove(self, symbol):
        log("ndf-> remove " + symbol)
        if symbol in nddf:
            del nddf[symbol]
        i_log = nddb.remove(symbol)
        ndf_meta.remove_meta(symbol)

    def refresh(self, symbol, log_off=False):
        if not log_off:
            log("ndf-> refresh " + symbol)
            log("Time frame (before refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(
                nddf[symbol]["Date"].max()))
            log("Number of rows (before refresh): " + str(nddf[symbol].shape[0]))
        to_dbdt = datetime.now() + timedelta(days=1)
        to_dbdt = to_dbdt.strftime('%Y-%m-%d %H:%M:%S')
        # print("to", to_dbdt)
        from_dbdt = str(nddf[symbol]["Date"].max())
        # print("from", from_dbdt)
        i_tounix = tools.dbdt_to_unixdt(to_dbdt)
        i_fromunix = tools.dbdt_to_unixdt(from_dbdt)
        i_res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True, log_off)

        # fast check tesult
        i_array1 = np.array(i_res["Date"])
        i_array2 = np.array(nddf[symbol]["Date"][-200:])
        if len(i_array1) != sum(np.isin(i_array1, i_array2)):
            nddf[symbol] = nddf[symbol].append(i_res)
            self.set_dt_order(symbol)
            if not log_off:
                log("Time frame (after refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(
                    nddf[symbol]["Date"].max()))
                log("Number of rows (after refresh): " + str(nddf[symbol].shape[0]))
            nddb.write(symbol, log_off)
        else:
            if not log_off:
                log("There is no new data from: " + from_dbdt)

    def remove_columns(self, symbol, columns):
        for i_c in columns:
            if i_c in tuple(nddf[symbol].columns):
                nddf[symbol] = nddf[symbol].drop(i_c, axis=1, errors='ignore')


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

    # def refresh_close(self):
    #     s("wl.refresh.close " + time.strftime("%H:%M:%S"))
    #     for index, row in self.df.iterrows():
    #         i_symbol = row['symbol']
    #         i_quote = md.quote(i_symbol)
    #         self.df.loc[self.df['symbol'] == i_symbol, 'c'] = i_quote['c']
    #         self.df.loc[self.df['symbol'] == i_symbol, 'pc'] = i_quote['pc']
    #     self.write()
    #     return

    def refresh_profile(self):
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_company_profile = md.company_profile(i_symbol)
            if len(i_company_profile.keys()) == 0:
                self.df.loc[self.df['symbol'] == i_symbol, 'name'] = i_symbol
                self.df.loc[self.df['symbol'] == i_symbol, 'profil'] = i_symbol
            else:
                self.df.loc[self.df['symbol'] == i_symbol, 'name'] = i_company_profile['name']
                self.df.loc[self.df['symbol'] == i_symbol, 'profil'] = "Web: " + i_company_profile['weburl']
        self.write()
        return

    def refresh_sentiment(self):
        for index, row in self.df.iterrows():
            i_symbol = row['symbol']
            i_news_sentiment = md.news_sentiment(i_symbol)
            if i_news_sentiment['sentiment']:
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bearish'] = i_news_sentiment['sentiment'][
                    'bearishPercent']
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bullish'] = i_news_sentiment['sentiment'][
                    'bullishPercent']
            else:
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bearish'] = 0
                self.df.loc[self.df['symbol'] == i_symbol, 'snt_bullish'] = 0

        self.write()
        return

    def add(self, symbol, years=3):
        self.remove(symbol)
        new_row = {'symbol': symbol}
        self.df = self.df.append(new_row, ignore_index=True)
        self.refresh_profile()
        # self.refresh_close()
        self.refresh_sentiment()
        self.write()
        gui.refresh_ui()
        ndf.add(symbol, years)
        return

    def remove(self, symbol):
        self.df.drop(self.df.loc[self.df['symbol'] == symbol].index, inplace=True)
        self.write()
        return


# PROGRAMS ----------------------------------------------------------------------------


def help2():
    gui.print_command()


def do(symbol="", p2="", p3=""):
    symbol = "APA"

    print(nddf[symbol])
    nddf[symbol]["T"] = True
    print(nddf[symbol]["T"].sum())
    nddf[symbol]["T"] = nddf[symbol]["T"].shift(2)
    print(nddf[symbol]["T"].sum())


# df = pd.DataFrame(None)
# df = nddf[symbol].copy()
# df = df.set_index("Date")
# print("itt")
# print(df)
# df = df.asfreq('1Min')
# print("itt"*20)
# print(df[1275:1300])
#
# # df = df.fillna(0)
# df = df.interpolate()
# print("itt2")
# print(df[1275:1300])
# print(df.shape)
# df = df.between_time('16:00', '22:00')
# print(df.shape)
# # print(df_slice)
# # print(df_slice.dtypes)
# df = df.reset_index(drop=False)
# print("100")
# print(nddf[symbol].shape)
# nddf[symbol] = df
# print(nddf[symbol].shape)
#
# ndf.set_dt_order(symbol)
# # print(df_slice.head(300))
# # print("1")
# # # Take the diff of the first column (drop 1st row since it's undefined)
# #
# # # print(df_slice['Date'].diff())
# deltas = nddf[symbol]['Date'].diff()[1:]
# # print("2")
# #
# # # Filter diffs (here days > 1, but could be seconds, hours, etc)
# nddf[symbol]['gaps'] = deltas[deltas > timedelta(minutes=1)]
# nddb.write(symbol)
# # print(gaps)
# # print("3")
# #
# # print(gaps.shape)
# # print(max(gaps))
#

# print(df)
# print(df.shape)
# print(df.dtypes)
# print('-'*80)
# df = df.ta.reverse
# print(df)
# print(df.shape)
# df = df.set_index("date")
# print(df)
# print(df.shape)
# df = ndf.i_df_dt_order(df)
# print(df)
# print(df.shape)

# df.ta.time_range = "minutes"
# print(df.ta.time_range)
# print(df.ta.indicators(as_list=True))
#
# # print(nddf["APA"].index[0] < nddf["APA"].index[-1])
# # print(nddf["APA"])
# #
# # # print("1")
# ndf.add("MSFT",1)
# a = np.array(nddf["MSFT"]["Date"].astype(str))
# print("2")
# ndf.add("MSFT",1)
# b = np.array(nddf["MSFT"]["Date"].astype(str))
# print("3 előbb")
# print(np.setdiff1d(a, b))
# print("4 kicsit később")
# print(np.setdiff1d(b, a))

# a_df = pd.DataFrame(None)
# a_df = nddf["APA"][-50:].copy()
# # a_df.set_index("t", inplace=True)
# print(a_df)
# a_df.drop_duplicates('t', keep='last', inplace=True)
# print(a_df)
# a_df.reset_index(drop=True, inplace=True)
# print(a_df)
#
# a_df.sort_values(by=['t'], inplace=True, ascending=False)
# print(a_df)
#
# print(a_df)
# a_df.reset_index(drop=True, inplace=True)
#
# print(a_df)
# a_df.reset_index(drop=True, inplace=True)
# for smb in nddf:
#     nddf[smb] = nddf[smb][0:-3]
#     nddb.write(smb)


def s(msg_str):
    if LogTo == "Gui":
        QApplication.processEvents()
        gui.Status.setText("Status: " + msg_str)
        QApplication.processEvents()


s2_value = 0
s2_max = 0


def s2(null=False, steps=0):
    global s2_value, s2_max
    if LogTo == "Gui":
        QApplication.processEvents()
        if null:
            s2_value = 0
            s2_max = steps
            gui.Status.setText(" ".join(["Status:", str(int(s2_value)), "%"]))
        else:
            gui.Status.setText(" ".join(["Status:", str(int(s2_value / s2_max * 100)), "%"]))
            s2_value += 1
        QApplication.processEvents()


def stream_last_refresh(text):
    gui.Ndf_last_update.setText(text)
    QApplication.processEvents()


def log(add_text, line=False, indent=True, color="normal"):
    if LogTo == "Gui":
        i_vbar = gui.LT_scrollArea_2.verticalScrollBar()
        i_vbar.setValue(i_vbar.maximum())
        QApplication.processEvents()
        i_for_cut = "<html>\n<head/>\n<body>\n<br/>\n<p>\n</p>\n</body>\n</html>"
        i_for_cut = i_for_cut.splitlines()
        i_cut_html = gui.Logs_Browser2.text()
        for i_c in i_for_cut:
            i_cut_html = i_cut_html.replace(i_c, "")

        i_colors = {'blue': "#078F12",
                    'red': "#ff3333",
                    'orange': "#ff9100",
                    'normal': "#333333"}
        i_web_color = i_colors[color]

        if indent:
            i_ind = "│  "
        else:
            i_ind = ""
        i_log_text = "<html><head/><body>" + i_cut_html
        if line:
            i_log_text = i_log_text \
                         + "<font color='#000000'>" \
                         + "─" * 65 \
                         + "</font>" \
                         + "<br>"

        lines = add_text.splitlines()

        for one_line in lines:
            i_log_text = i_log_text \
                         + "<font color='#000000'>" \
                         + time.strftime("%m-%d %H:%M:%S") + " > " \
                         + i_ind \
                         + "</font>" \
                         + "<font color='" + i_web_color + "'>" \
                         + one_line \
                         + "</font>" \
                         + "<br>"
        i_log_text = i_log_text + "</body></html>"
        gui.Logs_Browser2.setText(i_log_text)
        i_vbar = gui.LT_scrollArea_2.verticalScrollBar()
        i_vbar.setValue(i_vbar.maximum())
        QApplication.processEvents()
    elif LogTo == "Screen":
        if line:
            print(time.strftime("%m-%d %H:%M:%S") + " > " + "─" * 80)
        if indent:
            print(time.strftime("%m-%d %H:%M:%S") + " > " + "│  " + str(add_text))
        else:
            print(time.strftime("%m-%d %H:%M:%S") + " > " + str(add_text))


def test():
    log("2/1. This is a test log message.")
    log("2/2. This is a test log message.")
    s("This is a test status message")
    if md.check_finnhub_connection():
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")
    ndf_info()
    process = psutil.Process(os.getpid())
    log("Memory usage: " + str(round(process.memory_percent(), 2)) + " %")
    i_disk_usage = psutil.disk_usage('/')
    log("Disk usage: " + str(i_disk_usage.percent) + " %")


def exit_program():
    gui.close()


# ndf programs  ----------------------------------------------------------------------------


def ndf_add(symbol="", years=3):
    ndf.add(symbol, years)


def ndf_tech(symbol, tech_indicator):
    ndf.add_tech(symbol, tech_indicator)


def ndf_tech_info():
    for symbol in nddf:

        i_indicators = ndf.get_added_indicators(symbol)
        if len(i_indicators) > 0:
            i_str = ', '.join(i_indicators)
            log(symbol + ": " + i_str)
        else:
            log(symbol + ": -")


def ndf_tech_remove(symbol, tech_indicator):
    ndf.tech_remove(symbol, tech_indicator)


def ndf_tech_refresh(symbol):
    i_indicators = ndf.get_added_indicators(symbol)
    # print(i_indicators)
    for i_i in i_indicators:
        ndf.add_tech(symbol, i_i)


def ndf_tech_refresh_all():
    i_symbols = tuple(nddf.keys())
    for i_s in i_symbols:
        log("Refresh indicators in dataframe: " + i_s)
        i_indicators = ndf.get_added_indicators(i_s)
        for i_i in i_indicators:
            ndf.add_tech(i_s, i_i)


# def ndf_images(symbol="", images_for="", contras=""):
#     ndf.create_images(symbol, images_for, contras)


def ndf_dataset(symbol="", config_file=""):
    ndf.create_dataset(symbol, config_file)


def ndf_remove(symbol=""):
    ndf.remove(symbol)


def ndf_refresh(symbol=""):
    ndf.refresh(symbol)


def ndf_refresh_all():
    i_symbols = tuple(nddf.keys())
    for smb in i_symbols:
        ndf.refresh(smb)
        log(" ")


def ndf_info():
    log(nddb.info())
    log("nDot db size: " + str(nddb.get_size()) + " KB")
    i_nddf_size = sys.getsizeof(nddf)
    for key in nddf:
        i_nddf_size += nddf[key].memory_usage(deep=True).sum()
    log("nddf size in memory: " + str(int(i_nddf_size / 1024)) + " KB")


def ndf_columns():
    i_cols = tuple(nddf.keys())
    log("Data Frame columns by symbols:")
    for i_c in i_cols:
        log(i_c)
        log(str(tuple(nddf[i_c].columns)))


def ndf_show_last(symbol="", xminute="60"):
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
                df = nddf[symbol].copy()
                self.table = pt = Table(f, dataframe=df,
                                        showtoolbar=True, showstatusbar=True)
                # self.table = pt = Table(f, dataframe=nddf[symbol].iloc[::-1],
                #                         showtoolbar=True, showstatusbar=True)
                options = {'align': 'w',
                           'cellbackgr': '#F4F4F3',
                           'cellwidth': 70,
                           'colheadercolor': '#535b71',
                           'floatprecision': 6,
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
        del app
    else:
        log("nddf key not exist: " + symbol)


# md programs -------------------------------------------------------------------------------------------------------


def md_check(symbol=""):
    if md.check_finnhub_connection(symbol):
        log("  FinnHub connection is OK.")
    else:
        log("  FinnHub connection ERROR.")


def md_symbols(market):
    market_symbols = pd.DataFrame(md.stock_symbols(market))
    print(market_symbols)


# wl programs -------------------------------------------------------------------------------------------------------


def wl_add(symbol="", years=3):
    wl.add(symbol, years)
    # ndf.check(symbol)
    gui.refresh_ui()


def wl_remove(symbol=""):
    wl.remove(symbol)
    ndf.remove(symbol)
    gui.refresh_ui()


def wl_refresh_profile():
    wl.refresh_profile()
    gui.refresh_ui()


def wl_refresh_sentiment():
    wl.refresh_sentiment()
    gui.refresh_ui()


# PROGRAMS fo wl buttons----------------------------------------------------------------------------


def wl_trade_short(btn_no):
    symbol = wl.df.loc[btn_no - 1]['symbol']
    trade.order['symbol'] = symbol
    trade.order['position'] = "SHORT"
    i_market_price = trade.get_market_price_by_symbol(symbol)
    trade.order['market_price'] = float(i_market_price)
    trade.order['qty'] = int(trade.config["trade_block_size"] / trade.order['market_price'])
    trade.order['stop_trailing'] = False
    gui.set_trade_frame()


def wl_trade_long(btn_no):
    symbol = wl.df.loc[btn_no - 1]['symbol']
    trade.order['symbol'] = symbol
    trade.order['position'] = "LONG"
    i_market_price = trade.get_market_price_by_symbol(symbol)
    trade.order['market_price'] = float(i_market_price)
    trade.order['qty'] = int(trade.config["trade_block_size"] / trade.order['market_price'])
    trade.order['stop_trailing'] = False
    gui.set_trade_frame()


def wl_btn_chart(btn_no):
    symbol = wl.df.loc[btn_no - 1]['symbol']
    log("start: nchart " + symbol, True, False)
    i_indecators = ndf.get_added_indicators(symbol)
    i_df = nddf[symbol].tail(20000).copy()
    nchart.fit(i_df, symbol, i_indecators)
    nchart.show()


def wl_btn_show(btn_no):
    symbol = wl.df.loc[btn_no - 1]['symbol']
    log("start: ndf.show.last " + symbol, True, False)
    ndf_show_last(symbol)
    log("ready.", False, False)


# tr PROGRAMS ----------------------------------------------------------------------------


def tr_set_order():
    if trade.order["position"] == "LONG":
        i_qty = int(trade.order["qty"])
    else:
        i_qty = -1 * int(trade.order["qty"])
    trade.set_tp_position(trade.order["symbol"], i_qty)
    gui.Tr_frame.hide()
    QApplication.processEvents()
    gui.refresh_ui("info")
    trade.broker_run()


def tr_stop(btn_no):
    symbol = wl.df.loc[btn_no - 1]['symbol']
    if gui.confirm("Stop " + symbol, "Are you sure? Stop " + symbol + " position?"):
        trade.order["symbol"] = symbol
        trade.order["position"] = "STOP"
        trade.order["qty"] = 0
        trade.order["stop_trailing"] = False
        trade.set_tp_position(trade.order["symbol"], 0)
        gui.Tr_frame.hide()
        QApplication.processEvents()
        gui.refresh_ui("info")
        trade.broker_run()


def tr_stop_all():
    gui.Tr_frame.hide()
    QApplication.processEvents()
    if gui.confirm("Stop all!", "Are you sure? Stop all position?"):
        gui.tlog(f"Start: STOP ALL!", line=True, indent=False, color="normal")
        i_open_orders = trade.get_all_open_orders()
        i_symbol_dic = {}
        for i_o1 in i_open_orders:
            i_symbol_dic[i_o1.symbol] = 1
        for i_o2 in i_symbol_dic:
            gui.tlog(f"Clear orders: {i_o2}", line=False, indent=True, color="normal")
            trade.cancel_orders_by_symbol(i_o2)

        for i_s in tuple(wl.df["symbol"]):
            trade.set_tp_position(i_s, 0)

        i_pos = trade.get_all_positions()
        for i_s2 in i_pos:
            if i_s2.symbol not in tuple(wl.df["symbol"]):
                trade.set_tp_position(i_s2.symbol, 0)

        gui.refresh_ui("info")
        gui.tlog(f"Ready.", line=False, indent=False, color="normal")
        trade.broker_run()


def tr_portfolio_monitor():
    if gui.Tr_portfolio_monitor.checkState():
        trade.monitor_run()
    else:
        trade.monitor_stop()


def ndf_stream():
    if gui.Ndf_stream.checkState():
        md.stream_run()
    else:
        md.stream_stop()


def tr_info_refresh():
    trade.refresh_tr_info()


if __name__ == "__main__":

    wl = watch_list()
    nddf = {}
    nddb = nd_db(nddf, log)

    if LocalRUN:
        print("Status: GUI Loading...")
        app = QApplication([])
        gui = gui()
        trade = trade(gui=gui)
        nchart = nchart(trade)

    if LocalRUN:
        gui.refresh_ui()
        gui.showMaximized()

    ndf = n_date_frame2()
    ndf_meta = n_date_frame_meta(log)
    tools = tools(gui=gui)
    md = market_data(log, s, tools, ndf, stream_last_refresh)

    if not LocalRUN:
        i_start = datetime.now()
        print("")
        print("nDot job mode.")
        print("_" * 80)
        # ------------------------------------------------------------------------ JOB Strat
        ndf_tech("APA", "SMA30")

        # ------------------------------------------------------------------------ JOB End
        log("Ready.", False, False)
        log("Runtime:" + str(datetime.now() - i_start), False, False)

    if LocalRUN:
        sys.exit(app.exec_())
