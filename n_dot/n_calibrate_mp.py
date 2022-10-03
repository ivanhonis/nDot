import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime
import asyncio


from threading import Thread
import pickle
from n_dot.n_algo_trade import n_algo_trade
from multiprocessing import shared_memory, Lock
lock = Lock()


class n_calibrate_mp:

    def __init__(self, param_mp):
        self.s = param_mp
        self.temp_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\temp\\"
        self.cores = self.s['cores']  # összesen hány process van
        self.process = self.s['process']  # én hanyadik process vagyok
        self.mpi = str(self.process + 1) + "/" + str(self.cores) + " core ->"
        self.shared_memory_name = self.s['shm_name']
        existing_shm = shared_memory.SharedMemory(name=self.shared_memory_name)
        self.max_p1 = np.ndarray((1,), dtype=np.float64, buffer=existing_shm.buf)
        if self.process == self.cores - 1:
            print(self.mpi, "multiprocessing ai.clalibrate starts. Last speak.")
        self.calibrate()


    def set_max_p1(self, value):
        lock.acquire()
        if self.max_p1[0] < value:
            self.max_p1[0] = value
        lock.release()

    def get_max_p1(self):
        lock.acquire()
        i_ret = self.max_p1[0]
        lock.release()
        return i_ret

    def summary(self, obj, run_time_window, setings, x_try):
        global last_pp1, last_pp2, last_pp3
        # log("  ")
        # log(f"{obj.name}")
        # log(f"  (1) value limit: {obj.value_limit}       (2) stock_size: {obj.stock_size_orig}")
        # log(f"  (3) avg. profit/day: {obj.get_profit_per_day()}       (4) avg. profit/closed deal: {obj.get_profit_per_closed_deal()}")
        # log(f"  (5) closed_deal/day: {obj.get_closed_deal_per_day()}  (6) transaction/day: {obj.get_transaction_per_day()}")
        # log(f"  (7) turnover: {int(obj.get_turnover())}      (8) gross profit: {obj.get_profit()}")
        p1 = obj.get_profit() - int(obj.get_turnover() * (.075 / 100))
        p2 = obj.get_profit() - int(obj.get_turnover() * (.055 / 100))
        p3 = obj.get_profit() - int(obj.get_turnover() * (.025 / 100))
        # log(f"  (8) net profit (nominal) (.075%, .055%, .025%): {p1}, {p2} ,{p3}")
        pp1 = round((((p1 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
        pp2 = round((((p2 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
        pp3 = round((((p3 / run_time_window) * 60 * 24 * 365) / obj.value_limit) * 100, 2)
        print(" ")
        print(self.mpi, " Try: 2 / ", x_try + 1, " -" * 60)
        print(f"Gross pr.: {obj.get_profit()} net pr.: {pp1}%, {pp2}% ,{pp3}% tr/day: {obj.get_transaction_per_day()} ddown: {obj.ddown}")
        print("Settings:", setings)

        return

    def calibrate(self):
        # src_array = self.s['src_array']
        all_setings = self.s['all_setings']
        symbol = self.s['symbol']
        x_from = self.s['x_from']
        x_to = self.s['x_to']
        value_limit = self.s['value_limit']
        stock_size = self.s['stock_size']
        pre_low = self.s['pre_low']
        pre_high = self.s['pre_high']
        pre_ohlc4 = self.s['pre_ohlc4']
        sig = self.s['sig']
        y_predict_sig = self.s['y_predict_sig']
        y_predict_strength = self.s['y_predict_strength']
        pre_date = self.s['pre_date']
        run_time_window = self.s['run_time_window']
        trade_strategy = self.s['trade_strategy']

        for x in range(len(all_setings)):
            first_ok = False
            first_p1 = 0
            for x_try in range(2):
                p_strength_filter = all_setings[x]["p_strength_filter"]
                p_monitor_window_size = all_setings[x]["p_monitor_window_size"]
                p_monitor_profit = all_setings[x]["p_monitor_profit"]
                p_monitor_std = all_setings[x]["p_monitor_std"]
                p_steps_limit = all_setings[x]["p_steps_limit"]
                p_trailer_stop = all_setings[x]["p_trailer_stop"]
                p_stop_loss_limit = all_setings[x]["p_stop_loss_limit"]
                p_trailer_min_profit = all_setings[x]["p_trailer_min_profit"]
                setings = all_setings[x]

                algo_main = n_algo_trade()
                algo_main.config({"name": symbol + " Ai " + str(x_from) + " - " + str(x_to),
                                  "id": 1,
                                  "value_limit": value_limit,
                                  "stock_size": stock_size,
                                  "stop_loss_limit": -stock_size * (p_stop_loss_limit / 100),
                                  "profit_take_limit": -1,  # -1 nincs bekapcsolva, amúgy nominálisan mondja usd ben
                                  "trailer_stop": p_trailer_stop,
                                  # .15 = 15% ennyivel eshet vissz a aktuális profit a legmagasabb trailer profithoz képest
                                  "trailer_min_profit": p_trailer_min_profit,  # nominal in usd
                                  "value_limit_profit_reinvest": False,
                                  "steps_limit": p_steps_limit,
                                  "strategy": trade_strategy,
                                  "trade_time_start": (0, 1),
                                  "trade_time_stop": (23, 59),
                                  "next_price_random": True,
                                  "enter_limit_order": False,  # limit = actual_ohlc4
                                  "strength_filter": p_strength_filter,
                                  "monitor_window_size": int(p_monitor_window_size),
                                  "monitor_profit": p_monitor_profit,
                                  "monitor_std": p_monitor_std
                                  })

                for ix in range(0, x_to - x_from):
                    price_dict = {
                        "actual_low": pre_low[ix],
                        "actual_high": pre_high[ix],
                        "actual_ohlc4": pre_ohlc4[ix],
                        "next_low": pre_low[ix + 1],
                        "next_high": pre_high[ix + 1],
                        "next_ohlc4": pre_ohlc4[ix + 1]}

                    algo_main.transaction(sig[ix], y_predict_sig[ix],
                                          y_predict_strength[ix],
                                          price_dict, pre_date[ix], x_from + ix)

                p1 = algo_main.get_profit() - int(algo_main.get_turnover() * (.075 / 100))
                pp1 = round((((p1 / run_time_window) * 60 * 24 * 365) / algo_main.value_limit) * 100, 2)

                if x_try == 0:
                    if pp1 > self.get_max_p1():
                        self.summary(algo_main, run_time_window, setings, x_try)
                        first_ok = True
                        first_p1 = pp1
                        if pp1 < 0:
                            self.set_max_p1((pp1 + first_p1) / 2)
                else:
                    if pp1 > 0 and first_ok:
                        self.summary(algo_main, run_time_window, setings, x_try)
                        self.set_max_p1((pp1 + first_p1) / 2)

                del algo_main

                if pp1 <= 0:
                    break

            if x % 2 == 0 and self.process == self.cores - 1:
                print("\r" + str(100 * round(x / len(all_setings), 2))[:6] + " %,  Done: ",
                      x, "   Max p1:", round(self.get_max_p1(), 4), "%",
                      end="")
            #     r0 = str(np.count_nonzero(r_array == 0))
            #     r1 = str(np.count_nonzero(r_array == 1))
            #     r2 = str(np.count_nonzero(r_array == 2))
            #     print(f"{self.mpi} - 0:{r0}   1:{r1}   2:{r2}")
        if self.process == self.cores - 1:
            print(" ")


if __name__ == '__main__':
    pass
