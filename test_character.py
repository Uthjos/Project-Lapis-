from src.object_class.Character import Character


# checks that the character starts with the correct values
def test_character_starting_values():
    player = Character()

    assert player.x == 0
    assert player.y == 0
    assert player.health == 100


# checks that the character can move
def test_character_movement():
    player = Character()

    player.move(5, 10)

    assert player.x == 5
    assert player.y == 10


# checks that taking damage lowers health
def test_character_takes_damage():
    player = Character()

    player.take_damage(25)

    assert player.health == 75


# checks that health cannot go below 0
def test_character_health_does_not_go_below_zero():
    player = Character()

    player.take_damage(150)

    assert player.health == 0


# checks if the character is alive or dead
def test_character_is_alive():
    player = Character()

    assert player.is_alive() is True

    player.take_damage(100)

    assert player.is_alive() is False
