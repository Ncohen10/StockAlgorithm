from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import *
import time


def elementIsLoaded(driver, cssSelector):
    element = driver.find_element_by_css_selector(cssSelector)
    return element == True


def getTickers(geckoPath: str, firefoxPath: str, yahooScreenURL: str) -> list:
    tickerList = []
    binary = FirefoxBinary(firefoxPath)
    profile = webdriver.FirefoxProfile()
    profile.set_preference('permissions.default.desktop-notification', 1)
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(
        firefox_binary=binary,
        firefox_profile=profile,
        firefox_options=options,
        executable_path=geckoPath  # download/install GD and drag it into the selenium_stuff directory
    )
    print("the type: {}".format(type(driver)))
    tickerCount = 1
    timeout = 10  # max time in seconds to wait for element to appear
    changeButton = "th.Ta\(end\):nth-child(4) > span:nth-child(1)"  # CSS Selector path of "change" button on Yahoo
    driver.get(yahooScreenURL)
    WebDriverWait(driver, timeout).until(
        lambda x: x.find_element_by_css_selector(changeButton))  # wait for changeButton to load
    driver.find_element_by_css_selector(changeButton).click()
    WebDriverWait(driver, timeout).until(
        lambda x: x.find_element_by_css_selector(changeButton))  # wait again...
    driver.find_element_by_css_selector(changeButton).click()
    WebDriverWait(driver, timeout).until(
        lambda x: x.find_element_by_css_selector("tr.simpTblRow:nth-child(1) > td:nth-child(1) > a:nth-child(2)"))  # Now wait for stock tickers to load
    while tickerCount <= 25:  # There are up to 25 stocks listed per page on Yahoo
        try:
            tickerObj = driver.find_elements_by_css_selector(
                "tr.simpTblRow:nth-child(" + str(tickerCount) + ") > td:nth-child(1) > a:nth-child(2)")
            tickerCount += 1
            if tickerObj: tickerList.append(tickerObj[0].text)
            print(tickerList)
            """
            <a href="/quote/PBR?p=PBR" title="Petroleo Brasileiro S.A. - Petrobras" class="Fw(600)" data-reactid="77">PBR</a>
            """
        except (NoSuchElementException, ElementNotInteractableException):
            print("Amount of tickers found: {}".format(tickerCount))
            raise Exception("Out of tickers to choose from on page.")
    return tickerList


getTickers("geckodriver.exe",
           'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
           "https://finance.yahoo.com/screener/predefined/growth_technology_stocks")

# TODO - Finish waitUntilLoad() method
