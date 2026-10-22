from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import User
from database.repositories.accounts import RefreshTokenRepository, UserRepository
from exceptions.accounts import UserNotActivatedError
from exceptions.auth import InvalidEmailOrPasswordError
from security.tokens import JWTAuthManager
from security.utils import hash_token
from services.base import BaseService


class AuthService(BaseService[User]):
    def __init__(self, session: AsyncSession, jwt_manager: JWTAuthManager) -> None:
        super().__init__(session, UserRepository)
        self._jwt = jwt_manager
        self._refresh_token_repo = RefreshTokenRepository(session)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self._repo.get(User.email == email)
        if user is None or not user.verify_password(password):
            raise InvalidEmailOrPasswordError()
        if not user.is_active:
            raise UserNotActivatedError()

        access_token = self._jwt.create_access_token(user.id)

        refresh_token = self._jwt.create_refresh_token(user.id)
        refresh_payload = self._jwt.decode_refresh_token(refresh_token)
        refresh_expires_at = datetime.fromtimestamp(
            refresh_payload["exp"], tz=timezone.utc
        )
        await self._refresh_token_repo.create(
            {
                "user_id": user.id,
                "expires_at": refresh_expires_at,
                "token_hash": hash_token(refresh_token),
            }
        )
        await self._session.commit()
        return access_token, refresh_token
