import json
from pathlib import Path

from src.object_class.item import Item


class PotionFactory:
    """Potion factory class."""
    def __init__(self):
        # Find the potion JSON file
        data_file = (
            Path(__file__).resolve().parent.parent / "data_file_manage" / "potions.json"
        )

        # Load the potion data
        with open(data_file, "r", encoding="utf-8") as file:
            self.potions = json.load(file)

    def create_potion(self, potion_id):
        # Check that the potion exists
        if potion_id not in self.potions:
            raise ValueError(f"Potion not found: {potion_id}")

        data = self.potions[potion_id]

        # Create the potion as an Item object
        potion = Item(data["name"], "consumable", data.get("description", ""))

        # Add all of its stat adjustments
        for stat in ("health", "mana", "stamina", "strength", "defense", "speed"):
            setattr(potion, stat, data.get(stat, 0))

        return potion
