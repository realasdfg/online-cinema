from fastapi import FastAPI

from routers.accounts import router as account_router

app = FastAPI(
    title="Online Cinema API",
    description="Online Cinema API",
    version="1.0",
    root_path="/api/v1",
)

app.include_router(account_router, prefix="/accounts", tags=["accounts"])
