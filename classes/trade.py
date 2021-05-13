import alpaca_trade_api as tradeapi
import pandas as pd
import tables
import threading
from datetime import time as dt_time
from time import sleep, gmtime, time
from random import randint # azért használom, hogy a rendszres lekérdezések nem pont ugyan olyan ütemben történjenek, ne tűnjek junk nak


class trade:

    def __init__(self, gui):
        self.gui = gui
        self.request_count = {}
        self.request_count_max = 0
        self.trade_api = tradeapi.REST('PKSJI4DQMLN4IQ8L6KFT',
                                       '8CUv1fVN3s9Vl5hkxojTuDChZiXIe7E3qvbC147F',
                                       base_url='https://paper-api.alpaca.markets')

        self.clock = ""
        # alpaca accountot csak iylen időközönként kérem le.
        self.clock_refresh_time = 600
        # utolsó alpaca accunt lekérés ideje
        self.last_time_get_clock = 0


        self.account = ""
        # alpaca accountot csak iylen időközönként kérem le.
        self.account_refresh_time = 240
        # utolsó alpaca accunt lekérés ideje
        self.last_time_get_account = 0

        # result by last get orders in apaca object
        self.orders = []
        # result by last get position in apaca object
        self.positions = []

        # target position data frame
        self.tp_df = self.read_tp_df()
        # decision matrix data frame
        self.dm_df = pd.DataFrame(None)

        # current position data frame
        self.cp_df = pd.DataFrame(None)

        self.broker_thread = ""
        self.broker_refresh_rate = 5
        self.broker_is_working = False
        self.broker_break = False

        self.monitor_thread = ""
        self.monitor_refresh_rate = 25
        self.monitor_is_working = False
        self.monitor_break = False

        self.refresh_info_string = ""
        self.refresh_info_thread = ""

        self.config = {
            'time_zone': 'UTC+2',
            'nyse_open': dt_time(15, 30, 0),
            'nyse_close': dt_time(22, 00, 0),
            'trade_from': '16:00',
            'trade_to': '22:00',
            'stop_margin': 5,
            'stop_margin_measure': 'Percent',
            'trade_block_size': 500,
            'trade_block_size_currency': 'USD',
        }

        # ez egy kommunikációs dictionary a ui és a trade objektum között az ui ebbe állítja be amit be adar adni
        self.order = {
            'symbol': '',
            'position': '',
            'qty': 0,
            'stop_trailing ': False
        }

    def write_tp_df(self):
        self.tp_df.to_csv('target_position.csv', index=True)

    def read_tp_df(self):
        try:
            i_return = pd.read_csv('target_position.csv', sep=',')
        except:
            i_return = pd.DataFrame(None)
        else:
            i_return = pd.DataFrame(i_return)
        i_return = i_return.set_index("symbol")
        # print(i_return)
        return i_return

    def call_alpaca(self, function_name, args=[], kwargs={}):
        obj = self.trade_api
        try:
            i_return = getattr(obj, function_name)(*args, **kwargs)
        except:
            print("Alpaca error")
            i_return = ""
        else:
            i_now = gmtime()
            i_now_str = f"{int(i_now.tm_hour)}:{int(i_now.tm_min)}"
            if i_now_str in self.request_count.keys():
                self.request_count[i_now_str] += 1
            else:
                self.request_count[i_now_str] = 1
            self.request_count_max = max(self.request_count_max, self.request_count[i_now_str])
        return i_return

    def get_market_price_by_symbol(self, symbol):
        symbol_bars = self.call_alpaca("get_barset", [symbol, 'minute', 1], {})
        return symbol_bars[symbol][0].c

    def create_decision_matrix(self):
        # add target position to decision matrix: dm_df
        self.dm_df = self.tp_df.copy()
        self.dm_df['position'] = 0

        # add actual position to decision matrix: dm_df
        i_positions = self.get_all_positions()

        for i_p in i_positions:
            if i_p.symbol in self.dm_df.index:
                self.dm_df.loc[i_p.symbol, 'position'] = int(i_p.qty)
            else:
                self.dm_df.loc[i_p.symbol, 'position'] = int(i_p.qty)
                self.dm_df.loc[i_p.symbol, 'trading'] = True
        # add orders to decision matrix: dm_df
        i_orders_market, i_orders_trailing, i_orders_other = self.get_all_sum_orders()
        self.dm_df = self.dm_df.join(pd.Series(i_orders_market).to_frame('order_market'), how='outer')
        self.dm_df = self.dm_df.join(pd.Series(i_orders_trailing).to_frame('order_trailing'), how='outer')
        self.dm_df = self.dm_df.join(pd.Series(i_orders_other).to_frame('order_other'), how='outer')

        # fixing dm_df
        self.dm_df = self.dm_df.fillna(0)
        self.dm_df['position'] = pd.to_numeric(self.dm_df['position'])
        self.dm_df['target_position'] = pd.to_numeric(self.dm_df['target_position'])
        self.dm_df['order_market'] = pd.to_numeric(self.dm_df['order_market'])
        self.dm_df['order_trailing'] = pd.to_numeric(self.dm_df['order_trailing'])
        self.dm_df['order_other'] = pd.to_numeric(self.dm_df['order_other'])

        # 1 szint eldönti, hogy mennyi stop illetve trading pozíció
        self.dm_df['total_trade'] = self.dm_df['target_position'] - self.dm_df['position']
        self.dm_df['stop_trade'] = 0
        self.dm_df['position_trade'] = 0
        self.dm_df['trade_chk_ok'] = False
        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'target_position'] == self.dm_df.loc[i_index, 'position']:
                self.dm_df.loc[i_index, 'stop_trade'] = 0
                self.dm_df.loc[i_index, 'position_trade'] = 0
            else:
                ix_tp = self.dm_df.loc[i_index, 'target_position']
                ix_p = self.dm_df.loc[i_index, 'position']
                ix_tt = self.dm_df.loc[i_index, 'total_trade']
                if (ix_tp > 0 and ix_p < 0) or (ix_tp < 0 and ix_p > 0) or (ix_tp == 0):
                    self.dm_df.loc[i_index, 'stop_trade'] = ix_tt - ix_tp
                    self.dm_df.loc[i_index, 'position_trade'] = ix_tt - (ix_tt - ix_tp)
                else:
                    self.dm_df.loc[i_index, 'stop_trade'] = 0
                    self.dm_df.loc[i_index, 'position_trade'] = ix_tp - ix_p

        # ellenőrzi, hogy a szétosztás megfelelőe, ez gyakorlatilag nem lehet soha hibás
        self.dm_df['trade_chk_ok'] = self.dm_df['target_position'] == (self.dm_df['position']
                                                                       + self.dm_df['stop_trade']
                                                                       + self.dm_df['position_trade'])

        # 2.szint
        # felépíti a to_do -t
        # kiválasztja, hogy mit kell csinálni most, TO DO stop vagy trade pozíciót vesz fel, vagy vár

        self.dm_df['to_do'] = ""
        self.dm_df['to_do_type'] = ""
        self.dm_df['to_do_qty'] = 0

        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'trade_chk_ok']:
                if self.dm_df.loc[i_index, 'stop_trade'] != 0:
                    if self.dm_df.loc[i_index, 'stop_trade'] < 0:
                        self.dm_df.loc[i_index, 'to_do'] = "sell"
                    else:
                        self.dm_df.loc[i_index, 'to_do'] = "buy"
                    self.dm_df.loc[i_index, 'to_do_type'] = "stop"
                    self.dm_df.loc[i_index, 'to_do_qty'] = abs(self.dm_df.loc[i_index, 'stop_trade'])
                elif self.dm_df.loc[i_index, 'position_trade'] != 0:
                    if self.dm_df.loc[i_index, 'position_trade'] < 0:
                        self.dm_df.loc[i_index, 'to_do'] = "sell"
                    else:
                        self.dm_df.loc[i_index, 'to_do'] = "buy"
                    self.dm_df.loc[i_index, 'to_do_type'] = "trade"
                    self.dm_df.loc[i_index, 'to_do_qty'] = abs(self.dm_df.loc[i_index, 'position_trade'])
                else:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
            else:
                # nem tudta a target_pozícióból és pozícióból elödnteni mit kell tenni
                # Ez elméletileg nem fodulhat elő, de ha mégis akkor nagy a BAJ!!!!
                self.dm_df.loc[i_index, 'to_do'] = "error"
                self.dm_df.loc[i_index, 'to_do_type'] = ""
                self.dm_df.loc[i_index, 'to_do_qty'] = 0
        # 3. szint
        # lehet, hogy a szükséges döntés már megszületett előzőleg és az orderek ki lettek adva
        #  - ha az orderek száma rendben akkor vár
        #  - ha nincs rendben akkor order törlést beállítja
        #  ezt broker megteszi az orderek behelyezése előtt

        self.dm_df['to_do_order_clear'] = False

        for i_index in self.dm_df.index:
            if self.dm_df.loc[i_index, 'to_do'] == "buy":
                if self.dm_df.loc[i_index, 'order_market'] == self.dm_df.loc[i_index, 'to_do_qty']:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
                else:
                    if self.dm_df.loc[i_index, 'order_market'] == 0:
                        self.dm_df['to_do_order_clear'] = False
                    else:
                        self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "sell":
                if self.dm_df.loc[i_index, 'order_market'] == -1 * self.dm_df.loc[i_index, 'to_do_qty']:
                    self.dm_df.loc[i_index, 'to_do'] = "wait"
                    self.dm_df.loc[i_index, 'to_do_type'] = ""
                    self.dm_df.loc[i_index, 'to_do_qty'] = 0
                else:
                    if self.dm_df.loc[i_index, 'order_market'] == 0:
                        self.dm_df['to_do_order_clear'] = False
                    else:
                        self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "wait":
                # ha "wait" -tal érkezik ide, akkor annak az az oka, hogy a pozíció és a target megegyezik, azaz
                # nincs tennivaló, ha valamirét mégis van market order, akkor azt törölni kell
                # order_cleart igazra állítom és bóker majd törli
                if self.dm_df.loc[i_index, 'order_market'] == 0:
                    self.dm_df['to_do_order_clear'] = False
                else:
                    self.dm_df['to_do_order_clear'] = True
            elif self.dm_df.loc[i_index, 'to_do'] == "error":
                # ha ide error-al érkezik akkor nagy a BAJ
                print("!! ERROR !!")
        return self.dm_df

