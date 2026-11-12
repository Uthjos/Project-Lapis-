from src.object_class.entity import Entity


class FakeMap:
    """Collision map that only allows standing at x >= 0."""

    def is_walkable(self, px, py):
        return px >= 0


def test_entity_defaults():
    e = Entity()

    assert (e.x, e.y) == (0, 0)
    assert e.health == 100
    assert e.max_health == 100
    assert e.collision_map is None


def test_hitboxes_follow_position():
    e = Entity(10, 20)

    assert e.hurtbox.topleft == (10, 20)
    assert e.hurtbox.size == (32, 32)
    assert e.movement_hitbox.midbottom == (26, 52)
    assert e.movement_hitbox.size == (32, 16)


def test_take_damage_and_floor_at_zero():
    e = Entity(health=50)

    e.take_damage(20)
    assert e.health == 30

    e.take_damage(999)
    assert e.health == 0
    assert e.is_alive() is False


def test_max_health_unchanged_by_damage():
    e = Entity(health=40)
    e.take_damage(10)

    assert e.max_health == 40


def test_can_stand_without_map_is_always_true():
    assert Entity()._can_stand(-1000, 0) is True


def test_can_stand_uses_collision_map():
    e = Entity(0, 0)
    e.set_collision_map(FakeMap())
    # Feet box spans x 0..31, so moving left would push a corner below x=0.
    assert e._can_stand(0, 0) is True
    assert e._can_stand(-1, 0) is False
    assert e._can_stand(5, 0) is True
