import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Trade:
    def __init__(self, open_date, open_price, position, shares, take_profit, stop_loss, data, equity_balance):
        self.open_date = open_date
        self.open_price = round(open_price, 2)
        self.position = position
        self.shares = shares
        self.returns = 0
        self.pct_returns = 0
        self.close_date = None
        self.close_price = None
        self.duration = None
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.max_drawdown = 0
        self.pct_max_drawdown = 0
        self.data = data
        self.equity_balance = equity_balance
        self.open = True

    def close_trade(self, close_date, close_price):
        self.close_date = close_date
        self.close_price = round(close_price, 2)
        if self.position == 'Buy':
            self.returns = round((self.close_price - self.open_price) * self.shares, 2)
            self.max_drawdown = round((self.data.loc[self.open_date:self.close_date]['SPY Low Price'].min() - self.open_price) * self.shares, 2)
            if self.returns < 0 and self.max_drawdown < self.returns:
                self.max_drawdown = self.returns
        else:
            self.returns = round((self.open_price - self.close_price) * self.shares, 2)
            self.max_drawdown = round((self.open_price - self.data.loc[self.open_date:self.close_date]['SPY High Price'].max()) * self.shares, 2)
            if self.returns < 0 and self.max_drawdown < self.returns:
                self.max_drawdown = self.returns
        self.pct_max_drawdown = round((self.max_drawdown / self.equity_balance) * 100, 2)
        self.pct_returns = round((self.returns / self.equity_balance) * 100, 2)
        self.duration = (self.close_date - self.open_date).days
        self.open = False
        return self

    def __repr__(self):
        return (f"Open Date: {self.open_date} \n"
                f"Open Price: {self.open_price} \n"
                f"Position: {self.position} \n"
                f"Share Size: {self.shares} \n"
                f"Returns: {self.returns} \n"
                f"Returns (%): {self.pct_returns}% \n"
                f"Close Date: {self.close_date} \n"
                f"Close Price: {self.close_price} \n"
                f"Duration: {self.duration} days \n"
                f"Max Drawdown: {self.max_drawdown} \n"
                f"Max Drawdown (%): {self.pct_max_drawdown}% \n")
    
