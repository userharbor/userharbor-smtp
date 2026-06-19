from userharbor_smtp import SMTPEmailSender
from userharbor_smtp.sender import SMTPEmailSender as SenderImplementation


def test_exports_smtp_email_sender() -> None:
    assert SMTPEmailSender is SenderImplementation
