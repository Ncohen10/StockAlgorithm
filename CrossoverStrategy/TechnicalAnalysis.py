import requests
import random
import datetime as dt
import time
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from StockAlgorithm.WebScrapers.YahooSymbolScraper import YahooSymbolScraper


class TechnicalAnalysis:

    # TODO - Put Alphavantage API call methods into separate class.

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key
        self.boughtStocks = {}
        self.soldStocks = {}  # map of stocks to price sold
        self.sellDip = set()  # Set of stocks that have experienced a sell dip.
        self.profit = 0

    def getEMA(self, symbol: str, timePeriod: str, interval: str = "daily") -> dict:  # Only set up for equity
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfEMA = data.get("Technical Analysis: EMA")
        if not dictOfEMA:
            print("getEMA() is returning an empty dictionary. May be too many API calls or there isn't data for these dates.")
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

    def checkBuyStock(self, prices: dict, thirtyEMA: dict, ninetyEMA: dict, tick: str) -> bool:
        if tick in self.boughtStocks:
            return False
        todays_date = max(prices)
        # make sure curDate and next(iter(fiveEMA)) are same
        if todays_date not in thirtyEMA or todays_date not in ninetyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        todays_price = float(prices[todays_date]["4. close"])
        latest_thirty_ema = float(thirtyEMA[todays_date]["EMA"])
        latest_ninety_ema = float(ninetyEMA[todays_date]["EMA"])
        if latest_thirty_ema < latest_ninety_ema:
            print("{} has been bought at {} on {}".format(tick, todays_price, todays_date))
            self.boughtStocks[tick] = (todays_price, todays_date)
            return True
        else:
            return False

    def checkSellStock(self, thirtyEMA: dict, ninetyEMA: dict, prices: dict, tick: str) -> float:
        if tick not in self.boughtStocks:
            return 0.0
        cur_date = max(prices)
        # cur_date = next(iter(fiveEMA))
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        cur_date = str(cur_date)
        if cur_date not in thirtyEMA or cur_date not in ninetyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        cur_thirty_ema = float(thirtyEMA[cur_date]["EMA"])
        cur_ninety_ema = float(ninetyEMA[cur_date]["EMA"])
        cur_price = float(prices[cur_date]["4. close"])
        stop_loss_threshold = 0.75
        # buy_threshold = 1.25
        stock_profit = cur_price / self.boughtStocks[tick][0]

        if stock_profit <= stop_loss_threshold:
            print("{} has been sold at {} on {}".format(tick, cur_price, cur_date))
            del self.boughtStocks[tick]
            self.soldStocks[tick] = cur_price
            return stock_profit
        heldForTwoMonths = self.boughtStocks[tick][1] <= str(dt.datetime.strptime(cur_date, "%Y-%m-%d").date() - dt.timedelta(60))
        if cur_thirty_ema > cur_ninety_ema:
            if stock_profit <= 1.0:
                return 0.0
            print("{} has been sold at {} on {}".format(tick, cur_price, cur_date))
            del self.boughtStocks[tick]
            self.soldStocks[tick] = cur_price
            return stock_profit
        return 0.0
#TODO -  Put API key in naughty folder
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

if __name__ == '__main__':
    API_KEY = input("Paste your API key: ")
    ta = TechnicalAnalysis(API_KEY)
    att = 0
    fail = True
    ticks = []
    boughStocks = []
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
    count = 0
    print(ticks)
    print('\n')
    for tick in ticks:
        if count % 5 == 0: time.sleep(70)
        count += 1
        tEMA = ta.getEMA(tick, "30")
        if count % 5 == 0: time.sleep(70)
        count += 1
        nEMA = ta.getEMA(tick, "90")
        if count % 5 == 0: time.sleep(70)
        count += 1
        priceDict = ta.getPrice(tick)

        currentPrice = priceDict[next(iter(priceDict))]
        currentTEMA = tEMA[next(iter(tEMA))]
        currentNEMA = nEMA[next(iter(nEMA))]

        print("testing: {}".format(tick))
        print("{}'s current prince is: {}".format(tick, currentPrice["4. close"]))
        print("current 30 EMA is: {}".format(currentTEMA["EMA"]))
        print("current 90 EMA is: {}".format(currentNEMA["EMA"]))

        if ta.checkBuyStock(prices=priceDict, thirtyEMA=tEMA, ninetyEMA=nEMA, tick=tick):
            boughStocks.append(tick)
        ta.checkSellStock(prices=priceDict, thirtyEMA=tEMA, ninetyEMA=nEMA, tick=tick)


        print("\n")
        print(boughStocks)
