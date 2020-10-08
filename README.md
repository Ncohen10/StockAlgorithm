# StockAlgorithm

A profitable stock trading algorithm based on a exponential moving average (EMA) crossover strategy.

## Download and Install
```
git clone https://github.com/Ncohen10/StockAlgorithm
cd StockAlgorithm
py -m pip install -r requirements.txt
```

## Run a Backtest
* Get an Alpha Vantage API key from [here](https://www.alphavantage.co/support/#api-key).
* Run main on the Tests/RunBacktest.py file.
* Paste your API key in console and hit enter.

*Note - Alpha Vantage claims you can make 500 requests per day. I have been able to more than that however.*

**Dates can be taken as parameters for the RunTest() function in the RunBacktest file. They must be entererd in the form YYYY-MM-DD**.

## Scan for Stocks to Buy
* Install [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/) and [geckodriver](https://github.com/mozilla/geckodriver/releases)
* Put the geckodriver.exe file in the root directory
* Run main on CrossoverStrategy/TechnicalAnalysis.py
* Paste Alpha Vantage API key in console (explained above) and hit enter
