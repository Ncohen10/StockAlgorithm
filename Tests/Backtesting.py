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
        self.force_sold_profit = 1000
        self.cash = 1000
        self.invest_amount = 100
        self.buy_hold_money = 1000
        self.buy_hold_stocks = {}

    def test_algorithm(self, test_tickers: List[str]):
        api_call_count = 1
        for ticker in test_tickers:
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            twenty_ema = self.ta.getEMA(symbol=ticker, timePeriod="20", interval="daily")
            twenty_ema = self.filter_dates(twenty_ema)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            fifty_ema = self.ta.getEMA(symbol=ticker, timePeriod="50", interval="daily")
            fifty_ema = self.filter_dates(fifty_ema)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            prices = self.ta.getPrice(symbol=ticker, fullOutput=True)
            prices = self.filter_dates(prices)
            # if api_call_count % 5 == 0: time.sleep(70)
            # api_call_count += 1
            # two_hund_ema = self.ta.getEMA(symbol=ticker, timePeriod="200", interval="daily")
            print("testing: {}".format(ticker))
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)
            twenty_ema_gen = self.stock_info_generator(date_dict=twenty_ema)
            fifty_ema_gen = self.stock_info_generator(date_dict=fifty_ema)
            price_gen = self.stock_info_generator(date_dict=prices)

            max_days = len(min(twenty_ema, fifty_ema, prices, key=len)) - 101
            for day in range(max_days):
                cur_t_ema = next(twenty_ema_gen)
                cur_f_ema = next(fifty_ema_gen)
                cur_day_prices = next(price_gen)
                # TODO - Unnecessary to do max()
                # if self.ta.meetsCrossoverRequirements(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, tick=ticker):
                # if self.ta.isTripleCrossover(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker):
                if self.ta.basicCrossoverTest(prices=cur_day_prices, twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, tick=ticker):
                    self.cash -= self.invest_amount
                if ticker in self.ta.boughtStocks:
                    # self.ta.checkSellDip(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker)
                    profit_percent = self.ta.checkSellStock(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker)
                    if profit_percent != 0:
                        print(profit_percent)
                        self.cash += (self.invest_amount * (1 + profit_percent)) - self.invest_amount
                        print("updated cash: {}".format(self.cash))
            if ticker in self.ta.boughtStocks:
                #self.cash += self.invest_amount
                self.force_sold_profit += self.force_sell(tick=ticker, prices_dict=prices)
            print("New total cash: {}, New forced profit: {}".format(self.cash, self.force_sold_profit))
            print('\n')
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)
        print("TOTAL PROFIT: {}".format(self.ta.profit))
        print("TOTAL FORCE SOLD PROFIT: {}".format(self.force_sold_profit))
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
        try:
            if tick not in self.buy_hold_stocks:
                buy_date = min(prices_dict)
                buy_price = prices_dict[buy_date]["4. close"]
                self.buy_hold_stocks[tick] = float(buy_price)
                print("{} entered buy and hold at {} on {}".format(tick, buy_price, buy_date))
            else:
                sell_date = max(prices_dict)
                sell_price = float(prices_dict[sell_date]["4. close"])
                profit = 1 + ((sell_price - self.buy_hold_stocks[tick]) / sell_price)
                print("{} sold from buy and hold at {} on {}".format(tick, sell_price, sell_date))
                self.buy_hold_money += self.invest_amount * profit
                print("new buy hold profit: {}".format(self.buy_hold_money))
                del self.buy_hold_stocks[tick]
        except:
            pass

    def force_sell(self, tick, prices_dict):
        last_day = max(prices_dict)
        last_price = float(prices_dict[last_day]["4. close"])
        total_stock_profit = 1 + ((last_price - self.ta.boughtStocks[tick][0]) / last_price)
        total_stock_profit *= self.invest_amount
        print("{} force sold on {} for {}".format(tick, last_day, last_price))
        return total_stock_profit

    def get_NYSE_ticks(self, amount=50):
        tick_list = []
        with open("../Data/NYSE.txt") as f:
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
    historical_test = Backtesting(start_date="2013-01-01", end_date="2020-01-01")
    tickers = historical_test.get_NYSE_ticks(amount=100)
    print(tickers)
    # PACD is outlier...
    # tickers = ["C", "T", "HOG", "HPQ",
    #            "IBM", "A", "RNG",
    #            "AMD", "TUP",
    #            "GOOG", "KO", "LUV", "MMM",
    #            "TGT", "WMT"]
    historical_test.test_algorithm(tickers)
