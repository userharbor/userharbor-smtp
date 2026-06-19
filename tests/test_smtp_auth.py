import pytest

from smtplib import SMTPAuthenticationError

from userharbor_smtp import SMTPEmailSender


def test_send_raises_when_smtp_authentication_fails(smtp_server) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        username="smtp-user",
        password="wrong-password",
        from_email="noreply@example.com",
        use_starttls=False,
    )

    with pytest.raises(SMTPAuthenticationError):
        sender.send_verification("alice", "alice@example.com", "verification-token")

    assert smtp_server.auth_attempts[0].username == "smtp-user"
    assert smtp_server.auth_attempts[0].password == "wrong-password"
    assert smtp_server.messages == []
