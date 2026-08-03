import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

# Load model
model = tf.keras.models.load_model("food_model_32.keras")

# Load class names
with open('class_names_32.txt', 'r') as f:
    class_names = [line.strip() for line in f.readlines()]

print(f"✅ Model loaded with {len(class_names)} classes")


# Test on a sample image
def predict_food(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    predictions = model.predict(img_array, verbose=0)[0]
    top_3_idx = np.argsort(predictions)[-3:][::-1]

    print(f"\n📸 Image: {img_path}")
    print("🔝 Top 3 predictions:")
    for idx in top_3_idx:
        print(f"   {class_names[idx]}: {predictions[idx] * 100:.2f}%")


# Test on validation images
test_dir = "combined_dataset_full_backup/val"
for class_name in class_names[:3]:  # Test first 3 classes
    class_path = os.path.join(test_dir, class_name)
    if os.path.exists(class_path):
        images = os.listdir(class_path)
        if images:
            predict_food(os.path.join(class_path, images[0]))