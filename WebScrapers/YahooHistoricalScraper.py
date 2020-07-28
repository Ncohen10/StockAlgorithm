from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options


class YahooHistoricalScraper:

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
            executable_path=geckoPath  # download/install GD and drag it into the selenium_stuff directory maybe
        )
        self.yahooURL = yahooURL

    def get_historical_csv(self):
        url = "https://finance.yahoo.com/quote/MSFT/history?p=MSFT"
        os.system('wget %s' % url)

if __name__ == '__main__':
    s = YahooHistoricalScraper()
    s.get_historical_csv()