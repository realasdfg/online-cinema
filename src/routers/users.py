from fastapi import APIRouter

from dependencies.auth import AdminDep
from dependencies.services import UserServiceDep
from schemas.users import (
    UserActivationUpdateRequestSchema,
    UserGroupUpdateRequestSchema,
    UserResponseSchema,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}/group")
async def change_user_group(
    user_id: int,
    group_data: UserGroupUpdateRequestSchema,
    admin: AdminDep,
    service: UserServiceDep,
) -> UserResponseSchema:
    user = await service.change_group(admin, user_id, group_data.group)
    return UserResponseSchema.model_validate(user)


@router.patch("/{user_id}/activation")
async def set_user_activation(
    user_id: int,
    activation_data: UserActivationUpdateRequestSchema,
    admin: AdminDep,
    service: UserServiceDep,
) -> UserResponseSchema:
    user = await service.set_active(admin, user_id, activation_data.is_active)
    return UserResponseSchema.model_validate(user)
