"""Pygame inventory overlay for viewing and equipping carried items."""

import pygame


class InventoryUI:
    PANEL_WIDTH = 440
    PANEL_HEIGHT = 360
    VISIBLE_ROWS = 5

    def __init__(self, inventory, character):
        self.inventory = inventory
        self.character = character
        self.selected_index = 0 if inventory.get_items() else None
        self.scroll_offset = 0
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 21)
        self.equip_button = pygame.Rect(0, 0, 120, 38)
        self.message = ""

    def handle_event(self, event, screen_size):
        """Handle selection and equip clicks. Return True when an item was equipped."""
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_DOWN):
            items = self.inventory.get_items()
            if items:
                current = self.selected_index or 0
                step = -1 if event.key == pygame.K_UP else 1
                self.selected_index = (current + step) % len(items)
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
                elif self.selected_index >= self.scroll_offset + self.VISIBLE_ROWS:
                    self.scroll_offset = self.selected_index - self.VISIBLE_ROWS + 1
            return False

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_e):
            return self.equip_selected()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            panel = self._panel_rect(screen_size)
            items = self.inventory.get_items()
            for visible_index, index in enumerate(
                range(self.scroll_offset, min(len(items), self.scroll_offset + self.VISIBLE_ROWS))
            ):
                row = pygame.Rect(panel.x + 24, panel.y + 72 + visible_index * 42, panel.width - 48, 36)
                if row.collidepoint(event.pos):
                    self.selected_index = index
                    return False
            self.equip_button = pygame.Rect(panel.right - 144, panel.bottom - 54, 120, 36)
            if self.equip_button.collidepoint(event.pos):
                return self.equip_selected()
        return False

    def equip_selected(self):
        items = self.inventory.get_items()
        if self.selected_index is None or not items:
            self.message = "Your inventory is empty."
            return False
        item = items[self.selected_index]
        if self.character.equip_item(item):
            self.message = f"Equipped {item.name}."
            return True
        self.message = "That item is no longer in your inventory."
        return False

    def draw(self, surface):
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        panel = self._panel_rect((width, height))
        pygame.draw.rect(surface, (28, 25, 32), panel, border_radius=8)
        pygame.draw.rect(surface, (191, 157, 91), panel, width=3, border_radius=8)
        self._label(surface, "Inventory", self.font, (240, 221, 177), (panel.x + 24, panel.y + 18))

        items = self.inventory.get_items()
        if not items:
            self._label(surface, "No items yet", self.small_font, (205, 199, 190), (panel.x + 26, panel.y + 83))
        else:
            self.selected_index = min(self.selected_index or 0, len(items) - 1)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            elif self.selected_index >= self.scroll_offset + self.VISIBLE_ROWS:
                self.scroll_offset = self.selected_index - self.VISIBLE_ROWS + 1
            for visible_index, index in enumerate(
                range(self.scroll_offset, min(len(items), self.scroll_offset + self.VISIBLE_ROWS))
            ):
                item = items[index]
                row = pygame.Rect(panel.x + 24, panel.y + 72 + visible_index * 42, panel.width - 48, 36)
                color = (91, 71, 44) if index == self.selected_index else (47, 43, 48)
                pygame.draw.rect(surface, color, row, border_radius=4)
                if index == self.selected_index:
                    pygame.draw.rect(surface, (232, 190, 104), row, width=2, border_radius=4)
                item_type = item.item_type.replace("_", " ").title()
                self._label(surface, item.name, self.small_font, (245, 241, 232), (row.x + 10, row.y + 8))
                type_text = self.small_font.render(item_type, True, (192, 184, 168))
                surface.blit(type_text, (row.right - type_text.get_width() - 10, row.y + 8))

        equipped = getattr(self.character, "equipped_item", None)
        equipped_name = equipped.name if equipped else "None"
        self._label(surface, f"Equipped: {equipped_name}", self.small_font, (220, 214, 200), (panel.x + 24, panel.bottom - 50))
        self.equip_button = pygame.Rect(panel.right - 144, panel.bottom - 54, 120, 36)
        pygame.draw.rect(surface, (113, 78, 34), self.equip_button, border_radius=5)
        pygame.draw.rect(surface, (232, 190, 104), self.equip_button, width=2, border_radius=5)
        self._label(surface, "Equip (E)", self.small_font, (255, 245, 221), self.equip_button.center, centered=True)
        footer = self.message or "Up/Down: select   |   I/Esc: close"
        self._label(surface, footer, self.small_font, (185, 179, 169), (panel.x + 24, panel.bottom + 12))

    def _panel_rect(self, screen_size):
        width, height = screen_size
        return pygame.Rect(
            (width - self.PANEL_WIDTH) // 2,
            (height - self.PANEL_HEIGHT) // 2,
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
        )

    @staticmethod
    def _label(surface, text, font, color, position, centered=False):
        image = font.render(text, True, color)
        rect = image.get_rect(center=position) if centered else image.get_rect(topleft=position)
        surface.blit(image, rect)
