import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import datetime

BASE_USER = "homer"
#BASE_USER = "zicocharts"

# Load historical data
# data_file = f'/home/{BASE_USER}/zicocharts/data/data.csv'
# historical_data = pd.read_csv(data_file)

# # Ensure the Timestamp column is in datetime format
# historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'])

# Function to create candlestick chart for a given date and timeframe
def create_candlestick_chart(data, date, timeframe):
    # Filter data for the specific date
    date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
    daily_data = data[data['Timestamp'].dt.strftime('%Y-%m-%d') == date_str]
    
    if daily_data.empty:
        print(f"No data available for the date: {date}")
        return
    
    # Set the Timestamp as index
    daily_data.set_index('Timestamp', inplace=True)
    
    # Resample the data based on the specified timeframe
    resampled_data = daily_data.resample(timeframe).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()  # Drop rows with NaN values which result from no data being available in the period
    
    # Plot the candlestick chart
    mpf.plot(
        resampled_data,
        type='line',
        style='charles',
        ylabel='Price',
        title='',  # No title
        savefig=dict(fname=f'/home/{BASE_USER}/zicocharts/tmp/{date_str}_{timeframe}.png', dpi=300, bbox_inches='tight')  # Save with higher DPI and full view
    )

def plot_todays_chart(ticker, timeframe, cutoff_time=None):
    # Get today's date
    today = datetime.datetime.now().date()

    # Determine the end time for data fetching
    if cutoff_time:
        end_time = datetime.datetime.strptime(f'{today} {cutoff_time}', '%Y-%m-%d %H:%M')
    else:
        end_time = datetime.datetime.combine(today, datetime.time.max)
    
    # Fetch data for today from yfinance
    data = yf.download(ticker, start=today, end=end_time, interval=timeframe)
    
    if data.empty:
        print(f"No data available for today: {today} for the ticker: {ticker}")
        return

    # Check if there is sufficient data to plot
    if 'Open' not in data.columns:
        print("Incomplete data received, cannot plot chart.")
        return
    
    # Plot the candlestick chart
    mpf.plot(data, type='candle', style='charles', title=f'Today\'s Candlestick chart for {ticker} at {timeframe}', ylabel='Price')
    plt.savefig(f'/home/{BASE_USER}/zicocharts/tmp/current.png')

# Example usage
#date_to_plot = '2023-01-27'  # Change this to the date you want to plot
#timeframe_to_plot = '15min'  # Change this to the desired timeframe
#create_candlestick_chart(historical_data, date_to_plot, timeframe_to_plot)
