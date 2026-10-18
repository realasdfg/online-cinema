import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import ClassVar

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from exceptions.email import BaseEmailError
from notifications.interfaces import EmailSenderInterface

logger = logging.getLogger(__name__)


class EmailSender(EmailSenderInterface):
    _TEMPLATES: ClassVar[dict[str, str]] = {
        "activation": "activation_email.html",
        "activation_complete": "activation_complete_email.html",
    }

    def __init__(
        self,
        hostname: str,
        port: int,
        email: str,
        password: str,
        use_tls: bool,
        template_dir: str,
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._email = email
        self._password = password
        self._use_tls = use_tls

        self._env = Environment(loader=FileSystemLoader(template_dir))

    async def _send_email(
        self, recipient: str, subject: str, html_content: str
    ) -> None:
        """
        Asynchronously send an email with the given subject and HTML content.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            html_content (str): The HTML content of the email.

        Raises:
            BaseEmailError: If sending the email fails.
        """
        message = MIMEMultipart()
        message["From"] = self._email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            smtp = aiosmtplib.SMTP(
                hostname=self._hostname, port=self._port, start_tls=self._use_tls
            )
            await smtp.connect()
            if self._use_tls:
                await smtp.starttls()
            await smtp.login(self._email, self._password)
            await smtp.sendmail(self._email, [recipient], message.as_string())
            await smtp.quit()
        except aiosmtplib.SMTPException as error:
            logger.error(f"Failed to send email to {recipient}: {error}")
            raise BaseEmailError(f"Failed to send email to {recipient}: {error}")

    async def _send_templated(
        self, recipient: str, subject: str, template_key: str, **context
    ) -> None:
        """
        Send templated email asynchronously.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            template_key (str): The template key from _TEMPLATES.
            context: The context to be used in the template.
        """
        html = self._env.get_template(self._TEMPLATES[template_key]).render(
            email=recipient, **context
        )
        await self._send_email(recipient, subject, html)

    async def send_activation_email(self, email, activation_link):
        """
        Send an account activation email asynchronously.

        Args:
            email (str): The recipient's email address.
            activation_link (str): The activation link to be included in the email.
        """
        await self._send_templated(
            email, "Account Activation", "activation", activation_link=activation_link
        )

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Send an account activation completion email asynchronously.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to be included in the email.
        """
        await self._send_templated(
            email,
            "Account Activated Successfully",
            "activation_complete",
            login_link=login_link,
        )
