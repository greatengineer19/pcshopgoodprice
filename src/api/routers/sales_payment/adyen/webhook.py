import Adyen
import json
import uuid
from fastapi import APIRouter, Request
from Adyen.util import is_valid_hmac_notification
from config import setting

router = APIRouter(
    prefix='/api/sales-payment/adyen'
)

@router.post("/webhooks/notifications", status_code=200)
def webhook_notifications(request: Request):
    print("<<< raw request")
    print(request)

    notifications = request.json['notificationItems']
    notification = notifications[0]

    print("<<<")
    print(request)
    if is_valid_hmac_notification(notification['NotificationRequestItem'], setting.ADYEN_HMAC_KEY):
        consume_event(notification)
    else:
        raise Exception("Invalid HMAC signature")
    
    return '', 202

def consume_event(notification):
    print(f"consume_event merchantReference: {notification['NotificationRequestItem']['merchantReference']} "
          f"result? {notification['NotificationRequestItem']['success']}")