from Tests.Backtesting import Backtesting


def PrintMetrics(test_object, iteration_count):
    avg_algo_cash = 0
    total_algo_cash = 0
    total_avg_stock_profit_sum = 0
    total_algo_trades = 0
    total_buy_hold_profit = 0
    total_buy_hold_pct = 0
    total_buy_hold_trades = 0
    total_algo_cash += test_object.cash
    avg_algo_cash = total_algo_cash / iteration_count
    total_algo_trades += test_object.trades_count
    total_avg_stock_profit_sum += test_object.stock_profit_percent_sum
    print("Info for all iterations so far: ".format(iteration_count))
    # metrics for buy and hold


    # metrics for stock algo
    print("Algorithm trades executed for {} iterations: {}".format(iteration_count, total_algo_trades))
    print("Total algorithm cash average for {} iterations: {}".format(iteration_count, avg_algo_cash))
    avg_pct = 0
    if total_algo_trades != 0:
        avg_pct = total_avg_stock_profit_sum / total_algo_trades
    print("Average algorithm profit based on ${} investments for {} iterations: {}"
          .format(test_object.invest_amount, iteration_count, avg_pct))
    print("Commencing next iteration...")
    print("_" * 150)


def RunTest(start_date="2007-01-01", end_date="2015-01-01", iterations=10):
    NYSE = "../Data/NYSE.txt"
    SPY = "../Data/SPY.txt"
    PENNY = "../Data/PENNY.txt"  # Data is biased for penny stock info.
    USA = "../Data/USA.txt"
    API_KEY = "MA6YR6D5TVXK1W67"

    for i in range(1, iterations + 1):
        historical_test = Backtesting(start_date=start_date, end_date=end_date, api_key=API_KEY)
        tickers = historical_test.get_random_ticks(file=SPY, amount=1)
        tickers.append("HSY")
        print(tickers)
        historical_test.test_algorithm(tickers)
        PrintMetrics(historical_test, i)
    print("Backtest complete.")


if __name__ == '__main__':
    RunTest()