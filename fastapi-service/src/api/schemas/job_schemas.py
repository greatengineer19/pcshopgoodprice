from pydantic import BaseModel, Field
from typing import List, Optional

class PaymentLoadTestRequestSchema(BaseModel):
    num_requests: int = Field(default=10000, gt=0, le=100000, description="Number of payment requests to generate")
    user_id: int = Field(default=1, gt=0, description="User ID for test payments")
    account_id: int = Field(default=1, gt=0, description="Account ID for test payments")

    class Config:
        json_schema_extra = {
            "example": {
                "num_requests": 10000,
                "user_id": 1,
                "account_id": 1
            }
        }

class PaymentLoadTestResponseSchema(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status (started, running, completed, failed)")
    message: str = Field(..., description="Status message")
    total_requests: Optional[int] = Field(None, description="Total number of requests to be executed")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "payment-load-test-1234567890",
                "status": "started",
                "message": "Payment load test job started with 10000 requests",
                "total_requests": 10000
            }
        }
