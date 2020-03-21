from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import *


class seleniumStockScraper:

    def __init__(self, firefoxPath, geckoPath, yahooURL):  # Initialize selenium and url to visit
        self.binary = FirefoxBinary(firefoxPath)
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('permissions.default.desktop-notification', 1)
        self.options = Options()
        self.options.headless = False
        self.driver = webdriver.Firefox(
            firefox_binary=self.binary,
            firefox_profile=self.profile,
            firefox_options=self.options,
            executable_path=geckoPath  # download/install GD and drag it into the selenium_stuff directory
        )
        self.yahooURL = yahooURL

    # Goes to the Yahoo finance page
    def __visitYahoo(self, yahooScreenURL: str) -> None:
        timeout = 15  # max time in seconds to wait for element to appear
        changeButton = "th.Ta\(end\):nth-child(4) > span:nth-child(1)"  # CSS Selector path of "change" button on Yahoo
        stockListings = "tr.simpTblRow:nth-child(1) > td:nth-child(1) > a:nth-child(2)"
        self.driver.get(yahooScreenURL)
        WebDriverWait(self.driver, timeout).until(
            lambda x: x.find_element_by_css_selector(changeButton))  # wait for changeButton to load
        print("wait 1 complete")
        self.driver.find_element_by_css_selector(changeButton).click()
        WebDriverWait(self.driver, timeout).until(
            lambda x: x.find_element_by_css_selector(changeButton))  # wait again after pressing once...
        print("wait 2 complete")
        self.driver.find_element_by_css_selector(changeButton).click()
        WebDriverWait(self.driver, timeout).until(
            lambda x: x.find_element_by_css_selector(stockListings))  # Now wait for stock tickers to load

    # Gets stocks from Yahoo finance page
    def __selectTickers(self) -> list:
        tickerCount = 1
        tickers = []
        while tickerCount <= 25:  # There are up to 25 stocks listed per page on Yahoo
            try:
                tickerObj = self.driver.find_elements_by_css_selector(
                    "tr.simpTblRow:nth-child(" + str(tickerCount) + ") > td:nth-child(1) > a:nth-child(2)")
                tickerCount += 1
                if tickerObj:
                    tickers.append(tickerObj[0].text)
            except (NoSuchElementException, ElementNotInteractableException):
                print("Amount of tickers found: {}".format(tickerCount - 1))
                raise Exception("Wasn't able to find a ticker.")
        print(tickers)
        return tickers

    def generateTickers(self) -> list:
        self.__visitYahoo(self.yahooURL)
        tickerList = self.__selectTickers()
        return tickerList


if __name__ == '__main__':
    webScraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                      "../geckodriver.exe",
                                      "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    print(webScraper.generateTickers())
