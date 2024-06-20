import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import datetime

BASE_USER = 'homer'
#BASE_USER = 'zicocharts'

# Function to fetch and plot today's candlestick chart for a given stock symbol and timeframe
def plot_todays_chart(ticker, timeframe):
    # Get today's date
    today = datetime.datetime.now().date()

    # Fetch data for today from yfinance
    data = yf.download(ticker, start=today, end=today + datetime.timedelta(days=1), interval=timeframe)
    
    if data.empty:
        print(f"No data available for today: {today} for the ticker: {ticker}")
        return

    # Check if there is sufficient data to plot
    if 'Open' not in data.columns:
        print("Incomplete data received, cannot plot chart.")
        return
    
    # Plot the candlestick chart
    mpf.plot(data, type='candle', style='charles', title=f'Today\'s Candlestick chart for {ticker} at {timeframe}', ylabel='Price')
    plt.savefig(f'/home/{BASE_USER}/zicocharts/tmp/{today}_{ticker}_{timeframe}.png')

# Example usage
ticker_to_plot = '^GSPC'  # Apple Inc. as an example
timeframe_to_plot = '15m'  # 5 minutes timeframe
plot_todays_chart(ticker_to_plot, timeframe_to_plot)
