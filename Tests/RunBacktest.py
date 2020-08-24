from Tests.Backtesting import Backtesting


def PrintStockAlgoMetrics(test_object, iteration_count, algo_cash, algo_trades, avg_stock_profit_sum):
    algo_cash += test_object.cash
    avg_algo_cash = algo_cash / iteration_count
    algo_trades += test_object.trades_count
    avg_stock_profit_sum += test_object.stock_profit_percent_sum
    print("Stock algorithm info for all iterations so far:")
    # metrics for stock algo
    print("Algorithm trades executed for {} iterations: {}".format(iteration_count, algo_trades))
    print("Total algorithm cash average for {} iterations: {}".format(iteration_count, avg_algo_cash))
    avg_pct = 0
    if algo_trades != 0:
        avg_pct = avg_stock_profit_sum / algo_trades
    print("Average algorithm profit based on ${} investments for {} iterations: {}"
          .format(test_object.invest_amount, iteration_count, avg_pct))
    print("Commencing next iteration...")
    print("_" * 150)
    print("\n")


def PrintBuyHoldMetrics(test_object, iteration_count, bh_cash, bh_trades, bh_avg_stock_profit_sum):
    bh_cash += test_object.buy_hold_money
    bh_trades += test_object.buy_hold_trades_count
    bh_avg_stock_profit_sum += test_object.buy_hold_profit_percent_sum
    avg_bh_cash = bh_cash / iteration_count
    print("Buy and hold info for all iterations so far:")
    # metrics for buy and hold
    print("Buy and hold executed {} trades in {} iterations".format(bh_trades, iteration_count))
    print("Total buy and hold cash average for {} iterations: {}".format(iteration_count, avg_bh_cash))
    avg_bh_pct = 0
    if bh_trades != 0:
        avg_bh_pct = bh_avg_stock_profit_sum / bh_trades
    print("Average buy and hold profit based on ${} investments for {} iterations: {}"
          .format(test_object.invest_amount, iteration_count, avg_bh_pct))
    print("_" * 150)



def RunTest(start_date="2007-01-01", end_date="2015-01-01", iterations=2):
    NYSE = "../Data/NYSE.txt"
    SPY = "../Data/SPY.txt"
    PENNY = "../Data/PENNY.txt"  # Data is biased for penny stock info.
    USA = "../Data/USA.txt"
    API_KEY = "MA6YR6D5TVXK1W67"

    total_algo_cash = 0
    total_avg_stock_profit_sum = 0
    total_algo_trades = 0

    total_bh_cash = 0
    total_avg_bh_profit_sum = 0
    total_bh_trades = 0

    for i in range(1, iterations + 1):
        historical_test = Backtesting(start_date=start_date, end_date=end_date, api_key=API_KEY)
        tickers = historical_test.get_random_ticks(file=SPY, amount=1)
        tickers.append("HSY")
        print(tickers)
        historical_test.test_algorithm(tickers)
        print()
        PrintBuyHoldMetrics(historical_test, i,
                            bh_cash=total_bh_cash,
                            bh_trades=total_algo_trades,
                            bh_avg_stock_profit_sum=total_avg_bh_profit_sum)
        PrintStockAlgoMetrics(historical_test, i,
                              algo_cash=total_algo_cash,
                              algo_trades=total_algo_trades,
                              avg_stock_profit_sum=total_avg_stock_profit_sum)

    print("Backtest complete.")


if __name__ == '__main__':
    RunTest()