import time
from typing import List
from Python.TechnicalAnalysis import TechnicalAnalysis


class Backtesting:

    # dates must be in form "YYYY-MM-DD"
    def __init__(self, test_tickers: List[str], start_date: str, end_date: str):
        self.test_tickers = test_tickers
        self.start_date = start_date
        self.end_date = end_date
        self.ta = TechnicalAnalysis("MA6YR6D5TVXK1W67")

    def test_algorithm(self):
        api_call_count = 1
        for ticker in self.test_tickers:
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            twenty_ema = self.ta.getEMA(symbol=ticker, timePeriod="20", interval="daily")
            twenty_ema = self.filter_dates(twenty_ema)
            # twenty_ema = {'2014-05-05': {'EMA': '192.5629'}, '2014-05-06': {'EMA': '192.4074'}, '2014-05-07': {'EMA': '192.1153'}, '2014-05-08': {'EMA': '191.8338'}, '2014-05-09': {'EMA': '191.5620'}, '2014-05-12': {'EMA': '191.5199'}, '2014-05-13': {'EMA': '191.6409'}, '2014-05-14': {'EMA': '191.6665'}, '2014-05-15': {'EMA': '191.4192'}, '2014-05-16': {'EMA': '190.9288'}, '2014-05-19': {'EMA': '190.5175'}, '2014-05-20': {'EMA': '190.1111'}, '2014-05-21': {'EMA': '189.7053'}, '2014-05-22': {'EMA': '189.3952'}, '2014-05-23': {'EMA': '189.0566'}, '2014-05-27': {'EMA': '188.6513'}, '2014-05-28': {'EMA': '188.2540'}, '2014-05-29': {'EMA': '187.8146'}, '2014-05-30': {'EMA': '187.3922'}, '2014-06-02': {'EMA': '187.1415'}, '2014-06-03': {'EMA': '186.9900'}, '2014-06-04': {'EMA': '186.7728'}, '2014-06-05': {'EMA': '186.5716'}, '2014-06-06': {'EMA': '186.5619'}, '2014-06-09': {'EMA': '186.5294'}, '2014-06-10': {'EMA': '186.4980'}, '2014-06-11': {'EMA': '186.2229'}, '2014-06-12': {'EMA': '185.8665'}, '2014-06-13': {'EMA': '185.4982'}, '2014-06-16': {'EMA': '185.2032'}, '2014-06-17': {'EMA': '184.8886'}, '2014-06-18': {'EMA': '184.6173'}, '2014-06-19': {'EMA': '184.5699'}, '2014-06-20': {'EMA': '184.3814'}, '2014-06-23': {'EMA': '184.1469'}, '2014-06-24': {'EMA': '183.8949'}, '2014-06-25': {'EMA': '183.5477'}, '2014-06-26': {'EMA': '183.2927'}, '2014-06-27': {'EMA': '182.9572'}, '2014-06-30': {'EMA': '182.8022'}, '2014-07-01': {'EMA': '182.6973'}, '2014-07-02': {'EMA': '183.0442'}, '2014-07-03': {'EMA': '183.5533'}, '2014-07-07': {'EMA': '183.9397'}, '2014-07-08': {'EMA': '184.2930'}, '2014-07-09': {'EMA': '184.6156'}, '2014-07-10': {'EMA': '184.7894'}, '2014-07-11': {'EMA': '185.0694'}, '2014-07-14': {'EMA': '185.4009'}, '2014-07-15': {'EMA': '185.7951'}, '2014-07-16': {'EMA': '186.4089'}, '2014-07-17': {'EMA': '186.9757'}, '2014-07-18': {'EMA': '187.4504'}, '2014-07-21': {'EMA': '187.8170'}, '2014-07-22': {'EMA': '188.1763'}, '2014-07-23': {'EMA': '188.7414'}, '2014-07-24': {'EMA': '189.2375'}, '2014-07-25': {'EMA': '189.8149'}, '2014-07-28': {'EMA': '190.2420'}, '2014-07-29': {'EMA': '190.7237'}, '2014-07-30': {'EMA': '191.1501'}, '2014-07-31': {'EMA': '191.3110'}, '2014-08-01': {'EMA': '191.2338'}, '2014-08-04': {'EMA': '191.0544'}, '2014-08-05': {'EMA': '190.8349'}, '2014-08-06': {'EMA': '190.3135'}, '2014-08-07': {'EMA': '189.9636'}, '2014-08-08': {'EMA': '189.4338'}, '2014-08-11': {'EMA': '189.2791'}, '2014-08-12': {'EMA': '189.1049'}, '2014-08-13': {'EMA': '188.9997'}, '2014-08-14': {'EMA': '188.8635'}, '2014-08-15': {'EMA': '188.7670'}, '2014-08-18': {'EMA': '188.7035'}, '2014-08-19': {'EMA': '188.8308'}, '2014-08-20': {'EMA': '188.9288'}, '2014-08-21': {'EMA': '189.1165'}, '2014-08-22': {'EMA': '189.2740'}, '2014-08-25': {'EMA': '189.4755'}, '2014-08-26': {'EMA': '189.6226'}, '2014-08-27': {'EMA': '189.9471'}, '2014-08-28': {'EMA': '190.0922'}, '2014-08-29': {'EMA': '190.3005'}, '2014-09-02': {'EMA': '190.5271'}, '2014-09-03': {'EMA': '190.7046'}, '2014-09-04': {'EMA': '190.7984'}, '2014-09-05': {'EMA': '190.7728'}, '2014-09-08': {'EMA': '190.7707'}, '2014-09-09': {'EMA': '190.7297'}, '2014-09-10': {'EMA': '190.6716'}, '2014-09-11': {'EMA': '190.7105'}, '2014-09-12': {'EMA': '190.7828'}, '2014-09-15': {'EMA': '190.8435'}, '2014-09-16': {'EMA': '190.8822'}, '2014-09-17': {'EMA': '191.1049'}, '2014-09-18': {'EMA': '191.2654'}, '2014-09-19': {'EMA': '191.5772'}, '2014-09-22': {'EMA': '191.7813'}, '2014-09-23': {'EMA': '191.8736'}, '2014-09-24': {'EMA': '191.7904'}, '2014-09-25': {'EMA': '191.8151'}, '2014-09-26': {'EMA': '191.5403'}, '2014-09-29': {'EMA': '191.2517'}, '2014-09-30': {'EMA': '191.0982'}, '2014-10-01': {'EMA': '190.9851'}, '2014-10-02': {'EMA': '190.6684'}, '2014-10-03': {'EMA': '190.4247'}, '2014-10-06': {'EMA': '190.3548'}, '2014-10-07': {'EMA': '190.1086'}, '2014-10-08': {'EMA': '189.7144'}, '2014-10-09': {'EMA': '189.6578'}, '2014-10-10': {'EMA': '189.2961'}, '2014-10-13': {'EMA': '188.9336'}, '2014-10-14': {'EMA': '188.5485'}, '2014-10-15': {'EMA': '187.9687'}, '2014-10-16': {'EMA': '187.1907'}, '2014-10-17': {'EMA': '186.6240'}, '2014-10-20': {'EMA': '184.7403'}, '2014-10-21': {'EMA': '182.9936'}, '2014-10-22': {'EMA': '181.0332'}, '2014-10-23': {'EMA': '179.2320'}, '2014-10-24': {'EMA': '177.5984'}, '2014-10-27': {'EMA': '176.1129'}, '2014-10-28': {'EMA': '174.7688'}, '2014-10-29': {'EMA': '173.7746'}, '2014-10-30': {'EMA': '172.7961'}, '2014-10-31': {'EMA': '172.0993'}, '2014-11-03': {'EMA': '171.3518'}, '2014-11-04': {'EMA': '170.6840'}, '2014-11-05': {'EMA': '169.9646'}, '2014-11-06': {'EMA': '169.1375'}, '2014-11-07': {'EMA': '168.4025'}, '2014-11-10': {'EMA': '167.7832'}, '2014-11-11': {'EMA': '167.3943'}, '2014-11-12': {'EMA': '166.9072'}, '2014-11-13': {'EMA': '166.4399'}, '2014-11-14': {'EMA': '166.0265'}, '2014-11-17': {'EMA': '165.8488'}, '2014-11-18': {'EMA': '165.7422'}, '2014-11-19': {'EMA': '165.3906'}, '2014-11-20': {'EMA': '164.9677'}, '2014-11-21': {'EMA': '164.6689'}, '2014-11-24': {'EMA': '164.3709'}, '2014-11-25': {'EMA': '164.2070'}, '2014-11-26': {'EMA': '163.9901'}, '2014-11-28': {'EMA': '163.8720'}, '2014-12-01': {'EMA': '163.6594'}, '2014-12-02': {'EMA': '163.5462'}, '2014-12-03': {'EMA': '163.4437'}, '2014-12-04': {'EMA': '163.4976'}, '2014-12-05': {'EMA': '163.5083'}, '2014-12-08': {'EMA': '163.4875'}, '2014-12-09': {'EMA': '163.2354'}, '2014-12-10': {'EMA': '163.2139'}, '2014-12-11': {'EMA': '162.9859'}, '2014-12-12': {'EMA': '162.7254'}}
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            fifty_ema = self.ta.getEMA(symbol=ticker, timePeriod="50", interval="daily")
            fifty_ema = self.filter_dates(fifty_ema)
            if api_call_count % 5 == 0: time.sleep(70)
            api_call_count += 1
            prices = self.ta.getPrice(symbol=ticker, fullOutput=True)
            prices = self.filter_dates(prices)

            print("testing: {}".format(ticker))
            twenty_ema = self.filter_dates(twenty_ema)
            twenty_ema_gen = self.stock_info_generator(date_dict=twenty_ema)
            fifty_ema_gen = self.stock_info_generator(date_dict=fifty_ema)
            price_gen = self.stock_info_generator(date_dict=prices)

            max_days = len(min(twenty_ema, fifty_ema, prices, key=len)) - 101
            print("Max days: {}".format(max_days))
            for day in range(max_days):
                cur_t_ema = next(twenty_ema_gen)
                cur_f_ema = next(fifty_ema_gen)
                cur_day_prices = next(price_gen)
                if self.ta.meetsCrossoverRequirements(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, tick=ticker):
                    if self.ta.isTripleCrossover(cur_t_ema, cur_f_ema, cur_day_prices, tick=ticker):
                        print("{} has been bought".format(ticker))
                if ticker in self.ta.boughtStocks:
                    self.ta.checkSell(twentyEMA=cur_t_ema, fiftyEMA=cur_f_ema, prices=cur_day_prices, stock=ticker)
        print("TOTAL PROFIT: {}".format(self.ta.profit))
        return self.ta.profit

    def filter_dates(self, date_dict):
        # TODO - Clean this up and reduce space used. Maybe write dictionary data to a file.
        date_filtered_dict = {}
        if not date_dict:
            print("date_dict is empty")
            return {}
        # sort the dates into ascending order
        date_dict = dict(sorted(date_dict.items()))
        for date in date_dict:
            if self.start_date <= date <= self.end_date:
                date_filtered_dict[date] = date_dict[date]  # Map date to its original data
        return date_filtered_dict

    @staticmethod
    def stock_info_generator(date_dict):
        # TODO - Make sure the dates are being generated in reverse order
        data_up_to_date = {}
        for count, day in enumerate(date_dict):
            data_up_to_date[day] = date_dict[day]
            if count > 100:
                yield data_up_to_date

    """
    1) Given x amount of tickers, get historical data of tickers from alphavantage's API.
    2) Preprocess data by selecting only EMA and price ticker data from start date to end date.
    3) Pass in data to triplecrossover strategy
   """


if __name__ == '__main__':
    historical_test = Backtesting(test_tickers=["IBM"], start_date="2017-12-03", end_date="2020-07-07")
    historical_test.test_algorithm()