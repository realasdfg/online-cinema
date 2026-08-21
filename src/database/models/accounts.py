from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.enums import GenderEnum, UserGroupEnum
from database.session import Base


class UserGroup(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[UserGroupEnum] = mapped_column(
        Enum(UserGroupEnum, name="user_group_enum"), nullable=False, unique=True
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="group")

    def __repr__(self):
        return f"<UserGroup(id={self.id}, name={self.name})>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("user_groups.id", ondelete="RESTRICT"), nullable=False
    )

    group: Mapped["UserGroup"] = relationship("UserGroup", back_populates="users")

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan"
    )

    activation_token: Mapped[Optional["ActivationToken"]] = relationship(
        "ActivationToken", back_populates="user", cascade="all, delete-orphan"
    )

    password_reset_token: Mapped[Optional["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    info: Mapped[str | None] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, first_name={self.first_name}, last_name={self.last_name})>"


class BaseToken(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )


class ActivationToken(BaseToken):
    __tablename__ = "activation_tokens"

    user: Mapped["User"] = relationship("User", back_populates="activation_token")

    def __repr__(self):
        return f"<ActivationToken(id={self.id}, token={self.token}, expires_at={self.expires_at})>"


class PasswordResetToken(BaseToken):
    __tablename__ = "password_reset_tokens"

    user: Mapped["User"] = relationship("User", back_populates="password_reset_token")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, token={self.token}, expires_at={self.expires_at})>"


class RefreshToken(BaseToken):
    __tablename__ = "refresh_tokens"

    user: Mapped["User"] = relationship("User", back_populates="refresh_token")

    @classmethod
    def create(
        cls, user_id: int | Mapped[int], days_valid: int, token: str
    ) -> "RefreshToken":
        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
        return cls(user_id=user_id, expires_at=expires_at, token=token)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, token={self.token}, expires_at={self.expires_at})>"
