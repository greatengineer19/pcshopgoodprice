from tests.conftest import (
    db_session,
    sell_price_on_wednesday_of_keyboard_logitech,
    sell_price_on_thursday_of_keyboard_logitech,
    sell_price_default_of_keyboard_logitech,
    review_component_keyboard_logitech,
    component_keyboard_logitech
)
from src.sellable_products.ratings_in_component_ids_service import RatingsInComponentIdsService
from src.sellable_products.sell_price_and_ratings_finder_service import SellPriceAndRatingsFinderService
import datetime as dt
import time_machine
from decimal import Decimal

def test_no_rating(db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        component_keyboard_logitech
    ):
    service = SellPriceAndRatingsFinderService(db=db_session, component=component_keyboard_logitech, ratings={})
    assert hasattr(component_keyboard_logitech, 'sell_price') == False

    result = service.call()
    assert result.sell_price == Decimal('1550000.000000')
    assert hasattr(component_keyboard_logitech, 'sell_price') == True
    assert result.rating == 0.0
    assert result.count_review_given == 0

def test_when_thursday_price_is_active(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        review_component_keyboard_logitech,
        component_keyboard_logitech
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 10)) # thursday
    traveller.start()

    rating_service = RatingsInComponentIdsService(db=db_session, component_ids=[component_keyboard_logitech.id])
    rating_result = rating_service.call()

    service = SellPriceAndRatingsFinderService(db=db_session, component=component_keyboard_logitech, ratings=rating_result)
    result = service.call()

    assert result.sell_price == Decimal('1660000.000000')
    assert result.rating == 5.0
    assert result.count_review_given == 1
    traveller.stop()

def test_when_thursday_price_is_not_active(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        review_component_keyboard_logitech,
        component_keyboard_logitech
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 10)) # thursday
    traveller.start()

    sell_price_on_thursday_of_keyboard_logitech.active = False
    db_session.add(sell_price_on_thursday_of_keyboard_logitech)
    db_session.commit()

    rating_service = RatingsInComponentIdsService(db=db_session, component_ids=[component_keyboard_logitech.id])
    rating_result = rating_service.call()

    service = SellPriceAndRatingsFinderService(db=db_session, component=component_keyboard_logitech, ratings=rating_result)
    result = service.call()

    assert result.sell_price == Decimal('1550000.000000')
    assert result.rating == 5.0
    assert result.count_review_given == 1

    traveller.stop()

def test_when_friday_price(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        review_component_keyboard_logitech,
        component_keyboard_logitech
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 11)) # friday
    traveller.start()

    rating_service = RatingsInComponentIdsService(db=db_session, component_ids=[component_keyboard_logitech.id])
    rating_result = rating_service.call()

    service = SellPriceAndRatingsFinderService(db=db_session, component=component_keyboard_logitech, ratings=rating_result)
    result = service.call()

    assert result.sell_price == Decimal('1550000.000000')
    assert result.rating == 5.0
    assert result.count_review_given == 1

    traveller.stop()