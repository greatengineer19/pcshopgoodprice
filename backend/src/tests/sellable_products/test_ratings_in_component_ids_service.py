from src.tests.conftest import (
    db_session,
    review_component_keyboard_logitech,
    review_component_liquid_fan
)
from src.sellable_products.ratings_in_component_ids_service import RatingsInComponentIdsService
import datetime as dt
import time_machine

def test_empty(db_session):
    service = RatingsInComponentIdsService(db=db_session, component_ids=[])
    result = service.call()
    assert result == {}

def test_default(db_session, review_component_keyboard_logitech, review_component_liquid_fan):
    service = RatingsInComponentIdsService(db=db_session, component_ids=[review_component_keyboard_logitech.component_id,
                                                                         review_component_liquid_fan.component_id])
    result = service.call()
    assert result == {
        review_component_keyboard_logitech.component_id: {'rating': 5.0, 'count_review_given': 1},
        review_component_liquid_fan.component_id: {'rating': 4.0, 'count_review_given': 1}}