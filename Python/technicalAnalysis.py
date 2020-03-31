import requests
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def getEMA(self, symbol: str, interval: str, timePeriod: str) -> float:  # Only set up for equity
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)

        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage.\n Response was: {}".format(resp))
        data = resp.json()
        dictOfEMA = data["Technical Analysis: EMA"]
        currentEMA = dictOfEMA[next(iter(dictOfEMA))]["EMA"]  # get first key from json/EMA dict, then get its EMA.
        return float(currentEMA)

    def getPrice(self, symbol: str) -> float:
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="
                            + symbol + "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage.\n Response was: {}".format(resp))
        data = resp.json()
        dictOfPrices = data["Time Series (1min)"]
        currentPrice = dictOfPrices[next(iter(dictOfPrices))]["4. close"]
        return float(currentPrice)

if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    # scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    #                                   "../geckodriver.exe",
    #                                   "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    # ticks = scraper.generateTickers()[0]
    # ticks = "SHOP"
    # print(ta.getEquityEMA(symbol=ticks, interval="daily", timePeriod="20"))
    print("current EMA is: {}".format(ta.getEMA(symbol=ticks, interval="daily", timePeriod="50")))
    print("current price is: {}".format(ta.getPrice(ticks)))
