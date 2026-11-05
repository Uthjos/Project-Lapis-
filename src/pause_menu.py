"""Pygame pause menu overlay with Continue and Quit buttons."""

from enum import Enum, auto

import pygame


class PauseAction(Enum):
    CONTINUE = auto()
    QUIT = auto()


class PauseMenu:
    PANEL_WIDTH = 320
    PANEL_HEIGHT = 240
    BUTTON_WIDTH = 220
    BUTTON_HEIGHT = 48
    BUTTON_GAP = 18
    BUTTONS = (("Continue", PauseAction.CONTINUE), ("Quit", PauseAction.QUIT))

    def __init__(self):
        self.selected_index = 0
        self.title_font = pygame.font.Font(None, 42)
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 21)

    def reset(self):
        """Put the highlight back on Continue. Call whenever the menu is opened."""
        self.selected_index = 0

    def handle_event(self, event, screen_size):
        """Return a PauseAction when a button is activated, otherwise None."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.BUTTONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.BUTTONS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.BUTTONS[self.selected_index][1]
            return None

        if event.type == pygame.MOUSEMOTION:
            index = self._button_at(event.pos, screen_size)
            if index is not None:
                self.selected_index = index
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._button_at(event.pos, screen_size)
            if index is not None:
                self.selected_index = index
                return self.BUTTONS[index][1]
        return None

    def draw(self, surface):
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        panel = self._panel_rect((width, height))
        pygame.draw.rect(surface, (28, 25, 32), panel, border_radius=8)
        pygame.draw.rect(surface, (191, 157, 91), panel, width=3, border_radius=8)
        self._label(surface, "Paused", self.title_font, (240, 221, 177),
                    (panel.centerx, panel.y + 36), centered=True)

        for index, ((text, _), rect) in enumerate(zip(self.BUTTONS, self.button_rects((width, height)))):
            selected = index == self.selected_index
            pygame.draw.rect(surface, (113, 78, 34) if selected else (47, 43, 48), rect, border_radius=5)
            pygame.draw.rect(surface, (232, 190, 104) if selected else (91, 85, 92), rect,
                             width=2, border_radius=5)
            self._label(surface, text, self.font, (255, 245, 221), rect.center, centered=True)

        self._label(surface, "Up/Down: select   |   Enter: confirm   |   Esc: continue",
                    self.small_font, (185, 179, 169), (panel.centerx, panel.bottom + 18), centered=True)

    def button_rects(self, screen_size):
        """One Rect per entry in BUTTONS, stacked and centred inside the panel."""
        panel = self._panel_rect(screen_size)
        top = panel.y + 80
        return [
            pygame.Rect(panel.centerx - self.BUTTON_WIDTH // 2,
                        top + i * (self.BUTTON_HEIGHT + self.BUTTON_GAP),
                        self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            for i in range(len(self.BUTTONS))
        ]

    def _button_at(self, pos, screen_size):
        for index, rect in enumerate(self.button_rects(screen_size)):
            if rect.collidepoint(pos):
                return index
        return None

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