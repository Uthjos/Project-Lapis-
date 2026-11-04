
# Item categories and the properties each one uses
ITEM_TYPES = {
    "weapon": {
        "file": "weapons.json",
        "fields": {
            "damage": int,
            "attack_speed": float,
            "range": int
        }
    },

    "potion": {
        "file": "potions.json",
        "fields": {
            "health": int,
            "mana": int,
            "stamina": int,
            "strength": int,
            "defense": int,
            "speed": int
        },
        "item_type": "consumable"
    }
}
