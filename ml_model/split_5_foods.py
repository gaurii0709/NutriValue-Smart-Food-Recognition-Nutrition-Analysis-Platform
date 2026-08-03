import os
import random
import shutil

# Paths
source_dir = "combined_dataset/train"
val_dir = "combined_dataset/val"
test_dir = "combined_dataset/test"

# Create val and test folders if they don't exist
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# The 5 foods we want
classes = ['pizza', 'hamburger', 'fried_rice', 'ice_cream', 'cheesecake']

print("📁 Splitting dataset into train/val/test...")

for class_name in classes:
    print(f"\nProcessing: {class_name}")

    class_path = os.path.join(source_dir, class_name)

    # Get all images in this class folder
    images = [f for f in os.listdir(class_path)
              if f.endswith(('.jpg', '.jpeg', '.png'))]

    print(f"   Total images: {len(images)}")

    # Shuffle the images randomly
    random.shuffle(images)

    # Split: 70% train, 15% val, 15% test
    train_count = int(len(images) * 0.7)
    val_count = int(len(images) * 0.15)

    train_images = images[:train_count]
    val_images = images[train_count:train_count + val_count]
    test_images = images[train_count + val_count:]

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

    print(f"   ✅ Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")

print("\n🎉 Dataset split complete!")
print(f"Train folder: {source_dir}")
print(f"Val folder: {val_dir}")
print(f"Test folder: {test_dir}")