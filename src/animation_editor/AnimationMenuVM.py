
from src.animation_editor.AnimationEditorVM import Observable


class AnimationMenuVM:
    def __init__(self, menus, editor_vm):
        self.menus = menus
        self.editor_vm = editor_vm
        self.open_menu = Observable(None)
        self.hover_item = Observable(None)

        e = editor_vm
        self._actions = {
            "edit.undo": (e.undo, lambda: bool(e._undo)),
            "edit.redo": (e.redo, lambda: bool(e._redo)),
            "view.onion": (lambda: e.onion(not e.onion.get()), lambda: bool(e._onion)),
            "file.save": (e.save, lambda: bool(e._save)),
            "app.quit": (self.request_quit, lambda: True),

        }
        self.quit_requested = False

        #state the view reads
        def is_enabled(self, item):
            entry = self._actions.get(item.action)
            return bool(entry and entry[1])

        def is_checked(self,item):
            return item.action == "view.onino" and self.editor.onino.get()

        def toggle_menu(self, i):
            if self.open_menu.get() is not None:
                self.open_menu.set(i)

        def hover_menu(self, i):
            if self.open_menu.get() is not None:
                self.open_menu.set(i)

        def activate(self, item):
            if self.is_enabled(item):
                self._actions[item.action][0]()
                self.close()

        def close(self):
            self.open_menu.set(None)
            self.hover_item.set(None)

        def request_quit(self):
            self.quit_requested = True
