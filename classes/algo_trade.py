class algo_trade:

    def __init__(self):
        self.qt = 0
        self.avg_income_price = 0
        self.income_volume = 0  # position + avg_price
        self.trailer_profit = 0
        self.profit = 0
        self.trailer_stop = .5
        self.stock_size = 30000  # in USD
        self.stop_limit = -10
        self.min_profit = 10
        self.deal_count = 0

    def buy(self, qt, price):
        self.income_volume += int(qt * price)
        self.qt += qt
        self.avg_income_price = self.income_volume / self.qt
        self.trailer_profit = int((price - self.avg_income_price) * self.qt)
        self.deal_count += 1

    def sell(self, qt, price):
        self.income_volume -= int(qt * price)
        self.qt -= qt
        self.avg_income_price = self.income_volume / self.qt
        self.trailer_profit = int((price - self.avg_income_price) * self.qt)
        self.deal_count +=1

    def stop(self, price):
        self.profit += int((price - self.avg_income_price) * self.qt)
        self.qt = 0
        self.avg_income_price = 0
        self.income_volume = 0  # position + avg_price
        self.trailer_profit = 0
        self.deal_count += 1

    def trailer(self, price):
        act_profit = int((price - self.avg_income_price) * self.qt)

        if self.qt != 0 and act_profit != self.trailer_profit:

            if act_profit < self.stop_limit:
                self.stop(price)
                i_return = True
            else:

                percent = (1 - self.trailer_stop)
                if act_profit < self.trailer_profit * percent:
                    if act_profit < self.min_profit:
                        self.trailer_profit = max(act_profit, self.trailer_profit)
                        i_return = False
                    else:
                        self.stop(price)
                        i_return = True
                else:
                    self.trailer_profit = max(act_profit, self.trailer_profit)

                    i_return = False
                    # print("TRAILER rise")
                self.print_position()
        else:
            i_return = False
            # print("TRAILER - SILENT")
        return i_return

    def get_qt(self, price):
        return int(self.stock_size / price)

    def print_position(self):
        pass
        # print(f"profit: {self.profit} qt: {self.qt} avg_income_price:" +
        #       f"{self.avg_income_price} income_volume: {self.income_volume} / {self.trailer_volume}")

    def get_position(self):
        return [self.profit,self.deal_count]

        # return (f"profit: {self.profit} qt: {self.qt} avg_income_price:" +
        #       f"{round(self.avg_income_price, 2)} income_volume: {self.income_volume}" +
        #         f" trailer_profit: {self.trailer_profit} deal count: {self.deal_count}")

# ago = algo_trade()
#
# ago.buy(10, 10)
# ago.trailer(12)
# ago.trailer(14)
# ago.trailer(15)
# ago.trailer(16)
# ago.trailer(15)
# ago.trailer(18)
# ago.trailer(19)
# ago.buy(10, 10)
# ago.trailer(12)
# ago.trailer(14)
# ago.buy(10, 15)
# ago.trailer(12)
