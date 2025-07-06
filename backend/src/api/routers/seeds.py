from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import (
        select,
        func
)
from src.schemas import (
    ComputerComponentAsParams,
    ComputerComponentAsResponse,
    ComputerComponentAsListResponse
)
from src.models import (
    PaymentMethod,
    ComputerComponent,
    ComputerComponentCategory,
    User
)
import logging
import faker
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db

router = APIRouter(
    prefix='/api/seeds'
)

@router.post('/')
def seeds_categories(db: Session = Depends(get_db)):
    try:
        fake = faker.Faker()
        if db.query(ComputerComponentCategory).first():
            return { 'message': 'Data is exist, returning' }

        default_status = 0
        default_time_now = func.now()

        # ---- seed categories -------------------------------------------------
        category_names = [
            "Laptops",
            "Macs",
            "Monitors",
            "Processors",
            "Graphics",
            "RAMs",
            "Motherboards",
            "Others",
        ]

        categories = [
            ComputerComponentCategory(
                name=name,
                status=default_status,
                created_at=default_time_now,
                updated_at=default_time_now,
            )
            for name in category_names
        ]

        # ---- seed payment methods --------------------------------------------
        payment_method_names = [
            "BBB Virtual Account",
            "BBB Bank Transfer",
            "BBB PayLater",
            "BBB CreditCard",
        ]

        payment_methods = [PaymentMethod(name=n) for n in payment_method_names]

        # ---- seeds users -----------------------------------------------------
        users = [User(fullname=fake.first_name()) for _ in range(100)] + [User(fullname="Seller")]

        # --- one round‑trip to the DB ----------------------------------------
        db.add_all(categories + payment_methods + users)
        db.commit()

        
        return { 'message': 'Seeding completed'}
    finally:
        db.close()