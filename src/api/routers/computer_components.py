from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import (
        select,
        func,
        delete
)
from src.schemas import (
    ComputerComponentAsParams,
    ComputerComponentAsResponse,
    ComputerComponentAsListResponse,
    DayTypeEnum
)
from src.models import (
    ComputerComponent,
    ComputerComponentCategory,
    ComputerComponentReview,
    ComputerComponentSellPriceSetting,
    User,
    Inventory,
    CartLine,
    PurchaseInvoiceLine,
    SalesQuoteLine,
    SalesDeliveryLine,
    SalesInvoiceLine,
    InboundDeliveryLine
)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.session_db import get_db
from src.data.review_schema import component_reviews_hash_map
import random

router = APIRouter(
    prefix='/api/computer-components'
)

@router.get("", response_model=ComputerComponentAsListResponse)
def index(db: Session = Depends(get_db)):
    try:
        components = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.component_category), joinedload(ComputerComponent.computer_component_sell_price_settings))
            .order_by(ComputerComponent.name).all()
        )

        if not components:
            return { 'computer_components': [] }
        
        response_components = []
        for component in components:
            images = []
            if component.images:
                presigned_url = s3_client().generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name(), 'Key': component.images[0]},
                    ExpiresIn=3600
                )
                images = [presigned_url]

            response_components.append(
                ComputerComponentAsResponse(
                    id=component.id,
                    name=component.name,
                    product_code=component.product_code,
                    component_category_name=getattr(component.component_category, 'name', None),
                    component_category_id=component.component_category_id,
                    computer_component_sell_price_settings=component.computer_component_sell_price_settings,
                    images=images,
                    description=component.description,
                    status=component.status,
                    created_at=component.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    updated_at=component.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                )
            )

        return { 'computer_components': response_components }
    finally:
        db.close()

@router.get("/{id}", response_model=ComputerComponentAsResponse)
def show(id: int, db: Session = Depends(get_db)):
    try:
        computer_component = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings), joinedload(ComputerComponent.component_category))
            .filter(ComputerComponent.id == id)
            .first()
        )
        if computer_component is None:
            raise HTTPException(status_code=404, detail="Computer not found")
        
        computer_component.component_category_name = computer_component.component_category.name

        sell_price_settings = computer_component.computer_component_sell_price_settings
        sorted_sell_price_settings = sorted(
            sell_price_settings,
            key=lambda setting: setting.day_type
        )
        computer_component.computer_component_sell_price_settings = sorted_sell_price_settings

        return computer_component
    finally:
        db.close()

@router.post("", response_model=ComputerComponentAsResponse)
def create(params: ComputerComponentAsParams, db: Session = Depends(get_db)):
    try:
        category = (
                    db.query(ComputerComponentCategory)
                        .filter(ComputerComponentCategory.name == params.component_category_name)
                        .first()
                   )
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

        images = []
        if params.images:
            images = params.images

        computer_component = ComputerComponent(
            name=params.name,
            product_code=params.product_code,
            images=images,
            description=params.description,
            component_category_id=category.id,
            status=params.status
        )

        db.add(computer_component)
        db.commit()

        price_settings = []
        for price_setting_params in params.computer_component_sell_price_settings_attributes:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = computer_component.id,
                    day_type=price_setting_params.day_type,
                    price_per_unit=price_setting_params.price_per_unit,
                    active=price_setting_params.active
                )
            )

        users = db.query(User.id, User.fullname).filter(User.role != 0).all()

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=computer_component.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()
        
        computer_component = (
            db.query(ComputerComponent)
              .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
              .filter(ComputerComponent.id == computer_component.id)
              .first()
        )

        return computer_component
    except Exception as e:
        db.rollback()
        logging.error(f"An error occurred: {e}")
        raise
    finally:
        db.close()

@router.patch("/{id}", response_model=ComputerComponentAsResponse)
def update(params: ComputerComponentAsParams, db: Session = Depends(get_db)):
    try:
        computer_component = db.query(ComputerComponent).filter(ComputerComponent.id == params.id).first()
        category = (
                    db.query(ComputerComponentCategory)
                        .filter(ComputerComponentCategory.name == params.component_category_name)
                        .first()
                   )
                   
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        elif computer_component is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update only provided fields
        update_fields = [
            'name', 'product_code',
            'description', 'status'
        ]
        
        for field in update_fields:
            value = getattr(params, field, None)
            if value is not None:
                setattr(computer_component, field, value)

        computer_component.component_category_id = category.id
        if params.images:
            computer_component.images = params.images

        computer_component.updated_at = func.now()

        component_sell_price_settings = { line.id: line for line in computer_component.computer_component_sell_price_settings }

        for price_setting_params in params.computer_component_sell_price_settings_attributes:
            if price_setting_params.id:
                price_setting_object = component_sell_price_settings[price_setting_params.id]
                price_setting_object.price_per_unit = price_setting_params.price_per_unit
                price_setting_object.active = price_setting_params.active

        db.commit()
        
        computer_component = (
            db.query(ComputerComponent)
              .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
              .filter(ComputerComponent.id == computer_component.id)
              .first()
        )

        return computer_component
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

@router.delete("/{id}", status_code=204)
def destroy(id: int, db: Session = Depends(get_db)):
    db_computer_component = db.query(ComputerComponent).filter(ComputerComponent.id == id).first()

    # Check if it exists
    if not db_computer_component:
        raise HTTPException(status_code=404, detail="Data not found")
    
    for model in [Inventory,
     CartLine,
     PurchaseInvoiceLine,
     SalesQuoteLine,
     SalesDeliveryLine,
     SalesInvoiceLine,
     InboundDeliveryLine]:
        check_model = db.query(func.count(model.id)).filter(model.component_id == db_computer_component.id).scalar()
        if check_model > 0:
            raise HTTPException(status_code=422, detail="Association is exist, unable to delete")

    db.delete(db_computer_component)
    db.commit()

    return { "message": "Data deleted successfully" }
