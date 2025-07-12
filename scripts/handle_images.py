from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os, json, requests, glob

BASE_USER = "zicofinance/zicofinance"
#BASE_USER = "homer/zcharts"

BASE_IMG_DIR = f"/home/{BASE_USER}/tmp/"
BASE_IMG_URL = 'https://zaki-ay.github.io/zicocharts_images/plots/'

def clear_tmp_folder():
    png_files = glob.glob(f'{BASE_IMG_DIR}*.png')
    for file in png_files:
        os.remove(file)

def download_images(filenames):
    local_paths = []
    for filename in filenames:
        url = BASE_IMG_URL + filename
        local_path = os.path.join(f'{BASE_IMG_DIR}', filename)
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        with open(local_path, 'wb') as f:
            f.write(response.content)
        local_paths.append(local_path)
    return local_paths
def merge_images(image_files, output_file):
        images = [Image.open(BASE_IMG_DIR + file) for file in image_files]

        # Assuming all images have the same size, use the first image's size
        width, height = images[0].size

        # Create a new transparent image with the same size
        merged_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Paste each image onto the transparent image
        for im in images:
            merged_image.paste(im, (0, 0), im)

        merged_image.save(output_file)

def average_non_white_position(image_path, average_image_path):
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size
    output_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Transparent background

    for x in range(width):
        non_transparent_positions = []
        for y in range(height):
            r, g, b, alpha = image.getpixel((x, y))
            if alpha != 0:  # Non-transparent pixel
                non_transparent_positions.append(y)

        if non_transparent_positions:
            average_position = sum(non_transparent_positions) // len(non_transparent_positions)
            # Set a 2x2 block of pixels to black with full opacity
            for y_offset in range(2):
                for x_offset in range(2):
                    if x + x_offset < width and average_position + y_offset < height:
                        output_image.putpixel((x + x_offset, average_position + y_offset), (0, 0, 0, 255))

    output_image.save(average_image_path, format="PNG")

def connect_dots(image_path, data_fineness):
    def analyze_image(image_path):
        img = Image.open(image_path)
        img = img.convert('L')
        data = np.array(img)
        
        coordinates = []
        for x in range(data.shape[1]):
            y_indices = np.where(data[:, x] == 0)[0]
            if len(y_indices) > 0:
                coordinates.append((x, y_indices[0]))
        return coordinates

    def aggregate_coordinates(coordinates, window_size):
        x, y = zip(*coordinates)
        x_avg = np.convolve(x, np.ones(window_size)/window_size, mode='valid')
        y_avg = np.convolve(y, np.ones(window_size)/window_size, mode='valid')
        return list(zip(x_avg, y_avg))

    def plot_coordinates(coordinates):
        fig, ax = plt.subplots(figsize=(10, 6))
        x, y = zip(*coordinates)
        ax.plot(x, y, color='black')
        ax.axis('off')
        
        # Set wider y-axis limits
        ax.set_ylim(min(y)*0, max(y) * 1.15)
        
        # Mirror the plot vertically
        ax.invert_yaxis()
        
        plt.savefig(f'{BASE_IMG_DIR}connected.png', transparent=True, bbox_inches='tight')
        plt.close(fig)  # Free up memory by closing the plot
        return coordinates

    coordinates = analyze_image(image_path)
    aggregated_coordinates = aggregate_coordinates(coordinates, window_size=data_fineness)
    final_coordinates = plot_coordinates(aggregated_coordinates)
    return json.dumps(final_coordinates)  # Serialize to JSON for API output or storage
