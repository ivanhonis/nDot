# This Python file uses the following encoding: utf-8
# GUI -----------------------------------------------
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QScrollArea, QProgressBar, QToolButton, QMessageBox, QFrame
from PyQt5 import QtGui, QtCore, QtWebEngineWidgets, uic
from PyQt5.QtCore import QTime, QDate

# other checked ----------------------------------------------------
import pandas as pd
import os  # for test command
import psutil  # for test command
import pandas_ta as ta  # technical indicators for ndf2.tech
from functools import partial  # a kattintás hozzá rendeléséhez használom
from datetime import datetime, timedelta  # a log ban használom
import sys  # a test parancs használja hdd szabad hely kiíratására
# from multiprocessing import Process
import threading  # refresh info párhuzamosítva van
import numpy as np


# User classes ------------------------------------------------------
from classes.trade import trade
from classes.market_data import market_data
from classes.nd_db import nd_db
from classes.nchart import nchart

import websocket

import time
# import random
# from pandas import DataFrame
# import threading
from tkinter import *
# import tables
# import alpaca_trade_api as tradeapi
# import matplotlib.animation as animation
# import matplotlib.dates as mdates
# from pandasgui.datasets import pokemon, titanic, all_datasets
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QProgressBar, QToolButton
# from PyQt5.QtCore import *
# from datetime import timedelta
# from PyQt5.QtWidgets import*
# from PyQt5 import QtGui
# from PyQt5 import
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib
matplotlib.rcParams["toolbar"] = "toolmanager"
from matplotlib.backend_tools import ToolBase


class gui(QWidget, object):

    def __init__(self):
        super(gui, self).__init__()
        self.load_ui()
        self.usd_huf = 0
        # self.show_dialog_return = False
        self.commands = self.load_commands()
        # első alkalommal amikor megjelenik a trade frame akkor is újra kalkulálni
        self.pause_trader_frame_calculation = True
        # refresh_info párhuzamosítva van hogy ne kelljen várni a frissülésére--
        self.refresh_info_thread = ""
        self.refresh_info_string = ""

        # ablak beállítások ----------------------------------------------------
        self.setWindowTitle("   nDot")
        app_icon = QtGui.QIcon()
        app_icon.addFile('./images/ndot_icon_x2.png', QtCore.QSize(16, 16))
        app.setWindowIcon(app_icon)

# GUI - Over Writes

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            trade.monitor_stop()
            trade.broker_stop()
            print("Status: GUI Closed")
            self.close()
        elif e.key() == QtCore.Qt.Key_F12:
            tr_stop_all()

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
        # self.Command_Line.setText("")

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
                f_id = "fr"+str(i_no+1)
                i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setText(i_symbol)
                i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol"+i_noid[i_no]).setToolTip(row['profil'])
                i_info = self.get_monitor_info_by_symbol(i_symbol)
                i_wl_frame_list[f_id].findChild(QLabel, "WL_info"+i_noid[i_no]).setText(i_info)
                i_pl = self.get_pl_by_symbol(i_symbol)
                i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).setText(i_pl)
                i_wl_frame_list[f_id].findChild(QProgressBar, "WL_bear"+i_noid[i_no]).setValue(int(row['snt_bearish']*100))
                i_wl_frame_list[f_id].show()
                i_no = i_no + 1
        elif mode == "info":
            i_wl_frame_list = get_frame_objects_list("fr", "WL_frame")
            i_no = 0
            for index, row in wl.df.iterrows():
                i_symbol = row['symbol']
                f_id = "fr"+str(i_no+1)

                # akkor frissítek ha volt változás
                i_info = self.get_monitor_info_by_symbol(i_symbol)
                i_info_now = i_wl_frame_list[f_id].findChild(QLabel, "WL_info"+i_noid[i_no]).text()
                if i_info != i_info_now:
                    i_wl_frame_list[f_id].findChild(QLabel, "WL_info"+i_noid[i_no]).setText(i_info)
                    QApplication.processEvents()

                # akkor frissítek ha volt változás
                i_pl = self.get_pl_by_symbol(i_symbol)
                i_pl_now = i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).text()
                if i_pl != i_pl_now:
                    if i_symbol in tuple(trade.cp_df.index):
                        if float(trade.cp_df.loc[i_symbol, "unrealized_pl"]) > 0:
                            i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).setStyleSheet(
                            'color: #ffffff; background: #ff9100')
                        else:
                            i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).setStyleSheet(
                            'color: #000000; background: #ff9100')
                    else:
                        i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setStyleSheet(
                            'color: #ffffff; background: #ff9100')
                    i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop"+i_noid[i_no]).setText(i_pl)
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
        i_return = pd.DataFrame(i_return)
        i_return.columns = ['command', 'program', 'hint', 'params']
        i_return.set_index('command')
        return i_return

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
                         + time.strftime("%m-%d %H:%M:%S") + " > "\
                         + i_ind \
                         + "</font>" \
                         + "<font color='" + i_web_color + "'>"\
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