class Backtest:
    def __init__(self, data, initial_balance, buy_threshold, sell_threshold, risk_reward_ratio=3, loss_buffer=3, risk_per_trade=1):
        self.data = data
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.risk_reward_ratio = risk_reward_ratio 
        self.loss_buffer = loss_buffer # percentage buffer we give for the stop loss from open price
        self.risk_per_trade = risk_per_trade 
        self.signals = self.generate_signal(buy_threshold, sell_threshold)
        self.report = {}

    def buy_and_hold_return(self):
        shares = self.initial_balance // self.data.iloc[0]['SPY Opening Price']
        trade = Trade(self.data.index[0], self.data.iloc[0]['SPY Opening Price'], 'Buy', shares, None, None, self.data, self.initial_balance)
        returns = trade.close_trade(self.data.index[-1], self.data.iloc[-1]['SPY Closing Price']).returns
        return returns
    
    def generate_signal(self, buy_threshold, sell_threshold):
        open_buy = False
        buy_tp = None
        buy_sl = None
        open_sell = False
        sell_tp = None
        sell_sl = None
        signals = []

        for index in range(0, len(self.data)):
            # Check if any open buy positions hit take profit or stop loss, allow buy signal if so 
            if open_buy and (self.data.iloc[index]['SPY High Price'] >= buy_tp or self.data.iloc[index]['SPY Low Price'] <= buy_sl):
                open_buy = False
                buy_tp = None
                buy_sl = None
            # Check if any open sell positions hit take profit or stop loss, allow sell signal if so
            if open_sell and (self.data.iloc[index]['SPY Low Price'] <= sell_tp or self.data.iloc[index]['SPY High Price'] >= sell_sl):
                open_sell = False
                sell_tp = None
                sell_sl = None
            # Buy criteria hit, no existing buy position, set buy signal
            if self.data.iloc[index]['Fear and Greed Index'] <= buy_threshold and not open_buy:
                open_buy = True
                buy_sl = self.data.iloc[index]['SPY Opening Price'] * (1 - (self.loss_buffer * 0.01))
                buy_tp = self.data.iloc[index]['SPY Opening Price'] * (1 + (self.loss_buffer * 0.01 * self.risk_reward_ratio))
                signals.append('Buy')
            # Sell criteria hit, no existing sell position, set sell signal
            elif self.data.iloc[index]['Fear and Greed Index'] >= sell_threshold and not open_sell:
                open_sell = True
                sell_sl = self.data.iloc[index]['SPY Opening Price'] * (1 + (self.loss_buffer * 0.01))
                sell_tp = self.data.iloc[index]['SPY Opening Price'] * (1 - (self.loss_buffer * 0.01 * self.risk_reward_ratio))
                signals.append('Sell')
            # No new criteria hit or there is existing positions, set hold signal
            else:
                signals.append('Hold')
            # Check if newly open buy position hit take profit or stop loss and on the same day, allow buy signal if so
            if open_buy and (self.data.iloc[index]['SPY High Price'] >= buy_tp or self.data.iloc[index]['SPY Low Price'] <= buy_sl):
                open_buy = False
                buy_tp = None
                buy_sl = None
            # Check if newly open sell position hit take profit or stop loss and on the same day, allow sell signal if so
            if open_sell and (self.data.iloc[index]['SPY Low Price'] <= sell_tp or self.data.iloc[index]['SPY High Price'] >= sell_sl):
                open_sell = False
                sell_tp = None
                sell_sl = None
        return signals

    def backtest(self):
        for index in range(0, len(self.data)):
            signal = self.signals[index]
            open_price = self.data.iloc[index]['SPY Opening Price']
            close_price = self.data.iloc[index]['SPY Closing Price']
            high_price = self.data.iloc[index]['SPY High Price']
            low_price = self.data.iloc[index]['SPY Low Price']
            date = self.data.iloc[index].name

            # Handle last day of data, close all open positions
            if index == len(self.data) - 1:
                if self.trades:
                    for trade in self.trades:
                        if trade.open:
                            trade.close_trade(date, close_price)
                            self.balance += trade.returns
                break
            
            # Handle rest of the days,
            # Check closing positions first
            if self.signals:
                for trade in self.trades:
                    if trade.open:
                        if trade.position == 'Buy':
                            if high_price >= trade.take_profit:
                                trade.close_trade(date, trade.take_profit)
                                self.balance += trade.returns
                            elif low_price <= trade.stop_loss:
                                trade.close_trade(date, trade.stop_loss)
                                self.balance += trade.returns
                            else:
                                continue
                        else: # for sell position
                            if low_price <= trade.take_profit:
                                trade.close_trade(date, trade.take_profit)
                                self.balance += trade.returns
                            elif high_price >= trade.stop_loss:
                                trade.close_trade(date, trade.stop_loss)
                                self.balance += trade.returns
                            else:
                                continue
             # Check any positions to open and close on the same day if necessary
             # Check if we can open a buy position
            if signal == 'Buy':
                risk_amount = self.risk_per_trade * 0.01 * self.balance 
                buy_tp = open_price * (1 + (self.loss_buffer * 0.01 * self.risk_reward_ratio))
                buy_sl = open_price * (1 - (self.loss_buffer * 0.01))
                shares = risk_amount // (open_price - buy_sl) # when I lose, I lose the entire risk amount
                self.trades.append(Trade(date, open_price, 'Buy', shares, buy_tp, buy_sl, self.data, self.balance))
                # Check if we can close on the same day
                if high_price >= buy_tp:
                    self.trades[-1].close_trade(date, buy_tp)
                    self.balance += self.trades[-1].returns
                elif low_price <= buy_sl:
                    self.trades[-1].close_trade(date, buy_sl)
                    self.balance += self.trades[-1].returns
            # Check if we can open a sell position
            elif signal == 'Sell':
                risk_amount = self.risk_per_trade * 0.01 * self.balance 
                sell_tp = open_price * (1 - (self.loss_buffer * 0.01 * self.risk_reward_ratio))
                sell_sl = open_price * (1 + (self.loss_buffer * 0.01))
                shares = risk_amount // (sell_sl - open_price)
                self.trades.append(Trade(date, open_price, 'Sell', shares, sell_tp, sell_sl, self.data, self.balance))
                # Check if we can close on the same day
                if low_price <= sell_tp:
                    self.trades[-1].close_trade(date, sell_tp)
                    self.balance += self.trades[-1].returns
                elif high_price >= sell_sl:
                    self.trades[-1].close_trade(date, sell_sl)
                    self.balance += self.trades[-1].returns
            else:
                continue
        self.report = self.generate_report()
        return self
    
    def plot(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True, height_ratios=[2, 1, 1])

        ax1.plot(self.data.index, self.data['SPY Opening Price'], label='SPY Opening Price', color='blue')
        buy_signals = [trade for trade in self.trades if trade.position == 'Buy']
        sell_signals = [trade for trade in self.trades if trade.position == 'Sell']
        ax1.scatter([trade.open_date for trade in buy_signals], [trade.open_price for trade in buy_signals], 
                    label='Buy', color='green', marker='^', s=70, zorder=5)
        ax1.scatter([trade.open_date for trade in sell_signals], [trade.open_price for trade in sell_signals], 
                    label='Sell', color='red', marker='v', s=70, zorder=5)
        ax1.set_ylabel('SPY Opening Price')
        ax1.legend(loc='upper left')

        ax2.plot(self.data.index, self.data['Fear and Greed Index'], label='Fear and Greed Index', color='orange')
        ax2.set_ylabel('Fear and Greed Index')
        ax2.legend(loc='upper left')

        transaction_records = self.transaction_records()
        initial_record = pd.DataFrame({
            'Close Date': [self.data.index.min()],
            'Equity Balance': [self.initial_balance]
        })
        last_record = pd.DataFrame({
            'Close Date': [self.data.index.max()],
            'Equity Balance': [transaction_records['Equity Balance'].iloc[-1]]
        })
        full_records = pd.concat([initial_record, transaction_records[['Close Date', 'Equity Balance']]]).reset_index(drop=True)
        full_records = pd.concat([full_records, last_record]).reset_index(drop=True)
        ax3.plot(full_records['Close Date'], full_records['Equity Balance'], label='Equity Balance', color='purple')
        ax3.set_ylabel('Equity Balance')
        ax3.set_xlabel('Date')
        ax3.legend(loc='upper left')

        fig.suptitle('Backtest of Trading Strategy', size=12, weight='bold', y=1)
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.1)

        plt.show()

    def transaction_records(self):
        records = []
        for trade in self.trades:
            if trade.close_date:
                records.append({
                    'Open Date': trade.open_date,
                    'Open Price': trade.open_price,
                    'Position': trade.position,
                    'Shares': trade.shares,
                    'Close Date': trade.close_date,
                    'Close Price': trade.close_price,
                    'Returns': trade.returns,
                    'Returns (%)': trade.pct_returns,
                    'Duration': trade.duration,
                    'Max Drawdown': trade.max_drawdown,
                    'Max Drawdown (%)': trade.pct_max_drawdown,
                    'Equity Balance': self.initial_balance + trade.returns if trade == self.trades[0] else records[-1]['Equity Balance'] + trade.returns
                })
            else:
                records.append({
                    'Open Date': trade.open_date,
                    'Open Price': trade.open_price,
                    'Position': trade.position,
                    'Shares': trade.shares,
                    'Close Date': None,
                    'Close Price': None,
                    'Returns': None,
                    'Returns (%)': None,
                    'Duration': None,
                    'Max Drawdown': None,
                    'Max Drawdown (%)': None,
                    'Equity Balance': None
                })
        return pd.DataFrame(records)
    
    def generate_report(self):
        total_trades = len(self.trades)
        durations = [trade.duration for trade in self.trades if trade.duration is not None]
        avg_duration = np.mean(durations) if durations else 0
        winners = [trade for trade in self.trades if trade.returns > 0]
        losers = [trade for trade in self.trades if trade.returns < 0]
        buy_and_hold_returns = self.buy_and_hold_return()
        average_drawdown = np.mean([trade.max_drawdown for trade in self.trades])
        pct_average_drawdown = np.mean([trade.pct_max_drawdown for trade in self.trades])
        max_loss_streak, current_loss_streak = 0, 0
        for trade in self.trades:
            if trade.returns < 0:
                current_loss_streak += 1
                max_loss_streak = max(max_loss_streak, current_loss_streak)
            else:
                current_loss_streak = 0

        report = {
            'Start Date': self.data.index.min(),
            'End Date': self.data.index.max(),
            'Backtest Duration': (self.data.index.max() - self.data.index.min()).days,
            'Total Trades': len(self.trades),
            'Total Buys': len([trade for trade in self.trades if trade.position == 'Buy']),
            'Total Sells': len([trade for trade in self.trades if trade.position == 'Sell']),
            'Initial Balance': self.initial_balance,
            'Final Balance': round(self.balance, 2),
            'Total Returns': round(self.balance - self.initial_balance, 2),
            'Total Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100, 2),
            'Annualised Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100 / (self.data.index.max().year - self.data.index.min().year), 2),
            'Average Returns': round((self.balance - self.initial_balance) / total_trades, 2),
            'Average Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100 / total_trades, 2),
            'Average Trade Duration': int(avg_duration),
            'Number of Winners': len(winners),
            'Number of Long Winners': len([trade for trade in winners if trade.position == 'Buy']),
            'Number of Short Winners': len([trade for trade in winners if trade.position == 'Sell']),
            'Average Winner Returns': round(np.mean([trade.returns for trade in winners]), 2) if winners else 0,
            'Average Winner Returns (%)': round(np.mean([trade.pct_returns for trade in winners]), 2) if winners else 0,
            'Number of Losers': len(losers),
            'Number of Long Losers': len([trade for trade in losers if trade.position == 'Buy']),
            'Number of Short Losers': len([trade for trade in losers if trade.position == 'Sell']),
            'Average Loser Returns': round(np.mean([trade.returns for trade in losers]), 2) if losers else 0,
            'Average Loser Returns (%)': round(np.mean([trade.pct_returns for trade in losers]), 2) if losers else 0,
            'Win Rate (%)': round((len(winners) / total_trades) * 100, 2),
            'Average Drawdown': round(average_drawdown, 2),
            'Average Drawdown (%)': round(pct_average_drawdown, 2),
            'Max Loss Streak': max_loss_streak,
            'Buy and Hold Returns': round(buy_and_hold_returns, 2),
            'Buy and Hold Returns (%)': round(((buy_and_hold_returns - self.initial_balance) / self.initial_balance) * 100, 2),
            'Annualised Buy and Hold Returns (%)': round(((buy_and_hold_returns - self.initial_balance) / self.initial_balance) * 100 / (self.data.index.max().year - self.data.index.min().year), 2),
            'Performance vs Buy and Hold (%)': round(((self.balance - buy_and_hold_returns) / buy_and_hold_returns) * 100, 2)
        }
        return report
    
    def backtest_report(self):
        report = self.generate_report()
        report_str = (
            "Backtest Report \n"
            "----------------------------------------------- \n"
            f"Start Date: {report['Start Date']} \n"
            f"End Date: {report['End Date']} \n"
            f"Backtest Duration: {report['Backtest Duration']} days \n"
            f"Total Trades: {report['Total Trades']} \n"
            f"Total Buys: {report['Total Buys']} \n"
            f"Total Sells: {report['Total Sells']} \n"
            f"Initial Balance: {report['Initial Balance']} \n"
            f"Final Balance: {report['Final Balance']} \n"
            f"Total Returns: {report['Total Returns']} \n"
            f"Total Returns (%): {report['Total Returns (%)']}% \n"
            f"Annualised Returns (%): {report['Annualised Returns (%)']}% \n"
            f"Average Returns: {report['Average Returns']} \n"
            f"Average Returns (%): {report['Average Returns (%)']}% \n"
            f"Average Trade Duration: {report['Average Trade Duration']} days \n"
            f"Number of Winners: {report['Number of Winners']} \n"
            f"Number of Long Winners: {report['Number of Long Winners']} \n"
            f"Number of Short Winners: {report['Number of Short Winners']} \n"
            f"Average Winner Returns: {report['Average Winner Returns']} \n"
            f"Average Winner Returns (%): {report['Average Winner Returns (%)']}% \n"
            f"Number of Losers: {report['Number of Losers']} \n"
            f"Number of Long Losers: {report['Number of Long Losers']} \n"
            f"Number of Short Losers: {report['Number of Short Losers']} \n"
            f"Average Loser Returns: {report['Average Loser Returns']} \n"
            f"Average Loser Returns (%): {report['Average Loser Returns (%)']}% \n"
            f"Win Rate (%): {report['Win Rate (%)']}% \n"
            f"Average Drawdown: {report['Average Drawdown']} \n"
            f"Average Drawdown (%): {report['Average Drawdown (%)']}% \n"
            f"Max Loss Streak: {report['Max Loss Streak']} \n"
            f"Buy and Hold Returns: {report['Buy and Hold Returns']} \n"
            f"Buy and Hold Returns (%): {report['Buy and Hold Returns (%)']}% \n"
            f"Annualised Buy and Hold Returns (%): {report['Annualised Buy and Hold Returns (%)']}% \n"
            f"Performance vs Buy and Hold (%): {report['Performance vs Buy and Hold (%)']}% \n"
        )
        return report_str
    
    def __repr__(self):
        return self.backtest_report()