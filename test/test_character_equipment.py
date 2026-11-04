import math

from src.animation.AnimationStack import Action, SpriteDirection
from src.object_class.Character import Character
from src.object_class.Entity import Entity
from src.object_class.Item import Item
from src.object_class.Weapon import Weapon


class WallMap:
    """Nothing is walkable at x < 0."""

    def is_walkable(self, px, py):
        return px >= 0


def make_sword():
    return Weapon("Sword", damage=10, attack_speed=1.0, range=40)


def make_armed_character():
    player = Character(0, 0)
    sword = make_sword()
    player.inventory.add_item(sword)
    player.equip_item(sword)
    return player, sword


def test_character_defaults():
    player = Character()

    assert player.direction == SpriteDirection.S
    assert player.action == Action.IDLE
    assert player.facing == (1, 0)
    assert player.equipped_item is None
    assert player.last_attack_time == -math.inf


def test_update_state():
    player = Character()

    player.update_state(Action.WALK, SpriteDirection.NE)

    assert player.action == Action.WALK
    assert player.direction == SpriteDirection.NE


def test_equip_item_in_inventory():
    player = Character()
    item = Item("Rock")
    player.inventory.add_item(item)

    assert player.equip_item(item) is True
    assert player.equipped_item is item


def test_equip_item_not_in_inventory_fails():
    player = Character()

    assert player.equip_item(Item("Rock")) is False
    assert player.equipped_item is None


def test_move_blocked_by_collision_map_slides_on_other_axis():
    player = Character(0, 0)
    player.set_collision_map(WallMap())

    player.move(-5, 7)

    assert player.x == 0   # blocked
    assert player.y == 7   # free axis still moves


def test_attack_without_weapon_does_nothing():
    player = Character()
    target = Entity(40, 0)

    assert player.attack([target], 0) == []
    assert target.health == 100


def test_attack_with_non_weapon_item_does_nothing():
    player = Character()
    item = Item("Rock")
    player.inventory.add_item(item)
    player.equip_item(item)
    target = Entity(40, 0)

    assert player.attack([target], 0) == []


def test_attack_damages_target_in_front():
    player, sword = make_armed_character()
    target = Entity(50, 0)

    hits = player.attack([target], 0)

    assert hits == [target]
    assert target.health == 100 - sword.damage
    assert player.last_attack_time == 0


def test_attack_misses_target_behind():
    player, _ = make_armed_character()
    target = Entity(-200, 0)

    assert player.attack([target], 0) == []
    assert target.health == 100


def test_attack_respects_weapon_cooldown():
    player, _ = make_armed_character()
    target = Entity(50, 0)

    player.attack([target], 0)
    assert player.attack([target], 100) == []
    assert target.health == 90


def test_attack_skips_dead_targets_and_self():
    player, _ = make_armed_character()
    dead = Entity(50, 0)
    dead.take_damage(999)

    assert player.attack([dead, player], 0) == []
    assert player.health == 100
