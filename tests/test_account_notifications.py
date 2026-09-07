import pytest

from userharbor_smtp import SMTPEmailSender


@pytest.mark.parametrize(
    ("method_name", "expected_subject", "expected_text"),
    [
        ("send_email_verified", "Email verified", "email address alice@example.com"),
        ("send_password_changed", "Password changed", "password has been changed"),
        ("send_account_deleted", "Account deleted", "account has been deleted"),
    ],
)
def test_account_notification_sends_rendered_html(
    smtp_server,
    method_name: str,
    expected_subject: str,
    expected_text: str,
) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        username="smtp-user",
        password="smtp-password",
        from_email="noreply@example.com",
        use_starttls=False,
        allow_insecure=True,
    )

    getattr(sender, method_name)("alice", "alice@example.com")

    envelope = smtp_server.messages[0]
    message = envelope.message
    html = message.get_body(preferencelist=("html",)).get_content()

    assert message["From"] == "noreply@example.com"
    assert message["To"] == "alice@example.com"
    assert message["Subject"] == expected_subject
    assert envelope.rcpt_tos == ["<alice@example.com>"]
    assert "Hello alice" in html
    assert expected_text in html


def test_account_notifications_can_use_custom_subjects(smtp_server) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        from_email="noreply@example.com",
        email_verified_subject="Address confirmed",
        password_changed_subject="Credentials updated",
        account_deleted_subject="Account removed",
        use_starttls=False,
        allow_insecure=True,
    )

    sender.send_email_verified("alice", "alice@example.com")
    sender.send_password_changed("alice", "alice@example.com")
    sender.send_account_deleted("alice", "alice@example.com")

    assert smtp_server.messages[0].message["Subject"] == "Address confirmed"
    assert smtp_server.messages[1].message["Subject"] == "Credentials updated"
    assert smtp_server.messages[2].message["Subject"] == "Account removed"
