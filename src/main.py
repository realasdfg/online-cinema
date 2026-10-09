from fastapi import FastAPI

from routers.accounts import router as account_router

app = FastAPI()

app.include_router(account_router, prefix="/accounts", tags=["accounts"])
