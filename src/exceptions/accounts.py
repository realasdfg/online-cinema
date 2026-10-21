from exceptions.base import AppError


class UserAlreadyExistsError(AppError):
    status_code = 409
    detail = "User with this email already exists."


class DefaultGroupNotFoundError(AppError):
    status_code = 500
    detail = "Internal server error."


class InvalidOrExpiredTokenError(AppError):
    status_code = 400
    detail = "Invalid or expired token."


class UserAlreadyActivatedError(AppError):
    status_code = 400
    detail = "User account is already active."
