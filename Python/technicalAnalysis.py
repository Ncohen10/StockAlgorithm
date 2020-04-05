import requests
import time
import datetime
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def getEMA(self, symbol: str, timePeriod: str, interval: str = "daily") -> dict:  # Only set up for equity
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfEMA = data.get("Technical Analysis: EMA")
        return dictOfEMA

    def getPrice(self, symbol: str) -> dict:
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                            + symbol + "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfPrices = data.get("Time Series (Daily)")
        return dictOfPrices

    @staticmethod
    def isRecentCrossover(twentyEMA: dict, fiftyEMA: dict, prices: dict) -> bool:
        day = 0
        numDays = 50
        curDate = datetime.date.today()
        while day <= numDays:
            if twentyEMA[curDate] > fiftyEMA[curDate]:
                if prices[curDate] > twentyEMA[curDate]:
                    print("{} is price. Greater than EMA ({}) at day {}".format(prices[curDate], twentyEMA[curDate], curDate))
                else:
                    print("{} is price. LESS than EMA ({}) at day {}".format(prices[curDate], twentyEMA[curDate], curDate))
                return True
            day += 1
            curDate -= datetime.timedelta(1)
        return False

    @staticmethod
    def isPotentialCrossover(twentyEMA: dict, fiftyEMA: dict) -> bool:
        curDate = datetime.date.today()
        if not twentyEMA or not fiftyEMA:
            print("One or more EMAs are empty")
            return False
        if twentyEMA[curDate] > fiftyEMA[curDate]:
            return False
        diff = (fiftyEMA[curDate] - twentyEMA[curDate]) // fiftyEMA[curDate]
        tolerance = 0.05
        if diff <= tolerance:  # if difference is within 5%
            print("within range")
            return True
        return False


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                   "../geckodriver.exe",
                                   "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    ticks = scraper.generateTickers()
    count = 0
    today = datetime.date.today()
    for stock in ticks:
        if count % 5 == 0: time.sleep(62)
        count += 1
        tEMA = ta.getEMA(stock, "20")
        if count % 5 == 0: time.sleep(62)
        count += 1
        fEMA = ta.getEMA(stock, "50")
        if count % 5 == 0: time.sleep(62)
        count += 1
        priceDict = ta.getPrice(stock)
        print("testing: {}".format(stock))
        print("price: {}".format(priceDict[today]))
        print("twenty EMA: {}".format(tEMA[today]))
        print("fifty EMA: {}".format(fEMA[today]))
        if ta.isRecentCrossover(tEMA, fEMA, priceDict):
            print("{} is a recent crossover!".format(stock))
        if ta.isPotentialCrossover(tEMA, fEMA):
            print("{} is a potential crossover!".format(stock))
        print("\n")