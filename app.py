from flask import Flask, render_template, send_from_directory, redirect, url_for, request, Response
import os, csv, requests
from datetime import date
from scripts.fetch_plot import analyze_and_plot_specific_day
from scripts.model import run_model
from scripts.build_historical_charts import create_candlestick_chart, plot_todays_chart
import pandas as pd

app = Flask(__name__)

#BASE_USER = 'homer'
BASE_USER = 'zicocharts'

def clear_tmp_directory():
    tmp_dir = f'/home/{BASE_USER}/zicocharts/tmp/'
    for file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Error deleting file {file_path}: {e}')

def map_filenames_to_dates(filenames, csv_file_path=f'/home/{BASE_USER}/zicocharts/data/dates.csv'):
    number_to_date = {}
    with open(csv_file_path, mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            number_to_date[row[0]] = row[1]

    result_dates = []
    for filename in filenames:
        number = filename.split('_')[1].split('.')[0]
        corresponding_date = number_to_date.get(number)
        result_dates.append(corresponding_date if corresponding_date else None)
    return result_dates

@app.route('/')
def index():
    image_folder = f'/home/{BASE_USER}/zicocharts/tmp/'
    images = [file for file in os.listdir(image_folder) if file.endswith(('.png', '.jpg', '.jpeg'))]
    images = [f'/tmp/{file}' for file in images]
    return render_template('index.html', images=images)

@app.route('/submit', methods=['POST'])
def submit():
    clear_tmp_directory()

    TIMEFRAME = 15
    DATE_INPUTTED = date.today().isoformat()
    CUTOFF_TIME = '12:00'
    TICKER = '^GSPC'
    WINDOW_SIZE = 5
    MODEL_CUTOFF_TIME = '1200'

    INPUT_IMAGE = f'/home/{BASE_USER}/zicocharts/tmp/input.png'
    FEATURES_FILE = f'/home/{BASE_USER}/zicocharts/models/{MODEL_CUTOFF_TIME}_{TIMEFRAME}_vgg.pkl'
    DEFAULT_K_NEIGHBORS = 10

    analyze_and_plot_specific_day(TICKER, DATE_INPUTTED, WINDOW_SIZE, TIMEFRAME, f"{DATE_INPUTTED} {CUTOFF_TIME}")
    PREDICTION_FILES = run_model(FEATURES_FILE, INPUT_IMAGE, DEFAULT_K_NEIGHBORS)

    with open(f'/home/{BASE_USER}/zicocharts/tmp/prediction_files.txt', 'w') as f:
        f.write('\n'.join(PREDICTION_FILES))

    plot_todays_chart(TICKER, f'{TIMEFRAME}m')
    #os.unlink(f'/home/{BASE_USER}/zicocharts/tmp/input.png')

    # Fetch and save images from the URL
    BASE_URL = 'https://zaki-ay.github.io/zicocharts_images/plots/'
    tmp_dir = f'/home/{BASE_USER}/zicocharts/tmp/'

    for filename in PREDICTION_FILES:
        image_url = f'{BASE_URL}{filename}'
        response = requests.get(image_url)

        if response.status_code == 200:
            with open(os.path.join(tmp_dir, filename), 'wb') as f:
                f.write(response.content)
        else:
            print(f"Error fetching image {filename}: {response.status_code}")

    return redirect(url_for('index'))

@app.route('/tmp/<filename>')
def send_image(filename):
    return send_from_directory(f'/home/{BASE_USER}/zicocharts/tmp/', filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
