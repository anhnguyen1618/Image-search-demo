import numpy as np
from numpy.linalg import norm
import pickle
import os
import random
import time
import math
import tensorflow
import requests
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Flatten, Dense, Dropout, GlobalAveragePooling2D
from utilities import Logger

# logger = Logger()

def download_model(model_url):
    file_name = model_url.rsplit('/', 1)[1] if model_url.find('/') else ""
    path_dir = f"./tmp/{file_name}"
    if os.path.isfile(path_dir):
        print(f"File already exist. Load file from {path_dir}")
        return path_dir

    print(f"Start downloading model at {model_url}")
    r = requests.get(model_url, allow_redirects=True)
    print(f"Writing model to dir {path_dir}")
    open(path_dir, 'wb').write(r.content)
    print("Done writing model!!!")
    return path_dir

def model_picker(name, model_url = ""):
    # logger.info(f"Picking model {name} with custom url({model_url})")
    if model_url:
        if model_url[0] == "\"":
            model_url = model_url[1:-1]
        file_name = download_model(model_url)
        if file_name:
            model = load_model(file_name)
            return model

    if (name == 'vgg16'):
        model = VGG16(weights='imagenet',
                      include_top=False,
                      input_shape=(224, 224, 3),
                      pooling='max')
    elif (name == 'vgg19'):
        model = VGG19(weights='imagenet',
                      include_top=False,
                      input_shape=(224, 224, 3),
                      pooling='max')
    elif (name == 'mobilenet'):
        model = MobileNet(weights='imagenet',
                          include_top=False,
                          input_shape=(224, 224, 3),
                          pooling='max',
                          depth_multiplier=1,
                          alpha=1)
    elif (name == 'inception'):
        model = InceptionV3(weights='imagenet',
                            include_top=False,
                            input_shape=(224, 224, 3),
                            pooling='max')
    elif (name == 'resnet'):
        model = ResNet50(weights='imagenet',
                         include_top=False,
                         input_shape=(224, 224, 3),
                        pooling='max')
    else:
        pass
        # logger.error("Specified model not available")
    return model


def extract_features(img_path, model):
    input_shape = (224, 224, 3)
    img = image.load_img(img_path,
                         target_size=(input_shape[0], input_shape[1]))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    features = model.predict(preprocessed_img)
    flattened_features = features.flatten()
    normalized_features = flattened_features / norm(flattened_features)
    return normalized_features

