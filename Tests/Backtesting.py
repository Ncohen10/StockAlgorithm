import time
from typing import List
from Python.TechnicalAnalysis import TechnicalAnalysis


class Backtesting:

    # dates must be in form "YYYY-MM-DD"
    def __init__(self, test_tickers: List[str], start_date: str, end_date: str):
        self.test_tickers = test_tickers
        self.start_date = start_date
        self.end_date = end_date
        self.ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")
        self.total_profit = 0
        self.force_sold_profit = 0

    def test_algorithm(self):
        api_call_count = 1
        for ticker in self.test_tickers:
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

            print("testing: {}".format(ticker))
            twenty_ema_gen = self.stock_info_generator(date_dict=twenty_ema)
            fifty_ema_gen = self.stock_info_generator(date_dict=fifty_ema)
            price_gen = self.stock_info_generator(date_dict=prices)

            max_days = len(min(twenty_ema, fifty_ema, prices, key=len)) - 101
            print("Max days: {}".format(max_days))
            for day in range(max_days):
                cur_t_ema = next(twenty_ema_gen)
                cur_f_ema = next(fifty_ema_gen)
                cur_day_prices = next(price_gen)
                if self.ta.meetsCrossoverRequirements(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, tick=ticker):
                    if self.ta.isTripleCrossover(cur_t_ema, cur_f_ema, cur_day_prices, tick=ticker):
                        print("{} has been bought".format(ticker))
                if ticker in self.ta.boughtStocks:
                    if self.ta.checkSellDip(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, stock=ticker):
                        print("{} found sold dip".format(ticker))
                        if (self.ta.checkSellStock(twentyEMA=cur_t_ema, prices=cur_day_prices, tick=ticker)):
                            print("yo sold")
            if ticker in self.ta.boughtStocks:
                self.force_sold_profit += self.force_sell(tick=ticker, prices_dict=prices)
            print("\n")
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

    def force_sell(self, tick, prices_dict):
        last_day = max(prices_dict)
        last_price = float(prices_dict[last_day]["4. close"])
        total_stock_profit = (last_price - self.ta.boughtStocks[tick])
        print("{} sold on {} for {}".format(tick, last_day, last_price))
        return total_stock_profit

    @staticmethod
    def stock_info_generator(date_dict):
        # TODO - Make sure the dates are being generated in reverse order
        data_up_to_date = {}
        for count, day in enumerate(date_dict):
            data_up_to_date[day] = date_dict[day]
            if count > 100:
                yield data_up_to_date

    """
    1) Given x amount of tickers, get historical data of tickers from alphavantage's API.
    2) Preprocess data by selecting only EMA and price ticker data from start date to end date.
    3) Pass in data to triplecrossover strategy
   """


if __name__ == '__main__':
    historical_test = Backtesting(test_tickers=["IBM", "AMZN", "RNG", "AAPL", "AMD", "TSLA", "NVDA", "TUP", "GOOG"], start_date="2013-01-01", end_date="2019-01-01")
    historical_test.test_algorithm()