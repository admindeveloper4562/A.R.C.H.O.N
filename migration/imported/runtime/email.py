"""Typed email connector boundary and deterministic local fixture provider."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class MailMessage:
    message_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    unread: bool = True

class EmailProvider(Protocol):
    name: str
    account: str
    def search(self, query: str) -> list[MailMessage]: ...
    def send(self, recipient: str, subject: str, body: str) -> str: ...

class SampleEmailProvider:
    name = "sample"
    account = "owner@example.test"
    def __init__(self) -> None:
        self.messages = [MailMessage("sample-mail-1", "team@example.test", self.account, "JARVIS sample inbox", "Fixture message; not an external mailbox.")]
        self.sent: list[MailMessage] = []
    def search(self, query: str) -> list[MailMessage]:
        needle = query.casefold().strip()
        return [m for m in self.messages if not needle or needle in (m.sender + " " + m.subject + " " + m.body).casefold()]
    def send(self, recipient: str, subject: str, body: str) -> str:
        message_id = f"sample-sent-{len(self.sent) + 1}"
        self.sent.append(MailMessage(message_id, self.account, recipient, subject, body, False))
        return message_id
