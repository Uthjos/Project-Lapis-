import pygame
import pytest

from src.animation.animation_stack import Action
from src.object_class.character import Character
from src.object_class.weapon import Weapon


@pytest.fixture
def player(character_assets):
    player = Character(100, 100)
    sword = Weapon("Sword", damage=10, attack_speed=1.0, attack_range=40)
    player.inventory.add_item(sword)
    player.equip_item(sword)
    return player


def test_every_sheet_loads_eight_frames_per_direction(character_assets):
    for name in Character.SHEETS:
        for direction in Character.DIRECTIONS.values():
            animation = Character.animations[name, direction]
            assert len(animation.frames) == 8
            w, h = Character.FRAME_SIZE
            assert animation.frames[0].get_size() == (w * Character.SCALE, h * Character.SCALE)


def test_character_without_assets_has_no_animation(monkeypatch):
    monkeypatch.setattr(Character, "animations", {})
    player = Character()

    player.update(moving=True, dt=16)  # must not crash headless

    assert player.anim is None
    assert player.action == Action.RUN


def test_starts_idle_facing_right(player):
    assert player.anim.animation is Character.animations["idle", "right"]


def test_run_follows_facing(player):
    player.facing = (0, 1)

    player.update(moving=True, dt=16)

    assert player.action == Action.RUN
    assert player.anim.animation is Character.animations["run", "down"]


def test_attack_plays_through_then_returns_to_idle(player):
    player.attack([], now=0)
    assert player.action == Action.ATTACK
    assert player.anim.animation is Character.animations["attack1", "right"]

    player.update(moving=True, dt=100)  # moving doesn't cancel the swing
    assert player.attacking

    player.update(moving=False, dt=Character.animations["attack1", "right"].total_ms)
    player.update(moving=False, dt=0)
    assert player.action == Action.IDLE
    assert player.anim.animation is Character.animations["idle", "right"]


def test_attacks_alternate_between_sheets(player):
    player.attack([], now=0)
    assert player.anim.animation is Character.animations["attack1", "right"]

    player.attack([], now=5000)  # past the weapon cooldown
    assert player.anim.animation is Character.animations["attack2", "right"]


def test_draw_puts_feet_on_the_body_bottom(player):
    surface = pygame.Surface((300, 300), pygame.SRCALPHA)

    player.draw(surface)

    bbox = surface.get_bounding_rect()
    assert abs(bbox.bottom - (player.y + 32)) <= 1
    assert abs(bbox.centerx - (player.x + 16)) <= 2
