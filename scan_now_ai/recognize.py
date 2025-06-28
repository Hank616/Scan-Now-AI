import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import os

# 1. Load the AI model
model = MobileNetV2(weights='imagenet')

# 2. Ask user for image file
img_path = input("Enter the full path to the image (e.g., C:\\Users\\hao07\\Desktop\\image.jpg): ").strip()

# 3. Check if the file exists
if not os.path.exists(img_path):
    print("❌ File not found. Please check the path and try again.")
    exit()

# 4. Load and preprocess the image
print("Loading image:", img_path)
img = image.load_img(img_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = preprocess_input(img_array)

# 5. Predict
print("Running prediction...")
predictions = model.predict(img_array)

# 6. Decode predictions
top_labels = decode_predictions(predictions, top=3)[0]
print("\nPrediction Results:")
for label in top_labels:
    print(f"{label[1]}: {label[2]*100:.2f}%")