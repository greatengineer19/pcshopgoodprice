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
    ComputerComponentSellPriceSetting,
    User,
    ComputerComponentReview
)
import logging
import faker
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.session_db import get_db
import random
from src.data.review_schema import component_reviews_hash_map

router = APIRouter(
    prefix='/api/first-time-seeds'
)

@router.get("", status_code=200)
def seeds(db: Session = Depends(get_db)):
    try:
        if db.query(ComputerComponentCategory).first():
            return { 'message': 'Data is exist, returning' }

        fake = faker.Faker()

        default_status = 0
        default_time_now = func.now()

        # ---- seed categories -------------------------------------------------
        category_names = [
            "Graphic Cards",
            "Processors",
            "Macs",
            "Power Supplies",
            "Cpu Coolers",
            "RAMs",
            "Monitors",
            "Laptops",
            "Motherboards",
            "Others"
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
        buyer_role = 1
        users = [User(fullname=fake.first_name(), role=buyer_role) for _ in range(100)] + [
                    User(fullname="Super Buyer", role=1, username="super_buyer"),
                    User(fullname="Admin Seller", role=0, username="admin_seller")
                ]
        
        # --- one round‑trip to the DB ----------------------------------------
        db.add_all(categories + payment_methods + users)
        db.commit()

        categories = db.query(ComputerComponentCategory).all()
        categories_hash_map = { category.name: category for category in categories }
        
        components = []
        # 01 - GPU 5090
        components.append(ComputerComponent(
            name="ASUS ROG Astral GeForce RTX 5090 32GB GDDR7 OC Edition",
            product_code="GPU_ASUS_RTX_5090",
            images=['e0e33bb9-b3ee-49ca-9ea6-c9a232bdff01_01_gpu_rog_5090.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Graphic Cards'].id
        ))
        # 02 - GPU 5070
        components.append(ComputerComponent(
            name="ASUS ROG Strix GeForce RTX 5070 Ti 16GB GDDR7 OC Edition",
            product_code="GPU_ASUS_RTX_5070",
            images=['87d1e708-0645-45eb-bc6a-ec81115e1722_02_gpu_5070.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Graphic Cards'].id
        ))
        # 03 - Processor U7
        components.append(ComputerComponent(
            name="Intel Core Ultra 7 Processor 265 | Desktop Processor 20 (8P+12E) Cores LGA 1851",
            product_code="PROCESSOR_INTEL_U7",
            images=['d2290782-2b3e-422c-a71f-8105db1bae87_03_processor_intel_u7.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Processors'].id
        ))
        # 04 - Processor U5
        components.append(ComputerComponent(
            name="Intel Core Ultra 5 Processor 235 | Desktop Processor 14 (6P+8E) Cores LGA 1851",
            product_code="PROCESSOR_INTEL_U5",
            images=['bad0fd5c-bd78-44a5-a45f-8ad6e004a356_04_processor_u5.jpg'],
            description="-",
            component_category_id=categories_hash_map['Processors'].id
        ))
        # 05 - PHANTEKS 750W
        components.append(ComputerComponent(
            name="PHANTEKS AMP GH 750W | PSU 8=750W 80+ Gold ATX 3.1 PCIe Gen5.1 Fully Modular - Black",
            product_code="PSU_PHANTEKS_750W",
            images=['19e59f05-f501-4e6f-a25a-e09eb76a58a7_05_power_supply_750w.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Power Supplies'].id
        ))
        # 06 - PHANTEKS 850W
        components.append(ComputerComponent(
            name="PHANTEKS AMP GH 850W | PSU 850W 80+ Gold ATX 3.1 PCIe Gen5.1 Fully Modular - Black",
            product_code="PSU_PHANTEKS_850W",
            images=['37247a3f-7f13-476b-96a7-5005d88bb673_06_power_supply_850_w.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Power Supplies'].id
        ))
        # 07 - LIQUID COOLER ARCTIC
        components.append(ComputerComponent(
            name="ARCTIC Liquid Freezer III Pro 360 A-RGB | Multi Compatible All-in-One CPU Water Cooler with A-RGB - Black",
            product_code="COOLER_ARCTIC_LIQUID_FREEZER",
            images=['59408d0e-97d2-4e16-8edb-c03683ab804e_07_cooler_arctic.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Cpu Coolers'].id
        ))
        # 08 - MSI MAG COOLER
        components.append(ComputerComponent(
            name="MSI MAG CORELIQUID A15 240 | 240mm Liquid CPU Cooler",
            product_code="COOLER_MSI_MAG",
            images=['363bb3b5-4d50-4326-8e7d-d94448827fdf_08_cooler_msi_coreliquid.jpeg'],
            description="-",
            component_category_id=categories_hash_map['Cpu Coolers'].id
        ))
        # 09 - RAM CORSAIR
        components.append(ComputerComponent(
            name="CORSAIR CMK32GX5M2B6000Z30 | VENGEANCE 32GB (2x16GB) DDR5 6000MHz",
            product_code="RAM_CORSAIR_32GB_DDR5",
            images=['4cfff02f-a515-4ab6-86f3-05f4f5a4b393_09_ram_corsair.jpeg'],
            description="-",
            component_category_id=categories_hash_map['RAMs'].id
        ))
        # 10 - RAM KINGBANK
        components.append(ComputerComponent(
            name="KINGBANK FLM5ED9402 | Soarblade RGB 32GB (2x16GB) DDR5 6000MHz",
            product_code="RAM_KINGBANK",
            images=['9c925a35-19ef-4087-ba5a-07b59a1baa32_10_ram_kingbank.jpg'],
            description="-",
            component_category_id=categories_hash_map['RAMs'].id
        ))
        db.add_all(components)
        db.commit()

        users = db.query(User.id, User.fullname).filter(User.role != 0).all()

        # Reviews & Price Settings for 01 GPU RTX 5090
        price_settings = []
        component_01 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "GPU_ASUS_RTX_5090").first()
        component_01_price = 59345000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_01.id,
                    day_type=day_type_int,
                    price_per_unit=component_01_price,
                    active=True
                )
            )
            component_01_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_01.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 02 GPU RTX 5070
        price_settings = []
        component_02 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "GPU_ASUS_RTX_5070").first()
        component_02_price = 21115000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_02.id,
                    day_type=day_type_int,
                    price_per_unit=component_02_price,
                    active=True
                )
            )
            component_02_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_02.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )
        
        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 03 PROCESSOR INTEL U7
        price_settings = []
        component_03 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "PROCESSOR_INTEL_U7").first()
        component_03_price = 6349000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_03.id,
                    day_type=day_type_int,
                    price_per_unit=component_03_price,
                    active=True
                )
            )
            component_03_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_03.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )
        
        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 04 PROCESSOR INTEL U5
        price_settings = []
        component_04 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "PROCESSOR_INTEL_U5").first()
        component_04_price = 4829000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_04.id,
                    day_type=day_type_int,
                    price_per_unit=component_04_price,
                    active=True
                )
            )
            component_04_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_04.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )
        
        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 05 PHANTEKS POWER SUPPLY 750W
        price_settings = []
        component_05 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "PSU_PHANTEKS_750W").first()
        component_05_price = 1499000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_05.id,
                    day_type=day_type_int,
                    price_per_unit=component_05_price,
                    active=True
                )
            )
            component_05_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_05.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 06 PHANTEKS POWER SUPPLY 850W
        price_settings = []
        component_06 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "PSU_PHANTEKS_850W").first()
        component_06_price = 1699000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_06.id,
                    day_type=day_type_int,
                    price_per_unit=component_06_price,
                    active=True
                )
            )
            component_06_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_06.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 07 ARCTIC LIQUID COOLER
        price_settings = []
        component_07 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "COOLER_ARCTIC_LIQUID_FREEZER").first()
        component_07_price = 1949000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_07.id,
                    day_type=day_type_int,
                    price_per_unit=component_07_price,
                    active=True
                )
            )
            component_07_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_07.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 08 MSI MAG LIQUID COOLER
        price_settings = []
        component_08 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "COOLER_MSI_MAG").first()
        component_08_price = 1299000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_08.id,
                    day_type=day_type_int,
                    price_per_unit=component_08_price,
                    active=True
                )
            )
            component_08_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_08.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 09 CORSAIR RAM
        price_settings = []
        component_09 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "RAM_CORSAIR_32GB_DDR5").first()
        component_09_price = 2289000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_09.id,
                    day_type=day_type_int,
                    price_per_unit=component_09_price,
                    active=True
                )
            )
            component_09_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_09.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        # Reviews & Price Settings for 10 KINGBANK RAM
        price_settings = []
        component_10 = db.query(ComputerComponent).filter(ComputerComponent.product_code == "RAM_KINGBANK").first()
        component_10_price = 1849000
        for day_type_int in [0, 1, 2, 3, 4, 5, 6, 7]:
            price_settings.append(
                ComputerComponentSellPriceSetting(
                    component_id = component_10.id,
                    day_type=day_type_int,
                    price_per_unit=component_10_price,
                    active=True
                )
            )
            component_10_price += 1000

        reviews = []
        for _ in range(10):
            user = random.choice(users)
            reviews.append(
                ComputerComponentReview(
                    user_id=user[0],
                    user_fullname=user[1],
                    component_id=component_10.id,
                    rating=random.randint(4, 5),
                    comments=component_reviews_hash_map[random.randint(0, 39)]
                ) 
            )

        db.add_all(reviews + price_settings)
        db.commit()

        return 'ok'

        
        return { 'message': 'Seeding completed'}
    finally:
        db.close()