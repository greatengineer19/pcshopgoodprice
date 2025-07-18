from src.models import (
    ComputerComponentCategory,
    ComputerComponent,
    User,
    ComputerComponentSellPriceSetting
    )
from sqlalchemy import select, desc, func
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