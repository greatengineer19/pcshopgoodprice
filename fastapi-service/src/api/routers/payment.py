from fastapi import APIRouter, Depends, BackgroundTasks, Query
from ..schemas.payment_schemas import PaymentRequestSchema, PaymentResponseSchema, BulkPaymentRequestSchema
from src.domain.payment.commands.process_payment_command import ProcessPaymentCommand
from src.domain.payment.handlers.payment_command_handler import PaymentCommandHandler
from src.domain.payment.handlers.bulk_payment_command_handler import BulkPaymentCommandHandler
from src.api.dependencies.token_fetcher import get_token
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.api.session_db import get_db
from src.domain.payment.value_objects.currency import CurrencyEnum
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.entities.payment_index import PaymentIndex
from src.payments.filter_service import FilterService
import logging
from fastapi import HTTPException
from celery import Celery
import uuid
import random
from src.models import User, Account
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.infrastructure.persistence.models.import_payment_entry import ImportPaymentEntry
from datetime import datetime
import os

router = APIRouter(prefix='/api/payments', tags=['payments'])
celery = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'))

@celery.task
def process_bulk_payments_task(
        request_uuid: str,
        token: str,
        total_payments: int,
        user_ids: list[int],
        account_ids: list[int]
    ) -> str:

    db = next(get_db())
    entry = ImportPaymentEntry(
                request_uuid=request_uuid,
                total_payments=total_payments,
                start_time=datetime.now(),
                end_time=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
    try:
        payment_methods = [e.name.lower() for e in PaymentMethod]
        print(f"Total payments to create: {total_payments}")
        print(f"User IDs: {user_ids}")
        print(f"Account IDs: {account_ids}")

        # Add validation
        if not user_ids:
            raise ValueError("user_ids list is empty")
        if not account_ids:
            raise ValueError("account_ids list is empty")

        db.add(entry)
        db.commit()
        
        print("Starting payment creation...")
        commands = []
        for i_range in range(total_payments):
            user_id = random.choice(user_ids)
            account_id = random.choice(account_ids)
            amount = random.randint(100, 999)
            currency = 'idr'
            payment_method = random.choice(payment_methods)

            command = ProcessPaymentCommand(
                user_id=user_id,
                debit_account_id=account_id,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                request_uuid=request_uuid,
                fastapi_last_iter= i_range == total_payments - 1
            )
            commands.append(command)

        import asyncio
        asyncio.run(
            BulkPaymentCommandHandler().handle_bulk_payments(
                commands=commands,
                token=token,
                db=db
            )
        )
    
        return 'Done processing bulk payments'
    except Exception as e:
        db.rollback()  # ✅ Rollback on error
        raise
    finally:
        db.close()

@router.post("/bulk_create", status_code=202)
async def create_bulk_payments(
    request: BulkPaymentRequestSchema,
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    request_uuid = str(uuid.uuid4())
    user_ids = db.scalars(select(User.id)).all()
    account_ids = db.scalars(select(Account.id).filter(Account.account_type == 3)).all()
    process_bulk_payments_task.delay(request_uuid, token, request.total_payments, user_ids, account_ids)

    return { "message": "Background job is processed", "status": "accepted" }

@router.get("", response_model=PaymentIndex, status_code=200)
async def index(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
    page: str = Query('1'),
    item_per_page: int = 50
):
    try:
        filter_service = FilterService(db=db,
            page=page,
            item_per_page=item_per_page
        )

        payments = filter_service.call()
    
        return {
            'report_body': generate_response(payments),
            'page': page,
            'item_per_page': item_per_page
        }
    except Exception as e:
        logging.error(f"Failed to load payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def generate_response(payments):
    result = []

    for payment in payments:
        result.append({
            'id': payment.id,
            'debit_account_id': payment.debit_account_id,
            'amount': payment.amount,
            'currency': CurrencyEnum(payment.currency).name,
            'payment_method': PaymentMethod(payment.payment_method).name,
            'created_at': payment.created_at
        })

    return result

@router.post("", response_model=PaymentResponseSchema, status_code=201)
async def create_payment(
    request: PaymentRequestSchema,
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    command = ProcessPaymentCommand(
        user_id=request.user_id,
        debit_account_id=request.account_id,
        amount=request.amount,
        currency=request.currency,
        payment_method=request.payment_method,
        description=request.description
    )

    payment = await PaymentCommandHandler().handle_process_payment(command, token, db)
    return PaymentResponseSchema(
        payment_id=payment.id,
        currency=CurrencyEnum(payment.currency).name,
        payment_method=PaymentMethod(payment.payment_method).name,
        message="Payment is being processed"
    )

@router.get("/{payment_id}")
async def get_payment_status(payment_id: str):
    # TODO
    return {
        "payment_id": payment_id,
        "status": "completed"
    }