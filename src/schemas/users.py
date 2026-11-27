from datetime import datetime

from pydantic import BaseModel, EmailStr

from database.models.enums import UserGroupEnum


class UserGroupUpdateRequestSchema(BaseModel):
    group: UserGroupEnum


class UserGroupResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: UserGroupEnum


class UserResponseSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: EmailStr
    is_active: bool
    group: UserGroupResponseSchema
    created_at: datetime
    updated_at: datetime


class UserActivationUpdateRequestSchema(BaseModel):
    is_active: bool
