import math
from enum import Enum, auto

import pygame

from src.object_class.entity import Entity


class EnemyState(Enum):
    """Enemy action states enum"""
    IDLE = auto()
    CHASE = auto()
    WINDUP = auto()
    COOLDOWN = auto()
    HURT = auto()  # staggered by a hit; interrupts an attack
    DEAD = auto()


class Enemy(Entity):
    """Enemy class"""
    def __init__(
        self,
        x,
        y,
        health=50,
        speed=1.5,
        damage=10,
        aggro_range=250,
        attack_range=36,
        windup_ms=400,
        cooldown_ms=1000,
        hurt_ms=0,
        death_ms=0,
    ):
        super().__init__(x, y, health)
        self.speed = speed
        self.damage = damage
        self.aggro_range = aggro_range
        self.attack_range = attack_range
        self.windup_ms = windup_ms
        self.cooldown_ms = cooldown_ms
        self.hurt_ms = hurt_ms  # stagger time after a hit (0 = never staggers)
        self.death_ms = death_ms  # how long the body lingers before it can be removed

        self.state = EnemyState.IDLE
        self.state_start = 0
        self._now = 0  # last time passed to update(), so damage can stamp state changes

    @property
    def removable(self):
        """True once the enemy is dead and its death animation/linger time is over."""
        return (
            self.state == EnemyState.DEAD
            and self._now - self.state_start >= self.death_ms
        )

    def take_damage(self, damage):
        """apply damage to enemy object method"""
        if self.state == EnemyState.DEAD:
            return
        super().take_damage(damage)
        if not self.is_alive():
            self._set_state(EnemyState.DEAD, self._now)
        elif self.hurt_ms > 0:
            self._set_state(EnemyState.HURT, self._now)

    def draw(self, surface):
        """Fallback so a plain Enemy is visible; subclasses draw their sprites."""
        pygame.draw.rect(surface, (200, 50, 50), self.hurtbox, width=2)

    # Enemy AI
    def update(self, player, now):
        self._now = now
        if not self.is_alive():
            return

        dist = self._distance_to(player)

        if self.state == EnemyState.IDLE:
            if dist <= self.aggro_range:
                self._set_state(EnemyState.CHASE, now)

        elif self.state == EnemyState.CHASE:
            if dist > self.aggro_range * 1.5:  # lose interest (leash)
                self._set_state(EnemyState.IDLE, now)
            elif dist <= self.attack_range:
                self._set_state(EnemyState.WINDUP, now)
            else:
                self._step_toward(player)

        elif self.state == EnemyState.WINDUP:
            if now - self.state_start >= self.windup_ms:
                # Re-check range at the moment of impact so the player can dodge.
                if (
                    player.is_alive()
                    and self._distance_to(player) <= self.attack_range * 1.25
                ):
                    player.take_damage(self.damage)
                self._set_state(EnemyState.COOLDOWN, now)

        elif self.state == EnemyState.HURT:
            if now - self.state_start >= self.hurt_ms:
                self._set_state(EnemyState.CHASE, now)

        elif (
            self.state == EnemyState.COOLDOWN
            and now - self.state_start >= self.cooldown_ms
        ):
            self._set_state(EnemyState.CHASE, now)

    def _set_state(self, state, now):
        self.state = state
        self.state_start = now

    def _distance_to(self, other):
        ex, ey = self.hurtbox.center
        ox, oy = other.hurtbox.center
        return math.hypot(ox - ex, oy - ey)

    # ---------- movement ----------
    def _step_toward(self, target):
        ex, ey = self.hurtbox.center
        tx, ty = target.hurtbox.center
        dx, dy = tx - ex, ty - ey
        length = math.hypot(dx, dy) or 1
        dx, dy = dx / length * self.speed, dy / length * self.speed

        # One axis at a time so enemies slide along walls/water like the player does.
        if dx and self._can_stand(dx, 0):
            self.x += dx
        if dy and self._can_stand(0, dy):
            self.y += dy
        self._sync_hitboxes()
