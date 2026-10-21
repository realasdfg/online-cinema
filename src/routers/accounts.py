from fastapi import APIRouter, BackgroundTasks, Depends, status

from config import Settings, get_settings
from dependencies import get_account_service, get_email_sender
from notifications.interfaces import EmailSenderInterface
from notifications.links import build_activation_link, build_login_link
from schemas.accounts import (
    MessageResponseSchema,
    ResendActivationRequestSchema,
    UserActivationRequestSchema,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)
from services.accounts import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
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


@router.post("/activate", status_code=status.HTTP_200_OK)
async def activate_account(
    activation_data: UserActivationRequestSchema,
    background_tasks: BackgroundTasks,
    service: AccountService = Depends(get_account_service),
    email_sender: EmailSenderInterface = Depends(get_email_sender),
    settings: Settings = Depends(get_settings),
) -> MessageResponseSchema:
    user = await service.activate_account(activation_data.token)
    background_tasks.add_task(
        email_sender.send_activation_complete_email,
        user.email,
        build_login_link(settings),
    )
    return MessageResponseSchema(message="User account activated successfully.")


@router.post("/resend-activation", status_code=status.HTTP_200_OK)
async def resend_activation(
    payload: ResendActivationRequestSchema,
    background_tasks: BackgroundTasks,
    service: AccountService = Depends(get_account_service),
    email_sender: EmailSenderInterface = Depends(get_email_sender),
    settings: Settings = Depends(get_settings),
) -> MessageResponseSchema:
    raw_token = await service.refresh_activation_token(payload.email)
    if raw_token is not None:
        background_tasks.add_task(
            email_sender.send_activation_email,
            payload.email,
            build_activation_link(settings, raw_token),
        )
    return MessageResponseSchema(
        message="If the account exists, a new activation link has been sent."
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login():
    pass
