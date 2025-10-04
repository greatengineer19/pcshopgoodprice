import Adyen
import json
import uuid
from fastapi import APIRouter, Request, Depends
from Adyen.util import is_valid_hmac_notification
from config import setting
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from src.sales_invoices.show_service import ShowService
from src.sales_invoices.build_service import BuildService
from src.models import ( SalesInvoice, SalesInvoiceLine, User, SalesQuote, SalesQuoteLine, SalesDelivery )
from sqlalchemy import ( desc, and_, func )

router = APIRouter(
    prefix='/api/sales-payment/adyen'
)

# [{'NotificationRequestItem': {'additionalData': {'expiryDate': '03/2030', 'authCode': '086719', 'paymentLinkId': 'CS6549238AE99D7723FFE021E', 'cardSummary': '0005', 'isCardCommercial': 'unknown', 'threeds2.cardEnrolled': 'false', 'paymentMethod': 'mc', 'networkTxReference': '8SO3ZAZ7B1004', 'checkout.cardAddedBrand': 'mccommercialdebit', 'hmacSignature': 'J3d+dUm8buYQzMFBrmjiK2oXY7TSS1byjSDbP99iQSQ='}, 'amount': {'currency': 'IDR', 'value': 1955000}, 'eventCode': 'AUTHORISATION', 'eventDate': '2025-10-04T05:36:58+02:00', 'merchantAccountCode': 'RunchiseECOM', 'merchantReference': 'Reference 34b5a2c7-8fb5-4905-a141-ac0dbe416c71', 'operations': ['CANCEL', 'CAPTURE', 'REFUND'], 'paymentMethod': 'mc', 'pspReference': 'M6326G3LVW37WW65', 'reason': '086719:0005:03/2030', 'success': 'true'}}]
@router.post("/webhooks/notifications", status_code=202)
async def webhook_notifications(request: Request, db: Session = Depends(get_db)):
    try:
        raw_body = await request.body()
        request_body = json.loads(raw_body.decode())
        notifications = request_body['notificationItems']
        notification = notifications[0]

        print("<<< webhooked from adyen")
        print(notifications)
        if is_valid_hmac_notification(notification['NotificationRequestItem'], setting.ADYEN_HMAC_KEY):
            consume_event(notification)
        else:
            raise Exception("Invalid HMAC signature")
        
        sales_quote = db.query(SalesQuote).filter(SalesQuote.credit_card_bank_name == notification['NotificationRequestItem']['merchantReference']).first()
        if not sales_quote:
            return

        sales_quote_no = sales_quote.sales_quote_no
        sales_quote_id = sales_quote.id
        user = db.query(User).filter(User.id == sales_quote.customer_id).first()

        show_service = ShowService(db=db, sales_quote_no=sales_quote_no, sales_invoice_id=None, user_id=user.id)
        existing = show_service.call()
        if existing:
            return existing

        build_service = BuildService(db, sales_quote_id, user)
        sales_invoice = build_service.build()

        delete_query = SalesQuoteLine.__table__.delete().where(and_(SalesQuoteLine.sales_quote_id == sales_quote_id))
        db.execute(delete_query)

        delete_query = SalesQuote.__table__.delete().where(and_(SalesQuote.id == sales_quote_id, SalesQuote.customer_id == user.id))
        db.execute(delete_query)
        db.add(sales_invoice)
        db.commit()
        
        return '', 202
    finally:
        db.close()

def consume_event(notification):
    print(f"consume_event merchantReference: {notification['NotificationRequestItem']['merchantReference']} "
          f"result? {notification['NotificationRequestItem']['success']}")