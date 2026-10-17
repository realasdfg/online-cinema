from fastapi import FastAPI

from exceptions.handlers import register_exception_handlers
from routers.accounts import router as account_router

app = FastAPI(
    title="Online Cinema API",
    description="Online Cinema API",
    version="1.0",
    root_path="/api/v1",
)

register_exception_handlers(app)

app.include_router(account_router, prefix="/accounts", tags=["accounts"])
