from typing import List
from Python.TechnicalAnalysis import TechnicalAnalysis


class Backtesting:

    # dates must be in form "YYYY-MM-DD"
    def __init__(self, test_tickers: List[str], start_date: str, end_date: str):
        self.test_tickers = test_tickers
        self.start_date = start_date
        self.end_date = end_date
        self.ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")

    def get_historical_ema(self):
        ema_data = {}  # dictionary of dictionaries storing ema data for all stocks
        for ticker in self.test_tickers:
            ema_data[ticker] = {}
            twenty_ema = self.ta.getEMA(symbol=ticker, timePeriod="20")
            fifty_ema = self.ta.getEMA(symbol=ticker, timePeriod="50")
            price = self.ta.getPrice(symbol=ticker)
            twenty_ema = twenty_ema["Technical Analysis: EMA"]
            fifty_ema = fifty_ema["Technical Analysis: EMA"]
            price = price["Time Series (Daily)"]

    def filter_dates(self, stock_dict):
        pass


    """
    1) Given x amount of tickers, get historical data of tickers from alphavantage's API.
    2) Preprocess data by selecting only EMA and price ticker data from start date to end date.
    3) Pass in data to triplecrossover strategy
   """
