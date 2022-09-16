import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime
import asyncio

from multiprocessing import shared_memory, Lock, Pool, cpu_count

lock = Lock()

from threading import Thread
import pickle


class n_tech_mp:

    def __init__(self, param_mp):
        self.s = param_mp
        self.temp_path = "C:\\Users\\ivanh\\PycharmProjects\\nDot\\temp\\"
        self.cores = self.s['cores']  # összesen hány process van
        self.process = self.s['process']  # én hanyadik process vagyok
        self.mpi = str(self.process + 1) + "/" + str(self.cores) + " core ->"
        if self.process == 7:
            print(self.mpi, "multiprocessing P10INT starts. Last speak.")
        self.tech()

    @staticmethod
    def prob_profit(low_np, high_np, price_slices, profit_limit, prob_limit):
        if np.isnan(low_np).any() or np.isnan(low_np).any():
            return 10

        # print("5")
        high_mean = np.mean(high_np)
        low_mean = np.mean(low_np)

        tick_size = (high_mean - low_mean) / price_slices
        # print(f"{self.mpi} tick_size {tick_size}   high_mean: {high_mean}   low_mean: {low_mean}")

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

    def tech(self):

        # profit_limit = float(self.s['profit_limit']) / 100
        # prob_limit = float(self.s['prob_limit']) / 100
        # time_frame = int(self.s['time_frame'])  ## hán perces idő intervallumot figyel előre
        # log("  Settings: profit limit: " + str(profit_limit * 100) + "%,   Prob. limit: " +
        #     str(round(prob_limit * 100, 2)) + "%   Time frame: " + str(time_frame))
        full_time_traded_istrument = True  # kriptókhoz
        price_slices = float(self.s['price_slices'])
        # log("  Tick size: " + str(tick_size))
        # date_s = self.s['date_s_slice']
        # low_s = self.s['low_s_slice']
        # high_s = self.s['high_s_slice']
        # print(self.mpi, len(low_s))

        r_array = np.full(len(self.s['low_s_slice']), 9)  #
        for g in range(0, len(self.s['low_s_slice']) - self.s['time_frame'] - 1):  ## végigmegyek a low vektoron minus time frame
            # if (16 <= date_s[g].hour <= 20 and np.is_busday(
            #         date_s[g].date())) or full_time_traded_istrument:  # nézem akereskedési időt és a munkanapot
            low_np = self.s['low_s_slice'][g: g + self.s['time_frame']]
            high_np = self.s['high_s_slice'][g: g + self.s['time_frame']]
            pr = self.prob_profit(low_np, high_np, price_slices, self.s['profit_limit'], self.s['prob_limit'])
            # print(self.mpi, g)
            r_array[g] = pr
            if g % 1000 == 0 and self.process == 7:
                print("\r" + str(100 * round(g / (len(self.s['low_s_slice']) - self.s['time_frame'] - 1), 2)) + " % ", end="")
            #     r0 = str(np.count_nonzero(r_array == 0))
            #     r1 = str(np.count_nonzero(r_array == 1))
            #     r2 = str(np.count_nonzero(r_array == 2))
            #     print(f"{self.mpi} - 0:{r0}   1:{r1}   2:{r2}")
        if self.process == 7:
            print(" ")

        # print(self.mpi, "Result: ")
        # print("  0 = Under limit: " + str(np.count_nonzero(r_array == 0)))
        # print("  1 = Long over limit: " + str(np.count_nonzero(r_array == 1)))
        # print("  2 = Shor over limit: " + str(np.count_nonzero(r_array == 2)))

        file_name = self.temp_path + 'P10INT_MP_RESULT' + str(self.process)
        np.save(file_name, r_array)

if __name__ == '__main__':
    pass