# trade info methods ----------------------------------------------------------
    def refresh_tr_info(self):
        self.refresh_info_string = ""
        self.refresh_info_thread = threading.Thread(target=self.refresh_tr_info_job)
        self.refresh_info_thread.start()

    def refresh_tr_info_job(self):
        self.refresh_info_string = self.gui.create_tr_info_string()
        self.gui.nTrade_info.setText(self.refresh_info_string)

# monitor methods ---------------------------------------------------------------

    def monitor_run(self):
        if not self.monitor_is_working:
            self.monitor_is_working = True
            self.monitor_thread = threading.Thread(target=self.monitor_while)
            self.monitor_thread.start()
            self.refresh_tr_info()

    def monitor_stop(self):
        self.monitor_break = True

    def monitor_while(self):
        i_wait_sec = self.monitor_refresh_rate + randint(-5, 5)
        while not self.monitor_break:
            self.monitor_action()

            # várakozik egy adott ideig de ki tud belőle szállni menet közben is így esc re azonnal leáll
            # teszek hozzá +-5 másodpercet, hogy a várakozás a lekérdezési ütem ne legyen szabályos
            i_wait_no = 0
            while i_wait_no < (i_wait_sec * 2) and not self.monitor_break:
                sleep(0.5)
                i_wait_no += 1
        if self.monitor_break:
            print("Status: Monitor is stopped!")
        self.monitor_break = False
        self.monitor_is_working = False
        self.refresh_tr_info()

    def monitor_action(self):
        self.cp_df = pd.DataFrame(None)
        i_positions = self.get_all_positions()
        # print(i_positions)
        for i_p in i_positions:
            self.cp_df.loc[i_p.symbol, 'qty'] = int(i_p.qty)
            self.cp_df.loc[i_p.symbol, 'current_price'] = float(i_p.current_price)
            self.cp_df.loc[i_p.symbol, 'cost_basis'] = float(i_p.cost_basis)
            self.cp_df.loc[i_p.symbol, 'market_value'] = float(i_p.market_value)
            self.cp_df.loc[i_p.symbol, 'unrealized_pl'] = float(i_p.unrealized_pl)
        self.gui.refresh_ui("info")

