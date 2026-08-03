import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # App
    APP_NAME = "NutriValue"
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # API
    API_V1_PREFIX = "/api/v1"

    # Food Categories
    FOOD_CATEGORIES = [
        "flatbreads",
        "rice_dishes",
        "curries",
        "savory_snacks",
        "sweets_desserts"
    ]

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    UPLOAD_FOLDER = "uploads"

    # Frontend URLs
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


config = Config()