from tests.conftest import (
    db_session,
    sell_price_on_wednesday_of_keyboard_logitech,
    sell_price_on_thursday_of_keyboard_logitech,
    sell_price_default_of_keyboard_logitech,
    sell_price_on_wednesday_of_liquid_fan,
    sell_price_on_thursday_of_liquid_fan,
    sell_price_default_of_liquid_fan
)
from src.sellable_products.component_ids_filter_by_prices_service import ComponentIdsFilterByPricesService
import datetime as dt
import time_machine

def test_empty(db_session):
    service = ComponentIdsFilterByPricesService(db=db_session, start_price=None, end_price=None)
    result = service.call()
    assert result == []

def test_no_filters(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 10)) # thursday
    traveller.start()

    service = ComponentIdsFilterByPricesService(db=db_session, start_price=None, end_price=None)
    result = service.call()
    assert result == [sell_price_on_thursday_of_keyboard_logitech.component_id, sell_price_on_thursday_of_liquid_fan.component_id]
    traveller.stop()

def test_thursday_price_only_keyboard_match(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 10)) # thursday
    traveller.start()
    
    service = ComponentIdsFilterByPricesService(db=db_session, start_price=sell_price_on_thursday_of_keyboard_logitech.price_per_unit, end_price=None)
    result = service.call()
    assert result == [sell_price_on_thursday_of_keyboard_logitech.component_id]
    traveller.stop()

def test_thursday_price_none_match(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 10)) # thursday
    traveller.start()
    
    service = ComponentIdsFilterByPricesService(db=db_session, start_price=sell_price_on_thursday_of_keyboard_logitech.price_per_unit + 1, end_price=None)
    result = service.call()
    assert result == []
    traveller.stop()

def test_using_thursday_min_price_when_wednesday(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 9)) # wednesday
    traveller.start()
    
    # wednesday price is 1,6 mil, thursday is 1,66 mil
    # filter using thursday as min price will return none

    service = ComponentIdsFilterByPricesService(db=db_session, start_price=sell_price_on_thursday_of_keyboard_logitech.price_per_unit, end_price=None)
    result = service.call()
    assert result == []
    traveller.stop()

def test_should_not_fallback_to_default_price(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 9)) # wednesday
    traveller.start()
    
    # wednesday price is 1,6 mil, default is 1,55 mil
    # if end_price is 1,55 mil and its wednesday
    # should not fallback to default price

    service = ComponentIdsFilterByPricesService(db=db_session, start_price=None, end_price=sell_price_on_wednesday_of_keyboard_logitech.price_per_unit - 1)
    result = service.call()
    assert result == [sell_price_on_thursday_of_liquid_fan.component_id]
    traveller.stop()

def test_fallback_to_default_price(
        db_session,
        sell_price_on_wednesday_of_keyboard_logitech,
        sell_price_on_thursday_of_keyboard_logitech,
        sell_price_default_of_keyboard_logitech,
        sell_price_on_wednesday_of_liquid_fan,
        sell_price_on_thursday_of_liquid_fan,
        sell_price_default_of_liquid_fan
    ):
    traveller = time_machine.travel(dt.date(2025, 7, 9)) # wednesday
    traveller.start()

    sell_price_on_wednesday_of_keyboard_logitech.active = False
    sell_price_on_wednesday_of_liquid_fan.active = False
    db_session.add_all([sell_price_on_wednesday_of_keyboard_logitech, sell_price_on_wednesday_of_liquid_fan])
    db_session.commit()

    service = ComponentIdsFilterByPricesService(db=db_session, start_price=None, end_price=None)
    result = service.call()
    assert result == [sell_price_default_of_keyboard_logitech.component_id, sell_price_default_of_liquid_fan.component_id]
    traveller.stop()
