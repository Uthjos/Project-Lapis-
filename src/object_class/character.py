import math
from typing import ClassVar

import pygame

from src.animation.animation_stack import Action, SpriteDirection
from src.animation.sprite_animation import Animation, AnimationPlayer, load_strip
from src.object_class.entity import Entity
from src.object_class.inventory import Inventory
from src.object_class.weapon import Weapon


class Character(Entity):
    """Character class"""

    # ---- Adventurer sheets: 8 frames of 96x80 each, one sheet per direction.
    FRAME_SIZE = (96, 80)
    ANCHOR = (47, 58)  # ground point of a frame: between the adventurer's feet
    # name -> (folder, ms per frame, loops?). Files are <folder>/<name>_<direction>.png
    SHEETS: ClassVar[dict[str, tuple[str, int, bool]]] = {
        "idle": ("IDLE", 120, True),
        "run": ("RUN", 80, True),
        "attack1": ("ATTACK 1", 60, False),
        "attack2": ("ATTACK 2", 60, False),
    }
    ATTACKS = ("attack1", "attack2")  # swings alternate between these
    # facing (dx, dy) -> sheet direction suffix
    DIRECTIONS: ClassVar[dict[tuple[int, int], str]] = {
        (0, -1): "up",
        (0, 1): "down",
        (-1, 0): "left",
        (1, 0): "right",
    }

    animations: ClassVar[dict[tuple[str, str], Animation]] = {}

    @classmethod
    def load_assets(cls, sprite_dir):
        """Load every animation once. Call after pygame.display.set_mode()."""
        cls.animations = {}
        for name, (folder, frame_ms, loop) in cls.SHEETS.items():
            for direction in cls.DIRECTIONS.values():
                path = sprite_dir / folder / f"{name}_{direction}.png"
                frames = load_strip(path, *cls.FRAME_SIZE)
                cls.animations[name, direction] = Animation(
                    frames, [frame_ms] * len(frames), loop
                )

    def __init__(self, x=0, y=0, health=100):
        super().__init__(x, y, health)
        self.direction = SpriteDirection.S
        self.action = Action.IDLE
        self.inventory = Inventory()
        self.equipped_item = None
        self.facing = (1, 0)
        self.last_attack_time = -math.inf
        self.anim = None  # stays None until load_assets() has run (headless tests)
        self._attack_count = 0
        self._play("idle")

    def move(self, x, y):
        # One axis at a time so the character slides along edges instead of sticking
        if x and self._can_stand(x, 0):
            self.x += x
        if y and self._can_stand(0, y):
            self.y += y
        self._sync_hitboxes()

    def update_state(self, action, direction):
        self.direction = direction
        self.action = action

    def equip_item(self, item):
        if not self.inventory.has_item(item):
            return False
        self.equipped_item = item
        return True

    def attack(self, targets, now):
        weapon = self.equipped_item
        if not isinstance(weapon, Weapon) or not weapon.use(now):
            return []

        self.last_attack_time = now
        self.action = Action.ATTACK
        self._play(self.ATTACKS[self._attack_count % len(self.ATTACKS)], restart=True)
        self._attack_count += 1

        hitbox = weapon.attack_rect(self.hurtbox.center, self.facing)
        hits = []
        for target in targets:
            if (
                target is not self
                and target.is_alive()
                and hitbox.colliderect(target.hurtbox)
            ):
                target.take_damage(weapon.damage)
                hits.append(target)
        return hits

    # ---------- animation
    @property
    def attacking(self):
        """True while a swing animation is still playing."""
        swinging = self.anim is not None and not self.anim.finished
        return self.action == Action.ATTACK and swinging

    def update(self, moving, dt):
        """Pick idle/run unless mid-swing, then advance the animation by dt ms."""
        if not self.attacking:
            self.action = Action.RUN if moving else Action.IDLE
            self._play(self.action.value)  # "idle" / "run"
        if self.anim:
            self.anim.update(dt)

    def _play(self, name, restart=False):
        """Play a sheet in the current facing. No-op if assets aren't loaded."""
        animation = self.animations.get((name, self.DIRECTIONS.get(tuple(self.facing))))
        if animation is None:
            return
        if self.anim is None:
            self.anim = AnimationPlayer(animation)
        else:
            self.anim.play(animation, restart)

    # ---------- drawing
    def draw(self, surface):
        if self.anim is None:  # no art loaded: show the body box instead
            pygame.draw.rect(surface, (50, 120, 220), self.hurtbox, width=2)
            return
        ax, ay = self.ANCHOR
        # Entity x, y is the top-left of its 32x32 body, so the feet are at (x + 16, y + 32).
        feet_x, feet_y = self.x + 16, self.y + 32
        surface.blit(self.anim.image, (round(feet_x - ax), round(feet_y - ay)))
