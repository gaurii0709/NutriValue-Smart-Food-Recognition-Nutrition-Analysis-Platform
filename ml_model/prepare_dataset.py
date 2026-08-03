import os
import shutil
import random

# -----------------------------
# SETTINGS
# -----------------------------

# Correct path (since ml_model is inside PythonProject1)
BASE_DIR = "../archive/images"

# Choose classes you want
CLASSES = ["pizza", "hamburger", "ice_cream", "cheesecake", "fried_rice"]

# Output dataset folder
OUTPUT_DIR = "dataset"

# Train/Test split ratio
SPLIT_RATIO = 0.8

# -----------------------------
# CREATE TRAIN / TEST FOLDERS
# -----------------------------

for split in ["train", "test"]:
    for cls in CLASSES:
        os.makedirs(os.path.join(OUTPUT_DIR, split, cls), exist_ok=True)

# -----------------------------
# PROCESS EACH CLASS
# -----------------------------

for cls in CLASSES:
    print(f"\nProcessing {cls}...")

    class_path = os.path.join(BASE_DIR, cls)

    # Check if folder exists
    if not os.path.exists(class_path):
        print(f"❌ Folder not found: {class_path}")
        continue

    images = os.listdir(class_path)
    random.shuffle(images)

    split_index = int(len(images) * SPLIT_RATIO)
    train_images = images[:split_index]
    test_images = images[split_index:]

    # Copy training images
    for img in train_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(OUTPUT_DIR, "train", cls, img)
        shutil.copyfile(src, dst)

    # Copy testing images
    for img in test_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(OUTPUT_DIR, "test", cls, img)
        shutil.copyfile(src, dst)

    print(f"✅ Done {cls} - {len(train_images)} train / {len(test_images)} test")

print("\n🎉 Dataset preparation completed successfully!")