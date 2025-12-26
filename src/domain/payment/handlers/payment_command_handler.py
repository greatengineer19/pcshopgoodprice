from datetime import datetime
from fastapi import BackgroundTasks, Depends, HTTPException, Depends
import logging
import httpx
from ..commands.process_payment_command import ProcessPaymentCommand
from src.domain.payment.entities.payment_transaction import PaymentTransaction
from src.domain.payment.value_objects.payment_amount import PaymentAmount
from src.domain.payment.value_objects.currency import CurrencyEnum
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.api.session_db import AsyncDbSession
from src.infrastructure.persistence.models.payment import Payment
from sqlalchemy.orm import Session

class PaymentCommandHandler:
    def __init__(self):
        pass

    async def handle_process_payment(
        self,
        command: ProcessPaymentCommand,
        token: str,
        db: Session
    ) -> PaymentTransaction:
        await self._validate_user(command.user_id)
    
        try:
            payment = PaymentTransaction(
                id=None,
                user_id=command.user_id,
                debit_account_id=command.debit_account_id,
                amount=PaymentAmount(
                    amount=command.amount,
                    currency=CurrencyEnum.from_value(command.currency)
                ),
                payment_method=PaymentMethod.from_value(command.payment_method),
                status="pending",
                transaction_id=None,
                description=command.description,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            payment_model = Payment(
                user_id=payment.user_id,
                debit_account_id=payment.debit_account_id,
                amount=payment.amount.amount,
                currency=payment.amount.currency.value,
                payment_method=payment.payment_method.value,
                account_id=payment.debit_account_id
            )

            db.add(payment_model)
            response = await self._create_sales_journal(payment_model, token)
            # TODO: Need to check whether it is possible to query the payment in the Ruby on Rails
            db.commit()

            return payment_model
        except Exception as e:
            db.rollback()
            raise e
    
    async def _validate_user(self, user_id: int):
        return
        """Validate user exists"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://basic-service:3001/api/users/{user_id}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")

    async def _create_sales_journal(self, payment: PaymentTransaction, token: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"http://basic-service:3001/api/sales-journal",
                    json={
                        "payment_id": payment.id
                    },
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
        except httpx.ConnectError:
            logging.error(f"Failed to connect to basic-service:3001 for sales journal.")
            raise HTTPException(status_code=503, detail="Sales journal service is unavailable")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error for sales journal: {e.response.text}")
            raise HTTPException(status_code=500, detail="Failed to create sales journal")
        except Exception as e:
            logging.error(f"Unexpected error creating sales journal: {e}")
            raise HTTPException(status_code=500, detail="Internal server error in payment handling")