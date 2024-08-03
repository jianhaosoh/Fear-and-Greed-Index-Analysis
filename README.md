# Fear and Greed Index Analysis

## Project Motivation
“Be fearful when others are greedy and to be greedy only when others are fearful”. This quote by investing legend Warren Buffett is something that I believe in. The CNN Fear and Greed Index is one of the most well-known indicators of sentiment in the market and one that I personally reference against when making investments decisions. Essentially, buy when the sentiments are fearful, sell when the sentiments are greedy!

However, I am unsure of the exact effect of the index on market prices. While I have observed its influence anecdotally, I lack concrete justification to back up my observations. Furthermore, tracking this index daily can be exhausting and there are many times where I miss out on it entirely. Thus this serves as the motivation of my project.

## Project Aim
In this project, I aim to evaluate the Fear and Greed Index’s accuracy in signalling market reversals and to develop a trading strategy by using it as an indicator. The performance of the strategy will be benchmarked against the “buy and hold” strategy to evaluate its effectiveness. In order to streamline the process of staying updated, a Telegram bot will be created to fetch and alert us of the Fear and Greed Index daily.

## Results and Recommendations
Overall, we can conclude that both the strategy that was explored does have an edge in the markets and the best parameters used for both strategies was able to outperform the simple 'buy and hold' strategy by 65.87% and 54.12% respectively. However, choosing strategy 1 would mean having only 5 trades for the entire backtesting period.

Thus, the recommended strategy to follow will be **Strategy 2**. While the best threshold in strategy 1 offers better returns than the best threshold in strategy 2, the number of trades is very low and average trade duration is very high. This is not ideal for the live markets considering the psychological aspects.

For strategy 2, there is two recommended set of parameters to use depending on one's risk profile. The parameters with an higher risk tolerance outperforms the simple 'buy and hold' strategy by 54.12% while the parameters with an lower risk tolerance outperforms the simple 'buy and hold' strategy by 41.03%.  However, choosing the higher risk tolerance strategy would mean having to endure double the maximum potential drawdown (-54.0% vs -26.0%) for a potential 10% better outperformance returns offered.

Thus, the recommended strategy to follow will be the **lower risk tolerance strategy**. 

Overall, the recommended strategy 2 along with the lower risk tolerance approach has an **total return of 534.74%** over a 13 year period, having an **annualised 14.57% return** and a **max drawdown of -26.0%**. 

Attached below is the visualisation of the backtesting result of Strategy 2, using the lower risk tolerance approach.

![Recommended Strategy Backtest](/finalised_results/results.png)

## Reflection
While the results suggest that this strategy has an edge in the markets, there are some caveats to consider.

- The results suggests that no sell trades should be taken when the market sentiments are fearful and that we should only focus on buys. This makes sense considering that the dataset used covers a decade during which the market was trending upwards. The market crash in 2020 during the Coronavirus pandemic also contributed to the overall profitability as we were able to capture the recovery move. While it is true that markets tend to rise in the long run (over a few decades), short-term movements are unpredictable. Thus, this strategy may not perform well if the markets trend downwards for the next 10 years. But, that is something that no one can predict with certainty. 
- This strategy is one that works well in trending markets. If the market trends sideways during periods of consolidation, the strategy could struggle due to many false signals, leading to losses.
- The recommended strategy and risk tolerance approach have a win rate of 28.12% which is relatively low and can be challenging to manage psychologically in the live markets.
- The results did not take into account of commissions.s

## Overview Of Files
- `analysis.ipynb` is the jupyter notebook where all the analysis was done.
- `strategy_results` folder consists of the backtesting results of all the combination of parameters used for both strategy 1 and 2.
- `finalised_results` folder consists of the selected strategy (strategy 2) backtesting report and transaction records.
- `datasets` folder consists of the fear and greed data that was used in this project.
- `backtester` folder consists of the backtester script used for strategy 1 and strategy 2.
- `alert` folder consists of the script that generates the telegram alert.

## Setting Up the Telegram Alert
#### Creating a Telegram Bot and getting the Bot ID
1. Search for `@BotFather` on telegram
2. Click 'Start'
3. Type `/newbot` and click Send
4. Save the bot token in an `.env` file

#### Getting the Chat ID
1. Search for our created bot and open it 
2. Click start and send a message
3. Open this URL in a browser https://api.telegram.org/bot{our_bot_token}/getUpdates replacing it with your bot token
4. Retrieve the Chat ID from the json file and save it in the same `.env` file

#### Getting the alert
This can be done by automating the process of running the `telegram_alert.py` script which can be done differently depending on our operating system if we choose to run it locally or alternatively, we can also run it on a server.

## Disclaimer
All strategies, opinions, and information presented here are solely for informational purposes and do not constitute investment or trading advice.