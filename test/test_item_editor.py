import pytest

from src.data_file_manage.item_editor import ItemEditor


def test_add_potion(tmp_path):
    editor = ItemEditor(tmp_path)

    potion = {
        "name": "Test Potion",
        "type": "consumable",
        "description": "A test potion.",
        "health": 20,
        "mana": 0,
        "stamina": 0,
        "strength": 0,
        "defense": 0,
        "speed": -2,
    }

    editor.add_item("potion", "test_potion", potion)

    items = editor.load_items("potion")

    assert items["test_potion"]["health"] == 20
    assert items["test_potion"]["speed"] == -2


def test_edit_potion(tmp_path):
    editor = ItemEditor(tmp_path)

    potion = {
        "name": "Test Potion",
        "type": "consumable",
        "description": "A test potion.",
        "health": 20,
        "mana": 0,
        "stamina": 0,
        "strength": 0,
        "defense": 0,
        "speed": 0,
    }

    editor.add_item("potion", "test_potion", potion)

    editor.edit_item("test_potion", {"health": 50, "speed": -3})

    items = editor.load_items("potion")

    assert items["test_potion"]["health"] == 50
    assert items["test_potion"]["speed"] == -3
    assert items["test_potion"]["mana"] == 0


def test_add_weapon(tmp_path):
    editor = ItemEditor(tmp_path)

    weapon = {
        "name": "Test Sword",
        "description": "A test weapon.",
        "damage": 10,
        "attack_speed": 1.0,
        "range": 2,
    }

    editor.add_item("weapon", "test_sword", weapon)

    items = editor.load_items("weapon")

    assert items["test_sword"]["damage"] == 10


def test_invalid_weapon_damage(tmp_path):
    editor = ItemEditor(tmp_path)

    weapon = {
        "name": "Bad Sword",
        "description": "",
        "damage": -10,
        "attack_speed": 1.0,
        "range": 2,
    }

    with pytest.raises(ValueError):
        editor.add_item("weapon", "bad_sword", weapon)


def test_duplicate_item_id(tmp_path):
    editor = ItemEditor(tmp_path)

    potion = {
        "name": "Test Potion",
        "type": "consumable",
        "description": "",
        "health": 10,
        "mana": 0,
        "stamina": 0,
        "strength": 0,
        "defense": 0,
        "speed": 0,
    }

    editor.add_item("potion", "test_potion", potion)

    with pytest.raises(ValueError):
        editor.add_item("potion", "test_potion", potion)
