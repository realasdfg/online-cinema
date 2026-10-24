from fastapi import APIRouter, BackgroundTasks, Depends, status

from config import Settings, get_settings
from dependencies import get_account_service, get_auth_service, get_email_sender
from notifications.interfaces import EmailSenderInterface
from notifications.links import build_activation_link, build_login_link
from schemas.accounts import (
    MessageResponseSchema,
    ResendActivationRequestSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    UserActivationRequestSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)
from services.accounts import AccountService
from services.auth import AuthService

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
async def login_user(
    login_data: UserLoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
) -> UserLoginResponseSchema:
    access_token, refresh_token = await service.login(
        login_data.email, login_data.password
    )
    return UserLoginResponseSchema(
        access_token=access_token, refresh_token=refresh_token
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    token_data: TokenRefreshRequestSchema,
    service: AuthService = Depends(get_auth_service),
) -> TokenRefreshResponseSchema:
    access_token = await service.refresh(token_data.refresh_token)
    return TokenRefreshResponseSchema(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    token_data: TokenRefreshRequestSchema,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponseSchema:
    await service.logout(token_data.refresh_token)
    return MessageResponseSchema(message="Logged out successfully.")
