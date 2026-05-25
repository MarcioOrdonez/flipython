import uuid
from dataclasses import dataclass


@dataclass
class FeatureFlag:
    id: uuid.UUID
    key: str
    enabled: bool

    @classmethod
    def create(cls, key: str) -> "FeatureFlag":
        return cls(id=uuid.uuid4(), key=key, enabled=True)
