from fastapi import APIRouter, Depends, BackgroundTasks
from ..schemas.job_schemas import (
    PaymentLoadTestRequestSchema,
    PaymentLoadTestResponseSchema
)
from src.domain.payment.commands.generate_payment_load_command import GeneratePaymentLoadCommand
from src.domain.payment.handlers.payment_load_test_handler import PaymentLoadTestHandler
from src.api.dependencies.token_fetcher import get_token
from sqlalchemy.orm import Session
from src.api.session_db import get_db
import logging
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/jobs", tags=['jobs'])
logger = logging.getLogger(__name__)

# in memory storage for job results (in production, use redis or db)
job_results = {}

@router.post("/payment-load-test", response_model=PaymentLoadTestResponseSchema, status_code=202)
async def create_payment_load_test(
    request: PaymentLoadTestRequestSchema,
    background_tasks: BackgroundTasks,
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    job_id = f"payment-load-test-{uuid.uuid4().hex[:12]}"

    command = GeneratePaymentLoadCommand(
        num_requests=request.num_requests,
        user_id=request.user_id,
        account_id=request.account_id
    )

    background_tasks.add_task(execute_load_test, job_id, command, token, db)

    logger.info(f"Created job {job_id} for {request.num_requests} payment requests")

    return PaymentLoadTestResponseSchema(
        job_id=job_id,
        status="started",
        message=f"Payment load test job started with {request.num_requests} requests",
        total_requests=request.num_requests
    )

async def execute_load_test(
    job_id: str,
    command: GeneratePaymentLoadCommand,
    token: str,
    db: Session
):
    try:
        logger.info(f"Job {job_id}: Starting execution")
        job_results[job_id] = {"status": "running", "started_at": datetime.now().isoformat() }

        handler = PaymentLoadTestHandler()

        await handler.handle_generate_load(command, token, db)
    except Exception as e:
        logger.error(f"Job {job_id}: Failed with error: {str(e)}")
        job_results[job_id] = {
            "status": "failed",
            "started_at": job_results[job_id].get("started_at"),
            "completed_at": datetime.now().isoformat(),
            "error": str(e)
        }
    finally:
        db.close()

@router.get("/payment-load-test/{job_id}", response_model=dict)
async def get_payment_load_test_status(job_id: str, token: str = Depends(get_token)):
    if job_id not in job_results:
        return {
            "job_id": job_id,
            "status": "not found",
            "message": "Job not found"
        }
    
    job_data = job_results[job_id]
    response = {
        "job_id": job_id,
        "status": job_data["status"],
        "started_at": job_data.get("started_at")
    }

    if job_data["status"] == "completed":
        response["completed_at"] = job_data.get("completed_at")
        response["result"] = job_data.get("result")
    elif job_data["status"] == "failed":
        response["completed_at"] = job_data.get("completed_at")
        response["error"] = job_data.get("error")
    
    return response
