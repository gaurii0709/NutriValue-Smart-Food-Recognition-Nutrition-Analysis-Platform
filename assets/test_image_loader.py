import cv2
import matplotlib.pyplot as plt
import os

image_path = os.path.join(os.path.dirname(__file__), "..", "sample_food.jpg")

img = cv2.imread(image_path)

if img is None:
    print("❌ Image not found! Check if sample_food.jpg is in main project folder.")
else:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.axis("off")
    plt.show()
