from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2

# Load pre-trained MobileNet
model = MobileNet(weights='imagenet')

# Load image
img_path = r"C:\PythonProject1\sample_food.jpg"
img = image.load_img(img_path, target_size=(224, 224))

# Convert to array
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

# Predict
preds = model.predict(x)
print('Predicted:', decode_predictions(preds, top=3)[0])
