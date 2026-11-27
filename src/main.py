from fastapi import FastAPI

from config import get_settings
from exceptions.handlers import register_exception_handlers
from routers.accounts import router as account_router
from routers.users import router as users_router

settings = get_settings()

app = FastAPI(
    title="Online Cinema API",
    description="Online Cinema API",
    version="1.0",
)

register_exception_handlers(app)

app.include_router(account_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
