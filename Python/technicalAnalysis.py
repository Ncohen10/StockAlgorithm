import requests
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def equityEMA(self, symbol: str, interval: str, timePeriod: str):  # Only set up for EMA
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)

        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage.\n Response was: {}".format(resp))
        data = resp.json()
        dictOfEMA = data["Technical Analysis: EMA"]
        currentEMA = dictOfEMA[next(iter(dictOfEMA))]["EMA"]  # get first key from json/EMA dict
        return currentEMA

    def getPrice(self, symbol: str):

if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                      "../geckodriver.exe",
                                      "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    ticks = scraper.generateTickers()[0]
    # ticks = "SHOP"
    print(ta.equityEMA(symbol=ticks, interval="daily", timePeriod="20"))
    print(ta.equityEMA(symbol=ticks, interval="daily", timePeriod="50"))

