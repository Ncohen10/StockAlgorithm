import requests
import time
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def getEMA(self, symbol: str, timePeriod: str, interval: str = "daily") -> list:  # Only set up for equity
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfEMA = data.get("Technical Analysis: EMA")
        return dictOfEMA

    def getPrice(self, symbol: str) -> list:
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                            + symbol + "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfPrices = data.get("Time Series (Daily)")
        return dictOfPrices

    @staticmethod
    def recentCrossover(twentyEMA: list, fiftyEMA: list, prices: list) -> bool:
        day = 0
        numDays = 50
        while day <= numDays:
            if twentyEMA[day] > fiftyEMA[day]:
                if prices[day] > twentyEMA[day]:
                    print("{} is price. Greater than EMA ({}) at day {}".format(prices[day], twentyEMA[day], day))
                else:
                    print("{} is price. LESS than EMA ({}) at day {}".format(prices[day], twentyEMA[day], day))
                return True
        return False

    @staticmethod
    def isPotentialCrossover(twentyEMA: list, fiftyEMA: list, prices: list):
        if not twentyEMA or not fiftyEMA:
            print("One or more EMAs are empty")
            return False
        if twentyEMA[0] > fiftyEMA[0]:
            return False
        diff = abs(fiftyEMA[0] - twentyEMA[0])
        tolerance = 0.05
        if diff // max(fiftyEMA[0], twentyEMA[0]) <= tolerance:  # if difference is within 5%
            print("within range")
            return True
        return False


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                   "../geckodriver.exe",
                                   "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    ticks = scraper.generateTickers()
    print(ticks)
    count = 0
    for stock in ticks:
        if count % 5 == 0: time.sleep(65)
        tEMA = ta.getEMA(stock, "20")
        count += 1
        if count % 5 == 0: time.sleep(65)
        fEMA = ta.getEMA(stock, "50")
        count += 1
        if count % 5 == 0: time.sleep(65)
        priceHistory = ta.getPrice(stock)
        count += 1
        print("testing: {}".format(stock))
        if tEMA: print("tEMA: {}".format(tEMA[0]))
        if fEMA: print("fEMA: {}".format(fEMA[0]))
        if priceHistory: print("price: {}".format(priceHistory[0]))
        if tEMA and fEMA and tEMA[0] > fEMA[0]:
            isCrossover = ta.recentCrossover(tEMA, fEMA, priceHistory)
            if isCrossover:
                print("FOUND CROSSOVER!")
