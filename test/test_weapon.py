import pytest

from src.object_class.Item import Item
from src.object_class.Weapon import Weapon
from src.object_class.WeaponFactory import WeaponFactory


def make_weapon(**overrides):
    stats = {"name": "Test Sword", "damage": 10, "attack_speed": 2.0, "range": 40}
    stats.update(overrides)
    return Weapon(**stats)


def test_weapon_is_an_item_of_type_weapon():
    weapon = make_weapon()

    assert isinstance(weapon, Item)
    assert weapon.item_type == "weapon"


def test_weapon_stats_and_cooldown():
    weapon = make_weapon(attack_speed=2.0)

    assert weapon.damage == 10
    assert weapon.range == 40
    assert weapon.cooldown_ms == 500


@pytest.mark.parametrize("field,value", [("damage", -1), ("attack_speed", 0), ("range", -5)])
def test_invalid_stats_raise(field, value):
    with pytest.raises(ValueError):
        make_weapon(**{field: value})


def test_weapon_ready_and_use_respect_cooldown():
    weapon = make_weapon(attack_speed=1.0)  # 1000 ms cooldown

    assert weapon.ready(0) is True
    assert weapon.use(0) is True
    assert weapon.use(500) is False
    assert weapon.ready(1000) is True
    assert weapon.use(1000) is True


def test_attack_rect_is_placed_in_front_of_attacker():
    weapon = make_weapon(range=40)

    rect = weapon.attack_rect((16, 16), (1, 0))
    assert rect.size == (40, 40)
    assert rect.center == (56, 16)

    assert weapon.attack_rect((16, 16), (-1, 0)).center == (-24, 16)
    assert weapon.attack_rect((16, 16), (0, -1)).center == (16, -24)


def test_factory_creates_iron_sword():
    sword = WeaponFactory().create_weapon("iron_sword")

    assert sword.name == "Iron Sword"
    assert sword.damage == 15
    assert sword.attack_speed == 1.2
