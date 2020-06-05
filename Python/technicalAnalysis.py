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
        if not dictOfEMA:
            print(resp)
            print(data)
            print("getEMA() is returning an empty dictionary for some reason. May be too many API calls.")
        return dictOfEMA

    def getPrice(self, symbol: str) -> dict:  #TODO - make sure the API call is correct
        resp = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
                            + symbol + "&interval=1min&apikey=" + self.ALPHA_VANTAGE_API_KEY)
        if resp.status_code != 200:
            raise Exception("Error in request to Alpha Vantage. Response was:\n {}".format(resp))
        data = resp.json()
        dictOfPrices = data.get("Time Series (Daily)")
        return dictOfPrices

    @staticmethod
    def isTripleCrossover(twentyEMA: dict, fiftyEMA: dict, prices: dict) -> bool:
        numDays = 50
        ema_iter = iter(twentyEMA)
        cur_date = next(ema_iter)
        # if timestamp is attached to current date
        if len(cur_date) > 10:
            # Remove timestamp and transform into a datetime object
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d %H:%M:%S").date()
        else:
            cur_date = dt.datetime.strptime(cur_date, "%Y-%m-%d").date()
        # end date is current date - numDays
        end_date = str(cur_date - dt.timedelta(numDays))
        cur_date = str(cur_date)
        dipFound = False
        # Only check for last numDays amount of days
        while cur_date > end_date:
            # Ensure that given date is in fifty EMA and in prices
            if cur_date not in fiftyEMA or cur_date not in prices:
                cur_date = next(ema_iter)
                print("Continuing. Date not found in both twenty and fifty EMA.")
                continue
            cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
            cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
            cur_price = float(prices[cur_date]["4. close"])
            crossovers = 0
            # Triple crossover strategy code
            if cur_twenty_ema < cur_fifty_ema:
                return False
            if cur_price < cur_twenty_ema:
                dipFound = True
            elif dipFound and cur_price > cur_twenty_ema:
                dipFound = False
                crossovers += 1
            if crossovers == 3:
                print("Buy")
                return True
            cur_date = next(str(ema_iter))

        # no triple crossover found within specified time period.
        return False


    # Checks if the
    @staticmethod
    def isPotentialCrossover(twentyEMA: dict, fiftyEMA: dict) -> bool:
        if not twentyEMA or not fiftyEMA:
            print("How is this happening")
            return False
        ema_iter = iter(twentyEMA)
        curDate = next(ema_iter)
        if curDate not in fiftyEMA:
            commonDateFound = False
            for day in range(3):
                curDate = next(ema_iter)
                if curDate in fiftyEMA:
                    commonDateFound = True
                    break
            if not commonDateFound:
                print("No shared date for twenty EMA and fifty EMA within past 3 days.")
                return False
        print(twentyEMA[curDate])
        latest_twenty_ema = float(twentyEMA[curDate]["EMA"])
        latest_fifty_ema = float(fiftyEMA[curDate]["EMA"])

        if latest_twenty_ema > latest_fifty_ema:
            return False
        # Ensure the difference of the fifty and twenty ema are within 5% of eachother
        diff = abs(latest_fifty_ema - latest_twenty_ema) // latest_fifty_ema
        print("difference of twenty and fifty EMA: {}".format(diff))
        tolerance = 0.05  # Make higher to be less selective but also have less accurate predictions
        if diff <= tolerance:
            print("within range")
            return True
        return False


if __name__ == '__main__':
    ta = technicalAnalysis("MA6YR6D5TVXK1W67")
    # p = ta.getPrice("IBM")
    # tEMA = ta.getEMA("IBM", "20")
    # print(ta.isPotentialCrossover(tEMA, tEMA))
    # print(ta.checkTripleCrossover(tEMA, tEMA, {}))

    scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                   "../geckodriver.exe",
                                   "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    att = 0
    fail = True
    ticks = []
    while att < 10:
        try:
            scraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                           "../geckodriver.exe",
                                           "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
            ticks = scraper.generateTickers()
        except Exception as e:
            att += 1
            print(e)
            print("Scraper failed. Attempts={}".format(att))
        else:
            break
    count = 0
    print(ticks)
    print('\n')
    for stock in ticks:
        if count % 5 == 0: time.sleep(70)
        count += 1
        tEMA = ta.getEMA(stock, "20")
        if count % 5 == 0: time.sleep(70)
        count += 1
        fEMA = ta.getEMA(stock, "50")
        if count % 5 == 0: time.sleep(70)
        count += 1
        priceDict = ta.getPrice(stock)
        try:
            currentPrice = priceDict[next(iter(priceDict))]
            currentTEMA = tEMA[next(iter(tEMA))]
            currentFEMA = fEMA[next(iter(fEMA))]

            print("testing: {}".format(stock))
            print("{}'s current prince is: {}".format(stock, currentPrice["4. close"]))
            print("current twenty EMA is: {}".format(currentTEMA))
            print("current fifty EMA is: {}".format(currentFEMA))
        except Exception as e:
            print(e)
            pass
        if ta.isPotentialCrossover(tEMA, fEMA) and ta.isTripleCrossover(tEMA, fEMA, priceDict):
            print("{} IS A TRIPLE CROSSOVER!!! \t AHHHHJIJ".format(stock))
        else:
            print("{} does not pass crossover check".format(stock))
        print("\n")