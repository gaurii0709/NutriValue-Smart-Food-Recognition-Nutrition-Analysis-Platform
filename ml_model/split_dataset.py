import os
import random
import shutil
from pathlib import Path

# Paths
source_dir = "/ml_model/combined_dataset_full_backup/train"
val_dir = "/ml_model/combined_dataset_full_backup/val"
test_dir = "/ml_model/combined_dataset_full_backup/test"

# Create val and test folders
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Get all classes
classes = [d for d in os.listdir(source_dir)
           if os.path.isdir(os.path.join(source_dir, d))]

print(f"📁 Found {len(classes)} classes\n")

for class_name in classes:
    print(f"Processing: {class_name}")

    class_path = os.path.join(source_dir, class_name)
    images = [f for f in os.listdir(class_path)
              if f.endswith(('.jpg', '.jpeg', '.png'))]

    print(f"   Total images: {len(images)}")

    # Shuffle images
    random.shuffle(images)

    # Split: 35 train, 8 val, 7 test (for 50 images)
    train_images = images[:35]
    val_images = images[35:43]
    test_images = images[43:50]

    # Create class folders in val and test
    os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)

    # Move validation images
    for img in val_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(val_dir, class_name, img)
        shutil.move(src, dst)
        print(f"   Moved to val: {img}")

    # Move test images
    for img in test_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(test_dir, class_name, img)
        shutil.move(src, dst)
        print(f"   Moved to test: {img}")

    # Remaining 35 images stay in train
    print(f"   ✅ Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}\n")

print("\n🎉 Dataset split complete!")
print(f"Train: {source_dir}")
print(f"Val: {val_dir}")
print(f"Test: {test_dir}")