class n_date_frame2():

    def __init__(self):
        self.indicators = pd.DataFrame(None)
        self.load_indicators()
        self.tech_qualify_block_size = 10000  # one deal is 10.000 USD
        self.tech_qualify_min_profit = 250  # profit on one deal

    def set_dt_order(self, symbol, ascending=True):
        nddf[symbol]['Date'] = pd.to_datetime(nddf[symbol]['Date'])
        nddf[symbol].sort_values(by=['Date'], inplace=True, ascending=True)
        # nddf[symbol].sort_index(inplace=True)
        nddf[symbol].drop_duplicates(inplace=True)
        nddf[symbol].set_index('Date')
        nddf[symbol] = nddf[symbol].reset_index(drop=True)

    def add(self, symbol):
        log("ndf2-> add " + symbol)
        i_now = datetime.now() + timedelta(days=1)
        i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
        i_datetime_series = pd.date_range(start=i_now, periods=7, freq='-93d')
        nddf[symbol] = pd.DataFrame()
        for i_i in range(len(i_datetime_series)-1):
            i_tounix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=4)))
            i_fromunix = tools.dbdt_to_unixdt(str(i_datetime_series[i_i+1]))
            nddf[symbol] = nddf[symbol].append(md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True), ignore_index=True)
        self.set_dt_order(symbol)
        log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
        log("Number of rows: " + str(nddf[symbol].shape[0]))

        print(nddf[symbol])
        nddb.write(symbol)

    def load_indicators(self):
        i_i = [
            ['SMA30',   ['SMA_30']],
            ['SMA60',   ['SMA_60']],
            ['SMA90',   ['SMA_90']],
            ['ADX8',    ['ADX_8', 'DMP_8', 'DMN_8']],
            ['ICHIMOKU', ['ISA_9', 'ISB_26', 'ITS_9', 'IKS_26', 'ICS_26',
                          'SIG_ICHI_LONG_ALL', 'SIG_ICHI_LONG_FIRST',
                          'SIG_ICHI_SHORT_ALL', 'SIG_ICHI_SHORT_FIRST']]
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

        def find_first_signal(symbol, col, new_col, n):

            def find_pattern(df):
                i_o = tuple([1.0])
                i_z = tuple([0.0])
                i_pattern = i_z + (i_o * (n-1))
                i_data = tuple(df)
                # print(i_pattern, i_data)
                if i_pattern == i_data:
                    i_return = True
                else:
                    i_return = False
                return i_return

            nddf[symbol][new_col] = nddf[symbol][col] \
                .rolling(window=n, center=False) \
                .apply(lambda x: find_pattern(x)) \
                .astype(bool)

        def gualify_signal(symbol, col, new_col, side):

            def gualify(df):
                i_pattern = tuple([1.0])
                i_data = tuple(df)

                if i_pattern == i_data:
                    print(df.index)
                    start_index = df.index
                    for i_i in range (0,10):



Token próba


                i_return = True
                return i_return

            nddf[symbol][new_col] = nddf[symbol][col] \
                .rolling(window=1, center=False) \
                .apply(lambda x: gualify(x)) \
                .astype(bool)

        def case_set_back(symbol):
            # a pandas ta elállítgatja a neveket, ezért minden
            # hívás után szépen vissza állítom a neveket :)
            nddf[symbol] = nddf[symbol].rename(columns={"open": "Open",
                                                        "close": "Close",
                                                        "low": "Low",
                                                        "high": "High",
                                                        "volume": "Volume",
                                                        "date": "Date"
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
                log("Finding signals...", False, True)
                nddf[symbol]["conv_over_base"] = nddf[symbol]["ITS_9"] > nddf[symbol]["IKS_26"]
                nddf[symbol]["conv_under_base"] = nddf[symbol]["ITS_9"] < nddf[symbol]["IKS_26"]
                nddf[symbol]["cloud_top"] = nddf[symbol][['ISA_9', 'ISB_26']].max(axis=1)
                nddf[symbol]["cloud_bottom"] = nddf[symbol][['ISA_9', 'ISB_26']].min(axis=1)
                nddf[symbol]["ohlc4_over_cloud"] = nddf[symbol]["ohlc4"] > nddf[symbol]["cloud_top"]
                nddf[symbol]["ohlc4_under_cloud"] = nddf[symbol]["ohlc4"] < nddf[symbol]["cloud_bottom"]

                nddf[symbol]["lagging_over_cloud"] = nddf[symbol]["ICS_26"] > nddf[symbol]["cloud_top"]
                nddf[symbol]["lagging_under_cloud"] = nddf[symbol]["ICS_26"] < nddf[symbol]["cloud_bottom"]

                nddf[symbol]["SIG_ICHI_LONG_ALL"] = nddf[symbol]["conv_over_base"] \
                                                    & nddf[symbol]["ohlc4_over_cloud"]

                                                    # & nddf[symbol]["lagging_over_cloud"]
                find_first_signal(symbol, 'SIG_ICHI_LONG_ALL', 'SIG_ICHI_LONG_FIRST', 3)
                nddf[symbol]["SIG_ICHI_SHORT_ALL"] = nddf[symbol]["conv_under_base"] \
                                                     & nddf[symbol]["ohlc4_under_cloud"]
                                                     # & nddf[symbol]["lagging_under_cloud"]
                find_first_signal(symbol, 'SIG_ICHI_SHORT_ALL', 'SIG_ICHI_SHORT_FIRST', 3)

                nddf[symbol] = nddf[symbol].drop(
                    ['conv_over_base',
                     'conv_under_base',
                     'cloud_top',
                     'cloud_bottom',
                     'ohlc4_over_cloud',
                     'ohlc4_under_cloud',
                     'lagging_over_cloud',
                     'lagging_under_cloud',
                    ], axis=1)

                log("Qualifying signals... ", False, True)
                gualify_signal(symbol, 'SIG_ICHI_LONG_FIRST', 'SIG_QFY_ICHI_LONG', 'LONG')

            elif tech_indicator == "ADX8":
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
        # self.refresh_close()
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


# PROGRAMS ----------------------------------------------------------------------------


def help2(p1="", p2="", p3=""):
    gui.print_command()


def do(symbol="", p2="", p3=""):
    print(nddf['MSFT'])
    print(nddf['IBM'])
    print(nddf['APA'])


def s(msg_str):
    gui.Status.setText("Status: " + msg_str)
    QApplication.processEvents()


def log(add_text, line=False, indent=True):

    if indent:
        i_ind = "│  "
    else:
        i_ind = ""

    i_log_text = gui.Logs_Browser.toPlainText()

    if line:
        i_log_text = i_log_text + "─" * 65 + "\r"

    lines = add_text.splitlines()

    for one_line in lines:
        i_log_text = i_log_text + time.strftime("%m-%d %H:%M:%S") + " > " + i_ind + one_line + " \r"
    gui.Logs_Browser.setText(i_log_text)
    gui.Logs_Browser.moveCursor(QtGui.QTextCursor.End)
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
                self.table = pt = Table(f, dataframe=nddf[symbol],
                                        showtoolbar=True, showstatusbar=True)
                # self.table = pt = Table(f, dataframe=nddf[symbol].iloc[::-1],
                #                         showtoolbar=True, showstatusbar=True)
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
    i_market_price = trade.get_market_price_by_symbol(symbol)
    trade.order['market_price'] = float(i_market_price)
    trade.order['qty'] = int(trade.config["trade_block_size"] / trade.order['market_price'])
    trade.order['stop_trailing'] = False
    gui.set_trade_frame()


def wl_trade_long(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    trade.order['symbol'] = symbol
    trade.order['position'] = "LONG"
    i_market_price = trade.get_market_price_by_symbol(symbol)
    trade.order['market_price'] = float(i_market_price)
    trade.order['qty'] = int(trade.config["trade_block_size"] / trade.order['market_price'])
    trade.order['stop_trailing'] = False
    gui.set_trade_frame()


def wl_btn_chart(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: nchart " + symbol, True, False)
    i_indecators = ndf2.get_added_indicators(symbol)
    i_df = nddf[symbol].tail(3000)
    nchart.fit(i_df, symbol, i_indecators)
    nchart.show()


def wl_btn_show(btn_no):
    symbol = wl.df.loc[btn_no-1]['symbol']
    log("start: ndf2.show.last " + symbol, True, False)
    ndf2_show_last(symbol)
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
    symbol = wl.df.loc[btn_no-1]['symbol']
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


def tr_info_refresh(symbol="", p2="", p3=""):
    trade.refresh_tr_info()

# Back_processes -----------------------------------------------------


# class back_processes(object):
#     def __init__(self, interval=60):
#         self.interval = interval
#         self.kill = False
#         self.runnig = False
#         self.start()
#
#     def stop(self):
#         self.kill = True
#         log("bp-> stopped")
#
#     def start(self):
#         if self.runnig:
#             log("bp-> already running...")
#         else:
#             log("bp-> started")
#             self.kill = False
#             thread = threading.Thread(target=self.run, args=())
#             thread.daemon = True
#             self.runnig = True
#             thread.start()
#         return
#
#     def run(self):
#         while True:
#             # More statements comes here
#             # print(datetime.now().__str__() + ' : Start task in the background')
#             wl.refresh_close()
#             gui.refresh_ui()
#             time.sleep(self.interval)
#             if self.kill:
#                 self.runnig = False
#                 break

# Socket ----------------------------------------------------

# from PyQt5 import QtCore
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

    print("Status: Reading nDot data frame")
    nddf = {}
    nddb = nd_db(nddf, log)
    ndf2 = n_date_frame2()

    print("Status: GUI Load")
    app = QApplication([])
    gui = gui()
    trade = trade(gui=gui)
    tools = tools()
    md = market_data(log, s, tools)
    wl = watch_list()
    gui.refresh_ui()
    # gui.showFullScreen()
    gui.showMaximized()

    # ndf = n_date_frame()
    nchart = nchart()


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