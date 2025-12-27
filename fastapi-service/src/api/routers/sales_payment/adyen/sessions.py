import Adyen
import json
import uuid
from fastapi import APIRouter, Request, Depends
from config import setting
import logging
from src.schemas import AdyenSessionResponse
from src.schemas import SessionParams
from sqlalchemy.orm import joinedload, Session
from src.api.session_db import get_db
from src.models import SalesQuote

router = APIRouter(
    prefix='/api/sales-payment/adyen'
)

@router.post("/sessions-credit-card", response_model=AdyenSessionResponse, status_code=200)
def sessions(params: SessionParams, request: Request, db: Session = Depends(get_db)):
    try:
        host_url = request.headers.get('origin')

        sales_quote = db.query(SalesQuote).filter(SalesQuote.id == params.id).first()
        adyen = Adyen.Adyen()
        adyen.payment.client.xapikey = setting.ADYEN_API_KEY
        adyen.payment.client.platform = "test"
        adyen.payment.client.merchant_account = setting.ADYEN_MERCHANT_ACCOUNT

        request_body = {
            'amount': {"value": str(int(sales_quote.total_payable_amount)), "currency": "IDR"},
            'reference': f"Reference {uuid.uuid4()}",
            'returnUrl': f"{host_url}/orders",
            'countryCode': "ID",
            'lineItems': [],
            'mode': 'hosted',
            'themeId': 'e3ef2338-aed4-42df-b1c0-542864b786d4',
            'merchantAccount': setting.ADYEN_MERCHANT_ACCOUNT
        }
        result = adyen.checkout.payments_api.sessions(request_body)

        response_data = json.loads(result.raw_response)
        response_data['pay_link'] = f"https://checkoutshopper-test.adyen.com/checkoutshopper/v1/sessions/{response_data['id']}/payments?clientKey={setting.ADYEN_CLIENT_KEY}"
        response_data['sales_quote_no'] = sales_quote.sales_quote_no
        response_data['sales_quote_id'] = sales_quote.id

        sales_quote.credit_card_bank_name = request_body['reference']
        db.add(sales_quote)
        db.commit()

        session_response = AdyenSessionResponse(**response_data)
        return session_response
    except Exception as e:
        logging.error(f" An error occured in sessions: {e}")
        raise
    finally:
        db.close()