import pygame

from src.object_class.inventory import Inventory
from src.object_class.item import Item
from src.ui.inventory_ui import InventoryUI

SCREEN_SIZE = (1280, 720)


class FakeCharacter:
    """Just enough of Character for the UI: an inventory and equip_item."""

    def __init__(self, inventory):
        self.inventory = inventory
        self.equipped_item = None

    def equip_item(self, item):
        if not self.inventory.has_item(item):
            return False
        self.equipped_item = item
        return True


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def click(pos, button=1):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button)


def make_ui(count=3):
    inventory = Inventory()
    items = [Item(f"Item {i}") for i in range(count)]
    for item in items:
        inventory.add_item(item)
    character = FakeCharacter(inventory)
    return InventoryUI(inventory, character), character, items


# ---------- selection
def test_selection_starts_on_first_item(screen):
    ui, _, _ = make_ui(3)

    assert ui.selected_index == 0


def test_selection_is_none_for_empty_inventory(screen):
    ui, _, _ = make_ui(0)

    assert ui.selected_index is None


def test_down_and_up_move_selection_and_wrap(screen):
    ui, _, _ = make_ui(3)

    assert ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE) is False
    assert ui.selected_index == 1
    ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)
    ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)  # wraps to the top
    assert ui.selected_index == 0
    assert ui.handle_event(key(pygame.K_UP), SCREEN_SIZE) is False  # wraps to bottom
    assert ui.selected_index == 2


def test_arrow_keys_do_nothing_on_empty_inventory(screen):
    ui, _, _ = make_ui(0)

    assert ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE) is False
    assert ui.handle_event(key(pygame.K_UP), SCREEN_SIZE) is False
    assert ui.selected_index is None


def test_moving_down_scrolls_list_to_keep_selection_visible(screen):
    ui, _, _ = make_ui(7)  # only 5 rows fit

    for _ in range(5):
        ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)

    assert ui.selected_index == 5
    assert ui.scroll_offset == 1


def test_wrapping_up_scrolls_to_the_bottom(screen):
    ui, _, _ = make_ui(7)

    ui.handle_event(key(pygame.K_UP), SCREEN_SIZE)

    assert ui.selected_index == 6
    assert ui.scroll_offset == 2


# ---------- keyboard equip
def test_enter_equips_selected_item(screen):
    ui, character, items = make_ui(3)
    ui.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)

    assert ui.handle_event(key(pygame.K_RETURN), SCREEN_SIZE) is True
    assert character.equipped_item is items[1]
    assert ui.message == "Equipped Item 1."


def test_e_key_also_equips(screen):
    ui, character, items = make_ui(2)

    assert ui.handle_event(key(pygame.K_e), SCREEN_SIZE) is True
    assert character.equipped_item is items[0]


def test_equip_with_empty_inventory_reports_message(screen):
    ui, character, _ = make_ui(0)

    assert ui.handle_event(key(pygame.K_RETURN), SCREEN_SIZE) is False
    assert character.equipped_item is None
    assert ui.message == "Your inventory is empty."


def test_equip_fails_when_character_does_not_have_item(screen):
    inventory = Inventory()
    inventory.add_item(Item("Rock"))
    ui = InventoryUI(inventory, FakeCharacter(Inventory()))

    assert ui.equip_selected() is False
    assert ui.message == "That item is no longer in your inventory."


def test_unrelated_events_are_ignored(screen):
    ui, character, _ = make_ui(3)
    motion = pygame.event.Event(
        pygame.MOUSEMOTION, pos=(5, 5), rel=(0, 0), buttons=(0, 0, 0)
    )

    assert ui.handle_event(motion, SCREEN_SIZE) is False
    assert ui.handle_event(key(pygame.K_a), SCREEN_SIZE) is False
    assert ui.selected_index == 0
    assert ui.message == ""
    assert character.equipped_item is None


# ---------- mouse
def test_clicking_a_row_selects_it_without_equipping(screen):
    ui, character, _ = make_ui(3)
    panel = ui._panel_rect(SCREEN_SIZE)

    result = ui.handle_event(click(ui._row_rect(panel, 2).center), SCREEN_SIZE)

    assert result is False
    assert ui.selected_index == 2
    assert character.equipped_item is None


def test_clicking_equip_button_equips_selected_item(screen):
    ui, character, items = make_ui(3)
    panel = ui._panel_rect(SCREEN_SIZE)
    ui.handle_event(click(ui._row_rect(panel, 2).center), SCREEN_SIZE)

    result = ui.handle_event(click(ui._equip_button_rect(panel).center), SCREEN_SIZE)

    assert result is True
    assert character.equipped_item is items[2]


def test_clicking_equip_button_with_empty_inventory_reports_message(screen):
    ui, _, _ = make_ui(0)
    panel = ui._panel_rect(SCREEN_SIZE)

    result = ui.handle_event(click(ui._equip_button_rect(panel).center), SCREEN_SIZE)

    assert result is False
    assert ui.message == "Your inventory is empty."


def test_click_outside_rows_and_button_does_nothing(screen):
    ui, character, _ = make_ui(3)

    assert ui.handle_event(click((0, 0)), SCREEN_SIZE) is False
    assert ui.selected_index == 0
    assert character.equipped_item is None


def test_right_click_is_ignored(screen):
    ui, character, _ = make_ui(3)
    panel = ui._panel_rect(SCREEN_SIZE)

    result = ui.handle_event(
        click(ui._equip_button_rect(panel).center, button=3), SCREEN_SIZE
    )

    assert result is False
    assert character.equipped_item is None


def test_clicking_a_row_accounts_for_scroll_offset(screen):
    ui, _, _ = make_ui(7)
    ui.scroll_offset = 2
    panel = ui._panel_rect(SCREEN_SIZE)

    ui.handle_event(click(ui._row_rect(panel, 0).center), SCREEN_SIZE)

    assert ui.selected_index == 2


def test_row_at_returns_none_outside_visible_rows(screen):
    ui, _, _ = make_ui(2)
    panel = ui._panel_rect(SCREEN_SIZE)

    assert ui._row_at(panel, ui._row_rect(panel, 1).center) == 1
    assert ui._row_at(panel, ui._row_rect(panel, 4).center) is None  # no 5th item
    assert ui._row_at(panel, (0, 0)) is None


# ---------- drawing
def test_draw_with_items_and_empty_inventory_does_not_crash(screen):
    ui, _, _ = make_ui(3)
    ui.draw(screen)

    empty_ui, _, _ = make_ui(0)
    empty_ui.draw(screen)


def test_draw_clamps_selection_after_items_are_removed(screen):
    ui, _, items = make_ui(3)
    ui.selected_index = 2
    ui.inventory.remove_item(items[1])
    ui.inventory.remove_item(items[2])

    ui.draw(screen)

    assert ui.selected_index == 0
