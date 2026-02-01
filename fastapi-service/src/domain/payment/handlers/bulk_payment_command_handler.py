import asyncio
import httpx
import logging
from fastapi import HTTPException
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

    async def handle_bulk_payments(
        self,
        commands: list[ProcessPaymentCommand],
        token: str,
        db: Session
    ) -> str:
        # Batch validate users (using a cache to avoid redundant hits)
        user_cache = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = []
            for command in commands:
                tasks.append(self._process_single_payment(command, token, client, user_cache))
            
            # Run all payments concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for errors
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Error in batch payment: {result}")
                    raise result

        return 'Bulk payments processed successfully'

    async def _process_single_payment(
        self,
        command: ProcessPaymentCommand,
        token: str,
        client: httpx.AsyncClient,
        user_cache: dict
    ):
        await self._validate_user_async(command.user_id, token, client, user_cache)
        await self._create_payment_async(command, token, client)

    async def _validate_user_async(self, user_id: int, token: str, client: httpx.AsyncClient, user_cache: dict):
        """Validate user exists with caching"""
        if user_id in user_cache:
            if not user_cache[user_id]:
                raise HTTPException(status_code=404, detail="User not found")
            return

        try:
            response = await client.get(
                f"http://rails:3000/rails/api/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                user_cache[user_id] = False
                raise HTTPException(status_code=404, detail="User not found")
            
            user_cache[user_id] = True
        except httpx.RequestError as e:
            logging.error(f"Network error validating user {user_id}: {e}")
            raise HTTPException(status_code=503, detail="User validation service unavailable")

    async def _create_payment_async(self, command: ProcessPaymentCommand, token: str, client: httpx.AsyncClient):
        try:
            response = await client.post(
                f"http://rails:3000/rails/api/payments",
                json={
                    "user_id": command.user_id,
                    "request_uuid": command.request_uuid,
                    "debit_account_id": command.debit_account_id,
                    "account_id": command.debit_account_id,
                    "amount": command.amount,
                    "currency": command.currency,
                    "payment_method": command.payment_method,
                    "fastapi_last_iter": command.fastapi_last_iter
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error for payment: {e.response.text}")
            raise HTTPException(status_code=500, detail="Failed to create payment")
        except Exception as e:
            logging.error(f"Unexpected error creating payment: {e}")
            raise HTTPException(status_code=500, detail="Internal server error in payment handling")

    def _create_bulk_payment(
        self,
        command: ProcessPaymentCommand,
        token: str,
        db: Session
    ) -> str:
        # Keep old method for backward compatibility if needed, but warn it's slow
        # or refactor it to call the async version in a loop (still slow)
        return asyncio.run(self.handle_bulk_payments([command], token, db))