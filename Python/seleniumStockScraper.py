from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import *
import time


class seleniumStockScraper:

    def __init__(self, firefoxPath, geckoPath, yahooURL):  # Initialize selenium and url to visit
        self.binary = FirefoxBinary(firefoxPath)
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('permissions.default.desktop-notification', 1)
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Firefox(
            firefox_binary=self.binary,
            firefox_profile=self.profile,
            firefox_options=self.options,
            executable_path=geckoPath  # download/install GD and drag it into the selenium_stuff directory
        )
        self.yahooURL = yahooURL

    # Goes to the Yahoo finance page
    def _visitYahoo(self, yahooScreenURL: str) -> None:
        timeout = 10  # max time in seconds to wait for element to appear
        changeButton = "th.Ta\(end\):nth-child(4) > span:nth-child(1)"  # CSS Selector path of "change" button on Yahoo
        stockListings = "tr.simpTblRow:nth-child(1) > td:nth-child(1) > a:nth-child(2)"
        self.driver.get(yahooScreenURL)
        # WebDriverWait(self.driver, timeout).until(   # wait for changeButton to load
        #     lambda x: x.find_element_by_css_selector(changeButton))
        # # Need to hardcode wait times since clicking on button doesn't do anything even though the page is fully loaded
        # # Due to Yahoo website design...
        # time.sleep(10)
        # self.driver.find_element_by_css_selector(changeButton).click()
        # WebDriverWait(self.driver, timeout).until(  # wait again after pressing once...
        #     lambda x: x.find_element_by_css_selector(changeButton))
        # time.sleep(10)
        # self.driver.find_element_by_css_selector(changeButton).click()
        # WebDriverWait(self.driver, timeout).until(
        #     lambda x: x.find_element_by_css_selector(stockListings))  # Now wait for stock tickers to load
        time.sleep(20)

    # Gets stocks from Yahoo finance page
    def _selectTickers(self) -> list:
        tickerCount = 1
        attempts = 0
        tickers = []
        while tickerCount <= 25:  # There are up to 25 stocks listed per page on Yahoo
            try:  # try to select ticker css elements
                tickerObj = self.driver.find_elements_by_css_selector(
                    "tr.simpTblRow:nth-child(" + str(tickerCount) + ") > td:nth-child(1) > a:nth-child(2)")
                tickerCount += 1
                if tickerObj:
                    tickers.append(tickerObj[0].text)
            except (NoSuchElementException, ElementNotInteractableException):
                print("Amount of tickers found: {}".format(tickerCount - 1))
                raise Exception("Wasn't able to find a ticker.")
            except StaleElementReferenceException:
                if attempts == 3:
                    raise
                else:
                    attempts += 1
                    pass
        return tickers

    def generateTickers(self) -> list:
        self._visitYahoo(self.yahooURL)
        tickerList = self._selectTickers()
        return tickerList


if __name__ == '__main__':
    webScraper = seleniumStockScraper("C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                      "../geckodriver.exe",
                                      "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")
    print(webScraper.generateTickers())
