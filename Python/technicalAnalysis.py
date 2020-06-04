import requests
import time
import datetime as dt
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
        numDays = 50
        ema_iter = iter(twentyEMA)
        cur_date = next(ema_iter)
        # strip timestamp from current date
        cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        # end date is current date - numDays
        end_date = cur_date - dt.timedelta(numDays)

        while cur_date > end_date:
            # Ensure that date is in fifty EMA and in prices
            if cur_date not in fiftyEMA or cur_date not in prices:
                cur_date = next(ema_iter)
                continue
            cur_twenty_ema = twentyEMA[cur_date]["4. close"]
            cur_fifty_ema = fiftyEMA[cur_date]["4. close"]
            cur_price = prices[cur_date]["4. close"]
            dipFound = False
            crossovers = 0
            # Triple crossover strategy code
            if cur_twenty_ema < cur_fifty_ema:
                print("Not a triple crossover")
                return False
            if cur_price < cur_twenty_ema:
                dipFound = True
            elif dipFound and cur_price > cur_twenty_ema:
                dipFound = False
                crossovers += 1
            if crossovers == 3:
                print("TRIPLE CROSSOVER IDENTIFIED !!!")
                return True
            cur_date = next(ema_iter)

        # no triple crossover found within specified time period.
        return False

    @staticmethod
    def isPotentialCrossover(twentyEMA: dict, fiftyEMA: dict) -> bool:
        curDate = next(iter(twentyEMA))
        if not twentyEMA or not fiftyEMA:
            print("One or more EMAs are empty")
            return False
        if twentyEMA[curDate]['4. close'] > fiftyEMA[curDate]['4. close']:
            return False
        diff = (fiftyEMA[curDate]['4. close'] - twentyEMA[curDate]['4. close']) // fiftyEMA[curDate]
        tolerance = 0.05
        if diff <= tolerance:  # if difference is within 5%
            print("within range")
            return True
        return False


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    # p = ta.getPrice("IBM")
    tEMA = ta.getEMA("IBM", "20")
    print(ta.isRecentCrossover(tEMA, tEMA, {}))

    # scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    #                                "../geckodriver.exe",
    #                                "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    # att = 0
    # fail = True
    # while att < 5:
    #     try:
    #         ticks = scraper.generateTickers()
    #     except Exception:
    #         att += 1
    #         print("Failed. Attempts={}".format(att))
    #     else:
    #         break
    # count = 0
    # today = str(datetime.date.today())
    # print(ticks)
    # for stock in ticks:
    #     if count % 5 == 0: time.sleep(62)
    #     count += 1
    #     tEMA = ta.getEMA(stock, "20")
    #     if count % 5 == 0: time.sleep(62)
    #     count += 1
    #     fEMA = ta.getEMA(stock, "50")
    #     if count % 5 == 0: time.sleep(62)
    #     count += 1
    #     priceDict = ta.getPrice(stock)
    #     print("testing: {}".format(stock))
    #     print("price: {}".format(priceDict[today]))
    #     print("twenty EMA: {}".format(tEMA[today]))
    #     print("fifty EMA: {}".format(fEMA[today]))
    #     if ta.isRecentCrossover(tEMA, fEMA, priceDict):
    #         print("{} is a recent crossover!".format(stock))
    #     if ta.isPotentialCrossover(tEMA, fEMA):
    #         print("{} is a potential crossover!".format(stock))
    #     print("\n")