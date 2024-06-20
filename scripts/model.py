import os, sys
import pickle
import numpy as np
import json
import matplotlib.pyplot as plt
from PIL import Image
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.neighbors import NearestNeighbors

def preprocess_input_image(input_image_path):
    img = load_img(input_image_path, target_size=(224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img
 
def extract_features(image_path):
    img = preprocess_input_image(image_path)
    model = VGG16(weights='imagenet', include_top=False)
    features = model.predict(img)
    return features.flatten()

def load_data(filename):
    with open(filename, 'rb') as f:
        saved_data = pickle.load(f)
    return saved_data['features'], saved_data['image_files']

def run_model(features_file, input_image, k_neighbors):
    input_files = []
    # Load the saved data
    loaded_features, loaded_image_files = load_data(features_file)

    # Extract features for the input image
    input_features = extract_features(input_image)

    # Reshape the input feature vector to be compatible with the array of all features
    input_features = np.expand_dims(input_features, axis=0)

    # Create a Nearest Neighbors model and fit it to the loaded feature vectors
    nn_model = NearestNeighbors(n_neighbors=k_neighbors, metric='cosine')
    nn_model.fit(loaded_features)

    # Find the k most similar images to the input image
    distances, indices = nn_model.kneighbors(input_features)

    # Display the paths of the k most similar images along with the percentage of resemblance
    for i, idx in enumerate(indices[0]):
        similarity_percentage = (1 - distances[0][i]) * 100
        #print(f"{loaded_image_files[idx]} - Resemblance: {similarity_percentage:.2f}%")
        if similarity_percentage >= 0:
          input_files.append(loaded_image_files[idx].split('/')[-1])

    modified_files = [filename[5:] for filename in input_files]
    return modified_files

   