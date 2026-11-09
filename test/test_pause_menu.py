import pygame

from src.pause_menu import PauseAction, PauseMenu

SCREEN_SIZE = (1280, 720)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def click(pos, button=1):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button)


def hover(pos):
    return pygame.event.Event(
        pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)
    )


def make_menu(screen):
    return PauseMenu()


def test_has_continue_and_quit_buttons(screen):
    menu = make_menu(screen)

    assert [label for label, _ in menu.BUTTONS] == ["Continue", "Quit"]
    assert [action for _, action in menu.BUTTONS] == [
        PauseAction.CONTINUE,
        PauseAction.QUIT,
    ]


def test_starts_on_continue(screen):
    assert make_menu(screen).selected_index == 0


def test_down_and_up_move_selection_and_wrap(screen):
    menu = make_menu(screen)

    menu.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)
    assert menu.selected_index == 1
    menu.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)  # wraps to top
    assert menu.selected_index == 0
    menu.handle_event(key(pygame.K_UP), SCREEN_SIZE)  # wraps to bottom
    assert menu.selected_index == 1


def test_w_and_s_also_move_selection(screen):
    menu = make_menu(screen)

    menu.handle_event(key(pygame.K_s), SCREEN_SIZE)
    assert menu.selected_index == 1
    menu.handle_event(key(pygame.K_w), SCREEN_SIZE)
    assert menu.selected_index == 0


def test_navigation_keys_do_not_activate(screen):
    menu = make_menu(screen)

    assert menu.handle_event(key(pygame.K_DOWN), SCREEN_SIZE) is None
    assert menu.handle_event(key(pygame.K_UP), SCREEN_SIZE) is None


def test_enter_activates_selected_button(screen):
    menu = make_menu(screen)
    assert menu.handle_event(key(pygame.K_RETURN), SCREEN_SIZE) == PauseAction.CONTINUE

    menu.handle_event(key(pygame.K_DOWN), SCREEN_SIZE)
    assert menu.handle_event(key(pygame.K_RETURN), SCREEN_SIZE) == PauseAction.QUIT
    assert menu.handle_event(key(pygame.K_SPACE), SCREEN_SIZE) == PauseAction.QUIT


def test_click_activates_the_clicked_button(screen):
    menu = make_menu(screen)
    continue_rect, quit_rect = menu.button_rects(SCREEN_SIZE)

    assert menu.handle_event(click(quit_rect.center), SCREEN_SIZE) == PauseAction.QUIT
    assert menu.selected_index == 1
    assert (
        menu.handle_event(click(continue_rect.center), SCREEN_SIZE)
        == PauseAction.CONTINUE
    )
    assert menu.selected_index == 0


def test_click_outside_buttons_does_nothing(screen):
    menu = make_menu(screen)

    assert menu.handle_event(click((0, 0)), SCREEN_SIZE) is None
    assert menu.selected_index == 0


def test_right_click_does_nothing(screen):
    menu = make_menu(screen)
    _, quit_rect = menu.button_rects(SCREEN_SIZE)

    assert menu.handle_event(click(quit_rect.center, button=3), SCREEN_SIZE) is None


def test_hover_moves_highlight_without_activating(screen):
    menu = make_menu(screen)
    _, quit_rect = menu.button_rects(SCREEN_SIZE)

    assert menu.handle_event(hover(quit_rect.center), SCREEN_SIZE) is None
    assert menu.selected_index == 1


def test_hover_over_empty_space_keeps_selection(screen):
    menu = make_menu(screen)
    menu.selected_index = 1

    menu.handle_event(hover((0, 0)), SCREEN_SIZE)

    assert menu.selected_index == 1


def test_reset_returns_to_continue(screen):
    menu = make_menu(screen)
    menu.selected_index = 1

    menu.reset()

    assert menu.selected_index == 0


def test_buttons_are_inside_panel_and_do_not_overlap(screen):
    menu = make_menu(screen)
    panel = menu._panel_rect(SCREEN_SIZE)
    rects = menu.button_rects(SCREEN_SIZE)

    assert all(panel.contains(r) for r in rects)
    assert not rects[0].colliderect(rects[1])
    assert panel.center[0] == (SCREEN_SIZE[0] // 2)


def test_draw_dims_the_screen_and_draws_panel(screen):
    menu = make_menu(screen)
    screen.fill((200, 200, 200))

    menu.draw(screen)

    assert tuple(screen.get_at((0, 0)))[:3] < (200, 200, 200)  # dimmed overlay
    panel = menu._panel_rect(SCREEN_SIZE)
    assert tuple(screen.get_at((panel.x + 10, panel.y + 10)))[:3] != (200, 200, 200)


def test_draw_highlights_selected_button(screen):
    menu = make_menu(screen)
    continue_rect, quit_rect = menu.button_rects(SCREEN_SIZE)
    # Sample a corner-ish spot inside each button, clear of the label text.
    spot = lambda r: (r.x + 8, r.y + 8)

    menu.selected_index = 0
    menu.draw(screen)
    assert tuple(screen.get_at(spot(continue_rect)))[:3] == (113, 78, 34)
    assert tuple(screen.get_at(spot(quit_rect)))[:3] == (47, 43, 48)

    menu.selected_index = 1
    menu.draw(screen)
    assert tuple(screen.get_at(spot(continue_rect)))[:3] == (47, 43, 48)
    assert tuple(screen.get_at(spot(quit_rect)))[:3] == (113, 78, 34)
