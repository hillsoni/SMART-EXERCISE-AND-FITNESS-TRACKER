from minio import Minio
from minio.error import S3Error
import os
from werkzeug.utils import secure_filename
import uuid

class MinioService:
    def __init__(self):
        self.client = Minio(
            os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=os.getenv('MINIO_SECURE', 'False') == 'True'
        )
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME')
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def upload_file(self, file, folder="general"):
        """Upload file to MinIO and return URL"""
        filename = secure_filename(file.filename)
        unique_filename = f"{folder}/{uuid.uuid4()}_{filename}"
        
        try:
            self.client.put_object(
                self.bucket_name,
                unique_filename,
                file,
                length=-1,
                part_size=10*1024*1024
            )
            
            url = f"http://{os.getenv('MINIO_ENDPOINT')}/{self.bucket_name}/{unique_filename}"
            return url
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
    
    def delete_file(self, file_path):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")