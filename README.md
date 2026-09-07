<picture>
  <img src="https://github.com/userharbor/userharbor/raw/master/docs/assets/logo-full.png" alt="userharbor">
</picture>

[![GitHub License](https://img.shields.io/github/license/userharbor/userharbor-smtp)](https://github.com/userharbor/userharbor-smtp?tab=MIT-1-ov-file)
[![Tests](https://img.shields.io/github/actions/workflow/status/userharbor/userharbor-smtp/publish.yml?label=tests)](https://github.com/userharbor/userharbor-smtp/blob/master/.github/workflows/tests.yml)
[![Codecov](https://img.shields.io/codecov/c/github/userharbor/userharbor-smtp)](https://codecov.io/gh/userharbor/userharbor-smtp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/userharbor-smtp)](https://pypi.org/project/userharbor-smtp)
[![PyPI - Version](https://img.shields.io/pypi/v/userharbor-smtp)](https://pypi.org/project/userharbor-smtp)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-Ruff-black?logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pytest](https://img.shields.io/badge/testing-Pytest-red?logo=pytest&logoColor=red)](https://docs.pytest.org/)
[![Zensical](https://img.shields.io/badge/docs-Zensical-yellow?logo=MaterialForMkDocs&logoColor=yellow)](https://userharborpaceshaman.github.io/userharbor/)

SMTP email sender integration for
[`userharbor`](https://github.com/userharbor/userharbor).

The package provides `SMTPEmailSender`, an implementation of UserHarbor's
`EmailSender` protocol. It sends verification, password reset, and account
security notification messages with Python's standard `smtplib` and renders
HTML email templates with Jinja.

## Installation

```bash
pip install userharbor-smtp
```

## Usage

```python
from userharbor_smtp import SMTPEmailSender

email_sender = SMTPEmailSender(
    host="smtp.example.com",
    port=587,
    username="smtp-user",
    password="smtp-password",
    from_email="noreply@example.com",
    from_name="UserHarbor",
)
```

By default, the sender uses HTML templates bundled with the package:

* `verification.html`
* `password_reset.html`
* `email_verified.html`
* `password_changed.html`
* `account_deleted.html`

To use custom templates, pass a directory containing files with the same names:

```python
email_sender = SMTPEmailSender(
    host="smtp.example.com",
    port=587,
    username="smtp-user",
    password="smtp-password",
    from_email="noreply@example.com",
    template_dir="templates/emails",
)
```

Each template receives:

* `username`
* `email`
* `token` for verification and password reset messages

Example `templates/emails/verification.html`:

```html
<p>Hello {{ username }},</p>
<p>Use this token to verify {{ email }}:</p>
<p><strong>{{ token }}</strong></p>
```

## Configuration

```python
SMTPEmailSender(
    host="smtp.example.com",
    from_email="noreply@example.com",
    port=587,
    username=None,
    password=None,
    from_name=None,
    template_dir=None,
    verification_subject="Verify your email",
    password_reset_subject="Reset your password",
    email_verified_subject="Email verified",
    password_changed_subject="Password changed",
    account_deleted_subject="Account deleted",
    use_starttls=True,
    use_ssl=False,
    ssl_context=None,
    allow_insecure=False,
    timeout=10,
)
```

TLS certificate and hostname verification use Python's secure default SSL
context. Pass `ssl_context` only when the application needs a custom trusted
certificate authority or TLS policy. At least one of `use_starttls` and
`use_ssl` must be enabled by default. Set `allow_insecure=True` only for a
trusted local SMTP relay where plaintext transport is an explicit decision.

## License

UserHarbor SMTP is released under the MIT License.
