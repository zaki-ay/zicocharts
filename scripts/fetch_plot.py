import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

#BASE_USER = 'homer'
BASE_USER = 'zicocharts'
    
def fetch_financial_data(ticker, start_date, end_date, interval):
    """Fetches financial data for a given ticker and date range."""
    spx = yf.Ticker(ticker)
    data = spx.history(interval=interval, start=start_date, end=end_date)
    return data

def get_min_max_prices(data):
    """Calculates the minimum and maximum prices from the given data."""
    min_price = data['Close'].min()
    max_price = data['Close'].max()
    return min_price, max_price

def get_current_trading_time():
    """Returns the current time within the trading day, aware of timezone."""
    now = datetime.now().astimezone()
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    if now < market_open:
        return market_open
    elif now > market_close:
        return market_close
    return now

def plot_data_for_specific_day(data, specific_day, y_min, y_max, cutoff_time):
    """Plots the data for a specific day up to the cutoff time, maintaining full day dimensions."""
    plt.figure(figsize=(10, 6))

    if not data.empty:
        data_to_plot = data[data.index <= cutoff_time]
        full_day_end = pd.Timestamp(specific_day + " 16:00").tz_localize(cutoff_time.tzinfo)
        plt.plot(data_to_plot['Close'], color='black')
        plt.xlim([data.index[0], full_day_end])
        plt.ylim([y_min, y_max])
        plt.tight_layout()
        plt.axis('off')
    else:
        print(f"No trading data available for {specific_day}.")

    plt.savefig(f'/home/{BASE_USER}/zicocharts/tmp/input.png', transparent=True)
    plt.close()

def analyze_and_plot_specific_day(ticker, specific_day, window_size, timeframe, cutoff_time=None):
    """Main function to analyze and plot data for a specific day."""
    end_date = datetime.strptime(specific_day, "%Y-%m-%d") + timedelta(days=1)
    start_date = end_date - timedelta(days=window_size)

    # Prepare interval string for minute data
    interval = f"{timeframe}m"

    # Fetch data
    data = fetch_financial_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), interval)

    # Check if data is empty
    if data.empty:
        print("No data fetched. There might be no trading data available for this range or interval.")
        return

    # Get min and max prices
    min_price, max_price = get_min_max_prices(data)

    # Extracting data for the specific day
    specific_day_data = data[data.index.date == datetime.strptime(specific_day, '%Y-%m-%d').date()]

    # Determine current time within trading hours if cutoff_time is not provided
    if cutoff_time is None:
        cutoff_time = get_current_trading_time()
    else:
        cutoff_time = pd.Timestamp(cutoff_time).tz_localize('America/New_York') if pd.Timestamp(cutoff_time).tzinfo is None else pd.Timestamp(cutoff_time)

    # Ensure data index is timezone-aware
    if specific_day_data.index.tzinfo is None:
        specific_day_data.index = specific_day_data.index.tz_localize('America/New_York')
    else:
        specific_day_data.index = specific_day_data.index.tz_convert('America/New_York')

    # Plot data for the specific day up to the cutoff time
    plot_data_for_specific_day(specific_day_data, specific_day, min_price, max_price, cutoff_time)
