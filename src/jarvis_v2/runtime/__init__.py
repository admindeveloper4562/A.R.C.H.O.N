"""ARCHON Runtime boundary over authenticated Core and Backend services."""

from .service import (
    RUNTIME_HEALTH_SCOPE,
    RUNTIME_MODULE,
    RUNTIME_READ_SCOPE,
    RuntimeResponse,
    RuntimeService,
    RuntimeServiceError,
)
from .security import OwnerSession, RuntimeSecurity, RuntimeSecurityError, SECURITY_HEADERS
from .chat import ChatService, ChatServiceError
from .offline import LocalAdapter, OfflineChatService, OfflineChatServiceError
from .speech import MAX_AUDIO_CHUNK_BYTES, MAX_AUDIO_CHUNKS, SpeechAdapter, SpeechService, SpeechServiceError
from .browser import (
    BrowserActionReceipt,
    BrowserAdapter,
    BrowserProfile,
    BrowserProfileError,
    BrowserProfileService,
    BrowserToolError,
    BrowserToolResult,
    BrowserToolService,
    LoginHandoff,
)
from .file_actions import FileActionError, FileActionRequest, FileActionService, FileIdentity
from .calendar import (
    CALENDAR_READ_SCOPE,
    CALENDAR_WRITE_SCOPE,
    CalendarAdapter,
    CalendarAuthorizationError,
    CalendarConnector,
    CalendarError,
    CalendarEvent,
    CalendarService,
)

__all__ = [
    "RUNTIME_HEALTH_SCOPE",
    "RUNTIME_MODULE",
    "RUNTIME_READ_SCOPE",
    "RuntimeResponse",
    "RuntimeService",
    "RuntimeServiceError",
    "OwnerSession",
    "RuntimeSecurity",
    "RuntimeSecurityError",
    "SECURITY_HEADERS",
    "ChatService",
    "ChatServiceError",
    "LocalAdapter",
    "OfflineChatService",
    "OfflineChatServiceError",
    "MAX_AUDIO_CHUNK_BYTES",
    "MAX_AUDIO_CHUNKS",
    "SpeechAdapter",
    "SpeechService",
    "SpeechServiceError",
    "BrowserActionReceipt",
    "BrowserAdapter",
    "BrowserProfile",
    "BrowserProfileError",
    "BrowserProfileService",
    "BrowserToolError",
    "BrowserToolResult",
    "BrowserToolService",
    "LoginHandoff",
    "FileActionError",
    "FileActionRequest",
    "FileActionService",
    "FileIdentity",
    "CALENDAR_READ_SCOPE",
    "CALENDAR_WRITE_SCOPE",
    "CalendarAdapter",
    "CalendarAuthorizationError",
    "CalendarConnector",
    "CalendarError",
    "CalendarEvent",
    "CalendarService",
]
