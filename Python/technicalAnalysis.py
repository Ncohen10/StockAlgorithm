import requests
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def equityEMA(self, symbol, interval, timePeriod): # Only set up for EMA
        resp = requests.get("https://www.alphavantage.co/query?function=EMA&symbol="
                            + symbol + "&interval=" + interval + "&time_period=" + timePeriod +
                            "&series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)

        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage.\n Response was: {}".format(resp))
        data = resp.content
        currentEMA = data["Technical Analysis: EMA"]
    # def getPrice(self, symbol):
    #     resp = requests

if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    # scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    #                                   "../geckodriver.exe",
    #                                   "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    # ticks = scraper.generateTickers()
    ticks = "SHOP"
    ta.equityEMA(symbol=ticks, interval="daily", timePeriod=20) # Maybe the low EMA?
    ta.equityEMA(symbol=ticks, interval="daily", timePeriod=50)

