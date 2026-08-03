import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import sys

# Load trained model
model = tf.keras.models.load_model("food_model.keras")

# Class names (must match training order)
class_names = ['cheesecake', 'fried_rice', 'hamburger', 'ice_cream', 'pizza']

# Get image path from command line
img_path = sys.argv[1]

# Load and preprocess image
img = image.load_img(img_path, target_size=(128, 128))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# Predict
predictions = model.predict(img_array)
predicted_class = class_names[np.argmax(predictions)]

print("\n✅ Prediction:", predicted_class)