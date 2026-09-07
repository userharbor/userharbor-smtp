from __future__ import annotations

import ssl
from email.message import EmailMessage

import pytest

from userharbor_smtp import SMTPEmailSender


class FakeSMTP:
    instances: list["FakeSMTP"] = []

    def __init__(self, host: str, port: int, *, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.starttls_context: ssl.SSLContext | None = None
        self.sent_messages: list[EmailMessage] = []
        FakeSMTP.instances.append(self)

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def starttls(self, *, context: ssl.SSLContext | None = None) -> None:
        self.started_tls = True
        self.starttls_context = context

    def send_message(self, message: EmailMessage) -> None:
        self.sent_messages.append(message)


class FakeSMTPSSL(FakeSMTP):
    instances: list["FakeSMTPSSL"] = []

    def __init__(
        self,
        host: str,
        port: int,
        *,
        timeout: float,
        context: ssl.SSLContext | None = None,
    ) -> None:
        super().__init__(host, port, timeout=timeout)
        self.ssl_context = context
        FakeSMTPSSL.instances.append(self)


def test_send_starts_tls_for_plain_smtp(monkeypatch) -> None:
    FakeSMTP.instances = []
    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)

    sender = SMTPEmailSender(
        host="smtp.example.com",
        port=2525,
        from_email="noreply@example.com",
        use_starttls=True,
        timeout=3,
    )

    sender.send_email_verified("alice", "alice@example.com")

    smtp = FakeSMTP.instances[0]
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 2525
    assert smtp.timeout == 3
    assert smtp.started_tls is True
    assert smtp.starttls_context is not None
    assert smtp.starttls_context.verify_mode == ssl.CERT_REQUIRED
    assert smtp.starttls_context.check_hostname is True
    assert smtp.sent_messages[0]["To"] == "alice@example.com"


def test_send_uses_smtp_ssl_without_starttls(monkeypatch) -> None:
    FakeSMTPSSL.instances = []
    monkeypatch.setattr("smtplib.SMTP_SSL", FakeSMTPSSL)

    sender = SMTPEmailSender(
        host="smtp.example.com",
        port=465,
        from_email="noreply@example.com",
        use_ssl=True,
        timeout=7,
    )

    sender.send_password_changed("alice", "alice@example.com")

    smtp = FakeSMTPSSL.instances[0]
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 465
    assert smtp.timeout == 7
    assert smtp.started_tls is False
    assert smtp.ssl_context is not None
    assert smtp.ssl_context.verify_mode == ssl.CERT_REQUIRED
    assert smtp.ssl_context.check_hostname is True
    assert smtp.sent_messages[0]["Subject"] == "Password changed"


def test_send_uses_custom_ssl_context_for_starttls(monkeypatch) -> None:
    FakeSMTP.instances = []
    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    sender = SMTPEmailSender(
        host="smtp.example.com",
        from_email="noreply@example.com",
        ssl_context=context,
    )

    sender.send_email_verified("alice", "alice@example.com")

    assert FakeSMTP.instances[0].starttls_context is context


def test_insecure_transport_is_rejected() -> None:
    with pytest.raises(ValueError, match="TLS"):
        SMTPEmailSender(
            host="smtp.example.com",
            from_email="noreply@example.com",
            use_starttls=False,
            use_ssl=False,
        )
