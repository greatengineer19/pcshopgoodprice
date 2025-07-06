import os
import io
import requests
import uuid
import boto3
from src.schemas import ( UploadResponseSchema, ListUploadResponseSchema )
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from botocore.exceptions import ClientError
from src.api.s3_dependencies import ( bucket_name, s3_client )
from typing import List
from src.api.routers import (
    computer_components,
    purchase_invoices,
    inbound_deliveries,
    report_purchase_invoice,
    report_inventory_movement,
    computer_component_categories,
    sellable_products,
    cart,
    sales_quotes,
    sales_invoices,
    sales_deliveries,
    user
)
from src.api.routers.sales_payment import (
    bank_transfer,
    virtual_account
)

app = FastAPI()

origins = [
    'http://localhost',
    "http://localhost:3000",
    'localhost',
    "http://frontend:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(computer_components.router)
app.include_router(purchase_invoices.router)
app.include_router(inbound_deliveries.router)
app.include_router(report_purchase_invoice.router)
app.include_router(report_inventory_movement.router)
app.include_router(computer_component_categories.router)
app.include_router(sellable_products.router)
app.include_router(cart.router)
app.include_router(sales_quotes.router)
app.include_router(bank_transfer.router)
app.include_router(virtual_account.router)
app.include_router(sales_invoices.router)
app.include_router(sales_deliveries.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return { "message": "Hello World" }

@app.post("/api/upload_url", response_model=UploadResponseSchema)
async def upload_file(file: UploadFile):
    uuid4_value = uuid.uuid4()
    s3_filename = f"{uuid4_value}_{file.filename}"

    presigned_post = create_presigned_post(s3_filename)
    if presigned_post is None:
        exit(1)

    try:
        file_content = await file.read()
        files = { 'file': (s3_filename, file_content) }
        http_response = requests.post(
            presigned_post['url'],
            data=presigned_post['fields'],
            files=files
        )

        return {
            'status_code': http_response.status_code,
            's3_key': presigned_post['fields']['key']
        }
    except ClientError as e:
        logging.error(e)
        return False
    
@app.post("/api/multi_upload_url", response_model=ListUploadResponseSchema)
async def upload_files(files: List[UploadFile] = File(...)):
    presigned_posts = []
    print('A')
    for file in files:
        uuid4_value = uuid.uuid4()
        s3_filename = f"{uuid4_value}_{file.filename}"

        presigned_post = create_presigned_post(s3_filename)
        if presigned_post is None:
            exit(1)

        post_result = {
            's3_filename': s3_filename,
            'presigned_post': presigned_post
        }
        presigned_posts.append(post_result)
        print('B')

    try:
        final_result = []
        print('C')
        for i, post_result in enumerate(presigned_posts):
            presigned_post = post_result['presigned_post']
            s3_filename = post_result['s3_filename']

            file_content = await files[i].read()
            files_to_upload = { 'file': (s3_filename, file_content) }
            http_response = requests.post(
                presigned_post['url'],
                data=presigned_post['fields'],
                files=files_to_upload
            )

            result = {
                'status_code': http_response.status_code,
                's3_key': presigned_post['fields']['key']
            }
            final_result.append(result)
            print('D')

        print('E')
        return {'image_list': final_result}
    except ClientError as e:
        logging.error(e)
        print('F')
        return False

def create_presigned_post(file_name: str):
    try:
        response = s3_client().generate_presigned_post(
            bucket_name(),
            file_name,
            ExpiresIn=3600
        )
    except ClientError as e:
        logging.error(e)
        return None
    
    # The response contains the presigned URL and required fields
    return response