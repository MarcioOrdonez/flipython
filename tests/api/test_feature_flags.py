from typing import Generator
from hashlib import sha256

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models.base import Base
from app.db.models.api_key import ApiKey
from app.db.session import get_session
from app.main import app

AUTH_HEADERS = {"Authorization": "Bearer test-token"}


def make_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        session.add(
            ApiKey(
                name="test-client",
                env="dev",
                key_hash="v1:" + sha256("test-token".encode("utf-8")).hexdigest(),
                enabled=True,
            )
        )
        session.commit()

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
        headers=AUTH_HEADERS,
        json={"key": "new-checkout", "enabled": False},
    )

    assert response.status_code == 201
    assert response.json()["key"] == "new-checkout"
    assert response.json()["enabled"] is False


def test_list_feature_flags():
    client = make_client()
    client.post("/feature-flags", headers=AUTH_HEADERS, json={"key": "second"})
    client.post("/feature-flags", headers=AUTH_HEADERS, json={"key": "first"})

    response = client.get("/feature-flags", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert [flag["key"] for flag in response.json()] == ["first", "second"]


def test_update_feature_flag():
    client = make_client()
    create_response = client.post(
        "/feature-flags",
        headers=AUTH_HEADERS,
        json={"key": "new-checkout"},
    )
    flag_id = create_response.json()["id"]

    response = client.put(
        f"/feature-flags/{flag_id}",
        headers=AUTH_HEADERS,
        json={"key": "new-checkout-v2", "enabled": False},
    )

    assert response.status_code == 200
    assert response.json()["key"] == "new-checkout-v2"
    assert response.json()["enabled"] is False


def test_delete_feature_flag():
    client = make_client()
    create_response = client.post(
        "/feature-flags",
        headers=AUTH_HEADERS,
        json={"key": "new-checkout"},
    )
    flag_id = create_response.json()["id"]

    response = client.delete(f"/feature-flags/{flag_id}", headers=AUTH_HEADERS)

    assert response.status_code == 204
    assert client.get("/feature-flags", headers=AUTH_HEADERS).json() == []


def test_update_missing_feature_flag_returns_404():
    client = make_client()

    response = client.put(
        "/feature-flags/00000000-0000-0000-0000-000000000000",
        headers=AUTH_HEADERS,
        json={"key": "new-checkout", "enabled": False},
    )

    assert response.status_code == 404


def test_create_duplicate_feature_flag_key_returns_409():
    client = make_client()
    client.post("/feature-flags", headers=AUTH_HEADERS, json={"key": "new-checkout"})

    response = client.post(
        "/feature-flags",
        headers=AUTH_HEADERS,
        json={"key": "new-checkout"},
    )

    assert response.status_code == 409


def test_feature_flag_routes_require_authorization_header():
    client = make_client()

    response = client.get("/feature-flags")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization header"


def test_feature_flag_routes_reject_invalid_token():
    client = make_client()

    response = client.get(
        "/feature-flags",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