# broker methods

    def broker_run(self):
        if not self.broker_is_working:
            self.broker_is_working = True
            self.refresh_tr_info()
            self.broker_thread = threading.Thread(target=self.broker_while)
            self.broker_thread.start()

    def broker_stop(self):
        self.broker_break = True

    def broker_while(self):
        self.gui.tlog("Start: Broker", line=True, indent=False, color="normal")
        is_broker_action = self.broker_action()
        while is_broker_action and not self.broker_break:
            # várakozik egy adott ideig, de ki tud belőle szállni menet közben is így esc re azonnal leáll
            i_wait_no = 0
            while i_wait_no < (self.broker_refresh_rate * 2) and not self.broker_break:
                sleep(0.5)
                i_wait_no += 1
            is_broker_action = self.broker_action()
        if self.broker_break:
            print("Status: Broker is stopped!")
        else:
            self.gui.tlog("Ready.", line=False, indent=False, color="normal")
        self.broker_is_working = False
        self.refresh_tr_info()

    def broker_action(self):
        self.create_decision_matrix()
        for i_index in self.dm_df.index:

            # 1. szint
            # végrehajtja az utasítáokat

            if self.dm_df.loc[i_index, 'trading']:

                if self.dm_df.loc[i_index, 'to_do_order_clear']:
                    i_is_canceled = self.cancel_orders_by_symbol(i_index)
                    while not i_is_canceled:
                        i_is_canceled = self.cancel_orders_by_symbol(i_index)

                if self.dm_df.loc[i_index, 'to_do'] == "buy" or self.dm_df.loc[i_index, 'to_do'] == "sell":
                    i_qty = abs(self.dm_df.loc[i_index, 'to_do_qty'])
                    i_side = self.dm_df.loc[i_index, 'to_do']
                    if self.dm_df.loc[i_index, 'to_do_type'] == "stop":
                        # stop hoz market ordert használok
                        self.order_market(i_index, i_side, i_qty)
                    else:
                        # TODO: trailer trade order
                        # trade hez is market ordert használok
                        # majd ehhez kell hozzá kapcsolni a OTO -
                        self.order_market(i_index, i_side, i_qty)
                elif self.dm_df.loc[i_index, 'to_do'] == "wait":
                    # 2. sint
                    # megvizsgálja, hogy a target állpot beállt-e, aza position == tartget position
                    # és nincsenek orderek bent ha minden ok, akkor befejeződött a trading iteráció
                    i_x = (self.dm_df.loc[i_index, 'target_position'] - self.dm_df.loc[i_index, 'position']) == 0
                    i_ox = self.dm_df.loc[i_index, 'order_market'] == 0
                    if i_x and i_ox:
                        self.set_tp_done(i_index)
                elif self.dm_df.loc[i_index, 'to_do'] == "error":
                    # ha a bróker egy pozícióra errort kap
                    # TODO: bokeren végig kell vezetni az errort
                    print("Broker error")
        # ha van legalább egy trading true, akkor true val tér vissza
        # azaz legalább 1 olyan symbol van amivel még foglalkozni kell addig nem fog lállni a broker_wait
        # ha a tp_df ben azaz a target positionban minden trading False akkor meg fog állni a bróker while
        i_return = self.tp_df["trading"].sum() > 0
        return i_return

