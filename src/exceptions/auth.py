from typing import ClassVar

from exceptions.base import AppError


class AuthError(AppError):
    status_code = 401
    headers: ClassVar[dict[str, str] | None] = {"WWW-Authenticate": "Bearer"}


class TokenExpiredError(AuthError):
    detail = "Token has expired."


class InvalidJWTError(AuthError):
    detail = "Invalid token."


class InvalidEmailOrPasswordError(AuthError):
    detail = "Invalid email or password."
