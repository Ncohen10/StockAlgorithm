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

    def basicCrossoverTest(self, prices: dict, fiveEMA: dict, twentyEMA: dict, tick: str) -> bool:
        if tick in self.boughtStocks:
            return False
        if not fiveEMA or not twentyEMA:
            print("How is this happening")
            return False
        todays_date = max(prices)
        # make sure curDate and next(iter(fiveEMA)) are same
        if todays_date not in fiveEMA or todays_date not in twentyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        todays_price = float(prices[todays_date]["4. close"])
        # ema_iter = iter(fiveEMA)
        # curDate = next(ema_iter)
        if todays_date not in twentyEMA or todays_date not in fiveEMA:
            commonDateFound = False
            # for day in range(5):
            #     curDate = next(ema_iter)
            #     if curDate in twentyEMA:
            #         commonDateFound = True
            #         break
            if not commonDateFound:
                print("No shared date for twenty EMA and fifty EMA within past 5 days.")
                return False

        latest_twenty_ema = float(twentyEMA[todays_date]["EMA"])
        latest_five_ema = float(fiveEMA[todays_date]["EMA"])
        ema_diff = latest_five_ema / latest_twenty_ema
        # print("difference of twenty and fifty EMA: {}".format(diff))
        if ema_diff >= 1.03 and todays_price >= latest_twenty_ema:
            print("{} has been bought at {} on {}".format(tick, todays_price, todays_date))
            self.boughtStocks[tick] = (todays_price, todays_date)
            return True
        else:
            return False

    def checkSellStock(self, fiveEMA: dict, twentyEMA: dict, prices: dict, tick: str) -> float:
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
        if cur_date not in fiveEMA:
            print("No common date")
            return 0.0
        if cur_date not in fiveEMA or cur_date not in twentyEMA:
            print("date not in 20 EMA or not in 50 EMA")
            return False
        cur_five_ema = float(fiveEMA[cur_date]["EMA"])
        cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
        cur_price = float(prices[cur_date]["4. close"])
        stop_loss_threshold = 0.75
        # buy_threshold = 0.25
        stock_profit = cur_price / self.boughtStocks[tick][0]


        # if stock_profit <= stop_loss_threshold:
        #     print("{} has been stop-loss sold at {} on {}\n".format(tick, cur_price, cur_date))
        #     del self.boughtStocks[tick]
        #     self.soldStocks[tick] = cur_price
        #     return stock_profit
        heldForTwoMonths = self.boughtStocks[tick][1] <= str(dt.datetime.strptime(cur_date, "%Y-%m-%d").date() - dt.timedelta(60))
        if cur_five_ema < cur_twenty_ema:
            if stock_profit <= 1.0:
                return 0.0
            print("{} has been sold at {} on {}\n".format(tick, cur_price, cur_date))
            del self.boughtStocks[tick]
            self.soldStocks[tick] = cur_price
            return stock_profit
        return 0.0

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