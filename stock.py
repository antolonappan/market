
import yfinance as yf
import sqlite3
import datetime
from config import DATABASE_CONFIG  # You should have a config.py file with your database configurations

class StockDB:
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.connect_to_database()

    def connect_to_database(self):
        try:
            # Connect to the database
            # SQLite will create the database file if it doesn't exist
            self.db_connection = sqlite3.connect(DATABASE_CONFIG['database'])
            self.db_cursor = self.db_connection.cursor()

            # Create the tables if they do not exist
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (username TEXT PRIMARY KEY, password_hash TEXT)''')
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS stocks
                          (symbol TEXT, quantity INTEGER, purchase_time TIMESTAMP, purchase_price REAL)''')

            # Check if user exists, if not, create a new user
            stored_password_hash = self.db_cursor.execute("SELECT password_hash FROM users WHERE username = ?", (DATABASE_CONFIG['username'],)).fetchone()
            if stored_password_hash is None:
                self.db_cursor.execute("INSERT INTO users VALUES (?, ?)",
                                       (DATABASE_CONFIG['username'], self.hash_password(DATABASE_CONFIG['password'])))
                self.db_connection.commit()
            elif stored_password_hash[0] != self.hash_password(DATABASE_CONFIG['password']):
                raise Exception("Invalid username or password")

        except Exception as e:
            print("Error occurred while connecting to the database: ", str(e))





    def fetch_closing_price(self,symbol, date):
        # Fetch historical market data
        data = yf.Ticker(symbol).history(start=date, end=date + datetime.timedelta(days=1))

        # Return the closing price
        return data['Close'][0]

    