from fastapi import APIRouter, Depends, BackgroundTasks, Query
from ..schemas.payment_schemas import PaymentRequestSchema, PaymentResponseSchema
from src.domain.payment.commands.process_payment_command import ProcessPaymentCommand
from src.domain.payment.handlers.payment_command_handler import PaymentCommandHandler
from src.api.dependencies.token_fetcher import get_token
from sqlalchemy.orm import Session
from src.api.session_db import get_db
from src.domain.payment.value_objects.currency import CurrencyEnum
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.entities.payment_index import PaymentIndex
from src.payments.filter_service import FilterService
import logging
from fastapi import HTTPException

router = APIRouter(prefix='/api/payments', tags=['payments'])

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