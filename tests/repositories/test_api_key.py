from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.api_key import ApiKey as ApiKeyModel
from app.db.models.base import Base
from app.domain.api_key import ApiKey, Env
from app.repositories.api_key import ApiKeyRepository


def make_repository() -> ApiKeyRepository:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    return ApiKeyRepository(session_factory())


def test_add_persists_api_key_and_returns_domain_object() -> None:
    repository = make_repository()
    api_key = ApiKey.create("service-a", Env.DEV)

    saved = repository.add(api_key)

    assert saved == api_key


def test_save_updates_existing_api_key() -> None:
    repository = make_repository()
    api_key = repository.add(ApiKey.create("service-a", Env.DEV))

    updated = ApiKey(
        id=api_key.id,
        name="service-a-updated",
        env=Env.PROD,
        key_hash=api_key.key_hash,
        enabled=False,
    )

    saved = repository.save(updated)

    assert saved == updated


def test_save_adds_api_key_when_missing() -> None:
    repository = make_repository()
    api_key = ApiKey.create("service-a", Env.STAGING)

    saved = repository.save(api_key)

    assert saved == api_key


def test_delete_removes_existing_api_key() -> None:
    repository = make_repository()
    api_key = repository.add(ApiKey.create("service-a", Env.DEV))

    repository.delete(api_key.id)

    assert repository.session.get(ApiKeyModel, api_key.id) is None


def test_delete_missing_api_key_is_noop() -> None:
    repository = make_repository()

    repository.delete(ApiKey.create("service-a", Env.DEV).id)

    assert repository.session.query(ApiKeyModel).count() == 0


def test_repository_maps_database_row_to_env_enum() -> None:
    repository = make_repository()
    model = ApiKeyModel(
        name="service-a",
        env="staging",
        key_hash="v1:abc",
        enabled=True,
    )
    repository.session.add(model)
    repository.session.flush()

    domain = repository.save(
        ApiKey(
            id=model.id,
            name=model.name,
            env=Env.STAGING,
            key_hash=model.key_hash,
            enabled=model.enabled,
        )
    )

    assert isinstance(domain.env, Env)
    assert domain.env == Env.STAGING
