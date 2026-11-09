import json
from pathlib import Path

from src.object_class.weapon import Weapon


class WeaponFactory:
    def __init__(self):
        # Find the JSON file containing weapon definitions
        data_file = (
            Path(__file__).resolve().parent.parent / "data_file_manage" / "weapons.json")  # Load the weapon data into a dictionary
        with open(data_file, "r", encoding="utf-8") as file:
            self.weapons = json.load(file)

    def create_weapon(self, weapon_id):
        # Make sure the requested weapon exists
        if weapon_id not in self.weapons:
            raise ValueError(f"Weapon not found: {weapon_id}")

        # Get the stats for the selected weapon
        data = self.weapons[weapon_id]

        # Create a new weapon using the stored stats
        return Weapon(
            data["name"],
            data["damage"],
            data["attack_speed"],
            data["range"],
            data.get("description", ""),
        )
