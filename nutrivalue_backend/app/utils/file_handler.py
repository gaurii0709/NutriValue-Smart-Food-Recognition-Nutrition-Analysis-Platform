import os
import uuid
from fastapi import UploadFile
from app.config import config


async def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file and return file path
    """
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

        # Ensure upload directory exists
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

        # Read and save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        print(f"✅ File saved successfully: {file_path}")
        return file_path

    except Exception as e:
        print(f"❌ Error saving file: {e}")
        raise e
    finally:
        await file.close()