# detect is it a local running environment or a cloud running environment
# import random
import gc
# This Python file uses the following encoding: utf-8
# GUI -----------------------------------------------
# from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QScrollArea, QProgressBar, QToolButton, QMessageBox, \
#     QFrame
import statistics

from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QProgressBar, QToolButton, QMessageBox, QFrame
# from PyQt5 import QtGui, QtCore, QtWebEngineWidgets, uic
from PyQt5 import QtGui, QtCore, uic
# from PyQt5.QtCore import QTime, QDate

from tkinter import *  # ez a show table hoz kell.

import psutil  # for test command
from functools import partial  # a kattintás hozzá rendeléséhez használom

# other checked ----------------------------------------------------
import pandas as pd
from xlsxwriter import Workbook
import numpy as np
import os  # for test command
import os.path
import pandas_ta as ta  # technical indicators for ndf.tech
from datetime import datetime, timedelta  # , time as dt_time  # a log ban használom
import time
import sys  # a test parancs használja hdd szabad hely kiíratására
# from multiprocessing import Process
import threading  # info párhuzamosítva van illetve ndf.add
import random  # a gambling módszerhez kell
import pickle
import hashlib
# import pickle as pickle
# import json  # dataset config beolvasóhoz kell
# import re  # dataset config beolvasóhoz kell
import pathlib  # dataset config beolvasóhoz kell

from multiprocessing import shared_memory, Lock, Pool, cpu_count, Process
lock = Lock()

import asyncio

# User nDot ------------------------------------------------------
from n_dot.n_trade import n_trade
from n_dot.n_market_data import n_market_data
from n_dot.n_db import n_db
from n_dot.n_chart import n_chart
from n_dot.n_datasets import n_dataset
from n_dot.n_data_frame_meta import n_date_frame_meta
from n_dot.n_tools import n_tools
from n_dot.n_algo_trade import n_algo_trade
from n_dot.n_ai import n_ai
from n_dot.n_tech_mp import n_tech_mp
from n_dot.n_calibrate_mp import n_calibrate_mp
from n_dot.n_binance_trade import n_binance_trade
from n_dot.n_dataset_constructor_mp import n_dataset_constructor_mp

# # Ai components
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# from tensorflow.keras.models import load_model

