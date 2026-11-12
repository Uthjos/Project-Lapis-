import pytest

from src.object_class.inventory import Inventory
from src.object_class.item import Item


def test_inventory_starts_empty():
    inv = Inventory()

    assert inv.get_items() == []
    assert inv.capacity == 20


def test_invalid_capacity_raises():
    with pytest.raises(ValueError):
        Inventory(capacity=0)


def test_add_item():
    inv = Inventory()
    item = Item("Rock")

    assert inv.add_item(item) is True
    assert inv.has_item(item)


def test_add_item_fails_when_full():
    inv = Inventory(capacity=1)
    inv.add_item(Item("A"))

    assert inv.add_item(Item("B")) is False
    assert len(inv.get_items()) == 1


def test_remove_item():
    inv = Inventory()
    item = Item("Rock")
    inv.add_item(item)

    assert inv.remove_item(item) is True
    assert not inv.has_item(item)


def test_remove_missing_item_returns_false():
    inv = Inventory()

    assert inv.remove_item(Item("Ghost")) is False


def test_get_items_returns_copy():
    inv = Inventory()
    inv.add_item(Item("Rock"))

    inv.get_items().clear()

    assert len(inv.get_items()) == 1
