import yfinance as yf
from configparser import ConfigParser
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import display, clear_output

class StockMonitor:
    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.purchases = self._parse_ini_file()

    def _parse_ini_file(self):
        parser = ConfigParser()
        parser.read(self.ini_file)

        purchases = {}
        for section in parser.sections():
            purchase_info = {}

            if 'purchase_date' in parser[section]:
                purchase_info['purchase_date'] = parser.get(section, 'purchase_date')

                if 'purchase_time' in parser[section]:
                    purchase_info['purchase_time'] = parser.get(section, 'purchase_time')

            if 'purchase_price' in parser[section]:
                purchase_price = parser.get(section, 'purchase_price')
                if ',' in purchase_price:
                    purchase_price = purchase_price.strip('[]')
                    purchase_info['purchase_price'] = [float(price.strip()) for price in purchase_price.split(',')]
                else:
                    purchase_info['purchase_price'] = float(purchase_price)

            if 'quantity' in parser[section]:
                quantity = parser.get(section, 'quantity')
                if ',' in quantity:
                    quantity = quantity.strip('[]')
                    purchase_info['quantity'] = [int(qty.strip()) for qty in quantity.split(',')]
                else:
                    purchase_info['quantity'] = int(quantity)

            purchases[section] = purchase_info

        return purchases

    def _get_closing_price(self, symbol, date):
        stock = yf.Ticker(symbol)
        data = stock.history(start=date, end=date)
        return data['Close'].values[0]

    @property
    def get_dict(self):
        stock_dict = {}
        for symbol, purchase_info in self.purchases.items():
            if 'purchase_price' in purchase_info:
                purchase_price = purchase_info['purchase_price']
            elif 'purchase_date' in purchase_info:
                purchase_date = purchase_info['purchase_date']
                purchase_time = purchase_info.get('purchase_time', None)

                if isinstance(purchase_date, list):
                    purchase_price = []
                    for date, time in zip(purchase_date, purchase_time):
                        closing_price = self._get_closing_price(symbol, date)
                        purchase_price.append(closing_price)
                else:
                    closing_price = self._get_closing_price(symbol, purchase_date)
                    purchase_price = closing_price

            quantity = purchase_info['quantity']
            stock_dict[symbol] = (purchase_price, quantity)

        return stock_dict

    @property
    def total_invested_amount(self):
        stock_dict = self.get_dict
        total_amount = 0
        for symbol, (purchase_price, quantity) in stock_dict.items():
            if isinstance(purchase_price, list):
                total_amount += sum([price * qty for price, qty in zip(purchase_price, quantity)])
            else:
                total_amount += purchase_price * quantity

        return total_amount

    @property
    def current_amount(self):
        stock_dict = self.get_dict
        current_amount = 0
        for symbol, (purchase_price, quantity) in stock_dict.items():
            stock = yf.Ticker(symbol)
            current_price = stock.history(period='1d')['Close'][-1]
            if isinstance(purchase_price, list):
                current_amount += sum([current_price * qty for qty in quantity])
            else:
                current_amount += current_price * quantity

        return current_amount

    def _animate(self, i):
        stock_dict = self.get_dict

        for symbol, (purchase_price, quantity) in stock_dict.items():
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d')

            ax = plt.gca()
            ax.cla()
            ax.plot(data['Close'], label='Close Price')
            ax.axhline(y=purchase_price, color='r', linestyle='--', label='Purchase Price')
            ax.set_title(f'{symbol} Stock')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.legend()

            current_price = data['Close'][-1]
            if isinstance(purchase_price, list):
                profit = sum([(current_price - purchase) * qty for purchase, qty in zip(purchase_price, quantity)])
            else:
                profit = (current_price - purchase_price) * quantity

            ax.text(0.02, 0.95, f'Live Profit: {profit:.2f}', transform=ax.transAxes, ha='left', va='top')

    @property
    def plot_stocks(self):
        fig = plt.figure(figsize=(10, 6))
        anim = FuncAnimation(fig, self._animate, interval=2000)
        
        # Clear the previous plot and display the updated animation
        clear_output(wait=True)
        display(fig)
        
        # Delay before starting the next animation frame
        plt.pause(0.1)
        
        # Stop the animation after 10 frames
        if anim.frame_seq.__len__() >= 10:
            plt.close(fig)
        else:
            plt.close(fig)
            self.plot_stocks()