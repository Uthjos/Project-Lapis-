import json
from pathlib import Path

from src.data_file_manage.item_types import ITEM_TYPES


class ItemEditor:
    def __init__(self, folder=None):
        # Folder containing the item JSON files
        self.folder = Path(folder) if folder else Path(__file__).resolve().parent

    def load_items(self, item_type):
        # Read the JSON file for the selected item type
        filename = ITEM_TYPES[item_type]["file"]
        path = self.folder / filename

        if not path.exists():
            return {}

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_items(self, item_type, items):
        # Save the item definitions back to JSON
        filename = ITEM_TYPES[item_type]["file"]
        path = self.folder / filename

        with open(path, "w", encoding="utf-8") as file:
            json.dump(items, file, indent=4)

    def list_items(self):
        # Display items from all registered categories
        for item_type in ITEM_TYPES:
            print(f"\n--- {item_type.upper()} ---")

            items = self.load_items(item_type)

            for item_id, data in items.items():
                print(f"{item_id}: {data['name']}")

    def find_item(self, item_id):
        # Search all categories for an existing item
        for item_type in ITEM_TYPES:
            items = self.load_items(item_type)

            if item_id in items:
                return item_type, items, items[item_id]

        raise ValueError("Item not found")

    def validate_item(self, item_type, data):
        # Make sure the item has a name
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise ValueError("Item name cannot be empty")

        # Check the required stats for this item type
        fields = ITEM_TYPES[item_type]["fields"]

        for field, field_type in fields.items():
            value = data.get(field)

            if type(value) not in (int, float):
                raise ValueError(f"Invalid value for {field}")

            if field_type is int and type(value) is not int:
                raise ValueError(f"{field} must be a whole number")

            # Weapon attack speed must be greater than zero
            if field == "attack_speed" and value <= 0:
                raise ValueError("Attack speed must be positive")

            # Potion stats can be negative to represent debuffs
            if item_type != "potion" and field != "attack_speed" and value < 0:
                raise ValueError(f"{field} cannot be negative")

    def add_item(self, item_type, item_id, data):
        # Check for empty or duplicate item IDs
        if not item_id.strip():
            raise ValueError("Item ID cannot be empty")

        for existing_type in ITEM_TYPES:
            if item_id in self.load_items(existing_type):
                raise ValueError("Item ID already exists")

        self.validate_item(item_type, data)

        # Save the new item
        items = self.load_items(item_type)
        items[item_id] = data
        self.save_items(item_type, items)

    def edit_item(self, item_id, changes):
        # Find the existing item
        item_type, items, old_data = self.find_item(item_id)

        # Only allow changes to supported properties
        allowed = {"name", "description", *ITEM_TYPES[item_type]["fields"]}

        if not changes.keys() <= allowed:
            raise ValueError("Unknown item property")

        # Keep the old values and apply only the changes
        updated = old_data.copy()
        updated.update(changes)

        self.validate_item(item_type, updated)

        # Replace the item data and save it
        items[item_id] = updated
        self.save_items(item_type, items)


def main():
    editor = ItemEditor()

    while True:
        print("\n--- Item Editor ---")
        print("1. List items")
        print("2. Add item")
        print("3. Edit item")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                editor.list_items()

            elif choice == "2":
                print("Available types:", ", ".join(ITEM_TYPES))
                item_type = input("Item type: ").strip().lower()

                if item_type not in ITEM_TYPES:
                    print("Invalid item type.")
                    continue

                item_id = input("Item ID: ").strip()

                data = {
                    "name": input("Name: ").strip(),
                    "description": input("Description: ").strip(),
                }

                # Ask for the stats defined for this category
                for field, field_type in ITEM_TYPES[item_type]["fields"].items():
                    data[field] = field_type(input(f"{field}: "))

                # Add the game's item classification if configured
                game_type = ITEM_TYPES[item_type].get("item_type")

                if game_type:
                    data["type"] = game_type

                editor.add_item(item_type, item_id, data)
                print("Item added.")

            elif choice == "3":
                item_id = input("Item ID to edit: ").strip()
                item_type, _, current = editor.find_item(item_id)

                print("Leave blank to keep the current value.")
                changes = {}

                fields = ITEM_TYPES[item_type]["fields"]

                # Go through each property and ask for changes
                for key in ("name", "description", *fields):
                    old_value = current.get(key, "")
                    answer = input(f"{key} ({old_value}): ").strip()

                    if answer:
                        if key in fields:
                            changes[key] = fields[key](answer)
                        else:
                            changes[key] = answer

                editor.edit_item(item_id, changes)
                print("Item updated.")

            elif choice == "4":
                print("Closing editor.")
                break

            else:
                print("Invalid option.")

        except (ValueError, OSError, json.JSONDecodeError, KeyError) as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
