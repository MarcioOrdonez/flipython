import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.service import authenticate
from app.db.session import get_session
from app.domain.feature_flag import FeatureFlag
from app.repositories.feature_flags import FeatureFlagRepository

router = APIRouter(
    prefix="/feature-flags",
    tags=["feature-flags"],
    dependencies=[Depends(authenticate)],
)


class FeatureFlagCreate(BaseModel):
    key: str
    enabled: bool = True


class FeatureFlagByKeyRequest(BaseModel):
    key: str


class FeatureFlagUpdate(BaseModel):
    key: str
    enabled: bool


class FeatureFlagResponse(BaseModel):
    id: uuid.UUID
    key: str
    enabled: bool


def get_repository(
    session: Session = Depends(get_session),
) -> FeatureFlagRepository:
    return FeatureFlagRepository(session)


@router.post(
    "",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feature_flag(
    payload: FeatureFlagCreate,
    repository: FeatureFlagRepository = Depends(get_repository),
) -> FeatureFlag:
    flag = FeatureFlag.create(payload.key)
    flag.enabled = payload.enabled

    try:
        created_flag = repository.add(flag)
        repository.session.commit()
    except IntegrityError as exc:
        repository.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feature flag key already exists.",
        ) from exc

    return created_flag


@router.get("", response_model=List[FeatureFlagResponse])
def list_feature_flags(
    repository: FeatureFlagRepository = Depends(get_repository),
) -> List[FeatureFlag]:
    return repository.list()


@router.post("/by-key", response_model=FeatureFlagResponse)
def get_feature_flag_by_key(
    payload: FeatureFlagByKeyRequest,
    repository: FeatureFlagRepository = Depends(get_repository),
) -> FeatureFlag:
    flag = repository.get_by_key(payload.key)
    if flag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found.",
        )
    return flag


@router.put("/{flag_id}", response_model=FeatureFlagResponse)
def update_feature_flag(
    flag_id: uuid.UUID,
    payload: FeatureFlagUpdate,
    repository: FeatureFlagRepository = Depends(get_repository),
) -> FeatureFlag:
    existing_flag = repository.get(flag_id)

    if existing_flag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found.",
        )

    existing_flag.key = payload.key
    existing_flag.enabled = payload.enabled

    try:
        updated_flag = repository.save(existing_flag)
        repository.session.commit()
    except IntegrityError as exc:
        repository.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feature flag key already exists.",
        ) from exc

    return updated_flag


@router.delete("/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature_flag(
    flag_id: uuid.UUID,
    repository: FeatureFlagRepository = Depends(get_repository),
) -> Response:
    existing_flag = repository.get(flag_id)

    if existing_flag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found.",
        )

    repository.delete(flag_id)
    repository.session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
