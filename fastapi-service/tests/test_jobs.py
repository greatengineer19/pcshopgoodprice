import pytest
from tests.factories.user_factory import UserFactory
from tests.factories.account_factory import AccountFactory
from tests.factories.payment_factory import PaymentFactory
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
from src.api.schemas.payment_schemas import PaymentRequestSchema
from src.api.routers.jobs import execute_load_test
from src.domain.payment.commands.generate_payment_load_command import GeneratePaymentLoadCommand
from src.domain.payment.handlers.payment_load_test_handler import PaymentLoadTestHandler
import asyncio

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

@pytest.fixture
def payment_request_json(user_sean_ali, account_0):
    return {
        "user_id": user_sean_ali.id,
        "account_id": account_0.id,
        "num_requests": 10
    }

@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock)
def test_write_request(
    mock_journal,
    mock_user,
    client,
    db_session,
    fetch_token_sean_ali,
    payment_request_json):
    db_session.commit()

    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }
    response = client.post("/api/jobs/payment-load-test", headers=headers, json=payment_request_json)
    response_body = response.json()

    assert list(response_body.keys()) == ['job_id', 'status', 'message', 'total_requests']
    assert response.status_code == 202

    assert mock_journal.call_count == 10
    assert mock_user.call_count == 10
    assert db_session.query(Payment).count() == 10

@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock)
@patch('src.api.routers.jobs.execute_load_test')
def test_api_load_test(
    mock_execute_load_test,
    mock_sales_journal,
    mock_user,
    client,
    db_session,
    fetch_token_sean_ali,
    payment_request_json,
    user_sean_ali,
    account_0):
    db_session.commit()

    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }
    response = client.post(
        "/api/jobs/payment-load-test",
        headers=headers,
        json=payment_request_json
    )
    assert response.status_code == 202
    response_body = response.json()
    mock_execute_load_test.assert_called_once()

    # Verify correct arguments passed
    call_args = mock_execute_load_test.call_args
    job_id, command, token, db = call_args[0]
    
    assert job_id.startswith("payment-load-test-")
    assert isinstance(command, GeneratePaymentLoadCommand)
    assert command.num_requests == 10

    assert mock_sales_journal.call_count == 0
    assert mock_user.call_count == 0
    assert db_session.query(Payment).count() == 0
    
@patch.object(PaymentCommandHandler, 'handle_process_payment', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_payment_n_times(
    mock_process_payment,
    db_session,
    user_sean_ali,
    account_0,
    fetch_token_sean_ali
):
    db_session.commit()
    # Setup
    command = GeneratePaymentLoadCommand(
        num_requests=10,
        user_id=user_sean_ali.id,
        account_id=account_0.id
    )

    handler = PaymentLoadTestHandler()

    await handler.handle_generate_load(command, fetch_token_sean_ali, db_session)
    assert mock_process_payment.call_count == 10

    for call_args in mock_process_payment.call_args_list:
        payment_cmd, call_token, call_db = call_args[0]
        assert isinstance(payment_cmd, ProcessPaymentCommand)
        assert call_token == fetch_token_sean_ali
        assert call_db == db_session    

@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_handle_create_journal(
    mock_journal,
    mock_user,
    db_session,
    user_sean_ali,
    account_0,
    fetch_token_sean_ali
):
    db_session.commit()
    command = ProcessPaymentCommand(
        user_id=user_sean_ali.id,
        debit_account_id=account_0.id,
        amount=Decimal("1000000.0"),
        currency="IDR",
        payment_method="cash"
    )

    handler = PaymentCommandHandler()
    await handler.handle_process_payment(command, fetch_token_sean_ali, db_session)

    mock_user.assert_called_once()
    mock_journal.assert_called_once()
