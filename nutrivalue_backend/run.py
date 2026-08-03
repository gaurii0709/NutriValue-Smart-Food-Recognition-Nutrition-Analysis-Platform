import uvicorn
from app.main import app   # 🔥 DIRECT IMPORT — FIXES EVERYTHING

if __name__ == "__main__":
    print("🚀 Starting NutriValue Backend...")
    print("📝 API Docs: http://localhost:8000/docs")
    print("🌐 Health Check: http://localhost:8000/health")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(
        app,               # ✅ pass app object, NOT string
        host="0.0.0.0",
        port=8000,
        reload=False,      # ❗ important on Windows + py3.13
        log_level="info"
    )
