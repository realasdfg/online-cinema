from urllib.parse import urlencode

from config import Settings


def build_activation_link(settings: Settings, token: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/activate?{urlencode({'token': token})}"


def build_login_link(settings: Settings) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/accounts/login"


def build_password_reset_link(settings: Settings, token: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/reset-password?{urlencode({'token': token})}"
