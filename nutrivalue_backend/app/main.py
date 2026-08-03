from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import config

# Create uploads directory if it doesn't exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(
    title=config.APP_NAME,
    description="Smart Food Nutrition Estimator with AI",
    version="1.0.0"
)

# ✅ Allow React frontend (CORS FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads folder
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_FOLDER), name="uploads")

# Import API routes
from app.routes.api import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to NutriValue API! 🍎",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": config.APP_NAME,
        "message": "Ready to analyze food! 🚀"
    }