import asyncio
import logging
import time
from typing import Dict, Any
from decimal import Decimal
from ..commands.generate_payment_load_command import GeneratePaymentLoadCommand
from ..commands.process_payment_command import ProcessPaymentCommand
from .payment_command_handler import PaymentCommandHandler
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PaymentLoadTestHandler:
    def __init__(self):
        self.payment_handler = PaymentCommandHandler()

    async def handle_generate_load(
        self,
        command: GeneratePaymentLoadCommand,
        token: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Execute payment load test asynchronously

        Args:
            command: Load test configuration
            token: Authentication token
            db: Database session

        Returns:
            Dictionary with execution statistics
        """
        logger.info(f"Starting payment load test: {command.num_requests} requests")

        start_time = time.time()
        success_count = 0
        failure_count = 0
        errors = []

        payment_command = ProcessPaymentCommand(
            user_id=command.user_id,
            debit_account_id=command.account_id,
            amount=Decimal("100.00"),
            currency="EUR",
            payment_method="CASH",
            description="Load test payment"
        )

        # Execute requests sequentially (async but not parallel)
        # For true parallel execution, we could use asyncio.gather with batching
        for i in range(command.num_requests):
            try:
                await self.payment_handler.handle_process_payment(
                    payment_command,
                    token,
                    db
                )

                success_count += 1
                if (i + 1) % 1000 == 0:
                    logger.info(f"Progress: {i + 1}/{command.num_requests} requests completed")
            except Exception as e:
                failure_count += 1
                error_msg = f"Request {i + 1} failed: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

                if len(errors) > 100:
                    errors.pop(0)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_request = total_time / command.num_requests if command.num_requests > 0 else 0

        result = {
            "total_requests": command.num_requests,
            "successful": success_count,
            "failed": failure_count,
            "total_time_seconds": round(total_time, 2),
            "avg_time_per_request_ms": round(avg_time_per_request * 1000, 2),
            "requests_per_second": round(command.num_requests / total_time, 2) if total_time > 0 else 0,
            "recent_errors": errors[-10:] if errors else []
        }

        logger.info(f"Load test completed: {result}")
        print(f"Load test completed: {result}")
        return result
