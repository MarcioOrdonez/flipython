from sqlalchemy.orm import Session
import uuid

from app.db.models.api_key import ApiKey as ApiKeyModel
from app.domain.api_key import ApiKey, Env


class ApiKeyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, api_key: ApiKey) -> ApiKey:
        model = self._to_model(api_key)
        self.session.add(model)
        self.session.flush()

        return self._to_domain(model)

    def save(self, api_key: ApiKey) -> ApiKey:
        model = self.session.get(ApiKeyModel, api_key.id)

        if model is None:
            return self.add(api_key)

        model.name = api_key.name
        model.env = api_key.env
        model.key_hash = api_key.key_hash
        model.enabled = api_key.enabled
        self.session.flush()

        return self._to_domain(model)

    def delete(self, api_key_id: uuid.UUID) -> None:
        model = self.session.get(ApiKeyModel, api_key_id)

        if model is None:
            return

        self.session.delete(model)
        self.session.flush()

    @staticmethod
    def _to_model(api_key: ApiKey) -> ApiKeyModel:
        return ApiKeyModel(
            id=api_key.id,
            name=api_key.name,
            env=api_key.env.value,
            key_hash=api_key.key_hash,
            enabled=api_key.enabled,
        )

    @staticmethod
    def _to_domain(model: ApiKeyModel) -> ApiKey:
        return ApiKey(
            id=model.id,
            name=model.name,
            env=Env(model.env),
            key_hash=model.key_hash,
            enabled=model.enabled,
        )
