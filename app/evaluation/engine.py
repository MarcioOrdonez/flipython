import hashlib


# TODO: add rollout implementation.
def is_enabled(
    flag_key: str,
    user_id: str,
    rollout_percentage: int,
) -> bool:
    key = f"{flag_key}:{user_id}"

    hash_value = hashlib.sha256(key.encode()).hexdigest()

    bucket = int(hash_value, 16) % 100

    return bucket < rollout_percentage
