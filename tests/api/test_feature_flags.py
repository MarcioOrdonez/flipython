from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models.base import Base
from app.db.session import get_session
from app.main import app


def make_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_get_session() -> Generator[Session, None, None]:
        session = session_factory()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    return TestClient(app)


def test_create_feature_flag():
    client = make_client()

    response = client.post(
        "/feature-flags",
        json={"key": "new-checkout", "enabled": False},
    )

    assert response.status_code == 201
    assert response.json()["key"] == "new-checkout"
    assert response.json()["enabled"] is False


def test_list_feature_flags():
    client = make_client()
    client.post("/feature-flags", json={"key": "second"})
    client.post("/feature-flags", json={"key": "first"})

    response = client.get("/feature-flags")

    assert response.status_code == 200
    assert [flag["key"] for flag in response.json()] == ["first", "second"]


def test_update_feature_flag():
    client = make_client()
    create_response = client.post("/feature-flags", json={"key": "new-checkout"})
    flag_id = create_response.json()["id"]

    response = client.put(
        f"/feature-flags/{flag_id}",
        json={"key": "new-checkout-v2", "enabled": False},
    )

    assert response.status_code == 200
    assert response.json()["key"] == "new-checkout-v2"
    assert response.json()["enabled"] is False


def test_delete_feature_flag():
    client = make_client()
    create_response = client.post("/feature-flags", json={"key": "new-checkout"})
    flag_id = create_response.json()["id"]

    response = client.delete(f"/feature-flags/{flag_id}")

    assert response.status_code == 204
    assert client.get("/feature-flags").json() == []


def test_update_missing_feature_flag_returns_404():
    client = make_client()

    response = client.put(
        "/feature-flags/00000000-0000-0000-0000-000000000000",
        json={"key": "new-checkout", "enabled": False},
    )

    assert response.status_code == 404


def test_create_duplicate_feature_flag_key_returns_409():
    client = make_client()
    client.post("/feature-flags", json={"key": "new-checkout"})

    response = client.post("/feature-flags", json={"key": "new-checkout"})

    assert response.status_code == 409
