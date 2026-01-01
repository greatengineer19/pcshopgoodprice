import pytest
from tests.factories.user_factory import UserFactory
from tests.factories.account_factory import AccountFactory
from tests.conftest import (
    client, db_session, setup_factories,
    user_sean_ali,
    component_category_gpu
)
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user
from src.domain.payment.commands.process_payment_command import ProcessPaymentCommand
from decimal import Decimal
from src.domain.payment.handlers.payment_command_handler import PaymentCommandHandler
from unittest.mock import AsyncMock, patch
import httpx
from src.infrastructure.persistence.models.payment import Payment
from fastapi import HTTPException

@pytest.fixture
def fetch_token_sean_ali(user_sean_ali):
    return create_access_token(user_sean_ali.id, 30)

@pytest.fixture
def account_0(db_session):
    account = AccountFactory(
        account_code=200,
        account_name="Cash",
        account_type=0,
        subtype=0,
        parent_id=None,
        normal_balance=0,
        is_active=True,
        tax_code_id=None
    )

    db_session.add(account)
    db_session.commit()

    return account

@pytest.fixture
def mock_process_payment_command(user_sean_ali, account_0):
    return ProcessPaymentCommand(
        user_id=user_sean_ali.id,
        debit_account_id=account_0.id,
        amount=Decimal("1000000.0"),
        currency="IDR",
        payment_method="cash"
    )

@pytest.mark.asyncio
async def test_create_payment(
    client,
    db_session,
    fetch_token_sean_ali,
    mock_process_payment_command):
    db_session.commit()

    with patch.object(
        PaymentCommandHandler,
        '_create_sales_journal',
        new_callable=AsyncMock
    ) as mock_journal:
        response = await PaymentCommandHandler().handle_process_payment(
                        mock_process_payment_command,
                        fetch_token_sean_ali,
                        db_session)
        assert mock_journal.called
        assert mock_journal.call_count == 1

@pytest.mark.asyncio
async def test_create_payment_journal_fails(
    client,
    db_session,
    fetch_token_sean_ali,
    mock_process_payment_command
):
    db_session.commit()

    with patch.object(
        PaymentCommandHandler,
        '_create_sales_journal',
        new_callable=AsyncMock,
        side_effect=httpx.HTTPError("Journal service unavailable")
    ) as mock_journal:
        with pytest.raises(HTTPException):
            await PaymentCommandHandler().handle_process_payment(
                mock_process_payment_command,
                fetch_token_sean_ali,
                db_session
            )

        assert mock_journal.called

@pytest.mark.asyncio
async def test_create_payment_network_timeout(
    client,
    db_session,
    fetch_token_sean_ali,
    mock_process_payment_command
):
    db_session.commit()
    initial_count = db_session.query(Payment).count()

    assert initial_count == 0

    with patch.object(
        PaymentCommandHandler,
        '_create_sales_journal',
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Request timeout")
    ) as mock_journal:
        with pytest.raises(HTTPException):
            await PaymentCommandHandler().handle_process_payment(
                mock_process_payment_command,
                fetch_token_sean_ali,
                db_session
            )
            

    final_count = db_session.query(Payment).count()
    assert final_count == initial_count