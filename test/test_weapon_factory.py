from src.object_class.weapon import Weapon
from src.object_class.weapon_factory import WeaponFactory


def test_weapon_creation():
    # Create a weapon using the JSON data
    factory = WeaponFactory()
    sword = factory.create_weapon("rusty_sword")

    # make sure that the weapon was created correctly
    assert isinstance(sword, Weapon)
    assert sword.name == "Rusty Sword"
    assert sword.damage == 10
    assert sword.attack_speed == 1.0
    assert sword.attack_range >= 32  # bigger than body of player


def test_invalid_weapon():
    # Check that an invalid weapon ID shows an error
    factory = WeaponFactory()

    try:
        factory.create_weapon("fake_weapon")
        assert False, "Expected an error for an invalid weapon"
    except ValueError:
        pass
