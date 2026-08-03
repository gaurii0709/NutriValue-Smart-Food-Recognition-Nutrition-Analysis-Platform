import tensorflow as tf
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.preprocessing import image
import os

app = Flask(__name__)
CORS(app)  # Allow React frontend to talk to Flask

# Load model once when server starts
model = tf.keras.models.load_model("food_model.keras")

class_names = ['cheesecake', 'fried_rice', 'hamburger', 'ice_cream', 'pizza']

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    filepath = "temp.jpg"
    file.save(filepath)

    # Preprocess image
    img = image.load_img(filepath, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Predict
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = float(np.max(predictions) * 100)

    os.remove(filepath)

    return jsonify({
        "predicted_food": predicted_class,
        "mapped_food": predicted_class,
        "confidence": round(confidence, 2),
        "adjusted_nutrition": {
            "Calories": "250 kcal",
            "Protein": "8 g",
            "Fat": "10 g",
            "Carbs": "30 g"
        }
    })

if __name__ == "__main__":
    app.run(debug=True)