# Ordering methods -----------------------------------------------

    def order_market(self, symbol, side, qty):
        i_is_trading_blocked = self.is_trading_blocked()
        i_is_market_open = self.is_market_open()
        if i_is_trading_blocked:
            self.gui.tlog(f"Trading blocked! Set:Refresh time: 60 sec (Slow down)",
                          line=False,
                          indent=True,
                          color="long")
            self.broker_refresh_rate = 60
        if not i_is_market_open:
            self.gui.tlog(f"Market is closed! Set:Refresh time: 60 sec (Slow down)",
                          line=False,
                          indent=True,
                          color="long")
            self.broker_refresh_rate = 60
        if not i_is_trading_blocked and i_is_market_open:
            if self.broker_refresh_rate != 5:
                self.gui.tlog(f"Set:Refresh time: 5 sec (Speed down)", line=False, indent=True, color="long")
                self.broker_refresh_rate = 5
            if side == "buy":
                self.gui.tlog(f"Submit order: {symbol} {side} {int(qty)}", line=False, indent=True, color="long")
            else:
                self.gui.tlog(f"Submit order: {symbol} {side} {int(qty)}", line=False, indent=True, color="short")

            self.call_alpaca("submit_order",
                             [],
                             {"symbol": symbol,
                               "qty": int(qty),
                               "side": side,
                               "type": 'market',
                               "time_in_force": 'gtc'
                               }
                             )

    def order_trailing_stop(self, symbol, side, qty):
        print(f'Submit trailing stop order: {symbol} , {side}, {int(qty)}')
        # self.trade_api.submit_order(
        #     side=side,
        #     symbol=symbol,
        #     type="trailing_stop",
        #     qty=int(qty),
        #     time_in_force="day",
        #     trail_percent="10"
        # )

        self.call_alpaca("submit_order",
                         [],
                         {"side": side,
                           "symbol": symbol,
                           "type": "trailing_stop",
                           "qty": int(qty),
                           "time_in_force": "day",
                           "trail_percent": "10"
                           }
                         )

