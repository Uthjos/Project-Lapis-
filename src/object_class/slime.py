"""Crypt Slime: an Enemy with sprite animations that hops toward the player."""

from typing import ClassVar

import pygame

from src.animation.sprite_animation import Animation, AnimationPlayer, load_strip
from src.object_class.enemy import Enemy, EnemyState


class Slime(Enemy):
    """Slime class"""
    # ---- sprite sheets: 80x80 frames; (file, per-frame ms read from Crypt-Slime.aseprite, loops?)
    FRAME_SIZE = 80
    ANCHOR = (32, 50)  # ground point of a frame: bottom-centre of the slime's body
    SHEETS: ClassVar[dict[str, tuple[str, list[int], bool]]] = {
        "idle": ("crypt-slime-idle-sheet.png", [800], True),
        "hop": (
            "crypt-slime-hop-sheet.png",
            [160, 80, 90, 60, 110, 70, 50, 80, 100],
            True,
        ),
        "attack": (
            "crypt-slime-attack-sheet.png",
            [100, 70, 120, 40, 50, 70, 80, 100, 170],
            False,
        ),
        "hurt": ("crypt-slime-hurt-sheet.png", [60, 60, 80, 90, 90, 120], False),
        "death": (
            "crypt-slime-death-sheet.png",
            [80, 70, 70, 90, 100, 120, 140, 700],
            False,
        ),
    }
    # Which sheet plays in each AI state. COOLDOWN is absent on purpose: the attack
    # animation keeps playing through it, then the slime settles back to idle.
    STATE_ANIMATIONS: ClassVar[dict[EnemyState, str]] = {
        EnemyState.IDLE: "idle",
        EnemyState.CHASE: "hop",
        EnemyState.WINDUP: "attack",
        EnemyState.HURT: "hurt",
        EnemyState.DEAD: "death",
    }
    SPRITE_FACES_RIGHT = True  # flip this if the art looks mirrored in game
    HOP_AIR_FRAMES = (3, 4, 5)  # hop frames where the slime is off the ground
    FADE_MS = 400  # corpse fade-out after the death animation

    animations: ClassVar[dict[str, Animation]] = {}

    @classmethod
    def load_assets(cls, sprite_dir):
        """Load every animation once. Call after pygame.display.set_mode()."""
        cls.animations = {}
        for name, (filename, durations, loop) in cls.SHEETS.items():
            frames = load_strip(sprite_dir / filename, cls.FRAME_SIZE, cls.FRAME_SIZE)
            cls.animations[name] = Animation(frames, durations, loop)

    def __init__(self, x, y):
        anims = self.animations
        super().__init__(
            x,
            y,
            health=30,
            speed=4.0,
            damage=8,
            aggro_range=260,
            attack_range=40,
            windup_ms=330,  # = start of attack frame 4, the lunge
            cooldown_ms=1300,  # attack anim is 800ms; the rest is recovery
            hurt_ms=anims["hurt"].total_ms,
            death_ms=anims["death"].total_ms + self.FADE_MS,
        )
        self.hurtbox.size = (32, 24)  # the slime is shorter than a 32x32 body
        self._sync_hitboxes()
        self.anim = AnimationPlayer(anims["idle"])
        self.facing_right = True
        self._last_now = None

    def _sync_hitboxes(self):
        super()._sync_hitboxes()
        self.hurtbox.midbottom = (
            self.x + 16,
            self.y + 32,
        )  # sit on the feet, not float above

    # ---------- Enemy hooks
    def _set_state(self, state, now):
        super()._set_state(state, now)
        name = self.STATE_ANIMATIONS.get(state)
        if name:
            self.anim.play(self.animations[name], restart=True)

    def _step_toward(self, target):
        """Only advance while airborne, so the slime hops instead of gliding."""
        if self.anim.index in self.HOP_AIR_FRAMES:
            super()._step_toward(target)

    def update(self, player, now):
        dt = 0 if self._last_now is None else min(now - self._last_now, 100)
        self._last_now = now

        # Face the player, except while committed to an attack.
        if self.is_alive() and self.state not in (
            EnemyState.WINDUP,
            EnemyState.COOLDOWN,
        ):
            self.facing_right = player.hurtbox.centerx >= self.hurtbox.centerx

        super().update(player, now)
        self.anim.update(dt)
        if self.state == EnemyState.COOLDOWN and self.anim.finished:
            self.anim.play(self.animations["idle"])

    # ---------- drawing
    def draw(self, surface):
        img = self.anim.image
        ax, ay = self.ANCHOR
        if self.facing_right != self.SPRITE_FACES_RIGHT:
            img = pygame.transform.flip(img, True, False)
            ax = img.get_width() - ax
        if self.state == EnemyState.DEAD and self.anim.finished:
            faded = (self._now - self.state_start) - self.animations["death"].total_ms
            img = img.copy()
            img.set_alpha(max(0, int(255 * (1 - faded / self.FADE_MS))))
        # Entity x, y is the top-left of its 32x32 body, so the feet are at (x + 16, y + 32).
        surface.blit(img, (round(self.x + 16 - ax), round(self.y + 32 - ay)))
