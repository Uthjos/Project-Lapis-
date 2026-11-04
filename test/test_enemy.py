from src.object_class.Character import Character
from src.object_class.Enemy import Enemy, EnemyState


def make_enemy(**kwargs):
    return Enemy(0, 0, **kwargs)


def test_enemy_defaults():
    enemy = make_enemy()

    assert enemy.state == EnemyState.IDLE
    assert enemy.health == 50
    assert enemy.is_alive()


def test_idle_enemy_ignores_far_player():
    enemy = make_enemy(aggro_range=100)
    player = Character(1000, 0)

    enemy.update(player, 0)

    assert enemy.state == EnemyState.IDLE


def test_idle_enemy_aggros_when_player_close():
    enemy = make_enemy(aggro_range=250)
    player = Character(100, 0)

    enemy.update(player, 0)

    assert enemy.state == EnemyState.CHASE


def test_chasing_enemy_moves_toward_player():
    enemy = make_enemy(speed=1.5)
    player = Character(200, 0)

    enemy.update(player, 0)   # IDLE -> CHASE
    enemy.update(player, 1)   # step toward player

    assert enemy.x > 0
    assert enemy.y == 0


def test_chasing_enemy_leashes_back_to_idle():
    enemy = make_enemy(aggro_range=100)
    player = Character(1000, 0)
    enemy.state = EnemyState.CHASE

    enemy.update(player, 0)

    assert enemy.state == EnemyState.IDLE


def test_enemy_in_range_starts_windup():
    enemy = make_enemy()
    player = Character(30, 0)
    enemy.update(player, 0)   # -> CHASE
    enemy.update(player, 1)   # -> WINDUP

    assert enemy.state == EnemyState.WINDUP


def test_windup_hits_player_then_cooldown_then_chase():
    enemy = make_enemy(damage=10, windup_ms=400, cooldown_ms=1000)
    player = Character(30, 0)
    enemy.update(player, 0)
    enemy.update(player, 1)    # WINDUP starts at t=1

    enemy.update(player, 200)  # still winding up
    assert player.health == 100

    enemy.update(player, 401)  # impact
    assert player.health == 90
    assert enemy.state == EnemyState.COOLDOWN

    enemy.update(player, 1401)
    assert enemy.state == EnemyState.CHASE


def test_player_can_dodge_windup():
    enemy = make_enemy(damage=10, windup_ms=400)
    player = Character(30, 0)
    enemy.update(player, 0)
    enemy.update(player, 1)

    player.x = 500   # move out of range before impact
    player._sync_hitboxes()
    enemy.update(player, 401)

    assert player.health == 100
    assert enemy.state == EnemyState.COOLDOWN


def test_damage_staggers_when_hurt_ms_set():
    enemy = make_enemy(hurt_ms=100)
    player = Character(30, 0)

    enemy.take_damage(5)
    assert enemy.state == EnemyState.HURT

    enemy.update(player, 50)
    assert enemy.state == EnemyState.HURT
    enemy.update(player, 100)
    assert enemy.state == EnemyState.CHASE


def test_damage_does_not_stagger_when_hurt_ms_zero():
    enemy = make_enemy(hurt_ms=0)

    enemy.take_damage(5)

    assert enemy.state == EnemyState.IDLE
    assert enemy.health == 45


def test_lethal_damage_sets_dead_state():
    enemy = make_enemy()

    enemy.take_damage(999)

    assert enemy.state == EnemyState.DEAD
    assert not enemy.is_alive()


def test_dead_enemy_ignores_further_damage_and_updates():
    enemy = make_enemy()
    player = Character(30, 0)
    enemy.take_damage(999)

    enemy.take_damage(10)
    enemy.update(player, 5000)

    assert enemy.health == 0
    assert enemy.state == EnemyState.DEAD
    assert player.health == 100


def test_removable_only_after_death_time():
    enemy = make_enemy(death_ms=500)
    player = Character(30, 0)
    enemy.take_damage(999)

    assert enemy.removable is False
    enemy.update(player, 100)
    assert enemy.removable is False
    enemy.update(player, 500)
    assert enemy.removable is True


def test_living_enemy_is_not_removable():
    assert make_enemy().removable is False
