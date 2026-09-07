from userharbor_smtp import SMTPEmailSender


def test_send_verification_logs_in_and_sends_rendered_html(smtp_server) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        username="smtp-user",
        password="smtp-password",
        from_email="noreply@example.com",
        from_name="UserHarbor",
        use_starttls=False,
        allow_insecure=True,
    )

    sender.send_verification("alice", "alice@example.com", "verification-token")

    assert len(smtp_server.auth_attempts) == 1
    assert smtp_server.auth_attempts[0].username == "smtp-user"
    assert smtp_server.auth_attempts[0].password == "smtp-password"

    envelope = smtp_server.messages[0]
    message = envelope.message
    html = message.get_body(preferencelist=("html",)).get_content()

    assert message["From"] == "UserHarbor <noreply@example.com>"
    assert message["To"] == "alice@example.com"
    assert message["Subject"] == "Verify your email"
    assert envelope.rcpt_tos == ["<alice@example.com>"]
    assert "Hello alice" in html
    assert "verification-token" in html


def test_send_verification_can_use_custom_subject(smtp_server) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        from_email="noreply@example.com",
        verification_subject="Confirm account",
        use_starttls=False,
        allow_insecure=True,
    )

    sender.send_verification("alice", "alice@example.com", "verification-token")

    assert smtp_server.messages[0].message["Subject"] == "Confirm account"
