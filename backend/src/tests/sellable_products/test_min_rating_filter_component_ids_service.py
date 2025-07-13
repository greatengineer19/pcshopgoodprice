from src.tests.conftest import (
    db_session,
    review_component_keyboard_logitech,
    review_component_liquid_fan
)
from src.sellable_products.min_rating_filter_component_ids_service import MinRatingFilterComponentIdsService
import datetime as dt
import time_machine

def test_no_components(db_session):
    service = MinRatingFilterComponentIdsService(db=db_session, min_rating=None)
    result = service.call()
    assert result == []

def test_no_filter(db_session, review_component_keyboard_logitech, review_component_liquid_fan):
    service = MinRatingFilterComponentIdsService(db=db_session, min_rating=None)
    result = service.call()
    assert result == [review_component_liquid_fan.component_id,
                      review_component_keyboard_logitech.component_id]

def test_with_rating(db_session, review_component_keyboard_logitech, review_component_liquid_fan):
    service = MinRatingFilterComponentIdsService(db=db_session, min_rating=5)
    result = service.call()
    assert result == [review_component_keyboard_logitech.component_id]