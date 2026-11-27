from fastapi import APIRouter

from dependencies.auth import AdminDep
from dependencies.services import UserServiceDep
from schemas.users import UserGroupUpdateRequestSchema, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}/group")
async def change_user_group(
    user_id: int,
    group_data: UserGroupUpdateRequestSchema,
    admin: AdminDep,
    service: UserServiceDep,
):
    user = await service.change_group(admin, user_id, group_data.group)
    return UserResponseSchema.model_validate(user)
