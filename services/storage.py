import boto3
from botocore.config import Config
from django.conf import settings

class R2StorageService:
    def __init__(self):
        self.access_key = settings.R2_ACCESS_KEY
        self.secret_key = settings.R2_SECRET_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.access_key or 'your_' in self.access_key:
                # Return a mock or None if credentials are placeholders
                return None
            
            self._client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
        return self._client

    def generate_signed_url(self, object_key, expiration=3600):
        if self.client is None:
            # Fallback for development if R2 is not configured
            return f"https://placeholder-r2.com/{self.bucket_name}/{object_key}?signed=true"
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            # In production, use a logger
            print(f"Error generating signed URL: {e}")
            return None

    def upload_file(self, file_path, object_key, content_type=None):
        if self.client is None:
            return False
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
            
        try:
            self.client.upload_file(
                file_path, 
                self.bucket_name, 
                object_key,
                ExtraArgs=extra_args
            )
            return True
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            return False

    def list_files(self, prefix=''):
        if self.client is None:
            return {"files": [], "folders": []}
        
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            result = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter='/')
            
            files = []
            folders = []
            
            for page in result:
                # Handle subfolders (prefixes)
                for folder in page.get('CommonPrefixes', []):
                    folders.append(folder.get('Prefix'))
                
                # Handle files
                for obj in page.get('Contents', []):
                    if obj.get('Key') != prefix: # Don't include the folder itself
                        files.append({
                            "key": obj.get('Key'),
                            "size": obj.get('Size'),
                            "last_modified": obj.get('LastModified').isoformat(),
                            "url": self.generate_signed_url(obj.get('Key'))
                        })
            
            return {"files": files, "folders": folders}
        except Exception as e:
            print(f"Error listing R2 files: {e}")
            return {"files": [], "folders": []}

    def download_file(self, object_key, destination_path):
        if self.client is None:
            return False
        
        try:
            self.client.download_file(self.bucket_name, object_key, destination_path)
            return True
        except Exception as e:
            print(f"Error downloading from R2: {e}")
            return False

# Singleton instance
storage_service = R2StorageService()
