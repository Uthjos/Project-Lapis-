import pytest

from src.object_class.item import Item


def test_item_stores_values():
    item = Item("Health Potion", "consumable", "Restores health.")

    assert item.name == "Health Potion"
    assert item.item_type == "consumable"
    assert item.description == "Restores health."


def test_item_defaults():
    item = Item("Rock")

    assert item.item_type == "item"
    assert item.description == ""


def test_item_empty_name_raises():
    with pytest.raises(ValueError):
        Item("")


def test_item_repr():
    assert repr(Item("Rock", "misc")) == "Item('Rock', 'misc')"
