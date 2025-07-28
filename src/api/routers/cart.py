from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import (
        and_,
)
from src.schemas import (
    CartLinesResponse,
    AddItemToCartParam,
    PaymentMethodList
)
from src.models import (
    CartLine,
    User,
    ComputerComponent,
    PaymentMethod
)
import logging
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from datetime import datetime
from utils.auth import get_current_user
from src.computer_components.service import Service
from src.api.s3_dependencies import ( bucket_name, s3_client )

router = APIRouter(prefix='/api/cart', tags=['Cart'])
  
@router.get("", response_model=CartLinesResponse)
def index(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        cart_lines = (
            db.query(CartLine)
              .filter(CartLine.customer_id == user.id)
              .order_by(CartLine.id)
              .options(joinedload(CartLine.component).subqueryload(ComputerComponent.computer_component_sell_price_settings)) # Eagerly load price settings
              .all()
        )

        if not cart_lines:
            return { 'cart': [] }

        result = []
        service = Service()

        for cart_line in cart_lines:
            component = cart_line.component
            price = service.select_price(component)

            images = []
            if component.images:
                presigned_url = s3_client().generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name(), 'Key': component.images[0]},
                    ExpiresIn=3600
                )
                images = [presigned_url]

            result.append({
                'sell_price': price,
                'id': cart_line.id,
                'customer_id': cart_line.customer_id,
                'component_id': cart_line.component_id,
                'component_name': cart_line.component.name,
                'customer_name': user.fullname,
                'quantity': cart_line.quantity,
                'images': images,
                'created_at': cart_line.created_at,
                'updated_at': cart_line.updated_at,
                'status': cart_line.status
            })

        return { 'cart': result }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/add-item", status_code=200)
def post_item_to_cart(
    param: AddItemToCartParam,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    new_cart_line = db.query(CartLine).filter(and_(CartLine.customer_id == user.id, CartLine.component_id == param.component_id)).first()
    if new_cart_line:
        new_cart_line.quantity += param.quantity
    else:
        new_cart_line = CartLine(
            component_id=param.component_id,
            quantity=param.quantity,
            customer_id=user.id,
            status=0
        )

    db.add(new_cart_line)
    db.commit()    

    return 'ok'

@router.delete("/remove-item/{id}", status_code=204)
def remove_item_from_cart(id: int,
                          user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    cart_line = db.query(CartLine).filter(and_(CartLine.id == id, CartLine.customer_id == user.id)).first()
    if cart_line:
        db.delete(cart_line)
        db.commit()

    return "ok"

@router.get("/payment-methods", response_model=PaymentMethodList)
def list_payment_methods(db: Session = Depends(get_db)):
    payment_methods = (
            db.query(
                PaymentMethod.id,
                PaymentMethod.name
              )
              .order_by(PaymentMethod.name)
              .all()
        )

    return { 'payment_methods': payment_methods }