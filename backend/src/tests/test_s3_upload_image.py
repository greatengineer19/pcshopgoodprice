from src.tests.conftest import ( client, db_session, setup_factories )
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from io import BytesIO
from fastapi import UploadFile
from src.api.api import app

import pytest
import boto3
import requests
import uuid

@pytest.mark.asyncio
async def test_upload_file_success(client):
    test_uuid = uuid.UUID('12345678123456781234567812345678')
    mock_presigned_post = {
        'url': 'https://mock-s3-url.com',
        'fields': {
            'key': '12345678123456781234567812345678_test.jpg'
        }
    }

    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.file_name = "test_image.jpg"
    mock_file.read.return_value = b"test file content"

    with patch('uuid.uuid4', return_value=test_uuid), \
         patch('src.api.api.create_presigned_post', return_value=mock_presigned_post), \
         patch('requests.post', return_value=mock_http_response):
        
        test_file = BytesIO(b"test file content")

        response = client.post("/api/upload_url",
                               files={"file": ("test_image.jpg", test_file, "image/jpeg")})
        assert response.status_code == 200
        assert response.json() == {
            'status_code': 200,
            's3_key': '12345678123456781234567812345678_test.jpg'
        }

def test_upload_file(client):
    s3_client = boto3.client('s3')
    bucket_name = 'test-bucket'
    file_name = 'test_jpeg.jpg'
    file_content = b"test image content"

    sample_response = {
        'url': 'https://test-bucket.s3.amazonaws.com/',
        'fields': {
            'key': 'test-key-object-name',
            'AWSAccessKeyId': 'test-access-key-id',
            'policy': 'test-policy',
            'signature': 'test-signature'
        }
    }
    
    with patch.object(s3_client, 'generate_presigned_post', return_value=sample_response) as mock_method:
        stubbed_response = s3_client.generate_presigned_post(
            bucket_name,
            file_name,
            ExpiresIn=3600
        )

        assert stubbed_response == sample_response
        mock_method.assert_called_with(bucket_name, file_name, ExpiresIn=3600)

