import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from celery_app import celery_app
from config import get_settings
from database.models.accounts import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
)

TOKEN_MODELS = (ActivationToken, PasswordResetToken, RefreshToken)


async def _cleanup_expired_tokens() -> dict[str, int]:
    engine = create_async_engine(get_settings().DB_URI, poolclass=NullPool)
    deleted: dict[str, int] = {}
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            now = datetime.now(timezone.utc)
            for model in TOKEN_MODELS:
                result = await session.execute(
                    delete(model).where(model.expires_at < now)
                )
                deleted[model.__tablename__] = result.rowcount
            await session.commit()
    finally:
        await engine.dispose()
    return deleted


@celery_app.task(name="tokens.cleanup_expired")
def cleanup_expired_tokens() -> dict[str, int]:
    return asyncio.run(_cleanup_expired_tokens())
