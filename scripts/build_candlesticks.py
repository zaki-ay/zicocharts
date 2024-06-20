import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

#BASE_USER = "homer"
BASE_USER = "zicocharts"

# Load historical data
data_file = '/home/{BASE_USER}/zicocharts/data/data.csv'
historical_data = pd.read_csv(data_file)

# Ensure the Timestamp column is in datetime format
historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'])

# Function to create candlestick chart for a given date
def create_candlestick_chart(data, date):
    # Filter data for the specific date
    date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
    daily_data = data[data['Timestamp'].dt.strftime('%Y-%m-%d') == date_str]
    
    if daily_data.empty:
        print(f"No data available for the date: {date}")
        return
    
    # Set the Timestamp as index
    daily_data.set_index('Timestamp', inplace=True)
    
    # Plot the candlestick chart
    mpf.plot(daily_data, type='candle', style='charles', title=f'Candlestick chart for {date_str}', ylabel='Price')
    plt.savefig('f.png')

# Example usage
date_to_plot = '2023-02-02'  # Change this to the date you want to plot
create_candlestick_chart(historical_data, date_to_plot)
