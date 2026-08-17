from sqlalchemy import Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.models.enums import UserGroupEnum
from database.session import Base


class UserGroup(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[UserGroupEnum] = mapped_column(
        Enum(UserGroupEnum), nullable=False, unique=True
    )

    def __repr__(self):
        return f"<UserGroup(id={self.id}, name={self.name})>"
