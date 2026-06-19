from userharbor_smtp import SMTPEmailSender


def test_send_password_reset_sends_rendered_html(smtp_server) -> None:
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        username="smtp-user",
        password="smtp-password",
        from_email="noreply@example.com",
        use_starttls=False,
    )

    sender.send_password_reset("alice", "alice@example.com", "reset-token")

    envelope = smtp_server.messages[0]
    message = envelope.message
    html = message.get_body(preferencelist=("html",)).get_content()

    assert message["From"] == "noreply@example.com"
    assert message["To"] == "alice@example.com"
    assert message["Subject"] == "Reset your password"
    assert envelope.rcpt_tos == ["<alice@example.com>"]
    assert "Hello alice" in html
    assert "reset-token" in html
