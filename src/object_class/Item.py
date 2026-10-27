"""Simple data model for an item the player can carry."""


class Item:
    def __init__(self, name, item_type="item", description=""):
        if not name:
            raise ValueError("Item name cannot be empty")
        self.name = name
        self.item_type = item_type
        self.description = description

    def __repr__(self):
        return f"Item({self.name!r}, {self.item_type!r})"
