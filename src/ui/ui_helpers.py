"""Drawing helpers shared by the overlay menus (pause menu, inventory)."""

import pygame


def panel_rect(screen_size, panel_width, panel_height):
    """Return a panel Rect centred on the screen."""
    width, height = screen_size
    return pygame.Rect(
        (width - panel_width) // 2,
        (height - panel_height) // 2,
        panel_width,
        panel_height,
    )


def draw_label(surface, text, font, color, position, centered=False):
    """Render text at position (top-left, or centre when centered=True)."""
    image = font.render(text, True, color)
    rect = (
        image.get_rect(center=position)
        if centered
        else image.get_rect(topleft=position)
    )
    surface.blit(image, rect)


def dim_screen(surface, alpha=150):
    """Darken the whole surface so an overlay stands out."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))
