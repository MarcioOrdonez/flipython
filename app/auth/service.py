import hashlib
import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.api_key import ApiKey
from app.db.session import get_session


async def authenticate(
    authorization: Optional[str] = Header(default=None),
    session: Session = Depends(get_session),
):
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    try:
        scheme, token = authorization.split()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth scheme",
        )

    token_hash = "v1:" + hashlib.sha256(token.encode("utf-8")).hexdigest()
    statement = select(ApiKey).where(ApiKey.enabled.is_(True))
    api_keys = session.scalars(statement).all()

    if not any(secrets.compare_digest(token_hash, key.key_hash) for key in api_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return {
        "token_hash": token_hash,
    }
