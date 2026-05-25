from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import secrets

import uuid


class Env(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass(frozen=True)
class ApiKey:
    id: uuid.UUID
    name: str
    env: Env
    key_hash: str
    enabled: bool

    @classmethod
    def create(cls, name: str, env: Env) -> "ApiKey":
        id = uuid.uuid4()
        key_hash, token = cls._generate_key_hash()

        return cls(id, name=name, env=env, key_hash=key_hash, enabled=True), token

    @staticmethod
    def _generate_key_hash() -> str:
        token = secrets.token_urlsafe(32)

        key_hash = "v1:" + sha256(token.encode("utf-8")).hexdigest()
        return key_hash, token

    @staticmethod
    def verify_key(key: str, key_hash: str) -> bool:
        if not key_hash.startswith("v1:"):
            return False

        expected_hash = "v1:" + sha256(key.encode("utf-8")).hexdigest()
        return expected_hash == key_hash
