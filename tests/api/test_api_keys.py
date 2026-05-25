from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.api.api_keys import ApiKeyCreate, get_repository, router
from app.domain.api_key import ApiKey, Env


class _DummySession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class _SuccessRepository:
    def __init__(self) -> None:
        self.session = _DummySession()

    def add(self, api_key: ApiKey) -> ApiKey:
        return api_key


class _FailingRepository:
    def __init__(self) -> None:
        self.session = _DummySession()

    def add(self, api_key: ApiKey) -> ApiKey:
        raise IntegrityError("insert", {}, Exception("duplicate"))


def make_client_with_repository(repository: object) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_repository] = lambda: repository
    return TestClient(app)


def test_create_api_key_returns_201_and_payload_shape() -> None:
    repository = _SuccessRepository()
    client = make_client_with_repository(repository)

    response = client.post(
        "/api-keys",
        json={"name": "service-a", "env": Env.DEV.value},
    )

    assert response.status_code == 201
    assert response.json() == ApiKeyCreate(name="service-a", env=Env.DEV).model_dump(
        mode="json"
    )
    assert repository.session.committed is True
    assert repository.session.rolled_back is False


def test_create_api_key_duplicate_returns_409_and_rolls_back() -> None:
    repository = _FailingRepository()
    client = make_client_with_repository(repository)

    response = client.post(
        "/api-keys",
        json={"name": "service-a", "env": Env.PROD.value},
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "API key with the same name and environment already exists."
    )
    assert repository.session.committed is False
    assert repository.session.rolled_back is True
