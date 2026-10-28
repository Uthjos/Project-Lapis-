from pygame import Rect

from src.animation.AnimationStack import Action, SpriteDirection
from src.object_class.Inventory import Inventory


class Character:

    def __init__(self, x=0, y=0, health=100):
        self.x = x
        self.y = y
        self.health = health
        
        # initial state of character
        self.direction = SpriteDirection.S
        self.action = Action.IDLE
        self.inventory = Inventory()
        self.equipped_item = None
        self.movement_hitbox = Rect(0,0,32,16)
        self.collision_map = None
        self._sync_hitboxes()

    def set_collision_map(self, collision_map):
        self.collision_map = collision_map

    #updates hitbox to new character position
    def _sync_hitboxes(self):
        self.movement_hitbox.midbottom = (self.x + 16, self.y + 32)
        #TODO will add damage hitbox here too

    def _can_stand(self, dx, dy):
        """True if the feet hitbox, shifted by (dx, dy), is fully on walkable ground."""
        if self.collision_map is None:
            return True
        r = self.movement_hitbox.move(dx, dy)
        corners = [r.topleft, (r.right - 1, r.top),
                   (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1)]
        return all(self.collision_map.is_walkable(px, py) for px, py in corners)

    # moves the character by changing its x and y position
    def move(self, x, y):
        # One axis at a time so the character slides along edges instead of sticking
        if x and self._can_stand(x, 0):
            self.x += x
        if y and self._can_stand(0, y):
            self.y += y
        self._sync_hitboxes()

    # lowers the character's health when they take damage
    def take_damage(self, damage):
        self.health -= damage

        # health should not go below 0
        self.health = max(self.health, 0)

    # checks if the character is still alive
    def is_alive(self):
        return self.health > 0
    
    def update_state(self, action: Action, direction: SpriteDirection):
        self.direction = direction
        self.action = action

    #attack1
    def attack(self):
        #TODO build attack call from item
        pass

    def equip_item(self, item):
        """Equip an item only when it belongs to this character's inventory."""
        if not self.inventory.has_item(item):
            return False
        self.equipped_item = item
        return True

    def feet_on_floor(player, grid):
        r = player.movement_hitbox
        corners = [r.topleft, (r.right - 1, r.top),
                   (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1)]
        return all(grid.is_walkable(x, y) for x, y in corners)

    def try_move(player, grid, dx, dy):
        if dx:
            player.move(dx, 0)
            if not player.feet_on_floor(player, grid):
                player.move(-dx, 0)
        if dy:
            player.move(0, dy)
            if not player.feet_on_floor(player, grid):
                player.move(0, -dy)