import requests
from twilio.rest import Client
import os

STOCK = "CHOOSE_STOCK_CODE"
COMPANY_NAME = "CHOOSE_COMPANY_NAME"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
COMPANY_NEWS_API = os.environ.get("COMPANY_NEWS_API")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")


stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}

news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": COMPANY_NEWS_API,
}

stock_response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
stock_data_list = [value for (key,value) in stock_data.items()]
yesterday = float(stock_data_list[0]["4. close"])
day_before = float(stock_data_list[1]["4. close"])

price_difference = (yesterday - day_before)
up_down = None
if price_difference > 5:
    up_down = "⬆️"
else:
    up_down = "⬇️"

percentage_change = round((price_difference / yesterday) * 100)
# print(percentage_change)
if abs(percentage_change) >= 5:
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news = news_response.json()
    news_articles = news["articles"]
    news_list = news_articles[:3]

    formatted_news = [f"{STOCK} {up_down} {percentage_change}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in news_list]

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for news in formatted_news:
        message = client.messages.create(
            from_=os.environ.get("TWILIO_NUM"),
            body=news,
            to=os.environ.get("MY_NUM")
        )
        print(message.status)

