from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.db.session import get_session
from app.repositories.api_key import ApiKeyRepository
from app.domain.api_key import Env, ApiKey


router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class ApiKeyCreate(BaseModel):
    name: str
    env: Env


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    env: Env
    enabled: bool
    token: str


def get_repository(session: Session = Depends(get_session)) -> ApiKeyRepository:
    return ApiKeyRepository(session)


@router.post(
    "",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_api_key(
    payload: ApiKeyCreate,
    repository: ApiKeyRepository = Depends(get_repository),
):
    api_key, token = ApiKey.create(payload.name, payload.env)

    try:
        created_key = repository.add(api_key)
        repository.session.commit()
    except IntegrityError as exc:
        repository.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="API key with the same name and environment already exists.",
        ) from exc
    return ApiKeyResponse(
        id=str(created_key.id),
        name=created_key.name,
        env=created_key.env,
        enabled=created_key.enabled,
        token=token,
    )