# from tqdm import tqdm
# import websocket

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
		ntrade.monitor_stop()
		ntrade.broker_stop()
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

		# self.Run_Button.clicked.connect(self.run_button_action)
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
	# i_now = datetime.now()
	# self.From_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
	# self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
	# self.From_T.setTime(QTime(i_now.hour, i_now.minute))
	# self.To_T.setTime(QTime(i_now.hour, i_now.minute))
	# self.Datetime_mod1.clicked.connect(partial(self.date_modifier, "hours", 6))
	# self.Datetime_mod2.clicked.connect(partial(self.date_modifier, "days", 1))
	# self.Datetime_mod3.clicked.connect(partial(self.date_modifier, "days", 2))
	# self.Datetime_mod4.clicked.connect(partial(self.date_modifier, "days", 4))
	# self.Datetime_mod5.clicked.connect(partial(self.date_modifier, "days", 30))
	# self.Datetime_now.clicked.connect(self.date_now)

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
			for index, row in wl.wl_df.iterrows():
				i_symbol = row['symbol']
				f_id = "fr" + str(i_no + 1)
				i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol" + i_noid[i_no]).setText(i_symbol)
				i_wl_frame_list[f_id].findChild(QLabel, "WL_symbol" + i_noid[i_no]).setToolTip(row['profil'])
				# i_wl_frame_list[f_id].findChild(QProgressBar, "WL_bear" + i_noid[i_no]).setValue(
				# 	int(row['snt_bearish'] * 100))
				# i_info = self.get_monitor_info_by_symbol(i_symbol)
				# i_wl_frame_list[f_id].findChild(QLabel, "WL_info" + i_noid[i_no]).setText(i_info)
				# i_pl = self.get_pl_by_symbol(i_symbol)
				# i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setText(i_pl)

				i_wl_frame_list[f_id].show()
				i_no = i_no + 1
				QApplication.processEvents()
		if mode == "info" or mode == "full":
			i_wl_frame_list = get_frame_objects_list("fr", "WL_frame")
			i_no = 0
			for index, row in wl.wl_df.iterrows():
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
					if i_symbol in tuple(ntrade.cp_df.index):
						if float(ntrade.cp_df.loc[i_symbol, "unrealized_pl"]) > 0:
							i_wl_frame_list[f_id].findChild(QToolButton,
															"WL_trade_stop" + i_noid[i_no]).setStyleSheet(
								'color: #ffffff; background: #ff9100')
						else:
							i_wl_frame_list[f_id].findChild(QToolButton,
															"WL_trade_stop" + i_noid[i_no]).setStyleSheet(
								'color: #000000; background: #ff9100; border-bottom-left-radius: 5px;')
					else:
						i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setStyleSheet(
							'color: #ffffff; background: #ff9100; border-bottom-left-radius: 5px;')
					i_wl_frame_list[f_id].findChild(QToolButton, "WL_trade_stop" + i_noid[i_no]).setText(i_pl)
					QApplication.processEvents()
				i_no = i_no + 1
		if mode == "ai_info" or mode == "full":
			i_wl_frame_list = get_frame_objects_list("fr", "WL_frame")
			i_no = 0
			for index, row in wl.wl_df.iterrows():
				i_symbol = row['symbol']
				f_id = "fr" + str(i_no + 1)

				# akkor frissítek ha volt változás
				i_info = self.get_ai_info_by_symbol(i_symbol)
				i_info_now = i_wl_frame_list[f_id].findChild(QLabel, "WL_ai_info" + i_noid[i_no]).text()
				if i_info != i_info_now:
					i_wl_frame_list[f_id].findChild(QLabel, "WL_ai_info" + i_noid[i_no]).setText(i_info)
					QApplication.processEvents()
				i_no = i_no + 1

	# GUI - Trader Frame ----------------------------------------------------------------------------------------

	def set_trade_frame(self):
		self.pause_trader_frame_calculation = True
		self.Tr_symbol.setText(ntrade.order["symbol"])

		if ntrade.order["position"] == "SHORT":
			self.Tr_position.setStyleSheet('background-color: #ffffff; ' + \
										   'border-bottom-left-radius: 15px;' + \
										   'color: #ff3333;')
			self.Tr_set_order.setText("SET\nSHORT")
		else:
			self.Tr_position.setStyleSheet('background-color: #ffffff; ' + \
										   'border-bottom-left-radius: 15px;' + \
										   'color: #078F12;')
			self.Tr_set_order.setText("SET\nLONG")
		self.Tr_position.setText(ntrade.order["position"])
		self.Tr_market_price.setText(str(ntrade.order["market_price"]))
		# self.Tr_trailing_stop.setValue(True)
		self.Tr_qty.setValue(ntrade.order["qty"])
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
			ntrade.order["qty"] = int(self.Tr_qty.value())
			i_value_usd = round(ntrade.order["qty"] * ntrade.order["market_price"], 2)
			i_value_huf = round(i_value_usd * self.usd_huf, 2)
			i_value_text = '{0:,.2f}'.format(i_value_usd) + " USD\n" + '{0:,.2f}'.format(i_value_huf) + " HUF"
			self.Tr_value.setText(i_value_text)
			QApplication.processEvents()

	# GUI - DateTime Block  -----------------------------------------------------------

	# def date_now(self):
	#     i_now = datetime.now()
	#     self.To_D.setDate(QDate(i_now.year, i_now.month, i_now.day))
	#     self.To_T.setTime(QTime(i_now.hour, i_now.minute))

	# def date_modifier(self, interval_type, interval_num):
	#     i_nowp = datetime.now() - timedelta(**{interval_type: interval_num})
	#     self.From_D.setDate(QDate(i_nowp.year, i_nowp.month, i_nowp.day))
	#     self.From_T.setTime(QTime(i_nowp.hour, i_nowp.minute))

	# GUI - Commands -----------------------------------------------------------

	def load_commands(self):
		i_return = [
			['help', 'help2', 'help - List of all commands!', 0],
			['do', 'do', 'do', 0],
			['do2', 'do2', 'do2', 0],
			['test', 'test', 'test <p1 / optional> <p2 / optional> <p3 / optional>', 0],
			['wl.add', 'wl_add', 'wl.add <symbol> <year(s)>', 0],
			['wl.add.crypto', 'wl_add_crypto', 'wl.add.crypto <symbol> <year(s)>', 0],
			['wl.remove', 'wl_remove', 'wl.remove <symbol> ', 1],
			# ['wl.refresh.close', 'wl_refresh_close', 'wl.refresh.close <> ', 0],
			['wl.refresh.profile', 'wl_refresh_profile', 'wl.refresh.profile', 0],
			['wl.refresh.sentiment', 'wl_refresh_sentiment', 'wl.refresh.sentiment', 0],
			# ['wl.refresh.all', 'wl_refresh_all', 'wl.refresh.all <> ', 0],
			['ndf.add', 'ndf_add', 'ndf.add <symbol> <year(s)>', 1],
			['ndf.add.crypto', 'ndf_add_crypto', 'ndf.add.crypto <symbol> <year(s)>', 1],
			['ndf.tech', 'ndf_tech', 'ndf.tech <symbol> <technical indicator> [params otional]', 2],
			['ndf.tech.backtest', 'ndf_tech_backtest', 'ndf.tech.backtest <symbol> <run_time_window> <sig_field> <<start_position>>', 2],
			['ndf.tech.project', 'ndf_tech_project', 'ndf.tech.project <symbol> <project>', 2],
			['ndf.tech.remove', 'ndf_tech_remove', 'ndf.tech.remove <symbol> <technical indicator>', 2],
			['ndf.tech.refresh', 'ndf_tech_refresh', 'ndf.tech.refresh <symbol>', 1],
			['ndf.tech.refresh.all', 'ndf_tech_refresh_all', 'ndf.tech.refresh.all', 0],
			['ndf.tech.info', 'ndf_tech_info', 'ndf.tech.info', 0],
			['ndf.dataset', 'ndf_dataset', 'ndf.dataset <symbol> <project> <<NOFORCE / FORCE>> <<FULL / VECTOR / RND_CHOICE>>', 1],
			['ndf.dataset.int', 'ndf_dataset_int', 'ndf.dataset.int <symbol> <project>', 1],
			['ndf.dataset.full', 'ndf_dataset_full', 'ndf.dataset.full <symbol> <project>', 1],
			['ndf.remove', 'ndf_remove', 'ndf.remove <symbol>', 1],
			['ndf.remove.column', 'ndf_remove_column', 'ndf.remove.column <symbol> <column_name> <<SAVE>>', 1],
			['ndf.refresh', 'ndf_refresh', 'ndf.refresh <symbol>', 1],
			['ndf.refresh.all', 'ndf_refresh_all', 'ndf.refresh.all', 0],
			['ndf.info', 'ndf_info', 'ndf.info', 0],
			['ndf.columns', 'ndf_columns', 'ndf.columns', 0],
			['ndf.show.last', 'ndf_show_last', 'ndf.show.last <symbol> <numbers / optional>', 1],
			# ['ndf.check', 'ndf_check', 'ndf.check <symbol>', 1],
			['md.check', 'md_check', 'md.check <symbol>', 0],
			['md.symbols', 'md_symbols', 'md.symbols <market>', 0],
			['ai.add', 'ai_add', 'ai.add <symbol> <project>', 1],
			['ai.build', 'ai_build', 'ai.build', 0],
			['ai.remove', 'ai_remove', 'ai.remove <symbol> <project>', 1],
			['ai.download', 'ai_download', 'ai.download <project name> <<rename>>', 0],
			['ai.backtest', 'ai_backtest', 'ai.backtest <symbol> <time_window> <project> <<start position>>', 3],
			['ai.calibrate', 'ai_calibrate', 'ai.calibrate <symbol> <time_window> <project> <<start position>>', 3],
			['ai.confusion', 'ai_confusion', 'ai.confusion <symbol> <project>', 1],
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
				self.command_line_history = self.command_line_history[:250]
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

			args = command_partitioned[1:]

			if i_params >= 1:
				if len(command_partitioned) - 1 >= i_params:
					if len(wl.wl_df.loc[wl.wl_df['symbol'] == command_partitioned[1]]) > 0:
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
		for i_row in tuple(self.commands["command"]):
			log(" - " + str(i_row))

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
											border-top-left-radius: 5px;
											border-top-right-radius: 5px;
											border-bottom-right-radius: 0px;
											border-bottom-left-radius: 0px;
											border-bottom: 1px solid #eeeeee;
											padding-left: 10px;
											border-top: 1px solid #ffffff;
											border-left: 1px solid #888888;
											''')
			self.Command_Hint.setText(message)
			QApplication.processEvents()
		else:
			self.Command_Line.setStyleSheet('''background-color: #ffffff;
											border-top-left-radius: 5px;
											border-top-right-radius: 5px;
											border-bottom-right-radius: 0px;
											border-bottom-left-radius: 0px;
											border-bottom: 1px solid #eeeeee;
											padding-left: 10px;
											border-top: 1px solid #ffffff;
											border-left: 1px solid #888888;
											''')

			self.Command_Hint.setText(message)
			QApplication.processEvents()

	# GUI - Info text creators ------------------------------------------------

	def get_pl_by_symbol(self, symbol):
		if symbol in ntrade.cp_df.index:
			i_p = float(ntrade.cp_df.loc[symbol, "unrealized_pl"])
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
			i_max_key = max(ntrade.request_count.keys())
			return ntrade.request_count[i_max_key]

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

		i_a = ntrade.get_account()
		i_c = ntrade.get_clock()
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
				<td>Monitor: </td><td>{onf(ntrade.monitor_is_working)} - {ntrade.monitor_refresh_rate}</td><td>{nbs(s)}</td><td>Equity:</td><td>{ntofs(i_a.equity)} USD</td><td>{nbs(s)}</td><td>Market:</td><td>{oc(i_c.is_open)}</td>
			</tr>
			<tr>
				<td>Broker:</td><td>{onf(ntrade.broker_is_working)}  - {ntrade.broker_refresh_rate}</td><td>{nbs(s)}</td><td>USD/HUF:</td><td>{self.usd_huf} HUF</td><td>{nbs(s)}</td><td>{i_cst}</td><td>{i_cs}</td>
			</tr>
			<tr>
				<td>Reguests:</td><td>{rq()}/{ntrade.request_count_max}</td><td>{nbs(s)}</td><td>Cash / power:</td><td>{ntofs(i_a.cash)} / {ntofs(i_a.buying_power)} USD</td><td>{nbs(s)}</td><td>Status:</td><td>{bnb(i_a.trading_blocked)} - {i_a.status}</td>
			</tr>
			<tr>
				<td></td><td></td><td>{nbs(s)}</td><td>Block size:</td><td>{int(ntrade.config["trade_block_size"])} USD</td><td>{nbs(s)}</td><td></td><td></td>
			</tr>
		</table>
		</body></html>
		"""
		return i_return

	def get_monitor_info_by_symbol(self, symbol):
		# print("get_monitor_info_by_symbol\n", symbol)
		# print("get_monitor_info_by_symbol\n", trade.tp_df)
		if symbol in ntrade.tp_df.index:
			i_qt = int(ntrade.tp_df.loc[symbol, "target_position"])
		else:
			i_qt = 0
		# print("get_monitor_info_by_symbol\n", trade.cp_df)
		if symbol in ntrade.cp_df.index:
			i_qc = int(ntrade.cp_df.loc[symbol, "qty"])
			i_p = float(ntrade.cp_df.loc[symbol, "current_price"])
			i_v = float(ntrade.cp_df.loc[symbol, "market_value"])
		else:
			i_qc = 0
			i_p = 0
			i_v = 0
		i_return = f"q: {i_qt} / {i_qc}\np: {i_p}$\nv: {i_v}$"
		# print(i_return,"\n\n")
		return i_return

	def get_ai_info_by_symbol(self, symbol):
		ai_projects = ai.get_projects_by_symbol(symbol)
		i_return = f"""<html><head/><body>"""
		for prj in ai_projects:
			i_return = i_return + f"""
		<div style="margin-top: 5px;">{prj}<br/>Silent</div>"""
		i_return = i_return + "</body></html>"
		# # print(i_return,"\n\n")
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
		self.Logs_Ai.setText(i_log_text)
		i_vbar = self.LT_scrollArea.verticalScrollBar()
		i_vbar.setValue(i_vbar.maximum())
		QApplication.processEvents()

	def ailog(self, add_text, line=False, indent=True, color="normal"):
		i_for_cut = "<html>\n<head/>\n<body>\n<br/>\n<p>\n</p>\n</body>\n</html>"
		i_for_cut = i_for_cut.splitlines()
		i_cut_html = self.Logs_Ai.text()
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
		self.Logs_Ai.setText(i_log_text)
		i_vbar = self.LT_scrollArea_3.verticalScrollBar()
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
		self.temp_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\temp\\"
		self.cache_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\backtest_cache\\"

	# def get_dataset_config(self, file_name):
	#     log("ndf-> get_dataset_config " + file_name )
	#     ok = True
	#     # ez nem vizsgálja, hogy létezik e file, ezt hívás előtt kell
	#
	#     def clear_string(contents, space=True):
	#         if space:
	#             contents = contents.replace(" ", "")
	#         contents = contents.replace('\n', '').replace('\r', '')
	#         contents = re.sub('<.*?>', '', contents)
	#         if contents[-2:] == ",]":
	#             contents = contents[:-2] + "]"
	#         return contents
	#
	#     with open(file_name) as f:
	#         contents = f.read()
	#     contents = contents.split(";")
	#     description = clear_string(contents[0], space=False)
	#
	#     try:
	#         dataset_config = json.loads(clear_string(contents[1]))
	#     except ValueError:
	#         dataset_config = []
	#         ok = False
	#
	#     try:
	#         original_fields = json.loads(clear_string(contents[2]))
	#     except ValueError:
	#         original_fields = []
	#         ok = False
	#
	#     try:
	#         contras = json.loads(clear_string(contents[3]))
	#     except ValueError:
	#         contras = []
	#         ok = False
	#
	#     return ok, description, dataset_config, original_fields, contras
	def get_slice_index(self, xlen, parts, slice_no):
		slices = np.array_split(list(np.arange(0, xlen)), parts)
		start = slices[slice_no][0]
		end = slices[slice_no][-1:][0]
		end += 1
		end = min(end, xlen)
		return start, end

	def get_all_symbol(self):
		return nddf.keys()

	def get_allrow_count(self):
		""" az összes nddf symbol összes sorát adja vissza """
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
		""" rendezi időben az index oszlopot újra íraja kiszűri a duplikációt"""
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
		if len(df['Date']) - len(df['Date'].drop_duplicates()) > 0:
			log(f"Duplicates: {len(df['Date']) - len(df['Date'].drop_duplicates())}")
			df.drop_duplicates('Date', keep='last', inplace=True)
		df.sort_values(by=['Date'], inplace=True, ascending=True)
		df.reset_index(drop=True, inplace=True)
		return df

	def is_datetime_ordered(self, symbol):
		i_df = nddf[symbol].copy()
		i_df = i_df.set_index("Date")
		return i_df.index[0] < i_df.index[-1]

	# def add_crypto(self, symbol, years=1):
	# 	years = int(years)
	# 	if symbol in nbt.crypto:
	# 		nddf[symbol] = pd.DataFrame(None)
	# 		i_now = datetime.now() - timedelta(minutes=1001)
	# 		i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
	# 		period = (years * 365 * 24 * 60) / 1000
	# 		i_datetime_series = pd.date_range(start=i_now, periods=period, freq='-1000min')
	# 		s2(True, len(i_datetime_series) - 1)
	# 		for i_i in range(len(i_datetime_series) - 1):
	# 			s2()
	# 			from_dto = i_datetime_series[i_i]
	# 			from_dt = int(datetime.timestamp(from_dto) * 1000)
	# 			to_dto = i_datetime_series[i_i + 1]
	# 			to_dt = int(datetime.timestamp(to_dto) * 1000)
	# 			log(" Get klines from Binance: " + str(from_dto) + " - " + str(to_dto))
	# 			result = nbt.get_klines(symbol=symbol, from_dt=from_dt, to_dt=to_dt).copy()
	# 			# print(result)
	# 			# print('  első', datetime.datetime.fromtimestamp(int(result[0][0]) / 1000))
	# 			# print('  utolsó', datetime.datetime.fromtimestamp(int(result[-1][0]) / 1000))
	# 			# for x, r in enumerate(res):
	# 			#     print(x, 'utolsó', datetime.datetime.fromtimestamp(int(r[0]) / 1000))
	# 			#     time.sleep(0.25)
	# 			# time.sleep(2)
	# 			# print('első', datetime.datetime.fromtimestamp(int(res[0][0]) / 1000))
	#
	# 			# nddf[symbol] = nddf[symbol].append(result, ignore_index=True)
	# 			nddf[symbol] = pd.concat([nddf[symbol], result], ignore_index=True)
	#
	# 		nddf[symbol] = ndf.i_df_dt_order(nddf[symbol])
	# 		self.set_dt_order(symbol)
	#
	# 		if nddf[symbol].shape[0] > 0:
	# 			self.set_dt_order(symbol)
	# 			log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
	# 		log("Number of rows: " + str(nddf[symbol].shape[0]))
	# 		nddb.write(symbol)
	# 	else:
	# 		log("Symbol not found in Binance listed pairs.")

	# def add_crypto_multi(self, symbol, years=1):
	# 	years = int(years)
	# 	if symbol in nbt.crypto:
	# 		nddf[symbol] = pd.DataFrame(None)
	# 		i_now = datetime.now() - timedelta(minutes=1001)
	# 		i_now = i_now.strftime('%Y-%m-%d %H:%M')
	# 		period = (years * 365 * 24 * 60) / 1000
	# 		i_datetime_series = pd.date_range(start=i_now, periods=period, freq='-1000min')
	# 		s2(True, len(i_datetime_series) - 1)
	# 		result = []
	# 		thr = []
	# 		nddf[symbol] = pd.DataFrame(None)
	# 		log("Thread -  Get klines from Binance: " + str(i_now))
	# 		for i_i in range(len(i_datetime_series) - 1):
	# 			s2()
	# 			from_dto = i_datetime_series[i_i]
	# 			from_dt = int(datetime.timestamp(from_dto) * 1000)
	# 			to_dto = i_datetime_series[i_i + 1]
	# 			param = {"symbol": symbol,
	# 					 "from_dt": from_dt,
	# 					 "result":result}
	#
	# 			thr.append(threading.Thread(target=nbt.get_klines_mth, args=(param,)))
	# 			thr[-1].start()
	# 			time.sleep(.09)  # max 1200 request / 1 minute
	# 			max_paralel_thr = 100
	# 			if i_i % max_paralel_thr == 0 and i_i != 0:
	# 				for itr in thr:
	# 					itr.join()
	# 				result.append(nddf[symbol])
	# 				nddf[symbol] = pd.concat(result, ignore_index=True)
	# 				time.sleep(2)
	#
	# 				thr = []
	# 				result = []
	#
	# 				log(str(i_i) + " Thread -  Get klines from Binance: " + str(to_dto))
	#
	# 		for itr in thr:
	# 			itr.join()
	#
	# 		result.append(nddf[symbol])
	# 		nddf[symbol] = pd.concat(result, ignore_index=True)
	#
	# 		nddf[symbol] = ndf.i_df_dt_order(nddf[symbol])
	# 		self.set_dt_order(symbol)
	#
	# 		# meg kell keresni a hibákat
	# 		a = np.array(nddf[symbol]["Date"])
	# 		b = np.roll(a, 1)
	# 		c = a - b
	# 		c = c[1:-1]
	# 		bug_index = np.where(c == np.max(c))[0]
	# 		print(bug_index)
	# 		print(nddf[symbol][bug_index])
	#
	#
	# 		if nddf[symbol].shape[0] > 0:
	# 			log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
	# 		log("Number of rows: " + str(nddf[symbol].shape[0]))
	# 		nddb.write(symbol)
	# 	else:
	# 		log("Symbol not found in Binance listed pairs.")

	def get_date_bug_index(self, symbol):
		a = nddf[symbol]["Date"].to_numpy(dtype=np.int64)
		b = np.roll(a, 1)
		c = a - b
		c = c[1:-1]
		c = c / 60000000000
		bug_index = np.where(c != 1)[0]
		return bug_index

	def add_crypto_multi2(self, symbol, years=1):

		def day_slices(years, slices_size, overlay=3):
			a = np.array(range(0, years * 365, slices_size))
			b = np.roll(a, 1)
			a = a[1:]
			b = b[1:]
			res = []
			for i in range(len(a)):
				res.append([b[i], a[i] + overlay])
			return res


		years = int(years)
		if symbol in nbt.crypto:
			nddf[symbol] = pd.DataFrame(None)
			i_now = datetime.now()
			day_shift_arr = day_slices(years, 30)
			result = []
			thr = []
			nddf[symbol] = pd.DataFrame(None)
			log(f"Thread -  Get klines from Binance. Years: {years}, Num of threads: {len(day_shift_arr)}")
			for dx, ds in enumerate(day_shift_arr):
				from_dt = i_now - timedelta(days=int(ds[1]))

				to_dt = i_now - timedelta(days=int(ds[0]))
				param = {"symbol": symbol,
						 "from_dt": from_dt,
						 "to_dt": to_dt,
						 "result":result}

				thr.append(threading.Thread(target=nbt.get_klines_mth2, args=(param,)))
				thr[-1].start()
				time.sleep(5.5)

			for itr in thr:
				itr.join()

			nddf[symbol] = pd.concat(result, ignore_index=True)

			nddf[symbol] = ndf.i_df_dt_order(nddf[symbol])
			self.set_dt_order(symbol)

			bx = self.get_date_bug_index(symbol)
			print("bug index", bx)
			if len(bx) != 0:
				log(f" Missing time slices. Resample")
				nddf[symbol] = nddf[symbol].set_index("Date")
				nddf[symbol] = nddf[symbol].resample('1min').asfreq()
				nddf[symbol] = ndf.i_df_dt_order(nddf[symbol])
				ndf.set_dt_order(symbol)


			if nddf[symbol].shape[0] > 0:
				log("Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))
			log("Number of rows: " + str(nddf[symbol].shape[0]))
			nddb.write(symbol)
		else:
			log("Symbol not found in Binance listed pairs.")

	def add(self, symbol, years=1):
		years = int(years)
		i_results_md = [None] * 300
		i_rcu = 0

		# def threat_function(symbol, i_fromunix, i_tounix, i_paralel_req):
		# 	nonlocal i_results_md, i_rcu
			# i_rcu += 1
			# i_sleep_time = int(i_rcu / 1)
			# # print("i_rcu", i_rcu, i_sleep_time)
			# time.sleep(i_sleep_time*.5)
			# # print(time.gmtime().tm_sec)
			# res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True, True)
			# print(res)
			# i_results_md[i_paralel_req] = res

		''' új nddf et hoz létre letölti a részvény árakat'''
		i_now = datetime.now() + timedelta(days=1)
		i_now = i_now.strftime('%Y-%m-%d %H:%M:%S')
		i_datetime_series = pd.date_range(start=i_now, periods=(years * 12) + years + 1, freq='-28d')

		log("ndf-> add (paralell requests): " + symbol + " - " + str(
			i_datetime_series[len(i_datetime_series) - 1]) + " - " + str(i_datetime_series[0]))

		# i_paralel_req = 0
		# threads = list()
		nddf[symbol] = pd.DataFrame(None)
		for i_i in range(len(i_datetime_series) - 1):
			i_tounix = n_tools.dbdt_to_unixdt(str(i_datetime_series[i_i] + timedelta(days=1)))
			i_fromunix = n_tools.dbdt_to_unixdt(str(i_datetime_series[i_i + 1] - timedelta(days=1)))
			i_res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True, True)
			nddf[symbol] = pd.concat([nddf[symbol], i_res], ignore_index=True)
			# print(nddf[symbol].shape[0])
			time.sleep(.25)
			# nddf[symbol] = nddf[symbol].append(i_res, ignore_index=True)
			# x = threading.Thread(target=threat_function, args=(symbol, i_fromunix, i_tounix, i_paralel_req))
			# threads.append(x)
			# i_paralel_req += 1

		# for i_t, th in enumerate(threads):
		# 	time.sleep(.5)
		# 	th.start()
		#
		# for th in threads:
		# 	th.join()
		#
		# nddf[symbol] = pd.DataFrame(None)
		# for xi, irm in enumerate(i_results_md):
		# 	if irm is not None:
		# 		nddf[symbol] = nddf[symbol].append(irm, ignore_index=True)
		# # print(irm)

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
			['BBANDS', ['BBANDS']],
			['CCI21', ['CCI_21_0.015']],
			['P10', ['y_P10', 'SIG_P10']],
			['P10INT', ['y_P10INT', 'SIG_P10INT']],
			['GAM', ['y_GAM', 'SIG_GAM']],
			['GAM2', ['y_GAM2', 'SIG_GAM2']],
			['MT', ['MTx']],
			['SMA30', ['SMA_30']],
			['VWAP', ['VWAP_D', 'VWAP_D_R_OHLC4']],
			['SMA60', ['SMA_60']],
			['SMA90', ['SMA_90']],
			['SMA5813', ['SMA_5', 'SMA_8', 'SMA_13', 'SIG_SMA5813',
						 'SMA_5_DIFF', 'SMA_8_DIFF', 'SMA_13_DIFF',
						 'SMA_5_R_OHLC4', 'SMA_8_R_OHLC4', 'SMA_13_R_OHLC4']],

			['MA_X', ['SMA_5', 'SMA_8', 'SMA_13', 'SMA_26', 'SMA_52',
					   'EMA_5', 'EMA_8', 'EMA_13', 'EMA_26', 'EMA_52'
					   'SMA_5_DIFF', 'SMA_8_DIFF', 'SMA_13_DIFF', 'SMA_26_DIFF', 'SMA_52_DIFF',
					   'EMA_5_DIFF', 'EMA_8_DIFF', 'EMA_13_DIFF', 'EMA_26_DIFF', 'EMA_52_DIFF']],

			['PRICE_DIFF', ['LOW_DIFF', 'HIGH_DIFF',
							'OPEN_DIFF', 'CLOSE_DIFF',
							'OHLC4_DIFF', 'VOLUME_DIFF',
							'LOW_R_OHLC4', 'HIGH_R_OHLC4']],
			['RSI14', ['RSI_14']],
			['MACD', ['MACD_12_2', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9']],
			['MACD_LONG', ['MACDh_26_48_12']],
			['BREAKOUT', ['SIG_BREAKOUT']],
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
		return tuple(i_detectd_indicators.keys())

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

	# def sig_to_y(self, symbol, ori_field, new_field, overlay_steps):
	# 	if ori_field in nddf[symbol].columns:
	# 		log("Start overlay manager." + symbol + " " + ori_field + " " + new_field + " " + str(overlay_steps))
	# 		i_remove = []
	# 		nddf[symbol].set_index("Date")
	# 		for i_dif in range(1, overlay_steps + 1):
	# 			c_name = "TEMP_CUY" + str(i_dif)
	# 			i_remove.append(c_name)
	# 			nddf[symbol][c_name] = nddf[symbol][ori_field].shift(i_dif)
	#
	# 		i_pos_first = nddf[symbol].columns.get_loc("TEMP_CUY1")
	# 		i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
	#
	# 		nddf[symbol]["TEMP_CUY_MAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
	# 		self.remove_columns(symbol, i_remove)
	# 		nddf[symbol][new_field] = 9
	# 		nddf[symbol].loc[nddf[symbol]["TEMP_CUY_MAX"] == 0, new_field] = nddf[symbol][ori_field]
	# 		i_remove.append('TEMP_CUY_MAX')
	# 		# eddig minden 1es és 2ből csak az első van a nem hsználható 1és 2 ből 9es lett
	#
	# 		for i_dif in range(1, overlay_steps + 1 + 1):
	# 			c_name = "TEMP_LZ" + str(i_dif)
	# 			i_remove.append(c_name)
	# 			nddf[symbol][c_name] = nddf[symbol][new_field].shift(- i_dif)
	#
	# 		i_pos_first = nddf[symbol].columns.get_loc("TEMP_LZ1")
	# 		i_ser = list(range(i_pos_first, i_pos_first + overlay_steps + 1))
	# 		nddf[symbol]["TEMP_LZ_MAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
	#
	# 		nddf[symbol].loc[((nddf[symbol]["TEMP_LZ_MAX"] > 0) & (nddf[symbol][new_field] == 0)), new_field] = 9
	# 		i_remove.append('TEMP_LZ_MAX')
	# 		i_remove.append('TEMP_CUY_MAX')
	# 		self.remove_columns(symbol, i_remove)
	# 		c1 = np.count_nonzero(nddf[symbol][ori_field] == 0)
	# 		c2 = np.count_nonzero(nddf[symbol][ori_field] == 1)
	# 		c3 = np.count_nonzero(nddf[symbol][ori_field] == 2)
	# 		x1 = np.count_nonzero(nddf[symbol][new_field] == 0)
	# 		x2 = np.count_nonzero(nddf[symbol][new_field] == 1)
	# 		x3 = np.count_nonzero(nddf[symbol][new_field] == 2)
	# 		log("  Before overlay manager: " + ori_field + "  " + str(c1 + c2 + c3))
	# 		log("  After overlay manager: " + new_field + "  " + str(x1 + x2 + x3))
	# 		# ndf.set_dt_order(symbol)
	# 		# nddb.write(symbol)
	# 	else:
	# 		log("create_unique_y -> orig field is missing from ndf: " + ori_field )

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

	def get_contra_copies(self, contras):
		result = {}
		result_dt = {}
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
				# con_field = con_sep[1]

				if con_symbol not in result:
					result[con_symbol] = nddf[con_symbol].copy()
					result[con_symbol].set_index("Date", inplace=True)
					result_dt[con_symbol] = np.array(result[con_symbol].index)
		return result, result_dt

	def get_dataset_by_index(self, symbol, index, time_window_size, original_fields, contras, contra_copies_dt):

		i_int_to = int(index)
		i_int_from = i_int_to - time_window_size + 1
		# print(nddf[symbol]["Date"][i_int_to:i_int_to + 1])
		# sys.exit(0)

		i_data_array = np.array([])
		if i_int_from > 0:
			if len(original_fields) > 0:
				for i_of in original_fields:
					# i_add = np.array(nddf[symbol].loc[i_int_from:i_int_to, i_of])
					# print(i_add)
					i_add = np.array(nddf[symbol][i_of][i_int_from:i_int_to + 1])
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
					# print(con_symbol,con_field)

					# orig_date = nddf[symbol].loc[index, "Date"]
					# print(orig_date)
					orig_date = nddf[symbol]["Date"][index:index+1].values[0]
					# print(orig_date)
					# sys.exit()
					try:
						# i_int_to_contra = contra_copies[con_symbol].index.get_loc(orig_date, method='ffill')
						i_int_to_contra = np.where(contra_copies_dt[con_symbol] == orig_date)[0][0]
						# print(i_int_to_contra, i_int_to_contra2, orig_date)
						# i_int_to_contra2 = contra_copies[con_symbol].get_indexer(orig_date, method='ffill')
						# print(i_int_to_contra, i_int_to_contra2)
						# if i_int_to_contra == i_int_to_contra2:
						# 	print("jó a csere")
						# sys.exit(0)
					except:
						return np.array([])

					i_int_from_contra = i_int_to_contra - time_window_size + 1
					# i_new = np.array(nddf[con_symbol].loc[i_int_from_contra:i_int_to_contra, con_field])
					# print(i_new)
					i_new = np.array(nddf[con_symbol][con_field][i_int_from_contra:i_int_to_contra + 1])
					# print(i_new)
					i_data_array = np.append(i_data_array, i_new)
		# print(i_data_array.shape)
		return i_data_array

	def create_dataset(self, symbol, project_name, force=False, overlay_manager="rnd_choice"):

		def dataset_constructor(symbol, indexes, time_window_size, y, original_fields, contras, back_shift=0):

			array_len = time_window_size * (len(original_fields) + len(contras))

			contra_copies = self.get_contra_copies(contras)
			asked = 0
			recieved = 0
			for nx, i_il in enumerate(indexes):
				asked += 1
				i_data_array = self.get_dataset_by_index(symbol=symbol,
														 index=i_il + back_shift,
														 # :) predict in the present, but trade in the future
														 time_window_size=time_window_size,
														 original_fields=original_fields,
														 contras=contras,
														 contra_copies=contra_copies
														 # contras_indexes=contras_indexes,
														 # contra_n=nx
														 )

				if not np.isnan(i_data_array).any() and array_len == len(i_data_array):
					recieved += 1
					nd_dset.add_X(i_data_array)
					nd_dset.add_y(y)
				s2()
			log("  Get dataset from ndf: (asked, recieved) by y" + str(y) + ": " + str(asked)+" , "+str(recieved))
			del contra_copies

		config_file_path = "projects/" + project_name + "/nDot_PRO_" + project_name + ".txt"
		file = pathlib.Path(config_file_path)
		if file.exists():
			gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_dataset_config(
				config_file_path)
			if gdc_ok:
				sig_field = "SIG_" + dataset_config['sig_suffix']
				field_ok_basic = ndf.is_field_exist(symbol, sig_field)

				if not force:
					field_ok_basic = True # ha force akkor nincs szükség sigre sem

				field_ok_original_fields = True
				for o_f in original_fields:
					field_ok_original_fields = field_ok_original_fields and ndf.is_field_exist(symbol, o_f)

				field_ok_contras = True
				for c in contras:
					field_ok_contras = field_ok_contras and ndf.is_contra(c)

				if field_ok_basic and field_ok_original_fields and field_ok_contras:
					time_window_size = dataset_config["time_window_size"]
					back_shift = dataset_config["data_window_back_shift"]
					y_field = "y_" + dataset_config["sig_suffix"]
					if force:  # ha már van y akkor kitörli és mindenképen megcsinálja
						ndf.remove_columns(symbol, [y_field])
					if y_field in nddf[symbol].columns:
						log(y_field + " already exist.")
					else:
						ndf.vector_qualify(symbol,
										   sig_suffix=dataset_config["sig_suffix"],
										   stock_size=dataset_config["stock_size"],
										   min_profit=dataset_config["min_profit"],
										   min_step_profit=dataset_config["min_step_profit"],
										   stop=dataset_config["stop"],
										   steps=dataset_config["steps"],
										   overlay_steps=dataset_config["overlay_steps"],
										   overlay_manager=overlay_manager,
										   profit_window_shift=dataset_config["profit_window_shift"])

						self.set_dt_order(symbol)
						nddb.write(symbol)

					s2(True, 12)

					log("Creating dataset.")
					# image fej megcsinálása, minden image nél ugyan az
					nd_dset = n_dataset(log)
					nd_dset.set_symbol(symbol)

					s2()

					nd_dset.set_source("nDot.py->n_data_frame2->create_dataset")
					nd_dset.set_name("nDot_DATASET_" + project_name)
					nd_dset.set_project_name(project_name)

					nd_dset.set_description(description)

					y_names = {'0': "Good LONG signal",
							   '1': "Good SHORT signal",
							   '2': "Bad LONG signal",
							   '3': "Bad SHORT signal"
							   }
					nd_dset.add_y_names(y_names)
					#  beteszem a 'good' signálokat -----------------------------------------
					first_cut = 1000
					s2()
					i_index_good_long = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 0].index)
					i_index_good_long = i_index_good_long[(i_index_good_long > time_window_size + first_cut)]
					i_index_good_short = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 1].index)
					i_index_good_short = i_index_good_short[(i_index_good_short > time_window_size + first_cut)]
					s2()
					i_index_bad_long = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 2].index)
					i_index_bad_long = i_index_bad_long[(i_index_bad_long > time_window_size + first_cut)]
					i_index_bad_short = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 3].index)
					i_index_bad_short = i_index_bad_short[(i_index_bad_short > time_window_size + first_cut)]

					# ha egy érték y (0,1,2,3) hinyzik akkor az nem számít bele a minimumna
					min_array = np.array([len(i_index_good_long),
									  len(i_index_good_short),
									  len(i_index_bad_long),
									  len(i_index_bad_short)])
					min_array = np.ma.masked_equal(min_array, 0, copy=False)

					max_signals = min_array.min()
					max_signals = int(max_signals * dataset_config['bad_overweight'])

					i_index_good_long = i_index_good_long[0:max_signals]
					i_index_good_short = i_index_good_short[0:max_signals]
					i_index_bad_long = i_index_bad_long[0:max_signals]
					i_index_bad_short = i_index_bad_short[0:max_signals]

					global s2_max
					s2_max += len(i_index_good_long) + len(i_index_good_short) + len(i_index_bad_long) + len(
						i_index_bad_short)

					nd_dset.set_window_size(time_window_size)
					s2()
					dataset_constructor(symbol=symbol,
										indexes=i_index_good_long,
										time_window_size=time_window_size,
										y=0,
										original_fields=original_fields,
										contras=contras,
										back_shift=back_shift)
					s2()
					dataset_constructor(symbol=symbol,
										indexes=i_index_good_short,
										time_window_size=time_window_size,
										y=1,
										original_fields=original_fields,
										contras=contras,
										back_shift=back_shift)
					s2()
					dataset_constructor(symbol=symbol,
										indexes=i_index_bad_long,
										time_window_size=time_window_size,
										y=2,
										original_fields=original_fields,
										contras=contras,
										back_shift=back_shift)
					s2()
					dataset_constructor(symbol=symbol,
										indexes=i_index_bad_short,
										time_window_size=time_window_size,
										y=3,
										original_fields=original_fields,
										contras=contras,
										back_shift=back_shift)
					s2()
					# historic max and min ---------------------------------

					i_historic_max = np.array([])
					i_historic_min = np.array([])
					if len(original_fields) > 0:
						for i_of in original_fields:
							nd_dset.add_field(i_of)
							i_conc = float(np.nanmax(tuple(nddf[symbol][i_of])))
							i_conc = np.full(time_window_size, i_conc)
							i_historic_max = np.concatenate((i_historic_max, i_conc))

							i_conc = float(np.nanmin(tuple(nddf[symbol][i_of])))
							i_conc = np.full(time_window_size, i_conc)
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
						i_conc = np.full(time_window_size, i_conc)
						i_historic_max = np.concatenate((i_historic_max, i_conc))

						i_conc = float(np.nanmin(tuple(nddf[con_symbol][con_field])))
						i_conc = np.full(time_window_size, i_conc)
						i_historic_min = np.concatenate((i_historic_min, i_conc))
					s2()
					nd_dset.set_historic_max(i_historic_max)
					nd_dset.set_historic_min(i_historic_min)
					s2()
					nd_dset.set_meta(ndf_meta.get_all_meta_key(symbol))
					s2()
					nd_dset.save()
					s2()
					del nd_dset
				else:
					if not field_ok_basic:
						log("Config file, basic parameter(s) is missing.")
					if not field_ok_original_fields:
						log("Config file, Orifinal field(s) is missing.")
					if not field_ok_contras:
						log("Config file, Contra field(s) is missing.")
			else:
				log("config file conversion error. (,) is missing ? :)")

		else:
			log("config file is missing:" + str(config_file_path))


	async def add_x_y(self, symbol, i_il, back_shift, time_window_size, original_fields, contras, contra_copies,
				contra_copies_dt, array_len, nd_dset, y):
		i_data_array = await self.get_dataset_by_index_async(symbol=symbol,
												 index=i_il + back_shift,
												 # :) predict in the present, but trade in the future
												 time_window_size=time_window_size,
												 original_fields=original_fields,
												 contras=contras,
												 contra_copies=contra_copies,
												 contra_copies_dt=contra_copies_dt)

		if not np.isnan(i_data_array).any() and array_len == len(i_data_array):
			nd_dset.add_X(i_data_array)
			# print(y)
			nd_dset.add_y(y)
			s2()

	def roll_time_frame(self, iarray, time_window, data_window_back_shift=0):  # rolling time frame
		a = np.array(iarray)
		s_array = [0] * time_window
		for i in range(time_window):
			nprt = np.roll(a, (time_window - i - 1 + data_window_back_shift))
			# print(nprt)
			s_array[i] = nprt
			for n in range(time_window - i - 1 + data_window_back_shift):
				s_array[i][n] = np.NaN
		# print(stack_array[i])

		return np.vstack(s_array).T

	def create_dataset_full_stack(self, symbol, project_name):
		log(f"ndf-> create_dataset_full_stack: {symbol} {project_name}")
		gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project_name)

		time_window_size = int(dataset_config['time_window_size'])
		back_shift = dataset_config["data_window_back_shift"]
		array_len = time_window_size * (len(original_fields) + len(contras))

		hstack_array = []
		for field in original_fields:
			hstack_array.append(self.roll_time_frame(nddf[symbol][field], time_window_size, back_shift))

		x_full = np.hstack(hstack_array)

		cstr = "".join(contras)
		ostr = "".join(original_fields)
		olen = str(nddf[symbol].shape[0])
		full_cache_name = str(time_window_size) + cstr + ostr + olen
		full_cache_name = hashlib.md5(full_cache_name.encode('utf-8')).hexdigest()
		log(f"Len chk: nddf.len: {nddf[symbol].shape[0]} dataset.len:{x_full.shape[0]}")

		np.save(self.cache_path + symbol + "_DATASET_FULL_CACHE_" + full_cache_name, x_full)
		log(f"Cache dataset saved: {symbol}_DATASET_FULL_CACHE_{full_cache_name}")
		return x_full

	def get_dataset_full_stack(self, symbol, project_name, nan_manager="leave"):
		def get_bug_index(array):
			i_inf = np.where(array == np.inf)[0]
			i_nan = np.where(np.isnan(array))[0]
			return np.unique(np.concatenate([i_inf, i_nan]))

		log(f"ndf-> get_dataset_full_stack: {symbol} {project_name}")
		gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project_name)

		time_window_size = int(dataset_config['time_window_size'])
		array_len = time_window_size * (len(original_fields) + len(contras))

		cstr = "".join(contras)
		ostr = "".join(original_fields)
		olen = str(nddf[symbol].shape[0])
		full_cache_name = str(time_window_size) + cstr + ostr + olen
		full_cache_name = hashlib.md5(full_cache_name.encode('utf-8')).hexdigest()

		cache_path = ndf.cache_path
		f_name = cache_path + symbol + "_DATASET_FULL_CACHE_" + full_cache_name + '.npy'
		if os.path.isfile(f_name):
			log(f"Dataset loaded from full cache.")
			x_array = np.load(f_name)
		else:
			x_array = self.create_dataset_full_stack(symbol, project_name)

		# bug_index = []
		log(f"Detect bugs (Nan, Inf) manager:{nan_manager}")
		bug_index = get_bug_index(x_array)
		if nan_manager == "leave":
			pass
		elif nan_manager == "empty":
			x_array[bug_index] = np.array([0] * array_len)
		elif nan_manager == "drop":
				x_array = np.delete(x_array, bug_index, 0)
		return x_array, bug_index


	def create_dataset_full(self, symbol, project_name):
		log(f"ndf-> create_dataset_full: {symbol} {project_name}")


		gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project_name)

		time_window_size = int(dataset_config['time_window_size'])
		back_shift = dataset_config["data_window_back_shift"]

		i_indexes = np.array(range(time_window_size + 1, nddf[symbol].shape[0]))

		used_cores = cpu_count()
		runing_processes = np.array([None] * used_cores)
		contra_copies, contra_copies_dt = ndf.get_contra_copies(contras)
		for ix in range(used_cores):
			x_from = ndf.get_slice_index(i_indexes.shape[0], used_cores, ix)[0]
			x_to = ndf.get_slice_index(i_indexes.shape[0], used_cores, ix)[1]
			params = {'cores': used_cores,
					  'process': ix,
					  'symbol': symbol,
					  'indexes': i_indexes[x_from:x_to],
					  'time_window_size': time_window_size,
					  'y': 0,
					  'original_fields': original_fields,
					  'contras': contras,
					  'back_shift': back_shift,
					  'contra_copies_dt': contra_copies_dt,
					  'nddf': nddf,
					  'gap_manager': "empty"
					  }

			runing_processes[ix] = Process(target=mp_dataset_constructor, args=(params,))

		log(f"Start multiproess. Full dataset is creating.")
		for x, prc in enumerate(runing_processes):
			prc.start()

		for prc in runing_processes:
			prc.join()

		X_arra = []

		for ic in range(used_cores):
			file_name = self.temp_path + 'DATASET_DATACONSTRUCTOR_X_RESULTS' + str(ic) + '.npy'
			l_array = np.load(file_name)
			X_arra.append(l_array)
		X_full = np.concatenate(X_arra)

		# the first windowsize + 1 is missing !! create it
		array_len = time_window_size * (len(original_fields) + len(contras))
		missing_part_array = np.array([0] * array_len)
		for ii in range(time_window_size):
			missing_part_array = np.vstack((missing_part_array, np.array([0] * array_len)))
		X_full = np.vstack((missing_part_array, X_full))

		cstr = "".join(contras)
		ostr = "".join(original_fields)
		full_cache_name = str(time_window_size) + cstr + ostr
		full_cache_name = hashlib.md5(full_cache_name.encode('utf-8')).hexdigest()
		log(f"Len chk: nddf.len: {nddf[symbol].shape[0]} dataset.len:{X_full.shape[0]}")

		np.save(self.cache_path + "DATASET_FULL_CACHE_" + full_cache_name, X_full)
		log(f"Cache dataset saved: DATASET_FULL_CACHE_{full_cache_name}")

	def create_dataset_int_stack(self, symbol, project_name, full=False):

		config_file_path = "projects/" + project_name + "/nDot_PRO_" + project_name + ".txt"
		file = pathlib.Path(config_file_path)
		if not file.exists():
			log("config file is missing:" + str(config_file_path))
			return

		gdc_ok, descr, dataset_config, orig_fields, contras, indexes = ai.get_dataset_config(config_file_path)
		if not gdc_ok:
			log("config file conversion error. (,) is missing ? :)")
			return

		sig_field = "SIG_" + dataset_config['sig_suffix']
		ok_sig = ndf.is_field_exist(symbol, sig_field)

		y_field = "y_" + dataset_config["sig_suffix"]
		ok_y = ndf.is_field_exist(symbol, y_field)

		ok_orig = True
		for o_f in orig_fields:
			ok_orig = ok_orig and ndf.is_field_exist(symbol, o_f)

		ok_contras = True
		for c in contras:
			ok_contras = ok_contras and ndf.is_contra(c)

		if not ok_sig or not ok_orig or not ok_contras or not ok_y:
			if not ok_sig:
				log("Config file, basic parameter(s) is missing.")
			if not ok_orig:
				log("Config file, Orifinal field(s) is missing.")
			if not ok_contras:
				log("Config file, Contra field(s) is missing.")
			if not ok_y:
				log("Config file, y field(s) is missing.")
			return

		# create dataset ----------------------------------------------------------------

		time_window_size = dataset_config["time_window_size"]

		log("Creating dataset.")
		# image fej megcsinálása, minden image nél ugyan az
		nd_dset = n_dataset(log)
		nd_dset.set_symbol(symbol)

		nd_dset.set_source("nDot.py->n_data_frame2->create_dataset_int")
		nd_dset.set_name("nDot_DATASET_" + project_name)
		nd_dset.set_project_name(project_name)
		nd_dset.set_description(descr)

		y_names = {'0=under limit; 1=good long; 2=good short'}
		nd_dset.add_y_names(y_names)
		nd_dset.set_window_size(time_window_size)
		i_indexes = {}
		X_array_all, bug_index = ndf.get_dataset_full_stack(symbol, project_name, nan_manager="drop")
		log("  Number of deleted dataset with Nan Inf:" + str(len(bug_index)))

		y_sig_all = np.array(nddf[symbol][y_field].values)
		y_sig_all = np.delete(y_sig_all, bug_index, 0)

		log("  Set locked part of the dataset:")
		log("  Orig size:" + str(X_array_all.shape))
		# X_array_all = X_array_all[-400000:]
		# y_sig_all = y_sig_all[-400000:]

		X_array_all = X_array_all[0:-100000]
		y_sig_all = y_sig_all[0:-100000]
		log("  Reduced size:" + str(X_array_all.shape))

		if not full:
			for ix in range(3):
				i_indexes[ix] = np.where(y_sig_all == ix)[0]
			# print(i_indexes[ix].shape)
			# módosítom a nullák számát --------------------------------
			len1 = len(i_indexes[1])
			len2 = len(i_indexes[2])
			max_elemet = max(len1, len2) * int(dataset_config['bad_overweight'])
			# i_indexes[0] = i_indexes[0][0+600000: max_elemet+600000]
			# i_indexes[0] = i_indexes[0][0: max_elemet]
			i_indexes[0] = np.random.choice(i_indexes[0], min(i_indexes[0].shape[0], max_elemet), replace=False)
			s2(True, len1 + len2 + max_elemet)
			for ix in range(3):
				log("  Number of selected y: " + str(ix) + " " + str(len(i_indexes[ix])))

			X_arra = np.concatenate((X_array_all[i_indexes[0]], X_array_all[i_indexes[1]], X_array_all[i_indexes[2]]))
			nd_dset.add_X(X_arra)
			y_arra = np.concatenate((y_sig_all[i_indexes[0]], y_sig_all[i_indexes[1]], y_sig_all[i_indexes[2]]))
			nd_dset.add_y(y_arra)

		else:
			i_indexes_9 = np.where(y_sig_all == 9)[0]
			y_sig_all = np.delete(y_sig_all, i_indexes_9, 0)
			X_array_all = np.delete(X_array_all, i_indexes_9, 0)
			i_indexes_10 = np.where(y_sig_all == 10)[0]
			y_sig_all = np.delete(y_sig_all, i_indexes_10, 0)
			X_array_all = np.delete(X_array_all, i_indexes_10, 0)
			nd_dset.add_X(X_array_all)
			nd_dset.add_y(y_sig_all)

		# historic max and min ---------------------------------

		i_historic_max = np.array([])
		i_historic_min = np.array([])
		if len(orig_fields) > 0:
			for i_of in orig_fields:
				nd_dset.add_field(i_of)
				i_conc = float(np.nanmax(tuple(nddf[symbol][i_of])))
				i_conc = np.full(time_window_size, i_conc)
				i_historic_max = np.concatenate((i_historic_max, i_conc))

				i_conc = float(np.nanmin(tuple(nddf[symbol][i_of])))
				i_conc = np.full(time_window_size, i_conc)
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
			i_conc = np.full(time_window_size, i_conc)
			i_historic_max = np.concatenate((i_historic_max, i_conc))

			i_conc = float(np.nanmin(tuple(nddf[con_symbol][con_field])))
			i_conc = np.full(time_window_size, i_conc)
			i_historic_min = np.concatenate((i_historic_min, i_conc))
		nd_dset.set_historic_max(i_historic_max)
		nd_dset.set_historic_min(i_historic_min)
		nd_dset.set_meta(ndf_meta.get_all_meta_key(symbol))
		nd_dset.save()
		del nd_dset


	# def create_dataset_int(self, symbol, project_name, force=False, overlay_manager="rnd_choice"):
	#
	# 	def get_slice_index(xlen, parts, slice_no):
	# 		slices = np.array_split(list(np.arange(0, xlen)), parts)
	# 		start = slices[slice_no][0]
	# 		end = slices[slice_no][-1:][0]
	# 		end += 1
	# 		end = min(end, xlen)
	# 		return start, end
	#
	# 	# def dataset_constructor(symbol, indexes, time_window_size, y, original_fields, contras, nd_dset, back_shift=0):
	# 	# def dataset_constructor(params):
	# 	# 	print("start")
	# 	# 	task = params['task']
	# 	# 	symbol = params['symbol']
	# 	# 	indexes = params['indexes']
	# 	# 	time_window_size = params['time_window_size']
	# 	# 	y = params['y']
	# 	# 	original_fields = params['original_fields']
	# 	# 	contras = params['contras']
	# 	# 	nd_dset = params['nd_dset']
	# 	# 	back_shift = params['back_shift']
	# 	#
	# 	# 	array_len = time_window_size * (len(original_fields) + len(contras))
	# 	#
	# 	# 	# contra_copies = self.get_contra_copies(contras)
	# 	# 	contra_copies, contra_copies_dt = ndf.get_contra_copies(contras)
	# 	# 	asked = 0
	# 	# 	recieved = 0
	# 	# 	for nx, i_il in enumerate(indexes):
	# 	# 		asked += 1
	# 	#
	# 	# 		i_data_array = self.get_dataset_by_index(symbol=symbol,
	# 	# 												 index=i_il + back_shift,
	# 	# 												 # :) predict in the present, but trade in the future
	# 	# 												 time_window_size=time_window_size,
	# 	# 												 original_fields=original_fields,
	# 	# 												 contras=contras,
	# 	# 												 contra_copies=contra_copies,
	# 	# 												 contra_copies_dt=contra_copies_dt)
	# 	#
	# 	# 		if not np.isnan(i_data_array).any() and array_len == len(i_data_array):
	# 	# 			recieved += 1
	# 	# 			nd_dset.add_X(i_data_array)
	# 	# 			nd_dset.add_y(y)
	# 	#
	# 	# 		# s2()
	# 	# 		if nx % 1000 == 0:
	# 	# 			print("task ->",task, nx)
	# 	# 	log("  Get dataset from ndf: (asked, recieved) by y" + str(y) + ": " + str(asked)+" , "+str(recieved))
	# 	# 	del contra_copies
	#
	# 	i_save = nddf[symbol].copy()
	# 	log("  Set locked part of the ndf:")
	# 	log("  Orig size:" + str(nddf[symbol].shape))
	# 	nddf[symbol] = nddf[symbol][0:-200000].copy()
	# 	log("  New size:" + str(nddf[symbol].shape))
	#
	# 	config_file_path = "projects/" + project_name + "/nDot_PRO_" + project_name + ".txt"
	# 	file = pathlib.Path(config_file_path)
	# 	if file.exists():
	# 		gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_dataset_config(
	# 			config_file_path)
	# 		if gdc_ok:
	# 			sig_field = "SIG_" + dataset_config['sig_suffix']
	# 			field_ok_basic = ndf.is_field_exist(symbol, sig_field)
	#
	# 			if not force:
	# 				field_ok_basic = True  # ha force akkor nincs szükség sigre sem
	#
	# 			field_ok_original_fields = True
	# 			for o_f in original_fields:
	# 				field_ok_original_fields = field_ok_original_fields and ndf.is_field_exist(symbol, o_f)
	#
	# 			field_ok_contras = True
	# 			for c in contras:
	# 				field_ok_contras = field_ok_contras and ndf.is_contra(c)
	#
	# 			if field_ok_basic and field_ok_original_fields and field_ok_contras:
	# 				time_window_size = dataset_config["time_window_size"]
	# 				back_shift = dataset_config["data_window_back_shift"]
	# 				overlay_steps = dataset_config["overlay_steps"]
	# 				y_field = "y_" + dataset_config["sig_suffix"]
	# 				if force:  # ha már van y akkor kitörli és mindenképen megcsinálja
	# 					ndf.remove_columns(symbol, [y_field])
	# 				if y_field in nddf[symbol].columns:
	# 					log(y_field + " already exist.")
	# 				else:
	# 					log("Creating y from SIG. with overlay manager: " + sig_field + "->" + y_field)
	# 					self.sig_to_y(symbol, sig_field, y_field, overlay_steps)
	#
	# 				log("Creating dataset.")
	# 				# image fej megcsinálása, minden image nél ugyan az
	# 				nd_dset = n_dataset(log)
	# 				nd_dset.set_symbol(symbol)
	#
	# 				nd_dset.set_source("nDot.py->n_data_frame2->create_dataset_int")
	# 				nd_dset.set_name("nDot_DATASET_" + project_name)
	# 				nd_dset.set_project_name(project_name)
	#
	# 				nd_dset.set_description(description)
	#
	# 				y_names = {'0=under limit; 1=good long; 2=good short'}
	# 				# itt nem négy kategóriát(cimkét tanítok hanem 100 cimkét) jel erősségét fogom tnítani
	# 				nd_dset.add_y_names(y_names)
	# 				#  beteszem a 'good' signálokat -----------------------------------------
	# 				first_cut = 1000
	# 				i_indexes = {}
	#
	# 				for ix in range(3):
	# 					i_indexes[ix] = np.array(nddf[symbol].loc[nddf[symbol][y_field] == ix].index)
	# 					fr = np.where(nddf[symbol][y_field].to_numpy() == ix)[0]
	# 					print(i_indexes[ix])
	# 					print(fr)
	# 					# i_indexes[ix] = i_indexes[ix][(i_indexes[ix] > time_window_size + first_cut)]
	#
	# 				# i_indexes[1] = i_indexes[1][0:2000]
	# 				# i_indexes[2] = i_indexes[2][0:2000]
	#
	# 				len1 = len(i_indexes[1])
	# 				len2 = len(i_indexes[2])
	# 				max_elemet = max(len1, len2) * int(dataset_config['bad_overweight'])
	# 				# i_indexes[0] = i_indexes[0][0+600000: max_elemet+600000]
	# 				# i_indexes[0] = i_indexes[0][0: max_elemet]
	# 				i_indexes[0] = np.random.choice(i_indexes[0], min(i_indexes[0].shape[0], max_elemet), replace=False)
	# 				s2(True, len1 + len2 + max_elemet)
	# 				for ix in range(3):
	# 					log("  Number of selectd y: " + str(ix) + " " + str(len(i_indexes[ix])))
	# 				# i_index_good_long = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 0].index)
	# 				# i_index_good_long = i_index_good_long[(i_index_good_long > time_window_size + first_cut)]
	# 				# i_index_good_short = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 1].index)
	# 				# i_index_good_short = i_index_good_short[(i_index_good_short > time_window_size + first_cut)]
	# 				# s2()
	# 				# i_index_bad_long = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 2].index)
	# 				# i_index_bad_long = i_index_bad_long[(i_index_bad_long > time_window_size + first_cut)]
	# 				# i_index_bad_short = np.array(nddf[symbol].loc[nddf[symbol][y_field] == 3].index)
	# 				# i_index_bad_short = i_index_bad_short[(i_index_bad_short > time_window_size + first_cut)]
	#
	# 				# ha egy érték y (0,1,2,3) hinyzik akkor az nem számít bele a minimumna
	# 				# min_array = np.array([len(i_index_good_long),
	# 				# 					  len(i_index_good_short),
	# 				# 					  len(i_index_bad_long),
	# 				# 					  len(i_index_bad_short)])
	# 				# min_array = np.ma.masked_equal(min_array, 0, copy=False)
	# 				#
	# 				# max_signals = min_array.min()
	# 				# max_signals = int(max_signals * dataset_config['bad_overweight'])
	# 				#
	# 				# i_index_good_long = i_index_good_long[0:max_signals]
	# 				# i_index_good_short = i_index_good_short[0:max_signals]
	# 				# i_index_bad_long = i_index_bad_long[0:max_signals]
	# 				# i_index_bad_short = i_index_bad_short[0:max_signals]
	#
	# 				nd_dset.set_window_size(time_window_size)
	# 				used_cores = cpu_count()
	# 				runing_processes = np.array([None] * used_cores)
	# 				contra_copies, contra_copies_dt = ndf.get_contra_copies(contras)
	# 				prc_count = 0
	# 				for ix in range(6):
	# 					x_from = get_slice_index(i_indexes[0].shape[0], 6, ix)[0]
	# 					x_to = get_slice_index(i_indexes[0].shape[0], 6, ix)[1]
	# 					# print(ix)
	# 					# dataset_constructor(symbol=symbol,
	# 					# 					indexes=i_indexes[ix],
	# 					# 					time_window_size=time_window_size,
	# 					# 					y=ix,
	# 					# 					original_fields=original_fields,
	# 					# 					contras=contras,
	# 					# 					back_shift=back_shift,
	# 					# 					nd_dset=nd_dset)
	#
	# 					params = {'cores': used_cores,
	# 							  'process': ix,
	# 							  'symbol': symbol,
	# 							  'indexes': i_indexes[0][x_from:x_to],
	# 							  'time_window_size': time_window_size,
	# 							  'y': 0,
	# 							  'original_fields': original_fields,
	# 							  'contras': contras,
	# 							  'back_shift': back_shift,
	# 							  'contra_copies_dt': contra_copies_dt,
	# 							  'nddf': nddf,
	# 							  'gap_manager': 'drop'
	# 							  }
	#
	# 					runing_processes[prc_count] = Process(target=mp_dataset_constructor, args=(params,))
	# 					prc_count += 1
	#
	# 				params = {'cores': used_cores,
	# 						  'process': 6,
	# 						  'symbol': symbol,
	# 						  'indexes': i_indexes[1],
	# 						  'time_window_size': time_window_size,
	# 						  'y': 1,
	# 						  'original_fields': original_fields,
	# 						  'contras': contras,
	# 						  'back_shift': back_shift,
	# 						  'contra_copies_dt': contra_copies_dt,
	# 						  'nddf': nddf,
	# 						  'gap_manager': 'drop'
	# 						  }
	#
	# 				runing_processes[prc_count] = Process(target=mp_dataset_constructor, args=(params,))
	# 				prc_count += 1
	#
	# 				params = {'cores': used_cores,
	# 						  'process': 7,
	# 						  'symbol': symbol,
	# 						  'indexes': i_indexes[2],
	# 						  'time_window_size': time_window_size,
	# 						  'y': 2,
	# 						  'original_fields': original_fields,
	# 						  'contras': contras,
	# 						  'back_shift': back_shift,
	# 						  'contra_copies_dt': contra_copies_dt,
	# 						  'nddf': nddf,
	# 						  'gap_manager': 'drop'
	# 						  }
	#
	# 				runing_processes[prc_count] = Process(target=mp_dataset_constructor, args=(params,))
	# 				prc_count += 1
	#
	# 				for x, prc in enumerate(runing_processes):
	# 					prc.start()
	# 					time.sleep(.25)
	#
	# 				for prc in runing_processes:
	# 					prc.join()
	#
	# 				X_arra = []
	#
	#
	# 				for ic in range(used_cores):
	# 					file_name = self.temp_path + 'DATASET_DATACONSTRUCTOR_X_RESULTS' + str(ic) + '.npy'
	# 					X_arra.append(np.load(file_name))
	# 				X_arra = np.concatenate(X_arra)
	#
	# 				nd_dset.add_X(X_arra)
	#
	# 				y_arra = []
	# 				for ic in range(used_cores):
	# 					file_name = self.temp_path + 'DATASET_DATACONSTRUCTOR_y_RESULTS' + str(ic) + '.npy'
	# 					y_arra.append(np.load(file_name))
	# 				y_arra = np.concatenate(y_arra)
	# 				nd_dset.add_y(y_arra)
	#
	# 				# historic max and min ---------------------------------
	#
	# 				i_historic_max = np.array([])
	# 				i_historic_min = np.array([])
	# 				if len(original_fields) > 0:
	# 					for i_of in original_fields:
	# 						nd_dset.add_field(i_of)
	# 						i_conc = float(np.nanmax(tuple(nddf[symbol][i_of])))
	# 						i_conc = np.full(time_window_size, i_conc)
	# 						i_historic_max = np.concatenate((i_historic_max, i_conc))
	#
	# 						i_conc = float(np.nanmin(tuple(nddf[symbol][i_of])))
	# 						i_conc = np.full(time_window_size, i_conc)
	# 						i_historic_min = np.concatenate((i_historic_min, i_conc))
	#
	# 				for i_con in contras:
	# 					nd_dset.add_field(i_con)
	# 					contra_sep_pre = i_con.split('_')
	# 					con_sep = []
	# 					if len(contra_sep_pre) > 2:
	# 						con_sep.append(contra_sep_pre[0])
	# 						s = "_"
	# 						con_sep.append(s.join(contra_sep_pre[1:]))
	# 					else:
	# 						con_sep = contra_sep_pre
	#
	# 					con_symbol = con_sep[0]
	# 					con_field = con_sep[1]
	# 					i_conc = float(np.nanmax(tuple(nddf[con_symbol][con_field])))
	# 					i_conc = np.full(time_window_size, i_conc)
	# 					i_historic_max = np.concatenate((i_historic_max, i_conc))
	#
	# 					i_conc = float(np.nanmin(tuple(nddf[con_symbol][con_field])))
	# 					i_conc = np.full(time_window_size, i_conc)
	# 					i_historic_min = np.concatenate((i_historic_min, i_conc))
	# 				s2()
	# 				nd_dset.set_historic_max(i_historic_max)
	# 				nd_dset.set_historic_min(i_historic_min)
	# 				s2()
	# 				nd_dset.set_meta(ndf_meta.get_all_meta_key(symbol))
	# 				s2()
	# 				nd_dset.save()
	# 				s2()
	# 				del nd_dset
	# 			else:
	# 				if not field_ok_basic:
	# 					log("Config file, basic parameter(s) is missing.")
	# 				if not field_ok_original_fields:
	# 					log("Config file, Orifinal field(s) is missing.")
	# 				if not field_ok_contras:
	# 					log("Config file, Contra field(s) is missing.")
	# 		else:
	# 			log("config file conversion error. (,) is missing ? :)")
	#
	# 	else:
	# 		log("config file is missing:" + str(config_file_path))
	#
	# 	nddf[symbol] = i_save

	def get_first_signal(self, symbol, long_field, short_field, long_field_first, short_field_first):
		nddf[symbol][long_field_first] = ~(nddf[symbol][long_field] == nddf[symbol][long_field].shift(1)) & \
										 nddf[symbol][long_field]
		nddf[symbol][short_field_first] = ~(nddf[symbol][short_field] == nddf[symbol][short_field].shift(1)) & \
										  nddf[symbol][short_field]
		return long_field_first, short_field_first

	def vector_qualify(self,
					   symbol,
					   sig_suffix,
					   stock_size,
					   min_profit, min_step_profit,
					   stop,
					   steps, overlay_steps,
					   overlay_manager="rnd_choice",
					   profit_window_shift=0):
		"""
		:param profit_window_shift:  honnan számolja a profitot
		:param symbol:
		:param sig_suffix: end of the signal  SIG_ + sig_suffix
		:param stock_size: invested stock size in USD
		:param min_profit: minimum profit in USD
		:param min_step_profit: protect against outlier, if profit comes too fast
		:param stop: stop loss in USD
		:param steps: maximum steps for profit takeing
		:param overlay_steps: signal overlay, the next qfy signal must be out of overlay_steps
		:param overlay_manager: vector / full / rnd_choice
		:return: no return auto update nddf
		"""

		# overlay_manager = "vector"
		# overlay_manager = "full"
		# overlay_manager = "rnd_choice"

		first_sig_field = "SIG_" + sig_suffix
		y_field = "y_" + sig_suffix

		# # save originalfields
		# original_df = pd.DataFrame(None)
		# original_df = nddf[symbol][[long_field, short_field]].copy()

		log(f"ndf->vector_qualify: {stock_size} $ p/s:" +
			f"{min_profit}$/{stop}$ steps:{steps} overlay steps:{overlay_steps} overlay_manager: {str(overlay_manager)}")

		s2(True, 22)

		def random_choice_overlay(a_from, overlay_steps):
			size = len(a_from)
			a_to_return = np.full(size, 4)

			def is_fit(pos, dist):
				sum_before = a_to_return[pos - dist: pos].sum() - (4 * dist) == 0
				sum_after = a_to_return[pos + 1: pos + dist + 1].sum() - (4 * dist) == 0
				return sum_before and sum_after

			def put_over(pos_array, dist, value):
				for pos in pos_array:
					if is_fit(pos, dist):
						a_to_return[pos] = value
						a_from[pos] = 4
					else:
						a_from[pos] = 4

			filtered_empty = []
			while len(filtered_empty) != 2:
				for sig in range(2):
					a_from_filtered = np.where(a_from == sig)[0]
					if len(a_from_filtered) != 0 and sig not in filtered_empty:
						pos_array = np.random.choice(a_from_filtered, int(size * .0008))
						# print(pos_array)
						put_over(pos_array, overlay_steps, sig)
					else:
						if sig not in filtered_empty:
							filtered_empty.append(sig)

			filtered_empty = []
			while len(filtered_empty) != 2:
				for sig in range(2):
					a_from_filtered = np.where(a_from == sig + 2)[0]
					if len(a_from_filtered) != 0 and sig + 2 not in filtered_empty:
						pos_array = np.random.choice(a_from_filtered, 10)
						# print(pos_array)
						put_over(pos_array, overlay_steps, sig + 2)
					else:
						if sig + 2 not in filtered_empty:
							filtered_empty.append(sig + 2)
			return a_to_return

		def y_chk(symbol, y_field, overlay_steps):

			s2()

			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXP" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][y_field].shift(i_dif)

			nddf[symbol]["chk_result"] = 0
			i_pos_first = nddf[symbol].columns.get_loc("SXP1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SCPMAX"] = nddf[symbol].iloc[:, i_ser].fillna(4).sum(axis=1)
			nddf[symbol]["chk_result"] = nddf[symbol][y_field] * (nddf[symbol]["SCPMAX"] - (4 * overlay_steps))
			i_remove.append('SCPMAX')
			self.remove_columns(symbol, i_remove)

			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXM" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][y_field].shift(0 - i_dif)

			i_pos_first = nddf[symbol].columns.get_loc("SXM1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SXMMAX"] = nddf[symbol].iloc[:, i_ser].fillna(4).sum(axis=1)
			nddf[symbol]["chk_result"] = nddf[symbol][y_field] * (nddf[symbol]["SXMMAX"] - (4 * overlay_steps))
			nddf[symbol].loc[nddf[symbol][y_field] == 4, 'chk_result'] = 0

			i_result = nddf[symbol]["chk_result"].sum()
			i_remove.append('SXMMAX')
			i_remove.append('chk_result')
			self.remove_columns(symbol, i_remove)
			return i_result

		def qfy_bad_cross(symbol, ori_field, envi_fileld, overlay_steps):

			s2()

			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXQF" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif)

			i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
			nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
			i_remove.append('SXQFMAX')
			self.remove_columns(symbol, i_remove)

			s2()

			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXQF" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(0 - i_dif)

			i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
			nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFMAX"] == 0)
			i_remove.append('SXQFMAX')
			self.remove_columns(symbol, i_remove)

		# if 1 == 1:
		#     # nem lehet utána qfy short
		#     i_remove = []
		#     for i_dif in range(1, overlay_steps + 1):
		#         c_name = "SXQF" + str(i_dif)
		#         i_remove.append(c_name)
		#         nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif)
		#
		#     i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
		#     i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
		#
		#     nddf[symbol]["qfy_bad_cross1"] = nddf[symbol].iloc[:, i_ser].max(axis=1) * nddf[symbol][ori_field]
		#     print(ori_field,envi_fileld,'qfy_bad_cross1', nddf[symbol]["qfy_bad_cross1"].sum())
		#     i_remove.append('qfy_bad_cross1')
		#     self.remove_columns(symbol, i_remove)
		#
		#     s2()
		#
		#     # nem lehet utána qfy short
		#     i_remove = []
		#     for i_dif in range(1, overlay_steps + 1):
		#         c_name = "SXQF" + str(i_dif)
		#         i_remove.append(c_name)
		#         nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(0 - i_dif)
		#
		#     i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
		#     i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
		#
		#     nddf[symbol]["qfy_bad_cross2"] = nddf[symbol].iloc[:, i_ser].max(axis=1) * nddf[symbol][ori_field]
		#     print(ori_field,envi_fileld,'qfy_bad_cross2', nddf[symbol]["qfy_bad_cross2"].sum())
		#     i_remove.append('qfy_bad_cross2')
		#     self.remove_columns(symbol, i_remove)

		def qfy_bad_cross_rnd(symbol, ori_field, envi_fileld, overlay_steps):

			s2()

			nddf[symbol]['XRND'] = np.random.randint(2, size=nddf[symbol].shape[0])
			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXQF" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(i_dif)

			i_pos_first = nddf[symbol].columns.get_loc("SXQF1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SXQFMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
			nddf[symbol][ori_field] = (nddf[symbol][ori_field] & \
									   (nddf[symbol]["SXQFMAX"] == 0)) | \
									  (nddf[symbol][ori_field] & \
									   (nddf[symbol]["XRND"] == 0))
			i_remove.append('SXQFMAX')
			self.remove_columns(symbol, i_remove)

			s2()

			# nem lehet utána qfy short
			i_remove = []
			for i_dif in range(1, overlay_steps + 1):
				c_name = "SXQF" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][envi_fileld].shift(0 - i_dif)

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
				c_name = "SXQFBB" + str(i_dif)
				i_remove.append(c_name)
				nddf[symbol][c_name] = nddf[symbol][ori_field].shift(i_dif)

			i_pos_first = nddf[symbol].columns.get_loc("SXQFBB1")
			i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))

			nddf[symbol]["SXQFBBMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1)
			nddf[symbol][ori_field] = nddf[symbol][ori_field] & (nddf[symbol]["SXQFBBMAX"] == 0)
			i_remove.append('SXQFBBMAX')
			self.remove_columns(symbol, i_remove)

		# check
		# if 1 == 1:
		#     # nem lehet utána qfy short
		#     i_remove = []
		#     for i_dif in range(1, overlay_steps + 1):
		#         c_name = "SXQFBB" + str(i_dif)
		#         i_remove.append(c_name)
		#         nddf[symbol][c_name] = nddf[symbol][ori_field].shift(i_dif)
		#
		#     i_pos_first = nddf[symbol].columns.get_loc("SXQFBB1")
		#     i_ser = list(range(i_pos_first, i_pos_first + overlay_steps))
		#
		#     nddf[symbol]["qfy_bad_befo_chk"] = nddf[symbol].iloc[:, i_ser].max(axis=1) * nddf[symbol][ori_field]
		#     print(ori_field, nddf[symbol]["qfy_bad_befo_chk"].sum())
		#     # i_remove.append('qfy_bad_befo_chk')
		#     # self.remove_columns(symbol, i_remove)

		# -----------------------------------------------------------------------------------------
		# main programof vector_qualify -----------------------------------------------------------
		# -----------------------------------------------------------------------------------------

		# adott stepen belül kiválasztoma maiximum és a minimum értékeket
		i_remove = []
		pnl_first_calc_position = 1
		for i_dif in range(pnl_first_calc_position, steps + 1):
			c_name = "XL" + str(i_dif)
			# print(c_name)
			i_remove.append(c_name)
			nddf[symbol][c_name] = ((nddf[symbol].Low.shift(-(i_dif + profit_window_shift)) /
									 nddf[symbol].High.shift(-profit_window_shift)) - 1) * 100

		for i_dif in range(pnl_first_calc_position, steps + 1):
			c_name = "XS" + str(i_dif)
			# print(c_name)
			i_remove.append(c_name)
			nddf[symbol][c_name] = ((nddf[symbol].High.shift(-(i_dif + profit_window_shift)) /
									 nddf[symbol].Low.shift(-profit_window_shift)) - 1) * 100

		# print(nddf[symbol].Date.shift(0))
		# print(nddf[symbol].Date.shift(-1))

		i_pos_first_l = nddf[symbol].columns.get_loc("XL" + str(pnl_first_calc_position))
		i_ser_l = list(range(i_pos_first_l, i_pos_first_l + steps))

		i_pos_first_s = nddf[symbol].columns.get_loc("XS" + str(pnl_first_calc_position))
		i_ser_s = list(range(i_pos_first_s, i_pos_first_s + steps))

		nddf[symbol]["XMAXL"] = nddf[symbol].iloc[:, i_ser_l].max(axis=1)
		nddf[symbol]["XMINL"] = nddf[symbol].iloc[:, i_ser_l].min(axis=1)

		nddf[symbol]["XMAXS"] = nddf[symbol].iloc[:, i_ser_s].max(axis=1)
		nddf[symbol]["XMINS"] = nddf[symbol].iloc[:, i_ser_s].min(axis=1)

		nddf[symbol]["XMAX"] = nddf[symbol][["XMAXL", "XMAXS"]].min(axis=1)
		nddf[symbol]["XMIN"] = nddf[symbol][["XMINL", "XMINS"]].max(axis=1)
		# print(nddf[symbol][["XMAXL", "XMAXS", "XMAX"]])
		# print(nddf[symbol][["XMINL", "XMINS", "XMIN"]])

		nddf[symbol]["XMAX_USD"] = nddf[symbol]["XMAX"] * stock_size / 100
		nddf[symbol]["XMIN_USD"] = nddf[symbol]["XMIN"] * stock_size / 100

		s2()

		# nddf[symbol]["XMAX_POS"] = nddf[symbol].iloc[:, i_ser].idxmax(axis=1)
		# nddf[symbol]["XMIN_POS"] = nddf[symbol].iloc[:, i_ser].idxmin(axis=1)


		#
		# nddf[symbol]["XMAX_POS"] = nddf[symbol]["XMAX_POS"].str.replace('X', '')
		# nddf[symbol]["XMAX_POS"] = pd.to_numeric(nddf[symbol]["XMAX_POS"])
		#
		# nddf[symbol]["XMIN_POS"] = nddf[symbol]["XMIN_POS"].str.replace('X', '')
		# nddf[symbol]["XMIN_POS"] = pd.to_numeric(nddf[symbol]["XMIN_POS"])

		# aztnézi, hogy a kreskedés  nem nyúlhat át másik nem kezdődhet a deal ma és honap fejeződik be.
		# ha ugyan az akkor a SHIFTED_DAY_OK = True
		nddf[symbol]["ACT_DAY"] = nddf[symbol]["Date"].dt.day
		nddf[symbol]["SHIFTED_DAY"] = nddf[symbol].Date.shift(0 - steps).dt.day
		nddf[symbol]["SHIFTED_DAY_OK"] = False
		nddf[symbol]["SHIFTED_DAY_OK"] = nddf[symbol]["ACT_DAY"] == nddf[symbol]["SHIFTED_DAY"]

		s2()

		# Qualify long positons
		qfy_long_field = "SIG_QFY_" + sig_suffix + "_GOOD_LONG"
		# nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMAX_USD"] > min_profit) & \
		# 								(nddf[symbol]["XMAX_POS"] > min_step_profit)
		#
		# nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMAX_USD"] > min_profit) & \
		# 								(nddf[symbol]["XMAX_POS"] > min_step_profit)

		nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMAX_USD"] > min_profit)

		# nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMIN_USD"] < stop
		# nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] > nddf[symbol]["XMAX_POS"]
		# nddf[symbol][qfy_long_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
		# 							   ((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
		# 								(~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
		# 								 ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"])) & nddf[symbol]["SHIFTED_DAY_OK"]

		nddf[symbol]["LOSS_NOT_OVER_STOP_LIMIT"] = nddf[symbol]["XMIN_USD"] > stop
		nddf[symbol][qfy_long_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
									   nddf[symbol]["LOSS_NOT_OVER_STOP_LIMIT"] & \
									   nddf[symbol]["SHIFTED_DAY_OK"]

		y_field_temp = y_field + "_TEMP"

		nddf[symbol][y_field_temp] = 0
		nddf[symbol][y_field_temp].values[nddf[symbol][qfy_long_field] & (nddf[symbol][first_sig_field] == 0)] = 1
		nddf[symbol][y_field_temp].values[(~nddf[symbol][qfy_long_field]) & (nddf[symbol][first_sig_field] == 0)] = 3

		i_remove.append('MIN_PROFIT_OK')
		i_remove.append('LOSS_NOT_OVER_STOP_LIMIT')
		# i_remove.append('STOP_POS_AFTER_PROFIT_POS')
		self.remove_columns(symbol, i_remove)

		s2()

		# Qualify SHORT positons
		qfy_short_field = "SIG_QFY_" + sig_suffix + "_GOOD_SHORT"
		# nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMIN_USD"] < -min_profit) & \
		# 								(nddf[symbol]["XMIN_POS"] > min_step_profit)

		nddf[symbol]["MIN_PROFIT_OK"] = (nddf[symbol]["XMIN_USD"] < -min_profit)

		# nddf[symbol]["LOSS_OVER_STOP_LIMIT"] = nddf[symbol]["XMAX_USD"] > -stop
		# nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] = nddf[symbol]["XMIN_POS"] < nddf[symbol]["XMAX_POS"]
		# nddf[symbol][qfy_short_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
		# 								((nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"]) |
		# 								 (~nddf[symbol]["STOP_POS_AFTER_PROFIT_POS"] &
		# 								  ~nddf[symbol]["LOSS_OVER_STOP_LIMIT"])) & nddf[symbol]["SHIFTED_DAY_OK"]

		nddf[symbol]["LOSS_NOT_OVER_STOP_LIMIT"] = nddf[symbol]["XMAX_USD"] < -stop
		nddf[symbol][qfy_short_field] = nddf[symbol]["MIN_PROFIT_OK"] & \
										nddf[symbol]["LOSS_NOT_OVER_STOP_LIMIT"] & \
										nddf[symbol]["SHIFTED_DAY_OK"]

		nddf[symbol][y_field_temp].values[nddf[symbol][qfy_short_field] & (nddf[symbol][first_sig_field] == 1)] = 2
		nddf[symbol][y_field_temp].values[(~nddf[symbol][qfy_short_field]) & (nddf[symbol][first_sig_field] == 1)] = 4

		log(f"Number of signal before overlay check.")
		log(f"  y=4 (None) result: {(nddf[symbol][y_field_temp] == 0).sum()}")
		log(f"  y=0 (GOOD LONG) result: {(nddf[symbol][y_field_temp] == 1).sum()}")
		log(f"  y=1 (GOOD SHORT) result: {(nddf[symbol][y_field_temp] == 2).sum()}")
		log(f"  y=2 (BAD LONG) result: {(nddf[symbol][y_field_temp] == 3).sum()}")
		log(f"  y=3 (BAD SHORT) result: {(nddf[symbol][y_field_temp] == 4).sum()}")

		if overlay_manager == "vector":
			log("overlay manager: Vector")
			nddf[symbol]["y_1"] = False
			nddf[symbol]["y_1"].values[nddf[symbol][y_field_temp] == 1] = True

			nddf[symbol]["y_2"] = False
			nddf[symbol]["y_2"].values[nddf[symbol][y_field_temp] == 2] = True

			nddf[symbol]["y_3"] = False
			nddf[symbol]["y_3"].values[nddf[symbol][y_field_temp] == 3] = True

			nddf[symbol]["y_4"] = False
			nddf[symbol]["y_4"].values[nddf[symbol][y_field_temp] == 4] = True

			qfy_bad_befo(symbol, 'y_1', overlay_steps)
			qfy_bad_befo(symbol, 'y_2', overlay_steps)

			qfy_bad_cross_rnd(symbol, 'y_1', 'y_2', overlay_steps)
			qfy_bad_cross(symbol, 'y_2', 'y_1', overlay_steps)

			qfy_bad_cross(symbol, 'y_3', 'y_1', overlay_steps)
			qfy_bad_cross(symbol, 'y_3', 'y_2', overlay_steps)

			qfy_bad_cross(symbol, 'y_4', 'y_1', overlay_steps)
			qfy_bad_cross(symbol, 'y_4', 'y_2', overlay_steps)

			qfy_bad_befo(symbol, 'y_3', overlay_steps)
			qfy_bad_befo(symbol, 'y_4', overlay_steps)

			qfy_bad_cross_rnd(symbol, 'y_3', 'y_4', overlay_steps)
			qfy_bad_cross(symbol, 'y_4', 'y_3', overlay_steps)

			nddf[symbol][y_field] = 4
			nddf[symbol][y_field].values[nddf[symbol]['y_1']] = 0
			nddf[symbol][y_field].values[nddf[symbol]['y_2']] = 1
			nddf[symbol][y_field].values[nddf[symbol]['y_3']] = 2
			nddf[symbol][y_field].values[nddf[symbol]['y_4']] = 3

			i_remove = ['y_1', 'y_2', 'y_3', 'y_4',
						y_field_temp]
			self.remove_columns(symbol, i_remove)

		elif overlay_manager == "rnd_choice":
			log("overlay manager: Rnd_choice")
			y_field_temp_shifted = y_field_temp + "S"
			nddf[symbol][y_field_temp_shifted] = 4
			nddf[symbol][y_field_temp_shifted].values[nddf[symbol][y_field_temp] == 1] = 0
			nddf[symbol][y_field_temp_shifted].values[nddf[symbol][y_field_temp] == 2] = 1
			nddf[symbol][y_field_temp_shifted].values[nddf[symbol][y_field_temp] == 3] = 2
			nddf[symbol][y_field_temp_shifted].values[nddf[symbol][y_field_temp] == 4] = 3

			a_from = np.array(nddf[symbol][y_field_temp_shifted])
			rco_result = random_choice_overlay(a_from, overlay_steps)
			nddf[symbol][y_field] = rco_result
			i_remove = [y_field_temp, y_field_temp_shifted]
			self.remove_columns(symbol, i_remove)

		elif overlay_manager == "full":
			nddf[symbol][y_field] = 4
			nddf[symbol][y_field].values[nddf[symbol][y_field_temp] == 1] = 0
			nddf[symbol][y_field].values[nddf[symbol][y_field_temp] == 2] = 1
			nddf[symbol][y_field].values[nddf[symbol][y_field_temp] == 3] = 2
			nddf[symbol][y_field].values[nddf[symbol][y_field_temp] == 4] = 3
			i_remove = [y_field_temp]
			self.remove_columns(symbol, i_remove)

		ychk = y_chk(symbol, y_field, overlay_steps)

		log(f"Number of signal after overlay check.")
		log(f"  y=4 (None) result: {(nddf[symbol][y_field] == 4).sum()}")
		log(f"  y=0 (GOOD LONG) result: {(nddf[symbol][y_field] == 0).sum()}")
		log(f"  y=1 (GOOD SHORT) result: {(nddf[symbol][y_field] == 1).sum()}")
		log(f"  y=2 (BAD LONG) result: {(nddf[symbol][y_field] == 2).sum()}")
		log(f"  y=3 (BAD SHORT) result: {(nddf[symbol][y_field] == 3).sum()}")
		log(f"  y chk sum: (0 = no overlay) result: {ychk}")
		log("  Time frame: " + str(nddf[symbol]["Date"].min()) + " - " + str(nddf[symbol]["Date"].max()))

		i_remove.append(["XMAX", "XMAXL", "XMINL", "XMAXS", "XMINS",
						 "XMIN", "XMAX", "XMAXL", "XMAXS",
						 "XMINL", "XMINS", 'XMAX_USD', 'XMIN_USD',
						 'XMAX_POS', 'XMIN_POS',
						 'MIN_PROFIT_OK', 'LOSS_OVER_STOP_LIMIT', 'STOP_POS_AFTER_PROFIT_POS',
						 'ACT_DAY', 'SHIFTED_DAY', 'SHIFTED_DAY_OK', 'XXRND',
						 qfy_long_field, qfy_short_field])
		self.remove_columns(symbol, i_remove)
		s("")

	def refresh_tech(self, symbol, indicator, tail_size=500, log_vissible=True):
		i_rows = nddf[symbol].shape[0]
		# print("nan", nddf[symbol].isna().sum())

		indi_overlay = 100
		reduce_tail = tail_size - indi_overlay
		# print(nddf[symbol])
		i_nddf = nddf[symbol].copy()
		nddf[symbol] = nddf[symbol][-tail_size:].copy()
		ndf.set_dt_order(symbol)

		# print("1.")
		# print(nddf[symbol][["Date", "LOW_DIFF"]])
		# nddf[symbol] = i_nddf.copy()
		# print(nddf[symbol])
		nddb.enable_write = False
		self.add_tech(symbol, indicator, log_visible=log_vissible)
		nddb.enable_write = True
		# print("2.")
		# print(nddf[symbol][["Date", "LOW_DIFF"]])
		i_nddf2 = i_nddf.copy()
		i_nddf2 = i_nddf2[:-reduce_tail].copy()

		# print(i_nddf2, nddf[symbol][-reduce_tail:])
		i_nddf3 = pd.concat([i_nddf2, nddf[symbol][-reduce_tail:]], ignore_index=True)
		# print("3.")
		# print(i_nddf3[["Date", "LOW_DIFF"]])
		# print("shape new:", i_nddf3.shape)
		# print("nan", i_nddf3.isna().sum())
		nddf[symbol] = i_nddf3.copy()
		ndf.set_dt_order(symbol)
		nddb.write(symbol, log_visible=log_vissible)
		if i_rows - nddf[symbol].shape[0] != 0:
			log("ndf-> tech_refresh error, row count not equal after refresh")

	def inf_to_max(self, symbol, field):
		vd = np.array(nddf[symbol][field])
		vdx = np.where(vd == np.inf)[0]
		vd[vdx] = 0
		vd_max = np.nanmax(vd)
		vd[vdx] = vd_max
		nddf[symbol][field] = vd

	def add_tech(self, symbol, tech_indicator="SMA60", params=[], log_visible=True):

		log("ndf-> add_tech " + symbol + " - " + str(tech_indicator), visible=log_visible)

		if self.is_indicator(tech_indicator):

			if tech_indicator == "PRICE_DIFF":
				self.case_set_back(symbol)
				nddf[symbol]["Low_DIFF"] = (nddf[symbol]["Low"] / nddf[symbol]["Low"].shift(1)) - 1
				nddf[symbol]["High_DIFF"] = (nddf[symbol]["High"] / nddf[symbol]["High"].shift(1)) - 1
				nddf[symbol]["Open_DIFF"] = (nddf[symbol]["Open"] / nddf[symbol]["Open"].shift(1)) - 1
				nddf[symbol]["Close_DIFF"] = (nddf[symbol]["Close"] / nddf[symbol]["Close"].shift(1)) - 1
				nddf[symbol]["ohlc4_DIFF"] = (nddf[symbol]["ohlc4"] / nddf[symbol]["ohlc4"].shift(1)) - 1
				nddf[symbol]["Volume_DIFF"] = (nddf[symbol]["Volume"] / nddf[symbol]["Volume"].shift(1)) - 1

				nddf[symbol]["Quote_asset_volume_DIFF"] = (nddf[symbol]["Quote_asset_volume"] / nddf[symbol]["Quote_asset_volume"].shift(1)) - 1
				nddf[symbol]["Number_of_trades_DIFF"] = (nddf[symbol]["Number_of_trades"] / nddf[symbol]["Number_of_trades"].shift(1)) - 1
				nddf[symbol]["Taker_buy_base_asset_volume_DIFF"] = (nddf[symbol]["Taker_buy_base_asset_volume"] / nddf[symbol]["Taker_buy_base_asset_volume"].shift(1)) - 1
				nddf[symbol]["Taker_buy_quote_asset_volume_DIFF"] = (nddf[symbol]["Taker_buy_quote_asset_volume"] / nddf[symbol]["Taker_buy_quote_asset_volume"].shift(1)) - 1

				# vol diff esetén előjön hogy np.inf készül amikor 0 forgaromlór 100000 ra ugrik, ezeket kicserélem
				# a legnagyobb hisztorikus számra
				self.inf_to_max(symbol, "Volume_DIFF")
				self.inf_to_max(symbol, "Quote_asset_volume_DIFF")
				self.inf_to_max(symbol, "Number_of_trades_DIFF")
				self.inf_to_max(symbol, "Taker_buy_base_asset_volume_DIFF")
				self.inf_to_max(symbol, "Taker_buy_quote_asset_volume_DIFF")

				nddf[symbol]["Low_R_OHLC4"] = nddf[symbol]["Low"] / nddf[symbol]["ohlc4"]
				nddf[symbol]["High_R_OHLC4"] = nddf[symbol]["High"] / nddf[symbol]["ohlc4"]

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

			elif tech_indicator == "MACD_LONG":
				df_copy = nddf[symbol].copy()
				df_copy.ta.macd(fast=26, slow=48, signal=12, append=True)
				nddf[symbol]['MACDh_26_48_12'] = df_copy['MACDh_26_48_12']
				del df_copy
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "BBANDS":
				nddf[symbol].ta.bbands(append=True)

			elif tech_indicator == "CCI21":
				nddf[symbol].ta.cci(length=21, append=True)
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "MT":
				a_len = nddf[symbol].shape[0]
				s2(True, a_len)
				cci = 20
				atr = 5
				multiplier = .7
				original = False
				nddf[symbol].ta.cci(length=cci, append=True)
				s2()
				nddf[symbol].ta.true_range(append=True)  # TRUERANGE_1
				nddf[symbol].ta.atr(length=atr, append=True)
				nddf[symbol]['TRsma_' + str(atr)] = ta.sma(nddf[symbol]["TRUERANGE_1"], length=atr)
				s2()
				nddf[symbol]['CCI_SHIFT'] = nddf[symbol]['CCI_' + str(cci) + '_0.015'].shift(1)
				nddf[symbol]['bufferDn'] = nddf[symbol]['high'] + multiplier * nddf[symbol]['TRsma_' + str(atr)]
				# nddf[symbol]['bufferDn_SHIFT'] = nddf[symbol]['bufferDn'].shift(1).fillna(0)
				nddf[symbol]['bufferUp'] = nddf[symbol]['low'] - multiplier * nddf[symbol]['TRsma_' + str(atr)]
				# nddf[symbol]['bufferUp_SHIFT'] = nddf[symbol]['bufferUp'].shift(1).fillna(0)
				nddf[symbol]['bufferDn_S'] = nddf[symbol]['bufferDn']
				nddf[symbol]['bufferUp_S'] = nddf[symbol]['bufferUp']

				s2()
				i_buffer_dn = np.array(nddf[symbol]['bufferDn'])
				i_buffer_up = np.array(nddf[symbol]['bufferUp'])
				i_this_cci = np.array(nddf[symbol]['CCI_' + str(cci) + '_0.015'])
				# i_last_cci = np.array(nddf[symbol]['CCI_SHIFT'])
				i_mt_x = np.zeros((a_len,), dtype=float)
				i_sig_all = np.zeros((a_len,), dtype=int)
				# i_swap2 = np.array(range(len(nddf[symbol]["high"])))
				# i_swap3 = np.array(range(len(nddf[symbol]["high"])))

				for i in range(1, len(nddf[symbol]["high"])-1):
					s2()
					if i_this_cci[i] >= 0 and i_this_cci[i-1] < 0:
						i_buffer_up[i] = i_buffer_dn[i-1]
					if i_this_cci[i] <= 0 and i_this_cci[i-1] > 0:
						i_buffer_dn[i] = i_buffer_up[i-1]

					if (i_this_cci[i] >= 0) and (i_buffer_up[i] < i_buffer_up[i-1]):
						i_buffer_up[i] = i_buffer_up[i-1]
					if (i_this_cci[i] < 0) and (i_buffer_dn[i] > i_buffer_dn[i-1]):
						i_buffer_dn[i] = i_buffer_dn[i-1]

						# x = thisCCI >= 0 ?bufferUp: bufferDn
					if i_this_cci[i] >= 0:
						i_mt_x[i] = i_buffer_up[i]
					else:
						i_mt_x[i] = i_buffer_dn[i]

						# swap = x > x[1]?1: x < x[1]?-1: swap[1]
					if i_mt_x[i] > i_mt_x[i-1]:
						i_sig_all[i] = 0
					elif i_mt_x[i] < i_mt_x[i-1]:
						i_sig_all[i] = 1
					else:
						i_sig_all[i] = i_sig_all[i-1]

				nddf[symbol]['MTx'] = i_mt_x
				nddf[symbol]['SIG_ALL_MT'] = i_sig_all

				nddf[symbol]['bufferDn'] = i_buffer_dn
				nddf[symbol]['bufferUp'] = i_buffer_up

				nddf[symbol]['SIG_ALL_MT_sma'] = ta.sma(nddf[symbol]["SIG_ALL_MT"], length=5)

				nddf[symbol]['SIG_MT'] = 4
				nddf[symbol]['SIG_MT'].values[(nddf[symbol]['SIG_ALL_MT_sma'] < .25) & (nddf[symbol]['SIG_ALL_MT'] == 1)] = 1
				nddf[symbol]['SIG_MT'].values[(nddf[symbol]['SIG_ALL_MT_sma'] > .75) & (nddf[symbol]['SIG_ALL_MT'] == 0)] = 0

				ix_remove = ["CCI_" + str(cci) + "_0.015", "CCI_SHIFT", "TRsma_" + str(atr),
							 "bufferDn", "bufferUp", "bufferDn_S", "bufferUp_S",
							 "SIG_ALL_MT_sma", "ATRr_"+str(atr), "TRUERANGE_1", "SIG_ALL_MT_sma"]
				self.remove_columns(symbol, ix_remove)

				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "MA_X":
				nddf[symbol].ta.sma(close=nddf[symbol].ta.ohlc4(), length=5, append=True)
				nddf[symbol].ta.sma(close=nddf[symbol].ta.ohlc4(), length=8, append=True)
				nddf[symbol].ta.sma(close=nddf[symbol].ta.ohlc4(), length=13, append=True)
				nddf[symbol].ta.sma(close=nddf[symbol].ta.ohlc4(), length=26, append=True)
				nddf[symbol].ta.sma(close=nddf[symbol].ta.ohlc4(), length=52, append=True)

				nddf[symbol].ta.ema(close=nddf[symbol].ta.ohlc4(), length=5, append=True)
				nddf[symbol].ta.ema(close=nddf[symbol].ta.ohlc4(), length=8, append=True)
				nddf[symbol].ta.ema(close=nddf[symbol].ta.ohlc4(), length=13, append=True)
				nddf[symbol].ta.ema(close=nddf[symbol].ta.ohlc4(), length=26, append=True)
				nddf[symbol].ta.ema(close=nddf[symbol].ta.ohlc4(), length=52, append=True)

				nddf[symbol]["SMA_5_DIFF"] = (nddf[symbol]["SMA_5"] / nddf[symbol]["SMA_5"].shift(1)) - 1
				nddf[symbol]["SMA_8_DIFF"] = (nddf[symbol]["SMA_8"] / nddf[symbol]["SMA_8"].shift(1)) - 1
				nddf[symbol]["SMA_13_DIFF"] = (nddf[symbol]["SMA_13"] / nddf[symbol]["SMA_13"].shift(1)) - 1
				nddf[symbol]["SMA_26_DIFF"] = (nddf[symbol]["SMA_26"] / nddf[symbol]["SMA_26"].shift(1)) - 1
				nddf[symbol]["SMA_52_DIFF"] = (nddf[symbol]["SMA_52"] / nddf[symbol]["SMA_52"].shift(1)) - 1

				nddf[symbol]["EMA_5_DIFF"] = (nddf[symbol]["EMA_5"] / nddf[symbol]["EMA_5"].shift(1)) - 1
				nddf[symbol]["EMA_8_DIFF"] = (nddf[symbol]["EMA_8"] / nddf[symbol]["EMA_8"].shift(1)) - 1
				nddf[symbol]["EMA_13_DIFF"] = (nddf[symbol]["EMA_13"] / nddf[symbol]["EMA_13"].shift(1)) - 1
				nddf[symbol]["EMA_26_DIFF"] = (nddf[symbol]["EMA_26"] / nddf[symbol]["EMA_26"].shift(1)) - 1
				nddf[symbol]["EMA_52_DIFF"] = (nddf[symbol]["EMA_52"] / nddf[symbol]["EMA_52"].shift(1)) - 1

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
				nddf[symbol]['INDX_SMA5813_SHIFT'] = nddf[symbol]['INDX_SMA5813'] != nddf[symbol]['INDX_SMA5813'].shift(
					1)
				nddf[symbol]['SIG_SMA5813'] = nddf[symbol]['INDX_SMA5813_SHIFT'] * nddf[symbol]['INDX_SMA5813']

				i_remove = ['INDX_SMA5813', 'INDX_SMA5813_SHIFT', 'SIG_SMA5813_LONG_ALL', 'SIG_SMA5813_SHORT_ALL']

				# SIG készítésnél belül 1,2,3,4et használok de sparscategorical cross entropy 0,1,2,3 ér meg ezért el siftelem

				nddf[symbol]["SIG_SMA5813"].values[nddf[symbol]['SIG_SMA5813'] == 0] = 4
				nddf[symbol]["SIG_SMA5813"].values[nddf[symbol]['SIG_SMA5813'] == 1] = 0
				nddf[symbol]["SIG_SMA5813"].values[nddf[symbol]['SIG_SMA5813'] == 2] = 1

				nddf[symbol]["SMA_5_DIFF"] = (nddf[symbol]["SMA_5"] / nddf[symbol]["SMA_5"].shift(1)) - 1
				nddf[symbol]["SMA_8_DIFF"] = (nddf[symbol]["SMA_8"] / nddf[symbol]["SMA_8"].shift(1)) - 1
				nddf[symbol]["SMA_13_DIFF"] = (nddf[symbol]["SMA_13"] / nddf[symbol]["SMA_13"].shift(1)) - 1

				nddf[symbol]["SMA_5_R_OHLC4"] = nddf[symbol]["SMA_5"] / nddf[symbol]["ohlc4"]
				nddf[symbol]["SMA_8_R_OHLC4"] = nddf[symbol]["SMA_8"] / nddf[symbol]["ohlc4"]
				nddf[symbol]["SMA_13_R_OHLC4"] = nddf[symbol]["SMA_13"] / nddf[symbol]["ohlc4"]

				self.remove_columns(symbol, i_remove)
				self.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "RSI14":
				nddf[symbol].ta.rsi(append=True)
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "ICHIMOKU":
				nddf[symbol].ta.ichimoku(append=True)
				self.case_set_back(symbol)

				nddf[symbol]["conv_over_base"] = nddf[symbol]["ITS_9"] > nddf[symbol]["IKS_26"]
				nddf[symbol]["conv_under_base"] = nddf[symbol]["ITS_9"] < nddf[symbol]["IKS_26"]
				nddf[symbol]["cloud_top"] = nddf[symbol][['ISA_9', 'ISB_26']].max(axis=1)
				nddf[symbol]["cloud_bottom"] = nddf[symbol][['ISA_9', 'ISB_26']].min(axis=1)
				nddf[symbol]["ohlc4_over_cloud"] = nddf[symbol]["ohlc4"] > nddf[symbol]["cloud_top"]
				nddf[symbol]["ohlc4_under_cloud"] = nddf[symbol]["ohlc4"] < nddf[symbol]["cloud_bottom"]

				# TODO: lagging linét megcsinálni, hogy a 26 percel előbbi állapotot nézze
				nddf[symbol]["lagging_over_cloud"] = nddf[symbol]["ICS_26"] > nddf[symbol]["cloud_top"]
				nddf[symbol]["lagging_under_cloud"] = nddf[symbol]["ICS_26"] < nddf[symbol]["cloud_bottom"]

				# print(nddf[symbol]["Date"], nddf[symbol]["Date"].shift(26))

				# LONG SIGNALS -----------------------------------------------------------------
				# A szignálokat csak intime ban csinálom meg
				nddf[symbol]["SIG_ICHI_LONG_ALL"] = nddf[symbol]["conv_over_base"] \
													& nddf[symbol]["ohlc4_over_cloud"] \
													& nddf[symbol]["lagging_over_cloud"]

				nddf[symbol]['SIG_ICHI_LONG_ALL_SHIFT'] = nddf[symbol]['SIG_ICHI_LONG_ALL'] != nddf[symbol][
					'SIG_ICHI_LONG_ALL'].shift(1)
				nddf[symbol]['SIG_ICHI_LONG_FIRST'] = nddf[symbol]['SIG_ICHI_LONG_ALL_SHIFT'] & nddf[symbol][
					'SIG_ICHI_LONG_ALL']

				# SHORT SIGNALS -----------------------------------------------------------------
				nddf[symbol]["SIG_ICHI_SHORT_ALL"] = nddf[symbol]["conv_under_base"] \
													 & nddf[symbol]["ohlc4_under_cloud"] \
													 & nddf[symbol]["lagging_under_cloud"]

				nddf[symbol]['SIG_ICHI_SHORT_ALL_SHIFT'] = nddf[symbol]['SIG_ICHI_SHORT_ALL'] != nddf[symbol][
					'SIG_ICHI_SHORT_ALL'].shift(1)
				nddf[symbol]['SIG_ICHI_SHORT_FIRST'] = nddf[symbol]['SIG_ICHI_SHORT_ALL_SHIFT'] & nddf[symbol][
					'SIG_ICHI_SHORT_ALL']

				nddf[symbol]['SIG_ICHIMOKU'] = 4
				nddf[symbol]['SIG_ICHIMOKU'].values[nddf[symbol]['SIG_ICHI_LONG_FIRST']] = 0
				nddf[symbol]['SIG_ICHIMOKU'].values[nddf[symbol]['SIG_ICHI_SHORT_FIRST']] = 1

				nddf[symbol].set_index('Date', inplace=True)
				mask = nddf[symbol].between_time('21:30', '16:00').index
				nddf[symbol].loc[mask, 'SIG_ICHIMOKU'] = 4

				i_remove = [
					'conv_over_base', 'conv_under_base',
					'cloud_top', 'cloud_bottom',
					'ohlc4_over_cloud', 'ohlc4_under_cloud',
					'lagging_over_cloud', 'lagging_under_cloud',
					'SIG_ICHI_LONG_ALL', 'SIG_ICHI_LONG_ALL_SHIFT', 'SIG_ICHI_LONG_FIRST',
					'SIG_ICHI_SHORT_ALL', 'SIG_ICHI_SHORT_ALL_SHIFT', 'SIG_ICHI_SHORT_FIRST'
				]
				self.remove_columns(symbol, i_remove)

				ndf.set_dt_order(symbol)
				nddb.write(symbol)

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

			elif tech_indicator == "VWAP":
				nddf[symbol].set_index(pd.DatetimeIndex(nddf[symbol]["Date"]), inplace=True, verify_integrity=True)
				nddf[symbol].ta.vwap(append=True)
				nddf[symbol].reset_index(drop=True, inplace=True)
				nddf[symbol]["VWAP_D_R_OHLC4"] = nddf[symbol]["VWAP_D"] / nddf[symbol]["ohlc4"]
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "GAM":
				log("GAM")

				np_date = nddf[symbol]["Date"]
				np_low = nddf[symbol]["Low"]
				np_high = nddf[symbol]["High"]

				rounds = 5
				results = np.zeros((len(np_high), rounds))
				y = np.zeros(len(np_high))

				steps = 10
				stock_size = 10000
				min_profit = 50

				s2(True, len(np_high) * (rounds + 1) - 10)

				for r in range(rounds):
					for i in range(nddf[symbol].shape[0] - steps - 1):
						s2()
						if 16 < np_date[i].hour < 21 and np.is_busday(np_date[i].date()) and \
								16 < np_date[i + steps + 1].hour < 21 and np.is_busday(np_date[i + steps + 1].date()):
							next_low = np_low[i + 1]
							next_high = np_high[i + 1]

							next_steps_low = np_low[i + steps + 1]
							next_steps_high = np_high[i + steps + 1]

							next_rnd = next_low + (((next_high - next_low) / 100) * random.randint(0, 101))
							next_steps_rnd = next_steps_low + (
										((next_steps_high - next_steps_low) / 100) * random.randint(0, 101))
							profit = int(stock_size / next_rnd) * (next_steps_rnd - next_rnd)
							results[i, r] = profit

				for x, res in enumerate(results):
					s2()
					if res.sum() == 0:
						yy = 4
					elif res.max() < 0 and res.min() < -min_profit:
						yy = 1
					elif res.min() > 0 and res.max() > min_profit:
						yy = 0
					else:
						yy = 2

					y[x] = yy

				nddf[symbol]['y_GAM'] = y
				nddf[symbol]['y_GAM'] = nddf[symbol]['y_GAM'].astype(int)
				nddf[symbol]['SIG_GAM'] = nddf[symbol]['y_GAM']
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "P10":

				def prob_profit(low_np, high_np):

					# def lh_steps(low, high):
					# 	return int(round(round(high, 2) - round(low, 2), 2) * 100) + 1
					#
					# time_window_size = len(low_np)
					# base_low = low_np[0]
					# base_high = high_np[0]
					# base_steps = lh_steps(base_low, base_high)
					stock_size = 10000
					all_step_profit_reward = 1.25
					# results = {}
					# for t in range(1, time_window_size):
					# 	next_low = low_np[t]
					# 	next_high = high_np[t]
					# 	next_steps = lh_steps(next_low, next_high)
					# 	for bs in range(base_steps):
					# 		for ns in range(next_steps):
					# 			qt = int(stock_size / round(base_low + bs * .01, 2))
					# 			profit = int(qt * (round(next_low + ns * .01, 2) - round(base_low + bs * .01, 2)))
					# 			if profit not in results:
					# 				results[profit] = 1
					# 			else:
					# 				results[profit] += 1
					# # print(results)
					# # print(sorted(results.items(), key=lambda x: x[1]))

					time_window_size = len(low_np)

					def n_arange(low, high, steps):

						steps_int = int(steps * 100)
						low_int = int(low * 100)
						high_int = int(high * 100) + steps_int

						int_arange = np.array(list(range(low_int, high_int, steps_int)))
						int_arange = int_arange / 100
						return int_arange

					base_array = n_arange(low_np[0], high_np[0], .01)
					b_lh_dist = len(base_array)
					bases = np.array([])
					nexts = np.array([])
					for x in range(time_window_size - 1):
						next_arange = n_arange(low_np[x + 1], high_np[x + 1], 0.01)
						n_lh_dist = len(next_arange)
						brep = np.repeat(base_array, n_lh_dist)
						bases = np.append([bases], [brep], axis=1)[0]
						lh_range = np.tile(next_arange, b_lh_dist)
						nexts = np.append([nexts], [lh_range], axis=1)[0]

					qt = stock_size / bases
					qt = qt.astype(int)

					profit = (nexts - bases) * qt
					profit = profit.astype(int)
					unique_profit = np.unique(profit, return_counts=True)
					r_keys = np.array(unique_profit[0])
					r_values = np.array(unique_profit[1])
					# print(r_keys)
					# print(r_values)

					# r_keys = np.array(list(results.keys()))
					# r_values = np.array(list(results.values()))
					m_key_value = r_keys * r_values

					wsum_profit = m_key_value.sum()
					min_profit = min(r_keys)
					max_profit = max(r_keys)
					sum_case = sum(r_values)
					prob_profit = int(wsum_profit / sum_case)
					# for r in results:
					# 	# print(r, results[r] )
					# 	sum_profit += r
					# 	sum_case += results[r]
					# # print("sum:", sum_profit, sum_case)

					# prob_profit = int(wsum_profit / sum_case * all_step_profit_reward)

					# if (prob_profit > 0 and max_profit >= 50) or (prob_profit < 0 and min_profit <= -50):
					# 	prob_profit = int(wsum_profit / sum_case * all_step_profit_reward)
					# else:
					# 	prob_profit = 0
					return prob_profit

				time_frame = 10
				date_s = nddf[symbol]["Date"]
				low_s = np.array(nddf[symbol]["Low"])
				high_s = np.array(nddf[symbol]["High"])

				s2(True, len(low_s) - time_frame - 1)

				r_array = np.zeros(len(low_s))
				for g in range(0, len(low_s) - time_frame - 1):
				# for g in range(0, 1000):
					s2()
					if 16 <= date_s[g].hour <= 19 and np.is_busday(date_s[g].date()):
						low_np = low_s[g: g + time_frame]
						high_np = high_s[g: g + time_frame]
						pr = prob_profit(low_np, high_np)
						r_array[g] = pr
				nddf[symbol]["y_P10"] = 4
				nddf[symbol]["SIG_P10"] = r_array
				nddf[symbol]['SIG_P10'] = nddf[symbol]['SIG_P10'].astype(int)

				sig_limit_bottom = 25
				sig_limit_top = 55

				# nddf[symbol]["y_P10"].values[(nddf[symbol]["SIG_P10"] > sig_limit_bottom) & (nddf[symbol]["SIG_P10"] < sig_limit_top)] = 0
				# nddf[symbol]["y_P10"].values[(0 < nddf[symbol]["SIG_P10"]) & (nddf[symbol]["SIG_P10"] <= sig_limit_bottom)] = 2
				# nddf[symbol]["y_P10"].values[(nddf[symbol]["SIG_P10"] < -sig_limit_bottom) & (nddf[symbol]["SIG_P10"] > -sig_limit_top)] = 1
				# nddf[symbol]["y_P10"].values[(0 > nddf[symbol]["SIG_P10"]) & (nddf[symbol]["SIG_P10"] >= -sig_limit_bottom)] = 3
				# nddf[symbol]["y_P10"].values[nddf[symbol]["SIG_P10"] == 0] = 4

				nddf[symbol]["y_P10"].values[(nddf[symbol]["SIG_P10"] > sig_limit_bottom) & (nddf[symbol]["SIG_P10"] < sig_limit_top)] = 0
				nddf[symbol]["y_P10"].values[(nddf[symbol]["SIG_P10"] < -sig_limit_bottom) & (nddf[symbol]["SIG_P10"] > -sig_limit_top)] = 1
				nddf[symbol]["y_P10"].values[(-15 < nddf[symbol]["SIG_P10"]) & (nddf[symbol]["SIG_P10"] < 15)] = 2
				nddf[symbol]["y_P10"].values[nddf[symbol]["SIG_P10"] == 0] = 4

				# get first

				# nddf[symbol]['y_P10_SHIFT'] = nddf[symbol]['y_P10'] != nddf[symbol]['y_P10'].shift(1)

				nddf[symbol].set_index('Date', inplace=True)
				mask = nddf[symbol].between_time('19:00', '16:00').index
				nddf[symbol].loc[mask, 'y_P10'] = 4
				nddf[symbol].loc[nddf[symbol].tail(90000).index, 'y_P10'] = 4

				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "P10INT":

				def get_slice_index(xlen, parts, slice_no):
					slices = np.array_split(list(np.arange(0, xlen)), parts)
					start = slices[slice_no][0]
					end = slices[slice_no][-1:][0]
					end += 1
					end = min(end, xlen)
					return start, end

				params = str(params[1:-1]).split(',')
				if len(params) != 3:
					params = [.4, .55, 10]

				# self.remove_columns(symbol, ['SIG_P10INT', 'y_P10INT'])

				profit_limit = float(params[0]) / 100
				prob_limit = float(params[1]) / 100
				time_frame = int(params[2])  ## hán perces idő intervallumot figyel előre
				log("  Settings: profit limit: " + str(profit_limit * 100) + "%,   Prob. limit: " +
					str(round(prob_limit * 100, 2)) + "%   Time frame: " + str(time_frame))
				full_time_traded_istrument = True  # kriptókhoz
				price_slices = 10  # ezt majd le kell kérni a részvény adataiból
				log("  Price slices: " + str(price_slices))

				used_cores = cpu_count()
				mp_params = []

				runing_processes = [None] * used_cores
				log(f"  Creating multiprocessing objects (params). ")
				for x in range(used_cores):
					x_from = get_slice_index(nddf[symbol].shape[0], used_cores, x)[0]
					x_to = get_slice_index(nddf[symbol].shape[0], used_cores, x)[1]
					# print(x_from, x_to)

					# np.save("BTCUSDT_Date", np.array(nddf[symbol]["Date"]))
					# np.save("BTCUSDT_Low", np.array(nddf[symbol]["Low"]))
					# np.save("BTCUSDT_High", np.array(nddf[symbol]["High"]))

					date_s = nddf[symbol]["Date"][x_from:x_to]
					low_s = np.array(nddf[symbol]["Low"])[x_from:x_to]
					high_s = np.array(nddf[symbol]["High"])[x_from:x_to]

					params = {'cores': used_cores,
							  'process': x,
							  'profit_limit': profit_limit,
							  'prob_limit': prob_limit,
							  'time_frame': time_frame,
							  'price_slices': price_slices,
							  'date_s_slice': date_s,
							  'low_s_slice': low_s,
							  'high_s_slice': high_s}

					# mp_params.append([used_cores, x + 1, params])

					runing_processes[x] = Process(target=mp_tech, args=(params,))

				for x, prc in enumerate(runing_processes):
					prc.start()
					log(f"  P10INT start process: {x + 1} ")
					# soft start for processor cooler sincronize
					if x == 3:
						time.sleep(15)
					else:
						time.sleep(3)

				for prc in runing_processes:
					prc.join()

				# xpool = Pool(used_cores)
				# res = xpool.map(mp_tech, mp_params)
				res_arra = []
				for ic in range(used_cores):
					file_name = self.temp_path + 'P10INT_MP_RESULT' + str(ic) + '.npy'
					res_arra.append(np.load(file_name))
				afr = np.concatenate(res_arra)

				## megszüntetem a GAPOKAT amelyek a szétszeletelés miatt keletkeznek
				afr_index = np.where(afr[:-(time_frame + 1)] == 9)[0]

				low_g = np.array(nddf[symbol]["Low"])
				high_g = np.array(nddf[symbol]["High"])
				for g in afr_index:
					low_np = low_g[g: g + time_frame]
					high_np = high_g[g: g + time_frame]
					pr = mp_tech.prob_profit(low_np, high_np, price_slices, profit_limit, prob_limit)
					afr[g] = pr

				# print(len(afr), nddf[symbol].shape[0])

				log("Result: ")
				log("  0 = Under limit: " + str(np.count_nonzero(afr == 0)))
				log("  1 = Long over limit: " + str(np.count_nonzero(afr == 1)))
				log("  2 = Shor over limit: " + str(np.count_nonzero(afr == 2)))
				log("  9 = GAP: " + str(np.count_nonzero(afr == 9)))
				log("  10 = dataset contains nan: " + str(np.count_nonzero(afr == 11)))

				nddf[symbol]["SIG_P10INT"] = afr
				nddf[symbol]['SIG_P10INT'] = nddf[symbol]['SIG_P10INT'].astype(int)
				nddf[symbol]["y_P10INT"] = nddf[symbol]["SIG_P10INT"]
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "P10INT_1C":
				params = str(params[1:-1]).split(',')
				if len(params) != 3:
					params = [.9, 60, 15]

				self.remove_columns(symbol, ['SIG_P10INT', 'y_P10INT'])

				def prob_profit(low_np, high_np, tick_size, profit_limit, prob_limit):
					# print("5")
					time_frame = low_np.shape[0]
					all_start = np.array([])
					all_exit = np.array([])
					# s2(True, len(low_s) - time_frame - 1)
					all_caes = 0
					for tf in range(time_frame - 1):
						if low_np[0] == high_np[0]:
							base_array_with_steps = np.array([low_np[0]])
						else:
							base_array_with_steps = np.arange(low_np[0], high_np[0], tick_size)
							if base_array_with_steps[-1] != high_np[0]:
								base_array_with_steps = np.append(base_array_with_steps, high_np[0])
						for bs in base_array_with_steps:  # ts = time slices
							if low_np[tf + 1] == high_np[tf + 1]:
								next_array_with_steps = np.array([low_np[tf + 1]])
							else:
								# print(low_np[tf + 1], high_np[tf + 1])
								next_array_with_steps = np.arange(low_np[tf + 1], high_np[tf + 1], tick_size)
								if next_array_with_steps[-1] != high_np[tf + 1]:
									next_array_with_steps = np.append(next_array_with_steps, high_np[tf + 1])
							len_naws = next_array_with_steps.shape[0]
							# print(len_naws)
							same_size_base = np.full(len_naws, bs)
							all_start = np.append(all_start, same_size_base)
							all_exit = np.append(all_exit, next_array_with_steps)
							all_caes += same_size_base.shape[0]

					# print(all_exit.shape)
					if_long = (all_exit / all_start) - 1
					if_short = (all_start / all_exit) - 1

					prob_long_over_limit = np.count_nonzero(if_long > profit_limit) / all_caes
					prob_short_over_limit = np.count_nonzero(if_short > profit_limit) / all_caes

					if prob_long_over_limit > prob_limit:
						i_ret = 1
					elif prob_short_over_limit > prob_limit:
						i_ret = 2
					else:
						i_ret = 0

					return i_ret

				profit_limit = float(params[0]) / 100
				prob_limit = float(params[1]) / 100
				time_frame = int(params[2])  ## hán perces idő intervallumot figyel előre
				log("  Settings: profit limit: " + str(profit_limit * 100) + "%,   Prob. limit: " +
					str(round(prob_limit * 100, 2)) + "%   Time frame: " + str(time_frame))
				full_time_traded_istrument = True  # kriptókhoz
				if symbol in nbt.crypto:
					tick_size = float(nbt.pai[symbol]['tick_size'])
					if nddf[symbol]["ohlc4"][0] > 10000:  # BTCUSDT .01 a tick size de 2-5 van a low and a high között túl sok lenne a esetek száma
						tick_size = float(10)
					else:
						tick_size = float(nbt.pai[symbol]['tick_size'])
				else:
					tick_size = float(0.1)  # ezt majd le kell kérni a részvény adataiból
				log("  Tick size: " + str(tick_size))
				date_s = nddf[symbol]["Date"]
				low_s = np.array(nddf[symbol]["Low"])
				high_s = np.array(nddf[symbol]["High"])

				log_run_len = len(low_s) - time_frame - 1

				s2(True, log_run_len)
				# print("2")
				r_array = np.zeros(len(low_s))  #
				for g in range(0, len(low_s) - time_frame - 1):  ## végigmegyek a low vektoron minus time frame
					# print("3")
					s2(text="".join([str(log_run_len), "/", str(g)]))
					if (16 <= date_s[g].hour <= 20 and np.is_busday(date_s[g].date())) or full_time_traded_istrument: # nézem akereskedési időt és a munkanapot
						low_np = low_s[g: g + time_frame]
						high_np = high_s[g: g + time_frame]
						pr = prob_profit(low_np, high_np, tick_size, profit_limit, prob_limit)
						r_array[g] = pr

					if g % 5000 == 0 and g != 0:
						uar1 = np.unique(np.array(r_array), return_counts=True)[1][1]
						uar2 = np.unique(np.array(r_array), return_counts=True)[1][2]
						uar_pred1 = int(len(low_s) / g * uar1)
						uar_pred2 = int(len(low_s) / g * uar2)
						log(f"  {g}->   1: now: {uar1} / predict: {uar_pred1}      2: now: {uar2} / predict: {uar_pred2}")

				log("Result: ")
				log("  0 = Under limit: " + str(np.count_nonzero(r_array == 0)))
				log("  1 = Long over limit: " + str(np.count_nonzero(r_array == 1)))
				log("  2 = Shor over limit: " + str(np.count_nonzero(r_array == 2)))

				nddf[symbol]["SIG_P10INT"] = r_array
				nddf[symbol]['SIG_P10INT'] = nddf[symbol]['SIG_P10INT'].astype(int)
				nddf[symbol]["y_P10INT"] = nddf[symbol]["SIG_P10INT"]
				nddf[symbol].set_index('Date', inplace=True)
				# mask = nddf[symbol].between_time('20:00', '16:00').index
				# nddf[symbol].loc[mask, 'y_P10INT'] = -1000

				ndf.set_dt_order(symbol)
				nddb.write(symbol)



			elif tech_indicator == "P10INT_ORIG":

				def prob_profit(low_np, high_np):

					stock_size = 10000
					time_window_size = len(low_np)

					def n_arange(low, high, steps):
						steps_int = int(steps * 100)
						low_int = int(low * 100)
						high_int = int(high * 100) + steps_int

						int_arange = np.array(list(range(low_int, high_int, steps_int)))
						int_arange = int_arange / 100
						return int_arange

					base_array = n_arange(low_np[0], high_np[0], .00001)
					b_lh_dist = len(base_array)
					bases = np.array([])
					nexts = np.array([])
					for x in range(time_window_size - 1):
						next_arange = n_arange(low_np[x + 1], high_np[x + 1], 0.01)
						n_lh_dist = len(next_arange)
						brep = np.repeat(base_array, n_lh_dist)
						bases = np.append([bases], [brep], axis=1)[0]
						lh_range = np.tile(next_arange, b_lh_dist)
						nexts = np.append([nexts], [lh_range], axis=1)[0]

					qt = stock_size / bases
					qt = qt.astype(int)

					profit = (nexts - bases) * qt
					profit = profit.astype(int)
					unique_profit = np.unique(profit, return_counts=True)
					r_keys = np.array(unique_profit[0])
					r_values = np.array(unique_profit[1])
					m_key_value = r_keys * r_values

					wsum_profit = m_key_value.sum()
					sum_case = sum(r_values)
					prob_profit = int(wsum_profit / sum_case)
					return prob_profit

				time_frame = 10  ## hán perces idő intervallumot figyel előre
				full_time_traded_istrument = True
				date_s = nddf[symbol]["Date"]
				low_s = np.array(nddf[symbol]["Low"])
				high_s = np.array(nddf[symbol]["High"])

				s2(True, len(low_s) - time_frame - 1)

				r_array = np.zeros(len(low_s))
				for g in range(0, len(low_s) - time_frame - 1):  ## végigmegyek a low vektoron minus time frame
					s2()
					if (16 <= date_s[g].hour <= 20 and np.is_busday(
							date_s[g].date())) or full_time_traded_istrument:  # nézem akereskedési időt és a munkanapot
						low_np = low_s[g: g + time_frame]
						high_np = high_s[g: g + time_frame]
						pr = prob_profit(low_np, high_np)
						r_array[g] = pr

				nddf[symbol]["SIG_P10INT"] = r_array
				nddf[symbol]['SIG_P10INT'] = nddf[symbol]['SIG_P10INT'].astype(int)
				nddf[symbol]["y_P10INT"] = nddf[symbol]["SIG_P10INT"]

				## SIG_P10INT és a y_P10INT is nullával van feltöltve

				nddf[symbol]["y_P10INT"].values[
					(50 < nddf[symbol]["SIG_P10INT"]) | (nddf[symbol]["SIG_P10INT"] < -50)] = -1050
				nddf[symbol]["y_P10INT"] = nddf[symbol]["y_P10INT"] + 50

				## minden ami -50 és +50 en kívül van -1000 kap
				## a többi 50 növekszik

				nddf[symbol].set_index('Date', inplace=True)
				# mask = nddf[symbol].between_time('20:00', '16:00').index
				# nddf[symbol].loc[mask, 'y_P10INT'] = -1000

				ndf.set_dt_order(symbol)
				nddb.write(symbol)



			elif tech_indicator == "GAM2":
				log("GAM2")

				np_date = nddf[symbol]["Date"]
				np_low = nddf[symbol]["Low"]
				np_high = nddf[symbol]["High"]

				rounds = 5
				results = np.zeros((len(np_high), rounds))
				y = np.zeros(len(np_high))

				steps = 10
				stock_size = 10000
				min_profit = 50

				s2(True, (len(np_high)-1) * (rounds + 1) - 10)

				for r in range(rounds):
					for i in range(nddf[symbol].shape[0] - steps - 1):
						s2()
						if 16 < np_date[i].hour < 21 and np.is_busday(np_date[i].date()) and \
								16 < np_date[i + steps + 1].hour < 21 and np.is_busday(np_date[i + steps + 1].date()):
							steps_results = np.zeros(steps)
							next_low = np_low[i + 1]
							next_high = np_high[i + 1]
							for stp in range(steps):
								next_steps_low = np_low[i + (stp + 1) + 1]  # mindik a következőtől számolom ezért +1
								next_steps_high = np_high[i + (stp + 1) + 1]

								next_rnd = next_low + (((next_high - next_low) / 100) * random.randint(0, 101))
								next_steps_rnd = next_steps_low + (((next_steps_high - next_steps_low) / 100) * random.randint(0, 101))
								profit = int(stock_size / next_rnd) * (next_steps_rnd - next_rnd)
								steps_results[stp] = int(profit)
							sr_max = steps_results.max()
							sr_min = steps_results.min()
							# print(sr_min, sr_max)
							if abs(sr_min) > abs(sr_max):  # az a profit amelyik irányba jobban eltér a nullától short or long profit
								profit = sr_min
							else:
								profit = sr_max
							# print(sr_min, sr_max, profit)
							results[i, r] = profit
							# print(results)

				for x, res in enumerate(results):
					s2()
					# print(res)
					if res.sum() == 0:
						yy = 4
					elif res.max() < 0 and res.min() < -min_profit:
						yy = 1
					elif res.min() > 0 and res.max() > min_profit:
						yy = 0
					else:
						yy = 2

					y[x] = yy

				nddf[symbol]['y_GAM2'] = y
				nddf[symbol]['y_GAM2'] = nddf[symbol]['y_GAM2'].astype(int)
				nddf[symbol]['SIG_GAM2'] = nddf[symbol]['y_GAM2']
				ndf.set_dt_order(symbol)
				nddb.write(symbol)

			elif tech_indicator == "BREAKOUT":
				nddf[symbol]['SIG_BREAKOUT'] = 0
				ndf.vector_qualify(symbol,
								   sig_suffix="BREAKOUT",
								   stock_size=10000,
								   min_profit=100,
								   min_step_profit=5,
								   stop=-8,
								   steps=30,
								   overlay_steps=30,
								   overlay_manager="full")

				nddf[symbol]['y_BREAKOUT'].values[nddf[symbol]['y_BREAKOUT'] == 0] = 5

				nddf[symbol]['y_BREAKOUT_SHIFT'] = nddf[symbol]['y_BREAKOUT'] != nddf[symbol]['y_BREAKOUT'].shift(1)
				nddf[symbol]['y_BREAKOUT'] = nddf[symbol]['y_BREAKOUT_SHIFT'] * nddf[symbol]['y_BREAKOUT']

				nddf[symbol]['y_BREAKOUT_TEMPX'] = 4
				nddf[symbol]['y_BREAKOUT_TEMPX'].values[nddf[symbol]['y_BREAKOUT'] == 5] = 0

				nddf[symbol]['SIG_BREAKOUT'] = 1
				ndf.vector_qualify(symbol,
								   sig_suffix="BREAKOUT",
								   stock_size=10000,
								   min_profit=100,
								   min_step_profit=5,
								   stop=-8,
								   steps=30,
								   overlay_steps=30,
								   overlay_manager="full")

				nddf[symbol]['y_BREAKOUT_SHIFT'] = nddf[symbol]['y_BREAKOUT'] != nddf[symbol]['y_BREAKOUT'].shift(1)
				nddf[symbol]['y_BREAKOUT'] = nddf[symbol]['y_BREAKOUT_SHIFT'] * nddf[symbol]['y_BREAKOUT']
				nddf[symbol]['y_BREAKOUT_TEMPX'].values[nddf[symbol]['y_BREAKOUT'] == 1] = 1

				nddf[symbol]['SIG_BREAKOUT'] = nddf[symbol]['y_BREAKOUT_TEMPX']

				i_remove = ['y_BREAKOUT_TEMPX', 'y_BREAKOUT_SHIFT', 'y_BREAKOUT']
				self.remove_columns(symbol, i_remove)

				steps = 30
				profit_window_shift = 0

				ix_remove = []
				pnl_first_calc_position = 1
				for i_dif in range(1, steps + 1):
					c_name = "XX" + str(i_dif)
					# print(c_name)
					ix_remove.append(c_name)
					nddf[symbol][c_name] = ((nddf[symbol].ohlc4.shift(-(i_dif + profit_window_shift)) /
											 nddf[symbol].ohlc4.shift(-profit_window_shift)) - 1) * 100

				i_pos_first = nddf[symbol].columns.get_loc("XX" + str(pnl_first_calc_position))
				i_ser = list(range(i_pos_first, i_pos_first + steps))

				nddf[symbol]["XXMAX"] = nddf[symbol].iloc[:, i_ser].max(axis=1).abs()
				nddf[symbol]["XXMIN"] = nddf[symbol].iloc[:, i_ser].min(axis=1).abs()

				raft_limit = .5
				nddf[symbol]["NON_TREND"] = (nddf[symbol]["XXMAX"] < raft_limit) & (nddf[symbol]["XXMIN"] < raft_limit)

				# nddf[symbol]['NON_TREND_SHIFT'] = nddf[symbol]['NON_TREND'] != nddf[symbol]['NON_TREND'].shift(1)
				# nddf[symbol]['NON_TREND'] = nddf[symbol]['NON_TREND_SHIFT'] & nddf[symbol]['NON_TREND']

				nddf[symbol]['SIG_BREAKOUT'].values[nddf[symbol]['NON_TREND'] & (nddf[symbol]['SIG_BREAKOUT'] == 4)] = 5
				nddf[symbol]['XXRND'] = np.random.randint(2, size=nddf[symbol].shape[0])
				nddf[symbol]['SIG_BREAKOUT'].values[
					(nddf[symbol]['XXRND'] == 0) & (nddf[symbol]['SIG_BREAKOUT'] == 5)] = 0
				nddf[symbol]['SIG_BREAKOUT'].values[
					(nddf[symbol]['XXRND'] == 1) & (nddf[symbol]['SIG_BREAKOUT'] == 5)] = 1

				ix_remove = ['XXMAX', "XXMIN", "NON_TREND", "NON_TREND_SHIFT",
								 "XXRND", "XMAX", "XMIN", "XMINS", "XMAXS", "XMINL", "XMAXL"]
				self.remove_columns(symbol, ix_remove)

				nddf[symbol].set_index('Date', inplace=True)
				mask = nddf[symbol].between_time('21:30', '16:00').index
				nddf[symbol].loc[mask, 'SIG_BREAKOUT'] = 4

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
		nddb.remove(symbol)
		ndf_meta.remove_meta(symbol)

	def refresh(self, symbol, log_visible=True):
		log("ndf-> refresh " + symbol, visible=log_visible)
		log("Time frame (before refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(
			nddf[symbol]["Date"].max()), visible=log_visible)
		num_of_rows_before = nddf[symbol].shape[0]
		log("Number of rows (before refresh): " + str(num_of_rows_before), visible=log_visible)
		to_dbdt = datetime.now() + timedelta(days=1)
		to_dbdt = to_dbdt.strftime('%Y-%m-%d %H:%M:%S')
		# print("to", to_dbdt)
		from_dbdt = str(nddf[symbol]["Date"].max())
		# print("from", from_dbdt)
		i_tounix = n_tools.dbdt_to_unixdt(to_dbdt)
		i_fromunix = n_tools.dbdt_to_unixdt(from_dbdt)
		i_res = md.get_stock_candles(symbol, "1", i_fromunix, i_tounix, True, log_visible)
		# print(i_res)

		# fast check result
		i_array1 = np.array(i_res["Date"])
		i_array2 = np.array(nddf[symbol]["Date"][-200:])
		if len(i_array1) != sum(np.isin(i_array1, i_array2)):
			nddf[symbol] = nddf[symbol].append(i_res)
			# print(nddf[symbol].shape)
			self.set_dt_order(symbol)
			# print(nddf[symbol].shape)
			num_of_rows_after = nddf[symbol].shape[0]
			log("Time frame (after refresh): " + str(nddf[symbol]["Date"].min()) + " - " + str(
				nddf[symbol]["Date"].max()), visible=log_visible)
			log("Number of rows (after refresh): " + str(num_of_rows_after), visible=log_visible)
			nddb.write(symbol, log_visible=False)
			return num_of_rows_after - num_of_rows_before
		else:
			log("There is no new data from: " + from_dbdt, visible=log_visible)
			return 0

	def remove_columns(self, symbol, columns):
		for i_c in columns:
			if i_c in tuple(nddf[symbol].columns):
				nddf[symbol] = nddf[symbol].drop(i_c, axis=1, errors='ignore')


class watch_list:

	def __init__(self):
		self.wl_df = self.read()

	# self.refresh_sentiment()

	def read(self):
		i_df = pd.read_csv('wl.csv', sep=';')
		return i_df

	def write(self):
		self.wl_df.to_csv('wl.csv', sep=';', index=False)
		self.wl_df = self.read()
		return

	def refresh_profile(self, symbol="none"):
		for index, row in self.wl_df.iterrows():
			i_symbol = row['symbol']
			if symbol == i_symbol or symbol == "none":
				i_company_profile = md.company_profile(i_symbol)
				if len(i_company_profile.keys()) == 0:
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'name'] = i_symbol
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'profil'] = i_symbol
				else:
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'name'] = i_company_profile['name']
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'profil'] = "Web: " + i_company_profile['weburl']
		self.write()
		return

	def refresh_sentiment(self, symbol="none"):
		for index, row in self.wl_df.iterrows():
			i_symbol = row['symbol']
			if symbol == i_symbol or symbol == "none":
				i_news_sentiment = md.news_sentiment(i_symbol)
				if i_news_sentiment['sentiment']:
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'snt_bearish'] = i_news_sentiment['sentiment'][
						'bearishPercent']
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'snt_bullish'] = i_news_sentiment['sentiment'][
						'bullishPercent']
				else:
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'snt_bearish'] = 0
					self.wl_df.loc[self.wl_df['symbol'] == i_symbol, 'snt_bullish'] = 0
		self.write()
		return

	def add(self, symbol, years=3):
		self.remove(symbol)
		new_row = {'symbol': symbol}
		# print(new_row)
		self.wl_df = self.wl_df.append(new_row, ignore_index=True)
		self.refresh_profile(symbol)
		# self.refresh_sentiment(symbol)
		self.wl_df.loc[self.wl_df['symbol'] == symbol, 'ai_project1'] = ""
		self.write()
		gui.refresh_ui()
		ndf.add(symbol, years)
		return

	def add_crypto(self, symbol, years=3):
		if symbol in nbt.crypto:
			self.remove(symbol)
			new_row = {'symbol': symbol}
			self.wl_df = self.wl_df.append(new_row, ignore_index=True)
			self.wl_df.loc[self.wl_df['symbol'] == symbol, 'ai_project1'] = ""
			self.wl_df.loc[self.wl_df['symbol'] == symbol, 'name'] = "-"
			self.wl_df.loc[self.wl_df['symbol'] == symbol, 'profil'] = "-"
			self.wl_df.loc[self.wl_df['symbol'] == symbol, 'snt_bearish'] = 0
			self.wl_df.loc[self.wl_df['symbol'] == symbol, 'snt_bullish'] = 0
			self.write()
			gui.refresh_ui()
			ndf.add_crypto_multi2(symbol, years)
		else:
			log(symbol + " - non listed symbol on Binance.")
		return

	def remove(self, symbol):
		self.wl_df.drop(self.wl_df.loc[self.wl_df['symbol'] == symbol].index, inplace=True)
		self.write()
		return

# def add_ai_project(self, symbol, project):
#     self.wl_df.loc[self.wl_df['symbol'] == symbol, 'ai_project1'] = project
#     self.wl_df['ai_project1'] = self.wl_df['ai_project1'].fillna("-")
#     print(self.wl_df)
#     self.write()
#     return


# PROGRAMS ----------------------------------------------------------------------------


def help2():
	gui.print_command()


def do(symbol="", p2="", p3=""):

	ai_clibrate_mp("BTCUSDT", 270000, "BTCUSDT_P10INT", 1800000)



def do2(symbol="", p2="", p3=""):
	def get_dataset_by_index(symbol, index, time_window_size, original_fields,
							 contras, contra_copies_dt, nddf):

		i_int_to = int(index)
		i_int_from = i_int_to - time_window_size + 1
		# print(nddf[symbol]["Date"][i_int_to:i_int_to + 1])
		# sys.exit(0)

		i_data_array = np.array([])
		if i_int_from > 0:
			if len(original_fields) > 0:
				for i_of in original_fields:
					i_add = np.array(nddf[symbol][i_of][i_int_from:i_int_to + 1])
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

					orig_date = nddf[symbol]["Date"][index:index + 1].values[0]
					try:
						i_int_to_contra = np.where(contra_copies_dt[con_symbol] == orig_date)[0][0]
					except:
						return np.array([])

					i_int_from_contra = i_int_to_contra - time_window_size + 1
					i_new = np.array(nddf[con_symbol][con_field][i_int_from_contra:i_int_to_contra + 1])
					i_data_array = np.append(i_data_array, i_new)
		return i_data_array

	def roll_time_frame(array, time_window, data_window_back_shift=0):  # rolling time frame
		a = np.array(array).astype(float)
		stack_array = [0] * time_window
		for i in range(time_window):
			nprt = np.roll(a, (time_window - i - 1 + data_window_back_shift))
			# print(nprt)
			stack_array[i] = nprt
			for n in range(time_window - i - 1 + data_window_back_shift):
				stack_array[i][n] = np.NaN
			# print(stack_array[i])

		return np.vstack(stack_array).T

	symbol = "BTCUSDT"
	project = "BTCUSDT_P10INT"
	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)
	# print(contras)
	time_window_size = int(dataset_config['time_window_size'])

	hstack_array = []
	for field in original_fields:
		hstack_array.append(roll_time_frame(nddf[symbol][field], time_window_size))

	# print(nddf[symbol].shape)

	dataset_new = np.hstack(hstack_array)

	for i in range(nddf[symbol].shape[0]):
		if i % 1000 == 0:
			print(i)
		old_data = get_dataset_by_index(symbol, i, time_window_size, original_fields, contras, {}, nddf)
		# print(old_data)
		if len(old_data) == 0:
			old_data = [np.NaN] * (time_window_size * len(original_fields))
		# print(dataset_new[i])
		# print(old_data)
		dataset_new[i] = np.array(list(dataset_new[i])).astype(np.float64).round(5)
		old_data = np.array(list(old_data)).astype(np.float64).round(5)
		# print(dataset_new[i])
		# print(old_data)

		if not np.allclose(old_data, dataset_new[i]):
			print(i, "eltérés")
			# print(str(dataset_new[i]))
			# print(str(old_data))
			# i_int_to = int(i)
			# i_int_from = i_int_to - time_window_size + 1
			#
			# for i_of in original_fields:
			# 	print(nddf[symbol][i_of][i_int_from:i_int_to + 1])


		# for dsx, dsn in enumerate(dataset_new[i]):
			# 	if dsn != old_data[dsx]:
			# 		print(dsn, old_data[dsx])
			# 		time.sleep(1)


def stream_job():
	print("run outer job")

	i_new_row_count = ndf.get_allrow_count()
	indicators_by_symbols = ai.get_all_indicators_by_symbols()  # ez csak azokat adja vissza ami a projekt futtatásához kell

	for smb in ndf.get_all_symbol():
		if ndf.refresh(smb, log_visible=False) > 0:  # frissítem az adatokat
			if smb in indicators_by_symbols:
				for indicator in indicators_by_symbols[smb]:
					ndf.refresh_tech(smb, indicator, log_vissible=False)

	# for smb in ndf.get_all_symbol():

	# ndf.get_dataset_by_index(symbol=symbol,
	# 						 index=ix + x_from,
	# 						 time_window_size=time_window_size,
	# 						 original_fields=original_fields,
	# 						 contras=contras,
	# 						 contra_copies=contra_copies)

	i_new_row_count = ndf.get_allrow_count() - i_new_row_count
	if i_new_row_count > 0:  # csak akkor frissítünk ha van új sor
		stream_last_refresh(time.strftime("%H:%M"))


def s(msg_str):
	# if LogTo == "Gui":
	QApplication.processEvents()
	gui.Status.setText("Status: " + msg_str)
	gui.Progress_Bar.setValue(0)
	QApplication.processEvents()


s2_value = 0
s2_max = 0
s2_last_dt = datetime.now()
re_ti_str = ""


def s2(null=False, steps=0, text="", recalc=500):
	global s2_value, s2_max, s2_last_dt, re_ti_str

	# if LogTo == "Gui":
	QApplication.processEvents()
	if null:
		s2_value = 0
		s2_max = steps
		gui.Status.setText(" ".join(["Status:", str(int(s2_value)), "%"]))
		gui.Progress_Bar.setValue(int(s2_value))
	else:
		if s2_value <= s2_max:
			prc = '{0:.2f}'.format(s2_value / s2_max * 100)
			perc_str = f"Status: {prc} % {text}                    "
			perc_str = perc_str[0:35]
			if s2_value % recalc == 0:
				t = (datetime.now() - s2_last_dt) / recalc
				s2_last_dt = datetime.now()
				re_ti = (s2_max - s2_value) * t
				imin = int(re_ti.seconds / 60)
				isec = "00" + str(re_ti.seconds - (imin * 60))
				isec = isec[-2:]
				re_ti_str = f"remaining time: {imin}:{isec} min."
			gui.Status.setText(f"{perc_str}  {re_ti_str}")
			gui.Progress_Bar.setValue(int(s2_value / s2_max * 100))
			s2_value += 1
		else:
			gui.Status.setText("Status: ok")
			gui.Progress_Bar.setValue(10)
	QApplication.processEvents()


def stream_last_refresh(text):
	gui.Ndf_last_update.setText(text)
	QApplication.processEvents()


def ai_log():
	pass


def log(add_text, line=False, indent=True, color="normal", visible=True):
	LogTo = "Gui"
	if visible:
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
				if one_line[0:2] == "  ":
					one_line = "&nbsp;&nbsp;" + one_line[2:]

				i_log_text = f"""
					{i_log_text}
					<font color='#000000'> {time.strftime("%m-%d %H:%M:%S")} >  {i_ind} </font>
					<font color='{i_web_color}'> {one_line} </font><br>"""
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


# ai programs  ----------------------------------------------------------------------------


def ai_add(symbol="", project=""):
	ai.add(symbol, project)
	gui.refresh_ui("ai_info")


def ai_remove(symbol="", project=""):
	ai.remove_project(symbol, project)
	gui.refresh_ui("ai_info")


def ai_download(project_name, rename=""):
	ai.download(project_name, rename)

def ai_confusion(symbol, project):

	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)
	cX_array, bug_index = ndf.get_dataset_full_stack(symbol, project, nan_manager="drop")
	y_field = "y_" + dataset_config["sig_suffix"]
	y_np = np.array(nddf[symbol][y_field].values)
	y_np = np.delete(y_np, bug_index, 0)

	i_indexes_9 = np.where(y_np == 9)[0]
	y_np = np.delete(y_np, i_indexes_9, 0)
	cX_array = np.delete(cX_array, i_indexes_9, 0)
	i_indexes_10 = np.where(y_np == 10)[0]
	y_np = np.delete(y_np, i_indexes_10, 0)
	cX_array = np.delete(cX_array, i_indexes_10, 0)

	ai.build()
	log(f" Predicting y, full dataset: {nddf[symbol].shape[0]}")
	y_predict, y_predict_sig, y_predict_strength = ai.predict_multi(symbol, project, cX_array)

	ai.confusion(y_predict_sig, y_predict_strength, y_np, name="Full")

	ai.confusion(y_predict_sig[-100000:], y_predict_strength[-200000:], y_np[-100000:], name="Last 100k")


last_pp1, last_pp2, last_pp3 = 0, 0, 0

# def ai_clibrate(symbol, run_time_window, project, start_position=0):
# 	if int(start_position) + int(run_time_window) > nddf[symbol].shape[0]:
# 		log(" Time window out of range.")
# 		return
#
# 	def summary(obj, run_time_window, setings, pos):
# 		global last_pp1, last_pp2, last_pp3
# 		# log("  ")
# 		# log(f"{obj.name}")
# 		# log(f"  (1) value limit: {obj.value_limit}       (2) stock_size: {obj.stock_size_orig}")
# 		# log(f"  (3) avg. profit/day: {obj.get_profit_per_day()}       (4) avg. profit/closed deal: {obj.get_profit_per_closed_deal()}")
# 		# log(f"  (5) closed_deal/day: {obj.get_closed_deal_per_day()}  (6) transaction/day: {obj.get_transaction_per_day()}")
# 		# log(f"  (7) turnover: {int(obj.get_turnover())}      (8) gross profit: {obj.get_profit()}")
# 		p1 = obj.get_profit() - int(obj.get_turnover() * (.075 / 100))
# 		p2 = obj.get_profit() - int(obj.get_turnover() * (.055 / 100))
# 		p3 = obj.get_profit() - int(obj.get_turnover() * (.025 / 100))
# 		# log(f"  (8) net profit (nominal) (.075%, .055%, .025%): {p1}, {p2} ,{p3}")
# 		pp1 = round((((p1 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
# 		pp2 = round((((p2 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
# 		pp3 = round((((p3 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
# 		if pp1 > last_pp1 and pp3 > 0:
# 			log(f"{pos} -  gross pr.: {obj.get_profit()} net pr.: (% year)(.075%, .055%, .025%): {pp1}%, {pp2}% ,{pp3}%")
# 			last_pp1 = pp1
# 			print(pos, pp1, pp2, pp3, setings)
# 			return
#
# 	start_position = int(start_position)
# 	run_time_window = int(run_time_window)
# 	ai.build()
#
# 	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)
#
# 	x_from = start_position
# 	x_to = x_from + run_time_window
#
# 	sig_field = "SIG_" + dataset_config['sig_suffix']
# 	res = tuple(nddf[symbol].loc[x_from, ['ohlc4', sig_field, 'Date']])
# 	from_date = res[2]
# 	res = tuple(nddf[symbol].loc[x_to, ['ohlc4', sig_field, 'Date']])
# 	to_date = res[2]
# 	log(f"Selected time frame: {from_date} - {to_date}")
#
# 	value_limit = 10000
# 	stock_size = 10000
# 	# transaction_fee_p = 0.055 /100  # %
# 	# transaction_fee_c = int(stock_size * transaction_fee_p)
# 	# stop_loss = stock_size * .25 / 100 * -1  # %
# 	log(f"stock size: {stock_size} USD")
# 	# log(f"stop loss: {stop_loss} USD")
#
# 	pre_load = nddf[symbol].loc[x_from:x_to + 1, ['ohlc4', sig_field, 'Date', 'Low', 'High', 'MACDh_12_26_9']]
# 	# print(pre_load)
# 	pre_ohlc4 = tuple(pre_load['ohlc4'])
# 	sig = tuple(pre_load[sig_field])
# 	# pre_sig_all = tuple(pre_load['SIG_ALL_MT'])
# 	pre_date = tuple(pre_load['Date'])
# 	pre_low = tuple(pre_load['Low'])
# 	pre_high = tuple(pre_load['High'])
#
# 	X_array, bug_index = ndf.get_dataset_full_stack(symbol, project, nan_manager="empty")
# 	X_array = X_array[x_from:x_to]
# 	bug_index = bug_index[np.where((bug_index >= x_from) & (bug_index <= x_to))[0]]
# 	gui.ailog(f"Predict y: {symbol} {project} X_set size: {len(X_array)}")
# 	y_predict, y_predict_sig, y_predict_strength = ai.predict_multi(symbol, project, X_array)
# 	np.put(y_predict_sig, bug_index, 3)
#
# 	# y_predict_sig = np.random.choice([0,1,2], x_to-x_from, p=[0.6, 0.2, 0.2])
# 	# y_predict_strength = np.random.choice([.9,.9,.9], x_to-x_from, p=[0.6, 0.2, 0.2])
#
# 	a_strength_filter = np.arange(0.35, 0.58, 0.01)
# 	l1 = a_strength_filter.shape[0]
# 	a_monitor_window_size = np.arange(2, 4, 1)
# 	l2 = a_monitor_window_size.shape[0]
# 	a_monitor_profitx = np.arange(0.1, 0.2, 0.01) # ezt minusszá teszi
# 	l3 = a_monitor_profitx.shape[0]
# 	a_monitor_std = np.arange(5, 25, 1)
# 	l4 = a_monitor_std.shape[0]
# 	a_steps_limit = np.arange(8, 20, 1)
# 	l5 = a_steps_limit.shape[0]
# 	a_trailer_stop = np.arange(0.1, 0.25, 0.1)
# 	l6 = a_trailer_stop.shape[0]
# 	a_stop_loss_limit = np.arange(0.1, 0.3, 0.05)
# 	l7 = a_stop_loss_limit.shape[0]
# 	a_trailer_min_profit = np.arange(2, 10, 1)
# 	l8 = a_trailer_min_profit.shape[0]
#
# 	all_setings = []
# 	all_comb = l1*l2*l3*l4*l5*l6
# 	s2(True, all_comb, recalc=2000)
#
# 	for p_strength_filter in a_strength_filter:
# 		for p_monitor_window_size in a_monitor_window_size:
# 			for p_monitor_profitx in a_monitor_profitx:
# 				p_monitor_profit = p_monitor_profitx * -1
# 				for p_monitor_std in a_monitor_std:
# 					for p_steps_limit in a_steps_limit:
# 						for p_trailer_stop in a_trailer_stop:
# 							for p_stop_loss_limit in a_stop_loss_limit:
# 								for p_trailer_min_profit in a_trailer_min_profit:
#
# 									setings = {"p_strength_filter": p_strength_filter,
# 											   "p_monitor_window_size": p_monitor_window_size,
# 											   "p_monitor_profit": p_monitor_profit,
# 											   "p_monitor_std": p_monitor_std,
# 											   "p_steps_limit": p_steps_limit,
# 											   "p_trailer_stop": p_trailer_stop,
# 											   "p_stop_loss_limit": p_stop_loss_limit,
# 											   "p_trailer_min_profit": p_trailer_min_profit,
# 											   }
#
# 									all_setings.append(setings)
# 							s2(recalc=2000)
#
# 	log(f"Number of parameters: {len(all_setings)}")
#
# 	strategi = 1
# 	src_array = []
# 	if strategi == 1:
# 		xx = np.array(range(0, len(all_setings)))
# 		random.seed(4)
# 		random.shuffle(xx)
# 		cfom = 0
# 		cto = 10000
# 		# 69 - 250
# 		src_array = xx[cfom:cto]
# 	elif strategi == 2:
# 		xx = np.array(range(0, len(all_setings), 10000))
# 		src_array = xx
# 		cfom = 0
#
# 	s2(True, (len(src_array)-1), recalc=1)
# 	for i, x in enumerate(src_array):
# 		p_strength_filter = all_setings[x]["p_strength_filter"]
# 		p_monitor_window_size = all_setings[x]["p_monitor_window_size"]
# 		p_monitor_profit = all_setings[x]["p_monitor_profit"]
# 		p_monitor_std = all_setings[x]["p_monitor_std"]
# 		p_steps_limit = all_setings[x]["p_steps_limit"]
# 		p_trailer_stop = all_setings[x]["p_trailer_stop"]
# 		p_stop_loss_limit = all_setings[x]["p_stop_loss_limit"]
# 		p_trailer_min_profit = all_setings[x]["p_trailer_min_profit"]
# 		setings = all_setings[x]
#
# 		algo_main = n_algo_trade()
# 		algo_main.config({"name": symbol + " Ai " + str(x_from) + " - " + str(x_to),
# 						  "id": 1,
# 						  "value_limit": value_limit,
# 						  "stock_size": stock_size,
# 						  "stop_loss_limit": -stock_size * (p_stop_loss_limit / 100),
# 						  "profit_take_limit": -1,  # -1 nincs bekapcsolva, amúgy nominálisan mondja usd ben
# 						  "trailer_stop": p_trailer_stop, # .15 = 15% ennyivel eshet vissz a aktuális profit a legmagasabb trailer profithoz képest
# 						  "trailer_min_profit": p_trailer_min_profit,  # nominal in usd
# 						  "value_limit_profit_reinvest": False,
# 						  "steps_limit": p_steps_limit,
# 						  "strategy": 69,
# 						  "trade_time_start": (0, 1),
# 						  "trade_time_stop": (23, 59),
# 						  "next_price_random": True,
# 						  "enter_limit_order": False,  # limit = actual_ohlc4
# 						  "strength_filter": p_strength_filter,
# 						  "monitor_window_size": int(p_monitor_window_size),
# 						  "monitor_profit": p_monitor_profit,
# 						  "monitor_std": p_monitor_std
# 						  })
#
#
# 		for ix in range(0, x_to - x_from):
# 			price_dict = {
# 				"actual_low": pre_low[ix],
# 				"actual_high": pre_high[ix],
# 				"actual_ohlc4": pre_ohlc4[ix],
# 				"next_low": pre_low[ix + 1],
# 				"next_high": pre_high[ix + 1],
# 				"next_ohlc4": pre_ohlc4[ix + 1]
# 			}
#
# 			algo_main.transaction(sig[ix], y_predict_sig[ix],
# 								  y_predict_strength[ix],
# 								  price_dict, pre_date[ix], x_from + ix)
#
# 		s2(recalc=1)
#
# 		summary(algo_main, run_time_window, setings, cfom+i)
# 		del algo_main


def ai_clibrate_mp(symbol, run_time_window, project, start_position=0):
	# TODO tedd át az ai objektumba
	if int(start_position) + int(run_time_window) > nddf[symbol].shape[0]:
		log(" Time window out of range.")
		return

	start_position = int(start_position)
	run_time_window = int(run_time_window)
	trade_strategy = 66
	ai.build()

	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)

	x_from = start_position
	x_to = x_from + run_time_window

	sig_field = "SIG_" + dataset_config['sig_suffix']
	res = tuple(nddf[symbol].loc[x_from, ['ohlc4', sig_field, 'Date']])
	from_date = res[2]
	res = tuple(nddf[symbol].loc[x_to, ['ohlc4', sig_field, 'Date']])
	to_date = res[2]
	log(f"Selected time frame: {from_date} - {to_date}")

	value_limit = 10000
	stock_size = 10000
	log(f"stock size: {stock_size} USD")

	pre_load = nddf[symbol].loc[x_from:x_to + 1, ['ohlc4', sig_field, 'Date', 'Low', 'High', 'MACDh_12_26_9']]
	pre_ohlc4 = tuple(pre_load['ohlc4'])
	sig = tuple(pre_load[sig_field])
	pre_date = tuple(pre_load['Date'])
	pre_low = tuple(pre_load['Low'])
	pre_high = tuple(pre_load['High'])

	X_array, bug_index = ndf.get_dataset_full_stack(symbol, project, nan_manager="empty")
	X_array = X_array[x_from:x_to]
	bug_index = bug_index[np.where((bug_index >= x_from) & (bug_index <= x_to))[0]]

	if len(bug_index) > 0:
		log(f"Time period contains data gap. bugindex len: {len(bug_index)}")
		return

	bug_index = bug_index - x_from  # nem fut le
	log(f"Bug index len: {len(bug_index)}")  # nem fut le
	gui.ailog(f"Predict y: {symbol} {project} X_set size: {len(X_array)}")
	y_predict, y_predict_sig, y_predict_strength = ai.predict_multi(symbol, project, X_array)
	np.put(y_predict_sig, bug_index, 3)  # nem fut le

	# azt vizsgálom milyen hatékonyság kell
	# y_predict_sig = np.array(sig).copy()
	# for iyx in range(len(y_predict_sig)):
	# 	rin = random.randint(0, 100) + 1
	# 	if y_predict_sig[iyx] == 1:
	# 		if 0 < rin < 10:
	# 			y_predict_sig[iyx] = 1
	# 		elif 11 < rin < 70:
	# 			y_predict_sig[iyx] = 0
	# 		else:
	# 			y_predict_sig[iyx] = 2
	# 	elif y_predict_sig[iyx] == 2:
	# 		if 0 < rin < 10:
	# 			y_predict_sig[iyx] = 1
	# 		# elif 11 < rin < 56:
	# 		# 	y_predict_sig[iyx] = 0
	# 		# else:
	# 		# 	y_predict_sig[iyx] = 2
	# 	else: ## == 0
	# 		if 0 < rin < 0:
	# 			y_predict_sig[iyx] = 1
	# 		# elif 11 < rin < 56:
	# 		# 	y_predict_sig[iyx] = 0
	# 		# else:
	# 		# 	y_predict_sig[iyx] = 2
	#
	# confusion_mtx = tf.math.confusion_matrix(sig, y_predict_sig)
	#
	# c0 = int(confusion_mtx[0][1])
	# c1 = int(confusion_mtx[1][1])
	# c2 = int(confusion_mtx[2][1])
	# cr = round(((c0 + c2) / c1) * 100, 3)
	#
	# log(f"Confusion (slice 1): {c0} , {c1} , {c2} r: {cr} %")
	# log(f'y: {np.unique(y_predict_sig, return_counts=True)}')
	# y_predict_strength *= 10

	a_strength_filter = np.arange(0.8, 1, 0.0001)
	l1 = a_strength_filter.shape[0]
	a_monitor_window_size = np.arange(1, 2, 1)
	l2 = a_monitor_window_size.shape[0]
	a_monitor_profitx = np.arange(0.1, 0.2, 0.1) # ezt minusszá teszi
	l3 = a_monitor_profitx.shape[0]
	a_monitor_std = np.arange(5, 6, 1)
	l4 = a_monitor_std.shape[0]
	a_steps_limit = np.arange(8, 15, 1)
	l5 = a_steps_limit.shape[0]
	a_trailer_stop = np.arange(0.1, 0.35, 0.05)
	l6 = a_trailer_stop.shape[0]
	a_stop_loss_limit = np.arange(0.05, 0.15, 0.05)
	# l7 = a_stop_loss_limit.shape[0]
	a_trailer_min_profit = np.arange(2, 15, 1)
	# l8 = a_trailer_min_profit.shape[0]

	all_setings = []
	all_comb = l1*l2*l3*l4*l5*l6
	s2(True, all_comb, recalc=2000)

	for p_strength_filter in a_strength_filter:
		for p_monitor_window_size in a_monitor_window_size:
			for p_monitor_profitx in a_monitor_profitx:
				p_monitor_profit = p_monitor_profitx * -1
				for p_monitor_std in a_monitor_std:
					for p_steps_limit in a_steps_limit:
						for p_trailer_stop in a_trailer_stop:
							for p_stop_loss_limit in a_stop_loss_limit:
								for p_trailer_min_profit in a_trailer_min_profit:

									setings = {"p_strength_filter": p_strength_filter,
											   "p_monitor_window_size": p_monitor_window_size,
											   "p_monitor_profit": p_monitor_profit,
											   "p_monitor_std": p_monitor_std,
											   "p_steps_limit": p_steps_limit,
											   "p_trailer_stop": p_trailer_stop,
											   "p_stop_loss_limit": p_stop_loss_limit,
											   "p_trailer_min_profit": p_trailer_min_profit,
											   }

									all_setings.append(setings)
							s2(recalc=2000)

	log(f"Number of parameters: {len(all_setings)}")
	all_setings = np.array(all_setings)

	search_strategy = 1
	src_array = []
	if search_strategy == 1:
		xx = np.array(range(0, len(all_setings)))
		random.seed(4)
		np.random.shuffle(xx)
		cfom = 0
		cto = 10000
		# 69 - 250
		src_array = xx[cfom:cto]
	elif search_strategy == 2:
		xx = np.array(range(0, len(all_setings), 10000))
		src_array = xx
		cfom = 0

	used_cores = cpu_count()
	used_cores = 7  # 1 kell nekem :)
	runing_processes = []

	loacl_a = np.array([1], dtype=np.float64)  # 1 = mehet a trade
	loacl_a[0] = -10000.0
	shm = shared_memory.SharedMemory(create=True, size=loacl_a.nbytes)
	shaped_array = np.ndarray(loacl_a.shape, dtype=np.float64, buffer=shm.buf)
	shaped_array[:] = loacl_a[:]  # Copy the original data into shared memory

	for x in range(used_cores):
		if x == 7:
			log(f"  ai.calibrate -> creating params for mp object. Last speak.")
		s_from = ndf.get_slice_index(src_array.shape[0], used_cores, x)[0]
		s_to = ndf.get_slice_index(src_array.shape[0], used_cores, x)[1]
		src_array_slice = np.array(src_array[s_from:s_to])

		params = {'cores': used_cores,
				  'process': x,
				  'shm_name': shm.name,
				  'pre_low': pre_low,
				  'pre_high': pre_high,
				  'pre_ohlc4': pre_ohlc4,
				  'sig': sig,
				  'y_predict_sig': y_predict_sig,
				  'y_predict_strength': y_predict_strength,
				  'pre_date': pre_date,
				  # 'src_array': src_array[s_from:s_to],
				  'all_setings': all_setings[src_array_slice],
				  'symbol': symbol,
				  'x_from': x_from,
				  'x_to': x_to,
				  'value_limit': value_limit,
				  'stock_size': stock_size,
				  'run_time_window': run_time_window,
				  'trade_strategy': trade_strategy
				  }

		runing_processes.append(Process(target=mp_calibrate, args=(params,)))

	del all_setings
	gc.collect()
	for x, prc in enumerate(runing_processes):
		prc.start()
		log(f"  ai.calibrate start process: {x + 1} ")
		# soft start for processor cooler sincronize
		if x == 3:
			time.sleep(3)
		else:
			time.sleep(.5)

	for prc in runing_processes:
		prc.join()


def ai_calibrate(symbol, run_time_window, project, start_position=0):
	ai_clibrate_mp(symbol, run_time_window, project, start_position)


def ai_backtest(symbol, run_time_window, project, start_position=0):
	if int(start_position) + int(run_time_window) > nddf[symbol].shape[0]:
		log(" Time window out of range.")
		return
	def summary(obj, run_time_window):
		log("  ")
		log(f"{obj.name}")
		log(f"  (1) value limit: {obj.value_limit}       (2) stock_size: {obj.stock_size_orig}")
		log(f"  (3) avg. profit/day: {obj.get_profit_per_day()}       (4) avg. profit/closed deal: {obj.get_profit_per_closed_deal()}")
		log(f"  (5) closed_deal/day: {obj.get_closed_deal_per_day()}  (6) transaction/day: {obj.get_transaction_per_day()}")
		log(f"  (7) turnover: {int(obj.get_turnover())}      (8) gross profit: {obj.get_profit()}")
		p1 = obj.get_profit() - int(obj.get_turnover() * (.075 / 100))
		p2 = obj.get_profit() - int(obj.get_turnover() * (.055 / 100))
		p3 = obj.get_profit() - int(obj.get_turnover() * (.025 / 100))
		log(f"  (8) net profit (nominal) (.075%, .055%, .025%): {p1}, {p2} ,{p3}")
		pp1 = round((((p1 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
		pp2 = round((((p2 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
		pp3 = round((((p3 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
		log(f"  (9) net profit (% year)(.075%, .055%, .025%): {pp1}%, {pp2}% ,{pp3}%")

	cache_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\backtest_cache\\"

	start_position = int(start_position)
	log(f"ai_backtest {symbol} {run_time_window} {project}")
	run_time_window = int(run_time_window)
	ai.build()

	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)
	time_window_size = int(dataset_config['time_window_size'])

	if start_position == 0:
		rnd_from = 100
		rnd_to = nddf[symbol].shape[0] - (run_time_window + 300)
		x_from = np.random.randint(rnd_from, rnd_to)
		x_to = x_from + run_time_window
	else:
		x_from = start_position
		x_to = x_from + run_time_window

	sig_field = "SIG_" + dataset_config['sig_suffix']
	res = tuple(nddf[symbol].loc[x_from, ['ohlc4', sig_field, 'Date']])
	from_date = res[2]
	res = tuple(nddf[symbol].loc[x_to, ['ohlc4', sig_field, 'Date']])
	to_date = res[2]
	log(f"Selected time frame: {from_date} - {to_date}")

	value_limit = 10000
	stock_size = 10000
	# transaction_fee_p = 0.055 /100  # %
	# transaction_fee_c = int(stock_size * transaction_fee_p)
	# stop_loss = stock_size * .25 / 100 * -1  # %
	log(f"stock size: {stock_size} USD")
	# log(f"stop loss: {stop_loss} USD")

	parallel_backtest = False
	overrider = False


	# algo_main = n_algo_trade()
	# algo_main.config({"name": symbol + " Ai " + str(x_from) + " - " + str(x_to),
	# 						 "id": 1,
	# 						 "value_limit": value_limit,
	# 						 "stock_size": stock_size,
	# 						 "stop_loss_limit": -stock_size * (.1 / 100),
	# 						 "profit_take_limit": -1,  # -1 nincs bekapcsolva, amúgy nominálisan mondja usd ben
	# 						 "trailer_stop": .15,  #.15 = 15% ennyivel eshet vissz a aktuális profit a legmagasabb trailer profithoz képest
	# 						 "trailer_min_profit": 10, # nominal in usd
	# 						 "value_limit_profit_reinvest": False,
	# 						 "steps_limit": 6,
	# 						 "strategy": 66,
	# 						 "trade_time_start": (0, 1),
	# 						 "trade_time_stop": (23, 59),
	# 						 "next_price_random": True,
	# 						 "enter_limit_order": False  # limit = actual_ohlc4
	# 						 })

	algo_main = n_algo_trade()
	algo_main.config({"name": symbol + " Ai " + str(x_from) + " - " + str(x_to),
					  "id": 1,
					  "value_limit": value_limit,
					  "stock_size": stock_size,
					  "strength_filter": 0.38,
					  "monitor_window_size": 1,
					  "monitor_profit": -0.15,
					  "monitor_std": 20,
					  "steps_limit": 9,
					  "trailer_stop": .25,  # .15 = 15% ennyivel eshet vissz a aktuális profit a legmagasabb trailer profithoz képest
					  "stop_loss_limit": -stock_size * (.2 / 100),
					  "trailer_min_profit": 7,  # nominal in usd
					  "profit_take_limit": -1,  # -1 nincs bekapcsolva, amúgy nominálisan mondja usd ben
					  "value_limit_profit_reinvest": False,
					  "strategy": 69,
					  "trade_time_start": (0, 1),
					  "trade_time_stop": (23, 59),
					  "next_price_random": True,
					  "enter_limit_order": False  # limit = actual_ohlc4
					 })

	if parallel_backtest:
		# algo_rnd = n_algo_trade()
		# algo_rnd.config({"name": symbol + " sig random.shuffle "  + str(x_from) + " - " + str(x_to),
		# 					"id": 2,
		# 					"value_limit": value_limit,
		# 					"stock_size": stock_size,
		# 					"stop_loss_limit": stock_size * .1 / 100 * -1,
		# 					"profit_take_limit": -1,  # -1 nincs bekapcsolva
		# 					"trailer_stop": .15,
		# 					"trailer_min_profit": 10,
		# 					"value_limit_profit_reinvest": True,
		# 					"steps_limit": 6,
		# 					"strategy": 66,
		# 					"trade_time_start": (0, 1),
		# 					"trade_time_stop": (23, 59),
		# 					"next_price_random": True,
		# 					 "enter_limit_order": False  # limit = actual_ohlc4
		# 					})

		algo_sig = n_algo_trade()
		algo_sig.config({"name": "TARGET   " + symbol + " y - what the qfy said   " + str(x_from) + " - " + str(x_to),
							"id": 3,
							"value_limit": value_limit,
							"stock_size": stock_size,
							"stop_loss_limit": stock_size * .1 / 100 * -1,
							"profit_take_limit": -1,  # -1 nincs bekapcsolva
							"trailer_stop": .10,
							"trailer_min_profit": 10,
							"value_limit_profit_reinvest": True,
							"steps_limit": 6,
							"strategy": 66,
							"trade_time_start": (0, 1),
							"trade_time_stop": (23, 59),
							"next_price_random": True,
							 "enter_limit_order": False  # limit = actual_ohlc4
							})

		algo_over_x = n_algo_trade()
		algo_over_x.config({"name": "LONG RUN   " + symbol + " sig strength over 98 trailer is 75   " + str(x_from) + " - " + str(x_to),
							"id": 4,
							"value_limit": value_limit,
							"stock_size": stock_size,
							"stop_loss_limit": stock_size * .25 / 100 * -1,
							"profit_take_limit": -1,  # -1 nincs bekapcsolva
							"trailer_stop": .25,
							"trailer_min_profit": 10,
							"value_limit_profit_reinvest": True,
							"steps_limit": 120,
							"strategy": 67,
							"trade_time_start": (0, 1),
							"trade_time_stop": (23, 59),
							"next_price_random": True,
							 "enter_limit_order": False  # limit = actual_ohlc4
							})

		# algo_sig_filter = n_algo_trade()
		# algo_sig_filter.config({"name": symbol + " sig filter 70 strength filter 96   " + str(x_from) + " - " + str(x_to),
		# 					"id": 5,
		# 					"value_limit": value_limit,
		# 					"stock_size": stock_size,
		# 					"stop_loss_limit": stock_size * .5 / 100 * -1,
		# 					"profit_take_limit": -1,  # -1 nincs bekapcsolva
		# 					"trailer_stop": .75,
		# 					"trailer_min_profit": 10,
		# 					"value_limit_profit_reinvest": True,
		# 					"steps_limit": 120,
		# 					"strategy": 66,
		# 					"trade_time_start": (0, 1),
		# 					"trade_time_stop": (23, 59),
		# 					"next_price_random": True,
		# 					 "enter_limit_order": False  # limit = actual_ohlc4
		# 					})




	contra_copies, contra_copies_dt = ndf.get_contra_copies(contras)
	# print(contra_copies_dt)

	pre_load = nddf[symbol].loc[x_from:x_to + 1, ['ohlc4', sig_field, 'Date', 'Low', 'High', 'MACDh_12_26_9']]
	# print(pre_load)
	pre_ohlc4 = tuple(pre_load['ohlc4'])
	sig = tuple(pre_load[sig_field])
	# pre_sig_all = tuple(pre_load['SIG_ALL_MT'])
	pre_date = tuple(pre_load['Date'])
	pre_low = tuple(pre_load['Low'])
	pre_high = tuple(pre_load['High'])

	# # load dataset
	# cstr = "".join(contras)
	# ostr = "".join(original_fields)
	# full_cache_name = str(time_window_size) + cstr + ostr
	# full_cache_name = hashlib.md5(full_cache_name.encode('utf-8')).hexdigest()
	# array_len = time_window_size * (len(original_fields) + len(contras))
	#
	# cache_path = ndf.cache_path
	# f_name = cache_path + "DATASET_FULL_CACHE_" + full_cache_name + '.npy'
	# if os.path.isfile(f_name):
	# 	log(f"Dataset loaded from full cache.")
	# 	# ha van full cache akkor onnan
	# 	X_array = np.load(f_name)
	# 	X_array = X_array[x_from:x_to]
	#
	# 	for ic, xia in enumerate(X_array):
	# 		if not np.isnan(xia).any() \
	# 				and array_len == len(xia) \
	# 				and np.isfinite(xia).all():
	# 			pass
	# 		else:
	# 			X_array[ic] = np.array([0] * array_len)
	# 	s2(True, (x_to - x_from) * 1)
	# else:
	# 	backtest_cache_name = "x_set_" + str(x_from) + "_"+str(x_to)
	# 	try:
	# 		# ha van sub cache akkor onnan
	# 		X_array = np.load(cache_path + backtest_cache_name + '.npy')
	# 		s2(True, (x_to - x_from) * 1)
	# 	except:
	# 		# ha semmisincs akkor meg kell csinálni
	# 		s2(True, (x_to - x_from) * 2)
	# 		X_array = np.array([])
	# 		last_i_data_array = []
	# 		gap_manager = "empty"
	# 		idx = []
	# 		for ix in range(0, x_to - x_from):
	# 			i_data_array = ndf.get_dataset_by_index(symbol=symbol,
	# 												  index=ix + x_from,
	# 												  time_window_size=time_window_size,
	# 												  original_fields=original_fields,
	# 												  contras=contras,
	# 												  contra_copies_dt=contra_copies_dt)
	#
	# 			if not np.isnan(i_data_array).any() \
	# 					and array_len == len(i_data_array) \
	# 					and np.isfinite(i_data_array).all():
	# 				if len(X_array) == 0:
	# 					X_array = i_data_array
	# 				else:
	# 					X_array = np.vstack((X_array, i_data_array))
	# 			elif gap_manager == "empty":
	# 				idx.append(ix)
	# 				if len(X_array) == 0:
	# 					X_array = np.array([0] * array_len)
	# 				else:
	# 					X_array = np.vstack((X_array, np.array([0] * array_len)))
	#
	# 			s2()
	#
	# 		np.save(cache_path + backtest_cache_name, X_array)
	# 	else:
	# 		log(f"Dataset loaded from cache.")
	#
	# print(X_array.shape)

	array_len = time_window_size * (len(original_fields) + len(contras))
	X_array, bug_index = ndf.get_dataset_full_stack(symbol, project, nan_manager="empty")
	X_array = X_array[x_from:x_to]
	bug_index = bug_index[np.where((bug_index >= x_from) & (bug_index <= x_to))[0]]
	if len(bug_index) > 0:
		log(f"Time period contains data gap. bugindex len: {len(bug_index)}")
		return

	# print(bug_index)

	gui.ailog(f"Predict y: {symbol} {project} X_set size: {len(X_array)}")
	y_predict, y_predict_sig, y_predict_strength = ai.predict_multi(symbol, project, X_array)
	# idx = np.where(X_array == np.array([0] * array_len))[0]  # az üres dataseteket keresem és cserélem 0 ra
	# print(X_array[idx[0]])
	np.put(y_predict_sig, bug_index, 3)
	del X_array
	# del contra_copies

	# Confusion matrix ------------------------------------
	# ai.confusion(y_predict_sig, y_predict_strength, sig)

	s2(True, (x_to - x_from))

	if parallel_backtest and overrider:  # turn off

		y_predict_sig_rnd = y_predict_sig.copy()
		y_predict_strength_rnd = y_predict_strength.copy()
		np.random.shuffle(y_predict_sig_rnd)
		np.random.shuffle(y_predict_strength_rnd)
		# for i in range(len(y_predict)):
		# 	print(y_predict[i], y_predict_sig[i], y_predict_strength[i])
		# 	time.sleep(0)

		p1_s2 = 0
		p1_s0 = 0
		p1_s1 = 0
		p1_under_limit = 0
		p2_p0_under_limit = 0
		p0_and_p2 = 0
		p1_s0_override = 0
		p1_s2_override = 0

		p1_s0_limit = 70  # persentage tell the truth 101, 0 leave the predicted
		p1_s2_limit = 70  # persentage tell the truth 101; 0 leave the predicted
		or_strength_filter = .96

	for ix in range(0, x_to - x_from):
		price_dict = {
			"actual_low": pre_low[ix],
			"actual_high": pre_high[ix],
			"actual_ohlc4": pre_ohlc4[ix],
			"next_low": pre_low[ix + 1],
			"next_high": pre_high[ix + 1],
			"next_ohlc4": pre_ohlc4[ix + 1]
		}

		if parallel_backtest and overrider: #turn off
			if y_predict_strength[ix] > or_strength_filter:
				if y_predict_sig[ix] == 1 and sig[ix] == 0:
					if np.random.randint(1, 101) > p1_s0_limit:
						# hagyom a rosszat
						mod_y_pedict_sig = 1
						mod_y_predict_strength = y_predict_strength[ix]
					else:
						# megmondom az igazit
						mod_y_pedict_sig = 0
						mod_y_predict_strength = 1
						p1_s0_override += 1

					p1_s0 += 1
				elif y_predict_sig[ix] == 1 and sig[ix] == 1:
					mod_y_pedict_sig = 1
					mod_y_predict_strength = y_predict_strength[ix]
					p1_s1 += 1
				elif y_predict_sig[ix] == 1 and sig[ix] == 2:
					if np.random.randint(1, 101) > p1_s2_limit:
						# hagyom a rosszat
						mod_y_pedict_sig = 1
						mod_y_predict_strength = y_predict_strength[ix]
					else:
						# megmondom az igazit
						mod_y_pedict_sig = 2
						mod_y_predict_strength = 1
						p1_s2_override += 1

					p1_s2 += 1
				else:
					mod_y_pedict_sig = 0
					mod_y_predict_strength = 1
					p0_and_p2 += 1
			else:
				mod_y_pedict_sig = 0
				mod_y_predict_strength = 1
				if y_predict_sig[ix] == 1:
					p1_under_limit += 1
				else:
					p2_p0_under_limit += 1
		else:
			mod_y_pedict_sig = y_predict_sig[ix]
			mod_y_predict_strength = y_predict_strength[ix]

		# if ix % 1000 == 0:
		# 	print(p1_s1, p1_s2, p1_s0, "->", p1_s0_override, p0_and_p2 + p1_under_limit + p2_p0_under_limit,
		# 		  p1_s1 + p1_under_limit + p1_s2 + p1_s0 + p0_and_p2 + p2_p0_under_limit)


		algo_main.transaction(sig[ix], y_predict_sig[ix], y_predict_strength[ix], price_dict, pre_date[ix], x_from+ix)
		if parallel_backtest:
			algo_sig.transaction(sig[ix], sig[ix], 1, price_dict, pre_date[ix])
			# algo_rnd.transaction(sig[ix], y_predict_sig_rnd[ix], y_predict_strength_rnd[ix], price_dict, pre_date[ix])
			algo_over_x.transaction(sig[ix], y_predict_sig[ix], y_predict_strength[ix], price_dict, pre_date[ix])
			# algo_sig_filter.transaction(sig[ix], mod_y_pedict_sig, mod_y_predict_strength, price_dict, pre_date[ix])
		s2()

		# if ix % 25000 == 0 and ix != 0:
		# 	summary(algo_main, ix)

	if parallel_backtest:
		summary(algo_sig, run_time_window)
		# summary(algo_rnd, run_time_window)
		summary(algo_over_x, run_time_window)
		# summary(algo_sig_filter, run_time_window)
	summary(algo_main, run_time_window)

	if parallel_backtest and overrider:
		log(f"Overrider.", line=True)
		log(f"  Strength filter: {or_strength_filter}")
		log(f"  Overrider limit p1_s0: {p1_s0_limit}    overided cases: {p1_s0_override}")
		log(f"  Overrider limit p1_s2: {p1_s2_limit}    overided cases: {p1_s2_override}")
		log(f"  Case stat. p1:{p1_s1 + p1_s0 + p1_s2}  p1_s1: {p1_s1}   p1_s0: {p1_s0}   p1_s2: {p1_s2}")
		log(f"  Case stat. p0 and p2:{p0_and_p2}")
		log(f"  Strength filtered:  p1 {p1_under_limit}, filtered p2 p0: {p2_p0_under_limit}")


	if parallel_backtest:
		algo_sig.show_history()
		# algo_rnd.show_history()
		algo_over_x.show_history()
		# algo_sig_filter.show_history()
	algo_main.show_history()

	# algo_ai_override.history.to_excel('algo_ai_override.xlsx', engine='xlsxwriter')
	# algo_ai_rnd.history.to_excel('algo_ai_rnd.xlsx', engine='xlsxwriter')

	del algo_main
	if parallel_backtest:
		# del algo_rnd
		del algo_over_x
		del algo_sig
		# del algo_sig_filter

	s("ok :)")


def ai_build():
	log("Build TF and Minmax Scaler object.")
	ai.build()


# ndf programs  ----------------------------------------------------------------------------


def ndf_add(symbol="", years=1):
	ndf.add(symbol, years)

def ndf_add_crypto(symbol="", years=1):
	ndf.add_crypto_multi2(symbol, years)

def ndf_tech(symbol, tech_indicator, params=[]):
	ndf.add_tech(symbol, tech_indicator, params)


def ndf_tech_backtest(symbol, run_time_window, sig_field, start_position=0):
	start_position = int(start_position)
	log(f"ndf_tech_backtest {symbol} {run_time_window} {sig_field}")
	run_time_window = int(run_time_window)

	if start_position == 0:
		rnd_from = 100
		rnd_to = nddf[symbol].shape[0] - (run_time_window + 300)
		x_from = np.random.randint(rnd_from, rnd_to)
		x_to = x_from + run_time_window
	else:
		x_from = start_position
		x_to = x_from + run_time_window

	res = tuple(nddf[symbol].loc[x_from, ['Date']])
	from_date = res[0]
	res = tuple(nddf[symbol].loc[x_to, ['Date']])
	to_date = res[0]
	log(f"start_position: {x_from}")
	log(f"Selected test time window: {from_date} - {to_date}")

	algo_sig = n_algo_trade()
	algo_sig.config({"name": symbol + " Ai override decisions drived",
							 "value_limit": 40000,
							 "stock_size": 15000,
							 "stop_loss_limit": -10,
					 		 "profit_take_limit": -1,  #  -1 nincs bekapcsolva
							 "trailer_stop": .5,  # -1 akkor nincs mebkapcsolva
							 "trailer_min_profit": 10,
							 "value_limit_profit_reinvest": True,
							 "steps_limit": 80,
							 "strategy": 22,
							 "trade_time_start": (16, 00),
							 "trade_time_stop": (21, 00),
							 "next_price_random": True
							 })

	s2(True, (x_to - x_from) * 2)

	pre_load = nddf[symbol].loc[x_from:x_to + 1, ['ohlc4', sig_field, 'Date', 'Low', 'High']]
	pre_ohlc4 = tuple(pre_load['ohlc4'])
	pre_sig = tuple(pre_load[sig_field])
	pre_date = tuple(pre_load['Date'])
	pre_low = tuple(pre_load['Low'])
	pre_high = tuple(pre_load['High'])

	for ix in range(0, x_to - x_from):
		price_dict = {
			"actual_low": pre_low[ix],
			"actual_high": pre_high[ix],
			"actual_ohlc4": pre_ohlc4[ix],
			"next_low": pre_low[ix + 1],
			"next_high": pre_high[ix + 1],
			"next_ohlc4": pre_ohlc4[ix + 1]
		}
		algo_sig.transaction(pre_sig[ix], pre_sig[ix], .25, price_dict, pre_date[ix])
		s2()

	log(f"Signal Drived algo trade.")
	log(f"  value limit: {algo_sig.value_limit} stock_size: {algo_sig.stock_size_orig}")
	log(f"  profit/day: {algo_sig.get_profit_per_day()} profit/closed deal: {algo_sig.get_profit_per_closed_deal()}")
	log(f"  closed_deal/day: {algo_sig.get_closed_deal_per_day()} transaction/day: {algo_sig.get_transaction_per_day()}")

	algo_sig.show_history()

	algo_sig.history.to_excel('signal_drived_algo_trade.xlsx', engine='xlsxwriter')
	del algo_sig


def ndf_tech_project(symbol, project):
	gdc_ok, description, dataset_config, original_fields, contras, indexes = ai.get_project_config(project)
	if gdc_ok:
		for indx in indexes:
			ndf.add_tech(symbol, indx)


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


def ndf_dataset(symbol="", config_file="", force="NOFORCE", overlay_manager="rnd_choice"):
	if force.lower() == "force":
		force = True
	else:
		force = False

	ndf.create_dataset(symbol, config_file, force, overlay_manager.lower())
	s("")


def ndf_dataset_full(symbol="", project=""):
	ndf.create_dataset_full_stack(symbol, project)


def ndf_dataset_int(symbol="", config_file="", full="NOFULL"):
	if full == "FULL":
		ifull = True
	else:
		ifull = False
	ndf.create_dataset_int_stack(symbol, config_file, ifull)


def ndf_remove(symbol=""):
	ndf.remove(symbol)


def ndf_remove_column(symbol="", field="", save=""):
	ndf.remove_columns(symbol, [field])
	if save == "SAVE":
		ndf.set_dt_order(symbol)
		nddb.write(symbol)


def ndf_refresh(symbol=""):
	ndf.refresh(symbol)


def ndf_refresh_all():
	i_symbols = tuple(nddf.keys())
	for smb in i_symbols:
		ndf.refresh(smb)


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


def ndf_show_last(symbol=""):
	if symbol in nddf:

		from pandastable import Table, config  # , TableModel

		class TestApp(Frame):
			"""Basic test frame for the table"""

			def __init__(self, parent=None):
				self.parent = parent
				Frame.__init__(self)
				self.main = self.master
				self.main.geometry('1800x900+50+50')
				self.main.title(symbol)
				f = Frame(self.main)
				f.pack(fill=BOTH, expand=1)
				df = nddf[symbol].copy()
				self.table = pt = Table(f, dataframe=df,
										showtoolbar=True, showstatusbar=True)
				# self.table = pt = Table(f, dataframe=nddf[symbol].iloc[::-1],
				#                         showtoolbar=True, showstatusbar=True)
				options = {'align': 'w',
						   'cellbackgr': '#dddddd',
						   'cellwidth': 70,
						   'colheadercolor': '#535b71',
						   'floatprecision': 8,
						   'font': 'Arial',
						   'fontsize': 10,
						   'fontstyle': '',
						   'grid_color': '#AAAAAA',
						   'linewidth': 1,
						   'rowheight': 20,
						   'rowselectedcolor': '#ff9100',
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
	if market == "ALT":
		for smb in nbt.get_all_symbols():
			print(smb)

	else:
		market_symbols = pd.DataFrame(md.stock_symbols(market))
		print(market_symbols)





# wl programs -------------------------------------------------------------------------------------------------------


def wl_add(symbol="", years=3):
	wl.add(symbol, years)

def wl_add_crypto(symbol="", years=3):
	wl.add_crypto(symbol, years)

def wl_remove(symbol=""):
	wl.remove(symbol)
	ndf.remove(symbol)
	ai.remove_symbol(symbol)
	gui.refresh_ui()


def wl_refresh_profile():
	wl.refresh_profile()
	gui.refresh_ui()


def wl_refresh_sentiment():
	wl.refresh_sentiment()
	gui.refresh_ui()


# PROGRAMS fo wl buttons----------------------------------------------------------------------------


def wl_trade_short(btn_no):
	symbol = wl.wl_df.loc[btn_no - 1]['symbol']
	ntrade.order['symbol'] = symbol
	ntrade.order['position'] = "SHORT"
	i_market_price = ntrade.get_market_price_by_symbol(symbol)
	ntrade.order['market_price'] = float(i_market_price)
	ntrade.order['qty'] = int(ntrade.config["trade_block_size"] / ntrade.order['market_price'])
	ntrade.order['stop_trailing'] = False
	gui.set_trade_frame()


def wl_trade_long(btn_no):
	symbol = wl.wl_df.loc[btn_no - 1]['symbol']
	ntrade.order['symbol'] = symbol
	ntrade.order['position'] = "LONG"
	i_market_price = ntrade.get_market_price_by_symbol(symbol)
	ntrade.order['market_price'] = float(i_market_price)
	ntrade.order['qty'] = int(ntrade.config["trade_block_size"] / ntrade.order['market_price'])
	ntrade.order['stop_trailing'] = False
	gui.set_trade_frame()


def wl_btn_chart(btn_no):
	symbol = wl.wl_df.loc[btn_no - 1]['symbol']
	log("start: nchart " + symbol, True, False)
	i_indecators = ndf.get_added_indicators(symbol)
	i_df = nddf[symbol].tail(60000).copy()
	nchart.fit(i_df, symbol, i_indecators)
	nchart.show()


def wl_btn_show(btn_no):
	symbol = wl.wl_df.loc[btn_no - 1]['symbol']
	log("start: ndf.show.last " + symbol, True, False)
	ndf_show_last(symbol)
	log("ready.", False, False)


# tr PROGRAMS ----------------------------------------------------------------------------


def tr_set_order():
	if ntrade.order["position"] == "LONG":
		i_qty = int(ntrade.order["qty"])
	else:
		i_qty = -1 * int(ntrade.order["qty"])
	ntrade.set_tp_position(ntrade.order["symbol"], i_qty)
	gui.Tr_frame.hide()
	QApplication.processEvents()
	gui.refresh_ui("info")
	ntrade.broker_run()


def tr_stop(btn_no):
	symbol = wl.wl_df.loc[btn_no - 1]['symbol']
	if gui.confirm("Stop " + symbol, "Are you sure? Stop " + symbol + " position?"):
		ntrade.order["symbol"] = symbol
		ntrade.order["position"] = "STOP"
		ntrade.order["qty"] = 0
		ntrade.order["stop_trailing"] = False
		ntrade.set_tp_position(ntrade.order["symbol"], 0)
		gui.Tr_frame.hide()
		QApplication.processEvents()
		gui.refresh_ui("info")
		ntrade.broker_run()


def tr_stop_all():
	gui.Tr_frame.hide()
	QApplication.processEvents()
	if gui.confirm("Stop all!", "Are you sure? Stop all position?"):
		gui.tlog(f"Start: STOP ALL!", line=True, indent=False, color="normal")
		i_open_orders = ntrade.get_all_open_orders()
		i_symbol_dic = {}
		for i_o1 in i_open_orders:
			i_symbol_dic[i_o1.symbol] = 1
		for i_o2 in i_symbol_dic:
			gui.tlog(f"Clear orders: {i_o2}", line=False, indent=True, color="normal")
			ntrade.cancel_orders_by_symbol(i_o2)

		for i_s in tuple(wl.wl_df["symbol"]):
			ntrade.set_tp_position(i_s, 0)

		i_pos = ntrade.get_all_positions()
		for i_s2 in i_pos:
			if i_s2.symbol not in tuple(wl.wl_df["symbol"]):
				ntrade.set_tp_position(i_s2.symbol, 0)

		gui.refresh_ui("info")
		gui.tlog(f"Ready.", line=False, indent=False, color="normal")
		ntrade.broker_run()


def tr_portfolio_monitor():
	if gui.Tr_portfolio_monitor.checkState():
		ntrade.monitor_run()
	else:
		ntrade.monitor_stop()


def ndf_stream():
	if gui.Ndf_stream.checkState():
		md.stream_run()
	else:
		md.stream_stop()


def tr_info_refresh():
	ntrade.refresh_tr_info()


if __name__ == "__main__":
	print("Status: Start")
	wl = watch_list()
	nddf = {}
	nddb = n_db(nddf, log)


	print("Status: GUI Loading...")
	app = QApplication([])
	gui = gui()
	ai = n_ai(log, nddf, gui)
	ntrade = n_trade(gui=gui)
	nchart = n_chart(ntrade)
	gui.refresh_ui()
	gui.show()

	ndf = n_date_frame2()
	ndf_meta = n_date_frame_meta(log)
	n_tools = n_tools(gui=gui)
	md = n_market_data(log, s, n_tools, ndf, stream_job)
	try:
		nbt = n_binance_trade(log=log, s=s, tools=n_tools)
	except:
		print("Internet connection error. (Binance)")
	mp_tech = n_tech_mp
	mp_calibrate = n_calibrate_mp
	mp_dataset_constructor = n_dataset_constructor_mp
	# do2("BTCUSDT")
	app.exec()


