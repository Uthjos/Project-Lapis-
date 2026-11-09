import math

import pygame

from src.object_class.item import Item


# Weapon class extends Item with weapon-specific stats
class Weapon(Item):
    """Weapon class"""
    def __init__(self, name, damage, attack_speed, attack_range, description=""):
        super().__init__(name, "weapon", description)

        # Check that the weapon stats are valid
        if damage < 0:
            raise ValueError("Damage cannot be negative")
        if attack_speed <= 0:
            raise ValueError("Attack speed must be greater than zero")
        if attack_range < 0:
            raise ValueError("Range cannot be negative")

        # Store stats for use by other parts of the game
        self.damage = damage
        self.attack_speed = attack_speed
        self.attack_range = attack_range  # in pixels
        self.cooldown_ms = 1000 / attack_speed
        self._last_attack = -math.inf

    def ready(self, now):
        return now - self._last_attack >= self.cooldown_ms

    def use(self, now):
        """Start an attack if off cooldown. Returns True if it fired."""
        if not self.ready(now):
            return False
        self._last_attack = now
        return True

    def attack_rect(self, origin, facing):
        """Hitbox placed in front of the attacker. facing is a (dx, dy) unit vector."""
        rect = pygame.Rect(0, 0, self.attack_range, self.attack_range)
        rect.center = (
            origin[0] + facing[0] * self.attack_range,
            origin[1] + facing[1] * self.attack_range,
        )
        return rect
