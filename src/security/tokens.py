from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from config import Settings
from exceptions.auth import InvalidJWTError, TokenExpiredError


class JWTAuthManager:
    def __init__(self, settings: Settings) -> None:
        self._secret_key = settings.SECRET_KEY
        self._algorithm = settings.JWT_ALGORITHM
        self._access_ttl = timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)
        self._refresh_ttl = timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)

    def _create_token(self, payload: dict, expires_delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        payload = {**payload, "iat": now, "exp": now + expires_delta}
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_access_token(
        self, user_id: int, expires_delta: timedelta | None = None
    ) -> str:
        return self._create_token(
            {"sub": str(user_id), "type": "access"},
            expires_delta or self._access_ttl,
        )

    def create_refresh_token(
        self, user_id: int, expires_delta: timedelta | None = None
    ) -> str:
        return self._create_token(
            {"sub": str(user_id), "type": "refresh"},
            expires_delta or self._refresh_ttl,
        )

    def _decode(self, token: str, expected_type: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub", "type"]},
            )
        except ExpiredSignatureError as e:
            raise TokenExpiredError() from e
        except InvalidTokenError as e:
            raise InvalidJWTError() from e

        if payload.get("type") != expected_type:
            raise InvalidJWTError()
        return payload

    def decode_access_token(self, token: str) -> dict:
        return self._decode(token, "access")

    def decode_refresh_token(self, token: str) -> dict:
        return self._decode(token, "refresh")
