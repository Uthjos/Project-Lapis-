
from src.object_class.Item import Item


# Weapon class extends Item with weapon-specific stats
class Weapon(Item):
    def __init__(self, name, damage, attack_speed, range, description=""):
        super().__init__(name, "weapon", description)

        # Check that the weapon stats are valid
        if damage < 0:
            raise ValueError("Damage cannot be negative")
        if attack_speed <= 0:
            raise ValueError("Attack speed must be greater than zero")
        if range < 0:
            raise ValueError("Range cannot be negative")

        # Store stats for use by other parts of the game
        self.damage = damage
        self.attack_speed = attack_speed
        self.range = range
