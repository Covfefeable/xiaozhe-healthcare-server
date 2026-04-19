from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return payload


def get_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None

    token = authorization.removeprefix(prefix).strip()
    return token or None

