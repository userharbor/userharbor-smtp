from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from importlib import resources
from os import PathLike
from pathlib import Path

from jinja2 import Environment, FunctionLoader, StrictUndefined, select_autoescape

TemplateName = str


class SMTPEmailSender:
    def __init__(
        self,
        *,
        host: str,
        from_email: str,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        from_name: str | None = None,
        template_dir: str | PathLike[str] | None = None,
        verification_subject: str = "Verify your email",
        password_reset_subject: str = "Reset your password",
        email_verified_subject: str = "Email verified",
        password_changed_subject: str = "Password changed",
        account_deleted_subject: str = "Account deleted",
        use_starttls: bool = True,
        use_ssl: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        allow_insecure: bool = False,
        timeout: float = 10,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._from_name = from_name
        self._template_dir = Path(template_dir) if template_dir is not None else None
        self._verification_subject = verification_subject
        self._password_reset_subject = password_reset_subject
        self._email_verified_subject = email_verified_subject
        self._password_changed_subject = password_changed_subject
        self._account_deleted_subject = account_deleted_subject
        self._use_starttls = use_starttls
        self._use_ssl = use_ssl
        if not use_starttls and not use_ssl and not allow_insecure:
            raise ValueError("SMTP transport must use TLS")
        self._ssl_context = ssl_context or ssl.create_default_context()
        self._timeout = timeout
        self._environment = Environment(
            loader=FunctionLoader(self._load_template),
            autoescape=select_autoescape(["html"]),
            undefined=StrictUndefined,
        )

    def send_verification(
        self, username: str, email: str, verification_token: str
    ) -> None:
        self._send(
            to_email=email,
            subject=self._verification_subject,
            template_name="verification.html",
            username=username,
            token=verification_token,
        )

    def send_password_reset(self, username: str, email: str, reset_token: str) -> None:
        self._send(
            to_email=email,
            subject=self._password_reset_subject,
            template_name="password_reset.html",
            username=username,
            token=reset_token,
        )

    def send_email_verified(self, username: str, email: str) -> None:
        self._send(
            to_email=email,
            subject=self._email_verified_subject,
            template_name="email_verified.html",
            username=username,
        )

    def send_password_changed(self, username: str, email: str) -> None:
        self._send(
            to_email=email,
            subject=self._password_changed_subject,
            template_name="password_changed.html",
            username=username,
        )

    def send_account_deleted(self, username: str, email: str) -> None:
        self._send(
            to_email=email,
            subject=self._account_deleted_subject,
            template_name="account_deleted.html",
            username=username,
        )

    def _send(
        self,
        *,
        to_email: str,
        subject: str,
        template_name: TemplateName,
        username: str,
        token: str | None = None,
    ) -> None:
        html = self._environment.get_template(template_name).render(
            username=username,
            email=to_email,
            token=token,
        )
        message = EmailMessage()
        message["From"] = self._format_from()
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content("This email requires an HTML-capable email client.")
        message.add_alternative(html, subtype="html")

        if self._use_ssl:
            smtp = smtplib.SMTP_SSL(
                self._host,
                self._port,
                timeout=self._timeout,
                context=self._ssl_context,
            )
        else:
            smtp = smtplib.SMTP(self._host, self._port, timeout=self._timeout)

        with smtp:
            if self._use_starttls and not self._use_ssl:
                smtp.starttls(context=self._ssl_context)
            if self._username is not None and self._password is not None:
                smtp.login(self._username, self._password)
            smtp.send_message(message)

    def _format_from(self) -> str:
        if self._from_name is None:
            return self._from_email
        return formataddr((self._from_name, self._from_email))

    def _load_template(self, template_name: TemplateName) -> str:
        if self._template_dir is not None:
            return (self._template_dir / template_name).read_text(encoding="utf-8")

        return (
            resources.files("userharbor_smtp.templates")
            .joinpath(template_name)
            .read_text(encoding="utf-8")
        )
