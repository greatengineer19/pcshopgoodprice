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

class BulkPaymentCommandHandler:
    def __init__(self):
        pass

    def _create_bulk_payment(
        self,
        command: ProcessPaymentCommand,
        token: str,
        db: Session
    ) -> str:
        self._validate_user(command.user_id, token)
    
        try:
            self._create_payment(command, token)

            return 'Payment is created successfully'
        except HTTPException as e:
            raise HTTPException(
                status_code=424,
                detail=f"Failed to create payment: {e.detail}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create payment: {str(e)}"
            )
    
    def _validate_user(self, user_id: int, token: str):
        """Validate user exists"""
        with httpx.Client() as client:
            response = client.get(
                f"http://rails:3000/rails/api/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")

    def _create_payment(self, command: ProcessPaymentCommand, token: str):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"http://rails:3000/rails/api/payments",
                    json={
                        "user_id": command.user_id,
                        "request_uuid": command.request_uuid,
                        "debit_account_id": command.debit_account_id,
                        "account_id": command.debit_account_id,
                        "amount": command.amount,
                        "currency": command.currency,
                        "payment_method": command.payment_method
                    },
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                response.raise_for_status()
        except httpx.ConnectError:
            logging.error(f"Failed to connect to rails:3000 for payment.")
            raise HTTPException(status_code=503, detail="payment service is unavailable")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error for payment: {e.response.text}")
            raise HTTPException(status_code=500, detail="Failed to create payment")
        except Exception as e:
            logging.error(f"Unexpected error creating payment: {e}")
            raise HTTPException(status_code=500, detail="Internal server error in payment handling")