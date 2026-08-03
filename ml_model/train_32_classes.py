import tensorflow as tf
from tensorflow.keras import layers, models
import os
import matplotlib.pyplot as plt

# Paths
train_dir = "combined_dataset_full_backup/train"
val_dir = "combined_dataset_full_backup/val"

# Image settings
IMG_SIZE = (128, 128)
BATCH_SIZE = 32

# Load datasets
train_data = tf.keras.preprocessing.image_dataset_from_directory(
    train_dir,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_data = tf.keras.preprocessing.image_dataset_from_directory(
    val_dir,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Get class names
class_names = train_data.class_names
print(f"\n✅ Total classes: {len(class_names)}")
print(f"📝 First 10 classes: {class_names[:10]}")

# Save class names for later use
with open('class_names_32.txt', 'w') as f:
    for name in class_names:
        f.write(f"{name}\n")

# Normalize pixel values
normalization_layer = layers.Rescaling(1. / 255)
train_data = train_data.map(lambda x, y: (normalization_layer(x), y))
val_data = val_data.map(lambda x, y: (normalization_layer(x), y))

# Data augmentation for better accuracy
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# Apply augmentation only to training data
train_data = train_data.map(
    lambda x, y: (data_augmentation(x, training=True), y)
)

# Build model (slightly deeper for 32 classes)
model = models.Sequential([
    # First conv block
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
    layers.MaxPooling2D(),

    # Second conv block
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(),

    # Third conv block
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D(),

    # Fourth conv block (added for complexity)
    layers.Conv2D(256, (3, 3), activation='relu'),
    layers.MaxPooling2D(),

    # Classifier
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),  # Reduce overfitting
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(
        patience=5,
        restore_best_weights=True,
        monitor='val_loss'
    ),
    tf.keras.callbacks.ModelCheckpoint(
        'best_model_32.keras',
        save_best_only=True,
        monitor='val_accuracy'
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        factor=0.2,
        patience=3,
        monitor='val_loss'
    )
]

# Train
print("\n🚀 Starting training...")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=30,
    callbacks=callbacks
)

# Save final model
model.save("food_model_32.keras")
print("\n🎉 Model training completed and saved as food_model_32.keras")

# Plot training history
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig('training_history_32.png')
plt.show()

print("\n📊 Training history saved as training_history_32.png")