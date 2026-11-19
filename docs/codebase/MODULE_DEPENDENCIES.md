# ARCHON Module Dependencies

| Module | Observed imports |
| --- | --- |
| `adapters.legacy_contracts` | `__future__`, `ast`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`, `typing` |
| `astra_one.__main__` | `.core`, `.planner`, `.runner`, `__future__`, `argparse`, `json`, `os`, `pathlib`, `shutil`, `sys`, `time`, `urllib.request` |
| `astra_one.core` | `.planner`, `.runner`, `__future__`, `contextlib`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sqlite3`, `subprocess`, `sys`, `uuid` |
| `astra_one.full_plan` | `__future__`, `dataclasses`, `hashlib`, `json`, `pathlib`, `typing` |
| `astra_one.linux_cli` | `.full_plan`, `.linux_runtime`, `.linux_sda`, `.supervisor`, `__future__`, `argparse`, `concurrent.futures`, `contextlib`, `functools`, `hashlib`, `json`, `os`, `pathlib`, `platform`, `re`, `shutil`, `subprocess`, `sys`, `time`, `uuid` |
| `astra_one.linux_runtime` | `.linux_sda`, `.test_evidence_cache`, `__future__`, `ast`, `hashlib`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `signal`, `sqlite3`, `stat`, `subprocess`, `tempfile`, `threading`, `time`, `tomllib`, `uuid` |
| `astra_one.linux_sda` | `.full_plan`, `.linux_runtime`, `.owner_approval`, `__future__`, `argparse`, `ast`, `concurrent.futures`, `contextlib`, `datetime`, `fcntl`, `hashlib`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `sqlite3`, `stat`, `subprocess`, `sys`, `threading`, `time`, `urllib.error`, `urllib.request`, `uuid` |
| `astra_one.owner_approval` | `__future__`, `argparse`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `subprocess`, `typing` |
| `astra_one.planner` | `.core`, `__future__`, `json`, `pathlib`, `re`, `urllib.request` |
| `astra_one.runner` | `.core`, `__future__`, `ast`, `datetime`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `subprocess`, `sys`, `threading`, `time`, `urllib.error`, `urllib.request`, `uuid` |
| `astra_one.supervisor` | `.linux_sda`, `__future__`, `datetime`, `hashlib`, `io`, `json`, `os`, `pathlib`, `re`, `sqlite3`, `subprocess`, `sys`, `tarfile`, `tempfile`, `typing`, `uuid` |
| `astra_one.test_evidence_cache` | `__future__`, `hashlib`, `json`, `os`, `pathlib`, `platform`, `subprocess`, `sys`, `typing` |
| `astra_watchdog` | `__future__`, `argparse`, `datetime`, `fcntl`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sqlite3`, `subprocess`, `sys` |
| `build_final_audit` | `__future__`, `argparse`, `ast`, `collections`, `datetime`, `hashlib`, `jarvis_v2.backend.code_index`, `json`, `os`, `pathlib`, `re`, `subprocess`, `sys`, `typing` |
| `check_git_policy` | `__future__`, `argparse`, `re`, `subprocess`, `sys` |
| `ci_checks` | `__future__`, `base64`, `hashlib`, `os`, `pathlib`, `re`, `stat`, `subprocess`, `sys`, `tempfile`, `tomllib`, `typing`, `zipfile` |
| `ci_report` | `__future__`, `argparse`, `json`, `os`, `pathlib`, `re`, `sys`, `typing` |
| `import_legacy` | `__future__`, `argparse`, `hashlib`, `json`, `os`, `pathlib`, `re`, `subprocess` |
| `imported.automation.windows.jarvis_queue_worker` | `__future__`, `argparse`, `dataclasses`, `json`, `logging`, `os`, `platform`, `socket`, `threading`, `time`, `typing`, `urllib.error`, `urllib.request`, `uuid` |
| `imported.backend.colibri` | `__future__`, `asyncio`, `dataclasses`, `ipaddress`, `json`, `math`, `os`, `pathlib`, `re`, `subprocess`, `time`, `typing`, `urllib.error`, `urllib.parse`, `urllib.request` |
| `imported.backend.permissions` | `.deletion_log`, `.storage`, `__future__`, `contextlib`, `ctypes`, `dataclasses`, `hashlib`, `os`, `pathlib`, `re`, `secrets`, `sqlite3`, `stat`, `sys`, `time` |
| `imported.backend.router` | `.colibri`, `__future__`, `asyncio`, `dataclasses`, `re`, `time`, `typing` |
| `imported.backend.storage` | `__future__`, `contextlib`, `pathlib`, `sqlite3`, `time`, `typing` |
| `imported.core.tasks` | `.storage`, `__future__`, `dataclasses`, `json`, `pathlib`, `secrets`, `time` |
| `imported.core.worker` | `.inventory`, `.tasks`, `__future__`, `asyncio`, `dataclasses`, `typing` |
| `imported.guardian.sda_module_integrity` | `__future__`, `argparse`, `hashlib`, `json`, `pathlib`, `re`, `sys` |
| `imported.guardian.sda_recovery_triage` | `__future__`, `argparse`, `importlib.util`, `json`, `pathlib`, `re` |
| `imported.runtime.calendar` | `__future__`, `datetime`, `zoneinfo` |
| `imported.runtime.email` | `__future__`, `dataclasses`, `typing` |
| `imported.runtime.inventory` | `.storage`, `__future__`, `dataclasses`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sqlite3`, `stat`, `time` |
| `imported.runtime.server` | `.calendar`, `.colibri`, `.diagnostics`, `.email`, `.inventory`, `.inventory_scheduler`, `.permissions`, `.storage`, `.tasks`, `.voice`, `.worker`, `__future__`, `asyncio`, `html`, `json`, `os`, `pathlib`, `re`, `secrets`, `sqlite3`, `string`, `time`, `urllib.parse`, `uuid` |
| `imported.runtime.voice` | `__future__`, `os`, `shutil` |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__` | `.core`, `.planner`, `.runner`, `__future__`, `argparse`, `json`, `os`, `pathlib`, `shutil`, `sys`, `time`, `urllib.request` |
| `imported.sda.astra_one_v0.2.0.astra_one.core` | `.planner`, `.runner`, `__future__`, `contextlib`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sqlite3`, `subprocess`, `sys`, `uuid` |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli` | `.linux_runtime`, `.linux_sda`, `__future__`, `argparse`, `concurrent.futures`, `json`, `os`, `pathlib`, `platform`, `re`, `shutil`, `subprocess`, `sys`, `time`, `uuid` |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime` | `.linux_sda`, `__future__`, `ast`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `signal`, `stat`, `subprocess`, `threading`, `time`, `tomllib`, `uuid` |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda` | `__future__`, `argparse`, `ast`, `concurrent.futures`, `contextlib`, `datetime`, `fcntl`, `hashlib`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `sqlite3`, `stat`, `subprocess`, `sys`, `threading`, `time`, `urllib.error`, `urllib.request`, `uuid` |
| `imported.sda.astra_one_v0.2.0.astra_one.planner` | `.core`, `__future__`, `json`, `pathlib`, `re`, `urllib.request` |
| `imported.sda.astra_one_v0.2.0.astra_one.runner` | `.core`, `__future__`, `ast`, `datetime`, `json`, `os`, `pathlib`, `queue`, `re`, `shutil`, `subprocess`, `sys`, `threading`, `time`, `urllib.error`, `urllib.request`, `uuid` |
| `imported.sda.codex_workhorse_v2` | `__future__`, `argparse`, `datetime`, `fcntl`, `json`, `os`, `pathlib`, `re`, `secrets`, `shutil`, `signal`, `sqlite3`, `subprocess`, `sys`, `time` |
| `imported.sda.sda_context_handoff` | `__future__`, `hashlib`, `json`, `re` |
| `imported.sda.workhorse_context` | `__future__`, `argparse`, `ast`, `hashlib`, `json`, `math`, `os`, `pathlib`, `re`, `sqlite3`, `struct`, `subprocess`, `urllib.parse`, `urllib.request` |
| `imported.tws.aurelia3d.build_portable` | `__future__`, `argparse`, `hashlib`, `json`, `math`, `pathlib`, `struct` |
| `imported.tws.engine` | `__future__`, `json`, `math`, `pathlib`, `sqlite3`, `urllib.parse` |
| `imported.tws.evidence` | `.`, `.engine`, `__future__`, `json` |
| `jarvis_v2.automation.device_registry` | `__future__`, `dataclasses`, `hashlib`, `hmac`, `jarvis_v2.backend.windows_agent`, `re` |
| `jarvis_v2.automation.dispatcher` | `__future__`, `collections.abc`, `dataclasses`, `jarvis_v2.automation.queue_api`, `jarvis_v2.backend.windows_agent`, `typing` |
| `jarvis_v2.automation.queue_api` | `__future__`, `dataclasses`, `jarvis_v2.core.queue`, `json`, `pathlib`, `sqlite3`, `time`, `typing` |
| `jarvis_v2.automation.recovery_drill` | `__future__`, `collections.abc`, `jarvis_v2.backend.backup`, `jarvis_v2.backend.event_bus`, `pathlib`, `typing` |
| `jarvis_v2.automation.scheduler` | `__future__`, `datetime`, `jarvis_v2.backend.scheduler`, `pathlib`, `sqlite3`, `typing` |
| `jarvis_v2.backend.authorization` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `jarvis_v2.core.registry`, `json`, `re`, `time`, `types`, `typing`, `uuid` |
| `jarvis_v2.backend.backup` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `json`, `os`, `pathlib`, `sqlite3`, `tempfile`, `typing`, `urllib.parse` |
| `jarvis_v2.backend.cloudflare_jobs` | `.windows_agent`, `__future__`, `collections.abc`, `dataclasses`, `json`, `re`, `urllib.error`, `urllib.parse`, `urllib.request` |
| `jarvis_v2.backend.code_index` | `__future__`, `ast`, `collections.abc`, `datetime`, `hashlib`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.backend.connectors` | `__future__`, `collections.abc`, `dataclasses`, `re`, `time`, `types`, `uuid` |
| `jarvis_v2.backend.context` | `__future__`, `collections.abc`, `hashlib`, `json`, `re`, `typing` |
| `jarvis_v2.backend.conversation` | `__future__`, `collections.abc`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `typing`, `uuid` |
| `jarvis_v2.backend.effects` | `__future__`, `collections.abc`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.backend.event_bus` | `.storage`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `typing`, `uuid` |
| `jarvis_v2.backend.generation_scheduler` | `__future__`, `collections.abc`, `dataclasses`, `jarvis_v2.core.budget` |
| `jarvis_v2.backend.handoff` | `__future__`, `collections.abc`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.backend.linux_service` | `__future__`, `collections.abc`, `dataclasses`, `pathlib`, `re`, `shlex` |
| `jarvis_v2.backend.module_manifest` | `__future__`, `dataclasses`, `types`, `typing` |
| `jarvis_v2.backend.ollama_profile` | `__future__`, `collections.abc`, `dataclasses`, `math`, `re`, `typing` |
| `jarvis_v2.backend.protocol_adapters` | `__future__`, `collections.abc`, `dataclasses`, `json`, `re`, `typing` |
| `jarvis_v2.backend.provider_registry` | `.event_bus`, `__future__`, `collections.abc`, `dataclasses`, `re`, `types` |
| `jarvis_v2.backend.reranking` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `math`, `queue`, `re`, `threading`, `time`, `typing` |
| `jarvis_v2.backend.retrieval` | `__future__`, `collections.abc`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.backend.routing` | `.provider_registry`, `__future__`, `collections.abc`, `dataclasses`, `enum`, `re`, `time` |
| `jarvis_v2.backend.scheduler` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `pathlib`, `re`, `sqlite3`, `typing`, `zoneinfo` |
| `jarvis_v2.backend.secrets` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `os`, `re`, `types` |
| `jarvis_v2.backend.storage` | `.module_manifest`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.backend.task_capability` | `.windows_agent`, `__future__`, `collections.abc`, `dataclasses`, `pathlib`, `re` |
| `jarvis_v2.backend.windows_agent` | `__future__`, `collections.abc`, `dataclasses`, `re`, `time`, `uuid` |
| `jarvis_v2.cli` | `.guardian.release`, `.health`, `.system_inventory`, `__future__`, `argparse`, `json`, `os`, `pathlib` |
| `jarvis_v2.core.budget` | `__future__`, `collections.abc`, `jarvis_v2.guardian.priority`, `types` |
| `jarvis_v2.core.control` | `__future__`, `datetime`, `pathlib`, `re`, `sqlite3` |
| `jarvis_v2.core.dependency` | `__future__`, `collections.abc`, `json`, `sqlite3` |
| `jarvis_v2.core.dispatch` | `__future__`, `collections.abc`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `uuid` |
| `jarvis_v2.core.event_session` | `__future__`, `datetime`, `hashlib`, `pathlib`, `re`, `sqlite3`, `uuid` |
| `jarvis_v2.core.intent` | `__future__`, `collections.abc`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `uuid` |
| `jarvis_v2.core.model_policy` | `__future__`, `collections.abc`, `dataclasses`, `re` |
| `jarvis_v2.core.queue` | `.control`, `.dependency`, `.dispatch`, `.event_session`, `.intent`, `.session`, `.timeline`, `__future__`, `json`, `pathlib`, `re`, `sqlite3`, `uuid` |
| `jarvis_v2.core.registry` | `__future__`, `dataclasses`, `jarvis_v2.backend.module_manifest`, `json`, `pathlib`, `types`, `typing` |
| `jarvis_v2.core.session` | `__future__`, `collections.abc`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `uuid` |
| `jarvis_v2.core.timeline` | `__future__`, `collections`, `hashlib`, `pathlib`, `re`, `sqlite3` |
| `jarvis_v2.finance.advice` | `.alerts`, `.ingestion`, `__future__`, `dataclasses` |
| `jarvis_v2.finance.alerts` | `.ingestion`, `__future__`, `collections`, `dataclasses`, `hashlib` |
| `jarvis_v2.finance.dashboard` | `.ingestion`, `__future__`, `collections.abc`, `dataclasses`, `datetime` |
| `jarvis_v2.finance.ingestion` | `.advice`, `.alerts`, `.dashboard`, `.planning`, `.reports`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.finance.mira_audit` | `__future__`, `dataclasses`, `hashlib`, `re`, `typing`, `uuid` |
| `jarvis_v2.finance.mira_connector` | `__future__`, `collections.abc`, `dataclasses`, `jarvis_v2.backend.connectors`, `types`, `typing` |
| `jarvis_v2.finance.paper` | `.ingestion`, `__future__`, `dataclasses`, `datetime`, `pathlib`, `sqlite3` |
| `jarvis_v2.finance.performance` | `.ingestion`, `__future__`, `collections.abc`, `dataclasses`, `datetime` |
| `jarvis_v2.finance.planning` | `.ingestion`, `.reports`, `__future__`, `collections.abc`, `dataclasses` |
| `jarvis_v2.finance.reconciliation` | `.ingestion`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `json`, `pathlib`, `sqlite3` |
| `jarvis_v2.finance.reports` | `.ingestion`, `__future__`, `collections.abc`, `dataclasses`, `datetime` |
| `jarvis_v2.guardian.controller` | `__future__`, `argparse`, `collections.abc`, `hashlib`, `pathlib`, `re`, `stat`, `subprocess`, `typing` |
| `jarvis_v2.guardian.cutover` | `.fencing`, `__future__`, `collections.abc`, `dataclasses`, `pathlib`, `re`, `typing` |
| `jarvis_v2.guardian.failure` | `.health`, `__future__`, `collections.abc`, `dataclasses`, `re`, `typing` |
| `jarvis_v2.guardian.fencing` | `__future__`, `dataclasses`, `re`, `threading`, `time`, `typing`, `uuid` |
| `jarvis_v2.guardian.health` | `__future__`, `collections.abc`, `dataclasses`, `re`, `typing` |
| `jarvis_v2.guardian.incidents` | `.failure`, `__future__`, `dataclasses`, `hashlib`, `json`, `re`, `typing` |
| `jarvis_v2.guardian.integrity` | `__future__`, `collections.abc`, `dataclasses`, `re`, `typing` |
| `jarvis_v2.guardian.isolation` | `__future__`, `collections.abc`, `dataclasses`, `re`, `typing` |
| `jarvis_v2.guardian.model` | `__future__`, `collections.abc`, `dataclasses`, `re`, `subprocess` |
| `jarvis_v2.guardian.priority` | `__future__`, `collections.abc` |
| `jarvis_v2.guardian.recovery` | `.controller`, `.restart`, `__future__`, `pathlib`, `typing` |
| `jarvis_v2.guardian.release` | `__future__`, `hashlib`, `json`, `pathlib`, `re` |
| `jarvis_v2.guardian.restart` | `__future__`, `collections.abc`, `dataclasses`, `re`, `time`, `typing` |
| `jarvis_v2.guardian.rollback` | `.release`, `__future__`, `dataclasses`, `hashlib`, `json`, `os`, `pathlib`, `re`, `shutil`, `stat`, `tempfile`, `typing` |
| `jarvis_v2.guardian.standby` | `.controller`, `__future__`, `hashlib`, `pathlib`, `re`, `typing` |
| `jarvis_v2.health` | `__future__`, `collections`, `json`, `pathlib`, `sqlite3`, `subprocess`, `typing` |
| `jarvis_v2.monitor` | `.monitor_supervision`, `__future__`, `argparse`, `collections`, `contextlib`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `sys`, `time`, `typing` |
| `jarvis_v2.monitor_supervision` | `__future__`, `re`, `sqlite3`, `typing` |
| `jarvis_v2.native_controller` | `.automation.queue_api`, `__future__`, `argparse`, `collections`, `collections.abc`, `fcntl`, `hashlib`, `json`, `os`, `pathlib`, `stat`, `threading`, `time`, `typing` |
| `jarvis_v2.research.analysis` | `.youtube`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3` |
| `jarvis_v2.research.comparison` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `re` |
| `jarvis_v2.research.github` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `re`, `urllib.parse` |
| `jarvis_v2.research.handbook` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `re` |
| `jarvis_v2.research.instagram` | `.youtube`, `__future__`, `collections.abc`, `dataclasses`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `urllib.parse` |
| `jarvis_v2.research.media_rag` | `.youtube`, `__future__`, `collections`, `collections.abc`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3` |
| `jarvis_v2.research.subscriptions` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `pathlib`, `re`, `sqlite3`, `time`, `typing` |
| `jarvis_v2.research.web` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `re`, `urllib.parse` |
| `jarvis_v2.research.youtube` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `json`, `pathlib`, `re`, `sqlite3`, `urllib.parse` |
| `jarvis_v2.runtime.browser` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `sqlite3`, `time`, `typing` |
| `jarvis_v2.runtime.calendar` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `itertools`, `re`, `typing`, `zoneinfo` |
| `jarvis_v2.runtime.chat` | `__future__`, `asyncio`, `collections.abc`, `inspect`, `jarvis_v2.backend.conversation`, `re`, `typing`, `uuid` |
| `jarvis_v2.runtime.dashboard` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `itertools`, `re` |
| `jarvis_v2.runtime.email` | `__future__`, `collections.abc`, `dataclasses`, `hashlib`, `itertools`, `jarvis_v2.backend`, `json`, `re`, `typing` |
| `jarvis_v2.runtime.file_actions` | `__future__`, `ctypes`, `dataclasses`, `datetime`, `hashlib`, `os`, `pathlib`, `re`, `secrets`, `sqlite3`, `stat`, `sys`, `time`, `typing` |
| `jarvis_v2.runtime.offline` | `.chat`, `__future__`, `collections.abc`, `jarvis_v2.core`, `re`, `typing` |
| `jarvis_v2.runtime.qualification` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `re` |
| `jarvis_v2.runtime.reminders` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `jarvis_v2.backend`, `pathlib`, `sqlite3`, `typing`, `zoneinfo` |
| `jarvis_v2.runtime.security` | `__future__`, `collections.abc`, `dataclasses`, `re`, `secrets`, `time`, `types`, `urllib.parse` |
| `jarvis_v2.runtime.service` | `.security`, `__future__`, `collections.abc`, `dataclasses`, `jarvis_v2.backend.authorization`, `jarvis_v2.backend.event_bus`, `jarvis_v2.core.dispatch`, `jarvis_v2.core.registry`, `re`, `typing` |
| `jarvis_v2.runtime.speech` | `__future__`, `asyncio`, `collections.abc`, `inspect`, `jarvis_v2.backend.conversation`, `re`, `typing` |
| `jarvis_v2.sda.handoff` | `__future__`, `dataclasses` |
| `jarvis_v2.system_inventory` | `__future__`, `collections.abc`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `shutil`, `stat`, `subprocess`, `typing` |
| `jarvis_v2.tws.__init__` | `..backend.event_bus`, `..backend.module_manifest`, `..backend.storage`, `.aurelia_model`, `__future__`, `collections.abc`, `datetime`, `hashlib`, `json`, `pathlib`, `re`, `typing` |
| `jarvis_v2.tws.aurelia_model` | `__future__`, `collections.abc`, `hashlib`, `json`, `math`, `re`, `struct`, `typing` |
| `jarvis_v2.wic.__init__` | `__future__`, `collections.abc`, `dataclasses`, `datetime`, `hashlib`, `jarvis_v2.research.web`, `json`, `pathlib`, `re`, `sqlite3`, `urllib.parse`, `zoneinfo` |
| `scripts.verify_manifest` | `__future__`, `hashlib`, `json`, `os`, `pathlib` |
| `scripts.verify_package` | `__future__`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`, `verify_manifest` |
| `test_acceptance_evidence` | `jarvis_v2.backend.module_manifest`, `jarvis_v2.core.queue`, `json`, `pathlib`, `tempfile`, `tools.ci_report`, `unittest`, `unittest.mock` |
| `test_aegis_slots` | `jarvis_v2.guardian.priority`, `random`, `unittest` |
| `test_astra_watchdog` | `importlib.util`, `pathlib`, `sqlite3`, `subprocess`, `tempfile`, `unittest` |
| `test_atlas_core_events` | `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_automation_devices` | `hashlib`, `jarvis_v2.automation.device_registry`, `jarvis_v2.backend`, `unittest` |
| `test_automation_dispatcher` | `jarvis_v2.automation.dispatcher`, `jarvis_v2.automation.queue_api`, `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_automation_leases` | `jarvis_v2.automation.queue_api`, `pathlib`, `tempfile`, `unittest` |
| `test_automation_queue_api` | `jarvis_v2.automation.queue_api`, `pathlib`, `tempfile`, `unittest` |
| `test_automation_recovery_drill` | `jarvis_v2.automation.recovery_drill`, `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_automation_scheduler` | `datetime`, `jarvis_v2.automation.scheduler`, `pathlib`, `tempfile`, `unittest`, `zoneinfo` |
| `test_backend_acceptance` | `jarvis_v2.backend`, `jarvis_v2.backend.backup`, `jarvis_v2.backend.storage`, `jarvis_v2.core`, `json`, `os`, `pathlib`, `subprocess`, `tempfile`, `tools.import_legacy`, `unittest` |
| `test_backend_authorization` | `jarvis_v2.backend`, `jarvis_v2.core`, `pathlib`, `time`, `unittest` |
| `test_backend_backup` | `jarvis_v2.backend.backup`, `os`, `pathlib`, `sqlite3`, `tempfile`, `unittest` |
| `test_backend_cloudflare_jobs` | `jarvis_v2.backend`, `jarvis_v2.backend.windows_agent`, `json`, `unittest`, `urllib.parse` |
| `test_backend_code_index` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_connectors` | `jarvis_v2.backend`, `unittest` |
| `test_backend_context` | `jarvis_v2.backend`, `unittest` |
| `test_backend_conversation` | `jarvis_v2.backend.conversation`, `os`, `pathlib`, `subprocess`, `sys`, `tempfile`, `unittest` |
| `test_backend_effects` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_event_bus` | `jarvis_v2.backend.event_bus`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_generation_scheduler` | `jarvis_v2.backend`, `unittest` |
| `test_backend_handoff` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_linux_service` | `jarvis_v2.backend`, `unittest` |
| `test_backend_manifest` | `jarvis_v2.backend.module_manifest`, `unittest` |
| `test_backend_ollama_profile` | `jarvis_v2.backend`, `unittest` |
| `test_backend_protocol_adapters` | `jarvis_v2.backend`, `unittest` |
| `test_backend_provider_registry` | `jarvis_v2.backend`, `unittest` |
| `test_backend_reranking` | `jarvis_v2.backend`, `time`, `unittest` |
| `test_backend_retrieval` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_routing` | `jarvis_v2.backend`, `unittest` |
| `test_backend_scheduler` | `datetime`, `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest`, `zoneinfo` |
| `test_backend_secrets` | `jarvis_v2.backend`, `json`, `unittest` |
| `test_backend_storage` | `jarvis_v2.backend.storage`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_task_capability` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_backend_windows_agent` | `jarvis_v2.backend`, `typing`, `unittest` |
| `test_batch_cycle` | `os`, `pathlib`, `shutil`, `stat`, `subprocess`, `tempfile`, `unittest` |
| `test_ci_workflow` | `json`, `pathlib`, `subprocess`, `sys`, `tempfile`, `tools.ci_checks`, `tools.ci_report`, `unittest` |
| `test_core` | `astra_one.core`, `astra_one.planner`, `astra_one.runner`, `hashlib`, `json`, `pathlib`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `unittest`, `uuid` |
| `test_core_budget` | `jarvis_v2.core`, `unittest` |
| `test_core_controls` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_dependencies` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_dispatch` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_event_guard` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_event_sessions` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_fault_injection` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_intents` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_model_policy` | `jarvis_v2.core`, `unittest` |
| `test_core_priority` | `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_queue_replay` | `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_registry` | `jarvis_v2.core`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_core_sessions` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_core_timeline` | `jarvis_v2.core`, `jarvis_v2.core.queue`, `pathlib`, `tempfile`, `unittest` |
| `test_event_readiness` | `astra_one.linux_sda`, `pathlib`, `sqlite3`, `tempfile`, `threading`, `time`, `unittest` |
| `test_evidence_cache` | `astra_one.test_evidence_cache`, `pathlib`, `tempfile`, `unittest`, `unittest.mock` |
| `test_finance_acceptance` | `datetime`, `jarvis_v2.backend`, `jarvis_v2.finance`, `jarvis_v2.finance.mira_connector`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_advice` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_alerts` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_dashboard` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_ingestion` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_mira_audit` | `jarvis_v2.finance.mira_audit`, `unittest` |
| `test_finance_mira_connector` | `jarvis_v2.finance.mira_connector`, `unittest` |
| `test_finance_paper` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_performance` | `datetime`, `jarvis_v2.finance`, `unittest` |
| `test_finance_planning` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_reconciliation` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_finance_reports` | `datetime`, `jarvis_v2.finance`, `pathlib`, `tempfile`, `unittest` |
| `test_foundation` | `jarvis_v2.core.queue`, `jarvis_v2.guardian.priority`, `jarvis_v2.guardian.release`, `jarvis_v2.sda.handoff`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_full_plan` | `astra_one.full_plan`, `astra_one.linux_runtime`, `astra_one.linux_sda`, `hashlib`, `json`, `pathlib`, `subprocess`, `tempfile`, `unittest` |
| `test_git_policy` | `tools.check_git_policy`, `unittest` |
| `test_guardian_controller` | `hashlib`, `jarvis_v2.guardian`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_cutover` | `hashlib`, `jarvis_v2.guardian.cutover`, `jarvis_v2.guardian.fencing`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_failure` | `jarvis_v2.guardian`, `unittest` |
| `test_guardian_fault_injection` | `hashlib`, `jarvis_v2.guardian.controller`, `jarvis_v2.guardian.cutover`, `jarvis_v2.guardian.fencing`, `jarvis_v2.guardian.recovery`, `jarvis_v2.guardian.release`, `jarvis_v2.guardian.restart`, `jarvis_v2.guardian.rollback`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_fencing` | `jarvis_v2.guardian.fencing`, `unittest` |
| `test_guardian_health` | `jarvis_v2.guardian`, `unittest` |
| `test_guardian_incidents` | `jarvis_v2.guardian`, `unittest` |
| `test_guardian_integrity` | `jarvis_v2.guardian`, `unittest` |
| `test_guardian_isolation` | `jarvis_v2.guardian.isolation`, `unittest` |
| `test_guardian_model` | `jarvis_v2.guardian`, `unittest` |
| `test_guardian_recovery` | `hashlib`, `jarvis_v2.guardian.controller`, `jarvis_v2.guardian.recovery`, `jarvis_v2.guardian.restart`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_release` | `hashlib`, `jarvis_v2.guardian.release`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_restart` | `jarvis_v2.guardian.restart`, `unittest` |
| `test_guardian_rollback` | `hashlib`, `jarvis_v2.guardian.rollback`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_guardian_standby` | `hashlib`, `jarvis_v2.guardian.standby`, `pathlib`, `tempfile`, `unittest` |
| `test_health` | `jarvis_v2.backend.storage`, `jarvis_v2.core.queue`, `jarvis_v2.health`, `json`, `pathlib`, `sqlite3`, `subprocess`, `tempfile`, `unittest`, `unittest.mock` |
| `test_importer` | `json`, `pathlib`, `subprocess`, `tempfile`, `tools.import_legacy`, `unittest` |
| `test_linux_sda` | `astra_one.linux_cli`, `astra_one.linux_runtime`, `astra_one.linux_sda`, `astra_one.supervisor`, `json`, `os`, `pathlib`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `threading`, `time`, `unittest`, `unittest.mock` |
| `test_mig_015_acceptance` | `hashlib`, `jarvis_v2.monitor`, `json`, `pathlib`, `sqlite3`, `tempfile`, `unittest` |
| `test_mig_016_identity` | `hashlib`, `json`, `pathlib`, `sqlite3`, `subprocess`, `tempfile`, `tools.import_legacy`, `unittest` |
| `test_migration_compatibility` | `json`, `migration.adapters.legacy_contracts`, `pathlib`, `shutil`, `tempfile`, `unittest` |
| `test_migration_guardrails` | `json`, `pathlib`, `subprocess`, `tempfile`, `tools.import_legacy`, `unittest` |
| `test_monitor` | `contextlib`, `io`, `jarvis_v2.core.queue`, `jarvis_v2.monitor`, `json`, `pathlib`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `unittest`, `unittest.mock` |
| `test_monitor_supervision` | `jarvis_v2.monitor`, `json`, `pathlib`, `sqlite3`, `tempfile`, `unittest` |
| `test_native_controller` | `jarvis_v2.native_controller`, `pathlib`, `tempfile`, `unittest` |
| `test_owner_approval` | `astra_one.owner_approval`, `json`, `os`, `pathlib`, `subprocess`, `tempfile`, `unittest` |
| `test_owner_approval_state` | `astra_one.linux_sda`, `hashlib`, `json`, `os`, `pathlib`, `sqlite3`, `subprocess`, `sys`, `tempfile`, `unittest` |
| `test_packaging_policy` | `hashlib`, `importlib.util`, `json`, `pathlib`, `sys`, `tempfile`, `unittest`, `unittest.mock` |
| `test_rel003_core_sda_delegation` | `jarvis_v2.backend.authorization`, `jarvis_v2.backend.event_bus`, `jarvis_v2.core.dispatch`, `jarvis_v2.core.registry`, `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_rel004_cross_device` | `jarvis_v2.backend`, `pathlib`, `tempfile`, `unittest` |
| `test_rel006_guardian_priority` | `__future__`, `jarvis_v2.core`, `unittest` |
| `test_rel013_recovery_drills` | `hashlib`, `jarvis_v2.automation.recovery_drill`, `jarvis_v2.backend`, `jarvis_v2.guardian.controller`, `jarvis_v2.guardian.recovery`, `jarvis_v2.guardian.restart`, `jarvis_v2.guardian.rollback`, `json`, `os`, `pathlib`, `sqlite3`, `subprocess`, `tempfile`, `tools.import_legacy`, `unittest` |
| `test_rel017_installation` | `astra_one.linux_runtime`, `infra.verify_installation`, `json`, `pathlib`, `subprocess`, `sys`, `unittest` |
| `test_rel_cross_module_contracts` | `jarvis_v2.backend.authorization`, `jarvis_v2.backend.event_bus`, `jarvis_v2.core.registry`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_rel_fault_isolation` | `jarvis_v2.guardian.isolation`, `json`, `pathlib`, `unittest` |
| `test_research_analysis` | `datetime`, `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_research_comparison` | `jarvis_v2.research`, `unittest` |
| `test_research_github` | `datetime`, `jarvis_v2.research`, `unittest` |
| `test_research_handbook` | `datetime`, `jarvis_v2.research`, `unittest` |
| `test_research_instagram` | `datetime`, `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_research_media_rag` | `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_research_safety` | `datetime`, `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_research_subscriptions` | `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_research_web` | `datetime`, `hashlib`, `jarvis_v2.research`, `unittest` |
| `test_research_youtube` | `datetime`, `jarvis_v2.research`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_browser` | `jarvis_v2.runtime`, `pathlib`, `sqlite3`, `tempfile`, `unittest` |
| `test_runtime_browser_tools` | `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_calendar` | `datetime`, `jarvis_v2.runtime`, `unittest`, `zoneinfo` |
| `test_runtime_chat` | `asyncio`, `jarvis_v2.backend.conversation`, `jarvis_v2.runtime.chat`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_dashboard` | `apps.web.server`, `http.client`, `http.server`, `pathlib`, `threading`, `unittest` |
| `test_runtime_dashboard_service` | `datetime`, `jarvis_v2.runtime`, `unittest` |
| `test_runtime_email` | `jarvis_v2.runtime`, `pathlib`, `sqlite3`, `tempfile`, `unittest` |
| `test_runtime_file_actions` | `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_offline` | `asyncio`, `jarvis_v2.backend.conversation`, `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_qualification` | `datetime`, `jarvis_v2.runtime`, `unittest` |
| `test_runtime_reminders` | `datetime`, `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_security` | `jarvis_v2.backend.authorization`, `jarvis_v2.backend.event_bus`, `jarvis_v2.core.dispatch`, `jarvis_v2.core.registry`, `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_service` | `jarvis_v2.backend.authorization`, `jarvis_v2.backend.event_bus`, `jarvis_v2.core.dispatch`, `jarvis_v2.core.registry`, `jarvis_v2.runtime`, `json`, `pathlib`, `tempfile`, `unittest` |
| `test_runtime_speech` | `asyncio`, `jarvis_v2.backend.conversation`, `jarvis_v2.runtime`, `pathlib`, `tempfile`, `unittest` |
| `test_scaffold` | `pathlib`, `unittest` |
| `test_scope_amendment` | `astra_one.full_plan`, `astra_one.linux_sda`, `json`, `pathlib`, `subprocess`, `tempfile`, `unittest` |
| `test_sda_003_profiles` | `importlib.util`, `json`, `pathlib`, `re`, `sys`, `tempfile`, `unittest`, `unittest.mock` |
| `test_sda_shadow_handoff` | `jarvis_v2.sda.handoff`, `unittest` |
| `test_supervisor_v3` | `astra_one.full_plan`, `astra_one.linux_runtime`, `astra_one.linux_sda`, `astra_one.supervisor`, `hashlib`, `json`, `os`, `pathlib`, `subprocess`, `tempfile`, `unittest` |
| `test_system_inventory` | `jarvis_v2.cli`, `jarvis_v2.system_inventory`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_aurelia_model` | `jarvis_v2.tws`, `unittest` |
| `test_tws_ci_local` | `pathlib`, `unittest` |
| `test_tws_cultivation` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_dialogue` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_lifecycle` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_preferences` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_rewards` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_sanctuary` | `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_storage` | `jarvis_v2.backend.storage`, `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_task_import` | `hashlib`, `jarvis_v2.tws`, `pathlib`, `tempfile`, `unittest` |
| `test_tws_visual_qa` | `jarvis_v2.tws`, `unittest` |
| `test_wic_alerts` | `hashlib`, `jarvis_v2.wic`, `pathlib`, `tempfile`, `unittest` |
| `test_wic_categories` | `datetime`, `jarvis_v2.wic`, `tempfile`, `unittest` |
| `test_wic_clusters` | `datetime`, `jarvis_v2.wic`, `tempfile`, `unittest` |
| `test_wic_sources` | `datetime`, `jarvis_v2.wic`, `tempfile`, `unittest` |
| `test_wic_summaries` | `datetime`, `jarvis_v2.wic`, `tempfile`, `unittest` |
| `test_wic_verification` | `datetime`, `hashlib`, `jarvis_v2.wic`, `tempfile`, `unittest` |
| `test_wic_watchlists` | `jarvis_v2.wic`, `pathlib`, `tempfile`, `unittest` |
| `test_wic_world` | `jarvis_v2.wic`, `unittest` |
| `verify_codex_profiles` | `__future__`, `argparse`, `astra_one.linux_runtime`, `astra_one.linux_sda`, `hashlib`, `json`, `os`, `pathlib`, `re`, `selectors`, `signal`, `subprocess`, `sys`, `tempfile`, `time`, `uuid` |
| `verify_foundation` | `__future__`, `json`, `pathlib` |
| `verify_installation` | `__future__`, `argparse`, `json`, `pathlib`, `re`, `shutil`, `sys`, `typing` |
| `web.server` | `__future__`, `functools`, `http.server`, `jarvis_v2.runtime.security`, `pathlib`, `urllib.parse` |
