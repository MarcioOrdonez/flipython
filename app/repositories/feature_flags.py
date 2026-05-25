import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.feature_flag import FeatureFlag as FeatureFlagModel
from app.domain.feature_flag import FeatureFlag


class FeatureFlagRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, flag: FeatureFlag) -> FeatureFlag:
        model = self._to_model(flag)
        self.session.add(model)
        self.session.flush()

        return self._to_domain(model)

    def save(self, flag: FeatureFlag) -> FeatureFlag:
        model = self.session.get(FeatureFlagModel, flag.id)

        if model is None:
            return self.add(flag)

        model.key = flag.key
        model.enabled = flag.enabled
        self.session.flush()

        return self._to_domain(model)

    def get(self, flag_id: uuid.UUID) -> Optional[FeatureFlag]:
        model = self.session.get(FeatureFlagModel, flag_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_key(self, key: str) -> Optional[FeatureFlag]:
        statement = select(FeatureFlagModel).where(FeatureFlagModel.key == key)
        model = self.session.scalars(statement).one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    def list(self) -> List[FeatureFlag]:
        statement = select(FeatureFlagModel).order_by(FeatureFlagModel.key)
        models = self.session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def delete(self, flag_id: uuid.UUID) -> None:
        model = self.session.get(FeatureFlagModel, flag_id)

        if model is None:
            return

        self.session.delete(model)
        self.session.flush()

    @staticmethod
    def _to_model(flag: FeatureFlag) -> FeatureFlagModel:
        return FeatureFlagModel(
            id=flag.id,
            key=flag.key,
            enabled=flag.enabled,
        )

    @staticmethod
    def _to_domain(model: FeatureFlagModel) -> FeatureFlag:
        return FeatureFlag(
            id=model.id,
            key=model.key,
            enabled=model.enabled,
        )
