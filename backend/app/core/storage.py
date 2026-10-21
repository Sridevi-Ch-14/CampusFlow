import os
import uuid
import shutil
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE.lower()
        self.local_dir = os.path.abspath(settings.LOCAL_STORAGE_DIR)
        if self.storage_type == "local":
            os.makedirs(self.local_dir, exist_ok=True)

    def save_file(self, file: UploadFile) -> Tuple[str, str, int]:
        """
        Saves uploaded file and returns (storage_key, filename, file_size)
        """
        ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_key = f"{uuid.uuid4().hex}{ext}"
        
        if self.storage_type == "local":
            destination_path = os.path.join(self.local_dir, unique_key)
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            with open(destination_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return unique_key, file.filename or unique_key, file_size
        else:
            # S3 fallback mock/boto3 interface
            # For local dev without AWS credentials, fall back to local disk
            destination_path = os.path.join(self.local_dir, unique_key)
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            with open(destination_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return unique_key, file.filename or unique_key, file_size

    def get_file_path(self, storage_key: str) -> str:
        return os.path.join(self.local_dir, storage_key)

    def delete_file(self, storage_key: str) -> bool:
        file_path = self.get_file_path(storage_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

storage_service = StorageService()
