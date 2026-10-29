import pytest
from userharbor_smtp import SMTPEmailSender


@pytest.mark.parametrize(
    ("method", "template_name", "token"),
    [
        ("send_verification", "verification.html", "verification-token"),
        ("send_password_reset", "password_reset.html", "reset-token"),
        ("send_email_verified", "email_verified.html", None),
        ("send_password_changed", "password_changed.html", None),
        ("send_account_deleted", "account_deleted.html", None),
    ],
)
def test_template_context_preserves_builtin_variables(
    smtp_server, tmp_path, method, template_name, token
) -> None:
    (tmp_path / template_name).write_text(
        '<a href="{{ app_url }}/verify?token={{ token | urlencode }}">'
        "{{ username }} at {{ email }}</a>",
        encoding="utf-8",
    )
    sender = SMTPEmailSender(
        host=smtp_server.host,
        port=smtp_server.port,
        from_email="noreply@example.com",
        template_dir=tmp_path,
        template_context={
            "app_url": "https://example.com",
            "username": "overridden-user",
            "email": "overridden@example.com",
            "token": "overridden-token",
        },
        use_starttls=False,
        allow_insecure=True,
    )
    args = ("<alice>", "alice@example.com")
    if token is not None:
        args += (token,)
    getattr(sender, method)(*args)

    html = (
        smtp_server.messages[0].message.get_body(preferencelist=("html",)).get_content()
    )
    assert "https://example.com/verify?token=" in html
    assert "&lt;alice&gt; at alice@example.com" in html
    assert "overridden" not in html
    if token is not None:
        assert token in html
