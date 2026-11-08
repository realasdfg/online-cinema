from fastapi import APIRouter, BackgroundTasks, status

from dependencies.auth import AuthServiceDep
from dependencies.common import SettingsDep
from dependencies.notifications import EmailSenderDep
from dependencies.services import AccountServiceDep
from notifications.links import (
    build_activation_link,
    build_login_link,
    build_password_reset_link,
)
from schemas.accounts import (
    MessageResponseSchema,
    PasswordChangeRequestSchema,
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    ResendActivationRequestSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    UserActivationRequestSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    service: AccountServiceDep,
    email_sender: EmailSenderDep,
    settings: SettingsDep,
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
    service: AccountServiceDep,
    email_sender: EmailSenderDep,
    settings: SettingsDep,
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
    service: AccountServiceDep,
    email_sender: EmailSenderDep,
    settings: SettingsDep,
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


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    payload: PasswordResetRequestSchema,
    background_tasks: BackgroundTasks,
    service: AccountServiceDep,
    email_sender: EmailSenderDep,
    settings: SettingsDep,
) -> MessageResponseSchema:
    raw_token = await service.request_password_reset(payload.email)
    if raw_token is not None:
        background_tasks.add_task(
            email_sender.send_password_reset_email,
            payload.email,
            build_password_reset_link(settings, raw_token),
        )
    return MessageResponseSchema(
        message="If you are registered, you will receive an email with instructions."
    )


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    payload: PasswordResetConfirmSchema,
    background_tasks: BackgroundTasks,
    service: AccountServiceDep,
    email_sender: EmailSenderDep,
    settings: SettingsDep,
) -> MessageResponseSchema:
    user = await service.confirm_password_reset(payload.token, payload.new_password)
    background_tasks.add_task(
        email_sender.send_password_reset_complete_email,
        user.email,
        build_login_link(settings),
    )
    return MessageResponseSchema(message="Password has been successfully changed.")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    login_data: UserLoginRequestSchema, service: AuthServiceDep
) -> UserLoginResponseSchema:
    access_token, refresh_token = await service.login(
        login_data.email, login_data.password
    )
    return UserLoginResponseSchema(
        access_token=access_token, refresh_token=refresh_token
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    token_data: TokenRefreshRequestSchema, service: AuthServiceDep
) -> TokenRefreshResponseSchema:
    access_token = await service.refresh(token_data.refresh_token)
    return TokenRefreshResponseSchema(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    token_data: TokenRefreshRequestSchema, service: AuthServiceDep
) -> MessageResponseSchema:
    await service.logout(token_data.refresh_token)
    return MessageResponseSchema(message="Logged out successfully.")
