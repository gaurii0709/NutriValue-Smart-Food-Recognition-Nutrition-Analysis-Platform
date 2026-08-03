import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from food_mapper import map_food
from nutrition_lookup import get_nutrition

# Load MobileNet model
model = MobileNet(weights="imagenet")

# Load and process image
image_path = r"C:\PythonProject1\sample_food.jpg"
img = cv2.imread(image_path)

if img is None:
    print("❌ Image not found")
    exit()

img = cv2.resize(img, (224, 224))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = np.expand_dims(img, axis=0)
img = preprocess_input(img)

# Predict food
preds = model.predict(img)
decoded = decode_predictions(preds, top=3)[0]

predicted_food = decoded[0][1]
print("🤖 AI Predicted:", predicted_food)

# Smart map prediction
mapped_food = map_food(predicted_food)
print("🧠 Mapped Food Category:", mapped_food)

# Get nutrition info
nutrition = get_nutrition(mapped_food)

print("\n🥗 Nutrition Result:")
print(nutrition)
