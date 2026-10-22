from exceptions.base import AppError


class AuthError(AppError):
    status_code = 401


class TokenExpiredError(AuthError):
    detail = "Token has expired."


class InvalidJWTError(AuthError):
    detail = "Invalid token."
