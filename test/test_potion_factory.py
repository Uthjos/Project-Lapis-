import pytest

from src.object_class.potion_factory import PotionFactory


def test_health_potion():
    factory = PotionFactory()
    potion = factory.create_potion("health_potion")

    assert potion.name == "Health Potion"
    assert potion.health == 25
    assert potion.speed == 0


def test_strength_potion():
    factory = PotionFactory()
    potion = factory.create_potion("strength_potion")

    assert potion.strength == 10
    assert potion.speed == -3


def test_invalid_potion():
    factory = PotionFactory()

    with pytest.raises(ValueError):
        factory.create_potion("fake_potion")
