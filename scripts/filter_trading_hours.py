import pandas as pd

def filter_by_trading_hours(file_path, output_path):
    # Load the data from CSV file
    data = pd.read_csv(file_path, parse_dates=['Timestamp'])
    
    # Ensure the 'Timestamp' column is recognized as datetime
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    # Set the timestamp as the index
    data.set_index('Timestamp', inplace=True)
    
    # Filter data between 09:30 and 16:00
    filtered_data = data.between_time('09:30:00', '16:00:00')
    
    # Save the filtered data to a new CSV file
    filtered_data.to_csv(output_path)
    print("Filtered data has been saved to:", output_path)

# Specify the path to the input and output files
input_file_path = '../data/cleaned_data.csv'
output_file_path = '../data/data.csv'

# Run the function
filter_by_trading_hours(input_file_path, output_file_path)
