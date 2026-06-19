from userharbor_smtp import SMTPEmailSender


def test_send_verification_uses_custom_template_directory(
    smtp_server,
    tmp_path,
) -> None:
    (tmp_path / "verification.html").write_text(
        "<html><body>Custom verification for {{ username }} at {{ email }}: "
        "{{ token }}</body></html>",
        encoding="utf-8",
    )

    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        from_email="noreply@example.com",
        template_dir=tmp_path,
        use_starttls=False,
    )

    sender.send_verification("alice", "alice@example.com", "verification-token")

    html = smtp_server.messages[0].message.get_body(
        preferencelist=("html",)
    ).get_content()
    assert "Custom verification for alice at alice@example.com" in html
    assert "verification-token" in html


def test_send_password_reset_uses_custom_template_directory(
    smtp_server,
    tmp_path,
) -> None:
    (tmp_path / "password_reset.html").write_text(
        "<html><body>Custom reset for {{ username }}: {{ token }}</body></html>",
        encoding="utf-8",
    )

    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        from_email="noreply@example.com",
        template_dir=tmp_path,
        use_starttls=False,
    )

    sender.send_password_reset("alice", "alice@example.com", "reset-token")

    html = smtp_server.messages[0].message.get_body(
        preferencelist=("html",)
    ).get_content()
    assert "Custom reset for alice" in html
    assert "reset-token" in html
