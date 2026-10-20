from fastapi import FastAPI

from config import Settings


def build_activation_link(app: FastAPI, settings: Settings, token: str) -> str:
    path = app.url_path_for("activate_account", token=token)
    return f"{settings.BASE_URL.rstrip('/')}{path}"
