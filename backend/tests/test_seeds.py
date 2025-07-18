from src.models import (
    ComputerComponentCategory,
    ComputerComponent,
    User,
    ComputerComponentSellPriceSetting,
    ComputerComponentReview
    )
from src.schemas import (
    ComputerComponentAsResponse,
    ComputerComponentAsParams,
    ComputerComponentSellPriceSettingAsParams,
    DayTypeEnum
)
import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from tests.factories.component_factory import ComponentFactory
from tests.factories.component_category_factory import ComponentCategoryFactory
from tests.factories.computer_component_review_factory import ComputerComponentReviewFactory
from tests.factories.computer_component_sell_price_setting_factory import ComputerComponentSellPriceSettingFactory
from tests.factories.user_factory import UserFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories )


def test_seeds(client, db_session):
    response = client.get("/api/first-time-seeds")
    response_body = response.json()

    counter = db_session.query(func.count(ComputerComponent.id)).scalar()
    assert counter == 10

    counter = db_session.query(func.count(ComputerComponentCategory.id)).scalar()
    assert counter == 10

    counter = db_session.query(func.count(ComputerComponentSellPriceSetting.id)).scalar()
    assert counter == 80 # 8 type * 10

    counter = db_session.query(func.count(User.id)).scalar()
    assert counter == 102 # 100 random + 2 super user super buyer , admin seller

    assert response_body == 'ok'