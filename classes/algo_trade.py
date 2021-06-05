import random
import pandas as pd
import numpy as np
import datetime
from bokeh.io import output_file, show
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, BooleanFilter, CDSView, Range1d, DatetimeTickFormatter, DataRange1d
from bokeh.models.callbacks import CustomJS
# from bokeh.models import HoverTool, ColumnDataSource, BooleanFilter, CDSView, Range1d, Span
from bokeh.layouts import column
from math import radians


class algo_trade:

    def __init__(self):

        # settings -----------------------------
        self.name = "Name"
        self.trailer_stop = .5
        self.stock_size = 5000  # in USD
        self.stop_loss_limit = -10  # in USD
        self.trailer_min_profit = 10  # in USD
        self.value_limit = 30000  # maximum value of opened position
        self.value_limit_profit_reinvest = True  # a megkeresett pénz be lehet fektetni
        self.steps_limit = 30  # 0 azt jelenti hogy nincs steps limit
        self.strategy = 1
        self.trade_time_start = (15, 30)
        self.trade_time_stop = (21, 30)
        # ---------------------------------------
        self.actual_qt = 0
        self.avg_income_price = 0
        self.income_value = 0  # position + avg_price
        self.actual_price = 0
        self.actual_date_time = ""
        self.trailer_profit = 0  # non realised profit or loss
        self.realised_profit = 0
        self.deal_count = 0
        self.closed_deal_count = 0
        self.act_profit = 0
        self.steps = 0
        # hisory -------------------------
        self.history = pd.DataFrame(None)
        self.chart_elements = list()
        self.h_buy = False
        self.h_sell = False
        self.h_stop = False
        self.h_stop_type = "s"
        self.trading_days = {}

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
        self.income_value += int(buy_qt * self.actual_price)
        self.actual_qt += buy_qt
        self.avg_income_price = self.income_value / self.actual_qt
        self.trailer_profit = int((self.actual_price - self.avg_income_price) * self.actual_qt)
        self.deal_count += 1

    def sell(self, sell_qt):
        # ha sell akkor is pozitív a qt
        self.income_value -= int(sell_qt * self.actual_price)
        self.actual_qt -= sell_qt
        self.avg_income_price = self.income_value / self.actual_qt
        self.trailer_profit = int((self.actual_price - self.avg_income_price) * self.actual_qt)
        self.deal_count += 1

    def stop(self):
        self.h_stop = True  # regisztrlom a hsztoryba
        self.realised_profit += int((self.actual_price - self.avg_income_price) * self.actual_qt)
        self.actual_qt = 0
        self.avg_income_price = 0
        self.income_value = 0  # position + avg_price
        self.trailer_profit = 0
        self.deal_count += 1
        self.closed_deal_count += 1
        if self.open_limit <= 0:
            print(f"Minden elúszott :)  TARTOZÁS: {self.value_limit - abs(self.realised_profit)}")

    def get_profit_per_day(self):
        return round(self.realised_profit / len(self.trading_days.keys()), 2)

    def get_profit_per_closed_deal(self):
        return round(self.realised_profit / self.closed_deal_count, 2)

    def get_closed_deal_per_day(self):
        return round(self.closed_deal_count / len(self.trading_days.keys()), 2)

    def get_transaction_per_day(self):
        return round(self.deal_count / len(self.trading_days.keys()), 2)

    def trailer(self):
        self.act_profit = int((self.actual_price - self.avg_income_price) * self.actual_qt)

        if self.actual_qt != 0 and self.act_profit != self.trailer_profit:

            if self.act_profit < self.stop_loss_limit:
                self.h_stop_type = "sLS"
                # print("Stop loss")
                self.stop()
                i_return = True
            else:
                percent = (1 - self.trailer_stop)
                if self.act_profit < self.trailer_profit * percent:
                    if self.act_profit < self.trailer_min_profit:
                        self.trailer_profit = max(self.act_profit, self.trailer_profit)
                        # print("trailer visszaesés, de tovább engedi, mert nincs meg a minimum profit")
                        i_return = False
                    else:
                        self.h_stop_type = "sTR"
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
        return int(self.stock_size / self.actual_price)

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

    def transaction(self, sig, y_predict, y_predict_strength, price, date_time):
        self.actual_price = price
        self.actual_date_time = date_time
        decision1, qt1 = self.decision(sig, y_predict, y_predict_strength)
        decision2, qt2 = self.limit(decision1, qt1)
        # print(decision1, qt1, " -> ", decision2, qt2)
        self.action(decision2, qt2, date_time)

    def decision(self, sig, y_predict, y_predict_strength):
        if self.strategy == 1:  # signal drived
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

        elif self.strategy == 2:  # ai decision if agree
            if sig == 0 and y_predict == 0:
                decision = "BUY"
                decision_qt = self.get_stock_qt()
            elif sig == 1 and y_predict == 1:
                decision = "SELL"
                decision_qt = self.get_stock_qt()
            else:
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
            return decision, decision_qt

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

        if abs(self.income_value) + (abs(decision_qt) * self.actual_price) > self.value_limit_actual:
            cutter_qt = int((abs(self.income_value) + (abs(decision_qt) * self.actual_price) - self.value_limit_actual) / self.actual_price)
            decision_qt = abs(decision_qt) - cutter_qt

        if decision_qt == 0:
            decision = "NONE"
        return decision, decision_qt

    def action(self, decision, decision_qt, date_time):
        dt = np.datetime64(date_time).tolist().time()
        dd = np.datetime64(date_time).tolist().date()
        is_in_trade_time = datetime.time(*self.trade_time_start) < dt < datetime.time(*self.trade_time_stop)

        self.h_buy = False
        self.h_sell = False
        if is_in_trade_time and np.is_busday(dd):
            self.trading_days[str(dd)] = 0  # day register for deal
            if self.steps < self.steps_limit or self.steps_limit == 0:
                if decision == "BUY":
                    self.h_buy = True
                    if self.actual_qt < 0:
                        self.h_stop_type = "sDW"
                        # print("Buy ból SELL be fordulok")
                        self.stop()
                    self.buy(decision_qt)
                    self.steps = 0
                elif decision == "SELL":
                    self.h_sell = True
                    if self.actual_qt > 0:
                        self.h_stop_type = "sUP"
                        # print("SELL ből BUY be fordulok")
                        self.stop()
                    self.sell(decision_qt)
                    self.steps = 0
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
                    self.h_stop_type = "sST"
                    self.stop()
                    self.steps = 0
        else:
            if self.actual_qt != 0:
                self.h_stop_type = "sTi"
                self.stop()
                self.steps = 0
        self.add_history()

    def add_history(self):
        add = {"steps": self.steps,
               "actual_qt": self.actual_qt,
               "avg_income_price": self.avg_income_price,
               "income_value": self.income_value,
               "actual_price": self.actual_price,
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
               "stock_size": self.stock_size
               }
        self.history = self.history.append(add, ignore_index=True)
        self.history['buy'] = self.history['buy'].astype('bool')
        self.history['sell'] = self.history['sell'].astype('bool')
        self.history['stop'] = self.history['stop'].astype('bool')
        self.h_buy = False
        self.h_sell = False
        self.h_stop = False

    def show_history(self, last_n=10000000):
        output_file("bokeh_html/" + self.name + "_algo_history.html")
        hdf = self.history.tail(last_n).copy()
        # hdf['index'] = hdf['actual_date_time']
        # hdf.set_index("actual_date_time", inplace=True)

        def algo_price_chart():
            hdf["actual_price_stop"] = hdf["actual_price"] * 1.002
            hdf["actual_price_steps"] = hdf["actual_price"] * .998
            hdf["avg_income_price"].replace(0, np.nan, inplace=True)
            hdf['steps'] = hdf['steps'].astype(int)
            hdf['steps'] = hdf['steps'].astype(str)

            i_min = hdf['actual_price'].min() * .995
            i_max = hdf['actual_price'].max() * 1.005

            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=220,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset",
                       title=self.name + " - price")
                       # y_range=(i_min, i_max))

            # p.y_range = Range1d(i_min, i_max)

            p.line('index', 'actual_price', color="#0000ff", legend_label="actual price", source=deals)
            p.line('index', 'avg_income_price', color="#ff9100", legend_label="avg income price", source=deals)

            sig = tuple(hdf["buy"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.triangle('index', 'actual_price', color="#00ff00", size=10, source=deals, view=view_sig)

            sig = tuple(hdf["sell"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.inverted_triangle('index', 'actual_price', color="#ff0000", size=10, source=deals, view=view_sig)

            sig = tuple(hdf["stop"])
            view_sig = CDSView(source=deals, filters=[BooleanFilter(sig)])
            p.circle('index', 'actual_price', color="#000000", size=3, source=deals, view=view_sig)
            p.text('index', 'actual_price_stop', text="stop_type", text_font_size="8pt", text_color="#000000", source=deals, view=view_sig)
            p.text('index', 'actual_price_steps', text="steps", text_font_size="8pt", text_color="#0000ff", source=deals)

            p.legend.location = "top_left"

            callback = CustomJS(args=dict(p=p), code="""
            clearTimeout(window._autoscale_timeout);
            var cv_price = cb_obj.plots[0].renderers[0].data_source.data.actual_price;
            var cv_price_slice = cv_price.slice(p.x_range.start,p.x_range.end);
            var cv_max = Math.max(...cv_price_slice);
            var cv_min = Math.min(...cv_price_slice);
            window._autoscale_timeout = setTimeout(function() {
                p.y_range.start = cv_min * .995;
                p.y_range.end = cv_max * 1.005;
            });
            """)

            p.x_range.js_on_change('start', callback)
            return p

        def algo_limit_chat():
            hdf["abs_income_value"] = abs(hdf["income_value"])
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=120,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset",
                       title=self.name + " - limit")
            p.vbar(x='index', top='value_limit_actual', width=1, color="#5555ff", legend_label="value limit actual", source=deals)
            p.vbar(x='index', top='abs_income_value', width=0.7, color="#55ff55", legend_label="income value", source=deals)
            p.vbar(x='index', top='stock_size', width=0.2, color="#ff5555", legend_label="stock_size value", source=deals)
            p.legend.location = "top_left"
            return p

        def algo_qt_chart():
            hdf["actual_qt"].replace(0, np.nan, inplace=True)
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=120,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset",
                       title=self.name + " - qt")
            p.vbar(x='index', top='actual_qt', width=1, color="#5555ff", source=deals)
            return p

        def algo_profit_chart():
            hdf["profit_rpa"] = hdf["realised_profit"] + hdf["act_profit"]
            deals = ColumnDataSource(hdf)
            p = figure(sizing_mode='fixed',
                       plot_width=1330,
                       plot_height=150,
                       toolbar_location="left",
                       y_axis_location="right",
                       tools="xpan,xwheel_zoom,reset",
                       title=self.name + " - profit")

            p.line('index', 'realised_profit', color="#0000ff", line_width=4, legend_label="realised profit", source=deals)
            p.line('index', 'profit_rpa', color="#ff9100", line_width=1, legend_label="actual profit", source=deals)
            p.legend.location = "top_left"
            return p

        # show ---------------------------------------------------------------
        self.chart_elements.append(algo_price_chart())
        self.chart_elements.append(algo_qt_chart())
        self.chart_elements.append(algo_profit_chart())
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

if __name__ == "__main__":
    algo = algo_trade()

    algo.config({"name": "APA",
                 "value_limit": 16000,
                 "stock_size": 5000,
                 "stop_loss_limit": -10,
                 "trailer_stop": .5,
                 "trailer_min_profit": 10,
                 "value_limit_profit_reinvest": True,
                 "steps_limit": 30,
                 "strategy": 1,
                 "trade_time_start": (15, 30),
                 "trade_time_stop": (21, 30)
                 })

    dt = np.datetime64('2013-06-03 13:14:00')
    print(dt.tolist().time() > datetime.time(13, 0))
    dt = dt + 60
    algo.transaction(0, 0, 0.6, 20, dt)
    algo.print_position()
    dt = dt + 60
    algo.transaction(4, 0, 0.6, 21, dt)
    algo.print_position()
    dt = dt + 60
    algo.transaction(4, 0, 0.6, 22, dt)
    algo.print_position()
    dt = dt + 60
    algo.transaction(4, 0, 0.6, 23, dt)
    algo.print_position()
    dt = dt + 60
    algo.transaction(4, 0, 0.6, 24, dt)
    algo.print_position()
    dt = dt + 60
    algo.transaction(4, 0, 0.6, 25, dt)
    algo.print_position()
    price = 26
    for i in range(1, 1000):
        price = max(price * (1 + (random.uniform(-2.9, 3)/100)), 8)
        # print(price)
        dt = dt + 60
        algo.transaction(random.randint(0, 4), 0, 0.6, price, dt)
    algo.show_history()



