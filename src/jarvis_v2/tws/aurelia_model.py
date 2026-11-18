"""Deterministic portable Aurelia model package and independent validator."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import math
import re
import struct
from typing import Any


MAGIC = b"ARCHON-AURELIA-MODEL\x01"
MAX_MODEL_BYTES = 1024 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class ModelValidationError(ValueError):
    """Raised when a portable model fails a deterministic assertion."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ModelValidationError(f"invalid {label}")
    return value


def _positive_int(value: object, label: str, maximum: int) -> int:
    if type(value) is not int or value < 1 or value > maximum:
        raise ModelValidationError(f"invalid {label}")
    return value


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ModelValidationError(f"invalid {label}")
    return float(value)


def _validate_payload(payload: object) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ModelValidationError("model payload must be an object")
    model_id = _identifier(payload.get("model_id"), "model id")
    vertex_count = _positive_int(payload.get("vertex_count"), "vertex count", 1_000_000)

    bones = payload.get("bones")
    if not isinstance(bones, list) or not 1 <= len(bones) <= 256:
        raise ModelValidationError("invalid bones")
    bone_ids: set[str] = set()
    parents: dict[str, str | None] = {}
    for bone in bones:
        if not isinstance(bone, Mapping):
            raise ModelValidationError("invalid bone")
        bone_id = _identifier(bone.get("id"), "bone id")
        if bone_id in bone_ids:
            raise ModelValidationError("duplicate bone id")
        parent = bone.get("parent")
        if parent is not None:
            parent = _identifier(parent, "bone parent")
        bone_ids.add(bone_id)
        parents[bone_id] = parent
    if any(parent is not None and parent not in bone_ids for parent in parents.values()):
        raise ModelValidationError("bone parent is unknown")
    if not any(parent is None for parent in parents.values()):
        raise ModelValidationError("model has no root bone")
    for bone_id in bone_ids:
        seen: set[str] = set()
        current: str | None = bone_id
        while current is not None:
            if current in seen:
                raise ModelValidationError("bone hierarchy contains a cycle")
            seen.add(current)
            current = parents[current]

    deformation = payload.get("deformation")
    if not isinstance(deformation, Mapping):
        raise ModelValidationError("invalid deformation")
    max_influences = _positive_int(deformation.get("max_influences"), "max influences", 8)
    weights = deformation.get("weights")
    if not isinstance(weights, list) or not weights:
        raise ModelValidationError("invalid deformation weights")
    totals = [0.0] * vertex_count
    influences: dict[int, set[str]] = {}
    for item in weights:
        if not isinstance(item, Mapping):
            raise ModelValidationError("invalid deformation weight")
        vertex = item.get("vertex")
        if type(vertex) is not int or not 0 <= vertex < vertex_count:
            raise ModelValidationError("deformation vertex is outside the model")
        bone_id = _identifier(item.get("bone"), "deformation bone")
        if bone_id not in bone_ids:
            raise ModelValidationError("deformation bone is unknown")
        weight = _number(item.get("weight"), "deformation weight")
        if not 0.0 < weight <= 1.0:
            raise ModelValidationError("deformation weight is outside the range")
        vertex_influences = influences.setdefault(vertex, set())
        if bone_id in vertex_influences:
            raise ModelValidationError("duplicate deformation influence")
        vertex_influences.add(bone_id)
        if len(vertex_influences) > max_influences:
            raise ModelValidationError("vertex has too many deformation influences")
        totals[vertex] += weight
    if any(not math.isclose(total, 1.0, abs_tol=1e-6) for total in totals):
        raise ModelValidationError("deformation weights must sum to one per vertex")

    morphs = payload.get("morphs")
    if not isinstance(morphs, list) or not 1 <= len(morphs) <= 128:
        raise ModelValidationError("invalid morphs")
    morph_ids: set[str] = set()
    for morph in morphs:
        if not isinstance(morph, Mapping):
            raise ModelValidationError("invalid morph")
        morph_id = _identifier(morph.get("id"), "morph id")
        if morph_id in morph_ids:
            raise ModelValidationError("duplicate morph id")
        morph_ids.add(morph_id)
        deltas = morph.get("deltas")
        if not isinstance(deltas, list) or len(deltas) != vertex_count:
            raise ModelValidationError("morph delta count does not match vertices")
        for delta in deltas:
            if not isinstance(delta, list) or len(delta) != 3:
                raise ModelValidationError("morph delta must have three coordinates")
            for coordinate in delta:
                if abs(_number(coordinate, "morph coordinate")) > 1_000_000:
                    raise ModelValidationError("morph coordinate is outside the range")

    clips = payload.get("clips")
    if not isinstance(clips, list) or not 1 <= len(clips) <= 128:
        raise ModelValidationError("invalid clips")
    clip_ids: set[str] = set()
    for clip in clips:
        if not isinstance(clip, Mapping):
            raise ModelValidationError("invalid clip")
        clip_id = _identifier(clip.get("id"), "clip id")
        if clip_id in clip_ids:
            raise ModelValidationError("duplicate clip id")
        clip_ids.add(clip_id)
        duration_ms = _positive_int(clip.get("duration_ms"), "clip duration", 86_400_000)
        channels = clip.get("channels")
        if not isinstance(channels, list) or not channels:
            raise ModelValidationError("clip has no channels")
        channel_ids = [_identifier(channel, "clip channel") for channel in channels]
        if len(channel_ids) != len(set(channel_ids)):
            raise ModelValidationError("clip has duplicate channels")
        if any(channel not in bone_ids for channel in channel_ids):
            raise ModelValidationError("clip channel is unknown")
        keyframes = clip.get("keyframes")
        if not isinstance(keyframes, list) or not keyframes:
            raise ModelValidationError("clip has no keyframes")
        previous_time = -1
        for keyframe in keyframes:
            if not isinstance(keyframe, Mapping) or type(keyframe.get("time_ms")) is not int:
                raise ModelValidationError("invalid clip keyframe")
            time_ms = keyframe["time_ms"]
            if not 0 <= time_ms <= duration_ms or time_ms <= previous_time:
                raise ModelValidationError("clip keyframe time is not monotonic")
            previous_time = time_ms

    return {
        "model_id": model_id,
        "vertex_count": vertex_count,
        "bone_count": len(bones),
        "morph_ids": tuple(sorted(morph_ids)),
        "clip_ids": tuple(sorted(clip_ids)),
    }


