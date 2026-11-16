"""JARVIS v2 Core boundary and immutable module capability registry."""

from .registry import CoreRegistryError, CoreService, ModuleCapability, ModuleRegistry
from .dispatch import DispatchError, DispatchStore
from .dependency import DependencyError, DependencyOrchestrator
from .event_session import EventSessionError, EventSessionInterpreter
from .session import SessionError, TaskSessionStore

__all__ = [
    "CoreRegistryError",
    "CoreService",
    "DispatchError",
    "DispatchStore",
    "DependencyError",
    "DependencyOrchestrator",
    "ModuleCapability",
    "ModuleRegistry",
    "EventSessionError",
    "EventSessionInterpreter",
    "SessionError",
    "TaskSessionStore",
]
