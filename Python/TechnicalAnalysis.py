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
            print(resp)
            print(data)
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

    def isTripleCrossover(self, twentyEMA: dict, fiftyEMA: dict, prices: dict, tick: str) -> bool:
        """
        - Checks for triple crossover, assuming minimum requirements have been met.
        - If triple crossover is found, maps stock to buying price.
        - self.boughStock[stock] = price
        """
        # TODO - Instead of curPrice going below 20EMA, check if curPrice is x less than previous 1-3 days.
        numDays = 100
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
        crossovers = 0
        # Only check for last numDays amount of days
        while cur_date > end_date:
            # Ensure that given date is in fifty EMA and in prices
            if cur_date not in fiftyEMA or cur_date not in prices:
                cur_date = next(ema_iter)
                # print("Continuing. Date not found in both twenty and fifty EMA.")
                continue
            cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
            cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
            cur_price = float(prices[cur_date]["4. close"])
            # Triple crossover strategy code
            if cur_twenty_ema < cur_fifty_ema:
                return False
            if cur_price < cur_twenty_ema:  # Change this to TODO
                dipFound = True
                # print("DIP")
                # Buy at 3rd dip.
                if crossovers == 2:
                    # print("Buy")
                    self.boughtStocks[tick] = cur_price
                    return True
                # New code between this and above comment
            elif dipFound and cur_price > cur_twenty_ema:
                # print("crossover 1")
                dipFound = False
                crossovers += 1
            # if crossovers == 3:
            #     print("Buy")
            #     return True
            cur_date = str(next(ema_iter))

        # no triple crossover found within specified time period.
        # print("Ran out of days")
        return False

    def meetsCrossoverRequirements(self, twentyEMA: dict, fiftyEMA: dict, tick: str) -> bool:
        if tick in self.boughtStocks:
            return False
        if not twentyEMA or not fiftyEMA:
            print("How is this happening")
            return False
        ema_iter = iter(twentyEMA)
        curDate = next(ema_iter)
        if curDate not in fiftyEMA:
            commonDateFound = False
            for day in range(5):
                curDate = next(ema_iter)
                if curDate in fiftyEMA:
                    commonDateFound = True
                    break
            if not commonDateFound:
                print("No shared date for twenty EMA and fifty EMA within past 3 days.")
                return False
        latest_twenty_ema = float(twentyEMA[curDate]["EMA"])
        latest_fifty_ema = float(fiftyEMA[curDate]["EMA"])

        # if latest_twenty_ema > latest_fifty_ema:
        #     return False
        # Ensure the difference of the fifty and twenty ema are within 5% of eachother
        diff = abs(latest_fifty_ema - latest_twenty_ema) / latest_fifty_ema
        # print("difference of twenty and fifty EMA: {}".format(diff))
        tolerance = 0.05  # Make higher to be less selective but also have less accurate predictions
        if diff <= tolerance:
            # print("within tolerance")
            return True
        return False

    def checkSell(self, twentyEMA: dict, fiftyEMA: dict, prices: dict, stock: str):
        # TODO - Perhaps just sell when 20EMA crosses below 50EMA. Or when price trades below 20EMA/50EMA
        # TODO - Deal with duplicate code.
        dipFound = False
        numDays = 100
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
        cur_twenty_ema = float(twentyEMA[cur_date]["EMA"])
        cur_fifty_ema = float(fiftyEMA[cur_date]["EMA"])
        cur_price = float(prices[cur_date]["4. close"])
        while cur_date < end_date:
            # if stock has experienced a dip, and the price is >= current 20 EMA then SELL.
            if cur_twenty_ema > cur_fifty_ema:
                return False
            if (stock in self.sellDip) and (cur_price >= cur_twenty_ema):
                stock_profit = self.boughtStocks[stock] - cur_price
                self.profit += stock_profit
                print("SEll {}!!!!".format(stock))
                print("Profit: {}".format(stock_profit))
                del self.boughtStocks[stock]
                self.soldStocks[stock] = cur_price
            if cur_price < cur_twenty_ema:
                self.sellDip.add(stock)
            cur_date = str(next(ema_iter))

        """
            - Requirements:
                - while 20 EMA < 50 EMA:
                    - prices dip below 20&50 EMA
                    - sell once price rises to 20 EMA 
            """



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

    count = 0
    print(ticks)
    print('\n')
    for tick in ticks:
        if count % 5 == 0: time.sleep(70)
        count += 1
        tEMA = ta.getEMA(tick, "20")
        if count % 5 == 0: time.sleep(70)
        count += 1
        fEMA = ta.getEMA(tick, "50")
        if count % 5 == 0: time.sleep(70)
        count += 1
        priceDict = ta.getPrice(tick)

        currentPrice = priceDict[next(iter(priceDict))]
        currentTEMA = tEMA[next(iter(tEMA))]
        currentFEMA = fEMA[next(iter(fEMA))]

        print("testing: {}".format(tick))
        print("{}'s current prince is: {}".format(tick, currentPrice["4. close"]))
        print("current 20 EMA is: {}".format(currentTEMA["EMA"]))
        print("current fifty EMA is: {}".format(currentFEMA["EMA"]))

        if ta.meetsCrossoverRequirements(tEMA, fEMA, tick):
            print("{} is potential crossover".format(tick))
            if ta.isTripleCrossover(tEMA, fEMA, priceDict, tick):
                print("{} IS A TRIPLE CROSSOVER!!! \t AHHHHJIJ".format(tick))
            else:
                print("{} Is not a triple crossover".format(tick))
        else:
            print("difference is not within tolerance".format(tick))
        ta.checkSell(tEMA, fEMA, priceDict, tick)
        print("\n")

#TODO - make function to check whether a given stock should be sold.