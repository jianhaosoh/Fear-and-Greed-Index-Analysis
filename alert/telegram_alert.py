import requests 
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv('../.env')

BOT_ID = os.getenv('BOT_ID')
CHAT_ID = os.getenv('CHAT_ID')

url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/"
headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)
data = response.json()['fear_and_greed']

timestamp = pd.to_datetime(data['timestamp']).date()
today_score = round(data['score'], 2)
previous_day_score = round(data['previous_close'], 2)
previous_week_score = round(data['previous_1_week'], 2)
previous_month_score = round(data['previous_1_month'], 2)
previous_year_score = round(data['previous_1_year'], 2)

def get_rating(score):
    if score < 25:
        return "Extreme Fear"
    elif score < 50:
        return "Fear"
    elif score < 55:
        return "Neutral"
    elif score < 75:
        return "Greed"
    else:
        return "Extreme Greed"
    
today_rating = get_rating(today_score)
previous_day_rating = get_rating(previous_day_score)
previous_week_rating = get_rating(previous_week_score)
previous_month_rating = get_rating(previous_month_score)
previous_year_rating = get_rating(previous_year_score)

message = f"Fear and Greed Index:\n Date: {timestamp}\n Today's Score: {today_score} ({today_rating}) \n Previous Day's Score: {previous_day_score} ({previous_day_rating}) \n Previous Week's Score: {previous_week_score} ({previous_week_rating}) \n Previous Month's Score: {previous_month_score} ({previous_month_rating}) \n Previous Year's Score: {previous_year_score} ({previous_year_rating})"

url = f"https://api.telegram.org/bot{BOT_ID}/sendMessage?chat_id={CHAT_ID}&text={message}"
requests.get(url)