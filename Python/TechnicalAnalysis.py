import requests
import time
import datetime as dt
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from WebScrapers.YahooSymbolScraper import YahooSymbolScraper

class TechnicalAnalysis:

    # TODO - Put Alphavantage API call methods into separate class.

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key
        # self.boughtStocks = {"RNG": 261.0, "AMD": 55.71, "UMC": 2.44, "IMOS": 20.34, "VNET": 13.89}  # map of stocks to price bought
        self.boughtStocks = {}
        self.soldStocks = {}  # map of stocks to price sold
        self.sellDip = set()  # Set of stocks that have experienced a sell dip.
        self.profit = 0

    def deathCross(self, tick, prices, twentyEMA, twoHundEMA):
        if tick not in self.boughtStocks:
            return 0.0
        cur_date = max(prices)
        # cur_date = next(iter(twentyEMA))
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        cur_date = str(cur_date)
        if cur_date not in twentyEMA:
            print("No common date")
            return 0.0
        cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
        cur_thund_ema = float(twoHundEMA[cur_date]["EMA"])
        cur_price = float(prices[cur_date]["4. close"])

        stock_profit = (cur_price - self.boughtStocks[tick][0]) / self.boughtStocks[tick][0]
        if cur_twenty_ema < cur_thund_ema:
            print("{} has been sold at {} on {}\n".format(tick, cur_price, cur_date))
            del self.boughtStocks[tick]
            self.soldStocks[tick] = cur_price
            return stock_profit


    def getEMA(self, symbol: str, timePeriod: str, interval: str = "daily") -> dict:  # Only set up for equity
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfEMA = data.get("Technical Analysis: EMA")
        if not dictOfEMA:
            print("getEMA() is returning an empty dictionary for some reason. May be too many API calls.")
        return dictOfEMA

    def getPrice(self, symbol: str, fullOutput=False) -> dict:  # TODO - make sure the API call is correct
        output_size = "compact"
        if fullOutput:
            output_size = "full"
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                            + symbol + "&outputsize=" + output_size +
                            "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfPrices = data.get("Time Series (Daily)")
        return dictOfPrices

    def isTripleCrossover(self, twentyEMA: dict, fiftyEMA: dict, prices: dict, tick: str) -> bool:
        """
        - Checks for triple crossover, assuming minimum requirements have been met.
        - If triple crossover is found, maps stock to buying price.
        - self.boughStock[stock] = price
        """
        # TODO - Instead of curPrice going below 20EMA, check if curPrice is x less than previous 1-3 days.
        if tick in self.boughtStocks:
            return False
        numDays = 100
        ema_iter = iter(twentyEMA)
        cur_date = next(ema_iter)
        prev_date = next(ema_iter)
        # if timestamp is attached to current date
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        # end date is current date - numDays
        end_date = str(cur_date - dt.timedelta(numDays))
        cur_date = str(cur_date)
        dipFound = False
        crossovers = 0
        todays_date = max(prices)
        if todays_date not in twentyEMA or todays_date not in fiftyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        todays_t_ema = float(twentyEMA[todays_date]["EMA"])
        todays_f_ema = float(fiftyEMA[todays_date]["EMA"])
        todays_price = float(prices[todays_date]["4. close"])
        if todays_t_ema < todays_f_ema:
            return False
        # Only check for last numDays amount of days
        while cur_date > end_date:
            # Ensure that given date is in fifty EMA and in prices
            if cur_date not in fiftyEMA or cur_date not in prices:
                cur_date = next(ema_iter)
                # print("Continuing. Date not found in both twenty and fifty EMA.")
                continue
            cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
            cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
            cur_price = float(prices[cur_date]["4. close"])
            # Triple crossover strategy code
            if cur_twenty_ema < cur_fifty_ema:
                return False
            if cur_price < cur_twenty_ema and cur_price < cur_fifty_ema:
                return False
            five_day_max = self.get_five_day_max(prices=prices, start_date=cur_date)
            max_dip_diff = (five_day_max - cur_price) / five_day_max
            if max_dip_diff >= 0.005:  # Change this to TODO
                dipFound = True
                # New code between this and above comment
            if dipFound and cur_price > cur_twenty_ema: # todo - replace with dip diff
                # print("crossover 1")
                dipFound = False
                crossovers += 1
                # Buy at 3rd dip.
            if crossovers >= 2:
                print("{} has been bought at {} on {}".format(tick, todays_price, todays_date))
                self.boughtStocks[tick] = (todays_price, todays_date)
                return True
            cur_date = prev_date
            prev_date = str(next(ema_iter))
            # is_buy = crossovers >= 2 # TODO - clean this up
        return False

    @staticmethod
    def get_five_day_max(prices: dict, start_date: str) -> float:
        start = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        five_day_max = "0"
        for day in range(5):
            cur_date = str(start - dt.timedelta(day))
            if cur_date not in prices: continue
            five_day_max = max(five_day_max, prices[cur_date]["4. close"])
        return float(five_day_max)


    def basicSell(self, prices: dict, twentyEMA: dict, fiftyEMA: dict, tick: str) -> bool:
        pass

    def basicCrossoverTest(self, prices: dict, twentyEMA: dict, fiftyEMA: dict, tick: str) -> bool:

        if tick in self.boughtStocks:
            return False
        if not twentyEMA or not fiftyEMA:
            print("How is this happening")
            return False
        todays_date = max(prices)
        if todays_date not in twentyEMA or todays_date not in fiftyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        todays_t_ema = float(twentyEMA[todays_date]["EMA"])
        todays_f_ema = float(fiftyEMA[todays_date]["EMA"])
        todays_price = float(prices[todays_date]["4. close"])
        ema_iter = iter(twentyEMA)
        curDate = next(ema_iter)
        if curDate not in fiftyEMA:
            commonDateFound = False
            for day in range(5):
                curDate = next(ema_iter)
                if curDate in fiftyEMA:
                    commonDateFound = True
                    break
            if not commonDateFound:
                print("No shared date for twenty EMA and fifty EMA within past 5 days.")
                return False
        latest_twenty_ema = float(twentyEMA[curDate]["EMA"])
        latest_fifty_ema = float(fiftyEMA[curDate]["EMA"])
        if latest_twenty_ema > latest_fifty_ema:
            print("{} has been bought at {} on {}".format(tick, todays_price, todays_date))
            self.boughtStocks[tick] = (todays_price, todays_date)
        else:
            return False

    def checkSellStock(self, twentyEMA: dict, fiftyEMA: dict, prices: dict, tick: str) -> float:
        if tick not in self.boughtStocks:
            return 0.0
        cur_date = max(prices)
        # cur_date = next(iter(twentyEMA))
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        cur_date = str(cur_date)
        if cur_date not in twentyEMA:
            print("No common date")
            return 0.0
        cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
        cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
        cur_price = float(prices[cur_date]["4. close"])
        heldForTwoMonths = self.boughtStocks[tick][1] <= str(dt.datetime.strptime(cur_date, "%Y-%m-%d").date() - dt.timedelta(60))
        if cur_price - self.boughtStocks[tick][0] == 0:
            return 0.0
        if cur_twenty_ema < cur_fifty_ema and heldForTwoMonths:
            print("{} has been sold at {} on {}\n".format(tick, cur_price, cur_date))
            stock_profit = (cur_price - self.boughtStocks[tick][0]) / self.boughtStocks[tick][0]
            del self.boughtStocks[tick]
            self.soldStocks[tick] = cur_price
            return stock_profit
        return 0.0

    def checkSellDip(self, twentyEMA: dict, fiftyEMA: dict, prices: dict, tick: str):
        # TODO - Deal with duplicate code.
        numDays = 30
        ema_iter = iter(twentyEMA)
        cur_date = next(ema_iter)
        prev_date = next(ema_iter)
        # if timestamp is attached to current date
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        # end date is current date - numDays
        end_date = str(cur_date - dt.timedelta(numDays))
        cur_date = str(cur_date)
        while cur_date > end_date:
            if cur_date not in fiftyEMA or cur_date not in prices:
                cur_date = next(ema_iter)
                # print("Continuing. Date not found in both twenty and fifty EMA.")
                continue
            cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
            cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
            cur_price = float(prices[cur_date]["4. close"])
            # prev_price = float(prices[prev_date]["4. close"])
            if cur_twenty_ema > cur_fifty_ema:  # We won't want to sell if this is true
                if tick in self.sellDip:
                    self.sellDip.remove(tick)
                return False
            if cur_price < cur_fifty_ema and cur_price < cur_fifty_ema:
                self.sellDip.add(tick)
                return True
            cur_date = str(next(ema_iter))
        if tick in self.sellDip:
            self.sellDip.remove(tick)
            return False

        # dipFound = False
        # while cur_date < end_date:
        #     # if stock has experienced a dip, and the price is >= current 20 EMA then SELL.
        #     if cur_twenty_ema > cur_fifty_ema:
        #         return False
        #     if cur_price < cur_twenty_ema and cur_price < cur_fifty_ema:
        #         dipFound = True
        #     if dipFound and (cur_price >= cur_twenty_ema):
        #         stock_profit = self.boughtStocks[stock] - cur_price
        #         self.profit += stock_profit
        #         print("SEll {}!!!!".format(stock))
        #         print("Profit: {}".format(stock_profit))
        #         del self.boughtStocks[stock]
        #         self.soldStocks[stock] = cur_price
        #     # if cur_price < cur_twenty_ema:
        #     #     self.sellDip.add(stock)
        #     cur_date = str(next(ema_iter))




if __name__ == '__main__':
    ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")
    # p = ta.getPrice("IBM")
    # tEMA = ta.getEMA("IBM", "20")
    # print(p)
    # print(tEMA)

    att = 0
    fail = True
    ticks = []
    while att < 10:
        try:
            scraper = YahooSymbolScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                         "../geckodriver.exe",
                                         "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
            ticks = scraper.generateTickers()
        except (NoSuchWindowException, WebDriverException) as e:
            att += 1
            print(e)
            print("Scraper failed. Attempts={}".format(att))
        else:
            break