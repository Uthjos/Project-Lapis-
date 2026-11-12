from pygame import Rect


class Entity:
    """Entity class."""
    def __init__(self, x=0, y=0, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.hurtbox = Rect(0, 0, 32, 32)  # body: where this entity can be hit
        self.movement_hitbox = Rect(0, 0, 32, 16)  # feet: used for terrain collision
        self.collision_map = None
        self._sync_hitboxes()

    def set_collision_map(self, collision_map):
        """apply new collision map."""
        self.collision_map = collision_map

    def _sync_hitboxes(self):
        """Sync hitbox and movement hitbox to current player position."""
        self.hurtbox.topleft = (self.x, self.y)
        self.movement_hitbox.midbottom = (self.x + 16, self.y + 32)

    def _can_stand(self, dx, dy):
        """True if the feet hitbox, shifted by (dx, dy), is fully on walkable ground."""
        if self.collision_map is None:
            return True
        r = self.movement_hitbox.move(round(dx), round(dy))
        corners = [
            r.topleft,
            (r.right - 1, r.top),
            (r.left, r.bottom - 1),
            (r.right - 1, r.bottom - 1),
        ]
        return all(self.collision_map.is_walkable(px, py) for px, py in corners)

    def take_damage(self, damage):
        """apply damage to character"""
        self.health = max(self.health - damage, 0)

    def is_alive(self):
        """return True if entity health is greater than 0"""
        return self.health > 0
