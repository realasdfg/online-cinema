from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from dependencies import get_account_service
from exceptions.accounts import DefaultGroupNotFoundError, UserAlreadyExistsError
from schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)
from services.accounts import AccountService

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistrationRequestSchema,
    service: AccountService = Depends(get_account_service),
) -> UserRegistrationResponseSchema:
    user = await service.register(user_data.email, user_data.password)
    return UserRegistrationResponseSchema.model_validate(user)
