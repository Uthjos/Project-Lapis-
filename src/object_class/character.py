import math

from src.animation.animation_stack import Action, SpriteDirection
from src.object_class.entity import Entity
from src.object_class.inventory import Inventory
from src.object_class.weapon import Weapon


class Character(Entity):
    """Character class"""
    def __init__(self, x=0, y=0, health=100):
        super().__init__(x, y, health)
        self.direction = SpriteDirection.S
        self.action = Action.IDLE
        self.inventory = Inventory()
        self.equipped_item = None
        self.facing = (1, 0)
        self.last_attack_time = -math.inf

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
