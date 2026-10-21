from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

from config import Settings, get_settings
from dependencies import get_account_service, get_email_sender
from notifications.interfaces import EmailSenderInterface
from notifications.links import build_activation_link
from schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)
from services.accounts import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    service: AccountService = Depends(get_account_service),
    email_sender: EmailSenderInterface = Depends(get_email_sender),
    settings: Settings = Depends(get_settings),
) -> UserRegistrationResponseSchema:
    user, raw_token = await service.register(user_data.email, user_data.password)
    background_tasks.add_task(
        email_sender.send_activation_email,
        user.email,
        build_activation_link(settings, raw_token),
    )
    return UserRegistrationResponseSchema.model_validate(user)


@router.get("/activate/{token}", name="activate_account")
async def activate_account(token: str):
    pass
