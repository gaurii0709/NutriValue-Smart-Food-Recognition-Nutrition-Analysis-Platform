import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
import os
import shutil
import random

print("🚀 1-HOUR TRAINING using your combined_dataset...")

# USE YOUR EXISTING DATA PATH
train_source = r"C:\PythonProject1\ml_model\combined_dataset\train"

FOODS = ['pizza', 'hamburger', 'fried_rice', 'ice_cream', 'cheesecake']

# Verify folders exist
for food in FOODS:
    food_path = os.path.join(train_source, food)
    if os.path.exists(food_path):
        print(f"✅ Found {food} with images")
    else:
        print(f"❌ Missing {food}")

# Load pre-trained MobileNetV2
print("\n📥 Loading MobileNetV2...")
base_model = MobileNetV2(
    input_shape=(128, 128, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

# Add classifier
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(5, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Create temporary dataset folders
os.makedirs("temp_train", exist_ok=True)
os.makedirs("temp_val", exist_ok=True)

print("\n📁 Preparing dataset from combined_dataset...")
for food in FOODS:
    src = os.path.join(train_source, food)
    images = os.listdir(src)
    random.shuffle(images)

    # Take 550 for training, 139 for validation
    train_imgs = images[:550]
    val_imgs = images[550:689]

    os.makedirs(f"temp_train/{food}", exist_ok=True)
    os.makedirs(f"temp_val/{food}", exist_ok=True)

    for img in train_imgs:
        shutil.copy(os.path.join(src, img), f"temp_train/{food}/{img}")
    for img in val_imgs:
        shutil.copy(os.path.join(src, img), f"temp_val/{food}/{img}")

    print(f"✅ {food}: {len(train_imgs)} train, {len(val_imgs)} val")

# Load data
train = tf.keras.preprocessing.image_dataset_from_directory(
    'temp_train',
    image_size=(128, 128),
    batch_size=32
)

val = tf.keras.preprocessing.image_dataset_from_directory(
    'temp_val',
    image_size=(128, 128),
    batch_size=32
)

# Train just the top layers (30 minutes)
print("\n🚀 Training top layers...")
history = model.fit(
    train,
    validation_data=val,
    epochs=10,
    callbacks=[tf.keras.callbacks.EarlyStopping(patience=2)]
)

# Fine-tune (30 more minutes)
print("\n🚀 Fine-tuning entire model...")
base_model.trainable = True
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history_fine = model.fit(
    train,
    validation_data=val,
    epochs=5
)

# Save model
model.save("food_model_90percent_final.keras")
print("\n✅✅✅ MODEL SAVED! 🎉")

# Show final accuracy
_, acc = model.evaluate(val)
print(f"\n🎯 FINAL ACCURACY: {acc * 100:.2f}%")
if acc > 0.9:
    print("✅ 90%+ ACCURACY ACHIEVED!")