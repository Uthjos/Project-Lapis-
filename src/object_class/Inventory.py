"""Stores the items carried by a character."""


class Inventory:
    def __init__(self, capacity=20):
        if capacity < 1:
            raise ValueError("Inventory capacity must be at least 1")
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        """Add an item if there is room. Return True when it was added."""
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item):
        """Remove an item if it is in the inventory. Return True on success."""
        try:
            self.items.remove(item)
            return True
        except ValueError:
            return False

    def get_items(self):
        """Return a copy so callers cannot edit the stored list by accident."""
        return list(self.items)

    def has_item(self, item):
        return item in self.items