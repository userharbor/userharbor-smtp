from __future__ import annotations

import base64
import socketserver
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from typing import cast

import pytest


@dataclass
class SMTPAuthAttempt:
    username: str
    password: str


@dataclass
class SMTPEnvelope:
    mail_from: str | None
    rcpt_tos: list[str]
    message: EmailMessage


class RecordingSMTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), RecordingSMTPHandler)
        self.auth_username = "smtp-user"
        self.auth_password = "smtp-password"
        self.auth_attempts: list[SMTPAuthAttempt] = []
        self.messages: list[SMTPEnvelope] = []

    @property
    def host(self) -> str:
        address = cast(tuple[str, int], self.server_address)
        return address[0]

    @property
    def port(self) -> int:
        address = cast(tuple[str, int], self.server_address)
        return address[1]


class RecordingSMTPHandler(socketserver.StreamRequestHandler):
    server: RecordingSMTPServer

    def handle(self) -> None:
        self._write("220 test smtp ready")
        mail_from: str | None = None
        rcpt_tos: list[str] = []

        while line := self.rfile.readline():
            command = line.decode("utf-8").rstrip("\r\n")
            upper_command = command.upper()

            if upper_command.startswith(("EHLO", "HELO")):
                self.wfile.write(
                    b"250-localhost\r\n"
                    b"250-AUTH PLAIN\r\n"
                    b"250 SIZE 1000000\r\n"
                )
            elif upper_command.startswith("AUTH PLAIN"):
                self._handle_auth_plain(command)
            elif upper_command.startswith("MAIL FROM:"):
                mail_from = command[len("MAIL FROM:") :].strip()
                self._write("250 ok")
            elif upper_command.startswith("RCPT TO:"):
                rcpt_tos.append(command[len("RCPT TO:") :].strip())
                self._write("250 ok")
            elif upper_command == "DATA":
                self._write("354 end data with <CR><LF>.<CR><LF>")
                raw_message = self._read_data()
                message = BytesParser(policy=policy.default).parsebytes(raw_message)
                self.server.messages.append(
                    SMTPEnvelope(
                        mail_from=mail_from,
                        rcpt_tos=rcpt_tos.copy(),
                        message=message,
                    )
                )
                self._write("250 accepted")
            elif upper_command == "RSET":
                mail_from = None
                rcpt_tos.clear()
                self._write("250 ok")
            elif upper_command == "QUIT":
                self._write("221 bye")
                return
            else:
                self._write("250 ok")

    def _handle_auth_plain(self, command: str) -> None:
        encoded_credentials = command.split(" ", 2)[2]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        _, username, password = decoded_credentials.split("\x00", 2)
        self.server.auth_attempts.append(SMTPAuthAttempt(username, password))

        if (
            username == self.server.auth_username
            and password == self.server.auth_password
        ):
            self._write("235 authenticated")
            return

        self._write("535 authentication failed")

    def _read_data(self) -> bytes:
        lines: list[bytes] = []

        while line := self.rfile.readline():
            if line == b".\r\n":
                break
            if line.startswith(b".."):
                line = line[1:]
            lines.append(line)

        return b"".join(lines)

    def _write(self, line: str) -> None:
        self.wfile.write(f"{line}\r\n".encode("utf-8"))


@pytest.fixture
def smtp_server() -> Iterator[RecordingSMTPServer]:
    server = RecordingSMTPServer()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)
