import time
import random
from typing import List
from CrossoverStrategy.TechnicalAnalysis import TechnicalAnalysis


class Backtesting:

    # dates must be in form "YYYY-MM-DD"
    def __init__(self, start_date: str, end_date: str, api_key: str):
        self.start_date = start_date
        self.end_date = end_date
        self.ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")
        self.cash = 10000
        self.initial_money = self.cash
        self.invest_amount = 200
        self.buy_hold_money = 10000
        self.buy_hold_stocks = {}
        self.stock_trade_percent_sum = 0
        self.trades_count = 0
        self.buy_hold_trades_count = 0
        self.buy_hold_profit_percent_sum = 0
        self.algo_portfolio_profit = 0
        self.buy_hold_portfolio_profit = 0

    def test_algorithm(self, test_tickers: List[str]):
        """
        - Retrieves stock EMA info and prices
        - Tests if it
        """
        api_call_count = 0
        for ticker in test_tickers:
            if api_call_count % 5 == 0:  # 5 API calls allowed per min
                time.sleep(70)
            api_call_count += 1
            thirty_ema = self.ta.getEMA(symbol=ticker, timePeriod="30", interval="daily")
            thirty_ema = self.filter_dates(thirty_ema)
            if api_call_count % 5 == 0:
                time.sleep(70)
            api_call_count += 1
            ninety_ema = self.ta.getEMA(symbol=ticker, timePeriod="90", interval="daily")
            ninety_ema = self.filter_dates(ninety_ema)
            if api_call_count % 5 == 0:
                time.sleep(70)
            api_call_count += 1
            prices = self.ta.getPrice(symbol=ticker, fullOutput=True)
            prices = self.filter_dates(prices)
            if api_call_count % 5 == 0:
                time.sleep(70)
            api_call_count += 1
            print("\ntesting: {}".format(ticker))
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)
            # Use generator function to simulate receiving stock info one day at a time.
            thirty_ema_gen = self.stock_info_generator(date_dict=thirty_ema)
            ninety_ema_gen = self.stock_info_generator(date_dict=ninety_ema)
            price_gen = self.stock_info_generator(date_dict=prices)
            max_days = len(min(thirty_ema, ninety_ema, prices, key=len)) - 101
            for day in range(max_days):
                cur_t_ema = next(thirty_ema_gen)
                cur_n_ema = next(ninety_ema_gen)
                cur_day_prices = next(price_gen)
                if self.ta.checkBuyStock(prices=cur_day_prices, thirtyEMA=cur_t_ema, ninetyEMA=cur_n_ema,  tick=ticker):
                    self.cash -= self.invest_amount
                if ticker in self.ta.boughtStocks:
                    # self.ta.checkSellDip(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, tick=ticker)
                    profit_percent = self.ta.checkSellStock(thirtyEMA=cur_t_ema, ninetyEMA=cur_n_ema, prices=cur_day_prices, tick=ticker)
                    if profit_percent != 0:
                        print("{}'s stock profit: {:.5f}".format(ticker, profit_percent))
                        self.cash += (self.invest_amount * profit_percent)
                        print("updated stock algo cash: {:.2f}\n".format(self.cash))
                        self.stock_trade_percent_sum += profit_percent
                        self.trades_count += 1
            if ticker in self.ta.boughtStocks:
                force_sold_profit = self.force_sell(tick=ticker, prices_dict=prices)
                self.cash += self.invest_amount * force_sold_profit
                self.stock_trade_percent_sum += force_sold_profit
                self.trades_count += 1
            print("New total stock algo cash: {:.2f}".format(self.cash))
            # If we've hit the end date, and we haven't sold the stock
            # Then force sell it.
            self.buy_and_hold_invest(tick=ticker, prices_dict=prices)  # Sell the buy and hold money if we bought it.
            print("new buy hold profit: {:.2f}\n\n".format(self.buy_hold_money))
        print("_" * 150)
        print("Info for this historical test: ")
        self.algo_portfolio_profit = self.cash / self.initial_money
        self.buy_hold_portfolio_profit = self.buy_hold_money / self.initial_money
        print("STOCK ALGORITHM TRADES EXECUTED: {}".format(self.trades_count))
        print("TOTAL STOCK ALGORITHM CASH: {}".format(self.cash))
        print("STOCK ALGORITHM TOTAL PROFIT PERCENTAGE: {}".format(self.algo_portfolio_profit))
        print("TOTAL BUY AND HOLD PROFIT: {}".format(self.buy_hold_portfolio_profit))
        print("_" * 150)
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
            print("{} entered buy and hold at {} on {}\n".format(tick, buy_price, buy_date))
        else:
            sell_date = max(prices_dict)
            sell_price = float(prices_dict[sell_date]["4. close"])
            profit = sell_price / self.buy_hold_stocks[tick]
            print("{} sold from buy and hold at {} on {}".format(tick, sell_price, sell_date))
            self.buy_hold_money += (self.invest_amount * profit)
            self.buy_hold_trades_count += 1
            self.buy_hold_profit_percent_sum += profit
            del self.buy_hold_stocks[tick]

    def force_sell(self, tick, prices_dict):
        """
        If a stock has been bought and we've hit the end date, then sell it at the current stock's price
        """
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
                if count == amount - 1: break
        return tick_list

    @staticmethod
    def stock_info_generator(date_dict):
        """
        - Generator function to simulate receiving stock info on a daily basis.
        - Given a dictionary of day->price, yields the dictionary's day by day prices.
            - Starts at earliest date + 100.
        """
        data_up_to_date = {}
        for count, day in enumerate(date_dict):

            data_up_to_date[day] = date_dict[day]
            if count > 100:
                # TODO - Definitely a better way to do this.
                yield data_up_to_date

    def visualize_data(self):
        pass