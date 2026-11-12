from src.object_class.potion_factory import PotionFactory
from src.object_class.weapon_factory import WeaponFactory


def give_starting_items(player):
    # Create the factories
    weapon_factory = WeaponFactory()
    potion_factory = PotionFactory()

    # Create the player's starting items
    sword = weapon_factory.create_weapon("rusty_sword")
    potion = potion_factory.create_potion("health_potion")

    # Add both items to the inventory
    player.inventory.add_item(sword)
    player.equip_item(sword)
    player.inventory.add_item(potion)