def build_portable_model(spec: Mapping[str, object]) -> bytes:
    """Build a deterministic binary package after validating its assertions."""
    summary = _validate_payload(spec)
    del summary
    try:
        encoded = json.dumps(
            dict(spec), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ModelValidationError("model payload is not canonical JSON") from exc
    package = MAGIC + struct.pack(">I", len(encoded)) + encoded
    if len(package) > MAX_MODEL_BYTES:
        raise ModelValidationError("model package is too large")
    return package


def validate_portable_model(package: bytes | bytearray) -> dict[str, Any]:
    """Validate package framing and all deformation, morph and clip assertions."""
    if not isinstance(package, (bytes, bytearray)) or len(package) > MAX_MODEL_BYTES:
        raise ModelValidationError("invalid model package")
    raw = bytes(package)
    if len(raw) < len(MAGIC) + 4 or not raw.startswith(MAGIC):
        raise ModelValidationError("invalid model package header")
    payload_length = struct.unpack(">I", raw[len(MAGIC):len(MAGIC) + 4])[0]
    payload = raw[len(MAGIC) + 4:]
    if payload_length != len(payload):
        raise ModelValidationError("model package length mismatch")
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelValidationError("model package payload is invalid") from exc
    summary = _validate_payload(decoded)
    return {
        **summary,
        "binary_sha256": hashlib.sha256(raw).hexdigest(),
        "assertions": {"deformation": True, "morphs": True, "clips": True},
    }


def validate_visual_qa_manifest(manifest: Mapping[str, object]) -> dict[str, Any]:
    """Validate the bounded, time-sampled TWS-012 visual-QA manifest."""
    if not isinstance(manifest, Mapping) or manifest.get("task_id") != "TWS-012":
        raise ModelValidationError("invalid visual-QA task")
    source = manifest.get("source")
    tool = manifest.get("tool")
    if (not isinstance(source, Mapping)
            or not re.fullmatch(r"[0-9a-f]{64}", str(source.get("sha256", "")))
            or not isinstance(tool, Mapping)
            or tool.get("name") != "Blender"
            or tool.get("version") != "5.3.0"):
        raise ModelValidationError("invalid visual-QA provenance")
    views = manifest.get("views")
    indices = (
        [item.get("index") if isinstance(item, Mapping) else None for item in views]
        if isinstance(views, list) else []
    )
    if (not isinstance(views, list) or len(views) != 24
            or any(type(index) is not int for index in indices)
            or set(indices) != set(range(24))):
        raise ModelValidationError("visual-QA manifest must contain 24 unique views")
    if any(not isinstance(item, Mapping)
           or not isinstance(item.get("path"), str) or not item["path"]
           or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", "")))
           for item in views):
        raise ModelValidationError("visual-QA view artifact is invalid")
    actions = manifest.get("actions")
    motion_actions = manifest.get("motion_actions")
    if (manifest.get("motion_present") is not True
            or not isinstance(actions, list)
            or not isinstance(motion_actions, list)
            or not motion_actions
            or any(not isinstance(name, str) for name in motion_actions)
            or len(motion_actions) != len(set(motion_actions))):
        raise ModelValidationError("visual-QA motion evidence is missing")
    by_track = {item.get("track"): item for item in actions if isinstance(item, Mapping)}
    for name in motion_actions:
        action = by_track.get(name)
        samples = action.get("samples") if isinstance(action, Mapping) else None
        if (not isinstance(action, Mapping) or action.get("pose_changed") is not True
                or not isinstance(samples, list) or len(samples) < 3
                or any(not isinstance(sample, Mapping)
                       or type(sample.get("frame")) is not int
                       or not re.fullmatch(r"[0-9a-f]{64}", str(sample.get("pose_sha256", "")))
                       for sample in samples)):
            raise ModelValidationError(f"visual-QA motion track is incomplete: {name}")
    return {
        "task_id": "TWS-012",
        "view_count": len(views),
        "motion_actions": tuple(motion_actions),
        "source_sha256": source["sha256"],
        "tool_version": tool["version"],
    }


def default_aurelia_spec() -> dict[str, Any]:
    """Return a small deterministic fixture for portable generation tests."""
    return {
        "model_id": "aurelia",
        "vertex_count": 3,
        "bones": [
            {"id": "root", "parent": None},
            {"id": "spine", "parent": "root"},
            {"id": "wing_l", "parent": "spine"},
            {"id": "wing_r", "parent": "spine"},
        ],
        "deformation": {
            "max_influences": 2,
            "weights": [
                {"vertex": 0, "bone": "root", "weight": 1.0},
                {"vertex": 1, "bone": "spine", "weight": 0.75},
                {"vertex": 1, "bone": "root", "weight": 0.25},
                {"vertex": 2, "bone": "wing_l", "weight": 0.5},
                {"vertex": 2, "bone": "wing_r", "weight": 0.5},
            ],
        },
        "morphs": [{"id": "smile", "deltas": [[0.0, 0.0, 0.0], [0.01, 0.0, 0.0], [0.0, 0.0, 0.0]]}],
        "clips": [{
            "id": "idle",
            "duration_ms": 1000,
            "channels": ["root", "spine"],
            "keyframes": [{"time_ms": 0}, {"time_ms": 1000}],
        }],
    }


__all__ = [
    "MAGIC",
    "MAX_MODEL_BYTES",
    "ModelValidationError",
    "build_portable_model",
    "default_aurelia_spec",
    "validate_visual_qa_manifest",
    "validate_portable_model",
]
