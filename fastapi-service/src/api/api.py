import requests
import uuid
from src.schemas import ( UploadResponseSchema, ListUploadResponseSchema )
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import ClientError
from src.api.s3_dependencies import ( bucket_name, s3_client )
from typing import List
from src.api.routers import (
    computer_components,
    purchase_invoices,
    inbound_deliveries,
    computer_component_categories,
    sellable_products,
    cart,
    sales_quotes,
    sales_invoices,
    sales_deliveries,
    users,
    seeds,
    report_inventory_movements,
    report_purchase_invoices,
    ai_report_analyzer,
    purchase_invoices_query_analysis,
    payment,
    jobs
)
from src.api.routers.sales_payment import (
    bank_transfer,
    virtual_account
)
from src.api.routers.sales_payment.adyen import (
    webhook,
    sessions
)
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import os
from src.api.session_db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from src.sales_deliveries.create_service import CreateService as SalesDeliveryCreateService
from config import setting

scheduler = AsyncIOScheduler()

def create_sales_delivery_every_thirty_seconds(db: Session = next(get_db())):
    create_service = SalesDeliveryCreateService(db)
    create_service.call()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get('TESTING'):
        scheduler.add_job(create_sales_delivery_every_thirty_seconds, 'interval', seconds=30) # Run every 30 seconds\
        scheduler.start()

    yield

    if not os.environ.get('TESTING'):
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan) # add lifespan to fastapi initialization

origins = [
    'http://localhost',
    "https://www.pcshopgoodprice.com",
    "https://pcshopgoodprice.com",
    "http://localhost:3000",
    "http://localhost:3003",
    'localhost',
    "http://frontend:3000",
    "http://backend:8000",
    setting.AWS_IPV4_PUBLIC_ADDRESS]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(computer_components.router)
app.include_router(purchase_invoices.router)
app.include_router(inbound_deliveries.router)
app.include_router(report_purchase_invoices.router)
app.include_router(report_inventory_movements.router)
app.include_router(computer_component_categories.router)
app.include_router(sellable_products.router)
app.include_router(cart.router)
app.include_router(sales_quotes.router)
app.include_router(bank_transfer.router)
app.include_router(virtual_account.router)
app.include_router(sales_invoices.router)
app.include_router(sales_deliveries.router)
app.include_router(users.router)
app.include_router(seeds.router)
app.include_router(ai_report_analyzer.router)
app.include_router(purchase_invoices_query_analysis.router)
app.include_router(webhook.router)
app.include_router(sessions.router)
app.include_router(payment.router)
app.include_router(jobs.router)

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

    try:
        final_result = []
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

        return {'image_list': final_result}
    except ClientError as e:
        logging.error(e)
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