from dataclasses import dataclass


@dataclass
class AnimationMenuItem:
    label: str
    action: str | None = None
    shortcut: str = ""

@dataclass
class Menu:
    title: str
    items: list[AnimationMenuItem]

ANIMATION_MENU = [
    Menu("File", [
        AnimationMenuItem("New", "file.new", "Ctrl+N"),
        AnimationMenuItem("Open", "file.open", "Ctrl+O"),
        AnimationMenuItem("Save", "file.save", "Ctrl+S"),
        AnimationMenuItem("-"),
        AnimationMenuItem("Export", "file.export"),
        AnimationMenuItem("Quit", "app.quit"),
    ]),

    Menu("Edit", [
        AnimationMenuItem("Undo", "file.undo", "Ctrl+Z"),
        AnimationMenuItem("Redo", "file.redo", "Ctrl+Y"),
    ]),

    Menu("View", [
        AnimationMenuItem("Onion Skin", "view.onion", "O"),
    ])
]