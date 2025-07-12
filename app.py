from flask import Flask, request, render_template, send_from_directory, jsonify
import os
from scripts.fetch_plot import *
from scripts.model import *
from scripts.handle_images import *

app = Flask(__name__)
PREDICTION_FILES = None
BASE_USER = "/home/zicocharts/zicocharts"
BASE_IMG_DIR = f"{BASE_USER}/tmp"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    clear_tmp_folder()

    DATA_FINENESS = int(request.form['data_fineness'])
    USER_K_NEIGHBORS = int(request.form['k_neighbors'])  # User's k-neighbors for image merging
    TIMEFRAME = int(request.form['timeframe'])
    DATE_INPUTTED = request.form['date_inputted']
    CUTOFF_TIME = request.form['cutoff_time']
    TICKER = request.form['ticker']
    WINDOW_SIZE = int(request.form['window_size'])
    MODEL_CUTOFF_TIME = request.form['cutoff_time'].replace(':', '')

    INPUT_IMAGE = f'{BASE_IMG_DIR}/input.png'
    FEATURES_FILE = f'{BASE_USER}/models/{MODEL_CUTOFF_TIME}_{TIMEFRAME}_vgg.pkl.gz'
    DEFAULT_K_NEIGHBORS = 50

    analyze_and_plot_specific_day(TICKER, DATE_INPUTTED, WINDOW_SIZE, TIMEFRAME, f"{DATE_INPUTTED} {CUTOFF_TIME}")
    PREDICTION_FILES = run_model(FEATURES_FILE, INPUT_IMAGE, DEFAULT_K_NEIGHBORS)  # Always use k-neighbors=50 for prediction

    download_images(PREDICTION_FILES)

    # Save prediction files list to allow re-merging without re-predicting
    with open(f'{BASE_USER}/prediction_files.txt', 'w') as f:
        f.write('\n'.join(PREDICTION_FILES))

    # Merge images using the first USER_K_NEIGHBORS predictions
    merge_images(PREDICTION_FILES[:USER_K_NEIGHBORS], f'{BASE_IMG_DIR}/merged_image.png')
    average_non_white_position(f'{BASE_IMG_DIR}/merged_image.png', f'{BASE_IMG_DIR}/prediction.png')
    JSON_COORDS = json.loads(connect_dots(f'{BASE_IMG_DIR}/prediction.png', DATA_FINENESS))

    return jsonify({
        'input_image': f'input.png',
        'merged_image': f'merged_image.png',
        'prediction_image': f'prediction.png',
        'connected_image': f'connected.png'
    })

@app.route('/images/<filename>')
def images(filename):
    return send_from_directory(BASE_IMG_DIR, filename)

@app.route('/remix', methods=['POST'])
def remix():
    USER_K_NEIGHBORS = int(request.form['k_neighbors'])
    DATA_FINENESS = int(request.form['data_fineness'])

    # Read the saved prediction files
    with open(f'{BASE_USER}/prediction_files.txt', 'r') as f:
        PREDICTION_FILES = f.read().splitlines()

    # Merge images using the first USER_K_NEIGHBORS predictions
    merge_images(PREDICTION_FILES[:USER_K_NEIGHBORS], f'{BASE_IMG_DIR}/merged_image.png')
    average_non_white_position(f'{BASE_IMG_DIR}/merged_image.png', f'{BASE_IMG_DIR}/prediction.png')
    JSON_COORDS = json.loads(connect_dots(f'{BASE_IMG_DIR}/prediction.png', DATA_FINENESS))

    return jsonify({
        'merged_image': f'merged_image.png',
        'prediction_image': f'prediction.png',
        'connected_image': f'connected.png'
    })

def extract_coordinates(image_path):
    # Open the image
    img = Image.open(image_path)

    # Convert image to numpy array
    img_array = np.array(img)

    # Find coordinates of non-transparent pixels (assumed to be black)
    # The condition checks for non-zero alpha (4th channel) and black color in RGB
    coords = np.column_stack(np.where((img_array[:,:,3] != 0) &
                                      (img_array[:,:,0] == 0) &
                                      (img_array[:,:,1] == 0) &
                                      (img_array[:,:,2] == 0)))

    # Convert to list of [x, y] coordinates
    # Note: numpy uses [y, x] order, so we swap them here
    coords_list = [[int(x), int(y)] for y, x in coords]

    return coords_list

@app.route('/get_coordinates')
def get_chart_data():
    try:
        coords = extract_coordinates('connected.png')
        return jsonify({"coordinates": coords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
