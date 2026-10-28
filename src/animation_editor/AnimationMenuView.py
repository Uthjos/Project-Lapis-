import pygame


class MenuView:
    BAR_H, ITEM_H, PAD = 24, 22, 12

    def __init__(self, vm, font, width):
        self.vm, self.font = vm, font
        self.bar_rect = pygame.Rect(0, 0, width, self.BAR_H)
        self._layout()

    def _layout(self):
        x = 0
        self.title_rects = []
        for m in self.vm.menus:
            w = self.font.size(m.title)[0] + self.PAD * 2
            self.title_rects.append(pygame.Rect(x, 0, w, self.BAR_H))
            x += w

    def _dropdown_rect(self, i):
        m, tr = self.vm.menus[i], self.title_rects[i]
        w = max(self.font.size(it.label + "    " + it.shortcut)[0] for it in m.items) + self.PAD * 2
        return pygame.Rect(tr.x, self.BAR_H, w, len(m.items) * self.ITEM_H)

    def _item_rects(self, i):
        dd = self._dropdown_rect(i)
        return [pygame.Rect(dd.x, dd.y + k * self.ITEM_H, dd.w, self.ITEM_H)
                for k in range(len(self.vm.menus[i].items))]

    def handle_event(self, e) -> bool:
        """Returns True if the menu consumed the event, so other views don't also react."""
        open_i = self.vm.open_menu.get()

        if e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.title_rects):
                if r.collidepoint(e.pos):
                    self.vm.hover_menu(i)
            if open_i is not None:
                hit = next((k for k, r in enumerate(self._item_rects(open_i))
                            if r.collidepoint(e.pos)), None)
                self.vm.hover_item.set(hit)
            return open_i is not None

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.title_rects):
                if r.collidepoint(e.pos):
                    self.vm.toggle_menu(i)
                    return True
            if open_i is not None:
                for k, r in enumerate(self._item_rects(open_i)):
                    if r.collidepoint(e.pos):
                        item = self.vm.menus[open_i].items[k]
                        if item.action:
                            self.vm.activate(item)
                        return True
                self.vm.close()                # clicked elsewhere: close, and swallow the click
                return True

        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE and open_i is not None:
            self.vm.close()
            return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, (40, 40, 48), self.bar_rect)
        open_i = self.vm.open_menu.get()
        for i, (m, r) in enumerate(zip(self.vm.menus, self.title_rects)):
            if i == open_i:
                pygame.draw.rect(surf, (70, 70, 90), r)
            surf.blit(self.font.render(m.title, True, (230, 230, 230)),
                      (r.x + self.PAD, r.y + 4))

        if open_i is None:
            return
        dd = self._dropdown_rect(open_i)
        pygame.draw.rect(surf, (50, 50, 60), dd)
        for k, (item, r) in enumerate(zip(self.vm.menus[open_i].items, self._item_rects(open_i))):
            if item.action is None:            # separator
                pygame.draw.line(surf, (90, 90, 100), (r.x + 6, r.centery), (r.right - 6, r.centery))
                continue
            enabled = self.vm.is_enabled(item)
            if k == self.vm.hover_item.get() and enabled:
                pygame.draw.rect(surf, (80, 100, 160), r)
            color = (230, 230, 230) if enabled else (110, 110, 120)
            label = ("✓ " if self.vm.is_checked(item) else "") + item.label
            surf.blit(self.font.render(label, True, color), (r.x + self.PAD, r.y + 3))
            if item.shortcut:
                s = self.font.render(item.shortcut, True, color)
                surf.blit(s, (r.right - s.get_width() - self.PAD, r.y + 3))