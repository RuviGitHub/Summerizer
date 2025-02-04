import boto3
import os
from werkzeug.utils import secure_filename

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    def upload_file(self, file, filename):
        try:
            filename = secure_filename(filename)
            self.s3.upload_fileobj(file, self.bucket_name, f"documents/{filename}")
            file_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/documents/{filename}"
            return file_url
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
