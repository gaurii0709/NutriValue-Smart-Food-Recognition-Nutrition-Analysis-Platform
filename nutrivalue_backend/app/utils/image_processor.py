import os
import uuid
from typing import Optional
import cv2
import numpy as np
from PIL import Image


def save_uploaded_file(file, upload_folder: str = "uploads") -> str:
    """
    Save uploaded file and return the file path
    """
    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(upload_folder, unique_filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)

    return file_path


def validate_image(file) -> bool:
    """Simple image validation"""
    if not file or not file.filename:
        return False

    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
    ext = file.filename.split('.')[-1].lower()

    return ext in allowed_extensions


def process_image_for_ml(image_path: str, target_size: tuple = (224, 224)) -> Optional[np.ndarray]:
    """
    Process image for ML model input
    Returns: Normalized image array or None if error
    """
    try:
        # Read image
        img = Image.open(image_path)

        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize
        img = img.resize(target_size)

        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0

        return img_array

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def extract_basic_features(image_path: str) -> Optional[dict]:
    """
    Extract basic image features for analysis
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Calculate basic statistics
        mean_color = np.mean(img, axis=(0, 1)).tolist()
        std_color = np.std(img, axis=(0, 1)).tolist()

        # Calculate brightness
        brightness = np.mean(hsv[:, :, 2])

        # Calculate colorfulness (simple metric)
        (B, G, R) = cv2.split(img.astype("float"))
        rg = np.absolute(R - G)
        yb = np.absolute(0.5 * (R + G) - B)
        colorfulness = np.sqrt((rg.std() ** 2) + (yb.std() ** 2)) + 0.3 * np.sqrt((rg.mean() ** 2) + (yb.mean() ** 2))

        return {
            "dimensions": {
                "height": img.shape[0],
                "width": img.shape[1],
                "channels": img.shape[2] if len(img.shape) > 2 else 1
            },
            "color_stats": {
                "mean": mean_color,
                "std": std_color,
                "brightness": float(brightness),
                "colorfulness": float(colorfulness)
            },
            "file_info": {
                "path": image_path,
                "size_kb": os.path.getsize(image_path) / 1024
            }
        }

    except Exception as e:
        print(f"Error extracting features: {e}")
        return None