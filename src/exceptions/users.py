from exceptions.base import AppError


class CannotChangeOwnGroupError(AppError):
    status_code = 400
    detail = "Administrators cannot change their own group."


class CannotDeactivateSelfError(AppError):
    status_code = 400
    detail = "Administrators cannot deactivate their own account."
