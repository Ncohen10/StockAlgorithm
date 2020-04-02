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
        if not dictOfEMA:
            return []
        EMAList = []
        for EMA in dictOfEMA:
            currentEMA = dictOfEMA[EMA]["EMA"]  # get first key from json/EMA dict, then get its EMA.
            EMAList.append(currentEMA)
        return EMAList

    def getPrice(self, symbol: str) -> list:
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                            + symbol + "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfPrices = data.get("Time Series (Daily)")
        if not dictOfPrices:
            return []
        priceList = []
        for price in dictOfPrices:
            currentPrice = float(dictOfPrices[price]["3. low"])
            priceList.append(currentPrice)
        return priceList

    @staticmethod
    def testCrossover(twentyEMA: list, fiftyEMA: list, prices: list):
        day = 0
        crossovers = 0
        numOfDays = len(twentyEMA)
        dipFound = False
        while day < numOfDays and twentyEMA[day] > fiftyEMA[day]:
            if prices[day] < twentyEMA[day]:
                dipFound = True
            elif dipFound and prices[day] > twentyEMA[day]:
                dipFound = False
                crossovers += 1
            if crossovers == 3:
                print("Buy")
                return True
            day += 1
        return False


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    # scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    #                                "../geckodriver.exe",
    #                                "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    # ticks = scraper.generateTickers()
    ticks = ["IBM"]
    tEMA = ta.getEMA(ticks[0], "20")
    fEMA = ta.getEMA(ticks[0], "50")
    priceHistory = ta.getPrice(ticks[0])
    isCrossover = ta.testCrossover(tEMA, fEMA, priceHistory)
    print(isCrossover)
