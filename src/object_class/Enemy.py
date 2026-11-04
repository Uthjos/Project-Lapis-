import math
from enum import Enum, auto

from src.object_class.Entity import Entity


class EnemyState(Enum):
    IDLE = auto()
    CHASE = auto()
    WINDUP = auto()
    COOLDOWN = auto()


class Enemy(Entity):
    def __init__(self, x, y, health=50, speed=1.5, damage=10,
                 aggro_range=250, attack_range=36,
                 windup_ms=400, cooldown_ms=1000):
        super().__init__(x, y, health)
        self.speed = speed
        self.damage = damage
        self.aggro_range = aggro_range
        self.attack_range = attack_range
        self.windup_ms = windup_ms
        self.cooldown_ms = cooldown_ms

        self.state = EnemyState.IDLE
        self.state_start = 0

    # ---------- AI ----------
    def update(self, player, now):
        if not self.is_alive():
            return

        dist = self._distance_to(player)

        if self.state == EnemyState.IDLE:
            if dist <= self.aggro_range:
                self._set_state(EnemyState.CHASE, now)

        elif self.state == EnemyState.CHASE:
            if dist > self.aggro_range * 1.5:            # lose interest (leash)
                self._set_state(EnemyState.IDLE, now)
            elif dist <= self.attack_range:
                self._set_state(EnemyState.WINDUP, now)
            else:
                self._step_toward(player)

        elif self.state == EnemyState.WINDUP:
            if now - self.state_start >= self.windup_ms:
                # Re-check range at the moment of impact so the player can dodge.
                if player.is_alive() and self._distance_to(player) <= self.attack_range * 1.25:
                    player.take_damage(self.damage)
                self._set_state(EnemyState.COOLDOWN, now)

        elif self.state == EnemyState.COOLDOWN and now - self.state_start >= self.cooldown_ms :
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