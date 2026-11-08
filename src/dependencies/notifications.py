from typing import Annotated

from fastapi import Depends

from dependencies.common import SettingsDep
from notifications.emails import EmailSender
from notifications.interfaces import EmailSenderInterface


def get_email_sender(settings: SettingsDep) -> EmailSenderInterface:
    return EmailSender(
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        email=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        template_dir=settings.PATH_TO_EMAIL_TEMPLATES_DIR,
    )


EmailSenderDep = Annotated[EmailSenderInterface, Depends(get_email_sender)]
