from pygame import Rect


class Entity:
    def __init__(self, x=0, y=0, health=100):
        self.x, self.y = x, y
        self.health = health
        self.max_health = health
        self.hurtbox = Rect(0, 0, 32, 32)          # body: where this entity can be hit
        self.movement_hitbox = Rect(0, 0, 32, 16)  # feet: used for terrain collision
        self.collision_map = None
        self._sync_hitboxes()

    def set_collision_map(self, collision_map):
        self.collision_map = collision_map

    def _sync_hitboxes(self):
        self.hurtbox.topleft = (self.x, self.y)
        self.movement_hitbox.midbottom = (self.x + 16, self.y + 32)

    def _can_stand(self, dx, dy):
        """True if the feet hitbox, shifted by (dx, dy), is fully on walkable ground."""
        if self.collision_map is None:
            return True
        r = self.movement_hitbox.move(round(dx), round(dy))
        corners = [r.topleft, (r.right - 1, r.top),
                   (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1)]
        return all(self.collision_map.is_walkable(px, py) for px, py in corners)

    def take_damage(self, damage):
        self.health = max(self.health - damage, 0)

    def is_alive(self):
        return self.health > 0