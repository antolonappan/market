import yfinance as yf
from datetime import datetime, timedelta,date
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from textblob import TextBlob
from eventregistry import *
import os

class StockPricePredictor:
    def __init__(self, symbol,api=False):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
        self.api = api

    def fetch_historical_data(self, start_date, end_date):
        history = self.stock.history(start=start_date, end=end_date, interval='1d')
        return history[['Open', 'High', 'Close']]

    def fetch_sentiments(self):
        if not self.api:
            news_sentiments = []
            for news in self.stock.news:
                title = news['title']
                combined_text = title 
                blob = TextBlob(combined_text)
                sentiment = blob.sentiment.polarity
                news_sentiments.append(sentiment)

            average_sentiment = sum(news_sentiments) / len(news_sentiments)
        else:
            print("Using Event Registry API")
            er = EventRegistry(apiKey=os.environ['NEWSAPI']) 

            company_name = self.stock.info['longName']
            query = f"{company_name}"

            q = QueryArticlesIter(
                keywords = QueryItems.OR([query]),
                dataType = ["news"])

            articles = []
            for art in q.execQuery(er, sortBy = "socialScore", maxItems = 20):
                articles.append(art['title'])
            news_sentiments = []
            for text in articles:
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                news_sentiments.append(sentiment)

            average_sentiment = sum(news_sentiments) / len(news_sentiments)
        return average_sentiment

    def predict_stock_price_statistics(self, data):
        pre_open = data['Open'].iloc[-1]
        next_high = data['High'].iloc[-1]
        next_close = data['Close'].iloc[-1]
        return pre_open, next_high, next_close

    def predict_stock_price_ml(self, data):
        X = data[['Open', 'High', 'Close']]
        y_pre_open = data['Open'].shift(-1)
        y_next_high = data['High'].shift(-1)
        y_next_close = data['Close'].shift(-1)
        X = X[:-1]
        y_pre_open = y_pre_open[:-1]
        y_next_high = y_next_high[:-1]
        y_next_close = y_next_close[:-1]


        pre_open_model = LinearRegression()
        pre_open_model.fit(X, y_pre_open)


        next_high_model = LinearRegression()
        next_high_model.fit(X, y_next_high)


        next_close_model = LinearRegression()
        next_close_model.fit(X, y_next_close)


        pre_open_prediction = pre_open_model.predict([X.iloc[-1]])
        next_high_prediction = next_high_model.predict([X.iloc[-1]])
        next_close_prediction = next_close_model.predict([X.iloc[-1]])

        return pre_open_prediction[0], next_high_prediction[0], next_close_prediction[0]

    def predict_stock_price_nn(self, data):
        X = data[['Open', 'High', 'Close']]
        y_pre_open = data['Open'].shift(-1)
        y_next_high = data['High'].shift(-1)
        y_next_close = data['Close'].shift(-1)
        X = X[:-1]
        y_pre_open = y_pre_open[:-1]
        y_next_high = y_next_high[:-1]
        y_next_close = y_next_close[:-1]


        pre_open_model = MLPRegressor(random_state=42)
        pre_open_model.fit(X, y_pre_open)


        next_high_model = MLPRegressor(random_state=42)
        next_high_model.fit(X, y_next_high)


        next_close_model = MLPRegressor(random_state=42)
        next_close_model.fit(X, y_next_close)


        pre_open_prediction = pre_open_model.predict([X.iloc[-1]])
        next_high_prediction = next_high_model.predict([X.iloc[-1]])
        next_close_prediction = next_close_model.predict([X.iloc[-1]])

        return pre_open_prediction[0], next_high_prediction[0], next_close_prediction[0]


       
def predict_stock_price(symbol, method, include_sentiments=False, include_one_month_data=False, api=False):
    predictor = StockPricePredictor(symbol,api=api)


    end_date = date.today().strftime('%Y-%m-%d')
    if include_one_month_data:
        start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    else:
        start_date = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = predictor.fetch_historical_data(start_date, end_date)


    if include_sentiments:
        average_sentiment = predictor.fetch_sentiments()
        data['Sentiment'] = average_sentiment


    if method == 'statistics':
        pre_open, next_high, next_close = predictor.predict_stock_price_statistics(data)
    elif method == 'machine_learning':
        pre_open, next_high, next_close = predictor.predict_stock_price_ml(data)
    elif method == 'neural_network':
        pre_open, next_high, next_close = predictor.predict_stock_price_nn(data)
    else:
        raise ValueError("Invalid prediction method. Available options: 'statistics', 'machine_learning', 'neural_network'")

    
    print("Stock Symbol:", symbol)
    print("Prediction Method:", method)
    print("Include Sentiments:", include_sentiments)
    print("Include One Month Data:", include_one_month_data)
    print()
    print("Pre-Open Price Prediction:", pre_open)
    print("Next Day's Highest Price Prediction:", next_high)
    print("Next Closing Price Prediction:", next_close)