# Target position methods -----------------------------------------

    def set_tp_position(self, symbol, qty):
        self.tp_df.loc[symbol, 'target_position'] = int(qty)
        self.tp_df.loc[symbol, 'trading'] = True
        self.write_tp_df()

        # a trade log on beljebb teszem ha éppen bokering közben állítgat
        i_indent = self.broker_is_working

        if int(qty) > 0:
            self.gui.tlog(f"Set position LONG {symbol} {int(qty)}", line=False, indent=i_indent, color="long")
        elif int(qty) < 0:
            self.gui.tlog(f"Set position SHORT {symbol} {int(qty)}", line=False, indent=i_indent, color="short")
        else:
            self.gui.tlog(f"Set position STOP {symbol} {int(qty)}", line=False, indent=True, color="stop")

    def drop_tp_symbol(self, symbol):
        self.tp_df = self.tp_df.drop([symbol], errors='ignore')
        self.write_tp_df()

    def set_tp_done(self, symbol):
        self.tp_df.loc[symbol, 'trading'] = False
        self.write_tp_df()

    def get_tp_position(self, symbol):
        return self.tp_df.loc[symbol, 'target_position']

    def is_tp_done(self, symbol):
        return self.tp_df.loc[symbol, 'target_position']

    def get_all_sum_orders(self):
        order_list_market = {}
        order_list_trailing_stop = {}
        order_list_other = {}
        i_orders = self.get_all_open_orders()
        for i_o in i_orders:
            if i_o.order_type == 'market':
                if i_o.symbol in order_list_market:
                    if i_o.side == "buy":
                        order_list_market[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_market[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_market[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_market[i_o.symbol] = int(i_o.qty) * -1
            elif i_o.order_type == 'trailing_stop':
                if i_o.symbol in order_list_trailing_stop:
                    if i_o.side == "buy":
                        order_list_trailing_stop[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_trailing_stop[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_trailing_stop[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_trailing_stop[i_o.symbol] = int(i_o.qty) * -1
            else:
                if i_o.symbol in order_list_other:
                    if i_o.side == "buy":
                        order_list_other[i_o.symbol] += int(i_o.qty)
                    else:
                        order_list_other[i_o.symbol] -= int(i_o.qty)
                else:
                    if i_o.side == "buy":
                        order_list_other[i_o.symbol] = int(i_o.qty)
                    else:
                        order_list_other[i_o.symbol] = int(i_o.qty) * -1
        return order_list_market, order_list_trailing_stop, order_list_other

    # def get_sum_order_by_symbol(self, symbol):
    #     orders_qty_list = {}
    #     i_orders = trade.get_all_open_orders()
    #
    #     for i_o in i_orders:
    #         if i_o.symbol in orders_qty_list:
    #             if i_o.side == "buy":
    #                 orders_qty_list[i_o.symbol] += int(i_o.qty)
    #             else:
    #                 orders_qty_list[i_o.symbol] -= int(i_o.qty)
    #         else:
    #             if i_o.side == "buy":
    #                 orders_qty_list[i_o.symbol] = int(i_o.qty)
    #             else:
    #                 orders_qty_list[i_o.symbol] = int(i_o.qty) * -1
    #
    #     if symbol in orders_qty_list:
    #         i_return = orders_qty_list[symbol]
    #     else:
    #         i_return = 0
    #     return i_return

    def get_all_open_orders(self):
        i_orders = self.call_alpaca("list_orders",
                                    [],
                                    {"status": 'open',
                                      "limit": 500,
                                      "nested": True}
                                    )
        self.orders = i_orders
        return i_orders

    def get_open_orders_by_symbol(self, symbol):
        i_orders = self.get_all_open_orders()
        i_symbol_orders = [o for o in i_orders if o.symbol == symbol]
        return i_symbol_orders

    def cancel_orders_by_symbol(self, symbol):
        i_orders = self.get_open_orders_by_symbol(symbol)
        for i_o in i_orders:
            self.cancel_order_by_id(i_o.id)
        i_orders2 = self.get_open_orders_by_symbol(symbol)
        if len(i_orders2) == 0:
            i_return = True
        else:
            i_return = False
        return i_return

    def cancel_order_by_id(self, order_id):
        try:
            # self.trade_api.cancel_order(order_id)
            self.call_alpaca("cancel_order", [order_id], {})
        except:
            i_all_open_orders = self.get_all_open_orders()
            if order_id in i_all_open_orders:
                i_return = False
            else:
                i_return = True
        else:
            i_return = True
        return i_return

    # account informations

    def get_account_now(self):
        # self.account = self.trade_api.get_account()
        self.account = self.call_alpaca("get_account", [], {})

    def get_account(self):
        if self.last_time_get_account > 0:
            i_now = time()
            i_last = self.last_time_get_account
            i_time_dif = int(i_now - i_last)
            if i_time_dif > self.account_refresh_time:
                self.account = self.call_alpaca("get_account", [], {})
                self.last_time_get_account = time()
        else:
            self.account = self.call_alpaca("get_account", [], {})
            self.last_time_get_account = time()
        return self.account

    def get_buying_power(self):
        self.get_account_now()
        return self.account.buying_power

    def is_trading_blocked(self):
        self.get_account_now()
        return self.account.trading_blocked

    # symbol checks

    def is_tradable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alpaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.tradable:
                i_return = True
            else:
                i_return = False
        return i_return

    def is_shortable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alpaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.shortable:
                i_return = True
            else:
                i_return = False
        return i_return

    def is_marginable(self, symbol):
        try:
            # i_asset = self.trade_api.get_asset(symbol)
            i_asset = self.call_alpaca("get_asset", [symbol], {})
        except:
            i_return = False
        else:
            if i_asset.marginable:
                i_return = True
            else:
                i_return = False
        return i_return

    def get_symbol(self, symbol):
        return self.call_alpaca("get_asset", [symbol], {})

# market infos
    def is_market_open(self):
        # i_clock = self.trade_api.get_clock()
        i_clock = self.call_alpaca("get_clock", [], {})
        return i_clock.is_open

    def get_clock(self):
        if self.last_time_get_clock > 0:
            i_now = time()
            i_last = self.last_time_get_clock
            i_time_dif = int(i_now - i_last)
            if i_time_dif > self.clock_refresh_time:
                self.clock = self.call_alpaca("get_clock", [], {})
                self.last_time_get_clock = time()
        else:
            self.clock = self.call_alpaca("get_clock", [], {})
            self.last_time_get_clock = time()
        return self.clock


# position methods

    def get_all_positions(self):
        # i_positions = self.trade_api.list_positions()
        i_positions = self.call_alpaca("list_positions", [], {})
        self.positions = i_positions
        return i_positions

    def get_position_by_symbol(self, symbol):
        try:
            # i_position = self.trade_api.get_position(symbol)
            i_position = self.call_alpaca("get_position", [symbol], {})
        except:
            i_position = []
            self.positions = []
        else:
            self.positions = i_position
        return i_position

    def time_filter(self, df, time_open, time_close):
        df = df.set_index('Date')
        i_intime = df.between_time(time_open, time_close).copy()
        i_outtime = df.between_time(time_close, time_open).copy()
        i_intime = i_intime.reset_index()
        i_outtime = i_outtime.reset_index()
        return i_intime, i_outtime
