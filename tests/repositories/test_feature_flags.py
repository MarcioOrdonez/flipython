from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.feature_flag import FeatureFlag as FeatureFlagModel
from app.domain.feature_flag import FeatureFlag
from app.repositories.feature_flags import FeatureFlagRepository


def make_repository():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    return FeatureFlagRepository(session_factory())


def test_add_and_get_feature_flag_by_key():
    repository = make_repository()
    flag = FeatureFlag.create("new-checkout")

    repository.add(flag)

    persisted_flag = repository.get_by_key("new-checkout")

    assert persisted_flag == flag


def test_save_updates_existing_feature_flag():
    repository = make_repository()
    flag = FeatureFlag.create("new-checkout")
    repository.add(flag)

    flag.enabled = False
    saved_flag = repository.save(flag)

    assert saved_flag == flag
    assert repository.get(flag.id) == flag


def test_list_orders_feature_flags_by_key():
    repository = make_repository()
    repository.add(FeatureFlag.create("second"))
    repository.add(FeatureFlag.create("first"))

    flags = repository.list()

    assert [flag.key for flag in flags] == ["first", "second"]


def test_delete_removes_feature_flag():
    repository = make_repository()
    flag = repository.add(FeatureFlag.create("new-checkout"))

    repository.delete(flag.id)

    assert repository.get(flag.id) is None


def test_save_creates_feature_flag_when_missing():
    repository = make_repository()
    flag = FeatureFlag.create("new-checkout")

    saved_flag = repository.save(flag)

    assert saved_flag == flag


def test_repository_maps_database_rows_to_domain_objects():
    repository = make_repository()
    model = FeatureFlagModel(key="new-checkout", enabled=False)
    repository.session.add(model)
    repository.session.flush()

    flag = repository.get_by_key("new-checkout")

    assert flag == FeatureFlag(
        id=model.id,
        key="new-checkout",
        enabled=False,
    )
