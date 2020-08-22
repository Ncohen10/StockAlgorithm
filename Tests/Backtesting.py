import time
import random
from typing import List
from Python.TechnicalAnalysis import TechnicalAnalysis


class Backtesting:

    # dates must be in form "YYYY-MM-DD"
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        self.ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")
        self.total_profit = 0
        self.cash = 10000
        self.invest_amount = 500
        self.buy_hold_money = 10000
        self.buy_hold_stocks = {}

    def test_algorithm(self, test_tickers: List[str]):
        api_call_count = 0
        for ticker in test_tickers:
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            thirty_ema = self.ta.getEMA(symbol=ticker, timePeriod="30", interval="daily")
            thirty_ema = self.filter_dates(thirty_ema)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            ninety_ema = self.ta.getEMA(symbol=ticker, timePeriod="90", interval="daily")
            ninety_ema = self.filter_dates(ninety_ema)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            prices = self.ta.getPrice(symbol=ticker, fullOutput=True)
            prices = self.filter_dates(prices)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            print("testing: {}".format(ticker))
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)
            thirty_ema_gen = self.stock_info_generator(date_dict=thirty_ema)
            ninety_ema_gen = self.stock_info_generator(date_dict=ninety_ema)
            price_gen = self.stock_info_generator(date_dict=prices)

            max_days = len(min(thirty_ema, ninety_ema, prices, key=len)) - 101
            for day in range(max_days):
                cur_t_ema = next(thirty_ema_gen)
                cur_n_ema = next(ninety_ema_gen)
                cur_day_prices = next(price_gen)
                # TODO - Unnecessary to do max()
                # if self.ta.meetsCrossoverRequirements(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, tick=ticker):
                # if self.ta.isTripleCrossover(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker):
                if self.ta.basicCrossoverTest(prices=cur_day_prices, thirtyEMA=cur_t_ema, ninetyEMA=cur_n_ema,  tick=ticker):
                    self.cash -= self.invest_amount
                if ticker in self.ta.boughtStocks:
                    # self.ta.checkSellDip(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker)
                    profit_percent = self.ta.checkSellStock(thirtyEMA=cur_t_ema, ninetyEMA=cur_n_ema, prices=cur_day_prices, tick=ticker)
                    if profit_percent != 0:
                        print(profit_percent)
                        self.cash += (self.invest_amount * profit_percent)
                        print("updated cash: {}".format(self.cash))

            if ticker in self.ta.boughtStocks:
                print("")
                self.cash += self.invest_amount * self.force_sell(tick=ticker, prices_dict=prices)
            print("New total cash: {}".format(self.cash))
            print('\n')
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)
        print("TOTAL PROFIT: {}".format(self.ta.profit))
        return self.ta.profit

    def filter_dates(self, date_dict):
        # TODO - Clean this up and reduce space used. Maybe write dictionary data to a file.
        date_filtered_dict = {}
        if not date_dict:
            print("date_dict is empty")
            return {}
        # sort the dates into ascending order
        date_dict = dict(sorted(date_dict.items()))
        for date in date_dict:
            if self.start_date <= date <= self.end_date:
                date_filtered_dict[date] = date_dict[date]  # Map date to its original data
        return date_filtered_dict

    def buy_and_hold_invest(self, tick, prices_dict):
        if not tick or not prices_dict:
            print("Unable to buy and hold invest")
            return
        if tick not in self.buy_hold_stocks:
            self.buy_hold_money -= self.invest_amount
            buy_date = min(prices_dict)
            buy_price = prices_dict[buy_date]["4. close"]
            self.buy_hold_stocks[tick] = float(buy_price)
            print("{} entered buy and hold at {} on {}".format(tick, buy_price, buy_date))
        else:
            sell_date = max(prices_dict)
            sell_price = float(prices_dict[sell_date]["4. close"])
            profit = sell_price / self.buy_hold_stocks[tick]
            print("{} sold from buy and hold at {} on {}".format(tick, sell_price, sell_date))
            self.buy_hold_money += (self.invest_amount * profit)
            print("new buy hold profit: {}".format(self.buy_hold_money))
            del self.buy_hold_stocks[tick]

    def force_sell(self, tick, prices_dict):
        last_day = max(prices_dict)
        last_price = float(prices_dict[last_day]["4. close"])
        total_stock_profit = last_price / self.ta.boughtStocks[tick][0]
        print("{} force sold on {} for {}".format(tick, last_day, last_price))
        return total_stock_profit

    @staticmethod
    def get_random_ticks(file,  amount=50):
        tick_list = []
        with open(file) as f:
            lines = list(f.readlines())
            random.shuffle(lines)
            for count, line in enumerate(lines):
                cur_tick = line.split()[0]
                tick_list.append(cur_tick)
                if count == amount: break
        return tick_list

    @staticmethod
    def stock_info_generator(date_dict):
        # TODO - Make sure the dates are being generated in reverse order
        data_up_to_date = {}
        for count, day in enumerate(date_dict):
            data_up_to_date[day] = date_dict[day]
            if count > 100:
                # TODO - Definitely a better way to do this.
                yield dict(sorted(data_up_to_date.items(), reverse=True))

    """
    1) Given x amount of tickers, get historical data of tickers from alphavantage's API.
    2) Preprocess data by selecting only EMA and price ticker data from start date to end date.
    3) Pass in data to triplecrossover strategy
   """


if __name__ == '__main__':
    avg = 0
    total = 0
    NYSE = "../Data/NYSE.txt"
    SPY = "../Data/SPY.txt"
    PENNY = "../Data/PENNY.txt"  # Data is biased for penny stock info.
    USA = "../Data/USA.txt"
    for i in range(1, 11):
        historical_test = Backtesting(start_date="2007-01-01", end_date="2015-01-01")
        tickers = historical_test.get_random_ticks(file=NYSE, amount=100)
        while "GOL" in tickers:  # GOL outlier that messes too much with testing
            tickers = historical_test.get_random_ticks(file=NYSE, amount=100)
        print(tickers)
        # GOL = outlier
        historical_test.test_algorithm(tickers)
        total += historical_test.cash
        avg = print("cash avg for {} iteration".format(total / i))

# TODO - Fix buy and hold