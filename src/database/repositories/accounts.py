from database.models.accounts import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserGroup,
    UserProfile,
)
from database.repositories.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User


class UserGroupRepository(SQLAlchemyRepository[UserGroup]):
    model = UserGroup


class UserProfileRepository(SQLAlchemyRepository[UserProfile]):
    model = UserProfile


class ActivationTokenRepository(SQLAlchemyRepository[ActivationToken]):
    model = ActivationToken


class PasswordResetTokenRepository(SQLAlchemyRepository[PasswordResetToken]):
    model = PasswordResetToken


class RefreshTokenRepository(SQLAlchemyRepository[RefreshToken]):
    model = RefreshToken
