from keys import AV_API_KEY, NEWS_API_KEY, VIRTUAL_TWILIO_NUMBER,VERIFIED_NUMBER, TWILIO_SID, TWILIO_AUTH_TOKEN
import requests
from twilio.rest import Client

STOCK_NAME = "SPOT"
COMPANY_NAME = "Spotify Technology SA"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "output_size": "compact",
    "apikey": AV_API_KEY
}

news_parameters = {
    "q": COMPANY_NAME,
    "apikey": NEWS_API_KEY,
}

response = requests.get(STOCK_ENDPOINT,params=stock_parameters)
response.raise_for_status()
stock_data=response.json()["Time Series (Daily)"]
stock_data_list = [value for (key, value) in stock_data.items()]

#Get  yesterday's closing stock price
yesterday_data =stock_data_list[0]
yesterday_close = yesterday_data['4. close']

#Get the day before yesterday's closing stock price
before_yesterday_data = stock_data_list[1]
before_yesterday_close = before_yesterday_data['4. close']

#Find the positive difference between yesterday and day before yesterday
difference = float(yesterday_close) - float(before_yesterday_close)

up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

#Work out the percentage difference in price between closing price yesterday and closing price the day before 
diff_percent = round((difference / float(yesterday_close)) * 100)

if diff_percent >= 5:
    news_response = requests.get(NEWS_ENDPOINT,params=news_parameters)
    response.raise_for_status()
    articles = news_response.json()['articles']
    article_slice = articles[:3]
    
    #Create a new list of the first 3 article's headline and description using list comprehension.
    formatted_articles = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in article_slice]
    
   #Send each article as a separate message via Twilio.
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=VIRTUAL_TWILIO_NUMBER,
            to=VERIFIED_NUMBER
        )

