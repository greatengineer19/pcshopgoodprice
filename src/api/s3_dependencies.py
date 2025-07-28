import boto3
from config import setting

def bucket_name():
    return 'hassle-free-computers-bucket'

def s3_client():
    return boto3.client('s3',
                         aws_access_key_id=setting.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=setting.AWS_SECRET_ACCESS_KEY)