import numpy as np
import pandas as pd
import plotly.graph_objects as go


class Trade:
    def __init__(self, open_date, open_price, position, shares):
        self.open_date = open_date
        self.open_price = open_price
        self.position = position
        self.shares = shares
        self.returns = 0
        self.pct_returns = 0
        self.close_date = None
        self.close_price = None
        self.duration = None

    def close_trade(self, close_date, close_price):
        self.close_date = close_date
        self.close_price = close_price
        if self.position == 'Buy':
            self.returns = (self.close_price - self.open_price) * self.shares
        else:
            self.returns = (self.open_price - self.close_price) * self.shares
        self.pct_returns = (self.returns / (self.open_price * self.shares)) * 100
        self.duration = (self.close_date - self.open_date).days
        return self

    def __repr__(self):
        return (f"Open Date: {self.open_date} \n"
                f"Open Price: {self.open_price} \n"
                f"Position: {self.position} \n"
                f"Share Size: {self.shares} \n"
                f"Returns: {self.returns} \n"
                f"% Returns: {self.pct_returns} \n"
                f"Close Date: {self.close_date} \n"
                f"Close Price: {self.close_price} \n"
                f"Duration: {self.duration} days")
    
class Backtest:
    def __init__(self, data, initial_balance, buy_threshold, sell_threshold):
        self.data = data
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.signals = self.generate_signal(buy_threshold, sell_threshold)
        self.report = {}

    def buy_and_hold_return(self):
        shares = self.initial_balance // self.data.iloc[0]['SPY Opening Price']
        trade = Trade(self.data.index[0], self.data.iloc[0]['SPY Opening Price'], 'Buy', shares)
        returns = trade.close_trade(self.data.index[-1], self.data.iloc[-1]['SPY Opening Price']).returns
        return returns
    
    def generate_signal(self, buy_threshold, sell_threshold):
        previous_signal = None
        current_signal = None
        signals = []

        for index in range(0, len(self.data)):
            if previous_signal != 'Buy' and self.data.iloc[index]['Fear and Greed Index'] <= buy_threshold:
                current_signal = 'Buy'
                previous_signal = current_signal
            elif previous_signal != 'Sell' and self.data.iloc[index]['Fear and Greed Index'] >= sell_threshold:
                current_signal = 'Sell'
                previous_signal = current_signal
            else:
                current_signal = 'Hold'
            signals.append(current_signal)
        return signals

    def backtest(self):
        for index in range(0, len(self.data)):
            signal = self.signals[index]
            price = self.data.iloc[index]['SPY Opening Price']
            date = self.data.iloc[index].name

            if index == len(self.data) - 1:
                if self.trades:
                    self.trades[-1].close_trade(date, price)
                    self.balance += self.trades[-1].returns
                break
            
            if signal == 'Buy':
                if self.trades: # Close existing trade if there is one and open new trade
                    self.trades[-1].close_trade(date, price)
                    self.balance += self.trades[-1].returns
                    risk = 1 * self.balance # Risk entire balance
                    shares = risk // price
                    self.trades.append(Trade(date, price, 'Buy', shares))
                else: # If there is no existing trade, just need to open new trade
                    risk = 1 * self.balance
                    shares = risk // price
                    self.trades.append(Trade(date, price, 'Buy', shares))
            elif signal == 'Sell': # Same logic as Buy, just reverse the position
                if self.trades:
                    self.trades[-1].close_trade(date, price)
                    self.balance += self.trades[-1].returns
                    risk = 1 * self.balance  # Risk entire balance
                    shares = risk // price
                    self.trades.append(Trade(date, price, 'Sell', shares))
                else: 
                    risk = 0.1 * self.balance
                    shares = risk // price
                    self.trades.append(Trade(date, price, 'Sell', shares))
            else:
                continue
        self.report = self.generate_report()
        return self
    
    def plot(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['SPY Opening Price'],
            mode='lines',
            name='SPY Opening Price',
            line=dict(color='blue')
        ))
        buy_signals = [trade for trade in self.trades if trade.position == 'Buy']
        sell_signals = [trade for trade in self.trades if trade.position == 'Sell']

        fig.add_trace(go.Scatter(
            x=[trade.open_date for trade in buy_signals],
            y=[trade.open_price for trade in buy_signals],
            mode='markers',
            name='Buy',
            marker=dict(symbol='triangle-up', size=10, color='green')
        ))

        fig.add_trace(go.Scatter(
            x=[trade.open_date for trade in sell_signals],
            y=[trade.open_price for trade in sell_signals],
            mode='markers',
            name='Sell',
            marker=dict(symbol='triangle-down', size=10, color='red')
        ))

        fig.update_layout(
            title={
                'text': "Backtest of Trading Strategy",
                'y':0.95,  
                'x':0.5,  
                'font': {
                    'size': 18,
                }
            },
            xaxis_title='Date',
            yaxis_title='SPY Opening Price',
            height=500,
            width=1150,
            legend=dict(orientation='h', x=0.5, xanchor='center', y=1.15),
            template='plotly_white'
        )

        fig.show()
    
    def generate_report(self):
        total_trades = len(self.trades)
        durations = [trade.duration for trade in self.trades if trade.duration is not None]
        avg_duration = np.mean(durations) if durations else 0
        winners = [trade for trade in self.trades if trade.returns > 0]
        losers = [trade for trade in self.trades if trade.returns < 0]
        buy_and_hold_returns = self.buy_and_hold_return()

        report = {
            'Initial Balance': self.initial_balance,
            'Final Balance': round(self.balance, 2),
            'Total Returns': round(self.balance - self.initial_balance, 2),
            'Total Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100, 2),
            'Annualised Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100 / (self.data.index.max().year - self.data.index.min().year), 2),
            'Average Returns': round((self.balance - self.initial_balance) / total_trades, 2),
            'Average Returns (%)': round(((self.balance - self.initial_balance) / self.initial_balance) * 100 / total_trades, 2),
            'Average Trade Duration': int(avg_duration),
            'Number of Winners': len(winners),
            'Average Winner Returns': round(np.mean([trade.returns for trade in winners]), 2) if winners else 0,
            'Average Winner Returns (%)': round(np.mean([trade.pct_returns for trade in winners]), 2) if winners else 0,
            'Number of Losers': len(losers),
            'Average Loser Returns': round(np.mean([trade.returns for trade in losers]), 2) if losers else 0,
            'Average Loser Returns (%)': round(np.mean([trade.pct_returns for trade in losers]), 2) if losers else 0,
            'Win Rate (%)': round((len(winners) / total_trades) * 100, 2),
            'Buy and Hold Returns': round(buy_and_hold_returns, 2),
            'Buy and Hold Returns (%)': round(((buy_and_hold_returns - self.initial_balance) / self.initial_balance) * 100, 2),
            'Annualised Buy and Hold Returns (%)': round(((buy_and_hold_returns - self.initial_balance) / self.initial_balance) * 100 / (self.data.index.max().year - self.data.index.min().year), 2),
            'Performance vs Buy and Hold (%)': round(((self.balance - buy_and_hold_returns) / buy_and_hold_returns) * 100, 2),
            'Total Trades': len(self.trades)
        }
        return report
    
    def backtest_report(self):
        report = self.generate_report()
        report_str = (
            "Backtest Report \n"
            "------------------------------------- \n"
            f"Initial Balance: {report['Initial Balance']} \n"
            f"Final Balance: {report['Final Balance']} \n"
            f"Total Returns: {report['Total Returns']} \n"
            f"Total Returns (%): {report['Total Returns (%)']}% \n"
            f"Annualised Returns (%): {report['Annualised Returns (%)']}% \n"
            f"Average Returns: {report['Average Returns']} \n"
            f"Average Returns (%): {report['Average Returns (%)']}% \n"
            f"Average Trade Duration: {report['Average Trade Duration']} days \n"
            f"Number of Winners: {report['Number of Winners']} \n"
            f"Average Winner Returns: {report['Average Winner Returns']} \n"
            f"Average Winner Returns (%): {report['Average Winner Returns (%)']}% \n"
            f"Number of Losers: {report['Number of Losers']} \n"
            f"Average Loser Returns: {report['Average Loser Returns']} \n"
            f"Average Loser Returns (%): {report['Average Loser Returns (%)']}% \n"
            f"Win Rate (%): {report['Win Rate (%)']}% \n"
            f"Buy and Hold Returns: {report['Buy and Hold Returns']} \n"
            f"Buy and Hold Returns (%): {report['Buy and Hold Returns (%)']}% \n"
            f"Annualised Buy and Hold Returns (%): {report['Annualised Buy and Hold Returns (%)']}% \n"
            f"Performance vs Buy and Hold (%): {report['Performance vs Buy and Hold (%)']}% \n"
            f"Total Trades: {report['Total Trades']} \n"
        )
        return report_str
    
    def __repr__(self):
        return self.backtest_report()