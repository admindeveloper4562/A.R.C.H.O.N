"""JARVIS v2 Core boundary and immutable module capability registry."""

from .registry import CoreRegistryError, CoreService, ModuleCapability, ModuleRegistry
from .dispatch import DispatchError, DispatchStore
from .dependency import DependencyError, DependencyOrchestrator
from .event_session import EventSessionError, EventSessionInterpreter
from .intent import IntentError, OwnerIntentRouter
from .model_policy import ModelPolicy, ModelPolicyError, ModelResolution
from .session import SessionError, TaskSessionStore
from .timeline import MAX_TIMELINE_ENTRIES, TaskTimeline, TimelineError
from .budget import ResourceBudget, ResourceBudgetError
from .control import CONTROL_STATES, ControlError, CoreControls

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
    "IntentError",
    "OwnerIntentRouter",
    "ModelPolicy",
    "ModelPolicyError",
    "ModelResolution",
    "MAX_TIMELINE_ENTRIES",
    "SessionError",
    "TaskSessionStore",
    "TaskTimeline",
    "TimelineError",
    "ResourceBudget",
    "ResourceBudgetError",
    "CONTROL_STATES",
    "ControlError",
    "CoreControls",
]
