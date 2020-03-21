import alpha_vantage
import requests
from Python.seleniumStockScraper import seleniumStockScraper


class technicalAnalysis:

    def __init__(self, api_key):
        self.ALPHA_VANTAGE_API_KEY = api_key

    def EMA(self):
        webScraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                          "../geckodriver.exe",
                                          "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
        symbols = webScraper.generateTickers()
        # symbols = ["SHOP"]
        if not symbols:
            raise Exception("No tickers were found from web scraper.")
        resp = requests.get("https://www.alphavantage.co/query?"
                            "function=EMA&symbol=" + symbols[0] +
                            "&interval=weekly&time_period=10&"
                            "series_type=open&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code == 200:
            stockData = resp.content
            print(stockData)
            return stockData
        else:
            raise Exception("Error in request to Alpha Vantage.\n Response was: {}".format(resp))


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    ta.EMA()
