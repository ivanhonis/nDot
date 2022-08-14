import random
import time

import pandas as pd
import numpy as np
import datetime
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BooleanFilter, CDSView, DataRange1d
from bokeh.models.callbacks import CustomJS
# from bokeh.models import HoverTool, ColumnDataSource, BooleanFilter, CDSView, Range1d, Span
from bokeh.layouts import column
# from math import radians


class n_algo_trade:

    def __init__(self):

        # settings -----------------------------
        self.name = "Name"
        self.trailer_stop = .5
        self.profit_take_limit = -1   # -1 nincs bekpcsolva
        self.stock_size = 5000  # in USD
        self.stop_loss_limit = -10  # in USD
        self.trailer_min_profit = 10  # in USD
        self.value_limit = 30000  # maximum value of opened position
        self.value_limit_profit_reinvest = True  # a megkeresett pénz be lehet fektetni
        self.steps_limit = 30  # 0 azt jelenti hogy nincs steps limit
        self.strategy = 1
        self.trade_time_start = (15, 30)
        self.trade_time_stop = (21, 30)
        self.next_price_random = False
        # ---------------------------------------
        self.actual_qt = 0
        self.avg_income_price = 0
        self.avg_income_price_h = 0
        self.income_value = 0  # position + avg_price
        self.actual_price = 0
        self.actual_date_time = ""
        self.trailer_profit = 0  # non realised profit or loss
        self.realised_profit = 0
        self.deal_count = 0
        self.closed_deal_count = 0
        self.act_profit = 0
        self.steps = 0
        self.stock_size_orig = 0
        self.price_dict = {}
        # hisory -------------------------
        self.sig_way_memory = np.zeros(11)
        self.sig_way = 0
        self.history = pd.DataFrame(None)
        self.chart_elements = list()
        self.h_buy = False
        self.h_sell = False
        self.h_stop = False
        self.h_stop_price = 0
        self.h_stop_type = ""
        self.trading_days = {}
        self.y_predict_strength = 0
        self.y_predict = 0
        self.h_actual_realised_pnl = 0
        self.turnover = 0
        # silent investor -------------------------------
        self.silent_investor_orig_amount = 0
        self.silent_investor_actual_amount = 0
        self.silent_investor_qt = 0
        self.silent_investor_profit = 0

    def config(self, conf_dict):
        self.name = conf_dict["name"]
        self.value_limit = conf_dict["value_limit"]
        self.stock_size = conf_dict["stock_size"]
        self.stock_size_orig = conf_dict["stock_size"]
        self.stop_loss_limit = conf_dict["stop_loss_limit"]
        self.trailer_stop = conf_dict["trailer_stop"]
        self.trailer_min_profit = conf_dict["trailer_min_profit"]
        self.value_limit_profit_reinvest = conf_dict["value_limit_profit_reinvest"]
        self.steps_limit = conf_dict["steps_limit"]
        self.strategy = conf_dict["strategy"]
        self.trade_time_start = conf_dict["trade_time_start"]
        self.trade_time_stop = conf_dict["trade_time_stop"]
        self.next_price_random = conf_dict["next_price_random"]
        self.profit_take_limit = conf_dict["profit_take_limit"]
        self.silent_investor_actual_amount = float(conf_dict["value_limit"])
        self.silent_investor_orig_amount = float(conf_dict["value_limit"])
        
    def get_sig_way(self, sig):

        m_sig = 0
        if sig == 4:
            m_sig = 0
        elif sig == 0:
            m_sig = 1
        elif sig == 1:
            m_sig = -1

        self.sig_way_memory = np.delete(self.sig_way_memory, 0)
        self.sig_way_memory = np.append(self.sig_way_memory, m_sig)
        # print(self.sig_way_memory, " ----------- ", self.sig_way_memory.sum(), self.sig_way_memory.mean())
        return self.sig_way_memory.mean()


    @property
    def value_limit_actual(self):
        # ez a kezdeti value limithez képest tartalmazza a realizált profitot és veszteséget
        # ha profit reinvest van akkor mehet a value limit felé is
        if self.value_limit_profit_reinvest:
            return max(self.value_limit + self.realised_profit, 0)
        else:
            return max(min(self.value_limit + self.realised_profit, self.value_limit), 0)

    @property
    def actual_value(self):
        return self.actual_qt * self.actual_price

    @property
    def open_limit(self):
        return self.value_limit_actual - abs(self.actual_qt) * self.avg_income_price

    def buy(self, buy_qt):
        # print("buy" , buy_qt)
        trade_price = self.next_rnd_price("buy")
        self.income_value += round(buy_qt * trade_price, 8)
        self.turnover += buy_qt * trade_price
        self.actual_qt += buy_qt
        self.avg_income_price = self.income_value / self.actual_qt
        self.avg_income_price_h = self.avg_income_price
        self.trailer_profit = round((trade_price - self.avg_income_price) * self.actual_qt, 8)
        self.deal_count += 1

        # if not self.next_price_random:
        #     trade_price = self.next_rnd_price
        #     self.income_value += int(buy_qt * trade_price)
        #     self.actual_qt += buy_qt
        #     self.avg_income_price = self.income_value / self.actual_qt
        #     self.trailer_profit = int((trade_price - self.avg_income_price) * self.actual_qt)
        #     self.deal_count += 1
        #     return True
        # else:
        #     trade_price = self.next_rnd_price
        #     if trade_price <= self.actual_price:
        #         self.income_value += int(buy_qt * trade_price)
        #         self.actual_qt += buy_qt
        #         self.avg_income_price = self.income_value / self.actual_qt
        #         self.trailer_profit = int((trade_price - self.avg_income_price) * self.actual_qt)
        #         self.deal_count += 1
        #         return True
        #     else:
        #         return False
            
    def sell(self, sell_qt):
        trade_price = self.next_rnd_price("sell")
        self.income_value -= round(sell_qt * trade_price, 8)
        self.turnover += sell_qt * trade_price
        self.actual_qt -= sell_qt
        self.avg_income_price = self.income_value / self.actual_qt
        self.avg_income_price_h = self.avg_income_price
        self.trailer_profit = round((trade_price - self.avg_income_price) * self.actual_qt, 8)
        self.deal_count += 1

        return True

        # if not self.next_price_random:
        #     # ha sell akkor is pozitív a qt
        #     trade_price = self.next_rnd_price
        #     self.income_value -= int(sell_qt * trade_price)
        #     self.actual_qt -= sell_qt
        #     self.avg_income_price = self.income_value / self.actual_qt
        #     self.trailer_profit = int((trade_price - self.avg_income_price) * self.actual_qt)
        #     self.deal_count += 1
        #     return True
        # else:
        #     # ha sell akkor is pozitív a qt
        #     trade_price = self.next_rnd_price
        #     if trade_price >= self.actual_price:
        #         self.income_value -= int(sell_qt * trade_price)
        #         self.actual_qt -= sell_qt
        #         self.avg_income_price = self.income_value / self.actual_qt
        #         self.trailer_profit = int((trade_price - self.avg_income_price) * self.actual_qt)
        #         self.deal_count += 1
        #         return True
        #     else:
        #         return False

    def stop(self):
        if self.actual_qt > 0:
            trade_price = self.next_rnd_price("sell")
        else:
            trade_price = self.next_rnd_price("buy")
            
        self.h_stop_price = trade_price
        self.turnover += self.actual_qt * trade_price
        self.h_stop = True  # regisztrálom a hisztoriba
        self.h_actual_realised_pnl = int((trade_price - self.avg_income_price) * self.actual_qt)
        self.realised_profit += self.h_actual_realised_pnl
        self.actual_qt = 0
        self.avg_income_price_h = self.avg_income_price
        self.avg_income_price = 0
        self.income_value = 0  # position + avg_price
        self.trailer_profit = 0
        self.act_profit = 0
        self.deal_count += 1
        self.closed_deal_count += 1
        if self.open_limit <= 0:
            print(f"Minden elúszott :)  TARTOZÁS: {self.value_limit - abs(self.realised_profit)}")

    def get_profit_per_day(self):
        return round(self.realised_profit / len(self.trading_days.keys()), 2)

    def get_turnover(self):
        return self.turnover

    def get_profit(self):
        return int(self.realised_profit)

    def get_profit_per_closed_deal(self):
        try:
            i_ret = round(self.realised_profit / self.closed_deal_count, 2)
        except:
            return 0
        else:
            return i_ret

    def get_closed_deal_per_day(self):
        return round(self.closed_deal_count / len(self.trading_days.keys()), 2)

    def get_transaction_per_day(self):
        return round(self.deal_count / len(self.trading_days.keys()), 2)

    def trailer(self):
        self.act_profit = int((self.actual_price - self.avg_income_price) * self.actual_qt)

        if self.actual_qt != 0 and self.act_profit != self.trailer_profit:
            
            if self.act_profit > self.profit_take_limit != -1:
                self.h_stop_type = "sPT"  # stop Profit take
                self.stop()
                i_return = True
            else:
                if self.act_profit < self.stop_loss_limit:
                    self.h_stop_type = "sLS"  # stop loss
                    self.stop()
                    i_return = True
                else:
                    percent = (1 - self.trailer_stop)
                    if self.act_profit < self.trailer_profit * percent and self.trailer_stop != -1:
                        if self.act_profit < self.trailer_min_profit:
                            self.trailer_profit = max(self.act_profit, self.trailer_profit)
                            # print("trailer visszaesés, de tovább engedi, mert nincs meg a minimum profit")
                            i_return = False
                        else:
                            self.h_stop_type = "sTR"  # trailer stop
                            # print("trailer visszaesés - stop")
                            self.stop()
                            i_return = True
                    else:
                        # if self.act_profit < self.trailer_profit:
                        #     print("trailer stagnál  - visszaesés még tűréshatáron beül")
                        # else:
                        #     # print(self.trailer_profit, self.act_profit, self.trailer_profit)
                        #     print("trailer növekedés")
                        self.trailer_profit = max(self.act_profit, self.trailer_profit)
                        i_return = False
        else:
            i_return = False
            # print("trailer csöndben van mert nincs változás")
        return i_return

    def get_stock_qt(self):
        return round(self.stock_size / self.actual_price, 8)

    def print_position(self):
        print(f"qt: {self.actual_qt}  " +
              f"avg_income_price: {round(self.avg_income_price, 2)}  " +
              f"income_value: {self.income_value}  " +
              f"actual_price: {self.actual_price}  " +
              f"actual_value: {self.actual_value}  " +
              # f"act_profit: {self.act_profit}  " +
              f"realised_profit: {self.realised_profit}  " +
              f"open_limit: {self.open_limit}  " +
              f"steps: {self.steps}  ")

    def get_position(self):
        return [self.realised_profit, self.deal_count]

        # return (f"profit: {self.profit} qt: {self.qt} avg_income_price:" +
        #       f"{round(self.avg_income_price, 2)} income_volume: {self.income_volume}" +
        #         f" trailer_profit: {self.trailer_profit} deal count: {self.deal_count}")

    def get_pd(self):
        return {'realised_profit': self.realised_profit,
                'act_profit': self.trailer_profit,
                'trailer_profit': self.trailer_profit,
                'stock_size': self.stock_size}

    def a_log(self, text):
        print(text)

    def next_rnd_price(self, buy_or_sell):
        if self.next_price_random:
            # if buy_or_sell == "buy":
            # # next_low = self.price_dict['next_low']
            # # next_high = self.price_dict['next_high']
            # # i_rnd_price = next_low + (((next_high - next_low) / 100) * random.randint(0, 101))
            # elif buy_or_sell == "sell":
            #     return self.price_dict['next_high']

            next_low = self.price_dict['next_low']
            next_high = self.price_dict['next_high']
            steps = round(next_high * 100, 0) - round(next_low * 100, 0) + 1
            i_rnd_price1 = next_low + (((next_high - next_low) / steps) * random.randint(0, steps + 1))
            i_rnd_price1 = max(min(i_rnd_price1, next_high), next_low)
            return i_rnd_price1
        else:
            return self.price_dict['actual_ohlc4']

    def transaction(self, sig, y_predict, y_predict_strength, price_dict, date_time):
        self.sig_way = self.get_sig_way(y_predict)
        self.y_predict = y_predict
        self.price_dict = price_dict.copy()
        self.y_predict_strength = y_predict_strength
        self.actual_price = self.price_dict['actual_ohlc4']
        self.actual_date_time = date_time
        decision1, qt1 = self.decision(sig, y_predict, y_predict_strength)
        # print(decision1, qt1)
        decision2, qt2 = self.limit(decision1, qt1)
        # print("Limit", decision2, qt2)
        self.action(decision2, qt2, date_time)

    def decision(self, sig, y_predict, y_predict_strength):

        if self.strategy == 66:  # signal drived
            if y_predict == 1 and y_predict_strength > .999:
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 2 and y_predict_strength > .999:
                decision = "SELL"
                decision_qt = 0
            else:
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt

        elif self.strategy == 1:  # signal drived
            if sig == 0 and y_predict_strength > .9:
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif sig == 1 and y_predict_strength > .9:
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt


        elif self.strategy == 2:  # ai decision if agree
            if sig == 0 and y_predict == 0 and y_predict_strength > .95:
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif sig == 1 and y_predict == 1 and y_predict_strength > .95:
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt

        elif self.strategy == 21:  # ai decision override
            if y_predict == 0:
                self.stock_size = self.stock_size_orig
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 1:
                self.stock_size = self.stock_size_orig
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                self.stock_size = 0
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt

        elif self.strategy == 22:  # ai decision override
            if y_predict == 0:
                self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 1:
                self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                self.stock_size = 0
                decision = "NONE"
                decision_qt = 0
            # print(y_predict, decision, decision_qt)
            return decision, decision_qt
        
        elif self.strategy == 23:  # ai decision override
            if y_predict == 0 and y_predict_strength > .95:
                self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 1 and y_predict_strength > .95:
                self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                self.stock_size = 0
                decision = "NONE"
                decision_qt = 0
            # print(y_predict, decision, decision_qt)
            return decision, decision_qt

        elif self.strategy == 44:  # ai decision + sig_way
            if y_predict == 0 and self.sig_way > 0:
                self.stock_size = self.stock_size_orig
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 1 and self.sig_way < 0:
                self.stock_size = self.stock_size_orig
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                self.stock_size = 0
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt

        elif self.strategy == 45:  # ai decision + sig_way
            if y_predict == 0 and self.sig_way < 0.5:
                self.stock_size = self.stock_size_orig
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif y_predict == 1 and self.sig_way > 0.5:
                self.stock_size = self.stock_size_orig
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                self.stock_size = 0
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt



        # elif self.strategy == 22:  # ai decision override
        #     self.act_profit = int((self.actual_price - self.avg_income_price) * self.actual_qt)
        #     if self.act_profit < self.trailer_profit or self.act_profit == 0:
        #         if y_predict == 0:
        #             self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
        #             decision = "BUY"
        #             decision_qt = self.get_stock_qt()
        #         elif y_predict == 1:
        #             self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
        #             decision = "SELL"
        #             decision_qt = self.get_stock_qt()
        #         else:
        #             self.stock_size = 0
        #             decision = "NONE"
        #             decision_qt = 0
        #     else:
        #         self.stock_size = 0
        #         decision = "NONE"
        #         decision_qt = 0
        #     return decision, decision_qt

        elif self.strategy == 3:  # ai limitter

            if y_predict == sig:
                self.stock_size = self.stock_size_orig * (1 + y_predict_strength)
            else:
                self.stock_size = self.stock_size_orig * .33
            if sig == 0:
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif sig == 1:
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
                decision = "NONE"
                decision_qt = 0
            return decision, decision_qt

        else:
            decision = "NONE"
            decision_qt = 0
            return decision, decision_qt

    def limit(self, decision, decision_qt):
        # beszerzési értékhez képest még belefér az aktuális vétel?
        # aza open_limitbe még belefér a vétel

        if (decision == "BUY" and self.actual_qt > 0) or (decision == "SELL" and self.actual_qt < 0):
            mod_income_value = self.income_value
        else:
            mod_income_value = 0
        # ez azért kell mert ha átfordulás van buy ból sell be vagy vissza akkor a stop nullázza az income valuet
        # és akkor csak nullártól indulva kell nézni, hogy a mennyiség jó e

        if abs(mod_income_value) + (abs(decision_qt) * self.actual_price) > self.value_limit_actual:
            cutter_qt = int((abs(mod_income_value) + (abs(decision_qt) * self.actual_price) - self.value_limit_actual) / self.actual_price)
            decision_qt = abs(decision_qt) - cutter_qt

        if decision_qt == 0:
            decision = "NONE"
        return decision, decision_qt

    def action(self, decision, decision_qt, date_time):
        self.avg_income_price_h = self.avg_income_price
        dt = np.datetime64(date_time).tolist().time()
        dd = np.datetime64(date_time).tolist().date()
        is_in_trade_time = datetime.time(*self.trade_time_start) < dt < datetime.time(*self.trade_time_stop)
        # print(is_in_trade_time)

        self.h_buy = False
        self.h_sell = False
        self.h_actual_realised_pnl = 0
        if is_in_trade_time and np.is_busday(dd) or True:
            self.trading_days[str(dd)] = 0  # day register for deal
            if (self.steps < self.steps_limit or self.steps_limit == 0) and decision != "STOP":
                if decision == "BUY":
                    if self.actual_qt < 0:
                        self.h_stop_type = "sDW"  # átfordulóós stop
                        # print("Buy ból SELL be fordulok")
                        self.stop()
                    self.buy(decision_qt)
                    self.steps = 0
                    self.h_buy = True
                elif decision == "SELL":
                    if self.actual_qt > 0:
                        self.h_stop_type = "sUP"  # átfordulós stop
                        # print("SELL ből BUY be fordulok")
                        self.stop()
                    self.sell(decision_qt)
                    self.steps = 0
                    self.h_sell = True
                elif decision == "NONE":
                    if self.trailer():
                        self.steps = 0
                    else:
                        if self.steps_limit != 0:
                            if self.actual_qt != 0:
                                self.steps += 1
                            else:
                                self.steps = 0
            else:
                if self.actual_qt != 0:
                    if decision == "STOP":
                        self.h_stop_type = "sDecision"  # step túllépésmiatt stop
                    else:
                        self.h_stop_type = "sSteps"  # step túllépésmiatt stop
                    # stop STep
                    self.stop()
                    self.steps = 0
        else:
            if self.actual_qt != 0:
                self.h_stop_type = "sTime"  # kereskedési idő leájárata miatt stop
                # stop Time
                self.stop()
                self.steps = 0
        self.add_history()

    def add_history(self):
        if self.silent_investor_qt == 0:
            # ha még nics semmije akkor ohc4en megkapja amennyiséget
            self.silent_investor_qt = round(self.silent_investor_actual_amount / self.actual_price, 8)
            self.silent_investor_profit = 0
        else:
            # ha már van akkor kiszámolom az értékét és a profitját
            self.silent_investor_actual_amount = self.silent_investor_qt * self.actual_price
            self.silent_investor_profit = self.silent_investor_actual_amount - self.silent_investor_orig_amount

        add = {"steps": self.steps,
               "actual_qt": self.actual_qt,
               "avg_income_price": self.avg_income_price_h,
               "income_value": self.income_value,
               "actual_price": self.actual_price,
               "next_low_price": self.price_dict['next_low'],
               "next_high_price": self.price_dict['next_high'],
               "actual_date_time": self.actual_date_time,
               "trailer_profit": self.trailer_profit,
               "realised_profit": self.realised_profit,
               "act_profit": self.act_profit,
               "value_limit_actual": self.value_limit_actual,
               "actual_value": self.actual_value,
               "buy": self.h_buy,
               "sell": self.h_sell,
               "stop": self.h_stop,
               "stop_type": self.h_stop_type,
               "stock_size": self.stock_size,
               "y_predict_strength": self.y_predict_strength,
               "h_actual_realised_pnl": self.h_actual_realised_pnl,
               "h_stop_price": self.h_stop_price,
               "y_predict": self.y_predict,
               "sig_way": self.sig_way,
               "silent_investor_profit": self.silent_investor_profit
               }

        x = pd.DataFrame.from_dict(add, orient='index').T
        self.history = pd.concat([self.history, x])
        self.history['buy'] = self.history['buy'].astype('bool')
        self.history['sell'] = self.history['sell'].astype('bool')
        self.history['stop'] = self.history['stop'].astype('bool')
        # print(self.history)
        # time.sleep(2)
        #vissza állítom
        self.h_buy = False
        self.h_sell = False
        self.h_stop = False

    def show_history(self, last_n=10000000):
        output_file("bokeh_html/" + self.name + "_algo_history.html")
        hdf = self.history.copy()
        hdf = hdf.reset_index(drop=True)
        # hdf['index'] = hdf['actual_date_time']
        # hdf.set_index("actual_date_time", inplace=True)

        def algo_price_chart(hdf):
            hdf["actual_price_y_perc"] = hdf["actual_price"] * 1.001  # feliratokhoz
            hdf["actual_price_stop"] = hdf["actual_price"] * 1.002  # feliratokhoz
            hdf["actual_price_steps"] = hdf["actual_price"] * .998  # feliratokhoz
            hdf["actual_price_y_predict"] = hdf["actual_price"] * .997  # feliratokhoz
            hdf["actual_price_sig_way"] = hdf["actual_price"] * .996  # feliratokhoz
            hdf["avg_income_price"].replace(0, np.nan, inplace=True)
            
            # megcsinálom a feliratokat string formában
            hdf['sig_way'] = hdf['sig_way'] * 100
            hdf['sig_way'] = hdf['sig_way'].astype(int)
            hdf['sig_way'] = hdf['sig_way'].astype(str)
            
            hdf['steps'] = hdf['steps'].astype(int)
            hdf['steps'] = hdf['steps'].astype(str)

            hdf['y_predict'] = hdf['y_predict'].astype(int)
            hdf['y_predict'] = hdf['y_predict'].astype(str)
            
            hdf['h_actual_realised_pnl'] = hdf['h_actual_realised_pnl'].astype(int)
            hdf['h_actual_realised_pnl'] = hdf['h_actual_realised_pnl'].astype(str)

            hdf['stop_type_pnl'] = hdf['stop_type'] + " " + hdf['h_actual_realised_pnl'] + "$"
            
            hdf['y_predict_strength'] = hdf['y_predict_strength'] * 100
            hdf['y_predict_strength'] = hdf['y_predict_strength'].astype(int)
            hdf['y_predict_strength'] = hdf['y_predict_strength'].astype(str) + "%"

            deals = ColumnDataSource(hdf)

            p = figure(sizing_mode='fixed',
                       tools="xpan,xwheel_zoom,reset",
                       active_drag='xpan',
                       active_scroll='xwheel_zoom',
                       x_axis_type='datetime',
                       toolbar_location="left",
                       plot_width=1330,
                       plot_height=250,
                       y_axis_location="right",
                       title=self.name + " - price",
                       )


            p.vbar(x='index', width=0.7, top='next_high_price', bottom='next_low_price', fill_color="#A7DBD8",
                   fill_alpha=.5, line_color="#A7DBD8", source=deals, legend_label="next low & high")
            p.line('index', 'actual_price', color="#0000ff", legend_label="actual OHLC4", source=deals)
            p.line('index', 'avg_income_price', color="#ff9100", line_width=2, legend_label="avg income price", source=deals)

            sig = tuple(hdf["buy"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.triangle('index', 'actual_price', color="#00ff00", size=10, source=deals, view=view_sig)

            sig = tuple(hdf["sell"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'actual_price', color="#ff0000", size=10, source=deals, view=view_sig)

            sig = tuple(hdf["stop"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.legend.title = 'Trade history'
            p.circle('index', 'h_stop_price', color="#000000", size=3, source=deals, view=view_sig)
            p.text('index', 'actual_price_stop', text="stop_type_pnl", text_font_size="8pt", text_color="#000000", source=deals, view=view_sig)
            p.text('index', 'actual_price_steps', text="steps", text_font_size="8pt", text_color="#0000ff", source=deals)
            p.text('index', 'actual_price_y_predict', text="y_predict", text_font_size="8pt", text_color="#756A34", source=deals)
            # p.text('index', 'actual_price_sig_way', text="sig_way", text_font_size="8pt", text_color="#ff0000", source=deals)

            sig = tuple(hdf["buy"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.text('index', 'actual_price_y_perc', text="y_predict_strength", text_font_size="8pt", text_color="#00ff00", source=deals, view=view_sig)

            sig = tuple(hdf["sell"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.text('index', 'actual_price_y_perc', text="y_predict_strength", text_font_size="8pt", text_color="#ff0000", source=deals, view=view_sig)

            p.legend.location = "top_left"
            p.legend.label_text_font_size = '8pt'
            p.legend.background_fill_alpha = 0.5

            callback = CustomJS(args=dict(p=p), code="""
            clearTimeout(window._autoscale_timeout);
            var cv_price = cb_obj.plots[0].renderers[0].data_source.data.actual_price;
            var x_start = p.x_range.start;
            var x_end = p.x_range.end;
            var x_start_int = Math.floor(x_start);
            var x_end_int = Math.floor(x_end);
            x_start_int = Math.max(x_start_int, 1);

            var cv_price_slice = cv_price.slice(x_start_int,x_end_int);
            var cv_max = Math.max(...cv_price_slice);
            var cv_min = Math.min(...cv_price_slice);
            window._autoscale_timeout = setTimeout(function() {
                p.y_range.start = cv_min * .996;
                p.y_range.end = cv_max * 1.003;
            });
            """)


            p.x_range.js_on_change('start', callback)

            # xaxis labell   ---------------------------------------------------------------------------------------
            label_dic = {}

            for i_i, i_date in enumerate(tuple(hdf['actual_date_time'])):
                label_dic[i_i] = f"{i_date.hour}:{i_date.minute}"

            p.xaxis.major_label_overrides = label_dic
            # p.x_range.range_padding = 60
            # p.xaxis.ticker.desired_num_ticks = 60
            p.xaxis.major_label_orientation = 3.14 / 8

            return p

        def algo_limit_chat():
            hdf["abs_income_value"] = abs(hdf["income_value"])
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=120,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset")
            p.vbar(x='index', top='value_limit_actual', width=1, color="#5555ff", legend_label="value limit actual", source=deals)
            p.vbar(x='index', top='abs_income_value', width=0.7, color="#55ff55", legend_label="income value", source=deals)
            p.vbar(x='index', top='stock_size', width=0.2, color="#ff5555", legend_label="stock_size value", source=deals)
            p.legend.title = 'Limits'
            p.legend.location = "top_left"
            p.legend.label_text_font_size = '8px'
            p.legend.background_fill_alpha = 0.5
            return p

        def actual_profit():
            hdf["abs_income_value"] = abs(hdf["income_value"])
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=120,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset")
            
            p.vbar(x='index', top='h_actual_realised_pnl', width=1, color="#5555ff", legend_label="actual_realised_pnl", source=deals)

            p.legend.title = 'Profit per deal'
            p.legend.location = "top_left"
            p.legend.label_text_font_size = '10px'
            p.legend.background_fill_alpha = 0.5
            return p

        def algo_qt_chart():
            hdf["actual_qt"].replace(0, np.nan, inplace=True)
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=80,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset")
            p.vbar(x='index', top='actual_qt', width=1, color="#5555ff", legend_label="qt", source=deals)
            p.legend.title = 'Actual stock (qt)'
            p.legend.location = "top_left"
            p.legend.label_text_font_size = '8px'
            p.legend.background_fill_alpha = 0.5
            return p

        def algo_profit_chart():
            hdf["profit_rpa"] = hdf["realised_profit"] + hdf["act_profit"]
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=150,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset")


            p.line('index', 'realised_profit', color="#0000ff", line_width=4, legend_label="realised profit",
                   source=deals)
            p.line('index', 'silent_investor_profit', color="#00ff00", line_width=1, legend_label="silent investro",
                   source=deals)
            p.line('index', 'profit_rpa', color="#ff9100", line_width=1, legend_label="actual profit", source=deals)
            p.legend.location = "top_left"
            p.legend.title = 'Realised profit'
            p.legend.label_text_font_size = '8pt'
            p.legend.background_fill_alpha = 0.5
            return p

        # show ---------------------------------------------------------------
        self.chart_elements.append(algo_price_chart(hdf))
        self.chart_elements.append(algo_qt_chart())
        self.chart_elements.append(algo_profit_chart())
        self.chart_elements.append(actual_profit())
        self.chart_elements.append(algo_limit_chat())
        plots = []

        for i, e in enumerate(self.chart_elements):
            if i == 0:
                e.y_range = DataRange1d(only_visible=True)
                e.xaxis.visible = True
            else:
                e.x_range = self.chart_elements[0].x_range
                # e.y_range = self.elements[0].y_range
                e.xaxis.visible = False
                e.min_border_top = 0

        for e in self.chart_elements:
            plots.append(e)
        c = column(self.chart_elements)
        show(c)

# if __name__ == "__main__":
#     algo = n_algo_trade()
#
#     algo.config({"name": "APA",
#                  "value_limit": 16000,
#                  "stock_size": 5000,
#                  "stop_loss_limit": -10,
#                  "trailer_stop": .5,
#                  "trailer_min_profit": 10,
#                  "value_limit_profit_reinvest": True,
#                  "steps_limit": 30,
#                  "strategy": 1,
#                  "trade_time_start": (15, 30),
#                  "trade_time_stop": (21, 30)
#                  })
#
#     dt = np.datetime64('2013-06-03 13:14:00')
#     print(dt.tolist().time() > datetime.time(13, 0))
#     dt = dt + 60
#     algo.transaction(0, 0, 0.6, 20, dt)
#     algo.print_position()
#     dt = dt + 60
#     algo.transaction(4, 0, 0.6, 21, dt)
#     algo.print_position()
#     dt = dt + 60
#     algo.transaction(4, 0, 0.6, 22, dt)
#     algo.print_position()
#     dt = dt + 60
#     algo.transaction(4, 0, 0.6, 23, dt)
#     algo.print_position()
#     dt = dt + 60
#     algo.transaction(4, 0, 0.6, 24, dt)
#     algo.print_position()
#     dt = dt + 60
#     algo.transaction(4, 0, 0.6, 25, dt)
#     algo.print_position()
#     price = 26
#     for i in range(1, 1000):
#         price = max(price * (1 + (random.uniform(-2.9, 3)/100)), 8)
#         # print(price)
#         dt = dt + 60
#         algo.transaction(random.randint(0, 4), 0, 0.6, price, dt)
#     algo.show_history()
#
#
#
