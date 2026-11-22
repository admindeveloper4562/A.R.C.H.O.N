"""Read-only module dashboard adapters over ARCHON's existing local services."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any


MAX_INDEX_FILES = 2_000
MAX_INDEX_BYTES = 64 * 1024 * 1024
MAX_INDEX_SOURCE_BYTES = 512 * 1024
_INDEX_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".py", ".sh", ".sql", ".toml", ".ts", ".tsx", ".yaml", ".yml"}
_INDEX_ROOTS = ("apps/", "docs/architecture/", "src/")
_INDEX_FILES = {"README.md", "SECURITY.md", "CODING_HANDBOOK.md", "config/modules.json"}
_STATE_LOCK = threading.RLock()


class ModuleRuntimeError(ValueError):
    """Raised when a bounded local module view is unavailable."""


class ModuleRuntime:
    """Connect local module stores to the loopback dashboard."""

    def __init__(self, state_dir: str | Path, repository: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.repository = Path(repository).resolve(strict=True)
        if not self.repository.is_dir():
            raise ModuleRuntimeError("repository_unavailable")

    def snapshot(self, module: str, *, query: str = "") -> dict[str, Any]:
        if not isinstance(module, str):
            raise ModuleRuntimeError("module_invalid")
        with _STATE_LOCK:
            if module == "research":
                return self._research(query)
            if module == "tws":
                return self._tws()
            if module == "wic":
                return self._wic()
            if module == "finance":
                return self._finance()
            if module == "automation":
                return self._automation()
        raise ModuleRuntimeError("module_data_unavailable")

    def action(self, module: str, action: str, payload: Any) -> dict[str, Any]:
        if not isinstance(module, str) or not isinstance(action, str) or not isinstance(payload, dict):
            raise ModuleRuntimeError("module_action_invalid")
        with _STATE_LOCK:
            if module == "tws":
                from jarvis_v2.tws import QuestStore

                if action == "add_wing":
                    data = self._action_payload(payload, {"wing_id", "name"})
                    with QuestStore(self._database("tws.sqlite3")) as store:
                        record = store.add_wing(data["wing_id"], data["name"])
                elif action == "create_quest":
                    data = self._action_payload(
                        payload, {"quest_id", "wing_id", "title"}, {"kind", "cadence"}
                    )
                    with QuestStore(self._database("tws.sqlite3")) as store:
                        record = store.create_quest(
                            data["quest_id"], data["wing_id"], data["title"],
                            kind=data.get("kind", "skill"), cadence=data.get("cadence", "once"),
                        )
                else:
                    raise ModuleRuntimeError("module_action_not_allowed")
            elif module == "finance":
                from jarvis_v2.finance.paper import PaperAccount, PaperLedger, PaperOrder

                if action == "open_paper_account":
                    data = self._action_payload(payload, {"account_id", "scope_id", "currency", "cash_satang"})
                    if type(data["cash_satang"]) is not int:
                        raise ModuleRuntimeError("module_action_invalid")
                    account = PaperAccount(
                        data["account_id"], data["scope_id"], data["currency"], data["cash_satang"], self._now()
                    )
                    with PaperLedger(self._database("paper-finance.sqlite3")) as ledger:
                        record = ledger.open_account(account).as_dict()
                elif action == "place_paper_order":
                    data = self._action_payload(
                        payload, {"order_id", "account_id", "symbol", "side", "quantity", "price_satang"}
                    )
                    if any(type(data[name]) is not int for name in ("quantity", "price_satang")):
                        raise ModuleRuntimeError("module_action_invalid")
                    order = PaperOrder(
                        data["order_id"], data["account_id"], data["symbol"], data["side"],
                        data["quantity"], data["price_satang"], "pending", self._now(),
                    )
                    with PaperLedger(self._database("paper-finance.sqlite3")) as ledger:
                        record = ledger.place_order(order).as_dict()
                elif action == "fill_paper_order":
                    data = self._action_payload(payload, {"order_id"})
                    with PaperLedger(self._database("paper-finance.sqlite3")) as ledger:
                        record = ledger.fill_order(data["order_id"], filled_at=self._now()).as_dict()
                else:
                    raise ModuleRuntimeError("module_action_not_allowed")
            elif module == "automation":
                from jarvis_v2.automation.scheduler import AutomationScheduleStore

                if action == "schedule_once":
                    data = self._action_payload(
                        payload, {"schedule_id", "message", "due_at"}, {"timezone_name"}
                    )
                    with AutomationScheduleStore(self._database("automation.sqlite3")) as store:
                        record = store.schedule_once(
                            data["schedule_id"], data["message"], data["due_at"],
                            timezone_name=data.get("timezone_name", "UTC"),
                        ).as_dict()
                elif action == "cancel_schedule":
                    data = self._action_payload(payload, {"schedule_id"})
                    with AutomationScheduleStore(self._database("automation.sqlite3")) as store:
                        record = store.cancel(data["schedule_id"]).as_dict()
                else:
                    raise ModuleRuntimeError("module_action_not_allowed")
            else:
                raise ModuleRuntimeError("module_action_not_allowed")
        return {"module": module, "action": action, "mode": "paper_only" if module == "finance" else "local_only", "record": record}

    @staticmethod
    def _action_payload(payload: dict[str, Any], required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
        allowed = required | (optional or set())
        if not required <= payload.keys() or not payload.keys() <= allowed:
            raise ModuleRuntimeError("module_action_invalid")
        return payload

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def _module_directory(self) -> Path:
        state = self.state_dir
        try:
            details = state.lstat()
        except OSError as exc:
            raise ModuleRuntimeError("state_directory_unavailable") from exc
        if (
            not stat.S_ISDIR(details.st_mode)
            or details.st_uid != os.geteuid()
            or stat.S_IMODE(details.st_mode) & 0o077
        ):
            raise ModuleRuntimeError("state_directory_not_private")
        directory = state / "modules"
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise ModuleRuntimeError("module_state_unavailable") from exc
        details = directory.lstat()
        if (
            not stat.S_ISDIR(details.st_mode)
            or details.st_uid != os.geteuid()
            or stat.S_IMODE(details.st_mode) & 0o077
        ):
            raise ModuleRuntimeError("module_state_not_private")
        return directory

    def _database(self, name: str) -> Path:
        directory = self._module_directory()
        path = directory / name
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path, flags, 0o600)
        except FileExistsError:
            pass
        except OSError as exc:
            raise ModuleRuntimeError("module_database_unavailable") from exc
        else:
            os.close(descriptor)
        try:
            details = path.lstat()
        except OSError as exc:
            raise ModuleRuntimeError("module_database_unavailable") from exc
        if (
            not stat.S_ISREG(details.st_mode)
            or details.st_uid != os.geteuid()
            or stat.S_IMODE(details.st_mode) & 0o077
        ):
            raise ModuleRuntimeError("module_database_not_private")
        return path

    def _research(self, query: str) -> dict[str, Any]:
        from jarvis_v2.backend.code_index import RepositoryIndex

        if not isinstance(query, str) or len(query.encode("utf-8")) > 512:
            raise ModuleRuntimeError("research_query_invalid")
        database = self._database("research-index.sqlite3")
        metadata_path = database.with_suffix(".json")
        sources, snapshot_sha = self._tracked_sources()
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            metadata = {}
        if metadata.get("snapshot_sha") != snapshot_sha:
            indexed = excluded = 0
            try:
                with RepositoryIndex(database) as index:
                    for path, content in sources:
                        blob_sha = hashlib.sha1(
                            b"blob " + str(len(content)).encode("ascii") + b"\0" + content
                        ).hexdigest()
                        result = index.index_file(
                            path, content, blob_sha=blob_sha, source_sha=snapshot_sha,
                        )
                        excluded += int(bool(result.get("excluded")))
                        indexed += int(bool(result.get("indexed")))
            except Exception as exc:
                raise ModuleRuntimeError("research_index_unavailable") from exc
            metadata = {
                "snapshot_sha": snapshot_sha,
                "source_files": len(sources),
                "indexed_files": indexed,
                "excluded_sensitive": excluded,
            }
            self._write_metadata(metadata_path, metadata)
        try:
            with RepositoryIndex(database) as index:
                results = index.search(query, limit=12, source_sha=snapshot_sha) if query.strip() else []
        except Exception as exc:
            raise ModuleRuntimeError("research_query_failed") from exc
        return {
            "module": "research",
            "mode": "local_repository",
            "summary": "Searches tracked ARCHON source, configuration, and architecture documents. It does not fetch external sources.",
            "snapshot_sha": snapshot_sha,
            "metrics": [
                {"label": "Indexed files", "value": str(metadata.get("indexed_files", 0))},
                {"label": "Excluded sensitive files", "value": str(metadata.get("excluded_sensitive", 0))},
                {"label": "Matches", "value": str(len(results))},
            ],
            "sections": [{
                "title": "Local source matches",
                "items": [
                    {"title": item["path"], "details": item["snippet"], "source_sha": item["source_sha"]}
                    for item in results
                ],
            }],
        }

    def _tracked_sources(self) -> tuple[list[tuple[str, bytes]], str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repository), "ls-files", "-z"],
                check=True, capture_output=True, timeout=5,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ModuleRuntimeError("research_repository_unavailable") from exc
        sources: list[tuple[str, bytes]] = []
        total = 0
        digest = hashlib.sha1()
        for raw_path in result.stdout.split(b"\0"):
            if not raw_path:
                continue
            try:
                name = raw_path.decode("utf-8")
            except UnicodeDecodeError:
                continue
            path = PurePosixPath(name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or path.suffix.lower() not in _INDEX_SUFFIXES
                or not (name in _INDEX_FILES or name.startswith(_INDEX_ROOTS))
            ):
                continue
            source = self.repository.joinpath(*path.parts)
            try:
                details = source.lstat()
                if not stat.S_ISREG(details.st_mode) or details.st_size > MAX_INDEX_SOURCE_BYTES:
                    continue
                content = source.read_bytes()
                content.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            total += len(content)
            if total > MAX_INDEX_BYTES or len(sources) >= MAX_INDEX_FILES:
                raise ModuleRuntimeError("research_index_limit_exceeded")
            sources.append((name, content))
            digest.update(name.encode("utf-8") + b"\0" + hashlib.sha256(content).digest())
        if not sources:
            raise ModuleRuntimeError("research_sources_unavailable")
        return sources, digest.hexdigest()[:40]

    @staticmethod
    def _write_metadata(path: Path, value: dict[str, Any]) -> None:
        if path.is_symlink():
            raise ModuleRuntimeError("research_metadata_unavailable")
        descriptor, temporary = tempfile.mkstemp(prefix="research-index-", dir=path.parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(value, stream, sort_keys=True)
                stream.write("\n")
            os.replace(temporary, path)
        except OSError as exc:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise ModuleRuntimeError("research_metadata_unavailable") from exc

    def _tws(self) -> dict[str, Any]:
        from jarvis_v2.tws import QuestStore

        try:
            with QuestStore(self._database("tws.sqlite3")) as store:
                snapshot = store.sanctuary_snapshot()
        except Exception as exc:
            raise ModuleRuntimeError("tws_store_unavailable") from exc
        wings = snapshot.get("wings", [])
        quests = snapshot.get("quests", [])
        return {
            "module": "tws",
            "mode": "local_quest_store",
            "summary": "Quest and wing state is read from the persistent local TWS store.",
            "metrics": [
                {"label": "Wings", "value": str(len(wings))},
                {"label": "Quests", "value": str(len(quests))},
                {"label": "Store", "value": "READY"},
            ],
            "sections": [
                {"title": "Wings", "items": [
                    {"title": str(item.get("name") or item.get("wing_id") or "Wing"),
                     "details": str(item.get("state", "unknown"))}
                    for item in wings if isinstance(item, dict)
                ]},
                {"title": "Quests", "items": [
                    {"title": str(item.get("title") or item.get("quest_id") or "Quest"),
                     "details": f'{item.get("state", "unknown")} · {item.get("kind", "skill")}'}
                    for item in quests if isinstance(item, dict)
                ]},
            ],
        }

    def _wic(self) -> dict[str, Any]:
        from jarvis_v2.wic import SourceStore

        try:
            with SourceStore(self._database("wic.sqlite3")) as store:
                observations = [item.as_dict() for item in store.observations()[-20:]]
        except Exception as exc:
            raise ModuleRuntimeError("wic_store_unavailable") from exc
        source_count = len({item.get("source_id") for item in observations if item.get("source_id")})
        return {
            "module": "wic",
            "mode": "local_source_archive",
            "summary": "The provenance archive is available. No feed list is configured, so no external world data is fetched.",
            "metrics": [
                {"label": "Recorded sources", "value": str(source_count)},
                {"label": "Observations", "value": str(len(observations))},
                {"label": "Feed ingestion", "value": "NOT CONFIGURED"},
            ],
            "sections": [{"title": "Recent source observations", "items": [
                {"title": str(item.get("title") or item.get("source_id") or "Source observation"),
                 "details": f'{item.get("published_at") or "publication date unknown"} · fetched {item.get("fetched_at") or "unknown"}',
                 "url": str(item.get("article_url") or "")}
                for item in observations
            ]}],
        }

    def _finance(self) -> dict[str, Any]:
        from jarvis_v2.finance.paper import PaperLedger

        try:
            with PaperLedger(self._database("paper-finance.sqlite3")) as ledger:
                accounts = ledger.accounts()
                items = []
                order_count = 0
                position_count = 0
                for account in accounts:
                    positions = ledger.positions(account.account_id)
                    orders = ledger.orders(account.account_id)
                    order_count += len(orders)
                    position_count += len(positions)
                    items.append({
                        "title": account.account_id,
                        "details": f'{account.currency} · {account.cash_satang} satang · {len(positions)} positions · {len(orders)} orders',
                    })
        except Exception as exc:
            raise ModuleRuntimeError("finance_paper_store_unavailable") from exc
        return {
            "module": "finance",
            "mode": "paper_only",
            "summary": "This dashboard reads the isolated paper ledger. It does not connect to accounts or submit real transactions.",
            "metrics": [
                {"label": "Paper accounts", "value": str(len(accounts))},
                {"label": "Paper orders", "value": str(order_count)},
                {"label": "Paper positions", "value": str(position_count)},
                {"label": "Real effects", "value": "LOCKED"},
            ],
            "sections": [{"title": "Paper accounts", "items": items}],
        }

    def _automation(self) -> dict[str, Any]:
        from jarvis_v2.automation.scheduler import AutomationScheduleStore

        try:
            with AutomationScheduleStore(self._database("automation.sqlite3")) as store:
                schedules = [item.as_dict() for item in store.list_reminders(limit=100)]
                due = [item.as_dict() for item in store.due(limit=100)]
        except Exception as exc:
            raise ModuleRuntimeError("automation_store_unavailable") from exc
        return {
            "module": "automation",
            "mode": "persistent_local_schedules",
            "summary": "The timezone-aware schedule store is active. Due entries are reported locally; no external action is dispatched.",
            "metrics": [
                {"label": "Active schedules", "value": str(len(schedules))},
                {"label": "Due now", "value": str(len(due))},
                {"label": "External dispatch", "value": "DISABLED"},
            ],
            "sections": [{"title": "Active schedules", "items": [
                {"schedule_id": str(item.get("reminder_id") or ""),
                 "title": str(item.get("message") or item.get("reminder_id") or "Reminder"),
                 "details": f'{item.get("next_due_utc", "unknown")} · {item.get("timezone", "UTC")} · {item.get("recurrence", "once")}' }
                for item in schedules
            ]}, {"title": "Due now", "items": [
                {"schedule_id": str(item.get("reminder_id") or ""),
                 "title": str(item.get("message") or item.get("reminder_id") or "Reminder"),
                 "details": f'{item.get("next_due_utc", "unknown")} · {item.get("timezone", "UTC")}' }
                for item in due
            ], "empty": "No reminders are due."}],
        }


__all__ = ["ModuleRuntime", "ModuleRuntimeError"]
