from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import (
        select,
        func,
        delete,
        text,
        and_,
        or_
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
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from src.data.review_schema import component_reviews_hash_map
import random
from datetime import datetime
from sqlalchemy.sql.expression import case
from utils.auth import get_current_user

router = APIRouter(
    prefix='/api/cart'
)
  
@router.get("", response_model=CartLinesResponse)
def index(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        cart_lines = (
            db.query(
                CartLine.id,
                CartLine.status,
                CartLine.customer_id,
                CartLine.component_id,
                ComputerComponent.name.label('component_name'),
                User.fullname.label('customer_name'),
                CartLine.quantity,
                CartLine.created_at,
                CartLine.updated_at
              )
              .join(CartLine.component)
              .join(CartLine.customer)
              .filter(CartLine.customer_id == user.id)
              .order_by(CartLine.id)
              .all()
        )

        if cart_lines is None:
            return { 'cart': [] }
        
        components = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
            .filter(ComputerComponent.id.in_([p.component_id for p in cart_lines]))
        )
        components_dict = { component.id: component for component in components}
        weekday = datetime.now().isoweekday() or 7  # Returns 1-7 (Mon-Sun)

        for cart_line in cart_lines:
            component = components_dict[cart_line.component_id]
            price_settings = component.computer_component_sell_price_settings

            default_price = next((sps.price_per_unit for sps in price_settings if sps.day_type == 0), 0)
            price = next(
                (sps.price_per_unit for sps in price_settings 
                if sps.day_type == weekday and sps.status == 0),
                default_price
            )

            cart_line.sell_price = price


        return { 'cart': cart_lines }
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