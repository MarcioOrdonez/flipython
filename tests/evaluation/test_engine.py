from app.evaluation.engine import is_enabled


def test_rollout_is_deterministic():
    result1 = is_enabled("feature", "123", 20)
    result2 = is_enabled("feature", "123", 20)

    assert result1 == result2
