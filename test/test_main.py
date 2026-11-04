import pytest

from src import main as main_module
from src.game_scene import main_game
from src.main_menu_scene import main_menu
from src.scenes import Scene


def test_scene_table_maps_scenes_to_functions():
    assert main_module.SCENES[Scene.MENU] is main_menu
    assert main_module.SCENES[Scene.GAME] is main_game


def test_every_playable_scene_is_registered():
    for scene in Scene:
        if scene != Scene.QUIT:
            assert scene in main_module.SCENES


def test_main_runs_scenes_until_quit(monkeypatch):
    visited = []

    def fake_menu(screen):
        visited.append("menu")
        return Scene.GAME

    def fake_game(screen):
        visited.append("game")
        return Scene.QUIT

    monkeypatch.setitem(main_module.SCENES, Scene.MENU, fake_menu)
    monkeypatch.setitem(main_module.SCENES, Scene.GAME, fake_game)

    with pytest.raises(SystemExit):
        main_module.main()

    assert visited == ["menu", "game"]
