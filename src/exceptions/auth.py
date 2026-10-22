from exceptions.base import AppError


class AuthError(AppError):
    status_code = 401


class TokenExpiredError(AuthError):
    detail = "Token has expired."


class InvalidJWTError(AuthError):
    detail = "Invalid token."


class InvalidEmailOrPasswordError(AuthError):
    detail = "Invalid email or password."


class UserNotActivatedError(AuthError):
    status_code = 403
    detail = "User account is not activated."
