from flask import Flask, request, render_template, send_from_directory, jsonify
import os, csv
from scripts.fetch_plot import *
from scripts.model import *
from scripts.build_historical_charts import *
from datetime import date

app = Flask(__name__)
PREDICTION_FILES = None

#BASE_USER = 'homer'
BASE_USER = 'zicocharts'
    
def map_filenames_to_dates(filenames, csv_file_path=f'/home/{BASE_USER}/zicocharts/data/dates.csv'):
    # Step 1: Read the CSV file and create a dictionary mapping from number to date
    number_to_date = {}
    with open(csv_file_path, mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            number_to_date[row[0]] = row[1]

    # Step 2: Process the filenames and map them to dates
    result_dates = []
    for filename in filenames:
        # Extract the number part from the filename (assuming the format is always number_filename.png)
        number = filename.split('_')[1].split('.')[0]
        print(number)
        # Find the corresponding date in the dictionary
        corresponding_date = number_to_date.get(number)
        if corresponding_date:
            result_dates.append(corresponding_date)
        else:
            # Handle the case where no corresponding date is found
            result_dates.append(None)  # or you could use 'unknown' or skip this entry

    return result_dates

@app.route('/')
def submit():
    #DATA_FINENESS = int(request.form['data_fineness'])
    #USER_K_NEIGHBORS = int(request.form['k_neighbors'])  # User's k-neighbors for image merging
    TIMEFRAME = 15 #int(request.form['timeframe'])
    DATE_INPUTTED = date.today().isoformat()
    CUTOFF_TIME = '12:00' #request.form['cutoff_time']
    TICKER = '^GSPC' #request.form['ticker']
    WINDOW_SIZE = 5 #int(request.form['window_size'])
    MODEL_CUTOFF_TIME = '1200' #request.form['cutoff_time'].replace(':', '')

    INPUT_IMAGE = f'/home/{BASE_USER}/zicocharts/tmp/input.png'
    FEATURES_FILE = f'/home/{BASE_USER}/zicocharts/models/{MODEL_CUTOFF_TIME}_{TIMEFRAME}_vgg.pkl'
    DEFAULT_K_NEIGHBORS = 10

    analyze_and_plot_specific_day(TICKER, DATE_INPUTTED, WINDOW_SIZE, TIMEFRAME, f"{DATE_INPUTTED} {CUTOFF_TIME}")
    PREDICTION_FILES = run_model(FEATURES_FILE, INPUT_IMAGE, DEFAULT_K_NEIGHBORS)  # Always use k-neighbors=50 for prediction

    # Save prediction files list to allow re-merging without re-predicting
    with open(f'/home/{BASE_USER}/zicocharts/tmp/prediction_files.txt', 'w') as f:
        f.write('\n'.join(PREDICTION_FILES))

    data_file = f'/home/{BASE_USER}/zicocharts/data/data.csv'
    historical_data = pd.read_csv(data_file)

    # Ensure the Timestamp column is in datetime format
    historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'])

    PRED_DATES = map_filenames_to_dates(PREDICTION_FILES)

    for pred in PRED_DATES:
        create_candlestick_chart(historical_data,pred,'15min')

    return jsonify()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
