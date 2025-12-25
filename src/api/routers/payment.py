from fastapi import APIRouter, Depends, BackgroundTasks
from ..schemas.payment_schemas import PaymentRequestSchema, PaymentResponseSchema
from src.domain.payment.commands.process_payment_command import ProcessPaymentCommand
from src.domain.payment.handlers.payment_command_handler import PaymentCommandHandler
from src.api.dependencies.token_fetcher import get_token
from sqlalchemy.orm import Session
from src.api.session_db import get_db
from src.domain.payment.value_objects.currency import CurrencyEnum
from src.domain.payment.value_objects.payment_method import PaymentMethod

router = APIRouter(prefix='/api/payments', tags=['payments'])

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