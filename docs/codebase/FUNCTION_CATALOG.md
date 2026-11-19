# ARCHON Function Catalog

Generated `2026-11-19T15:38:55.758241+00:00` from base commit `15e5dde9c3b9d95e6631757d0b95710a98991b80`; audited working tree state: `catalog generated from checkout 15e5dde9c3b9d95e6631757d0b95710a98991b80; status snapshot had 8 entries before output generation`.

Static inventory; callers, unresolved references, test links, and dead-code candidates are heuristic and must not be treated as acceptance receipts.

## Coverage

| Metric | Value |
| --- | --- |
| Source files | 345 |
| Indexed files | 549 |
| Functions | 901 |
| Methods | 2424 |
| Classes | 565 |
| Parser errors | 0 |
| Unresolved symbols | 6800 |
| Untested functions/methods | 994 |
| Suspected dead paths | 1733 |

Supported parsing is AST-based for Python and declaration-pattern based for JavaScript, TypeScript, shell, Swift, and SQL. Unsupported constructs are explicitly counted as gaps.

## Symbols

| Qualified name | Kind | Location | Signature | Tests | Status |
| --- | --- | --- | --- | --- | --- |
| `test_scaffold.IOSScaffoldTests` | class | `apps/ios/tests/test_scaffold.py:12-16` | class IOSScaffoldTests(unittest.TestCase) | 1 | test |
| `test_scaffold.IOSScaffoldTests.test_ios_app_boundary_is_tracked` | method | `apps/ios/tests/test_scaffold.py:13-16` | def test_ios_app_boundary_is_tracked(self) | 1 | test |
| `web.dashboard.renderWorldTimeline` | function | `apps/web/dashboard.js:32-32` | function renderWorldTimeline(cards) { | 0 | active |
| `web.server.DashboardHandler` | class | `apps/web/server.py:20-47` | class DashboardHandler(SimpleHTTPRequestHandler) | 0 | active |
| `web.server.DashboardHandler._rewrite_route` | method | `apps/web/server.py:23-31` | def _rewrite_route(self) -> bool | 0 | active |
| `web.server.DashboardHandler.do_GET` | method | `apps/web/server.py:33-35` | def do_GET(self) -> None | 0 | active |
| `web.server.DashboardHandler.do_HEAD` | method | `apps/web/server.py:37-39` | def do_HEAD(self) -> None | 0 | active |
| `web.server.DashboardHandler.end_headers` | method | `apps/web/server.py:41-44` | def end_headers(self) -> None | 0 | active |
| `web.server.DashboardHandler.log_message` | method | `apps/web/server.py:46-47` | def log_message(self, format: str, *_args: object) -> None | 0 | active |
| `web.server.handler_for` | function | `apps/web/server.py:50-51` | def handler_for(directory: Path=WEB_ROOT) | 1 | active |
| `web.server.serve` | function | `apps/web/server.py:54-58` | def serve(host: str='127.0.0.1', port: int=8765) -> None | 0 | active |
| `astra_one.__main__.emit` | function | `bootstrap/astra-one/astra_one/__main__.py:17-18` | def emit(value: object) -> None | 5 | legacy-bootstrap |
| `astra_one.__main__.doctor` | function | `bootstrap/astra-one/astra_one/__main__.py:21-39` | def doctor(store: Store, source: Path \| None) -> dict | 0 | legacy-bootstrap |
| `astra_one.__main__.main` | function | `bootstrap/astra-one/astra_one/__main__.py:42-118` | def main(argv: list[str] \| None=None) -> int | 155 | legacy-bootstrap |
| `astra_one.core.iso` | function | `bootstrap/astra-one/astra_one/core.py:52-53` | def iso() -> str | 0 | legacy-bootstrap |
| `astra_one.core.validate_task` | function | `bootstrap/astra-one/astra_one/core.py:56-74` | def validate_task(value: object) -> dict | 2 | legacy-bootstrap |
| `astra_one.core.git` | function | `bootstrap/astra-one/astra_one/core.py:77-81` | def git(root: Path, *args: str, timeout: int=20) -> str | 19 | legacy-bootstrap |
| `astra_one.core.validate_source` | function | `bootstrap/astra-one/astra_one/core.py:84-95` | def validate_source(root: Path) -> tuple[Path, str] | 2 | legacy-bootstrap |
| `astra_one.core.Store` | class | `bootstrap/astra-one/astra_one/core.py:98-361` | class Store() | 2 | legacy-bootstrap |
| `astra_one.core.Store.__init__` | method | `bootstrap/astra-one/astra_one/core.py:99-101` | def __init__(self, home: Path=DEFAULT_HOME) | 5 | legacy-bootstrap |
| `astra_one.core.Store.db` | method | `bootstrap/astra-one/astra_one/core.py:104-114` | def db(self) | 27 | legacy-bootstrap |
| `astra_one.core.Store.init` | method | `bootstrap/astra-one/astra_one/core.py:116-130` | def init(self, source: Path) -> dict | 14 | legacy-bootstrap |
| `astra_one.core.Store.config` | method | `bootstrap/astra-one/astra_one/core.py:132-135` | def config(self, key: str) -> str | 17 | legacy-bootstrap |
| `astra_one.core.Store.set_config` | method | `bootstrap/astra-one/astra_one/core.py:137-139` | def set_config(self, key: str, value: str) -> None | 0 | legacy-bootstrap |
| `astra_one.core.Store.import_architecture` | method | `bootstrap/astra-one/astra_one/core.py:141-157` | def import_architecture(self, path: Path) -> dict | 6 | legacy-bootstrap |
| `astra_one.core.Store.approve_architecture` | method | `bootstrap/astra-one/astra_one/core.py:159-163` | def approve_architecture(self, sha: str) -> None | 6 | legacy-bootstrap |
| `astra_one.core.Store.add_task` | method | `bootstrap/astra-one/astra_one/core.py:165-176` | def add_task(self, value: object) -> dict | 2 | legacy-bootstrap |
| `astra_one.core.Store.add_plan` | method | `bootstrap/astra-one/astra_one/core.py:178-198` | def add_plan(self, tasks: object) -> dict | 2 | legacy-bootstrap |
| `astra_one.core.Store.tasks` | method | `bootstrap/astra-one/astra_one/core.py:200-203` | def tasks(self) -> list[dict] | 18 | legacy-bootstrap |
| `astra_one.core.Store.claim` | method | `bootstrap/astra-one/astra_one/core.py:205-230` | def claim(self) -> dict \| None | 21 | legacy-bootstrap |
| `astra_one.core.Store.start_run` | method | `bootstrap/astra-one/astra_one/core.py:232-234` | def start_run(self, run_id: str, task_id: str, branch: str, sha: str, worktree: Path, attempt: int) | 2 | legacy-bootstrap |
| `astra_one.core.Store.update_status` | method | `bootstrap/astra-one/astra_one/core.py:236-240` | def update_status(self, task_id: str, run_id: str, stage: str, exit_code: int \| None=None, qc_result: str \| None=None, error_code: str \| None=None, tool_count: int=0) | 2 | legacy-bootstrap |
| `astra_one.core.Store.event` | method | `bootstrap/astra-one/astra_one/core.py:242-244` | def event(self, event: dict) -> None | 24 | legacy-bootstrap |
| `astra_one.core.Store.unsynced` | method | `bootstrap/astra-one/astra_one/core.py:246-248` | def unsynced(self, limit: int=100) -> list[dict] | 2 | legacy-bootstrap |
| `astra_one.core.Store.synced` | method | `bootstrap/astra-one/astra_one/core.py:250-252` | def synced(self, event_id: str) -> None | 3 | legacy-bootstrap |
| `astra_one.core.Store.approve_task` | method | `bootstrap/astra-one/astra_one/core.py:254-262` | def approve_task(self, task_id: str) -> dict | 2 | legacy-bootstrap |
| `astra_one.core.Store.recover` | method | `bootstrap/astra-one/astra_one/core.py:264-271` | def recover(self) -> list[str] | 4 | legacy-bootstrap |
| `astra_one.core.Store.retry` | method | `bootstrap/astra-one/astra_one/core.py:273-278` | def retry(self, task_id: str) -> None | 10 | legacy-bootstrap |
| `astra_one.core.Store.integration_lock` | method | `bootstrap/astra-one/astra_one/core.py:281-293` | def integration_lock(self) | 0 | legacy-bootstrap |
| `astra_one.core.Store.integrate` | method | `bootstrap/astra-one/astra_one/core.py:295-354` | def integrate(self, task_id: str) -> dict | 4 | legacy-bootstrap |
| `astra_one.core.Store.overview` | method | `bootstrap/astra-one/astra_one/core.py:356-361` | def overview(self) -> dict | 4 | legacy-bootstrap |
| `astra_one.full_plan.PlanValidationError` | class | `bootstrap/astra-one/astra_one/full_plan.py:30-31` | class PlanValidationError(ValueError) | 1 | legacy-bootstrap |
| `astra_one.full_plan._json` | function | `bootstrap/astra-one/astra_one/full_plan.py:34-39` | def _json(path: Path) -> tuple[bytes, Any] | 0 | legacy-bootstrap |
| `astra_one.full_plan.git_blob_sha` | function | `bootstrap/astra-one/astra_one/full_plan.py:42-44` | def git_blob_sha(raw: bytes) -> str | 0 | legacy-bootstrap |
| `astra_one.full_plan.payload_sha` | function | `bootstrap/astra-one/astra_one/full_plan.py:47-50` | def payload_sha(value: Any) -> str | 6 | legacy-bootstrap |
| `astra_one.full_plan._require` | function | `bootstrap/astra-one/astra_one/full_plan.py:53-55` | def _require(condition: bool, message: str) -> None | 0 | legacy-bootstrap |
| `astra_one.full_plan.FullPlan` | class | `bootstrap/astra-one/astra_one/full_plan.py:59-66` | class FullPlan() | 2 | legacy-bootstrap |
| `astra_one.full_plan._markdown_text` | function | `bootstrap/astra-one/astra_one/full_plan.py:69-72` | def _markdown_text(value: object) -> str | 0 | legacy-bootstrap |
| `astra_one.full_plan._task_markdown_manifest` | function | `bootstrap/astra-one/astra_one/full_plan.py:75-115` | def _task_markdown_manifest(project: dict[str, Any], parents: list[dict[str, Any]]) -> dict[str, Any] | 0 | legacy-bootstrap |
| `astra_one.full_plan.render_task_markdown` | function | `bootstrap/astra-one/astra_one/full_plan.py:118-189` | def render_task_markdown(project: dict[str, Any], parents: list[dict[str, Any]], *, statuses: dict[str, str] \| None=None, source_path: str='') -> str | 0 | legacy-bootstrap |
| `astra_one.full_plan.parse_task_markdown` | function | `bootstrap/astra-one/astra_one/full_plan.py:192-261` | def parse_task_markdown(text: str) -> dict[str, Any] | 1 | legacy-bootstrap |
| `astra_one.full_plan.validate_task_markdown` | function | `bootstrap/astra-one/astra_one/full_plan.py:264-277` | def validate_task_markdown(text: str, project: dict[str, Any], parents: list[dict[str, Any]]) -> dict[str, Any] | 0 | legacy-bootstrap |
| `astra_one.full_plan.load_full_plan` | function | `bootstrap/astra-one/astra_one/full_plan.py:280-494` | def load_full_plan(parent_path: Path, index_path: Path, module_dir: Path, *, source_ref: str='', source_commit: str='') -> FullPlan | 0 | legacy-bootstrap |
| `astra_one.linux_cli.report` | function | `bootstrap/astra-one/astra_one/linux_cli.py:34-35` | def report(obj: object) | 14 | legacy-bootstrap |
| `astra_one.linux_cli.diagnose` | function | `bootstrap/astra-one/astra_one/linux_cli.py:38-58` | def diagnose(source: Path \| None) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_cli.inspect_repository` | function | `bootstrap/astra-one/astra_one/linux_cli.py:69-100` | def inspect_repository(source: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_cli._bounded_requirement_text` | function | `bootstrap/astra-one/astra_one/linux_cli.py:103-106` | def _bounded_requirement_text(value: object, *, name: str, limit: int) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_cli.parse_requirements` | function | `bootstrap/astra-one/astra_one/linux_cli.py:109-182` | def parse_requirements(task: object) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_cli._task_requirements` | function | `bootstrap/astra-one/astra_one/linux_cli.py:185-198` | def _task_requirements(state: State, task_id: str) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_cli.supervise` | function | `bootstrap/astra-one/astra_one/linux_cli.py:201-256` | def supervise(state: State, *, focus: str, count: int, output: Path, model: str, effort: str, task_id: str='') | 1 | legacy-bootstrap |
| `astra_one.linux_cli._upgrade_audit_brief` | function | `bootstrap/astra-one/astra_one/linux_cli.py:259-282` | def _upgrade_audit_brief(task_id: str) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_cli.run_upgrade_audit` | function | `bootstrap/astra-one/astra_one/linux_cli.py:285-390` | def run_upgrade_audit(state: State, *, task_id: str, model: str, effort: str, timeout: int) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_cli.run_master` | function | `bootstrap/astra-one/astra_one/linux_cli.py:393-559` | def run_master(state: State, *, workers: int, max_tasks: int, max_minutes: int, model: str, effort: str, test_image: str, test_command: list[str], auto_integrate: bool, max_repairs | 2 | legacy-bootstrap |
| `astra_one.linux_cli.run_master.retry_decision` | function | `bootstrap/astra-one/astra_one/linux_cli.py:425-436` | def retry_decision(tid: str, result: dict) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_cli.run_master.maybe_requeue` | function | `bootstrap/astra-one/astra_one/linux_cli.py:438-474` | def maybe_requeue(tid: str, result: dict) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_cli.run_recovery` | function | `bootstrap/astra-one/astra_one/linux_cli.py:562-663` | def run_recovery(state: State, *, limit: int, model: str, effort: str, test_image: str, test_command: list[str], timeout: int, danger_bypass: bool=False, _schema_ready: bool=False) | 1 | legacy-bootstrap |
| `astra_one.linux_cli._single_controller` | function | `bootstrap/astra-one/astra_one/linux_cli.py:666-674` | def _single_controller(function) | 0 | legacy-bootstrap |
| `astra_one.linux_cli._single_controller.guarded` | function | `bootstrap/astra-one/astra_one/linux_cli.py:669-673` | def guarded(state, *args, _controller_locked=False, **kwargs) | 0 | legacy-bootstrap |
| `astra_one.linux_cli.run_concurrent` | function | `bootstrap/astra-one/astra_one/linux_cli.py:681-709` | def run_concurrent(state: State, *, workers: int, max_tasks: int, max_minutes: int, model: str, effort: str, recovery_limit: int, recovery_model: str, recovery_effort: str, test_im | 1 | legacy-bootstrap |
| `astra_one.linux_cli.process_candidate_queue` | function | `bootstrap/astra-one/astra_one/linux_cli.py:712-846` | def process_candidate_queue(state: State, *, limit: int, test_image: str, test_command: list[str], timeout: int, ai_review: bool=False, model: str=MODEL, effort: str=EFFORT) -> dic | 1 | legacy-bootstrap |
| `astra_one.linux_cli.main` | function | `bootstrap/astra-one/astra_one/linux_cli.py:849-1050` | def main(argv: list[str] \| None=None) -> int | 155 | legacy-bootstrap |
| `astra_one.linux_runtime.ChangeValidationError` | class | `bootstrap/astra-one/astra_one/linux_runtime.py:167-175` | class ChangeValidationError(ValueError) | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.ChangeValidationError.__init__` | method | `bootstrap/astra-one/astra_one/linux_runtime.py:170-175` | def __init__(self, code: str, detail: str='') | 5 | legacy-bootstrap |
| `astra_one.linux_runtime.DockerTestError` | class | `bootstrap/astra-one/astra_one/linux_runtime.py:178-190` | class DockerTestError(RuntimeError) | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.DockerTestError.__init__` | method | `bootstrap/astra-one/astra_one/linux_runtime.py:186-190` | def __init__(self, code: str) | 5 | legacy-bootstrap |
| `astra_one.linux_runtime.ReviewFailure` | class | `bootstrap/astra-one/astra_one/linux_runtime.py:193-204` | class ReviewFailure(ValueError) | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.ReviewFailure.__init__` | method | `bootstrap/astra-one/astra_one/linux_runtime.py:196-204` | def __init__(self, failure_code: str) | 5 | legacy-bootstrap |
| `astra_one.linux_runtime.review_finding_codes` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:207-262` | def review_finding_codes(findings: object) -> tuple[str, ...] | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.review_failure_code` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:265-269` | def review_failure_code(prefix: str, findings: object) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.sandbox_status` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:272-290` | def sandbox_status() -> dict[str, str \| bool] | 1 | legacy-bootstrap |
| `astra_one.linux_runtime._task_allows_ci_workflow` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:293-307` | def _task_allows_ci_workflow(task: dict \| None, path: str) -> bool | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._task_allows_audit_report` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:310-324` | def _task_allows_audit_report(task: dict \| None, path: str) -> bool | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._check_ci_workflow_actions` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:327-353` | def _check_ci_workflow_actions(worktree: Path, base_sha: str, path: str, target: Path) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._audit_markdown_paths` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:356-362` | def _audit_markdown_paths(task: dict \| None, paths: list[str] \| set[str]) -> set[str] | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._migration_blob_paths` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:365-374` | def _migration_blob_paths(task: dict \| None, paths: list[str] \| set[str]) -> set[str] | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._check_markdown_hard_breaks` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:377-394` | def _check_markdown_hard_breaks(worktree: Path, paths: set[str]) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._check_diff_whitespace` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:397-438` | def _check_diff_whitespace(worktree: Path, untracked_paths: list[Path], *, allow_markdown_hard_breaks: set[str] \| None=None, allow_whitespace_paths: set[str] \| None=None) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._git_common_dir` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:441-444` | def _git_common_dir(repo: Path) -> Path | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._validate_change_entries` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:447-521` | def _validate_change_entries(worktree: Path, entries: list[str], base_sha: str, *, task: dict \| None=None) -> tuple[list[str], set[str]] | 0 | legacy-bootstrap |
| `astra_one.linux_runtime.check_changes` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:524-552` | def check_changes(worktree: Path, base_sha: str, *, task: dict \| None=None) -> list[str] | 2 | legacy-bootstrap |
| `astra_one.linux_runtime.check_candidate_changes` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:555-597` | def check_candidate_changes(worktree: Path, base_sha: str, candidate_sha: str, *, task: dict \| None=None) -> list[str] | 1 | legacy-bootstrap |
| `astra_one.linux_runtime._check_commit_whitespace` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:600-613` | def _check_commit_whitespace(worktree: Path, base_sha: str, candidate_sha: str, *, allow_markdown_hard_breaks: set[str] \| None=None, allow_whitespace_paths: set[str] \| None=None) | 1 | legacy-bootstrap |
| `astra_one.linux_runtime._reference_relative_path` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:616-626` | def _reference_relative_path(value: object) -> PurePosixPath | 0 | legacy-bootstrap |
| `astra_one.linux_runtime.pack_scoped_source` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:629-702` | def pack_scoped_source(root: Path, allowlisted_roots: object, *, max_files: int=REFERENCE_CONTEXT_MAX_FILES, max_bytes: int=REFERENCE_CONTEXT_MAX_BYTES) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.make_prompt` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:705-791` | def make_prompt(task: dict, sha: str, architecture_sha: str, role: str, previous_error: str='', reference_context: str='') -> str | 2 | legacy-bootstrap |
| `astra_one.linux_runtime.codex_command` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:794-807` | def codex_command(worktree: Path, model: str, effort: str, output_file: Path \| None, sandbox: str, danger_bypass: bool=False) -> list[str] | 2 | legacy-bootstrap |
| `astra_one.linux_runtime._codex_event_metadata` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:810-853` | def _codex_event_metadata(line: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.codex_call` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:856-975` | def codex_call(*, worktree: Path, prompt: str, home: Path, state: State, model: str, effort: str, sandbox: str, timeout: int, output_file: Path \| None=None, role: str='worker', da | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.codex_call.record_event` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:875-889` | def record_event(line: str) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_runtime.codex_call.reader` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:891-919` | def reader(stream, tag) | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._docker_context` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:978-1011` | def _docker_context(worktree: Path) -> tuple[tempfile.TemporaryDirectory, Path] | 0 | legacy-bootstrap |
| `astra_one.linux_runtime._write_receipt_artifact` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1014-1029` | def _write_receipt_artifact(directory: Path, *, kind: str, context: dict, payload: dict, extra: dict \| None=None) -> tuple[str, str] | 2 | legacy-bootstrap |
| `astra_one.linux_runtime._complete_test_receipt` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1032-1043` | def _complete_test_receipt(receipt: dict, *, receipt_dir: Path \| None, receipt_context: dict \| None) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.bind_execution_receipts` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1046-1090` | def bind_execution_receipts(state: State, *, task_id: str, run_id: str, attempt: int, source_sha: str, candidate_sha: str, changed_files: list[str], test_receipt: dict, qc_receipt: | 0 | legacy-bootstrap |
| `astra_one.linux_runtime.docker_test` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1093-1155` | def docker_test(worktree: Path, image: str, command: list[str], timeout: int=300, *, receipt_dir: Path \| None=None, receipt_context: dict \| None=None) -> dict | 2 | legacy-bootstrap |
| `astra_one.linux_runtime.shutil_which` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1157-1159` | def shutil_which(name: str) -> str \| None | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.independent_qc_report` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1162-1270` | def independent_qc_report(state: State, worktree: Path, task: dict, *, model: str, effort: str, changed_files: list[str] \| None=None, child_ids: list[str] \| None=None, timeout: i | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.independent_qc` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1273-1281` | def independent_qc(state: State, worktree: Path, task: dict, *, model: str, effort: str, changed_files: list[str] \| None=None, timeout: int=600, danger_bypass: bool=False) -> tupl | 7 | legacy-bootstrap |
| `astra_one.linux_runtime._bounded_patch_preview` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1285-1292` | def _bounded_patch_preview(patch: bytes, limit: int=10000) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.merger_review_result` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1295-1384` | def merger_review_result(state: State, integration: Path, tid: str, patch: bytes, *, model: str, effort: str, task: dict \| None=None, danger_bypass: bool=False) -> tuple[bool, str | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.merger_review` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1387-1391` | def merger_review(state: State, integration: Path, tid: str, patch: bytes, *, model: str, effort: str, danger_bypass: bool=False) -> bool | 0 | legacy-bootstrap |
| `astra_one.linux_runtime.worker_failure_code` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1435-1464` | def worker_failure_code(error: BaseException) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_runtime.ensure_integration` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1467-1494` | def ensure_integration(state: State) -> Path | 2 | legacy-bootstrap |
| `astra_one.linux_runtime.integrate` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1497-1583` | def integrate(state: State, tid: str, *, merger_model: str \| None=None, merger_effort: str='medium', danger_bypass: bool=False, lane: str='normal') -> dict | 4 | legacy-bootstrap |
| `astra_one.linux_runtime.execute_claim` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1586-1729` | def execute_claim(state: State, item: dict, *, slot: int, model: str, effort: str, timeout: int, test_image: str, test_command: list[str], auto_integrate: bool=False, danger_bypass | 2 | legacy-bootstrap |
| `astra_one.linux_runtime.execute_claim.emit` | function | `bootstrap/astra-one/astra_one/linux_runtime.py:1612-1614` | def emit(stage: str, step: str, result: str='') | 5 | legacy-bootstrap |
| `astra_one.linux_sda._full_plan_ddl` | function | `bootstrap/astra-one/astra_one/linux_sda.py:359-362` | def _full_plan_ddl() -> tuple[str, ...] | 0 | legacy-bootstrap |
| `astra_one.linux_sda._ensure_v3_columns` | function | `bootstrap/astra-one/astra_one/linux_sda.py:365-387` | def _ensure_v3_columns(db: sqlite3.Connection) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_sda._ensure_codex_receipt_columns` | function | `bootstrap/astra-one/astra_one/linux_sda.py:389-401` | def _ensure_codex_receipt_columns(db: sqlite3.Connection) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_sda.now` | function | `bootstrap/astra-one/astra_one/linux_sda.py:403-404` | def now() -> str | 19 | legacy-bootstrap |
| `astra_one.linux_sda.file_sha256` | function | `bootstrap/astra-one/astra_one/linux_sda.py:406-411` | def file_sha256(path: Path) -> str | 3 | legacy-bootstrap |
| `astra_one.linux_sda._canonical_json` | function | `bootstrap/astra-one/astra_one/linux_sda.py:413-414` | def _canonical_json(value: object) -> bytes | 0 | legacy-bootstrap |
| `astra_one.linux_sda._amendment_payload_sha` | function | `bootstrap/astra-one/astra_one/linux_sda.py:417-421` | def _amendment_payload_sha(value: dict) -> str | 2 | legacy-bootstrap |
| `astra_one.linux_sda._checkpoint_value` | function | `bootstrap/astra-one/astra_one/linux_sda.py:424-430` | def _checkpoint_value(value: object) -> object | 0 | legacy-bootstrap |
| `astra_one.linux_sda._database_state_digest` | function | `bootstrap/astra-one/astra_one/linux_sda.py:433-444` | def _database_state_digest(db: sqlite3.Connection) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_sda.git` | function | `bootstrap/astra-one/astra_one/linux_sda.py:446-451` | def git(repo: Path, *args: str, timeout: int=90) -> str | 19 | legacy-bootstrap |
| `astra_one.linux_sda.assert_source` | function | `bootstrap/astra-one/astra_one/linux_sda.py:453-464` | def assert_source(source: Path) -> tuple[Path, str] | 2 | legacy-bootstrap |
| `astra_one.linux_sda.task_spec` | function | `bootstrap/astra-one/astra_one/linux_sda.py:466-493` | def task_spec(obj: object) -> dict | 2 | legacy-bootstrap |
| `astra_one.linux_sda.validate_task_type` | function | `bootstrap/astra-one/astra_one/linux_sda.py:496-541` | def validate_task_type(task: object) -> str | 1 | legacy-bootstrap |
| `astra_one.linux_sda.control_blocked` | function | `bootstrap/astra-one/astra_one/linux_sda.py:544-550` | def control_blocked(home: Path, lane: str) -> bool | 1 | legacy-bootstrap |
| `astra_one.linux_sda.builder_branch` | function | `bootstrap/astra-one/astra_one/linux_sda.py:553-561` | def builder_branch(task: dict, attempt: int, run_id: str) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_sda._bounded_evidence` | function | `bootstrap/astra-one/astra_one/linux_sda.py:564-589` | def _bounded_evidence(value: object, name: str) -> str | 0 | legacy-bootstrap |
| `astra_one.linux_sda._bounded_evidence.inspect` | function | `bootstrap/astra-one/astra_one/linux_sda.py:572-587` | def inspect(item: object) -> None | 10 | legacy-bootstrap |
| `astra_one.linux_sda._validate_builder_child_evidence` | function | `bootstrap/astra-one/astra_one/linux_sda.py:592-601` | def _validate_builder_child_evidence(child_ids: list[str], value: object) -> None | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State` | class | `bootstrap/astra-one/astra_one/linux_sda.py:603-3249` | class State() | 7 | legacy-bootstrap |
| `astra_one.linux_sda.State.__init__` | method | `bootstrap/astra-one/astra_one/linux_sda.py:604-607` | def __init__(self, home: Path=DEFAULT_HOME) | 5 | legacy-bootstrap |
| `astra_one.linux_sda.State.db` | method | `bootstrap/astra-one/astra_one/linux_sda.py:610-620` | def db(self) | 27 | legacy-bootstrap |
| `astra_one.linux_sda.State.data_version` | method | `bootstrap/astra-one/astra_one/linux_sda.py:622-625` | def data_version(self) -> int | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.wait_for_data_change` | method | `bootstrap/astra-one/astra_one/linux_sda.py:627-644` | def wait_for_data_change(self, observed: int, timeout: float=1.0) -> tuple[bool, int] | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.master_lock` | method | `bootstrap/astra-one/astra_one/linux_sda.py:647-665` | def master_lock(self, blocking: bool=False, timeout: float=30.0) | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.controller_lock` | method | `bootstrap/astra-one/astra_one/linux_sda.py:668-703` | def controller_lock(self, blocking: bool=False, timeout: float=30.0) | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.ensure_full_plan_schema` | method | `bootstrap/astra-one/astra_one/linux_sda.py:705-760` | def ensure_full_plan_schema(self) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.init` | method | `bootstrap/astra-one/astra_one/linux_sda.py:762-795` | def init(self, source: Path) -> dict | 14 | legacy-bootstrap |
| `astra_one.linux_sda.State.get` | method | `bootstrap/astra-one/astra_one/linux_sda.py:797-800` | def get(self, key: str) -> str | 27 | legacy-bootstrap |
| `astra_one.linux_sda.State.put` | method | `bootstrap/astra-one/astra_one/linux_sda.py:802-804` | def put(self, key: str, value: str) | 3 | legacy-bootstrap |
| `astra_one.linux_sda.State._checkpoint_snapshot` | method | `bootstrap/astra-one/astra_one/linux_sda.py:806-843` | def _checkpoint_snapshot(self, db: sqlite3.Connection) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.export_checkpoint` | method | `bootstrap/astra-one/astra_one/linux_sda.py:845-908` | def export_checkpoint(self, destination: Path \| None=None) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State._read_checkpoint` | method | `bootstrap/astra-one/astra_one/linux_sda.py:910-947` | def _read_checkpoint(self, checkpoint: Path) -> tuple[Path, dict] | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.restore_checkpoint` | method | `bootstrap/astra-one/astra_one/linux_sda.py:949-987` | def restore_checkpoint(self, checkpoint: Path, destination: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.import_architecture` | method | `bootstrap/astra-one/astra_one/linux_sda.py:989-1003` | def import_architecture(self, file: Path) -> str | 6 | legacy-bootstrap |
| `astra_one.linux_sda.State.approve_architecture` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1005-1009` | def approve_architecture(self, digest: str) | 6 | legacy-bootstrap |
| `astra_one.linux_sda.State.ensure_approved` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1011-1013` | def ensure_approved(self) | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.add_tasks` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1015-1036` | def add_tasks(self, values: object) -> list[str] | 3 | legacy-bootstrap |
| `astra_one.linux_sda.State._refresh_project_queues_db` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1039-1094` | def _refresh_project_queues_db(db: sqlite3.Connection, project_id: str) -> None | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.import_full_plan` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1096-1194` | def import_full_plan(self, plan: FullPlan) -> dict | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State._owner_binding` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1196-1270` | def _owner_binding(self, row: sqlite3.Row, db: sqlite3.Connection) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.owner_approval_request` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1272-1305` | def owner_approval_request(self, tid: str, owner_identity: str, *, allowed_signers: Path \| None=None, output: Path \| None=None) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State._record_base008_owner_children` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1307-1343` | def _record_base008_owner_children(self, db: sqlite3.Connection, row: sqlite3.Row, receipt_sha: str, verified: dict, timestamp: str) -> list[str] | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.approve_owner` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1345-1424` | def approve_owner(self, tid: str, *, owner_receipt: Path \| None=None) -> dict | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State.full_plan_status` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1426-1481` | def full_plan_status(self) -> dict | 3 | legacy-bootstrap |
| `astra_one.linux_sda.State._plan_graph_bindings` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1483-1504` | def _plan_graph_bindings(self, db: sqlite3.Connection) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State._plan_file` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1506-1514` | def _plan_file(self) -> Path | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State._validate_plan_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1516-1615` | def _validate_plan_amendment(self, path: Path) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.validate_plan_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1617-1622` | def validate_plan_amendment(self, path: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.record_plan_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1624-1770` | def record_plan_amendment(self, path: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State._validate_tws_scope_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1772-1923` | def _validate_tws_scope_amendment(self, path: Path) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.validate_tws_scope_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1925-1938` | def validate_tws_scope_amendment(self, path: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.record_tws_scope_amendment` | method | `bootstrap/astra-one/astra_one/linux_sda.py:1940-2044` | def record_tws_scope_amendment(self, path: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State._task_markdown_records` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2046-2079` | def _task_markdown_records(self, db: sqlite3.Connection) -> tuple[dict, list[dict], dict[str, str]] | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.export_task_markdown` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2081-2103` | def export_task_markdown(self, output: Path \| None=None) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.validate_task_markdown_file` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2105-2122` | def validate_task_markdown_file(self, source: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.list_tasks` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2124-2129` | def list_tasks(self) -> list[dict] | 3 | legacy-bootstrap |
| `astra_one.linux_sda.State.claim` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2131-2238` | def claim(self, model: str=MODEL, *, batch_id: str \| None=None, lane: str='normal') -> dict \| None | 21 | legacy-bootstrap |
| `astra_one.linux_sda.State.builder_claim` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2240-2271` | def builder_claim(self, *, model: str=MODEL, batch_id: str \| None=None) -> dict \| None | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.submit_candidate` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2273-2392` | def submit_candidate(self, *, task_id: str, run_id: str, attempt: int, builder_session_id: str, base_sha: str, candidate_sha: str, branch: str, worktree: str, changed_files: list[s | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.update_candidate_submission` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2394-2415` | def update_candidate_submission(self, submission_id: str, status: str, *, failure_code: str='') -> None | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.claim_recovery_task` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2417-2478` | def claim_recovery_task(self, lease: dict, *, model: str=MODEL) -> dict | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.set_task` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2480-2609` | def set_task(self, tid: str, status: str, *, error: str='', fields: dict \| None=None, run_id: str \| None=None, attempt: int \| None=None) | 4 | legacy-bootstrap |
| `astra_one.linux_sda.State.record_codex_receipt` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2611-2655` | def record_codex_receipt(self, run_id: str, *, thread_id: str='', input_tokens: int=0, output_tokens: int=0, tool_count: int=0, tool_effects: list[dict] \| None=None, error_categor | 1 | legacy-bootstrap |
| `astra_one.linux_sda.State.failure_codes` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2657-2671` | def failure_codes(self, tid: str) -> list[str] | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State.subtask_contract_sha` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2673-2684` | def subtask_contract_sha(self, tid: str) -> str | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State._read_receipt_artifact` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2686-2732` | def _read_receipt_artifact(self, receipt: dict, *, kind: str, task_id: str, run_id: str, attempt: int, source_sha: str, payload: dict \| None=None, candidate_sha: str \| None=None) | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.validate_execution_artifacts` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2734-2787` | def validate_execution_artifacts(self, tid: str, *, source_sha: str, candidate_sha: str, changed_files: list[str], test_receipt: dict, qc_receipt: dict, run_id: str, attempt: int)  | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.subtask_evidence_ready` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2789-2810` | def subtask_evidence_ready(self, tid: str, candidate_sha: str) -> bool | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.record_subtask_evidence` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2812-2976` | def record_subtask_evidence(self, tid: str, *, candidate_sha: str, source_sha: str, changed_files: list[str], test_receipt: dict, qc_receipt: dict, child_evidence: list[dict], lock | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State.emit` | method | `bootstrap/astra-one/astra_one/linux_sda.py:2978-3003` | def emit(self, tid: str, run_id: str, *, stage: str, step: str, branch: str, base_sha: str, tools: int=0, attempt: int=1, elapsed: int=0, result: str='') | 5 | legacy-bootstrap |
| `astra_one.linux_sda.State.sync` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3005-3027` | def sync(self, limit: int=50) -> dict | 13 | legacy-bootstrap |
| `astra_one.linux_sda.State.recover` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3029-3036` | def recover(self) -> list[str] | 4 | legacy-bootstrap |
| `astra_one.linux_sda.State._write_breakdown_report` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3038-3117` | def _write_breakdown_report(self, db: sqlite3.Connection, tid: str, reason: str) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State._write_breakdown_report.verify_existing` | function | `bootstrap/astra-one/astra_one/linux_sda.py:3052-3063` | def verify_existing(path: Path) -> dict | 0 | legacy-bootstrap |
| `astra_one.linux_sda.State.retry` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3119-3151` | def retry(self, tid: str) | 10 | legacy-bootstrap |
| `astra_one.linux_sda.State.reopen_failed` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3153-3213` | def reopen_failed(self, task_ids: list[str]) -> list[str] | 2 | legacy-bootstrap |
| `astra_one.linux_sda.State.approve` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3215-3236` | def approve(self, tid: str, *, run_id: str \| None=None, attempt: int \| None=None) | 6 | legacy-bootstrap |
| `astra_one.linux_sda.State.overview` | method | `bootstrap/astra-one/astra_one/linux_sda.py:3238-3249` | def overview(self) -> dict | 4 | legacy-bootstrap |
| `astra_one.owner_approval.OwnerApprovalError` | class | `bootstrap/astra-one/astra_one/owner_approval.py:31-32` | class OwnerApprovalError(ValueError) | 1 | legacy-bootstrap |
| `astra_one.owner_approval._canonical` | function | `bootstrap/astra-one/astra_one/owner_approval.py:35-37` | def _canonical(value: object) -> bytes | 0 | legacy-bootstrap |
| `astra_one.owner_approval._sha256` | function | `bootstrap/astra-one/astra_one/owner_approval.py:40-45` | def _sha256(path: Path) -> str | 0 | legacy-bootstrap |
| `astra_one.owner_approval._secure_file` | function | `bootstrap/astra-one/astra_one/owner_approval.py:48-58` | def _secure_file(path: Path, *, label: str) -> None | 0 | legacy-bootstrap |
| `astra_one.owner_approval._secure_directory` | function | `bootstrap/astra-one/astra_one/owner_approval.py:61-69` | def _secure_directory(path: Path, *, label: str) -> None | 0 | legacy-bootstrap |
| `astra_one.owner_approval._secure_directory_chain` | function | `bootstrap/astra-one/astra_one/owner_approval.py:72-86` | def _secure_directory_chain(path: Path, *, root: Path \| None=None) -> None | 0 | legacy-bootstrap |
| `astra_one.owner_approval._ensure_private_directory` | function | `bootstrap/astra-one/astra_one/owner_approval.py:89-98` | def _ensure_private_directory(path: Path) -> None | 0 | legacy-bootstrap |
| `astra_one.owner_approval._safe_child` | function | `bootstrap/astra-one/astra_one/owner_approval.py:101-112` | def _safe_child(parent: Path, value: object, *, label: str) -> Path | 0 | legacy-bootstrap |
| `astra_one.owner_approval._validate_payload` | function | `bootstrap/astra-one/astra_one/owner_approval.py:115-139` | def _validate_payload(payload: object) -> dict[str, Any] | 0 | legacy-bootstrap |
| `astra_one.owner_approval._document` | function | `bootstrap/astra-one/astra_one/owner_approval.py:142-163` | def _document(receipt: Mapping[str, Any]) -> dict[str, Any] | 0 | legacy-bootstrap |
| `astra_one.owner_approval.prepare_receipt` | function | `bootstrap/astra-one/astra_one/owner_approval.py:166-210` | def prepare_receipt(payload: Mapping[str, Any], *, receipt_path: Path, allowed_signers: Path, message_file: str, signature_file: str, trusted_root: Path \| None=None) -> dict[str,  | 1 | legacy-bootstrap |
| `astra_one.owner_approval._principal_is_allowed` | function | `bootstrap/astra-one/astra_one/owner_approval.py:213-220` | def _principal_is_allowed(allowed_signers: Path, principal: str) -> None | 0 | legacy-bootstrap |
| `astra_one.owner_approval.verify_receipt` | function | `bootstrap/astra-one/astra_one/owner_approval.py:223-266` | def verify_receipt(receipt_path: Path, *, allowed_signers: Path, expected: Mapping[str, object] \| None=None, trusted_root: Path \| None=None) -> dict[str, Any] | 1 | legacy-bootstrap |
| `astra_one.owner_approval.main` | function | `bootstrap/astra-one/astra_one/owner_approval.py:269-297` | def main(argv: list[str] \| None=None) -> int | 155 | legacy-bootstrap |
| `astra_one.planner.focused_architecture` | function | `bootstrap/astra-one/astra_one/planner.py:15-40` | def focused_architecture(text: str, focus: str='') -> str | 2 | legacy-bootstrap |
| `astra_one.planner.validate_plan` | function | `bootstrap/astra-one/astra_one/planner.py:43-56` | def validate_plan(obj: object) -> list[dict] | 2 | legacy-bootstrap |
| `astra_one.planner.propose` | function | `bootstrap/astra-one/astra_one/planner.py:59-90` | def propose(store: Store, focus: str='', count: int=4, model: str='qwen3:8b', output: Path \| None=None) -> dict | 0 | legacy-bootstrap |
| `astra_one.runner.event_payload` | function | `bootstrap/astra-one/astra_one/runner.py:26-32` | def event_payload(*, run_id: str, task_id: str, seq: int, stage: str, step: str, branch: str, base_sha: str, tool_count: int=0, elapsed_s: int=0, attempt: int=1, result: str='') -> | 2 | legacy-bootstrap |
| `astra_one.runner.Progress` | class | `bootstrap/astra-one/astra_one/runner.py:35-64` | class Progress() | 2 | legacy-bootstrap |
| `astra_one.runner.Progress.__init__` | method | `bootstrap/astra-one/astra_one/runner.py:36-41` | def __init__(self, store: Store) | 5 | legacy-bootstrap |
| `astra_one.runner.Progress.flush` | method | `bootstrap/astra-one/astra_one/runner.py:43-58` | def flush(self, limit: int=100) -> dict | 3 | legacy-bootstrap |
| `astra_one.runner.Progress.send` | method | `bootstrap/astra-one/astra_one/runner.py:60-64` | def send(self, e: dict) -> None | 3 | legacy-bootstrap |
| `astra_one.runner.publish_manual_state` | function | `bootstrap/astra-one/astra_one/runner.py:67-74` | def publish_manual_state(store: Store, task_id: str, stage: str, step: str) -> None | 0 | legacy-bootstrap |
| `astra_one.runner.build_prompt` | function | `bootstrap/astra-one/astra_one/runner.py:77-93` | def build_prompt(task: dict, base_sha: str, architecture_sha: str) -> str | 2 | legacy-bootstrap |
| `astra_one.runner.create_worktree` | function | `bootstrap/astra-one/astra_one/runner.py:96-114` | def create_worktree(store: Store, task_id: str, run_id: str) -> tuple[Path, str, str] | 2 | legacy-bootstrap |
| `astra_one.runner._read_lines` | function | `bootstrap/astra-one/astra_one/runner.py:117-122` | def _read_lines(pipe: object, queue_out: queue.Queue) | 0 | legacy-bootstrap |
| `astra_one.runner.changes_and_qc` | function | `bootstrap/astra-one/astra_one/runner.py:125-150` | def changes_and_qc(worktree: Path) -> tuple[bool, str] | 2 | legacy-bootstrap |
| `astra_one.runner.execute_claim` | function | `bootstrap/astra-one/astra_one/runner.py:153-271` | def execute_claim(store: Store, claimed: dict, *, model: str='qwen3:8b', context: int=16384, max_seconds: int=1800) -> int | 2 | legacy-bootstrap |
| `astra_one.runner.execute_claim.emit` | function | `bootstrap/astra-one/astra_one/runner.py:167-172` | def emit(stage: str, step: str, result: str='') | 5 | legacy-bootstrap |
| `astra_one.supervisor.classify_failure` | function | `bootstrap/astra-one/astra_one/supervisor.py:40-65` | def classify_failure(code: str) -> str | 1 | legacy-bootstrap |
| `astra_one.supervisor.failure_fingerprint` | function | `bootstrap/astra-one/astra_one/supervisor.py:68-74` | def failure_fingerprint(task_id: str, generation: int, category: str, code: str, base_sha: str='', candidate_sha: str='') -> str | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController` | class | `bootstrap/astra-one/astra_one/supervisor.py:77-1449` | class SupervisorController() | 2 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.__init__` | method | `bootstrap/astra-one/astra_one/supervisor.py:80-81` | def __init__(self, state: State) | 5 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.ensure_schema` | method | `bootstrap/astra-one/astra_one/supervisor.py:83-84` | def ensure_schema(self) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._lease_expired` | method | `bootstrap/astra-one/astra_one/supervisor.py:87-92` | def _lease_expired(updated_at: str, max_age_seconds: int) -> bool | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._reconcile_recovery_leases_locked` | method | `bootstrap/astra-one/astra_one/supervisor.py:94-136` | def _reconcile_recovery_leases_locked(self, db: sqlite3.Connection, max_age_seconds: int=RECOVERY_LEASE_TTL_SECONDS) -> list[dict] | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._reconcile_completed_cases_locked` | method | `bootstrap/astra-one/astra_one/supervisor.py:139-169` | def _reconcile_completed_cases_locked(db: sqlite3.Connection) -> list[dict] | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._candidate_patch_is_integrated` | method | `bootstrap/astra-one/astra_one/supervisor.py:171-210` | def _candidate_patch_is_integrated(self, worktree: str, base_sha: str, candidate_sha: str, integration: Path) -> bool | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.reconcile_recovery_leases` | method | `bootstrap/astra-one/astra_one/supervisor.py:212-218` | def reconcile_recovery_leases(self, max_age_seconds: int=RECOVERY_LEASE_TTL_SECONDS) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.triage_failure` | method | `bootstrap/astra-one/astra_one/supervisor.py:220-287` | def triage_failure(self, task_id: str, failure_code: str, *, base_sha: str='', candidate_sha: str='', generation: int \| None=None) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.self_doctor` | method | `bootstrap/astra-one/astra_one/supervisor.py:289-316` | def self_doctor(self, limit: int=50) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.mark_external_blocker` | method | `bootstrap/astra-one/astra_one/supervisor.py:318-365` | def mark_external_blocker(self, case_id: str, category: str, failure_code: str='') -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.resolve_external` | method | `bootstrap/astra-one/astra_one/supervisor.py:367-527` | def resolve_external(self, task_id: str, evidence_path: Path) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_rel_004_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:529-615` | def _validate_rel_004_evidence(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_github_free_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:617-640` | def _validate_github_free_evidence(self, evidence: dict) -> None | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_tws_blender_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:642-672` | def _validate_tws_blender_evidence(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_tws_motion_artist_review` | method | `bootstrap/astra-one/astra_one/supervisor.py:674-725` | def _validate_tws_motion_artist_review(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_cloudflare_deployment_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:727-755` | def _validate_cloudflare_deployment_evidence(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_pending_jobs_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:757-799` | def _validate_pending_jobs_evidence(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._validate_research_benchmark_evidence` | method | `bootstrap/astra-one/astra_one/supervisor.py:801-834` | def _validate_research_benchmark_evidence(self, evidence: dict) -> None | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.claim_recovery` | method | `bootstrap/astra-one/astra_one/supervisor.py:836-869` | def claim_recovery(self, case_id: str, lane_id: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.bind_recovery_candidate` | method | `bootstrap/astra-one/astra_one/supervisor.py:871-902` | def bind_recovery_candidate(self, lane_id: str, case_id: str, *, lease_token: str, run_id: str, generation: int, candidate_sha: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.finish_recovery` | method | `bootstrap/astra-one/astra_one/supervisor.py:904-970` | def finish_recovery(self, lane_id: str, case_id: str, *, lease_token: str, run_id: str, generation: int, candidate_sha: str='', state: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.release_unstarted_recovery` | method | `bootstrap/astra-one/astra_one/supervisor.py:972-997` | def release_unstarted_recovery(self, lane_id: str, case_id: str, *, lease_token: str) -> dict | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.claim_upgrade_audit` | method | `bootstrap/astra-one/astra_one/supervisor.py:999-1031` | def claim_upgrade_audit(self, task_id: str, *, model: str) -> dict | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.finish_upgrade_audit` | method | `bootstrap/astra-one/astra_one/supervisor.py:1033-1079` | def finish_upgrade_audit(self, audit_id: str, *, run_id: str, status: str, report_path: str='', report_sha: str='', evidence_sha: str='', failure_code: str='') -> dict | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.start_batch` | method | `bootstrap/astra-one/astra_one/supervisor.py:1081-1115` | def start_batch(self, batch_id: str, limit: int=20) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.batch_status` | method | `bootstrap/astra-one/astra_one/supervisor.py:1117-1128` | def batch_status(self, batch_id: str) -> dict | 2 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.replenish_batch` | method | `bootstrap/astra-one/astra_one/supervisor.py:1130-1183` | def replenish_batch(self, batch_id: str, target: int=20) -> dict | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.create_upgrade` | method | `bootstrap/astra-one/astra_one/supervisor.py:1185-1208` | def create_upgrade(self, batch_id: str, candidate_sha: str, rollback_sha: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._integration_repository` | method | `bootstrap/astra-one/astra_one/supervisor.py:1210-1221` | def _integration_repository(self) -> Path | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._verify_commit` | method | `bootstrap/astra-one/astra_one/supervisor.py:1224-1228` | def _verify_commit(repository: Path, sha: str) -> None | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._candidate_checkout` | method | `bootstrap/astra-one/astra_one/supervisor.py:1230-1251` | def _candidate_checkout(self, repository: Path, candidate_sha: str) -> tempfile.TemporaryDirectory | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._run_candidate_tests` | method | `bootstrap/astra-one/astra_one/supervisor.py:1253-1306` | def _run_candidate_tests(self, repository: Path, candidate_sha: str, *, canary: bool=False) -> str | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._verify_database_backup` | method | `bootstrap/astra-one/astra_one/supervisor.py:1308-1317` | def _verify_database_backup(self, batch_id: str) -> str | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.run_upgrade_check` | method | `bootstrap/astra-one/astra_one/supervisor.py:1319-1322` | def run_upgrade_check(self, batch_id: str, stage: str, artifact_sha: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController._run_upgrade_check_locked` | method | `bootstrap/astra-one/astra_one/supervisor.py:1324-1368` | def _run_upgrade_check_locked(self, batch_id: str, stage: str, artifact_sha: str) -> dict | 0 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.transition_upgrade` | method | `bootstrap/astra-one/astra_one/supervisor.py:1370-1415` | def transition_upgrade(self, batch_id: str, state: str) -> dict | 1 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.status` | method | `bootstrap/astra-one/astra_one/supervisor.py:1417-1431` | def status(self) -> dict | 80 | legacy-bootstrap |
| `astra_one.supervisor.SupervisorController.tick` | method | `bootstrap/astra-one/astra_one/supervisor.py:1433-1449` | def tick(self, limit: int=50) -> dict | 2 | legacy-bootstrap |
| `astra_one.test_evidence_cache._sha256_bytes` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:27-28` | def _sha256_bytes(value: bytes) -> str | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._sha256_file` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:31-36` | def _sha256_file(path: Path) -> str | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._git_head` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:39-45` | def _git_head(worktree: Path) -> str \| None | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._tree_sha` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:48-63` | def _tree_sha(worktree: Path) -> str \| None | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._dependency_lock_sha` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:66-80` | def _dependency_lock_sha(worktree: Path) -> str | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._security_policy_sha` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:83-85` | def _security_policy_sha(worktree: Path) -> str | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache._runner_version` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:88-99` | def _runner_version(command: list[str], context: dict[str, Any]) -> str \| None | 0 | legacy-bootstrap |
| `astra_one.test_evidence_cache.build_cache_material` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:102-130` | def build_cache_material(worktree: Path, image_digest: str, command: list[str], context: dict[str, Any] \| None=None) -> dict[str, Any] \| None | 1 | legacy-bootstrap |
| `astra_one.test_evidence_cache.cache_key` | function | `bootstrap/astra-one/astra_one/test_evidence_cache.py:133-135` | def cache_key(material: dict[str, Any]) -> str | 1 | legacy-bootstrap |
| `astra_one.test_evidence_cache.EvidenceCache` | class | `bootstrap/astra-one/astra_one/test_evidence_cache.py:138-170` | class EvidenceCache() | 1 | legacy-bootstrap |
| `astra_one.test_evidence_cache.EvidenceCache.__init__` | method | `bootstrap/astra-one/astra_one/test_evidence_cache.py:139-140` | def __init__(self, directory: Path) | 5 | legacy-bootstrap |
| `astra_one.test_evidence_cache.EvidenceCache.load` | method | `bootstrap/astra-one/astra_one/test_evidence_cache.py:142-156` | def load(self, key: str) -> dict[str, Any] \| None | 1 | legacy-bootstrap |
| `astra_one.test_evidence_cache.EvidenceCache.store` | method | `bootstrap/astra-one/astra_one/test_evidence_cache.py:158-170` | def store(self, key: str, receipt: dict[str, Any]) -> None | 44 | legacy-bootstrap |
| `index.make` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:50-50` | const make=(tag,text,cls)=>{const e=document.createElement(tag);e.textContent=String(text);if(cls)e.className=cls;return e}; | 0 | legacy-bootstrap |
| `index.get` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:51-51` | async function get(url){const r=await fetch(url,{headers:{authorization:'Bearer '+token},cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()} | 27 | legacy-bootstrap |
| `index.refresh` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:52-52` | async function refresh(){ | 0 | legacy-bootstrap |
| `index.loadEvents` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:69-69` | async function loadEvents(){if(!selected)return;try{const data=await get('/api/events?run_id='+encodeURIComponent(selected)); | 0 | legacy-bootstrap |
| `index.secureHeaders` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:76-76` | function secureHeaders(contentType: string): HeadersInit { | 0 | legacy-bootstrap |
| `index.json` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:82-82` | function json(data: unknown, status = 200): Response { | 44 | legacy-bootstrap |
| `index.equal` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:85-85` | function equal(a: string, b: string): boolean { | 5 | legacy-bootstrap |
| `index.authorized` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:91-91` | function authorized(req: Request, secret: string): boolean { | 4 | legacy-bootstrap |
| `index.validStr` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:94-94` | function validStr(v: unknown, max: number, regex: RegExp): v is string { | 0 | legacy-bootstrap |
| `index.validate` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:97-97` | function validate(body: unknown): Event \| null { | 2 | legacy-bootstrap |
| `index.postEvent` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/src/index.ts:116-116` | async function postEvent(req: Request, env: Env): Promise<Response> { | 0 | legacy-bootstrap |
| `worker.test.uuid` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/tests/worker.test.mjs:36-36` | const uuid=()=> '123e4567-e89b-42d3-a456-426614174000'; | 4 | legacy-bootstrap |
| `worker.test.message` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/tests/worker.test.mjs:37-37` | const message=(seq,stage)=>({event_id:seq===1?uuid():'123e4567-e89b-42d3-a456-426614174001',run_id:'123e4567-e89b-42d3-a456-426614174999',task_id:'ASTRA-101',seq,time:'2026-11-13T1 | 13 | legacy-bootstrap |
| `worker.test.call` | function | `bootstrap/astra-one/cloudflare/astra-one-monitor/tests/worker.test.mjs:38-38` | async function call(path,method='GET',body=null,token=''){ | 7 | legacy-bootstrap |
| `scripts.verify_manifest.ManifestError` | class | `bootstrap/astra-one/scripts/verify_manifest.py:10-11` | class ManifestError(ValueError) | 0 | legacy-bootstrap |
| `scripts.verify_manifest._validate_windows_component` | function | `bootstrap/astra-one/scripts/verify_manifest.py:25-30` | def _validate_windows_component(part: str) -> None | 0 | legacy-bootstrap |
| `scripts.verify_manifest._is_generated` | function | `bootstrap/astra-one/scripts/verify_manifest.py:33-39` | def _is_generated(relative: PurePosixPath) -> bool | 0 | legacy-bootstrap |
| `scripts.verify_manifest._safe_relative` | function | `bootstrap/astra-one/scripts/verify_manifest.py:42-55` | def _safe_relative(name: object) -> PurePosixPath | 1 | legacy-bootstrap |
| `scripts.verify_manifest._safe_path` | function | `bootstrap/astra-one/scripts/verify_manifest.py:58-73` | def _safe_path(root: Path, relative: PurePosixPath) -> Path | 0 | legacy-bootstrap |
| `scripts.verify_manifest._inventory` | function | `bootstrap/astra-one/scripts/verify_manifest.py:76-112` | def _inventory(root: Path) -> dict[tuple[str, ...], str] | 0 | legacy-bootstrap |
| `scripts.verify_manifest._verify_manifest` | function | `bootstrap/astra-one/scripts/verify_manifest.py:115-152` | def _verify_manifest(root: Path) -> int | 1 | legacy-bootstrap |
| `scripts.verify_manifest.verify_manifest` | function | `bootstrap/astra-one/scripts/verify_manifest.py:155-157` | def verify_manifest() -> int | 1 | legacy-bootstrap |
| `scripts.verify_manifest.main` | function | `bootstrap/astra-one/scripts/verify_manifest.py:160-167` | def main() -> int | 155 | legacy-bootstrap |
| `scripts.verify_package._run` | function | `bootstrap/astra-one/scripts/verify_package.py:15-19` | def _run(command: list[str], cwd: Path, env: dict[str, str]) -> None | 1 | legacy-bootstrap |
| `scripts.verify_package._verify_package` | function | `bootstrap/astra-one/scripts/verify_package.py:22-53` | def _verify_package(package_root: Path) -> None | 1 | legacy-bootstrap |
| `scripts.verify_package.verify_package` | function | `bootstrap/astra-one/scripts/verify_package.py:56-58` | def verify_package() -> None | 1 | legacy-bootstrap |
| `test_core.git` | function | `bootstrap/astra-one/tests/test_core.py:17-18` | def git(root, *args) | 19 | legacy-bootstrap |
| `test_core.AstraTests` | class | `bootstrap/astra-one/tests/test_core.py:21-252` | class AstraTests(unittest.TestCase) | 2 | legacy-bootstrap |
| `test_core.AstraTests.setUp` | method | `bootstrap/astra-one/tests/test_core.py:22-35` | def setUp(self) | 35 | legacy-bootstrap |
| `test_core.AstraTests.init` | method | `bootstrap/astra-one/tests/test_core.py:37-38` | def init(self) | 14 | legacy-bootstrap |
| `test_core.AstraTests.architecture` | method | `bootstrap/astra-one/tests/test_core.py:40-46` | def architecture(self) | 9 | legacy-bootstrap |
| `test_core.AstraTests.task` | method | `bootstrap/astra-one/tests/test_core.py:48-49` | def task(self, task_id='ASTRA-101', depends_on=None) | 24 | legacy-bootstrap |
| `test_core.AstraTests.test_init_starts_engine_stopped` | method | `bootstrap/astra-one/tests/test_core.py:51-54` | def test_init_starts_engine_stopped(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_refuse_reinitializing_state` | method | `bootstrap/astra-one/tests/test_core.py:56-59` | def test_refuse_reinitializing_state(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_refuse_dirty_source` | method | `bootstrap/astra-one/tests/test_core.py:61-64` | def test_refuse_dirty_source(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_architecture_requires_approval` | method | `bootstrap/astra-one/tests/test_core.py:66-71` | def test_architecture_requires_approval(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_wrong_architecture_sha_denied` | method | `bootstrap/astra-one/tests/test_core.py:73-78` | def test_wrong_architecture_sha_denied(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_approved_architecture_is_still_not_started` | method | `bootstrap/astra-one/tests/test_core.py:80-83` | def test_approved_architecture_is_still_not_started(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_task_rejects_unexpected_secret_field` | method | `bootstrap/astra-one/tests/test_core.py:85-88` | def test_task_rejects_unexpected_secret_field(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_task_requires_acceptance` | method | `bootstrap/astra-one/tests/test_core.py:90-93` | def test_task_requires_acceptance(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_enqueue_claim_once` | method | `bootstrap/astra-one/tests/test_core.py:95-101` | def test_enqueue_claim_once(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_dependencies_block_claim` | method | `bootstrap/astra-one/tests/test_core.py:103-108` | def test_dependencies_block_claim(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_dependencies_reject_unknown` | method | `bootstrap/astra-one/tests/test_core.py:110-113` | def test_dependencies_reject_unknown(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_pause_prevents_claim` | method | `bootstrap/astra-one/tests/test_core.py:115-118` | def test_pause_prevents_claim(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_stop_prevents_claim` | method | `bootstrap/astra-one/tests/test_core.py:120-123` | def test_stop_prevents_claim(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_architecture_replacement_pauses` | method | `bootstrap/astra-one/tests/test_core.py:125-129` | def test_architecture_replacement_pauses(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_recover_marks_interrupted` | method | `bootstrap/astra-one/tests/test_core.py:131-135` | def test_recover_marks_interrupted(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_retry_requires_explicit_failed_state` | method | `bootstrap/astra-one/tests/test_core.py:137-142` | def test_retry_requires_explicit_failed_state(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_event_metadata_has_no_private_content` | method | `bootstrap/astra-one/tests/test_core.py:144-149` | def test_event_metadata_has_no_private_content(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_events_persist_and_sync` | method | `bootstrap/astra-one/tests/test_core.py:151-159` | def test_events_persist_and_sync(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_progress_no_monitor_configuration` | method | `bootstrap/astra-one/tests/test_core.py:161-165` | def test_progress_no_monitor_configuration(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_prompt_does_not_include_private_architecture` | method | `bootstrap/astra-one/tests/test_core.py:167-172` | def test_prompt_does_not_include_private_architecture(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_qc_rejects_no_changes` | method | `bootstrap/astra-one/tests/test_core.py:174-177` | def test_qc_rejects_no_changes(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_qc_rejects_deletion` | method | `bootstrap/astra-one/tests/test_core.py:179-183` | def test_qc_rejects_deletion(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_qc_rejects_python_syntax` | method | `bootstrap/astra-one/tests/test_core.py:185-189` | def test_qc_rejects_python_syntax(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_qc_passes_python_syntax` | method | `bootstrap/astra-one/tests/test_core.py:191-195` | def test_qc_passes_python_syntax(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_reviewed_candidate_integrates_only_to_local_feature` | method | `bootstrap/astra-one/tests/test_core.py:197-216` | def test_reviewed_candidate_integrates_only_to_local_feature(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_integration_rejects_unapproved` | method | `bootstrap/astra-one/tests/test_core.py:218-221` | def test_integration_rejects_unapproved(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_planner_focus_selects_one_heading_section` | method | `bootstrap/astra-one/tests/test_core.py:223-227` | def test_planner_focus_selects_one_heading_section(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_planner_large_architecture_requires_focus` | method | `bootstrap/astra-one/tests/test_core.py:229-231` | def test_planner_large_architecture_requires_focus(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_planner_rejects_forward_dependency` | method | `bootstrap/astra-one/tests/test_core.py:233-236` | def test_planner_rejects_forward_dependency(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_atomic_plan_enqueue` | method | `bootstrap/astra-one/tests/test_core.py:238-245` | def test_atomic_plan_enqueue(self) | 2 | legacy-bootstrap |
| `test_core.AstraTests.test_cloudflare_schema_valid_sqlite` | method | `bootstrap/astra-one/tests/test_core.py:247-252` | def test_cloudflare_schema_valid_sqlite(self) | 2 | legacy-bootstrap |
| `test_event_readiness.EventReadinessTests` | class | `bootstrap/astra-one/tests/test_event_readiness.py:11-39` | class EventReadinessTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_event_readiness.EventReadinessTests.setUp` | method | `bootstrap/astra-one/tests/test_event_readiness.py:12-17` | def setUp(self) | 35 | legacy-bootstrap |
| `test_event_readiness.EventReadinessTests.test_data_version_wakes_after_external_commit` | method | `bootstrap/astra-one/tests/test_event_readiness.py:19-31` | def test_data_version_wakes_after_external_commit(self) | 1 | legacy-bootstrap |
| `test_event_readiness.EventReadinessTests.test_data_version_wakes_after_external_commit.commit` | function | `bootstrap/astra-one/tests/test_event_readiness.py:22-24` | def commit() | 22 | legacy-bootstrap |
| `test_event_readiness.EventReadinessTests.test_data_version_wait_is_bounded` | method | `bootstrap/astra-one/tests/test_event_readiness.py:33-39` | def test_data_version_wait_is_bounded(self) | 1 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests` | class | `bootstrap/astra-one/tests/test_evidence_cache.py:9-45` | class EvidenceCacheTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests.setUp` | method | `bootstrap/astra-one/tests/test_evidence_cache.py:10-15` | def setUp(self) | 35 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests.material` | method | `bootstrap/astra-one/tests/test_evidence_cache.py:17-21` | def material(self, **context) | 1 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests.test_key_contains_material_inputs_and_changes_with_source` | method | `bootstrap/astra-one/tests/test_evidence_cache.py:23-30` | def test_key_contains_material_inputs_and_changes_with_source(self) | 1 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests.test_cache_only_reuses_a_success_and_rejects_stale_key` | method | `bootstrap/astra-one/tests/test_evidence_cache.py:32-40` | def test_cache_only_reuses_a_success_and_rejects_stale_key(self) | 1 | legacy-bootstrap |
| `test_evidence_cache.EvidenceCacheTests.test_context_change_invalidates_key` | method | `bootstrap/astra-one/tests/test_evidence_cache.py:42-45` | def test_context_change_invalidates_key(self) | 1 | legacy-bootstrap |
| `test_full_plan.git_repo` | function | `bootstrap/astra-one/tests/test_full_plan.py:13-23` | def git_repo(root: Path) -> Path | 5 | legacy-bootstrap |
| `test_full_plan.child` | function | `bootstrap/astra-one/tests/test_full_plan.py:26-39` | def child(cid: str, sequence: int, depends_on: list[str] \| None=None) -> dict | 3 | legacy-bootstrap |
| `test_full_plan.bound_receipts` | function | `bootstrap/astra-one/tests/test_full_plan.py:42-77` | def bound_receipts(state: State, task_id: str, run_id: str, attempt: int, source_sha: str, changed_files: list[str], candidate_sha: str, contract_sha: str, child_evidence: list[dic | 2 | legacy-bootstrap |
| `test_full_plan.parent` | function | `bootstrap/astra-one/tests/test_full_plan.py:80-108` | def parent(pid: str, module: str, dependencies: list[str] \| None=None, owner_gate: bool=False, priority: str='P1') -> dict | 10 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests` | class | `bootstrap/astra-one/tests/test_full_plan.py:111-295` | class FullPlanImportTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.setUp` | method | `bootstrap/astra-one/tests/test_full_plan.py:112-121` | def setUp(self) | 35 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.tearDown` | method | `bootstrap/astra-one/tests/test_full_plan.py:123-124` | def tearDown(self) | 12 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.plan` | method | `bootstrap/astra-one/tests/test_full_plan.py:126-153` | def plan(self) | 7 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_import_attaches_children_and_populates_only_eligible_queue` | method | `bootstrap/astra-one/tests/test_full_plan.py:155-169` | def test_import_attaches_children_and_populates_only_eligible_queue(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_completion_promotes_dependent_parent_and_children` | method | `bootstrap/astra-one/tests/test_full_plan.py:171-198` | def test_completion_promotes_dependent_parent_and_children(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_import_is_idempotent_and_conflicts_are_not_overwritten` | method | `bootstrap/astra-one/tests/test_full_plan.py:200-220` | def test_import_is_idempotent_and_conflicts_are_not_overwritten(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_owner_gate_requires_authenticated_release` | method | `bootstrap/astra-one/tests/test_full_plan.py:222-227` | def test_owner_gate_requires_authenticated_release(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_approved_owner_gate_is_claimable_but_unapproved_gate_is_not` | method | `bootstrap/astra-one/tests/test_full_plan.py:229-274` | def test_approved_owner_gate_is_claimable_but_unapproved_gate_is_not(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_task_markdown_round_trips_to_sqlite_ids_and_payloads` | method | `bootstrap/astra-one/tests/test_full_plan.py:276-286` | def test_task_markdown_round_trips_to_sqlite_ids_and_payloads(self) | 1 | legacy-bootstrap |
| `test_full_plan.FullPlanImportTests.test_task_markdown_rejects_payload_or_id_drift` | method | `bootstrap/astra-one/tests/test_full_plan.py:288-295` | def test_task_markdown_rejects_payload_or_id_drift(self) | 1 | legacy-bootstrap |
| `test_linux_sda.git_repo` | function | `bootstrap/astra-one/tests/test_linux_sda.py:44-52` | def git_repo(root) | 5 | legacy-bootstrap |
| `test_linux_sda.task` | function | `bootstrap/astra-one/tests/test_linux_sda.py:55-56` | def task(i, deps=None) | 24 | legacy-bootstrap |
| `test_linux_sda.audit_task` | function | `bootstrap/astra-one/tests/test_linux_sda.py:59-76` | def audit_task(i=1) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests` | class | `bootstrap/astra-one/tests/test_linux_sda.py:78-1900` | class LinuxSDATests(unittest.TestCase) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.setUp` | method | `bootstrap/astra-one/tests/test_linux_sda.py:79-89` | def setUp(self) | 35 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests._add_supervisor_policy_files` | method | `bootstrap/astra-one/tests/test_linux_sda.py:91-103` | def _add_supervisor_policy_files(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_worker_failure_categories_are_bounded` | method | `bootstrap/astra-one/tests/test_linux_sda.py:105-110` | def test_worker_failure_categories_are_bounded(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_supervisor_inspection_is_pinned_and_read_only` | method | `bootstrap/astra-one/tests/test_linux_sda.py:112-124` | def test_supervisor_inspection_is_pinned_and_read_only(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_supervisor_inspection_rejects_missing_or_dirty_source` | method | `bootstrap/astra-one/tests/test_linux_sda.py:126-133` | def test_supervisor_inspection_rejects_missing_or_dirty_source(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_requirements_parser_preserves_exact_acceptance_and_child_order` | method | `bootstrap/astra-one/tests/test_linux_sda.py:135-162` | def test_requirements_parser_preserves_exact_acceptance_and_child_order(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_supervise_prompt_binds_task_acceptance_and_repository_citations` | method | `bootstrap/astra-one/tests/test_linux_sda.py:164-190` | def test_supervise_prompt_binds_task_acceptance_and_repository_citations(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_supervise_prompt_binds_task_acceptance_and_repository_citations.fake_codex_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:169-178` | def fake_codex_call(*, output_file, prompt, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_review_rejections_keep_only_bounded_repair_categories` | method | `bootstrap/astra-one/tests/test_linux_sda.py:192-202` | def test_review_rejections_keep_only_bounded_repair_categories(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repair_prompt_contains_only_bounded_guidance` | method | `bootstrap/astra-one/tests/test_linux_sda.py:204-215` | def test_repair_prompt_contains_only_bounded_guidance(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repair_prompt_covers_merge_and_scope_failures` | method | `bootstrap/astra-one/tests/test_linux_sda.py:217-226` | def test_repair_prompt_covers_merge_and_scope_failures(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_worker_prompt_renders_task_type_and_scope_contract` | method | `bootstrap/astra-one/tests/test_linux_sda.py:228-236` | def test_worker_prompt_renders_task_type_and_scope_contract(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_scoped_reference_pack_is_bounded_and_denies_untrusted_paths` | method | `bootstrap/astra-one/tests/test_linux_sda.py:238-254` | def test_scoped_reference_pack_is_bounded_and_denies_untrusted_paths(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_reference_prompt_data_cannot_replace_authoritative_policy` | method | `bootstrap/astra-one/tests/test_linux_sda.py:256-263` | def test_reference_prompt_data_cannot_replace_authoritative_policy(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_upgrade_audit_brief_is_task_specific_and_bounded` | method | `bootstrap/astra-one/tests/test_linux_sda.py:265-273` | def test_upgrade_audit_brief_is_task_specific_and_bounded(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_ci_local_only_prompt_preserves_quota_boundary` | method | `bootstrap/astra-one/tests/test_linux_sda.py:275-283` | def test_ci_local_only_prompt_preserves_quota_boundary(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_specific_packaging_guidance_requires_manifest_update` | method | `bootstrap/astra-one/tests/test_linux_sda.py:285-289` | def test_task_specific_packaging_guidance_requires_manifest_update(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_specific_code_index_guidance_targets_qc_findings` | method | `bootstrap/astra-one/tests/test_linux_sda.py:291-303` | def test_task_specific_code_index_guidance_targets_qc_findings(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_audit_prompt_is_report_only_and_metadata_bounded` | method | `bootstrap/astra-one/tests/test_linux_sda.py:305-310` | def test_audit_prompt_is_report_only_and_metadata_bounded(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_source_dirty_refused` | method | `bootstrap/astra-one/tests/test_linux_sda.py:312-315` | def test_source_dirty_refused(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_architecture_approval_explicit` | method | `bootstrap/astra-one/tests/test_linux_sda.py:317-321` | def test_architecture_approval_explicit(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_dependency_blocks_claim_until_integrated` | method | `bootstrap/astra-one/tests/test_linux_sda.py:323-329` | def test_dependency_blocks_claim_until_integrated(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_stop_and_pause_gate` | method | `bootstrap/astra-one/tests/test_linux_sda.py:331-337` | def test_stop_and_pause_gate(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_quota_pauses_builder_but_allows_deterministic_qc_tick` | method | `bootstrap/astra-one/tests/test_linux_sda.py:339-352` | def test_quota_pauses_builder_but_allows_deterministic_qc_tick(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_lane_pause_does_not_cross_block_the_other_lane` | method | `bootstrap/astra-one/tests/test_linux_sda.py:354-361` | def test_lane_pause_does_not_cross_block_the_other_lane(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_normal_and_recovery_lane_runner_overlap_without_second_master` | method | `bootstrap/astra-one/tests/test_linux_sda.py:363-386` | def test_normal_and_recovery_lane_runner_overlap_without_second_master(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_normal_and_recovery_lane_runner_overlap_without_second_master.fake_normal` | function | `bootstrap/astra-one/tests/test_linux_sda.py:366-370` | def fake_normal(*args, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_normal_and_recovery_lane_runner_overlap_without_second_master.fake_recovery` | function | `bootstrap/astra-one/tests/test_linux_sda.py:371-375` | def fake_recovery(*args, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads` | method | `bootstrap/astra-one/tests/test_linux_sda.py:388-412` | def test_concurrent_runner_initializes_schema_before_lane_threads(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads.fake_schema` | function | `bootstrap/astra-one/tests/test_linux_sda.py:390-392` | def fake_schema() | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads.fake_normal` | function | `bootstrap/astra-one/tests/test_linux_sda.py:393-396` | def fake_normal(*args, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_concurrent_runner_initializes_schema_before_lane_threads.fake_recovery` | function | `bootstrap/astra-one/tests/test_linux_sda.py:397-400` | def fake_recovery(*args, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_lane_critical_section_waits_for_master_lock_without_inference_locking` | method | `bootstrap/astra-one/tests/test_linux_sda.py:414-441` | def test_lane_critical_section_waits_for_master_lock_without_inference_locking(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_second_controller_is_rejected_and_stale_lock_reconciles` | method | `bootstrap/astra-one/tests/test_linux_sda.py:443-473` | def test_second_controller_is_rejected_and_stale_lock_reconciles(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_recover_no_replay` | method | `bootstrap/astra-one/tests/test_linux_sda.py:475-480` | def test_recover_no_replay(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_retry_claim_clears_stale_attempt_fields_but_keeps_history` | method | `bootstrap/astra-one/tests/test_linux_sda.py:482-495` | def test_retry_claim_clears_stale_attempt_fields_but_keeps_history(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_failed_and_retried_tasks_leave_no_stale_review_or_merge_queue` | method | `bootstrap/astra-one/tests/test_linux_sda.py:497-515` | def test_failed_and_retried_tasks_leave_no_stale_review_or_merge_queue(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_tool_count_is_persisted_on_run_transitions` | method | `bootstrap/astra-one/tests/test_linux_sda.py:517-525` | def test_tool_count_is_persisted_on_run_transitions(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_receipt_columns_migrate_additively_from_v4` | method | `bootstrap/astra-one/tests/test_linux_sda.py:527-537` | def test_codex_receipt_columns_migrate_additively_from_v4(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_reopen_failed_starts_new_generation_without_erasing_history` | method | `bootstrap/astra-one/tests/test_linux_sda.py:539-555` | def test_reopen_failed_starts_new_generation_without_erasing_history(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_checkpoint_export_and_restore_preserve_ledger_and_safety_controls` | method | `bootstrap/astra-one/tests/test_linux_sda.py:557-600` | def test_checkpoint_export_and_restore_preserve_ledger_and_safety_controls(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_checkpoint_restore_rejects_manifest_or_database_tampering` | method | `bootstrap/astra-one/tests/test_linux_sda.py:602-611` | def test_checkpoint_restore_rejects_manifest_or_database_tampering(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_failure_restart_rollback_controls_prevent_duplicate_effects_and_promotion` | method | `bootstrap/astra-one/tests/test_linux_sda.py:613-666` | def test_failure_restart_rollback_controls_prevent_duplicate_effects_and_promotion(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes` | method | `bootstrap/astra-one/tests/test_linux_sda.py:668-716` | def test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes.Response` | class | `bootstrap/astra-one/tests/test_linux_sda.py:684-691` | class Response() | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes.Response.__enter__` | method | `bootstrap/astra-one/tests/test_linux_sda.py:687-688` | def __enter__(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes.Response.__exit__` | method | `bootstrap/astra-one/tests/test_linux_sda.py:690-691` | def __exit__(self, *_) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_progress_sync_publishes_only_bounded_metadata_and_receipt_hashes.urlopen` | function | `bootstrap/astra-one/tests/test_linux_sda.py:693-696` | def urlopen(request, timeout) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_plan_is_atomic` | method | `bootstrap/astra-one/tests/test_linux_sda.py:718-721` | def test_plan_is_atomic(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_plan_rejects_duplicate_job_ids_atomically` | method | `bootstrap/astra-one/tests/test_linux_sda.py:723-726` | def test_plan_rejects_duplicate_job_ids_atomically(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_selector_preserves_fifo_for_same_priority_tasks` | method | `bootstrap/astra-one/tests/test_linux_sda.py:728-730` | def test_selector_preserves_fifo_for_same_priority_tasks(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_selector_honors_priority_before_fifo` | method | `bootstrap/astra-one/tests/test_linux_sda.py:732-737` | def test_selector_honors_priority_before_fifo(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_selector_skips_blocked_head_for_independent_task` | method | `bootstrap/astra-one/tests/test_linux_sda.py:739-742` | def test_selector_skips_blocked_head_for_independent_task(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_rejects_unknown_fields` | method | `bootstrap/astra-one/tests/test_linux_sda.py:744-746` | def test_task_rejects_unknown_fields(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_type_validation_rejects_malformed_design_packet` | method | `bootstrap/astra-one/tests/test_linux_sda.py:748-752` | def test_task_type_validation_rejects_malformed_design_packet(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_spec_preserves_valid_design_metadata_for_assignment` | method | `bootstrap/astra-one/tests/test_linux_sda.py:754-764` | def test_task_spec_preserves_valid_design_metadata_for_assignment(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_type_validation_requires_ordered_child_contract` | method | `bootstrap/astra-one/tests/test_linux_sda.py:766-771` | def test_task_type_validation_requires_ordered_child_contract(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_task_type_validation_rejects_unsafe_scope_root` | method | `bootstrap/astra-one/tests/test_linux_sda.py:773-777` | def test_task_type_validation_rejects_unsafe_scope_root(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_model_cli_is_codex_cloud_not_oss` | method | `bootstrap/astra-one/tests/test_linux_sda.py:779-784` | def test_model_cli_is_codex_cloud_not_oss(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_danger_bypass_is_explicit_and_omits_normal_sandbox` | method | `bootstrap/astra-one/tests/test_linux_sda.py:786-789` | def test_danger_bypass_is_explicit_and_omits_normal_sandbox(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_valid_python` | method | `bootstrap/astra-one/tests/test_linux_sda.py:791-794` | def test_static_change_accepts_valid_python(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_multiple_files_within_limit` | method | `bootstrap/astra-one/tests/test_linux_sda.py:796-800` | def test_static_change_accepts_multiple_files_within_limit(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_javascript_module_files` | method | `bootstrap/astra-one/tests/test_linux_sda.py:802-805` | def test_static_change_accepts_javascript_module_files(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_scoped_swift_migration_source` | method | `bootstrap/astra-one/tests/test_linux_sda.py:807-814` | def test_static_change_accepts_scoped_swift_migration_source(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_migration_blob_preserves_source_whitespace` | method | `bootstrap/astra-one/tests/test_linux_sda.py:816-830` | def test_migration_blob_preserves_source_whitespace(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_generated_artifact_paths` | method | `bootstrap/astra-one/tests/test_linux_sda.py:832-838` | def test_static_change_rejects_generated_artifact_paths(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_paths_outside_task_scope` | method | `bootstrap/astra-one/tests/test_linux_sda.py:840-846` | def test_static_change_rejects_paths_outside_task_scope(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_scope_prefix_sibling` | method | `bootstrap/astra-one/tests/test_linux_sda.py:848-855` | def test_static_change_rejects_scope_prefix_sibling(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_scoped_tool_script` | method | `bootstrap/astra-one/tests/test_linux_sda.py:857-863` | def test_static_change_accepts_scoped_tool_script(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_secret_bearing_env_profile` | method | `bootstrap/astra-one/tests/test_linux_sda.py:865-872` | def test_static_change_rejects_secret_bearing_env_profile(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_zero_files_with_specific_code` | method | `bootstrap/astra-one/tests/test_linux_sda.py:874-878` | def test_static_change_rejects_zero_files_with_specific_code(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_file_limit_with_specific_code` | method | `bootstrap/astra-one/tests/test_linux_sda.py:880-887` | def test_static_change_rejects_file_limit_with_specific_code(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_parses_staged_and_unstaged_porcelain` | method | `bootstrap/astra-one/tests/test_linux_sda.py:889-894` | def test_static_change_parses_staged_and_unstaged_porcelain(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_trailing_whitespace_in_untracked_and_staged_files` | method | `bootstrap/astra-one/tests/test_linux_sda.py:896-907` | def test_static_change_rejects_trailing_whitespace_in_untracked_and_staged_files(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_delete` | method | `bootstrap/astra-one/tests/test_linux_sda.py:909-913` | def test_static_change_rejects_delete(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_symlink` | method | `bootstrap/astra-one/tests/test_linux_sda.py:915-919` | def test_static_change_rejects_symlink(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_policy` | method | `bootstrap/astra-one/tests/test_linux_sda.py:921-925` | def test_static_change_rejects_policy(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_repair_can_change_only_workflow_yaml` | method | `bootstrap/astra-one/tests/test_linux_sda.py:927-936` | def test_scoped_ci_workflow_repair_can_change_only_workflow_yaml(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_rejects_new_floating_action_ref` | method | `bootstrap/astra-one/tests/test_linux_sda.py:938-948` | def test_scoped_ci_workflow_rejects_new_floating_action_ref(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_scoped_ci_workflow_accepts_immutable_action_ref` | method | `bootstrap/astra-one/tests/test_linux_sda.py:950-959` | def test_scoped_ci_workflow_accepts_immutable_action_ref(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_ci_workflow_scope_does_not_allow_other_hidden_paths` | method | `bootstrap/astra-one/tests/test_linux_sda.py:961-971` | def test_ci_workflow_scope_does_not_allow_other_hidden_paths(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_audit_scope_accepts_only_documentation_receipts` | method | `bootstrap/astra-one/tests/test_linux_sda.py:973-978` | def test_audit_scope_accepts_only_documentation_receipts(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_committed_audit_markdown_hard_breaks_use_same_bounded_policy` | method | `bootstrap/astra-one/tests/test_linux_sda.py:980-990` | def test_committed_audit_markdown_hard_breaks_use_same_bounded_policy(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_audit_scope_rejects_executable_or_test_changes` | method | `bootstrap/astra-one/tests/test_linux_sda.py:992-998` | def test_audit_scope_rejects_executable_or_test_changes(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_design_scope_accepts_only_documentation` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1000-1010` | def test_design_scope_accepts_only_documentation(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_preview_preserves_bounded_patch_tail` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1012-1016` | def test_merger_preview_preserves_bounded_patch_tail(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_audit_merger_prompt_accepts_explicit_unknowns` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1018-1038` | def test_audit_merger_prompt_accepts_explicit_unknowns(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_audit_merger_prompt_accepts_explicit_unknowns.fake_merger_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1021-1024` | def fake_merger_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_design_qc_prompt_does_not_require_downstream_implementation` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1040-1062` | def test_design_qc_prompt_does_not_require_downstream_implementation(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_design_qc_prompt_does_not_require_downstream_implementation.fake_qc_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1048-1051` | def fake_qc_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_design_merger_prompt_preserves_documentation_boundary` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1064-1085` | def test_design_merger_prompt_preserves_documentation_boundary(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_design_merger_prompt_preserves_documentation_boundary.fake_merger_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1072-1075` | def fake_merger_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_retries_once_after_invalid_findings_shape` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1087-1106` | def test_merger_retries_once_after_invalid_findings_shape(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_retries_once_after_invalid_findings_shape.fake_merger_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1090-1096` | def fake_merger_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_adjudicates_one_concrete_rejection` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1108-1130` | def test_merger_adjudicates_one_concrete_rejection(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_adjudicates_one_concrete_rejection.fake_merger_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1111-1119` | def fake_merger_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_invalid_python` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1132-1137` | def test_static_change_rejects_invalid_python(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_success_without_file_changes_is_not_a_worker_success` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1139-1151` | def test_codex_success_without_file_changes_is_not_a_worker_success(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_independent_qc_receives_validated_untracked_paths` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1153-1173` | def test_independent_qc_receives_validated_untracked_paths(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_independent_qc_receives_validated_untracked_paths.fake_qc_call` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1160-1163` | def fake_qc_call(*, output_file, **kwargs) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_failed_file_change_event_is_reported` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1175-1186` | def test_codex_failed_file_change_event_is_reported(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_crash_after_tool_effect_is_interrupted_without_replay` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1188-1216` | def test_crash_after_tool_effect_is_interrupted_without_replay(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_stop_marker_prevents_master_claims` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1218-1230` | def test_stop_marker_prevents_master_claims(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_jsonl_receipt_persists_bounded_metadata` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1232-1264` | def test_codex_jsonl_receipt_persists_bounded_metadata(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_jsonl_parser_redacts_payloads_and_bounds_lines` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1266-1294` | def test_codex_jsonl_parser_redacts_payloads_and_bounds_lines(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_codex_sandbox_failure_is_reported_before_process_start` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1296-1301` | def test_codex_sandbox_failure_is_reported_before_process_start(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_docker_qc_stages_linked_worktree_with_private_git_index` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1303-1334` | def test_docker_qc_stages_linked_worktree_with_private_git_index(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_docker_qc_stages_linked_worktree_with_private_git_index.fake_run` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1314-1320` | def fake_run(args, *rest, **kwargs) | 3 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_five_worker_parallel_scheduler` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1336-1354` | def test_five_worker_parallel_scheduler(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_five_worker_parallel_scheduler.fake_execute` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1340-1346` | def fake_execute(state, item, **kwargs) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_safe_serial_integration` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1356-1376` | def test_merger_safe_serial_integration(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_integration_accepts_verified_fast_forward_source_after_transfer` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1378-1389` | def test_integration_accepts_verified_fast_forward_source_after_transfer(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_rejects_non_ancestor_candidate_base_before_apply` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1391-1432` | def test_merger_rejects_non_ancestor_candidate_base_before_apply(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_main_builder_handoff_is_idempotent_and_merges_through_qc` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1434-1505` | def test_main_builder_handoff_is_idempotent_and_merges_through_qc(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_main_builder_handoff_is_idempotent_and_merges_through_qc.fake_docker` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1488-1492` | def fake_docker(worktree, image, command, timeout=300, *, receipt_dir=None, receipt_context=None) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_main_builder_qualifies_five_independent_candidates_serially` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1507-1587` | def test_main_builder_qualifies_five_independent_candidates_serially(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_main_builder_qualifies_five_independent_candidates_serially.fake_docker` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1545-1549` | def fake_docker(worktree, image, command, timeout=300, *, receipt_dir=None, receipt_context=None) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_candidate_diff_validation_rejects_base_mismatch_and_scope_escape` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1589-1600` | def test_candidate_diff_validation_rejects_base_mismatch_and_scope_escape(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_project_approval_moves_candidate_to_serial_merge_queue` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1602-1613` | def test_project_approval_moves_candidate_to_serial_merge_queue(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_rejection_fails_task_and_preserves_rebuild_queue` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1615-1640` | def test_merger_rejection_fails_task_and_preserves_rebuild_queue(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_merger_rejects_candidate_trailing_whitespace_before_apply` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1642-1662` | def test_merger_rejects_candidate_trailing_whitespace_before_apply(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_integration_rejects_worktree_from_different_repository` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1664-1670` | def test_integration_rejects_worktree_from_different_repository(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_architecture_change_invalidates_old_queued_tasks` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1672-1680` | def test_architecture_change_invalidates_old_queued_tasks(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1682-1720` | def test_full_codex_pipeline_mocked_five_tasks(self) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks.fake_docker_test` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1700-1704` | def fake_docker_test(worktree, image, command, timeout=300, *, receipt_dir=None, receipt_context=None) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repeated_worker_failure_stops_before_retry_ceiling` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1722-1741` | def test_repeated_worker_failure_stops_before_retry_ceiling(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repeated_worker_failure_stops_before_retry_ceiling.fake_execute` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1725-1728` | def fake_execute(state, item, **kwargs) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_failed_candidate_is_quarantined_and_retry_preserves_error_proof` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1743-1790` | def test_failed_candidate_is_quarantined_and_retry_preserves_error_proof(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_master_refuses_before_claim_when_sandbox_unavailable` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1792-1799` | def test_master_refuses_before_claim_when_sandbox_unavailable(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_danger_bypass_refuses_live_state` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1801-1806` | def test_danger_bypass_refuses_live_state(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_worker_failure_can_recover_on_bounded_repair` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1808-1826` | def test_worker_failure_can_recover_on_bounded_repair(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_worker_failure_can_recover_on_bounded_repair.fake_execute` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1811-1817` | def fake_execute(state, item, **kwargs) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_review_category_reaches_bounded_repair_prompt` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1828-1845` | def test_review_category_reaches_bounded_repair_prompt(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_review_category_reaches_bounded_repair_prompt.fake_execute` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1831-1838` | def fake_execute(state, item, **kwargs) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repair_budget_can_drain_all_kickoff_tasks` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1847-1869` | def test_repair_budget_can_drain_all_kickoff_tasks(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_repair_budget_can_drain_all_kickoff_tasks.fake_execute` | function | `bootstrap/astra-one/tests/test_linux_sda.py:1850-1859` | def fake_execute(state, item, **kwargs) | 2 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_event_metadata_accepts_new_rebuild_branch_policy` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1871-1881` | def test_event_metadata_accepts_new_rebuild_branch_policy(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_event_metadata_rejects_unsafe_branch_prefix` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1883-1889` | def test_event_metadata_rejects_unsafe_branch_prefix(self) | 1 | legacy-bootstrap |
| `test_linux_sda.LinuxSDATests.test_event_metadata_schema` | method | `bootstrap/astra-one/tests/test_linux_sda.py:1891-1900` | def test_event_metadata_schema(self) | 2 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests` | class | `bootstrap/astra-one/tests/test_owner_approval.py:16-97` | class OwnerApprovalTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.setUp` | method | `bootstrap/astra-one/tests/test_owner_approval.py:17-57` | def setUp(self) | 35 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.tearDown` | method | `bootstrap/astra-one/tests/test_owner_approval.py:59-60` | def tearDown(self) | 12 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.test_signed_receipt_verifies_and_binds_expected_fields` | method | `bootstrap/astra-one/tests/test_owner_approval.py:62-69` | def test_signed_receipt_verifies_and_binds_expected_fields(self) | 1 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.test_tampered_receipt_is_rejected` | method | `bootstrap/astra-one/tests/test_owner_approval.py:71-77` | def test_tampered_receipt_is_rejected(self) | 1 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.test_changed_trusted_signer_file_is_rejected` | method | `bootstrap/astra-one/tests/test_owner_approval.py:79-83` | def test_changed_trusted_signer_file_is_rejected(self) | 1 | legacy-bootstrap |
| `test_owner_approval.OwnerApprovalTests.test_receipt_symlink_and_weak_modes_are_rejected` | method | `bootstrap/astra-one/tests/test_owner_approval.py:85-97` | def test_receipt_symlink_and_weak_modes_are_rejected(self) | 1 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests` | class | `bootstrap/astra-one/tests/test_owner_approval_state.py:14-133` | class OwnerApprovalStateTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests.setUp` | method | `bootstrap/astra-one/tests/test_owner_approval_state.py:15-86` | def setUp(self) | 35 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests.tearDown` | method | `bootstrap/astra-one/tests/test_owner_approval_state.py:88-89` | def tearDown(self) | 12 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests.test_master_records_owner_and_three_child_receipts` | method | `bootstrap/astra-one/tests/test_owner_approval_state.py:91-102` | def test_master_records_owner_and_three_child_receipts(self) | 1 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests.test_cli_request_and_approval_commands` | method | `bootstrap/astra-one/tests/test_owner_approval_state.py:104-127` | def test_cli_request_and_approval_commands(self) | 1 | legacy-bootstrap |
| `test_owner_approval_state.OwnerApprovalStateTests.test_missing_owner_receipt_does_not_change_state` | method | `bootstrap/astra-one/tests/test_owner_approval_state.py:129-133` | def test_missing_owner_receipt_does_not_change_state(self) | 1 | legacy-bootstrap |
| `test_scope_amendment.git_repo` | function | `bootstrap/astra-one/tests/test_scope_amendment.py:16-29` | def git_repo(root: Path) -> Path | 5 | legacy-bootstrap |
| `test_scope_amendment.TwsScopeAmendmentTests` | class | `bootstrap/astra-one/tests/test_scope_amendment.py:32-226` | class TwsScopeAmendmentTests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_scope_amendment.TwsScopeAmendmentTests.setUp` | method | `bootstrap/astra-one/tests/test_scope_amendment.py:33-121` | def setUp(self) | 35 | legacy-bootstrap |
| `test_scope_amendment.TwsScopeAmendmentTests.tearDown` | method | `bootstrap/astra-one/tests/test_scope_amendment.py:123-124` | def tearDown(self) | 12 | legacy-bootstrap |
| `test_scope_amendment.TwsScopeAmendmentTests.amendment` | method | `bootstrap/astra-one/tests/test_scope_amendment.py:126-198` | def amendment(self) -> dict | 2 | legacy-bootstrap |
| `test_scope_amendment.TwsScopeAmendmentTests.test_scope_amendment_is_validated_applied_and_idempotent` | method | `bootstrap/astra-one/tests/test_scope_amendment.py:200-226` | def test_scope_amendment_is_validated_applied_and_idempotent(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.git_repo` | function | `bootstrap/astra-one/tests/test_supervisor_v3.py:15-42` | def git_repo(root: Path) -> Path | 5 | legacy-bootstrap |
| `test_supervisor_v3.plan` | function | `bootstrap/astra-one/tests/test_supervisor_v3.py:45-76` | def plan() -> FullPlan | 7 | legacy-bootstrap |
| `test_supervisor_v3.bound_receipts` | function | `bootstrap/astra-one/tests/test_supervisor_v3.py:79-113` | def bound_receipts(state: State, task_id: str, run_id: str, attempt: int, source_sha: str, changed_files: list[str], candidate_sha: str, contract_sha: str, child_evidence: list[dic | 2 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests` | class | `bootstrap/astra-one/tests/test_supervisor_v3.py:116-1000` | class SupervisorV3Tests(unittest.TestCase) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.setUp` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:117-131` | def setUp(self) | 35 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.tearDown` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:133-134` | def tearDown(self) | 12 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_child_completion_requires_candidate_bound_receipts` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:136-171` | def test_child_completion_requires_candidate_bound_receipts(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_failure_taxonomy_and_case_lane_lease_are_durable` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:173-197` | def test_failure_taxonomy_and_case_lane_lease_are_durable(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_self_doctor_creates_one_scoped_proposal_across_generations` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:199-224` | def test_self_doctor_creates_one_scoped_proposal_across_generations(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_tick_resolves_historical_case_only_after_task_completion` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:226-242` | def test_tick_resolves_historical_case_only_after_task_completion(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_tick_releases_lane_when_recovery_finished_before_callback` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:244-261` | def test_tick_releases_lane_when_recovery_finished_before_callback(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_patch_applied_merger_checkpoint_resolves_recovery` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:263-332` | def test_patch_applied_merger_checkpoint_resolves_recovery(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_external_blocker_fences_task_without_recovery_generation` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:334-344` | def test_external_blocker_fences_task_without_recovery_generation(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_external_resolution_never_reopens_windows_without_device_evidence` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:346-351` | def test_external_resolution_never_reopens_windows_without_device_evidence(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_rel004_external_evidence_requires_real_profile_and_sanitized_linux_manifest` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:353-397` | def test_rel004_external_evidence_requires_real_profile_and_sanitized_linux_manifest(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_research_external_evidence_binds_report_and_limits` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:399-416` | def test_research_external_evidence_binds_report_and_limits(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_cloudflare_deployment_evidence_requires_read_only_health_and_schema` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:418-435` | def test_cloudflare_deployment_evidence_requires_read_only_health_and_schema(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_pending_jobs_evidence_requires_metadata_only_deployment` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:437-463` | def test_pending_jobs_evidence_requires_metadata_only_deployment(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_pending_jobs_resolution_accepts_required_no_secrets_attestation` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:465-500` | def test_pending_jobs_resolution_accepts_required_no_secrets_attestation(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_external_blocker_clears_stale_pending_claim_and_survives_refresh` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:502-525` | def test_external_blocker_clears_stale_pending_claim_and_survives_refresh(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_reopen_failed_readmits_stale_batch_member_without_erasing_case` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:527-553` | def test_reopen_failed_readmits_stale_batch_member_without_erasing_case(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_expired_recovery_lease_is_fenced_after_process_loss` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:555-576` | def test_expired_recovery_lease_is_fenced_after_process_loss(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_stale_worker_cannot_write_after_retry_generation_changes` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:578-588` | def test_stale_worker_cannot_write_after_retry_generation_changes(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_resolved_recovery_rejects_empty_unbound_candidate` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:590-606` | def test_resolved_recovery_rejects_empty_unbound_candidate(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_active_batch_excludes_members_from_a_second_batch` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:608-612` | def test_active_batch_excludes_members_from_a_second_batch(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_upgrade_candidate_without_tests_is_rejected` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:614-623` | def test_upgrade_candidate_without_tests_is_rejected(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_batch_and_upgrade_checkpoints_are_not_model_authority` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:625-643` | def test_batch_and_upgrade_checkpoints_are_not_model_authority(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_github_free_plan_amendment_is_sha_bound_and_idempotent` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:645-688` | def test_github_free_plan_amendment_is_sha_bound_and_idempotent(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_mig010_single_builder_amendment_releases_obsolete_blocker` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:690-750` | def test_mig010_single_builder_amendment_releases_obsolete_blocker(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_rel003_single_builder_amendment_updates_pending_task_idempotently` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:752-816` | def test_rel003_single_builder_amendment_updates_pending_task_idempotently(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_rel016_packaging_amendment_expands_scope_and_releases_quota_blocker` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:818-891` | def test_rel016_packaging_amendment_expands_scope_and_releases_quota_blocker(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_linux_platform_amendment_preserves_windows_requirement_and_releases_root` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:893-955` | def test_linux_platform_amendment_preserves_windows_requirement_and_releases_root(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_tws_blender_evidence_is_artifact_bound_and_device_honest` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:957-976` | def test_tws_blender_evidence_is_artifact_bound_and_device_honest(self) | 1 | legacy-bootstrap |
| `test_supervisor_v3.SupervisorV3Tests.test_tws_motion_review_requires_approved_bound_manifest` | method | `bootstrap/astra-one/tests/test_supervisor_v3.py:978-1000` | def test_tws_motion_review_requires_approved_bound_manifest(self) | 1 | legacy-bootstrap |
| `cloudflare.dashboard_worker.json` | function | `infra/cloudflare/dashboard_worker.js:22-22` | function json(data, status = 200) { | 44 | active |
| `cloudflare.dashboard_worker.equal` | function | `infra/cloudflare/dashboard_worker.js:26-26` | function equal(a, b) { | 5 | active |
| `cloudflare.dashboard_worker.authorized` | function | `infra/cloudflare/dashboard_worker.js:36-36` | function authorized(request, token) { | 4 | active |
| `cloudflare.dashboard_worker.taskId` | function | `infra/cloudflare/dashboard_worker.js:40-40` | function taskId(path) { | 0 | active |
| `cloudflare.dashboard_worker.publicSummary` | function | `infra/cloudflare/dashboard_worker.js:46-46` | function publicSummary(rows) { | 0 | active |
| `cloudflare.dashboard_worker.taskEvidence` | function | `infra/cloudflare/dashboard_worker.js:57-57` | function taskEvidence(run, events) { | 0 | active |
| `cloudflare.dashboard_worker.privateRuns` | function | `infra/cloudflare/dashboard_worker.js:73-73` | async function privateRuns(env) { | 0 | active |
| `cloudflare.dashboard_worker.privateTask` | function | `infra/cloudflare/dashboard_worker.js:80-80` | async function privateTask(env, id) { | 0 | active |
| `cloudflare.heartbeat_worker.json` | function | `infra/cloudflare/heartbeat_worker.js:13-13` | function json(data, status = 200) { | 44 | active |
| `cloudflare.heartbeat_worker.equal` | function | `infra/cloudflare/heartbeat_worker.js:17-17` | function equal(a, b) { | 5 | active |
| `cloudflare.heartbeat_worker.authorized` | function | `infra/cloudflare/heartbeat_worker.js:27-27` | function authorized(request, token) { | 4 | active |
| `cloudflare.heartbeat_worker.clock` | function | `infra/cloudflare/heartbeat_worker.js:31-31` | function clock(env) { | 24 | active |
| `cloudflare.heartbeat_worker.timeout` | function | `infra/cloudflare/heartbeat_worker.js:35-35` | function timeout(env) { | 16 | active |
| `cloudflare.heartbeat_worker.devicePath` | function | `infra/cloudflare/heartbeat_worker.js:41-41` | function devicePath(url) { | 0 | active |
| `cloudflare.heartbeat_worker.heartbeat` | function | `infra/cloudflare/heartbeat_worker.js:49-49` | async function heartbeat(request, env, deviceId, receivedAt) { | 5 | active |
| `cloudflare.heartbeat_worker.status` | function | `infra/cloudflare/heartbeat_worker.js:75-75` | async function status(env, deviceId, now, timeoutSeconds) { | 80 | active |
| `cloudflare.rate_limit.setting` | function | `infra/cloudflare/rate_limit.js:4-4` | function setting(value, fallback, maximum) { | 0 | active |
| `cloudflare.rate_limit.digest` | function | `infra/cloudflare/rate_limit.js:9-9` | async function digest(value) { | 17 | active |
| `cloudflare.rate_limit.allowRequest` | function | `infra/cloudflare/rate_limit.js:14-14` | async function allowRequest(request, env, scope) { | 1 | active |
| `verify_installation.InstallationManifestError` | class | `infra/verify_installation.py:27-28` | class InstallationManifestError(ValueError) | 0 | active |
| `verify_installation._relative_file` | function | `infra/verify_installation.py:31-46` | def _relative_file(value: object, *, root: Path, label: str) -> Path | 0 | active |
| `verify_installation._bounded_string` | function | `infra/verify_installation.py:49-52` | def _bounded_string(value: object, label: str) -> str | 0 | active |
| `verify_installation.validate_manifest` | function | `infra/verify_installation.py:55-113` | def validate_manifest(root: Path=ROOT) -> dict[str, Any] | 1 | active |
| `verify_installation._tool_presence` | function | `infra/verify_installation.py:116-125` | def _tool_presence(platform: dict[str, Any]) -> dict[str, bool] | 0 | active |
| `verify_installation.main` | function | `infra/verify_installation.py:128-154` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `adapters.legacy_contracts.MigrationCompatibilityError` | class | `migration/adapters/legacy_contracts.py:61-62` | class MigrationCompatibilityError(ValueError) | 1 | active |
| `adapters.legacy_contracts.ContractRecord` | class | `migration/adapters/legacy_contracts.py:66-86` | class ContractRecord() | 0 | active |
| `adapters.legacy_contracts.ContractRecord.as_dict` | method | `migration/adapters/legacy_contracts.py:77-86` | def as_dict(self) -> dict[str, object] | 18 | active |
| `adapters.legacy_contracts._within` | function | `migration/adapters/legacy_contracts.py:89-98` | def _within(root: Path, value: str, label: str) -> Path | 0 | active |
| `adapters.legacy_contracts.LegacyContractAdapter` | class | `migration/adapters/legacy_contracts.py:101-187` | class LegacyContractAdapter() | 1 | active |
| `adapters.legacy_contracts.LegacyContractAdapter.__init__` | method | `migration/adapters/legacy_contracts.py:104-112` | def __init__(self, repository: str \| Path, import_log: str \| Path \| None=None) -> None | 5 | active |
| `adapters.legacy_contracts.LegacyContractAdapter._records` | method | `migration/adapters/legacy_contracts.py:114-155` | def _records(self) -> list[ContractRecord] | 0 | active |
| `adapters.legacy_contracts.LegacyContractAdapter.snapshot` | method | `migration/adapters/legacy_contracts.py:157-187` | def snapshot(self) -> dict[str, Any] | 17 | active |
| `index.nowSeconds` | function | `migration/imported/automation/cloudflare/src/index.ts:57-57` | function nowSeconds(): number { | 0 | legacy-imported |
| `index.jsonResponse` | function | `migration/imported/automation/cloudflare/src/index.ts:61-61` | function jsonResponse(body: unknown, status = 200): Response { | 0 | legacy-imported |
| `index.asObject` | function | `migration/imported/automation/cloudflare/src/index.ts:113-113` | function asObject(value: unknown, field = "body"): JsonObject { | 0 | legacy-imported |
| `index.jsonText` | function | `migration/imported/automation/cloudflare/src/index.ts:120-120` | function jsonText(value: unknown, field: string, maximumBytes: number): string { | 0 | legacy-imported |
| `index.parseStoredJson` | function | `migration/imported/automation/cloudflare/src/index.ts:136-136` | function parseStoredJson(value: string \| null): unknown { | 0 | legacy-imported |
| `index.publicJob` | function | `migration/imported/automation/cloudflare/src/index.ts:145-145` | function publicJob(row: JobRow): Record<string, unknown> { | 0 | legacy-imported |
| `index.publicWorker` | function | `migration/imported/automation/cloudflare/src/index.ts:168-168` | function publicWorker(row: WorkerRow): Record<string, unknown> { | 0 | legacy-imported |
| `index.readJson` | function | `migration/imported/automation/cloudflare/src/index.ts:179-179` | async function readJson(request: Request): Promise<JsonObject> { | 0 | legacy-imported |
| `index.isAuthorized` | function | `migration/imported/automation/cloudflare/src/index.ts:197-197` | function isAuthorized(request: Request, env: Env): boolean { | 0 | legacy-imported |
| `index.requeueExpiredLeases` | function | `migration/imported/automation/cloudflare/src/index.ts:213-213` | async function requeueExpiredLeases(env: Env, now: number): Promise<void> { | 0 | legacy-imported |
| `index.registerWorker` | function | `migration/imported/automation/cloudflare/src/index.ts:230-230` | async function registerWorker(request: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `index.heartbeatWorker` | function | `migration/imported/automation/cloudflare/src/index.ts:256-256` | async function heartbeatWorker(request: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `index.enqueueJob` | function | `migration/imported/automation/cloudflare/src/index.ts:274-274` | async function enqueueJob(request: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `index.leaseJob` | function | `migration/imported/automation/cloudflare/src/index.ts:320-320` | async function leaseJob(request: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `index.heartbeatJob` | function | `migration/imported/automation/cloudflare/src/index.ts:367-367` | async function heartbeatJob(request: Request, env: Env, pathJobId?: string): Promise<Response> { | 0 | legacy-imported |
| `index.completeJob` | function | `migration/imported/automation/cloudflare/src/index.ts:396-396` | async function completeJob(request: Request, env: Env, pathJobId?: string): Promise<Response> { | 0 | legacy-imported |
| `index.failJob` | function | `migration/imported/automation/cloudflare/src/index.ts:421-421` | async function failJob(request: Request, env: Env, pathJobId?: string): Promise<Response> { | 0 | legacy-imported |
| `index.stats` | function | `migration/imported/automation/cloudflare/src/index.ts:453-453` | async function stats(env: Env): Promise<Response> { | 2 | legacy-imported |
| `index.maintenance` | function | `migration/imported/automation/cloudflare/src/index.ts:461-461` | async function maintenance(env: Env): Promise<void> { | 0 | legacy-imported |
| `index.handleRequest` | function | `migration/imported/automation/cloudflare/src/index.ts:482-482` | async function handleRequest(request: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.bounded_int` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:57-63` | def bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.bounded_float` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:66-72` | def bounded_float(value: Any, default: float, minimum: float, maximum: float) -> float | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.normalize_url` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:75-76` | def normalize_url(value: str) -> str | 1 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.make_worker_id` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:79-82` | def make_worker_id() -> str | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.require_environment` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:85-89` | def require_environment(name: str) -> str | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.json_bytes` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:92-93` | def json_bytes(value: Any) -> bytes | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.error_text` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:96-98` | def error_text(exc: BaseException) -> str | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.extract_job` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:101-116` | def extract_job(response: Dict[str, Any]) -> Optional[Dict[str, Any]] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.job_payload` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:119-125` | def job_payload(job: Dict[str, Any]) -> Dict[str, Any] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.build_ollama_request` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:128-167` | def build_ollama_request(job: Dict[str, Any], default_model: str=DEFAULT_MODEL, num_predict: int=DEFAULT_NUM_PREDICT, num_ctx: int=DEFAULT_NUM_CTX) -> Tuple[str, Dict[str, Any]] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.extract_ollama_result` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:170-194` | def extract_ollama_result(response: Dict[str, Any]) -> Dict[str, Any] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.Settings` | class | `migration/imported/automation/windows/jarvis_queue_worker.py:198-257` | class Settings() | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.Settings.from_environment` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:212-257` | def from_environment(cls) -> 'Settings' | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.HttpError` | class | `migration/imported/automation/windows/jarvis_queue_worker.py:260-261` | class HttpError(RuntimeError) | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient` | class | `migration/imported/automation/windows/jarvis_queue_worker.py:264-387` | class CoordinatorClient() | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.__init__` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:265-266` | def __init__(self, settings: Settings) | 5 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.request` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:268-310` | def request(self, method: str, path: str, body: Optional[Dict[str, Any]]=None, timeout: Optional[float]=None) -> Dict[str, Any] | 23 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.register` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:312-328` | def register(self) -> Dict[str, Any] | 1 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.heartbeat` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:330-340` | def heartbeat(self, current_job_id: Optional[str]) -> Dict[str, Any] | 5 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.lease` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:342-352` | def lease(self) -> Optional[Dict[str, Any]] | 17 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.job_heartbeat` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:354-364` | def job_heartbeat(self, job: Dict[str, Any]) -> Dict[str, Any] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.complete` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:366-375` | def complete(self, job: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any] | 9 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.CoordinatorClient.fail` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:377-387` | def fail(self, job: Dict[str, Any], message: str, retryable: bool=True) -> Dict[str, Any] | 4 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.OllamaClient` | class | `migration/imported/automation/windows/jarvis_queue_worker.py:390-427` | class OllamaClient() | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.OllamaClient.__init__` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:391-392` | def __init__(self, settings: Settings) | 5 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.OllamaClient.generate` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:394-427` | def generate(self, job: Dict[str, Any]) -> Dict[str, Any] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker` | class | `migration/imported/automation/windows/jarvis_queue_worker.py:430-529` | class QueueWorker() | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.__init__` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:431-437` | def __init__(self, settings: Settings) | 5 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.set_current_job` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:439-441` | def set_current_job(self, job_id: Optional[str]) -> None | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.get_current_job` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:443-445` | def get_current_job(self) -> Optional[str] | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.heartbeat_loop` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:447-462` | def heartbeat_loop(self) -> None | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.start_heartbeat` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:464-471` | def start_heartbeat(self) -> threading.Thread | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.process_job` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:473-499` | def process_job(self, job: Dict[str, Any]) -> None | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.run_once` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:501-507` | def run_once(self) -> bool | 1 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.run_forever` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:509-526` | def run_forever(self) -> None | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.QueueWorker.stop` | method | `migration/imported/automation/windows/jarvis_queue_worker.py:528-529` | def stop(self) -> None | 4 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.parse_args` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:532-544` | def parse_args() -> argparse.Namespace | 0 | legacy-imported |
| `imported.automation.windows.jarvis_queue_worker.main` | function | `migration/imported/automation/windows/jarvis_queue_worker.py:547-563` | def main() -> int | 155 | legacy-imported |
| `imported.backend.colibri.ColibriConfig` | class | `migration/imported/backend/colibri.py:21-56` | class ColibriConfig() | 0 | legacy-imported |
| `imported.backend.colibri.ColibriConfig.__post_init__` | method | `migration/imported/backend/colibri.py:30-56` | def __post_init__(self) -> None | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient` | class | `migration/imported/backend/colibri.py:59-239` | class ColibriClient() | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.__init__` | method | `migration/imported/backend/colibri.py:60-61` | def __init__(self, config: ColibriConfig \| None=None) -> None | 5 | legacy-imported |
| `imported.backend.colibri.ColibriClient._bounded_message` | method | `migration/imported/backend/colibri.py:63-73` | def _bounded_message(self, message: str) -> str | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.models` | method | `migration/imported/backend/colibri.py:75-80` | def models(self) -> list[dict] | 1 | legacy-imported |
| `imported.backend.colibri.ColibriClient.status` | method | `migration/imported/backend/colibri.py:82-98` | def status(self) -> dict | 80 | legacy-imported |
| `imported.backend.colibri.ColibriClient.warmup` | method | `migration/imported/backend/colibri.py:100-104` | def warmup(self) -> dict | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.complete` | method | `migration/imported/backend/colibri.py:106-137` | def complete(self, message: str, model: str \| None=None) -> dict | 9 | legacy-imported |
| `imported.backend.colibri.ColibriClient.complete_async` | method | `migration/imported/backend/colibri.py:139-156` | async def complete_async(self, message: str, model: str \| None=None) -> dict | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.complete_stream` | method | `migration/imported/backend/colibri.py:158-187` | def complete_stream(self, message: str, model: str \| None=None) -> Iterator[dict[str, str]] | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient._available_model` | method | `migration/imported/backend/colibri.py:189-197` | def _available_model(self, requested: str \| None) -> str | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.complete_stream_async` | method | `migration/imported/backend/colibri.py:199-239` | async def complete_stream_async(self, message: str, model: str \| None=None) -> AsyncIterator[dict[str, str]] | 0 | legacy-imported |
| `imported.backend.colibri.ColibriClient.complete_stream_async.next_delta` | function | `migration/imported/backend/colibri.py:210-214` | def next_delta() -> tuple[bool, dict[str, str] \| None] | 0 | legacy-imported |
| `imported.backend.colibri.cli_status` | function | `migration/imported/backend/colibri.py:242-252` | def cli_status(config: ColibriConfig \| None=None) -> dict | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalError` | class | `migration/imported/backend/permissions.py:19-20` | class ApprovalError(Exception) | 0 | legacy-imported |
| `imported.backend.permissions.FileIdentity` | class | `migration/imported/backend/permissions.py:24-53` | class FileIdentity() | 0 | legacy-imported |
| `imported.backend.permissions.FileIdentity.capture` | method | `migration/imported/backend/permissions.py:32-37` | def capture(cls, target: Path) -> FileIdentity | 0 | legacy-imported |
| `imported.backend.permissions.FileIdentity.matches` | method | `migration/imported/backend/permissions.py:39-49` | def matches(self) -> bool | 0 | legacy-imported |
| `imported.backend.permissions.FileIdentity.digest` | method | `migration/imported/backend/permissions.py:51-53` | def digest(self) -> str | 17 | legacy-imported |
| `imported.backend.permissions.ApprovalRequest` | class | `migration/imported/backend/permissions.py:57-62` | class ApprovalRequest() | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker` | class | `migration/imported/backend/permissions.py:65-504` | class ApprovalBroker() | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker._validate_request_id` | method | `migration/imported/backend/permissions.py:73-77` | def _validate_request_id(cls, request_id: object) -> str | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.__init__` | method | `migration/imported/backend/permissions.py:79-120` | def __init__(self, db_path: Path, ttl: int=300, clock=time.time, trash_root: Path \| None=None) -> None | 5 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.propose` | method | `migration/imported/backend/permissions.py:122-142` | def propose(self, target: Path, action: str, reason: str) -> ApprovalRequest | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker._validate_reason` | method | `migration/imported/backend/permissions.py:145-154` | def _validate_reason(cls, reason: object) -> str | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.propose_directory` | method | `migration/imported/backend/permissions.py:156-162` | def propose_directory(self, target: Path, action: str, reason: str) -> None | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.decide` | method | `migration/imported/backend/permissions.py:164-182` | def decide(self, request_id: str, approved: bool) -> None | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.authorize_execution` | method | `migration/imported/backend/permissions.py:184-201` | def authorize_execution(self, request_id: str) -> ApprovalRequest | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.trash_file` | method | `migration/imported/backend/permissions.py:203-282` | def trash_file(self, request_id: str) -> Path | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.execute_trash_file` | method | `migration/imported/backend/permissions.py:284-290` | def execute_trash_file(self, request_id: str) -> tuple[ApprovalRequest, Path] | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker._rename_noreplace` | method | `migration/imported/backend/permissions.py:293-316` | def _rename_noreplace(source_dir_fd: int, source_name: str, target_dir_fd: int, target_name: str) -> None | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.verified_file` | method | `migration/imported/backend/permissions.py:319-361` | def verified_file(self, request_id: str) | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker._checksum_fd` | method | `migration/imported/backend/permissions.py:364-378` | def _checksum_fd(directory_fd: int \| Path, name: str) -> str | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.trash_manifest` | method | `migration/imported/backend/permissions.py:380-388` | def trash_manifest(self, request_id: str) -> dict[str, object] \| None | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.propose_restore` | method | `migration/imported/backend/permissions.py:390-406` | def propose_restore(self, request_id: str, reason: str) -> ApprovalRequest | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.restore_file` | method | `migration/imported/backend/permissions.py:408-467` | def restore_file(self, request_id: str) -> Path | 1 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.audit` | method | `migration/imported/backend/permissions.py:469-484` | def audit(self, limit: int=100) -> list[dict[str, object]] | 6 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker.emergency_stop` | method | `migration/imported/backend/permissions.py:486-496` | def emergency_stop(self) -> int | 0 | legacy-imported |
| `imported.backend.permissions.ApprovalBroker._audit` | method | `migration/imported/backend/permissions.py:498-504` | def _audit(self, request: ApprovalRequest, decision: str, result: str) -> None | 0 | legacy-imported |
| `imported.backend.router.RouterConfig` | class | `migration/imported/backend/router.py:21-22` | class RouterConfig() | 0 | legacy-imported |
| `imported.backend.router.RouterTelemetry` | class | `migration/imported/backend/router.py:26-37` | class RouterTelemetry() | 0 | legacy-imported |
| `imported.backend.router.RouterTelemetry.snapshot` | method | `migration/imported/backend/router.py:33-37` | def snapshot(self) -> dict[str, Any] | 17 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter` | class | `migration/imported/backend/router.py:40-89` | class ResourceAwareRouter() | 0 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter.__init__` | method | `migration/imported/backend/router.py:43-50` | def __init__(self, client: ColibriClient \| None=None, config: RouterConfig \| None=None) -> None | 5 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter.is_heavy` | method | `migration/imported/backend/router.py:53-54` | def is_heavy(model: str) -> bool | 0 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter.choose_model` | method | `migration/imported/backend/router.py:56-63` | def choose_model(self, requested: str \| None=None) -> str | 0 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter.complete` | method | `migration/imported/backend/router.py:65-82` | async def complete(self, message: str, model: str \| None=None) -> dict | 9 | legacy-imported |
| `imported.backend.router.ResourceAwareRouter.status` | method | `migration/imported/backend/router.py:84-89` | def status(self) -> dict[str, Any] | 80 | legacy-imported |
| `imported.backend.router._NullAsyncLock` | class | `migration/imported/backend/router.py:92-97` | class _NullAsyncLock() | 0 | legacy-imported |
| `imported.backend.router._NullAsyncLock.__aenter__` | method | `migration/imported/backend/router.py:93-94` | async def __aenter__(self) -> '_NullAsyncLock' | 0 | legacy-imported |
| `imported.backend.router._NullAsyncLock.__aexit__` | method | `migration/imported/backend/router.py:96-97` | async def __aexit__(self, *_: object) -> None | 0 | legacy-imported |
| `imported.backend.storage.prepare_path` | function | `migration/imported/backend/storage.py:12-17` | def prepare_path(path: Path) -> None | 0 | legacy-imported |
| `imported.backend.storage.connect` | function | `migration/imported/backend/storage.py:21-38` | def connect(path: Path) -> Iterator[sqlite3.Connection] | 13 | legacy-imported |
| `imported.backend.storage.ensure_schema` | function | `migration/imported/backend/storage.py:41-139` | def ensure_schema(path: Path) -> None | 1 | legacy-imported |
| `imported.core.tasks.Task` | class | `migration/imported/core/tasks.py:21-28` | class Task() | 2 | legacy-imported |
| `imported.core.tasks.TaskStore` | class | `migration/imported/core/tasks.py:31-127` | class TaskStore() | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.__init__` | method | `migration/imported/core/tasks.py:32-34` | def __init__(self, path: Path) -> None | 5 | legacy-imported |
| `imported.core.tasks.TaskStore._row` | method | `migration/imported/core/tasks.py:37-39` | def _row(row) -> Task | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.create` | method | `migration/imported/core/tasks.py:41-53` | def create(self, kind: str, payload: dict, idempotency_key: str) -> Task | 8 | legacy-imported |
| `imported.core.tasks.TaskStore._event` | method | `migration/imported/core/tasks.py:56-58` | def _event(db, task_id: str, state: str, detail: str) -> None | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.get` | method | `migration/imported/core/tasks.py:60-65` | def get(self, task_id: str) -> Task | 27 | legacy-imported |
| `imported.core.tasks.TaskStore.transition` | method | `migration/imported/core/tasks.py:67-79` | def transition(self, task_id: str, state: str, *, result: dict \| None=None, error: str \| None=None) -> Task | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.list` | method | `migration/imported/core/tasks.py:81-95` | def list(self, limit: int=50, query: str='') -> list[Task] | 13 | legacy-imported |
| `imported.core.tasks.TaskStore.events_since` | method | `migration/imported/core/tasks.py:97-103` | def events_since(self, event_id: int=0, limit: int=100) -> list[dict] | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.events_for` | method | `migration/imported/core/tasks.py:105-114` | def events_for(self, task_id: str, limit: int=50) -> list[dict] | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.cancel` | method | `migration/imported/core/tasks.py:116-117` | def cancel(self, task_id: str) -> Task | 0 | legacy-imported |
| `imported.core.tasks.TaskStore.recover_running` | method | `migration/imported/core/tasks.py:119-127` | def recover_running(self) -> int | 0 | legacy-imported |
| `imported.core.worker.ToolSpec` | class | `migration/imported/core/worker.py:21-26` | class ToolSpec() | 0 | legacy-imported |
| `imported.core.worker.WorkerDispatcher` | class | `migration/imported/core/worker.py:29-87` | class WorkerDispatcher() | 0 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.__init__` | method | `migration/imported/core/worker.py:30-33` | def __init__(self, tasks: TaskStore) -> None | 5 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.register` | method | `migration/imported/core/worker.py:35-40` | def register(self, spec: ToolSpec) -> None | 1 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.registered` | method | `migration/imported/core/worker.py:42-43` | def registered(self) -> tuple[str, ...] | 0 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.spec` | method | `migration/imported/core/worker.py:45-46` | def spec(self, kind: str) -> ToolSpec \| None | 13 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.validate` | method | `migration/imported/core/worker.py:48-54` | def validate(self, kind: str, payload: dict[str, Any]) -> dict[str, Any] | 2 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.run` | method | `migration/imported/core/worker.py:56-80` | async def run(self, task_id: str) -> Task | 36 | legacy-imported |
| `imported.core.worker.WorkerDispatcher.cancel` | method | `migration/imported/core/worker.py:82-87` | def cancel(self, task_id: str) -> bool | 0 | legacy-imported |
| `imported.core.worker.inventory_scan_tool` | function | `migration/imported/core/worker.py:90-101` | async def inventory_scan_tool(payload: dict[str, Any], cancel: asyncio.Event) -> dict[str, Any] | 0 | legacy-imported |
| `imported.core.worker.validate_inventory_scan` | function | `migration/imported/core/worker.py:104-117` | def validate_inventory_scan(payload: dict[str, Any]) -> dict[str, Any] | 0 | legacy-imported |
| `imported.core.worker.default_dispatcher` | function | `migration/imported/core/worker.py:120-123` | def default_dispatcher(tasks: TaskStore) -> WorkerDispatcher | 0 | legacy-imported |
| `imported.guardian.sda_module_integrity.IntegrityError` | class | `migration/imported/guardian/sda_module_integrity.py:24-25` | class IntegrityError(ValueError) | 0 | legacy-imported |
| `imported.guardian.sda_module_integrity._id` | function | `migration/imported/guardian/sda_module_integrity.py:28-31` | def _id(value: object, field: str) -> str | 0 | legacy-imported |
| `imported.guardian.sda_module_integrity._bool` | function | `migration/imported/guardian/sda_module_integrity.py:34-37` | def _bool(value: object, field: str) -> bool | 0 | legacy-imported |
| `imported.guardian.sda_module_integrity.plan` | function | `migration/imported/guardian/sda_module_integrity.py:40-176` | def plan(state: dict) -> dict | 7 | legacy-imported |
| `imported.guardian.sda_module_integrity.main` | function | `migration/imported/guardian/sda_module_integrity.py:179-198` | def main() -> int | 155 | legacy-imported |
| `imported.guardian.sda_recovery_triage._load_script` | function | `migration/imported/guardian/sda_recovery_triage.py:32-38` | def _load_script(filename: str) | 0 | legacy-imported |
| `imported.guardian.sda_recovery_triage.plan` | function | `migration/imported/guardian/sda_recovery_triage.py:41-113` | def plan(doctor: dict, checkpoint: dict \| None=None, *, limit: int=8) -> dict | 7 | legacy-imported |
| `imported.guardian.sda_recovery_triage.main` | function | `migration/imported/guardian/sda_recovery_triage.py:116-131` | def main() -> int | 155 | legacy-imported |
| `imported.runtime.calendar.proposal_event_ids` | function | `migration/imported/runtime/calendar.py:13-15` | def proposal_event_ids(timezone_name: str) -> set[str] | 0 | legacy-imported |
| `imported.runtime.calendar.sample_calendar` | function | `migration/imported/runtime/calendar.py:18-38` | def sample_calendar(timezone_name: str='UTC') -> dict | 0 | legacy-imported |
| `imported.runtime.email.MailMessage` | class | `migration/imported/runtime/email.py:7-13` | class MailMessage() | 0 | legacy-imported |
| `imported.runtime.email.EmailProvider` | class | `migration/imported/runtime/email.py:15-19` | class EmailProvider(Protocol) | 0 | legacy-imported |
| `imported.runtime.email.EmailProvider.search` | method | `migration/imported/runtime/email.py:18-18` | def search(self, query: str) -> list[MailMessage] | 9 | legacy-imported |
| `imported.runtime.email.EmailProvider.send` | method | `migration/imported/runtime/email.py:19-19` | def send(self, recipient: str, subject: str, body: str) -> str | 3 | legacy-imported |
| `imported.runtime.email.SampleEmailProvider` | class | `migration/imported/runtime/email.py:21-33` | class SampleEmailProvider() | 0 | legacy-imported |
| `imported.runtime.email.SampleEmailProvider.__init__` | method | `migration/imported/runtime/email.py:24-26` | def __init__(self) -> None | 5 | legacy-imported |
| `imported.runtime.email.SampleEmailProvider.search` | method | `migration/imported/runtime/email.py:27-29` | def search(self, query: str) -> list[MailMessage] | 9 | legacy-imported |
| `imported.runtime.email.SampleEmailProvider.send` | method | `migration/imported/runtime/email.py:30-33` | def send(self, recipient: str, subject: str, body: str) -> str | 3 | legacy-imported |
| `imported.runtime.inventory.mounted_volumes` | function | `migration/imported/runtime/inventory.py:22-45` | def mounted_volumes(proc_mounts: Path=Path('/proc/mounts')) -> list[dict[str, object]] | 0 | legacy-imported |
| `imported.runtime.inventory._is_secret_name` | function | `migration/imported/runtime/inventory.py:48-50` | def _is_secret_name(name: str) -> bool | 0 | legacy-imported |
| `imported.runtime.inventory.FileRecord` | class | `migration/imported/runtime/inventory.py:54-59` | class FileRecord() | 0 | legacy-imported |
| `imported.runtime.inventory.is_allowed` | function | `migration/imported/runtime/inventory.py:62-73` | def is_allowed(path: Path) -> bool | 0 | legacy-imported |
| `imported.runtime.inventory.default_roots` | function | `migration/imported/runtime/inventory.py:76-85` | def default_roots() -> list[Path] | 0 | legacy-imported |
| `imported.runtime.inventory.configured_roots` | function | `migration/imported/runtime/inventory.py:88-101` | def configured_roots(db_path: Path) -> list[Path] | 0 | legacy-imported |
| `imported.runtime.inventory._open_git_metadata` | function | `migration/imported/runtime/inventory.py:104-122` | def _open_git_metadata(directory_fd: int) -> int | 0 | legacy-imported |
| `imported.runtime.inventory._git_branch` | function | `migration/imported/runtime/inventory.py:125-146` | def _git_branch(directory_fd: int) -> str | 0 | legacy-imported |
| `imported.runtime.inventory._git_checkpoint` | function | `migration/imported/runtime/inventory.py:149-183` | def _git_checkpoint(directory_fd: int) -> str | 0 | legacy-imported |
| `imported.runtime.inventory.discover_projects` | function | `migration/imported/runtime/inventory.py:186-296` | def discover_projects(db_path: Path, limit: int=100) -> list[dict[str, object]] | 0 | legacy-imported |
| `imported.runtime.inventory.add_configured_root` | function | `migration/imported/runtime/inventory.py:299-310` | def add_configured_root(path: Path, db_path: Path) -> Path | 0 | legacy-imported |
| `imported.runtime.inventory.scan` | function | `migration/imported/runtime/inventory.py:313-363` | def scan(roots: list[Path], limit: int=2000) -> tuple[list[FileRecord], bool] | 2 | legacy-imported |
| `imported.runtime.inventory.store` | function | `migration/imported/runtime/inventory.py:366-399` | def store(records: list[FileRecord], db_path: Path, roots: list[Path] \| None=None) -> int | 44 | legacy-imported |
| `imported.runtime.inventory.refresh` | function | `migration/imported/runtime/inventory.py:402-425` | def refresh(roots: list[Path], db_path: Path, *, limit: int=2000, now: float \| None=None) -> dict[str, object] | 0 | legacy-imported |
| `imported.runtime.inventory.refresh_status` | function | `migration/imported/runtime/inventory.py:428-433` | def refresh_status(db_path: Path) -> list[dict[str, object]] | 0 | legacy-imported |
| `imported.runtime.inventory.search` | function | `migration/imported/runtime/inventory.py:436-480` | def search(query: str, db_path: Path, limit: int=50) -> list[dict] | 9 | legacy-imported |
| `imported.runtime.inventory.duplicate_groups` | function | `migration/imported/runtime/inventory.py:483-501` | def duplicate_groups(db_path: Path, limit: int=50) -> list[dict[str, object]] | 0 | legacy-imported |
| `imported.runtime.inventory.verified_duplicate_groups` | function | `migration/imported/runtime/inventory.py:504-578` | def verified_duplicate_groups(db_path: Path, limit: int=50, max_file_bytes: int=64 * 1024 * 1024) -> list[dict[str, object]] | 0 | legacy-imported |
| `imported.runtime.inventory.cleanup_preview` | function | `migration/imported/runtime/inventory.py:581-592` | def cleanup_preview(db_path: Path, limit: int=50) -> dict[str, object] | 0 | legacy-imported |
| `imported.runtime.inventory.organization_preview` | function | `migration/imported/runtime/inventory.py:595-611` | def organization_preview(db_path: Path, limit: int=50) -> dict[str, object] | 0 | legacy-imported |
| `imported.runtime.server._action_form` | function | `migration/imported/runtime/server.py:49-67` | def _action_form(body: bytes, allowed: set[str], required: set[str]) -> dict[str, str] | 0 | legacy-imported |
| `imported.runtime.server._csrf_form` | function | `migration/imported/runtime/server.py:70-72` | def _csrf_form(body: bytes, fields: set[str]=frozenset()) -> dict[str, str] | 0 | legacy-imported |
| `imported.runtime.server._query` | function | `migration/imported/runtime/server.py:75-91` | def _query(target: str, allowed: set[str]) -> dict[str, str] | 0 | legacy-imported |
| `imported.runtime.server._opaque_path_id` | function | `migration/imported/runtime/server.py:94-98` | def _opaque_path_id(value: str, label: str) -> str | 0 | legacy-imported |
| `imported.runtime.server.init_db` | function | `migration/imported/runtime/server.py:101-103` | def init_db(path: Path \| None=None) -> None | 0 | legacy-imported |
| `imported.runtime.server.chat_history` | function | `migration/imported/runtime/server.py:106-117` | def chat_history(path: Path, limit: int=40) -> list[dict] | 0 | legacy-imported |
| `imported.runtime.server.save_chat_turn` | function | `migration/imported/runtime/server.py:120-135` | def save_chat_turn(path: Path, message: str, answer: dict) -> None | 0 | legacy-imported |
| `imported.runtime.server.home_summary` | function | `migration/imported/runtime/server.py:138-152` | def home_summary(app: 'App') -> dict | 0 | legacy-imported |
| `imported.runtime.server.voice_summary` | function | `migration/imported/runtime/server.py:155-173` | def voice_summary() -> dict | 0 | legacy-imported |
| `imported.runtime.server.calendar_summary` | function | `migration/imported/runtime/server.py:176-188` | def calendar_summary(app: 'App' \| None=None) -> dict | 0 | legacy-imported |
| `imported.runtime.server.calendar_proposals` | function | `migration/imported/runtime/server.py:191-199` | def calendar_proposals(path: Path) -> list[dict] | 0 | legacy-imported |
| `imported.runtime.server.email_drafts` | function | `migration/imported/runtime/server.py:202-207` | def email_drafts(path: Path \| None=None) -> list[dict] | 0 | legacy-imported |
| `imported.runtime.server.email_summary` | function | `migration/imported/runtime/server.py:210-221` | def email_summary(path: Path \| None=None) -> dict | 0 | legacy-imported |
| `imported.runtime.server.email_search` | function | `migration/imported/runtime/server.py:224-233` | def email_search(query: str='') -> dict | 0 | legacy-imported |
| `imported.runtime.server.email_draft_preview` | function | `migration/imported/runtime/server.py:236-257` | def email_draft_preview(fields: dict[str, str], path: Path \| None=None) -> dict | 0 | legacy-imported |
| `imported.runtime.server.probe_colibri` | function | `migration/imported/runtime/server.py:260-262` | def probe_colibri() -> dict | 0 | legacy-imported |
| `imported.runtime.server.page` | function | `migration/imported/runtime/server.py:265-352` | def page(route: str, csrf: str, csp_nonce: str='static-test-nonce') -> bytes | 6 | legacy-imported |
| `imported.runtime.server.App` | class | `migration/imported/runtime/server.py:355-1364` | class App() | 0 | legacy-imported |
| `imported.runtime.server.App.__init__` | method | `migration/imported/runtime/server.py:356-374` | def __init__(self) -> None | 5 | legacy-imported |
| `imported.runtime.server.App.owner_bootstrapped` | method | `migration/imported/runtime/server.py:377-380` | def owner_bootstrapped(self) -> bool | 0 | legacy-imported |
| `imported.runtime.server.App.issue_owner_session` | method | `migration/imported/runtime/server.py:382-391` | def issue_owner_session(self, token: str, now: float \| None=None) -> tuple[str, str] \| None | 1 | legacy-imported |
| `imported.runtime.server.App.rotate_session` | method | `migration/imported/runtime/server.py:393-403` | def rotate_session(self, session: str, now: float \| None=None) -> tuple[str, str] \| None | 0 | legacy-imported |
| `imported.runtime.server.App.session_csrf` | method | `migration/imported/runtime/server.py:405-413` | def session_csrf(self, session: str, now: float \| None=None) -> str \| None | 0 | legacy-imported |
| `imported.runtime.server.App.origin_allowed` | method | `migration/imported/runtime/server.py:416-418` | def origin_allowed(origin: str \| None) -> bool | 0 | legacy-imported |
| `imported.runtime.server.App.request_origin_allowed` | method | `migration/imported/runtime/server.py:421-433` | def request_origin_allowed(host: str, origin: str \| None) -> bool | 0 | legacy-imported |
| `imported.runtime.server.App.handle` | method | `migration/imported/runtime/server.py:435-1296` | async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None | 3 | legacy-imported |
| `imported.runtime.server.App.respond` | method | `migration/imported/runtime/server.py:1298-1323` | async def respond(self, writer: asyncio.StreamWriter, status: int, body: bytes, sid: str \| None=None, content_type: str='application/json', clear_cookie: bool=False, csp_nonce: st | 0 | legacy-imported |
| `imported.runtime.server.App._session_cookie` | method | `migration/imported/runtime/server.py:1326-1341` | def _session_cookie(header: str) -> str \| None | 0 | legacy-imported |
| `imported.runtime.server.App._sse_event` | method | `migration/imported/runtime/server.py:1344-1345` | def _sse_event(event: dict) -> str | 0 | legacy-imported |
| `imported.runtime.server.App._respond_stream_headers` | method | `migration/imported/runtime/server.py:1347-1356` | async def _respond_stream_headers(self, writer: asyncio.StreamWriter, sid: str) -> None | 0 | legacy-imported |
| `imported.runtime.server.App.task_json` | method | `migration/imported/runtime/server.py:1358-1364` | def task_json(self, task) -> dict | 0 | legacy-imported |
| `imported.runtime.server.run` | function | `migration/imported/runtime/server.py:1367-1369` | async def run() -> None | 36 | legacy-imported |
| `imported.runtime.voice._found` | function | `migration/imported/runtime/voice.py:16-17` | def _found(commands: tuple[str, ...]) -> list[dict[str, str]] | 0 | legacy-imported |
| `imported.runtime.voice.local_adapters` | function | `migration/imported/runtime/voice.py:20-31` | def local_adapters() -> dict | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__.emit` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/__main__.py:17-18` | def emit(value: object) -> None | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__.doctor` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/__main__.py:21-39` | def doctor(store: Store, source: Path \| None) -> dict | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.__main__.main` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/__main__.py:42-118` | def main(argv: list[str] \| None=None) -> int | 155 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.iso` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:52-53` | def iso() -> str | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.validate_task` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:56-74` | def validate_task(value: object) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.git` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:77-81` | def git(root: Path, *args: str, timeout: int=20) -> str | 19 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.validate_source` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:84-95` | def validate_source(root: Path) -> tuple[Path, str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store` | class | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:98-361` | class Store() | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.__init__` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:99-101` | def __init__(self, home: Path=DEFAULT_HOME) | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.db` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:104-114` | def db(self) | 27 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.init` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:116-130` | def init(self, source: Path) -> dict | 14 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.config` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:132-135` | def config(self, key: str) -> str | 17 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.set_config` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:137-139` | def set_config(self, key: str, value: str) -> None | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.import_architecture` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:141-157` | def import_architecture(self, path: Path) -> dict | 6 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.approve_architecture` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:159-163` | def approve_architecture(self, sha: str) -> None | 6 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.add_task` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:165-176` | def add_task(self, value: object) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.add_plan` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:178-198` | def add_plan(self, tasks: object) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.tasks` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:200-203` | def tasks(self) -> list[dict] | 18 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.claim` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:205-230` | def claim(self) -> dict \| None | 21 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.start_run` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:232-234` | def start_run(self, run_id: str, task_id: str, branch: str, sha: str, worktree: Path, attempt: int) | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.update_status` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:236-240` | def update_status(self, task_id: str, run_id: str, stage: str, exit_code: int \| None=None, qc_result: str \| None=None, error_code: str \| None=None, tool_count: int=0) | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.event` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:242-244` | def event(self, event: dict) -> None | 24 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.unsynced` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:246-248` | def unsynced(self, limit: int=100) -> list[dict] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.synced` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:250-252` | def synced(self, event_id: str) -> None | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.approve_task` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:254-262` | def approve_task(self, task_id: str) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.recover` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:264-271` | def recover(self) -> list[str] | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.retry` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:273-278` | def retry(self, task_id: str) -> None | 10 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.integration_lock` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:281-293` | def integration_lock(self) | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.integrate` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:295-354` | def integrate(self, task_id: str) -> dict | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.core.Store.overview` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/core.py:356-361` | def overview(self) -> dict | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.report` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:21-22` | def report(obj: object) | 14 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.diagnose` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:25-45` | def diagnose(source: Path \| None) -> dict | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.supervise` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:48-92` | def supervise(state: State, *, focus: str, count: int, output: Path, model: str, effort: str) | 1 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.run_master` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:95-173` | def run_master(state: State, *, workers: int, max_tasks: int, max_minutes: int, model: str, effort: str, test_image: str, test_command: list[str], auto_integrate: bool, max_repairs | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_cli.main` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_cli.py:176-240` | def main(argv: list[str] \| None=None) -> int | 155 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.check_changes` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:26-75` | def check_changes(worktree: Path, base_sha: str) -> list[str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.make_prompt` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:78-87` | def make_prompt(task: dict, sha: str, architecture_sha: str, role: str, previous_error: str='') -> str | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_command` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:90-98` | def codex_command(worktree: Path, model: str, effort: str, output_file: Path \| None, sandbox: str) -> list[str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_call` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:101-166` | def codex_call(*, worktree: Path, prompt: str, home: Path, state: State, model: str, effort: str, sandbox: str, timeout: int, output_file: Path \| None=None, role: str='worker') -> | 1 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.codex_call.reader` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:113-133` | def reader(stream, tag) | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.docker_test` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:169-197` | def docker_test(worktree: Path, image: str, command: list[str], timeout: int=300) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.shutil_which` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:199-201` | def shutil_which(name: str) -> str \| None | 1 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.independent_qc` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:204-231` | def independent_qc(state: State, worktree: Path, task: dict, *, model: str, effort: str, timeout: int=600) -> tuple[bool, str] | 7 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.merger_review` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:235-256` | def merger_review(state: State, integration: Path, tid: str, patch: bytes, *, model: str, effort: str) -> bool | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.ensure_integration` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:259-273` | def ensure_integration(state: State) -> Path | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.integrate` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:276-320` | def integrate(state: State, tid: str, *, merger_model: str \| None=None, merger_effort: str='medium') -> dict | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.execute_claim` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:323-390` | def execute_claim(state: State, item: dict, *, slot: int, model: str, effort: str, timeout: int, test_image: str, test_command: list[str], auto_integrate: bool=False) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_runtime.execute_claim.emit` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_runtime.py:343-345` | def emit(stage: str, step: str, result: str='') | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.now` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:68-69` | def now() -> str | 19 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.git` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:71-76` | def git(repo: Path, *args: str, timeout: int=90) -> str | 19 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.assert_source` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:78-89` | def assert_source(source: Path) -> tuple[Path, str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.task_spec` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:91-109` | def task_spec(obj: object) -> dict | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State` | class | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:111-331` | class State() | 7 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.__init__` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:112-115` | def __init__(self, home: Path=DEFAULT_HOME) | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.db` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:118-128` | def db(self) | 27 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.master_lock` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:131-143` | def master_lock(self, blocking: bool=False) | 1 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.init` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:145-168` | def init(self, source: Path) -> dict | 14 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.get` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:170-173` | def get(self, key: str) -> str | 27 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.put` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:175-177` | def put(self, key: str, value: str) | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.import_architecture` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:179-193` | def import_architecture(self, file: Path) -> str | 6 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.approve_architecture` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:195-199` | def approve_architecture(self, digest: str) | 6 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.ensure_approved` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:201-203` | def ensure_approved(self) | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.add_tasks` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:205-224` | def add_tasks(self, values: object) -> list[str] | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.list_tasks` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:226-228` | def list_tasks(self) -> list[dict] | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.claim` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:230-251` | def claim(self, model: str=MODEL) -> dict \| None | 21 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.set_task` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:253-265` | def set_task(self, tid: str, status: str, *, error: str='', fields: dict \| None=None) | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.emit` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:267-277` | def emit(self, tid: str, run_id: str, *, stage: str, step: str, branch: str, base_sha: str, tools: int=0, attempt: int=1, elapsed: int=0, result: str='') | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.sync` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:279-301` | def sync(self, limit: int=50) -> dict | 13 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.recover` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:303-310` | def recover(self) -> list[str] | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.retry` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:312-317` | def retry(self, tid: str) | 10 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.approve` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:319-324` | def approve(self, tid: str) | 6 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.linux_sda.State.overview` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/linux_sda.py:326-331` | def overview(self) -> dict | 4 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.planner.focused_architecture` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/planner.py:15-40` | def focused_architecture(text: str, focus: str='') -> str | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.planner.validate_plan` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/planner.py:43-56` | def validate_plan(obj: object) -> list[dict] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.planner.propose` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/planner.py:59-90` | def propose(store: Store, focus: str='', count: int=4, model: str='qwen3:8b', output: Path \| None=None) -> dict | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.event_payload` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:26-32` | def event_payload(*, run_id: str, task_id: str, seq: int, stage: str, step: str, branch: str, base_sha: str, tool_count: int=0, elapsed_s: int=0, attempt: int=1, result: str='') -> | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress` | class | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:35-64` | class Progress() | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress.__init__` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:36-41` | def __init__(self, store: Store) | 5 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress.flush` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:43-58` | def flush(self, limit: int=100) -> dict | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.Progress.send` | method | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:60-64` | def send(self, e: dict) -> None | 3 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.publish_manual_state` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:67-74` | def publish_manual_state(store: Store, task_id: str, stage: str, step: str) -> None | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.build_prompt` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:77-93` | def build_prompt(task: dict, base_sha: str, architecture_sha: str) -> str | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.create_worktree` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:96-114` | def create_worktree(store: Store, task_id: str, run_id: str) -> tuple[Path, str, str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner._read_lines` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:117-122` | def _read_lines(pipe: object, queue_out: queue.Queue) | 0 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.changes_and_qc` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:125-150` | def changes_and_qc(worktree: Path) -> tuple[bool, str] | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.execute_claim` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:153-271` | def execute_claim(store: Store, claimed: dict, *, model: str='qwen3:8b', context: int=16384, max_seconds: int=1800) -> int | 2 | legacy-imported |
| `imported.sda.astra_one_v0.2.0.astra_one.runner.execute_claim.emit` | function | `migration/imported/sda/astra-one-v0.2.0/astra_one/runner.py:167-172` | def emit(stage: str, step: str, result: str='') | 5 | legacy-imported |
| `index.make` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:50-50` | const make=(tag,text,cls)=>{const e=document.createElement(tag);e.textContent=String(text);if(cls)e.className=cls;return e}; | 0 | legacy-imported |
| `index.get` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:51-51` | async function get(url){const r=await fetch(url,{headers:{authorization:'Bearer '+token},cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()} | 27 | legacy-imported |
| `index.refresh` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:52-52` | async function refresh(){ | 0 | legacy-imported |
| `index.loadEvents` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:69-69` | async function loadEvents(){if(!selected)return;try{const data=await get('/api/events?run_id='+encodeURIComponent(selected)); | 0 | legacy-imported |
| `index.secureHeaders` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:76-76` | function secureHeaders(contentType: string): HeadersInit { | 0 | legacy-imported |
| `index.json` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:82-82` | function json(data: unknown, status = 200): Response { | 44 | legacy-imported |
| `index.equal` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:85-85` | function equal(a: string, b: string): boolean { | 5 | legacy-imported |
| `index.authorized` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:91-91` | function authorized(req: Request, secret: string): boolean { | 4 | legacy-imported |
| `index.validStr` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:94-94` | function validStr(v: unknown, max: number, regex: RegExp): v is string { | 0 | legacy-imported |
| `index.validate` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:97-97` | function validate(body: unknown): Event \| null { | 2 | legacy-imported |
| `index.postEvent` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/src/index.ts:116-116` | async function postEvent(req: Request, env: Env): Promise<Response> { | 0 | legacy-imported |
| `worker.test.uuid` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/tests/worker.test.mjs:36-36` | const uuid=()=> '123e4567-e89b-42d3-a456-426614174000'; | 4 | legacy-imported |
| `worker.test.message` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/tests/worker.test.mjs:37-37` | const message=(seq,stage)=>({event_id:seq===1?uuid():'123e4567-e89b-42d3-a456-426614174001',run_id:'123e4567-e89b-42d3-a456-426614174999',task_id:'ASTRA-101',seq,time:'2026-11-13T1 | 13 | legacy-imported |
| `worker.test.call` | function | `migration/imported/sda/astra-one-v0.2.0/cloudflare/astra-one-monitor/tests/worker.test.mjs:38-38` | async function call(path,method='GET',body=null,token=''){ | 7 | legacy-imported |
| `test_core.git` | function | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:17-18` | def git(root, *args) | 19 | legacy-imported |
| `test_core.AstraTests` | class | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:21-252` | class AstraTests(unittest.TestCase) | 2 | legacy-imported |
| `test_core.AstraTests.setUp` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:22-35` | def setUp(self) | 35 | legacy-imported |
| `test_core.AstraTests.init` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:37-38` | def init(self) | 14 | legacy-imported |
| `test_core.AstraTests.architecture` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:40-46` | def architecture(self) | 9 | legacy-imported |
| `test_core.AstraTests.task` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:48-49` | def task(self, task_id='ASTRA-101', depends_on=None) | 24 | legacy-imported |
| `test_core.AstraTests.test_init_starts_engine_stopped` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:51-54` | def test_init_starts_engine_stopped(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_refuse_reinitializing_state` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:56-59` | def test_refuse_reinitializing_state(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_refuse_dirty_source` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:61-64` | def test_refuse_dirty_source(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_architecture_requires_approval` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:66-71` | def test_architecture_requires_approval(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_wrong_architecture_sha_denied` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:73-78` | def test_wrong_architecture_sha_denied(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_approved_architecture_is_still_not_started` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:80-83` | def test_approved_architecture_is_still_not_started(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_task_rejects_unexpected_secret_field` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:85-88` | def test_task_rejects_unexpected_secret_field(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_task_requires_acceptance` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:90-93` | def test_task_requires_acceptance(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_enqueue_claim_once` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:95-101` | def test_enqueue_claim_once(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_dependencies_block_claim` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:103-108` | def test_dependencies_block_claim(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_dependencies_reject_unknown` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:110-113` | def test_dependencies_reject_unknown(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_pause_prevents_claim` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:115-118` | def test_pause_prevents_claim(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_stop_prevents_claim` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:120-123` | def test_stop_prevents_claim(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_architecture_replacement_pauses` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:125-129` | def test_architecture_replacement_pauses(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_recover_marks_interrupted` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:131-135` | def test_recover_marks_interrupted(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_retry_requires_explicit_failed_state` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:137-142` | def test_retry_requires_explicit_failed_state(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_event_metadata_has_no_private_content` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:144-149` | def test_event_metadata_has_no_private_content(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_events_persist_and_sync` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:151-159` | def test_events_persist_and_sync(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_progress_no_monitor_configuration` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:161-165` | def test_progress_no_monitor_configuration(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_prompt_does_not_include_private_architecture` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:167-172` | def test_prompt_does_not_include_private_architecture(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_qc_rejects_no_changes` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:174-177` | def test_qc_rejects_no_changes(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_qc_rejects_deletion` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:179-183` | def test_qc_rejects_deletion(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_qc_rejects_python_syntax` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:185-189` | def test_qc_rejects_python_syntax(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_qc_passes_python_syntax` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:191-195` | def test_qc_passes_python_syntax(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_reviewed_candidate_integrates_only_to_local_feature` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:197-216` | def test_reviewed_candidate_integrates_only_to_local_feature(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_integration_rejects_unapproved` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:218-221` | def test_integration_rejects_unapproved(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_planner_focus_selects_one_heading_section` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:223-227` | def test_planner_focus_selects_one_heading_section(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_planner_large_architecture_requires_focus` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:229-231` | def test_planner_large_architecture_requires_focus(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_planner_rejects_forward_dependency` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:233-236` | def test_planner_rejects_forward_dependency(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_atomic_plan_enqueue` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:238-245` | def test_atomic_plan_enqueue(self) | 2 | legacy-imported |
| `test_core.AstraTests.test_cloudflare_schema_valid_sqlite` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_core.py:247-252` | def test_cloudflare_schema_valid_sqlite(self) | 2 | legacy-imported |
| `test_linux_sda.git_repo` | function | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:16-24` | def git_repo(root) | 5 | legacy-imported |
| `test_linux_sda.task` | function | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:27-28` | def task(i, deps=None) | 24 | legacy-imported |
| `test_linux_sda.LinuxSDATests` | class | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:30-211` | class LinuxSDATests(unittest.TestCase) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.setUp` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:31-41` | def setUp(self) | 35 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_source_dirty_refused` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:43-46` | def test_source_dirty_refused(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_architecture_approval_explicit` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:48-52` | def test_architecture_approval_explicit(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_dependency_blocks_claim_until_integrated` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:54-60` | def test_dependency_blocks_claim_until_integrated(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_stop_and_pause_gate` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:62-68` | def test_stop_and_pause_gate(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_recover_no_replay` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:70-75` | def test_recover_no_replay(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_plan_is_atomic` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:77-80` | def test_plan_is_atomic(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_task_rejects_unknown_fields` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:82-84` | def test_task_rejects_unknown_fields(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_model_cli_is_codex_cloud_not_oss` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:86-91` | def test_model_cli_is_codex_cloud_not_oss(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_static_change_accepts_valid_python` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:93-96` | def test_static_change_accepts_valid_python(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_delete` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:98-102` | def test_static_change_rejects_delete(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_symlink` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:104-108` | def test_static_change_rejects_symlink(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_policy` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:110-114` | def test_static_change_rejects_policy(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_static_change_rejects_invalid_python` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:116-120` | def test_static_change_rejects_invalid_python(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_five_worker_parallel_scheduler` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:122-140` | def test_five_worker_parallel_scheduler(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_five_worker_parallel_scheduler.fake_execute` | function | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:126-132` | def fake_execute(state, item, **kwargs) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_merger_safe_serial_integration` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:142-162` | def test_merger_safe_serial_integration(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_architecture_change_invalidates_old_queued_tasks` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:164-172` | def test_architecture_change_invalidates_old_queued_tasks(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_full_codex_pipeline_mocked_five_tasks` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:174-200` | def test_full_codex_pipeline_mocked_five_tasks(self) | 2 | legacy-imported |
| `test_linux_sda.LinuxSDATests.test_event_metadata_schema` | method | `migration/imported/sda/astra-one-v0.2.0/tests/test_linux_sda.py:202-211` | def test_event_metadata_schema(self) | 2 | legacy-imported |
| `imported.sda.codex_workhorse_v2.git` | function | `migration/imported/sda/codex_workhorse_v2.py:51-55` | def git(*args: str, cwd: Path=ROOT, check: bool=True) -> subprocess.CompletedProcess[str] | 19 | legacy-imported |
| `imported.sda.codex_workhorse_v2.proc_identity` | function | `migration/imported/sda/codex_workhorse_v2.py:58-64` | def proc_identity(pid: int) -> tuple[int, str] \| None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.alive` | function | `migration/imported/sda/codex_workhorse_v2.py:67-69` | def alive(pid: int, start_tick: int) -> bool | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.codex_events` | function | `migration/imported/sda/codex_workhorse_v2.py:72-107` | def codex_events(path: str) -> tuple[str \| None, int, int, bool, bool, str] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.require_one_line` | function | `migration/imported/sda/codex_workhorse_v2.py:111-114` | def require_one_line(value: str, max_len: int) -> str | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.task_rows` | function | `migration/imported/sda/codex_workhorse_v2.py:116-117` | def task_rows(text: str) -> list[tuple[str, int, bool]] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.checkbox_progress` | function | `migration/imported/sda/codex_workhorse_v2.py:120-122` | def checkbox_progress(text: str) -> tuple[int, int] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.quota_in_log` | function | `migration/imported/sda/codex_workhorse_v2.py:125-129` | def quota_in_log(path: str) -> bool | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.parent_checked` | function | `migration/imported/sda/codex_workhorse_v2.py:132-136` | def parent_checked(path: Path, parent: str) -> bool | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.deleted_sources_logged` | function | `migration/imported/sda/codex_workhorse_v2.py:139-171` | def deleted_sources_logged(worktree: Path, baseline: str='develop') -> tuple[bool, str] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.tests_pass` | function | `migration/imported/sda/codex_workhorse_v2.py:174-190` | def tests_pass(worktree: Path) -> tuple[bool, str] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master` | class | `migration/imported/sda/codex_workhorse_v2.py:193-990` | class Master() | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.__init__` | method | `migration/imported/sda/codex_workhorse_v2.py:194-266` | def __init__(self, root: Path=ROOT, state: Path=STATE, workers: int=5, models: dict \| None=None, push: bool=False, retry_limit: int=MAX_ATTEMPTS) | 5 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.rows` | method | `migration/imported/sda/codex_workhorse_v2.py:268-269` | def rows(self, sql: str, args: tuple=()) -> list[dict] | 6 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.job` | method | `migration/imported/sda/codex_workhorse_v2.py:271-275` | def job(self, parent: str) -> dict | 10 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.update` | method | `migration/imported/sda/codex_workhorse_v2.py:277-283` | def update(self, parent: str, **fields) -> None | 16 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.event` | method | `migration/imported/sda/codex_workhorse_v2.py:285-289` | def event(self, parent: str, actor: str, kind: str, detail: str) -> None | 24 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.ingest_submissions` | method | `migration/imported/sda/codex_workhorse_v2.py:291-341` | def ingest_submissions(self) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.archive_submission` | method | `migration/imported/sda/codex_workhorse_v2.py:343-349` | def archive_submission(self, source: Path) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.ingest` | method | `migration/imported/sda/codex_workhorse_v2.py:351-361` | def ingest(self) -> None | 5 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.validate` | method | `migration/imported/sda/codex_workhorse_v2.py:363-382` | def validate(self) -> None | 2 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.pick` | method | `migration/imported/sda/codex_workhorse_v2.py:384-391` | def pick(self, states: tuple[str, ...]) -> dict \| None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.prepare_worker` | method | `migration/imported/sda/codex_workhorse_v2.py:393-407` | def prepare_worker(self, row: dict) -> dict | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.prompt` | method | `migration/imported/sda/codex_workhorse_v2.py:409-441` | def prompt(self, row: dict, role: str) -> str | 7 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.spawn` | method | `migration/imported/sda/codex_workhorse_v2.py:443-465` | def spawn(self, row: dict, role: str, cwd: Path, session: str='') -> tuple[int, int, str] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.start_worker` | method | `migration/imported/sda/codex_workhorse_v2.py:467-471` | def start_worker(self, row: dict) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.start_role` | method | `migration/imported/sda/codex_workhorse_v2.py:473-480` | def start_role(self, role: str, row: dict, cwd: Path) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.exit_code` | method | `migration/imported/sda/codex_workhorse_v2.py:482-487` | def exit_code(self, pid: int, logfile: str) -> int | 10 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.saved_usage` | method | `migration/imported/sda/codex_workhorse_v2.py:489-506` | def saved_usage(self, parent: str, logfile: str, role: str) -> tuple[bool, bool, str] | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.finish_worker` | method | `migration/imported/sda/codex_workhorse_v2.py:508-531` | def finish_worker(self, row: dict) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.finish_repairer` | method | `migration/imported/sda/codex_workhorse_v2.py:533-576` | def finish_repairer(self, role_row: dict) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.setup_merge` | method | `migration/imported/sda/codex_workhorse_v2.py:578-592` | def setup_merge(self, row: dict) -> Path | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.finish_merger` | method | `migration/imported/sda/codex_workhorse_v2.py:594-646` | def finish_merger(self, role_row: dict) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.accept_integration` | method | `migration/imported/sda/codex_workhorse_v2.py:648-678` | def accept_integration(self, row: dict) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.retire_branch` | method | `migration/imported/sda/codex_workhorse_v2.py:680-694` | def retire_branch(self, row: dict, reason: str) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.rebuild` | method | `migration/imported/sda/codex_workhorse_v2.py:696-769` | def rebuild(self, parent: str, stage: str, error: str) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.checkpoint_push` | method | `migration/imported/sda/codex_workhorse_v2.py:771-802` | def checkpoint_push(self) -> str | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.reap` | method | `migration/imported/sda/codex_workhorse_v2.py:804-814` | def reap(self) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.dispatch` | method | `migration/imported/sda/codex_workhorse_v2.py:816-845` | def dispatch(self) -> None | 6 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.pause_quota` | method | `migration/imported/sda/codex_workhorse_v2.py:847-874` | def pause_quota(self, parent: str, role: str) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.archive_marker` | method | `migration/imported/sda/codex_workhorse_v2.py:876-887` | def archive_marker(self, path: Path) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.resume_quota` | method | `migration/imported/sda/codex_workhorse_v2.py:889-918` | def resume_quota(self) -> str | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.stop_children` | method | `migration/imported/sda/codex_workhorse_v2.py:920-932` | def stop_children(self) -> None | 0 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.tick` | method | `migration/imported/sda/codex_workhorse_v2.py:934-938` | def tick(self) -> None | 2 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.run` | method | `migration/imported/sda/codex_workhorse_v2.py:940-984` | def run(self, poll: int=3, once: bool=False) -> int | 36 | legacy-imported |
| `imported.sda.codex_workhorse_v2.Master.close` | method | `migration/imported/sda/codex_workhorse_v2.py:986-990` | def close(self) -> None | 34 | legacy-imported |
| `imported.sda.codex_workhorse_v2.dashboard` | function | `migration/imported/sda/codex_workhorse_v2.py:993-1028` | def dashboard(master: Master) -> str | 3 | legacy-imported |
| `imported.sda.codex_workhorse_v2.cli` | function | `migration/imported/sda/codex_workhorse_v2.py:1031-1106` | def cli() -> int | 3 | legacy-imported |
| `imported.sda.sda_context_handoff.HandoffError` | class | `migration/imported/sda/sda_context_handoff.py:17-18` | class HandoffError(ValueError) | 2 | legacy-imported |
| `imported.sda.sda_context_handoff.build_handoff` | function | `migration/imported/sda/sda_context_handoff.py:21-104` | def build_handoff(state: dict, next_provider: str, *, recent: int=8) -> dict | 0 | legacy-imported |
| `imported.sda.sda_context_handoff.verify_handoff` | function | `migration/imported/sda/sda_context_handoff.py:107-125` | def verify_handoff(packet: dict, history: list[dict], *, provider: str, policy_digest: str) -> bool | 0 | legacy-imported |
| `imported.sda.workhorse_context.run_git` | function | `migration/imported/sda/workhorse_context.py:32-36` | def run_git(root: Path, *args: str) -> str | 0 | legacy-imported |
| `imported.sda.workhorse_context.allowed` | function | `migration/imported/sda/workhorse_context.py:39-50` | def allowed(root: Path, rel: str) -> bool | 8 | legacy-imported |
| `imported.sda.workhorse_context.code_chunks` | function | `migration/imported/sda/workhorse_context.py:53-74` | def code_chunks(rel: str, source: str) | 0 | legacy-imported |
| `imported.sda.workhorse_context.connect` | function | `migration/imported/sda/workhorse_context.py:77-97` | def connect(state: Path) -> sqlite3.Connection | 13 | legacy-imported |
| `imported.sda.workhorse_context.update_index` | function | `migration/imported/sda/workhorse_context.py:100-130` | def update_index(db: sqlite3.Connection, root: Path) -> dict | 0 | legacy-imported |
| `imported.sda.workhorse_context.purge` | function | `migration/imported/sda/workhorse_context.py:133-138` | def purge(db: sqlite3.Connection, scope: str, rel: str) | 0 | legacy-imported |
| `imported.sda.workhorse_context.embed` | function | `migration/imported/sda/workhorse_context.py:141-154` | def embed(texts: list[str]) -> list[list[float]] | 0 | legacy-imported |
| `imported.sda.workhorse_context.cosine` | function | `migration/imported/sda/workhorse_context.py:157-161` | def cosine(a, b) | 0 | legacy-imported |
| `imported.sda.workhorse_context.query_words` | function | `migration/imported/sda/workhorse_context.py:164-168` | def query_words(s: str) -> list[str] | 0 | legacy-imported |
| `imported.sda.workhorse_context.rank` | function | `migration/imported/sda/workhorse_context.py:171-237` | def rank(db: sqlite3.Connection, scope: str, question: str, mode: str, limit=24) | 0 | legacy-imported |
| `imported.sda.workhorse_context.requirement` | function | `migration/imported/sda/workhorse_context.py:240-249` | def requirement(root: Path, task: str) -> str | 0 | legacy-imported |
| `imported.sda.workhorse_context.verified_memory` | function | `migration/imported/sda/workhorse_context.py:252-270` | def verified_memory(db: sqlite3.Connection, root: Path, question: str) -> list[str] | 0 | legacy-imported |
| `imported.sda.workhorse_context.record_verified_merge` | function | `migration/imported/sda/workhorse_context.py:273-280` | def record_verified_merge(root: Path, state: Path, task: str, sha: str) | 0 | legacy-imported |
| `imported.sda.workhorse_context.packet` | function | `migration/imported/sda/workhorse_context.py:283-322` | def packet(root: Path, state: Path, task: str, mode: str, budget: int=2400, feedback: str='') -> tuple[str, dict] | 5 | legacy-imported |
| `imported.sda.workhorse_context.optimize_prompt` | function | `migration/imported/sda/workhorse_context.py:325-342` | def optimize_prompt(root: Path, state: Path, task: str, role: str, baseline_prompt: str, budget: int=2400, feedback: str='') -> str | 0 | legacy-imported |
| `imported.sda.workhorse_context.main` | function | `migration/imported/sda/workhorse_context.py:345-365` | def main() -> int | 155 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.normalized_wings` | function | `migration/imported/tws/aurelia3d/build_portable.py:35-38` | def normalized_wings(value: int) -> int | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.quaternion` | function | `migration/imported/tws/aurelia3d/build_portable.py:41-43` | def quaternion(axis: tuple[float, float, float], angle: float) -> tuple[float, ...] | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB` | class | `migration/imported/tws/aurelia3d/build_portable.py:46-172` | class GLB() | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB.__init__` | method | `migration/imported/tws/aurelia3d/build_portable.py:47-55` | def __init__(self) | 5 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB.accessor` | method | `migration/imported/tws/aurelia3d/build_portable.py:57-76` | def accessor(self, values, *, fmt: str, kind: str, component: int, target=None, bounds=False) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB.material` | method | `migration/imported/tws/aurelia3d/build_portable.py:78-88` | def material(self, name) | 1 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB.add_mesh` | method | `migration/imported/tws/aurelia3d/build_portable.py:90-150` | def add_mesh(self, name, vertices, faces, material, *, joint, morphs=None, meta=None, skin=None) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.GLB.save` | method | `migration/imported/tws/aurelia3d/build_portable.py:152-172` | def save(self, path: Path, joints: list[int], root: int) | 5 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.sphere` | function | `migration/imported/tws/aurelia3d/build_portable.py:175-190` | def sphere(cx, cy, cz, rx, ry, rz, segments=18, rings=12) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.tapered` | function | `migration/imported/tws/aurelia3d/build_portable.py:193-209` | def tapered(cx, cz, profiles, segments=22) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.feather` | function | `migration/imported/tws/aurelia3d/build_portable.py:212-226` | def feather(start, end, width) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.facial_mesh` | function | `migration/imported/tws/aurelia3d/build_portable.py:229-270` | def facial_mesh() | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.facial_mesh.patch` | function | `migration/imported/tws/aurelia3d/build_portable.py:231-236` | def patch(name, x, y, z, w, h) | 7 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.build` | function | `migration/imported/tws/aurelia3d/build_portable.py:273-422` | def build(path: Path, *, wings: int=12) | 1 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.build.bone` | function | `migration/imported/tws/aurelia3d/build_portable.py:280-280` | def bone(name, loc, parent=None) | 1 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.build.add` | function | `migration/imported/tws/aurelia3d/build_portable.py:319-325` | def add(name, geom, mat, bone, *, morphs=None, meta=None, skin_fn=None) | 28 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.build.smoothstep` | function | `migration/imported/tws/aurelia3d/build_portable.py:327-329` | def smoothstep(value) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.build.gown_skin` | function | `migration/imported/tws/aurelia3d/build_portable.py:331-339` | def gown_skin(vertex) | 0 | legacy-imported |
| `imported.tws.aurelia3d.build_portable.main` | function | `migration/imported/tws/aurelia3d/build_portable.py:425-432` | def main() | 155 | legacy-imported |
| `imported.tws.engine.xp_to_next_level` | function | `migration/imported/tws/engine.py:11-14` | def xp_to_next_level(level: int) -> int | 0 | legacy-imported |
| `imported.tws.engine.connect` | function | `migration/imported/tws/engine.py:16-47` | def connect(path: str \| Path) -> sqlite3.Connection | 13 | legacy-imported |
| `imported.tws.engine.connect_readonly` | function | `migration/imported/tws/engine.py:49-58` | def connect_readonly(path: str \| Path) -> sqlite3.Connection | 0 | legacy-imported |
| `imported.tws.engine.initialize` | function | `migration/imported/tws/engine.py:60-66` | def initialize(db: sqlite3.Connection) -> None | 0 | legacy-imported |
| `imported.tws.engine.status` | function | `migration/imported/tws/engine.py:68-72` | def status(db: sqlite3.Connection) -> dict | 80 | legacy-imported |
| `imported.tws.engine.companion` | function | `migration/imported/tws/engine.py:74-78` | def companion(db: sqlite3.Connection) -> dict | 0 | legacy-imported |
| `imported.tws.engine.quests` | function | `migration/imported/tws/engine.py:80-81` | def quests(db: sqlite3.Connection) -> list[dict] | 1 | legacy-imported |
| `imported.tws.engine.accept` | function | `migration/imported/tws/engine.py:83-87` | def accept(db: sqlite3.Connection, quest_id: str) -> None | 0 | legacy-imported |
| `imported.tws.engine.submit` | function | `migration/imported/tws/engine.py:89-95` | def submit(db: sqlite3.Connection, quest_id: str, note: str) -> None | 6 | legacy-imported |
| `imported.tws.engine.complete` | function | `migration/imported/tws/engine.py:97-115` | def complete(db: sqlite3.Connection, quest_id: str) -> dict | 9 | legacy-imported |
| `imported.tws.engine.next_story` | function | `migration/imported/tws/engine.py:117-123` | def next_story(db: sqlite3.Connection) -> str \| None | 0 | legacy-imported |
| `imported.tws.evidence.migrate` | function | `migration/imported/tws/evidence.py:9-17` | def migrate(db) | 4 | legacy-imported |
| `imported.tws.evidence.submit` | function | `migration/imported/tws/evidence.py:19-29` | def submit(db, evidence_id: str, trial_id: str, note: str) | 6 | legacy-imported |
| `imported.tws.evidence.review` | function | `migration/imported/tws/evidence.py:31-38` | def review(db, evidence_id: str, approved: bool, reviewer: str) | 6 | legacy-imported |
| `imported.tws.evidence.verified_count` | function | `migration/imported/tws/evidence.py:40-41` | def verified_count(db, trial_id: str) -> int | 0 | legacy-imported |
| `imported.tws.evidence.advance` | function | `migration/imported/tws/evidence.py:43-47` | def advance(db, event_id: str, trial) | 1 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.makeCoordinator` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:33-33` | func makeCoordinator() -> Coordinator { Coordinator() } | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.makeUIView` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:35-35` | func makeUIView(context: Context) -> SCNView { | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.updateUIView` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:58-58` | func updateUIView(_ view: SCNView, context: Context) { | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.dismantleUIView` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:63-63` | static func dismantleUIView(_ view: SCNView, coordinator: Coordinator) { | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.make` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:246-246` | static func make() -> (scene: SCNScene, clips: AureliaImportedClipDriver?) { | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.bundledArt` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:254-254` | private static func bundledArt() -> | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.procedural` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:306-306` | private static func procedural() -> SCNScene { | 0 | legacy-imported |
| `imported.tws.ios.Aurelia3DSceneView.ensureCameraAndLights` | function | `migration/imported/tws/ios/Aurelia3DSceneView.swift:449-449` | private static func ensureCameraAndLights(_ scene: SCNScene) { | 0 | legacy-imported |
| `jarvis_v2.automation.device_registry.DeviceAuthError` | class | `src/jarvis_v2/automation/device_registry.py:25-26` | class DeviceAuthError(ValueError) | 1 | active |
| `jarvis_v2.automation.device_registry._identifier` | function | `src/jarvis_v2/automation/device_registry.py:29-32` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.automation.device_registry._key` | function | `src/jarvis_v2/automation/device_registry.py:35-40` | def _key(value: bytes \| bytearray, label: str='key') -> bytes | 0 | active |
| `jarvis_v2.automation.device_registry._proof` | function | `src/jarvis_v2/automation/device_registry.py:43-51` | def _proof(value: bytes \| str) -> bytes | 0 | active |
| `jarvis_v2.automation.device_registry._message` | function | `src/jarvis_v2/automation/device_registry.py:54-59` | def _message(value: str \| bytes) -> bytes | 2 | active |
| `jarvis_v2.automation.device_registry.DeviceRecord` | class | `src/jarvis_v2/automation/device_registry.py:63-78` | class DeviceRecord() | 0 | active |
| `jarvis_v2.automation.device_registry.DeviceRecord.__post_init__` | method | `src/jarvis_v2/automation/device_registry.py:70-78` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry` | class | `src/jarvis_v2/automation/device_registry.py:81-228` | class AuthenticatedDeviceRegistry() | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.__init__` | method | `src/jarvis_v2/automation/device_registry.py:84-87` | def __init__(self, agents: WindowsAgentRegistry \| None=None) -> None | 5 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.claim_message` | method | `src/jarvis_v2/automation/device_registry.py:90-91` | def claim_message(job_id: str) -> str | 0 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.complete_message` | method | `src/jarvis_v2/automation/device_registry.py:94-95` | def complete_message(job_id: str, lease_id: str, result_sha256: str) -> str | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.rotation_message` | method | `src/jarvis_v2/automation/device_registry.py:98-104` | def rotation_message(device_id: str, current_key_id: str, next_key_id: str, next_key_sha256: str) -> str | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.make_proof` | method | `src/jarvis_v2/automation/device_registry.py:107-108` | def make_proof(key_material: bytes \| bytearray, message: str \| bytes) -> str | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.register` | method | `src/jarvis_v2/automation/device_registry.py:110-128` | def register(self, manifest: NodeManifest, key_material: bytes \| bytearray, *, key_id: str='key-1') -> DeviceRecord | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.authenticate` | method | `src/jarvis_v2/automation/device_registry.py:132-141` | def authenticate(self, device_id: str, key_id: str, message: str \| bytes, proof: bytes \| str) -> DeviceRecord | 1 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.rotate_key` | method | `src/jarvis_v2/automation/device_registry.py:143-165` | def rotate_key(self, device_id: str, current_key_id: str, next_key_id: str, next_key_material: bytes \| bytearray, proof: bytes \| str) -> DeviceRecord | 0 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.revoke` | method | `src/jarvis_v2/automation/device_registry.py:169-177` | def revoke(self, device_id: str) -> DeviceRecord | 5 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.submit` | method | `src/jarvis_v2/automation/device_registry.py:179-180` | def submit(self, job: LocalAgentJob) -> LocalAgentJob | 6 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.heartbeat` | method | `src/jarvis_v2/automation/device_registry.py:182-206` | def heartbeat(self, device_id: str, key_id: str, proof: bytes \| str, *, status: str='online', observed_at: float \| None=None, cpu_percent: float \| None=None, memory_bytes: int \ | 5 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.claim` | method | `src/jarvis_v2/automation/device_registry.py:208-213` | def claim(self, job_id: str, device_id: str, key_id: str, proof: bytes \| str, *, ttl_seconds: int=60) -> CapabilityLease | 21 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.complete` | method | `src/jarvis_v2/automation/device_registry.py:215-220` | def complete(self, job_id: str, device_id: str, key_id: str, proof: bytes \| str, lease_id: str, *, result_sha256: str, error_code: str='') -> dict[str, object] | 9 | active |
| `jarvis_v2.automation.device_registry.AuthenticatedDeviceRegistry.snapshot` | method | `src/jarvis_v2/automation/device_registry.py:222-228` | def snapshot(self, device_id: str) -> dict[str, object] | 17 | active |
| `jarvis_v2.automation.dispatcher.DispatchDecision` | class | `src/jarvis_v2/automation/dispatcher.py:16-21` | class DispatchDecision() | 0 | active |
| `jarvis_v2.automation.dispatcher._job` | function | `src/jarvis_v2/automation/dispatcher.py:24-38` | def _job(item: QueueEnvelope) -> LocalAgentJob | 0 | active |
| `jarvis_v2.automation.dispatcher.ReconnectDispatcher` | class | `src/jarvis_v2/automation/dispatcher.py:41-82` | class ReconnectDispatcher() | 1 | active |
| `jarvis_v2.automation.dispatcher.ReconnectDispatcher.__init__` | method | `src/jarvis_v2/automation/dispatcher.py:44-53` | def __init__(self, queue: CoordinatorQueue, *, route: Callable[[LocalAgentJob], NodeRoute], handoff: Callable[[QueueEnvelope, LocalAgentJob, NodeRoute], bool]) -> None | 5 | active |
| `jarvis_v2.automation.dispatcher.ReconnectDispatcher.drain` | method | `src/jarvis_v2/automation/dispatcher.py:55-82` | def drain(self, *, limit: int=10) -> list[DispatchDecision] | 4 | active |
| `jarvis_v2.automation.queue_api.QueueSchemaError` | class | `src/jarvis_v2/automation/queue_api.py:28-29` | class QueueSchemaError(ValueError) | 1 | active |
| `jarvis_v2.automation.queue_api.QueueApiError` | class | `src/jarvis_v2/automation/queue_api.py:32-33` | class QueueApiError(ValueError) | 1 | active |
| `jarvis_v2.automation.queue_api._text` | function | `src/jarvis_v2/automation/queue_api.py:36-39` | def _text(value: Any, name: str, limit: int) -> str | 2 | active |
| `jarvis_v2.automation.queue_api._payload` | function | `src/jarvis_v2/automation/queue_api.py:42-52` | def _payload(value: Any) -> dict[str, Any] | 0 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope` | class | `src/jarvis_v2/automation/queue_api.py:56-110` | class QueueEnvelope() | 2 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope.__post_init__` | method | `src/jarvis_v2/automation/queue_api.py:65-72` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope.to_dict` | method | `src/jarvis_v2/automation/queue_api.py:74-84` | def to_dict(self) -> dict[str, Any] | 1 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope.dumps` | method | `src/jarvis_v2/automation/queue_api.py:86-87` | def dumps(self) -> str | 23 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope.from_dict` | method | `src/jarvis_v2/automation/queue_api.py:90-102` | def from_dict(cls, value: Any) -> 'QueueEnvelope' | 3 | active |
| `jarvis_v2.automation.queue_api.QueueEnvelope.loads` | method | `src/jarvis_v2/automation/queue_api.py:105-110` | def loads(cls, value: str) -> 'QueueEnvelope' | 23 | active |
| `jarvis_v2.automation.queue_api.detect_schema` | function | `src/jarvis_v2/automation/queue_api.py:113-130` | def detect_schema(path: Path) -> str | 1 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue` | class | `src/jarvis_v2/automation/queue_api.py:133-295` | class CoordinatorQueue() | 3 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.__init__` | method | `src/jarvis_v2/automation/queue_api.py:136-151` | def __init__(self, queue: TaskQueue, *, source_schema: str='new', clock: Callable[[], float] \| None=None) -> None | 5 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.open` | method | `src/jarvis_v2/automation/queue_api.py:154-157` | def open(cls, path: Path, *, clock: Callable[[], float] \| None=None) -> 'CoordinatorQueue' | 3 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.enqueue` | method | `src/jarvis_v2/automation/queue_api.py:159-167` | def enqueue(self, *, task_id: str, priority: str, module: str, payload: Mapping[str, Any]) -> QueueEnvelope | 4 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue._lease_seconds` | method | `src/jarvis_v2/automation/queue_api.py:170-173` | def _lease_seconds(value: int) -> int | 0 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue._requeue_expired` | method | `src/jarvis_v2/automation/queue_api.py:175-190` | def _requeue_expired(self) -> int | 0 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.lease_next` | method | `src/jarvis_v2/automation/queue_api.py:192-209` | def lease_next(self, *, guardian_waiting: bool=False, allowed_modules: set[str] \| None=None, lease_seconds: int=DEFAULT_LEASE_SECONDS) -> QueueEnvelope \| None | 12 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.eligible` | method | `src/jarvis_v2/automation/queue_api.py:211-217` | def eligible(self, *, guardian_waiting: bool=False, allowed_modules: set[str] \| None=None) -> list[QueueEnvelope] | 4 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.release` | method | `src/jarvis_v2/automation/queue_api.py:219-235` | def release(self, item: QueueEnvelope, *, reason: str='dispatch_deferred') -> None | 12 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.renew` | method | `src/jarvis_v2/automation/queue_api.py:237-254` | def renew(self, item: QueueEnvelope, *, lease_seconds: int=DEFAULT_LEASE_SECONDS) -> QueueEnvelope | 2 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.complete` | method | `src/jarvis_v2/automation/queue_api.py:256-276` | def complete(self, item: QueueEnvelope, *, ok: bool, receipt: str) -> dict[str, Any] | 9 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.status` | method | `src/jarvis_v2/automation/queue_api.py:278-279` | def status(self) -> list[dict[str, Any]] | 80 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.control_status` | method | `src/jarvis_v2/automation/queue_api.py:281-283` | def control_status(self) -> dict[str, str] | 1 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.history` | method | `src/jarvis_v2/automation/queue_api.py:285-286` | def history(self, task_id: str, *, limit: int=100) -> list[dict[str, Any]] | 12 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.close` | method | `src/jarvis_v2/automation/queue_api.py:288-289` | def close(self) -> None | 34 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.__enter__` | method | `src/jarvis_v2/automation/queue_api.py:291-292` | def __enter__(self) -> 'CoordinatorQueue' | 1 | active |
| `jarvis_v2.automation.queue_api.CoordinatorQueue.__exit__` | method | `src/jarvis_v2/automation/queue_api.py:294-295` | def __exit__(self, *_: Any) -> None | 1 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill` | class | `src/jarvis_v2/automation/recovery_drill.py:15-50` | class RecoveryDrill() | 2 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.__init__` | method | `src/jarvis_v2/automation/recovery_drill.py:18-23` | def __init__(self, database: str \| Path, *, max_replay_events: int=MAX_REPLAY_EVENTS) -> None | 5 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.inspect` | method | `src/jarvis_v2/automation/recovery_drill.py:25-27` | def inspect(self) -> dict[str, Any] | 10 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.backup` | method | `src/jarvis_v2/automation/recovery_drill.py:29-31` | def backup(self, destination: str \| Path) -> BackupReceipt | 5 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.restore` | method | `src/jarvis_v2/automation/recovery_drill.py:33-35` | def restore(self, backup: str \| Path, destination: str \| Path) -> RestoreReceipt | 6 | active |
| `jarvis_v2.automation.recovery_drill.RecoveryDrill.replay_pending` | method | `src/jarvis_v2/automation/recovery_drill.py:37-50` | def replay_pending(self, consumer: str, effect: Callable[[Any], Mapping[str, Any]], *, limit: int \| None=None) -> list[DeliveryReceipt] | 2 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore` | class | `src/jarvis_v2/automation/scheduler.py:16-73` | class AutomationScheduleStore() | 1 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.__init__` | method | `src/jarvis_v2/automation/scheduler.py:19-25` | def __init__(self, database: str \| Path \| sqlite3.Connection, *, clock: Callable[[], datetime] \| None=None) -> None | 5 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.schedule_once` | method | `src/jarvis_v2/automation/scheduler.py:27-35` | def schedule_once(self, schedule_id: str, message: str, due_at: datetime \| str, *, timezone_name: str=UTC) -> Reminder | 1 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.schedule_daily` | method | `src/jarvis_v2/automation/scheduler.py:37-52` | def schedule_daily(self, schedule_id: str, message: str, local_time: time, *, timezone_name: str=ASIA_BANGKOK, start_date: date \| None=None) -> Reminder | 2 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.get` | method | `src/jarvis_v2/automation/scheduler.py:54-55` | def get(self, schedule_id: str) -> Reminder | 27 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.due` | method | `src/jarvis_v2/automation/scheduler.py:57-58` | def due(self, now: datetime \| None=None, *, limit: int=100) -> list[Reminder] | 4 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.acknowledge` | method | `src/jarvis_v2/automation/scheduler.py:60-61` | def acknowledge(self, schedule_id: str) -> Reminder | 4 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.cancel` | method | `src/jarvis_v2/automation/scheduler.py:63-64` | def cancel(self, schedule_id: str) -> Reminder | 0 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.close` | method | `src/jarvis_v2/automation/scheduler.py:66-67` | def close(self) -> None | 34 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.__enter__` | method | `src/jarvis_v2/automation/scheduler.py:69-70` | def __enter__(self) -> 'AutomationScheduleStore' | 1 | active |
| `jarvis_v2.automation.scheduler.AutomationScheduleStore.__exit__` | method | `src/jarvis_v2/automation/scheduler.py:72-73` | def __exit__(self, *_: object) -> None | 1 | active |
| `jarvis_v2.backend.authorization.AuthorizationError` | class | `src/jarvis_v2/backend/authorization.py:23-24` | class AuthorizationError(ValueError) | 2 | active |
| `jarvis_v2.backend.authorization._identifier` | function | `src/jarvis_v2/backend/authorization.py:27-30` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.authorization._scope_set` | function | `src/jarvis_v2/backend/authorization.py:33-44` | def _scope_set(target_module: str, scopes: Iterable[str], allowed: frozenset[str]) -> frozenset[str] | 0 | active |
| `jarvis_v2.backend.authorization._request_digest` | function | `src/jarvis_v2/backend/authorization.py:47-53` | def _request_digest(identity_id: str, target_module: str, scopes: frozenset[str]) -> str | 0 | active |
| `jarvis_v2.backend.authorization.AuthIdentity` | class | `src/jarvis_v2/backend/authorization.py:57-62` | class AuthIdentity() | 0 | active |
| `jarvis_v2.backend.authorization.OwnerApproval` | class | `src/jarvis_v2/backend/authorization.py:66-96` | class OwnerApproval() | 2 | active |
| `jarvis_v2.backend.authorization.OwnerApproval.for_grant` | method | `src/jarvis_v2/backend/authorization.py:77-96` | def for_grant(cls, approval_id: str, identity_id: str, target_module: str, scopes: Iterable[str]) -> 'OwnerApproval' | 2 | active |
| `jarvis_v2.backend.authorization.CapabilityGrant` | class | `src/jarvis_v2/backend/authorization.py:100-108` | class CapabilityGrant() | 0 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer` | class | `src/jarvis_v2/backend/authorization.py:111-231` | class AuthorizationServer() | 6 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.__init__` | method | `src/jarvis_v2/backend/authorization.py:114-118` | def __init__(self, registry: ModuleRegistry) -> None | 5 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.register_identity` | method | `src/jarvis_v2/backend/authorization.py:120-130` | def register_identity(self, identity_id: str, module: int \| str, *, kind: str='service') -> AuthIdentity | 6 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.grant` | method | `src/jarvis_v2/backend/authorization.py:132-164` | def grant(self, identity_id: str, target_module: int \| str, scopes: Iterable[str], *, approval: OwnerApproval \| None=None, grant_id: str \| None=None, ttl_seconds: int=300) -> Ca | 8 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.authorize` | method | `src/jarvis_v2/backend/authorization.py:166-187` | def authorize(self, identity_id: str, target_module: int \| str, scope: str, *, grant_id: str \| None=None) -> bool | 6 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.require` | method | `src/jarvis_v2/backend/authorization.py:189-198` | def require(self, identity_id: str, target_module: int \| str, scope: str, *, grant_id: str \| None=None) -> CapabilityGrant | 5 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.revoke` | method | `src/jarvis_v2/backend/authorization.py:200-204` | def revoke(self, grant_id: str) -> None | 5 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer.identities` | method | `src/jarvis_v2/backend/authorization.py:206-207` | def identities(self) -> MappingProxyType | 1 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer._identity` | method | `src/jarvis_v2/backend/authorization.py:209-214` | def _identity(self, identity_id: str) -> AuthIdentity | 0 | active |
| `jarvis_v2.backend.authorization.AuthorizationServer._check_approval` | method | `src/jarvis_v2/backend/authorization.py:217-231` | def _check_approval(identity: AuthIdentity, target_module: str, scopes: frozenset[str], approval: OwnerApproval \| None) -> None | 0 | active |
| `jarvis_v2.backend.backup.BackupError` | class | `src/jarvis_v2/backend/backup.py:26-27` | class BackupError(RuntimeError) | 2 | active |
| `jarvis_v2.backend.backup.BackupCipher` | class | `src/jarvis_v2/backend/backup.py:30-37` | class BackupCipher(Protocol) | 0 | active |
| `jarvis_v2.backend.backup.BackupCipher.seal` | method | `src/jarvis_v2/backend/backup.py:33-34` | def seal(self, payload: bytes) -> bytes | 1 | active |
| `jarvis_v2.backend.backup.BackupCipher.unseal` | method | `src/jarvis_v2/backend/backup.py:36-37` | def unseal(self, payload: bytes) -> bytes | 1 | active |
| `jarvis_v2.backend.backup.BackupReceipt` | class | `src/jarvis_v2/backend/backup.py:41-58` | class BackupReceipt() | 0 | active |
| `jarvis_v2.backend.backup.BackupReceipt.as_dict` | method | `src/jarvis_v2/backend/backup.py:57-58` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.backend.backup.RestoreReceipt` | class | `src/jarvis_v2/backend/backup.py:62-76` | class RestoreReceipt() | 0 | active |
| `jarvis_v2.backend.backup.RestoreReceipt.as_dict` | method | `src/jarvis_v2/backend/backup.py:75-76` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.backend.backup._path` | function | `src/jarvis_v2/backend/backup.py:79-82` | def _path(value: str \| Path, label: str) -> Path | 0 | active |
| `jarvis_v2.backend.backup._same_path` | function | `src/jarvis_v2/backend/backup.py:85-86` | def _same_path(left: Path, right: Path) -> bool | 0 | active |
| `jarvis_v2.backend.backup._sha256` | function | `src/jarvis_v2/backend/backup.py:89-94` | def _sha256(path: Path) -> str | 0 | active |
| `jarvis_v2.backend.backup._bounded_bytes` | function | `src/jarvis_v2/backend/backup.py:97-101` | def _bounded_bytes(path: Path, limit: int) -> bytes | 0 | active |
| `jarvis_v2.backend.backup._sqlite_uri` | function | `src/jarvis_v2/backend/backup.py:104-105` | def _sqlite_uri(path: Path) -> str | 0 | active |
| `jarvis_v2.backend.backup._sidecar` | function | `src/jarvis_v2/backend/backup.py:108-109` | def _sidecar(path: Path, suffix: str) -> Path | 0 | active |
| `jarvis_v2.backend.backup._validate_cipher` | function | `src/jarvis_v2/backend/backup.py:112-116` | def _validate_cipher(cipher: BackupCipher \| None) -> None | 0 | active |
| `jarvis_v2.backend.backup._seal` | function | `src/jarvis_v2/backend/backup.py:119-126` | def _seal(cipher: BackupCipher, payload: bytes) -> bytes | 0 | active |
| `jarvis_v2.backend.backup._unseal` | function | `src/jarvis_v2/backend/backup.py:129-136` | def _unseal(cipher: BackupCipher, payload: bytes) -> bytes | 0 | active |
| `jarvis_v2.backend.backup._exclusive_write` | function | `src/jarvis_v2/backend/backup.py:139-152` | def _exclusive_write(path: Path, payload: bytes) -> None | 0 | active |
| `jarvis_v2.backend.backup.BackupManager` | class | `src/jarvis_v2/backend/backup.py:155-348` | class BackupManager() | 3 | active |
| `jarvis_v2.backend.backup.BackupManager.__init__` | method | `src/jarvis_v2/backend/backup.py:158-161` | def __init__(self, *, max_backup_bytes: int=MAX_BACKUP_BYTES) -> None | 5 | active |
| `jarvis_v2.backend.backup.BackupManager.inspect` | method | `src/jarvis_v2/backend/backup.py:163-211` | def inspect(self, database: str \| Path) -> dict[str, Any] | 10 | active |
| `jarvis_v2.backend.backup.BackupManager._copy_sqlite` | method | `src/jarvis_v2/backend/backup.py:213-229` | def _copy_sqlite(self, source: Path, destination: Path) -> None | 0 | active |
| `jarvis_v2.backend.backup.BackupManager.create` | method | `src/jarvis_v2/backend/backup.py:231-283` | def create(self, source: str \| Path, destination: str \| Path, *, cipher: BackupCipher \| None=None) -> BackupReceipt | 8 | active |
| `jarvis_v2.backend.backup.BackupManager.restore` | method | `src/jarvis_v2/backend/backup.py:285-348` | def restore(self, backup: str \| Path, destination: str \| Path, *, cipher: BackupCipher \| None=None, expected_sha256: str \| None=None, expected_schema_version: int \| None=None) | 6 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapterError` | class | `src/jarvis_v2/backend/cloudflare_jobs.py:23-24` | class CloudflareJobAdapterError(ValueError) | 1 | active |
| `jarvis_v2.backend.cloudflare_jobs._identifier` | function | `src/jarvis_v2/backend/cloudflare_jobs.py:27-30` | def _identifier(value: object, label: str, limit: int=128) -> str | 0 | active |
| `jarvis_v2.backend.cloudflare_jobs._digest` | function | `src/jarvis_v2/backend/cloudflare_jobs.py:33-36` | def _digest(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobRecord` | class | `src/jarvis_v2/backend/cloudflare_jobs.py:40-90` | class CloudflareJobRecord() | 0 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobRecord.from_payload` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:57-90` | def from_payload(cls, value: object) -> 'CloudflareJobRecord' | 0 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter` | class | `src/jarvis_v2/backend/cloudflare_jobs.py:93-200` | class CloudflareJobAdapter() | 1 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter.__init__` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:100-118` | def __init__(self, base_url: str, token_provider: TokenProvider, *, transport: Transport \| None=None, timeout_seconds: float=10.0) -> None | 5 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter._urlopen` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:121-123` | def _urlopen(request: Request, timeout: float) -> tuple[int, bytes] | 0 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter.create` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:125-138` | def create(self, job: LocalAgentJob) -> CloudflareJobRecord | 8 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter.claim` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:142-152` | def claim(self, job_id: str, device_id: str, lease_id: str, *, lease_seconds: int=60) -> CloudflareJobRecord | 21 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter.complete` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:154-164` | def complete(self, job_id: str, lease_id: str, *, ok: bool, result_sha256: str) -> CloudflareJobRecord | 9 | active |
| `jarvis_v2.backend.cloudflare_jobs.CloudflareJobAdapter._call` | method | `src/jarvis_v2/backend/cloudflare_jobs.py:166-200` | def _call(self, path: str, payload: Mapping[str, object]) -> CloudflareJobRecord | 0 | active |
| `jarvis_v2.backend.code_index.CodeIndexError` | class | `src/jarvis_v2/backend/code_index.py:31-32` | class CodeIndexError(ValueError) | 1 | active |
| `jarvis_v2.backend.code_index._sha` | function | `src/jarvis_v2/backend/code_index.py:35-38` | def _sha(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.code_index._path` | function | `src/jarvis_v2/backend/code_index.py:41-48` | def _path(value: str) -> str | 0 | active |
| `jarvis_v2.backend.code_index._now` | function | `src/jarvis_v2/backend/code_index.py:51-52` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.code_index._content` | function | `src/jarvis_v2/backend/code_index.py:55-65` | def _content(value: str \| bytes) -> str | 0 | active |
| `jarvis_v2.backend.code_index._language` | function | `src/jarvis_v2/backend/code_index.py:68-72` | def _language(path: str, value: str \| None) -> str | 0 | active |
| `jarvis_v2.backend.code_index._sensitive` | function | `src/jarvis_v2/backend/code_index.py:75-76` | def _sensitive(path: str, content: str) -> bool | 0 | active |
| `jarvis_v2.backend.code_index._symbols` | function | `src/jarvis_v2/backend/code_index.py:79-103` | def _symbols(path: str, content: str, language: str) -> list[dict[str, Any]] | 0 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex` | class | `src/jarvis_v2/backend/code_index.py:106-263` | class RepositoryIndex() | 1 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.__init__` | method | `src/jarvis_v2/backend/code_index.py:109-152` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.__enter__` | method | `src/jarvis_v2/backend/code_index.py:154-155` | def __enter__(self) -> 'RepositoryIndex' | 1 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.__exit__` | method | `src/jarvis_v2/backend/code_index.py:157-158` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.index_file` | method | `src/jarvis_v2/backend/code_index.py:160-221` | def index_file(self, path: str, content: str \| bytes, *, blob_sha: str, source_sha: str, language: str \| None=None) -> dict[str, Any] | 1 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.search` | method | `src/jarvis_v2/backend/code_index.py:225-246` | def search(self, query: str, *, limit: int=20, source_sha: str \| None=None) -> list[dict[str, Any]] | 9 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.symbols` | method | `src/jarvis_v2/backend/code_index.py:248-259` | def symbols(self, *, path: str \| None=None, source_sha: str \| None=None) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.backend.code_index.RepositoryIndex.close` | method | `src/jarvis_v2/backend/code_index.py:261-263` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.connectors.ConnectorAuthorizationError` | class | `src/jarvis_v2/backend/connectors.py:20-21` | class ConnectorAuthorizationError(ValueError) | 2 | active |
| `jarvis_v2.backend.connectors._identifier` | function | `src/jarvis_v2/backend/connectors.py:24-27` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.connectors._connector` | function | `src/jarvis_v2/backend/connectors.py:30-33` | def _connector(value: str) -> str | 0 | active |
| `jarvis_v2.backend.connectors._scopes` | function | `src/jarvis_v2/backend/connectors.py:36-47` | def _scopes(connector: str, values: Iterable[str]) -> frozenset[str] | 0 | active |
| `jarvis_v2.backend.connectors.ConnectorGrant` | class | `src/jarvis_v2/backend/connectors.py:51-62` | class ConnectorGrant() | 0 | active |
| `jarvis_v2.backend.connectors.ConnectorGrant.as_dict` | method | `src/jarvis_v2/backend/connectors.py:61-62` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker` | class | `src/jarvis_v2/backend/connectors.py:65-189` | class ConnectorBroker() | 2 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.__init__` | method | `src/jarvis_v2/backend/connectors.py:73-75` | def __init__(self) -> None | 5 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.grant` | method | `src/jarvis_v2/backend/connectors.py:77-114` | def grant(self, identity_id: str, connector: str, scopes: Iterable[str], *, credential_ref: str \| None=None, grant_id: str \| None=None, ttl_seconds: int=300) -> ConnectorGrant | 8 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.authorize` | method | `src/jarvis_v2/backend/connectors.py:116-138` | def authorize(self, identity_id: str, connector: str, scope: str, *, grant_id: str \| None=None) -> bool | 6 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.require` | method | `src/jarvis_v2/backend/connectors.py:140-160` | def require(self, identity_id: str, connector: str, scope: str, *, grant_id: str \| None=None) -> ConnectorGrant | 5 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.revoke` | method | `src/jarvis_v2/backend/connectors.py:162-166` | def revoke(self, grant_id: str) -> None | 5 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.revoke_connector` | method | `src/jarvis_v2/backend/connectors.py:168-178` | def revoke_connector(self, identity_id: str, connector: str) -> int | 2 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker.grants` | method | `src/jarvis_v2/backend/connectors.py:180-186` | def grants(self) -> tuple[dict[str, object], ...] | 2 | active |
| `jarvis_v2.backend.connectors.ConnectorBroker._active` | method | `src/jarvis_v2/backend/connectors.py:188-189` | def _active(self, grant: ConnectorGrant) -> bool | 0 | active |
| `jarvis_v2.backend.context.ContextPackError` | class | `src/jarvis_v2/backend/context.py:18-19` | class ContextPackError(ValueError) | 2 | active |
| `jarvis_v2.backend.context.estimate_tokens` | function | `src/jarvis_v2/backend/context.py:22-27` | def estimate_tokens(value: str) -> int | 1 | active |
| `jarvis_v2.backend.context._json` | function | `src/jarvis_v2/backend/context.py:30-38` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.context._reject_sensitive_keys` | function | `src/jarvis_v2/backend/context.py:41-49` | def _reject_sensitive_keys(value: object, label: str) -> None | 0 | active |
| `jarvis_v2.backend.context._sequence` | function | `src/jarvis_v2/backend/context.py:52-59` | def _sequence(value: Sequence[Any] \| None, label: str) -> list[Any] | 0 | active |
| `jarvis_v2.backend.context.ContextPacker` | class | `src/jarvis_v2/backend/context.py:62-141` | class ContextPacker() | 2 | active |
| `jarvis_v2.backend.context.ContextPacker.__init__` | method | `src/jarvis_v2/backend/context.py:65-67` | def __init__(self, *, default_max_tokens: int=DEFAULT_CONTEXT_TOKENS) -> None | 5 | active |
| `jarvis_v2.backend.context.ContextPacker.pack` | method | `src/jarvis_v2/backend/context.py:69-126` | def pack(self, requirements: object, policy: object, recent_receipts: Sequence[Any] \| None=None, history: Sequence[Any] \| None=None, *, max_tokens: int \| None=None) -> dict[str, | 2 | active |
| `jarvis_v2.backend.context.ContextPacker._packet` | method | `src/jarvis_v2/backend/context.py:129-136` | def _packet(protected: Mapping[str, Any], history: list[Any], *, dropped: int) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.context.ContextPacker._validate_budget` | method | `src/jarvis_v2/backend/context.py:139-141` | def _validate_budget(value: int) -> None | 0 | active |
| `jarvis_v2.backend.context.pack_context` | function | `src/jarvis_v2/backend/context.py:144-155` | def pack_context(requirements: object, policy: object, recent_receipts: Sequence[Any] \| None=None, history: Sequence[Any] \| None=None, *, max_tokens: int=DEFAULT_CONTEXT_TOKENS)  | 0 | active |
| `jarvis_v2.backend.conversation.ConversationStoreError` | class | `src/jarvis_v2/backend/conversation.py:23-24` | class ConversationStoreError(ValueError) | 1 | active |
| `jarvis_v2.backend.conversation._identifier` | function | `src/jarvis_v2/backend/conversation.py:27-30` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.conversation._now` | function | `src/jarvis_v2/backend/conversation.py:33-36` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.conversation._json` | function | `src/jarvis_v2/backend/conversation.py:39-52` | def _json(value: object, *, limit: int, label: str) -> str | 0 | active |
| `jarvis_v2.backend.conversation._mapping` | function | `src/jarvis_v2/backend/conversation.py:55-60` | def _mapping(value: Mapping[str, object] \| None, label: str) -> dict[str, object] | 0 | active |
| `jarvis_v2.backend.conversation._effects` | function | `src/jarvis_v2/backend/conversation.py:63-77` | def _effects(value: Sequence[Mapping[str, object]] \| None) -> tuple[list[dict[str, object]], str] | 0 | active |
| `jarvis_v2.backend.conversation.ConversationStore` | class | `src/jarvis_v2/backend/conversation.py:80-342` | class ConversationStore() | 4 | active |
| `jarvis_v2.backend.conversation.ConversationStore.__init__` | method | `src/jarvis_v2/backend/conversation.py:89-124` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.backend.conversation.ConversationStore.__enter__` | method | `src/jarvis_v2/backend/conversation.py:126-127` | def __enter__(self) -> 'ConversationStore' | 1 | active |
| `jarvis_v2.backend.conversation.ConversationStore.__exit__` | method | `src/jarvis_v2/backend/conversation.py:129-130` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.conversation.ConversationStore.close` | method | `src/jarvis_v2/backend/conversation.py:132-134` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.conversation.ConversationStore.create_conversation` | method | `src/jarvis_v2/backend/conversation.py:136-173` | def create_conversation(self, conversation_id: str \| None=None, *, metadata: Mapping[str, object] \| None=None) -> dict[str, Any] | 4 | active |
| `jarvis_v2.backend.conversation.ConversationStore.open_conversation` | method | `src/jarvis_v2/backend/conversation.py:175-189` | def open_conversation(self, conversation_id: str, *, metadata: Mapping[str, object] \| None=None) -> dict[str, Any] | 1 | active |
| `jarvis_v2.backend.conversation.ConversationStore.append_turn` | method | `src/jarvis_v2/backend/conversation.py:191-263` | def append_turn(self, conversation_id: str, *, role: str, provider: str, content: str, model: str='', tool_effects: Sequence[Mapping[str, object]] \| None=None, idempotency_key: st | 1 | active |
| `jarvis_v2.backend.conversation.ConversationStore.get_conversation` | method | `src/jarvis_v2/backend/conversation.py:265-272` | def get_conversation(self, conversation_id: str) -> dict[str, Any] | 1 | active |
| `jarvis_v2.backend.conversation.ConversationStore.list_turns` | method | `src/jarvis_v2/backend/conversation.py:274-286` | def list_turns(self, conversation_id: str, *, limit: int=100) -> list[dict[str, Any]] | 4 | active |
| `jarvis_v2.backend.conversation.ConversationStore._same_turn` | method | `src/jarvis_v2/backend/conversation.py:289-303` | def _same_turn(row: sqlite3.Row, role: str, provider: str, model: str, content: str, effects_json: str) -> bool | 0 | active |
| `jarvis_v2.backend.conversation.ConversationStore._turn` | method | `src/jarvis_v2/backend/conversation.py:306-324` | def _turn(row: sqlite3.Row) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.conversation.ConversationStore._conversation` | method | `src/jarvis_v2/backend/conversation.py:326-342` | def _conversation(self, row: sqlite3.Row, *, include_turns: bool) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.effects.EffectJournalError` | class | `src/jarvis_v2/backend/effects.py:18-19` | class EffectJournalError(ValueError) | 1 | active |
| `jarvis_v2.backend.effects._identifier` | function | `src/jarvis_v2/backend/effects.py:22-25` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.effects._text` | function | `src/jarvis_v2/backend/effects.py:28-33` | def _text(value: str, label: str, limit: int=512) -> str | 2 | active |
| `jarvis_v2.backend.effects._json` | function | `src/jarvis_v2/backend/effects.py:36-45` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.effects._now` | function | `src/jarvis_v2/backend/effects.py:48-49` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.effects.EffectJournal` | class | `src/jarvis_v2/backend/effects.py:52-276` | class EffectJournal() | 3 | active |
| `jarvis_v2.backend.effects.EffectJournal.__init__` | method | `src/jarvis_v2/backend/effects.py:59-85` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.backend.effects.EffectJournal.__enter__` | method | `src/jarvis_v2/backend/effects.py:87-88` | def __enter__(self) -> 'EffectJournal' | 1 | active |
| `jarvis_v2.backend.effects.EffectJournal.__exit__` | method | `src/jarvis_v2/backend/effects.py:90-91` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.effects.EffectJournal.prepare` | method | `src/jarvis_v2/backend/effects.py:93-150` | def prepare(self, effect_id: str, task_id: str, *, operation: str, target: str, request: Mapping[str, object] \| None=None) -> dict[str, Any] | 10 | active |
| `jarvis_v2.backend.effects.EffectJournal.complete` | method | `src/jarvis_v2/backend/effects.py:152-153` | def complete(self, effect_id: str, result: Mapping[str, object] \| None=None) -> dict[str, Any] | 9 | active |
| `jarvis_v2.backend.effects.EffectJournal.fail` | method | `src/jarvis_v2/backend/effects.py:155-156` | def fail(self, effect_id: str, result: Mapping[str, object] \| None=None) -> dict[str, Any] | 4 | active |
| `jarvis_v2.backend.effects.EffectJournal.reconcile_pending` | method | `src/jarvis_v2/backend/effects.py:158-172` | def reconcile_pending(self) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.backend.effects.EffectJournal.get` | method | `src/jarvis_v2/backend/effects.py:174-181` | def get(self, effect_id: str) -> dict[str, Any] | 27 | active |
| `jarvis_v2.backend.effects.EffectJournal.pending` | method | `src/jarvis_v2/backend/effects.py:183-190` | def pending(self, *, limit: int=100) -> list[dict[str, Any]] | 27 | active |
| `jarvis_v2.backend.effects.EffectJournal._finish` | method | `src/jarvis_v2/backend/effects.py:192-233` | def _finish(self, effect_id: str, status: str, result: Mapping[str, object] \| None) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.effects.EffectJournal._check_identity` | method | `src/jarvis_v2/backend/effects.py:236-249` | def _check_identity(row: sqlite3.Row, task_id: str, operation: str, target: str, request_json: str) -> None | 0 | active |
| `jarvis_v2.backend.effects.EffectJournal._snapshot` | method | `src/jarvis_v2/backend/effects.py:252-272` | def _snapshot(row: sqlite3.Row, *, execution_permitted: bool) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.effects.EffectJournal.close` | method | `src/jarvis_v2/backend/effects.py:274-276` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.event_bus.EventBusError` | class | `src/jarvis_v2/backend/event_bus.py:24-25` | class EventBusError(ValueError) | 2 | active |
| `jarvis_v2.backend.event_bus.DeliveryInProgress` | class | `src/jarvis_v2/backend/event_bus.py:28-29` | class DeliveryInProgress(EventBusError) | 0 | active |
| `jarvis_v2.backend.event_bus.DeliveryError` | class | `src/jarvis_v2/backend/event_bus.py:32-33` | class DeliveryError(EventBusError) | 1 | active |
| `jarvis_v2.backend.event_bus.EventEnvelope` | class | `src/jarvis_v2/backend/event_bus.py:37-53` | class EventEnvelope() | 0 | active |
| `jarvis_v2.backend.event_bus.EventEnvelope.canonical_payload` | method | `src/jarvis_v2/backend/event_bus.py:52-53` | def canonical_payload(self) -> str | 0 | active |
| `jarvis_v2.backend.event_bus.DeliveryReceipt` | class | `src/jarvis_v2/backend/event_bus.py:57-63` | class DeliveryReceipt() | 0 | active |
| `jarvis_v2.backend.event_bus._now` | function | `src/jarvis_v2/backend/event_bus.py:94-95` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.event_bus._identifier` | function | `src/jarvis_v2/backend/event_bus.py:98-101` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.event_bus._json` | function | `src/jarvis_v2/backend/event_bus.py:104-111` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.event_bus.EventBus` | class | `src/jarvis_v2/backend/event_bus.py:114-343` | class EventBus() | 7 | active |
| `jarvis_v2.backend.event_bus.EventBus.__init__` | method | `src/jarvis_v2/backend/event_bus.py:117-120` | def __init__(self, path: str \| Path) -> None | 5 | active |
| `jarvis_v2.backend.event_bus.EventBus.close` | method | `src/jarvis_v2/backend/event_bus.py:122-123` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.event_bus.EventBus.__enter__` | method | `src/jarvis_v2/backend/event_bus.py:125-126` | def __enter__(self) -> 'EventBus' | 1 | active |
| `jarvis_v2.backend.event_bus.EventBus.__exit__` | method | `src/jarvis_v2/backend/event_bus.py:128-129` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.event_bus.EventBus.publish` | method | `src/jarvis_v2/backend/event_bus.py:131-211` | def publish(self, event_type: str, producer: str, aggregate_id: str, sequence: int, payload: Mapping[str, Any], *, correlation_id: str, causation_id: str \| None=None, privacy_scop | 6 | active |
| `jarvis_v2.backend.event_bus.EventBus.pending` | method | `src/jarvis_v2/backend/event_bus.py:213-225` | def pending(self, consumer: str, *, limit: int=100) -> list[EventEnvelope] | 27 | active |
| `jarvis_v2.backend.event_bus.EventBus.deliver` | method | `src/jarvis_v2/backend/event_bus.py:227-310` | def deliver(self, consumer: str, event_id: str, effect: Callable[[EventEnvelope], Mapping[str, Any]]) -> DeliveryReceipt | 4 | active |
| `jarvis_v2.backend.event_bus.EventBus._same_event` | method | `src/jarvis_v2/backend/event_bus.py:313-320` | def _same_event(left: EventEnvelope, right: EventEnvelope) -> bool | 0 | active |
| `jarvis_v2.backend.event_bus.EventBus._event` | method | `src/jarvis_v2/backend/event_bus.py:323-336` | def _event(row: sqlite3.Row) -> EventEnvelope | 0 | active |
| `jarvis_v2.backend.event_bus.EventBus._receipt` | method | `src/jarvis_v2/backend/event_bus.py:339-343` | def _receipt(row: sqlite3.Row) -> DeliveryReceipt | 0 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationSchedulerError` | class | `src/jarvis_v2/backend/generation_scheduler.py:14-15` | class GenerationSchedulerError(ValueError) | 1 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationRequest` | class | `src/jarvis_v2/backend/generation_scheduler.py:19-26` | class GenerationRequest() | 1 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationLease` | class | `src/jarvis_v2/backend/generation_scheduler.py:30-38` | class GenerationLease() | 0 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler` | class | `src/jarvis_v2/backend/generation_scheduler.py:41-144` | class GenerationScheduler() | 1 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.__init__` | method | `src/jarvis_v2/backend/generation_scheduler.py:49-62` | def __init__(self, quota_units: int, *, slots: Iterable[str]=('cpu',), device_limits: Mapping[str, int] \| None=None) -> None | 5 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.quota_remaining` | method | `src/jarvis_v2/backend/generation_scheduler.py:65-66` | def quota_remaining(self) -> int | 4 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.submit` | method | `src/jarvis_v2/backend/generation_scheduler.py:68-82` | def submit(self, request: GenerationRequest) -> str | 6 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.claim_next` | method | `src/jarvis_v2/backend/generation_scheduler.py:84-115` | def claim_next(self) -> GenerationLease \| None | 1 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.finish` | method | `src/jarvis_v2/backend/generation_scheduler.py:117-121` | def finish(self, lease: GenerationLease) -> None | 12 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler.snapshot` | method | `src/jarvis_v2/backend/generation_scheduler.py:123-129` | def snapshot(self) -> dict[str, object] | 17 | active |
| `jarvis_v2.backend.generation_scheduler.GenerationScheduler._validate_request` | method | `src/jarvis_v2/backend/generation_scheduler.py:132-144` | def _validate_request(request: GenerationRequest) -> None | 0 | active |
| `jarvis_v2.backend.handoff.HandoffError` | class | `src/jarvis_v2/backend/handoff.py:19-20` | class HandoffError(ValueError) | 2 | active |
| `jarvis_v2.backend.handoff._identifier` | function | `src/jarvis_v2/backend/handoff.py:23-26` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.handoff._json` | function | `src/jarvis_v2/backend/handoff.py:29-38` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.handoff._scopes` | function | `src/jarvis_v2/backend/handoff.py:41-54` | def _scopes(values: Iterable[str]) -> list[str] | 0 | active |
| `jarvis_v2.backend.handoff._effects` | function | `src/jarvis_v2/backend/handoff.py:57-68` | def _effects(values: Iterable[Mapping[str, object]]) -> list[dict[str, object]] | 0 | active |
| `jarvis_v2.backend.handoff._now` | function | `src/jarvis_v2/backend/handoff.py:71-72` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.handoff.HandoffStore` | class | `src/jarvis_v2/backend/handoff.py:75-217` | class HandoffStore() | 2 | active |
| `jarvis_v2.backend.handoff.HandoffStore.__init__` | method | `src/jarvis_v2/backend/handoff.py:78-100` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.backend.handoff.HandoffStore.__enter__` | method | `src/jarvis_v2/backend/handoff.py:102-103` | def __enter__(self) -> 'HandoffStore' | 1 | active |
| `jarvis_v2.backend.handoff.HandoffStore.__exit__` | method | `src/jarvis_v2/backend/handoff.py:105-106` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.handoff.HandoffStore.handoff` | method | `src/jarvis_v2/backend/handoff.py:108-173` | def handoff(self, task_id: str, handoff_id: str, *, source_provider: str, target_provider: str, permission_scopes: Iterable[str], tool_effects: Iterable[Mapping[str, object]]=(), c | 12 | active |
| `jarvis_v2.backend.handoff.HandoffStore.get` | method | `src/jarvis_v2/backend/handoff.py:175-182` | def get(self, handoff_id: str) -> dict[str, Any] | 27 | active |
| `jarvis_v2.backend.handoff.HandoffStore.list_for_task` | method | `src/jarvis_v2/backend/handoff.py:184-192` | def list_for_task(self, task_id: str, *, limit: int=100) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.backend.handoff.HandoffStore._snapshot` | method | `src/jarvis_v2/backend/handoff.py:195-213` | def _snapshot(row: sqlite3.Row) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.handoff.HandoffStore.close` | method | `src/jarvis_v2/backend/handoff.py:215-217` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.linux_service.LinuxServiceError` | class | `src/jarvis_v2/backend/linux_service.py:15-16` | class LinuxServiceError(ValueError) | 1 | active |
| `jarvis_v2.backend.linux_service._argument` | function | `src/jarvis_v2/backend/linux_service.py:19-22` | def _argument(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile` | class | `src/jarvis_v2/backend/linux_service.py:26-71` | class LinuxServiceProfile() | 1 | active |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile.__post_init__` | method | `src/jarvis_v2/backend/linux_service.py:34-49` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.linux_service.LinuxServiceProfile.render` | method | `src/jarvis_v2/backend/linux_service.py:51-71` | def render(self) -> str | 3 | active |
| `jarvis_v2.backend.linux_service.startup_decision` | function | `src/jarvis_v2/backend/linux_service.py:74-89` | def startup_decision(profile: LinuxServiceProfile, active_units: Mapping[str, object], health_ok: bool) -> str | 1 | active |
| `jarvis_v2.backend.module_manifest.ManifestValidationError` | class | `src/jarvis_v2/backend/module_manifest.py:15-16` | class ManifestValidationError(ValueError) | 2 | active |
| `jarvis_v2.backend.module_manifest.ModuleManifest` | class | `src/jarvis_v2/backend/module_manifest.py:64-71` | class ModuleManifest() | 1 | active |
| `jarvis_v2.backend.module_manifest._fail` | function | `src/jarvis_v2/backend/module_manifest.py:74-75` | def _fail(message: str) -> None | 0 | active |
| `jarvis_v2.backend.module_manifest._strings` | function | `src/jarvis_v2/backend/module_manifest.py:78-90` | def _strings(value: Any, field: str, *, unique: bool=True, allow_empty: bool=False) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.backend.module_manifest.validate_module_manifest` | function | `src/jarvis_v2/backend/module_manifest.py:93-154` | def validate_module_manifest(manifest: ModuleManifest \| Mapping[str, Any]) -> ModuleManifest | 2 | active |
| `jarvis_v2.backend.module_manifest.validate_module_manifests` | function | `src/jarvis_v2/backend/module_manifest.py:157-172` | def validate_module_manifests(manifests: list[Any] \| tuple[Any, ...]) -> tuple[ModuleManifest, ...] | 2 | active |
| `jarvis_v2.backend.ollama_profile.OllamaProfileError` | class | `src/jarvis_v2/backend/ollama_profile.py:19-20` | class OllamaProfileError(ValueError) | 1 | active |
| `jarvis_v2.backend.ollama_profile._non_negative_int` | function | `src/jarvis_v2/backend/ollama_profile.py:23-26` | def _non_negative_int(value: Any, label: str) -> int | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaInferenceProfile` | class | `src/jarvis_v2/backend/ollama_profile.py:30-60` | class OllamaInferenceProfile() | 2 | active |
| `jarvis_v2.backend.ollama_profile.OllamaInferenceProfile.__post_init__` | method | `src/jarvis_v2/backend/ollama_profile.py:39-49` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaInferenceProfile.options` | method | `src/jarvis_v2/backend/ollama_profile.py:51-57` | def options(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.backend.ollama_profile.OllamaInferenceProfile.as_dict` | method | `src/jarvis_v2/backend/ollama_profile.py:59-60` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.ollama_profile.OllamaProbeEvidence` | class | `src/jarvis_v2/backend/ollama_profile.py:64-100` | class OllamaProbeEvidence() | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaProbeEvidence.__post_init__` | method | `src/jarvis_v2/backend/ollama_profile.py:74-88` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaProbeEvidence.as_dict` | method | `src/jarvis_v2/backend/ollama_profile.py:90-100` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.ollama_profile.OllamaErrorEvidence` | class | `src/jarvis_v2/backend/ollama_profile.py:104-117` | class OllamaErrorEvidence() | 1 | active |
| `jarvis_v2.backend.ollama_profile.OllamaErrorEvidence.__post_init__` | method | `src/jarvis_v2/backend/ollama_profile.py:110-114` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaErrorEvidence.as_dict` | method | `src/jarvis_v2/backend/ollama_profile.py:116-117` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.ollama_profile.OllamaTelemetry` | class | `src/jarvis_v2/backend/ollama_profile.py:121-171` | class OllamaTelemetry() | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaTelemetry.__post_init__` | method | `src/jarvis_v2/backend/ollama_profile.py:135-157` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.ollama_profile.OllamaTelemetry.as_dict` | method | `src/jarvis_v2/backend/ollama_profile.py:159-171` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.ollama_profile._duration` | function | `src/jarvis_v2/backend/ollama_profile.py:174-178` | def _duration(payload: Mapping[str, object], key: str) -> int \| None | 0 | active |
| `jarvis_v2.backend.ollama_profile._rate` | function | `src/jarvis_v2/backend/ollama_profile.py:181-184` | def _rate(count: int, duration_ns: int \| None) -> float \| None | 0 | active |
| `jarvis_v2.backend.ollama_profile.classify_ollama_error` | function | `src/jarvis_v2/backend/ollama_profile.py:187-195` | def classify_ollama_error(payload: Mapping[str, object]) -> OllamaErrorEvidence | 1 | active |
| `jarvis_v2.backend.ollama_profile.parse_ollama_telemetry` | function | `src/jarvis_v2/backend/ollama_profile.py:198-238` | def parse_ollama_telemetry(payload: Mapping[str, object], profile: OllamaInferenceProfile) -> OllamaTelemetry | 2 | active |
| `jarvis_v2.backend.ollama_profile.parse_ollama_probe` | function | `src/jarvis_v2/backend/ollama_profile.py:241-268` | def parse_ollama_probe(payload: Mapping[str, object], profile: OllamaInferenceProfile, *, expected_marker: str='READY', artifact_sha256: str \| None=None) -> OllamaProbeEvidence | 1 | active |
| `jarvis_v2.backend.protocol_adapters.AdapterError` | class | `src/jarvis_v2/backend/protocol_adapters.py:20-21` | class AdapterError(ValueError) | 1 | active |
| `jarvis_v2.backend.protocol_adapters._bounded` | function | `src/jarvis_v2/backend/protocol_adapters.py:24-29` | def _bounded(value: str, pattern: re.Pattern[str], label: str, *, empty: bool=False) -> str | 0 | active |
| `jarvis_v2.backend.protocol_adapters._json` | function | `src/jarvis_v2/backend/protocol_adapters.py:32-39` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.backend.protocol_adapters._object` | function | `src/jarvis_v2/backend/protocol_adapters.py:42-47` | def _object(value: object, label: str) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.protocol_adapters._text` | function | `src/jarvis_v2/backend/protocol_adapters.py:50-55` | def _text(value: object, label: str, *, required: bool=True) -> str | 2 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolMessage` | class | `src/jarvis_v2/backend/protocol_adapters.py:59-71` | class ProtocolMessage() | 1 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolMessage.__post_init__` | method | `src/jarvis_v2/backend/protocol_adapters.py:65-68` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolMessage.as_dict` | method | `src/jarvis_v2/backend/protocol_adapters.py:70-71` | def as_dict(self) -> dict[str, str] | 18 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolToolCall` | class | `src/jarvis_v2/backend/protocol_adapters.py:75-87` | class ProtocolToolCall() | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolToolCall.__post_init__` | method | `src/jarvis_v2/backend/protocol_adapters.py:82-87` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolRequest` | class | `src/jarvis_v2/backend/protocol_adapters.py:91-113` | class ProtocolRequest() | 1 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolRequest.__post_init__` | method | `src/jarvis_v2/backend/protocol_adapters.py:100-113` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolResponse` | class | `src/jarvis_v2/backend/protocol_adapters.py:117-136` | class ProtocolResponse() | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolResponse.__post_init__` | method | `src/jarvis_v2/backend/protocol_adapters.py:127-136` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter` | class | `src/jarvis_v2/backend/protocol_adapters.py:139-170` | class ProtocolAdapter() | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter.__init__` | method | `src/jarvis_v2/backend/protocol_adapters.py:144-145` | def __init__(self, provider_id: str) | 5 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter.encode` | method | `src/jarvis_v2/backend/protocol_adapters.py:147-150` | def encode(self, request: ProtocolRequest) -> dict[str, Any] | 10 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter.decode` | method | `src/jarvis_v2/backend/protocol_adapters.py:152-154` | def decode(self, payload: Mapping[str, Any]) -> ProtocolResponse | 4 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter.invoke` | method | `src/jarvis_v2/backend/protocol_adapters.py:156-164` | def invoke(self, request: ProtocolRequest, transport: Callable[[Mapping[str, Any]], Mapping[str, Any]]) -> ProtocolResponse | 2 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter._encode` | method | `src/jarvis_v2/backend/protocol_adapters.py:166-167` | def _encode(self, request: ProtocolRequest) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ProtocolAdapter._decode` | method | `src/jarvis_v2/backend/protocol_adapters.py:169-170` | def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ResponsesAdapter` | class | `src/jarvis_v2/backend/protocol_adapters.py:173-223` | class ResponsesAdapter(ProtocolAdapter) | 1 | active |
| `jarvis_v2.backend.protocol_adapters.ResponsesAdapter._encode` | method | `src/jarvis_v2/backend/protocol_adapters.py:178-186` | def _encode(self, request: ProtocolRequest) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ResponsesAdapter._decode` | method | `src/jarvis_v2/backend/protocol_adapters.py:188-214` | def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ResponsesAdapter._function_call` | method | `src/jarvis_v2/backend/protocol_adapters.py:217-223` | def _function_call(entry: Mapping[str, Any]) -> ProtocolToolCall | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ChatCompletionsAdapter` | class | `src/jarvis_v2/backend/protocol_adapters.py:226-266` | class ChatCompletionsAdapter(ProtocolAdapter) | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ChatCompletionsAdapter._encode` | method | `src/jarvis_v2/backend/protocol_adapters.py:231-239` | def _encode(self, request: ProtocolRequest) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ChatCompletionsAdapter._decode` | method | `src/jarvis_v2/backend/protocol_adapters.py:241-257` | def _decode(self, payload: Mapping[str, Any]) -> ProtocolResponse | 0 | active |
| `jarvis_v2.backend.protocol_adapters.ChatCompletionsAdapter._tool_call` | method | `src/jarvis_v2/backend/protocol_adapters.py:260-266` | def _tool_call(entry: Mapping[str, Any]) -> ProtocolToolCall | 0 | active |
| `jarvis_v2.backend.protocol_adapters._arguments` | function | `src/jarvis_v2/backend/protocol_adapters.py:269-275` | def _arguments(value: object) -> Mapping[str, Any] | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistryError` | class | `src/jarvis_v2/backend/provider_registry.py:19-20` | class ProviderRegistryError(ValueError) | 1 | active |
| `jarvis_v2.backend.provider_registry._bounded` | function | `src/jarvis_v2/backend/provider_registry.py:23-26` | def _bounded(value: str, pattern: re.Pattern[str], label: str) -> str | 0 | active |
| `jarvis_v2.backend.provider_registry._tools` | function | `src/jarvis_v2/backend/provider_registry.py:29-35` | def _tools(values: Iterable[str]) -> frozenset[str] | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderCapability` | class | `src/jarvis_v2/backend/provider_registry.py:39-65` | class ProviderCapability() | 3 | active |
| `jarvis_v2.backend.provider_registry.ProviderCapability.__post_init__` | method | `src/jarvis_v2/backend/provider_registry.py:51-65` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRequirements` | class | `src/jarvis_v2/backend/provider_registry.py:69-95` | class ProviderRequirements() | 3 | active |
| `jarvis_v2.backend.provider_registry.ProviderRequirements.__post_init__` | method | `src/jarvis_v2/backend/provider_registry.py:80-95` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderResolution` | class | `src/jarvis_v2/backend/provider_registry.py:99-107` | class ProviderResolution() | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry` | class | `src/jarvis_v2/backend/provider_registry.py:110-179` | class ProviderRegistry() | 3 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry.__init__` | method | `src/jarvis_v2/backend/provider_registry.py:113-116` | def __init__(self, capabilities: Iterable[ProviderCapability]=()) -> None | 5 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry.providers` | method | `src/jarvis_v2/backend/provider_registry.py:119-120` | def providers(self) -> MappingProxyType | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry.register` | method | `src/jarvis_v2/backend/provider_registry.py:122-129` | def register(self, capability: ProviderCapability) -> ProviderCapability | 1 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry.negotiate` | method | `src/jarvis_v2/backend/provider_registry.py:131-150` | def negotiate(self, requirements: ProviderRequirements) -> ProviderResolution | 1 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry._incompatibility` | method | `src/jarvis_v2/backend/provider_registry.py:153-166` | def _incompatibility(capability: ProviderCapability, requirements: ProviderRequirements) -> str \| None | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry._blocked` | method | `src/jarvis_v2/backend/provider_registry.py:169-173` | def _blocked(cls, requirements: ProviderRequirements, reason: str) -> ProviderResolution | 0 | active |
| `jarvis_v2.backend.provider_registry.ProviderRegistry._first_reason` | method | `src/jarvis_v2/backend/provider_registry.py:176-179` | def _first_reason(cls, candidates: list[ProviderCapability], requirements: ProviderRequirements) -> str | 0 | active |
| `jarvis_v2.backend.reranking.RerankingError` | class | `src/jarvis_v2/backend/reranking.py:15-16` | class RerankingError(ValueError) | 0 | active |
| `jarvis_v2.backend.reranking.HardwareBudget` | class | `src/jarvis_v2/backend/reranking.py:20-39` | class HardwareBudget() | 1 | active |
| `jarvis_v2.backend.reranking.HardwareBudget.__post_init__` | method | `src/jarvis_v2/backend/reranking.py:29-39` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.reranking.RerankResult` | class | `src/jarvis_v2/backend/reranking.py:43-62` | class RerankResult(Sequence[Mapping[str, Any]]) | 0 | active |
| `jarvis_v2.backend.reranking.RerankResult.__len__` | method | `src/jarvis_v2/backend/reranking.py:51-52` | def __len__(self) -> int | 0 | active |
| `jarvis_v2.backend.reranking.RerankResult.__getitem__` | method | `src/jarvis_v2/backend/reranking.py:54-55` | def __getitem__(self, index: int \| slice) -> Mapping[str, Any] \| tuple[Mapping[str, Any], ...] | 0 | active |
| `jarvis_v2.backend.reranking.RerankResult.__iter__` | method | `src/jarvis_v2/backend/reranking.py:57-58` | def __iter__(self) | 0 | active |
| `jarvis_v2.backend.reranking.RerankResult.mode` | method | `src/jarvis_v2/backend/reranking.py:61-62` | def mode(self) -> str | 11 | active |
| `jarvis_v2.backend.reranking._keywords` | function | `src/jarvis_v2/backend/reranking.py:68-69` | def _keywords(value: str) -> list[str] | 0 | active |
| `jarvis_v2.backend.reranking._keyword_order` | function | `src/jarvis_v2/backend/reranking.py:72-83` | def _keyword_order(query: str, candidates: tuple[Mapping[str, Any], ...], text_key: str) -> tuple[Mapping[str, Any], ...] | 0 | active |
| `jarvis_v2.backend.reranking._hashed_embedding` | function | `src/jarvis_v2/backend/reranking.py:86-95` | def _hashed_embedding(text: str, dimensions: int) -> tuple[float, ...] | 0 | active |
| `jarvis_v2.backend.reranking._cosine` | function | `src/jarvis_v2/backend/reranking.py:98-99` | def _cosine(left: Sequence[float], right: Sequence[float]) -> float | 0 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker` | class | `src/jarvis_v2/backend/reranking.py:102-239` | class LocalEmbeddingReranker() | 2 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker.__init__` | method | `src/jarvis_v2/backend/reranking.py:110-127` | def __init__(self, *, budget: HardwareBudget \| None=None, embedder: Callable[[str], Sequence[float]] \| None=None, enabled: bool=True, text_key: str='snippet') -> None | 5 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker.rerank` | method | `src/jarvis_v2/backend/reranking.py:129-181` | def rerank(self, query: str, candidates: Iterable[Mapping[str, Any]]) -> RerankResult | 1 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker._fallback` | method | `src/jarvis_v2/backend/reranking.py:185-192` | def _fallback(self, query: str, candidates: tuple[Mapping[str, Any], ...], reason: str, started: float) -> RerankResult | 0 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker._bounded_embed` | method | `src/jarvis_v2/backend/reranking.py:195-225` | def _bounded_embed(embedder: Callable[[str], Sequence[float]], text: str, timeout: float) -> tuple[tuple[float, ...] \| None, str \| None] | 0 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker._bounded_embed.invoke` | function | `src/jarvis_v2/backend/reranking.py:202-206` | def invoke() -> None | 2 | active |
| `jarvis_v2.backend.reranking.LocalEmbeddingReranker._result` | method | `src/jarvis_v2/backend/reranking.py:227-239` | def _result(self, items: tuple[Mapping[str, Any], ...], used_embeddings: bool, fallback_reason: str \| None, started: float) -> RerankResult | 0 | active |
| `jarvis_v2.backend.retrieval.RetrievalError` | class | `src/jarvis_v2/backend/retrieval.py:20-21` | class RetrievalError(ValueError) | 1 | active |
| `jarvis_v2.backend.retrieval._identifier` | function | `src/jarvis_v2/backend/retrieval.py:24-27` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.retrieval._text` | function | `src/jarvis_v2/backend/retrieval.py:30-35` | def _text(value: str, label: str, limit: int) -> str | 2 | active |
| `jarvis_v2.backend.retrieval._now` | function | `src/jarvis_v2/backend/retrieval.py:38-39` | def _now() -> str | 0 | active |
| `jarvis_v2.backend.retrieval.DocumentStore` | class | `src/jarvis_v2/backend/retrieval.py:42-253` | class DocumentStore() | 1 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.__init__` | method | `src/jarvis_v2/backend/retrieval.py:45-80` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.__enter__` | method | `src/jarvis_v2/backend/retrieval.py:82-83` | def __enter__(self) -> 'DocumentStore' | 1 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.__exit__` | method | `src/jarvis_v2/backend/retrieval.py:85-86` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.add_document` | method | `src/jarvis_v2/backend/retrieval.py:88-174` | def add_document(self, document_id: str, content: str, *, source_id: str, source_uri: str, access_scope: str, citation: str, title: str='', observed_at: str \| None=None, metadata: | 1 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.search` | method | `src/jarvis_v2/backend/retrieval.py:176-216` | def search(self, query: str, *, access_scope: str, source_id: str \| None=None, limit: int=10, reranker: Any \| None=None) -> list[dict[str, Any]] | 9 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.get` | method | `src/jarvis_v2/backend/retrieval.py:220-227` | def get(self, document_id: str) -> dict[str, Any] | 27 | active |
| `jarvis_v2.backend.retrieval.DocumentStore._snapshot` | method | `src/jarvis_v2/backend/retrieval.py:230-249` | def _snapshot(row: sqlite3.Row) -> dict[str, Any] | 0 | active |
| `jarvis_v2.backend.retrieval.DocumentStore.close` | method | `src/jarvis_v2/backend/retrieval.py:251-253` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.routing.RoutingError` | class | `src/jarvis_v2/backend/routing.py:16-17` | class RoutingError(ValueError) | 0 | active |
| `jarvis_v2.backend.routing._identifier` | function | `src/jarvis_v2/backend/routing.py:20-23` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.routing.CircuitState` | class | `src/jarvis_v2/backend/routing.py:26-29` | class CircuitState(str, Enum) | 1 | active |
| `jarvis_v2.backend.routing.StickyRouter` | class | `src/jarvis_v2/backend/routing.py:32-56` | class StickyRouter() | 1 | active |
| `jarvis_v2.backend.routing.StickyRouter.__init__` | method | `src/jarvis_v2/backend/routing.py:35-38` | def __init__(self, routes: Mapping[str, str] \| None=None) -> None | 5 | active |
| `jarvis_v2.backend.routing.StickyRouter.provider_for` | method | `src/jarvis_v2/backend/routing.py:40-41` | def provider_for(self, affinity_key: str) -> str \| None | 0 | active |
| `jarvis_v2.backend.routing.StickyRouter.bind` | method | `src/jarvis_v2/backend/routing.py:43-50` | def bind(self, affinity_key: str, provider_id: str, *, replace_existing: bool=False) -> str | 5 | active |
| `jarvis_v2.backend.routing.StickyRouter.handoff` | method | `src/jarvis_v2/backend/routing.py:52-53` | def handoff(self, affinity_key: str, provider_id: str) -> str | 12 | active |
| `jarvis_v2.backend.routing.StickyRouter.forget` | method | `src/jarvis_v2/backend/routing.py:55-56` | def forget(self, affinity_key: str) -> None | 0 | active |
| `jarvis_v2.backend.routing.CircuitBreaker` | class | `src/jarvis_v2/backend/routing.py:59-130` | class CircuitBreaker() | 1 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.__init__` | method | `src/jarvis_v2/backend/routing.py:62-81` | def __init__(self, *, failure_threshold: int=3, reset_timeout: float=30.0, clock: Callable[[], float] \| None=None) -> None | 5 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.state` | method | `src/jarvis_v2/backend/routing.py:84-86` | def state(self) -> CircuitState | 56 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.failures` | method | `src/jarvis_v2/backend/routing.py:89-90` | def failures(self) -> int | 1 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.allow` | method | `src/jarvis_v2/backend/routing.py:92-99` | def allow(self) -> bool | 1 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.record_success` | method | `src/jarvis_v2/backend/routing.py:101-105` | def record_success(self) -> None | 1 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.record_failure` | method | `src/jarvis_v2/backend/routing.py:107-114` | def record_failure(self) -> None | 1 | active |
| `jarvis_v2.backend.routing.CircuitBreaker.reset` | method | `src/jarvis_v2/backend/routing.py:116-117` | def reset(self) -> None | 2 | active |
| `jarvis_v2.backend.routing.CircuitBreaker._refresh` | method | `src/jarvis_v2/backend/routing.py:119-126` | def _refresh(self) -> None | 0 | active |
| `jarvis_v2.backend.routing.CircuitBreaker._open` | method | `src/jarvis_v2/backend/routing.py:128-130` | def _open(self) -> None | 0 | active |
| `jarvis_v2.backend.routing.UsageBudget` | class | `src/jarvis_v2/backend/routing.py:133-191` | class UsageBudget() | 1 | active |
| `jarvis_v2.backend.routing.UsageBudget.__init__` | method | `src/jarvis_v2/backend/routing.py:136-142` | def __init__(self, limit: int) -> None | 5 | active |
| `jarvis_v2.backend.routing.UsageBudget.remaining` | method | `src/jarvis_v2/backend/routing.py:145-146` | def remaining(self) -> int | 1 | active |
| `jarvis_v2.backend.routing.UsageBudget.reserved` | method | `src/jarvis_v2/backend/routing.py:149-150` | def reserved(self) -> int | 1 | active |
| `jarvis_v2.backend.routing.UsageBudget.used` | method | `src/jarvis_v2/backend/routing.py:153-154` | def used(self) -> int | 2 | active |
| `jarvis_v2.backend.routing.UsageBudget.can_consume` | method | `src/jarvis_v2/backend/routing.py:156-158` | def can_consume(self, units: int=1) -> bool | 0 | active |
| `jarvis_v2.backend.routing.UsageBudget.reserve` | method | `src/jarvis_v2/backend/routing.py:160-166` | def reserve(self, units: int=1) -> bool | 1 | active |
| `jarvis_v2.backend.routing.UsageBudget.commit` | method | `src/jarvis_v2/backend/routing.py:168-173` | def commit(self, units: int=1) -> None | 22 | active |
| `jarvis_v2.backend.routing.UsageBudget.consume` | method | `src/jarvis_v2/backend/routing.py:175-179` | def consume(self, units: int=1) -> bool | 2 | active |
| `jarvis_v2.backend.routing.UsageBudget.release` | method | `src/jarvis_v2/backend/routing.py:181-186` | def release(self, units: int=1) -> None | 12 | active |
| `jarvis_v2.backend.routing.UsageBudget._validate_units` | method | `src/jarvis_v2/backend/routing.py:189-191` | def _validate_units(units: int) -> None | 0 | active |
| `jarvis_v2.backend.routing.RouteDecision` | class | `src/jarvis_v2/backend/routing.py:195-202` | class RouteDecision() | 0 | active |
| `jarvis_v2.backend.routing.GatewayRouter` | class | `src/jarvis_v2/backend/routing.py:205-317` | class GatewayRouter() | 2 | active |
| `jarvis_v2.backend.routing.GatewayRouter.__init__` | method | `src/jarvis_v2/backend/routing.py:208-227` | def __init__(self, registry: ProviderRegistry, *, budgets: Mapping[str, UsageBudget] \| None=None, circuits: Mapping[str, CircuitBreaker] \| None=None, sticky: StickyRouter \| None | 5 | active |
| `jarvis_v2.backend.routing.GatewayRouter.route` | method | `src/jarvis_v2/backend/routing.py:229-281` | def route(self, affinity_key: str, requirements: ProviderRequirements, *, allow_handoff: bool=False, handoff_provider: str \| None=None) -> RouteDecision | 7 | active |
| `jarvis_v2.backend.routing.GatewayRouter.record_success` | method | `src/jarvis_v2/backend/routing.py:283-284` | def record_success(self, provider_id: str) -> None | 1 | active |
| `jarvis_v2.backend.routing.GatewayRouter.record_failure` | method | `src/jarvis_v2/backend/routing.py:286-287` | def record_failure(self, provider_id: str) -> None | 1 | active |
| `jarvis_v2.backend.routing.GatewayRouter._try_provider` | method | `src/jarvis_v2/backend/routing.py:289-310` | def _try_provider(self, affinity_key: str, requirements: ProviderRequirements, provider_id: str \| None) -> RouteDecision | 0 | active |
| `jarvis_v2.backend.routing.GatewayRouter._circuit` | method | `src/jarvis_v2/backend/routing.py:312-313` | def _circuit(self, provider_id: str) -> CircuitBreaker | 0 | active |
| `jarvis_v2.backend.routing.GatewayRouter._paused` | method | `src/jarvis_v2/backend/routing.py:316-317` | def _paused(affinity_key: str, reason: str) -> RouteDecision | 0 | active |
| `jarvis_v2.backend.scheduler.ReminderError` | class | `src/jarvis_v2/backend/scheduler.py:19-20` | class ReminderError(ValueError) | 1 | active |
| `jarvis_v2.backend.scheduler.Reminder` | class | `src/jarvis_v2/backend/scheduler.py:24-46` | class Reminder() | 0 | active |
| `jarvis_v2.backend.scheduler.Reminder.as_dict` | method | `src/jarvis_v2/backend/scheduler.py:35-46` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.backend.scheduler._format_utc` | function | `src/jarvis_v2/backend/scheduler.py:49-50` | def _format_utc(value: datetime) -> str | 0 | active |
| `jarvis_v2.backend.scheduler._parse_utc` | function | `src/jarvis_v2/backend/scheduler.py:53-60` | def _parse_utc(value: str) -> datetime | 0 | active |
| `jarvis_v2.backend.scheduler._now` | function | `src/jarvis_v2/backend/scheduler.py:63-67` | def _now(clock: Callable[[], datetime] \| None) -> datetime | 0 | active |
| `jarvis_v2.backend.scheduler._zone` | function | `src/jarvis_v2/backend/scheduler.py:70-76` | def _zone(name: str) -> ZoneInfo | 0 | active |
| `jarvis_v2.backend.scheduler._identifier` | function | `src/jarvis_v2/backend/scheduler.py:79-82` | def _identifier(value: str) -> str | 0 | active |
| `jarvis_v2.backend.scheduler._message` | function | `src/jarvis_v2/backend/scheduler.py:85-90` | def _message(value: str) -> str | 2 | active |
| `jarvis_v2.backend.scheduler._resolve_local` | function | `src/jarvis_v2/backend/scheduler.py:93-116` | def _resolve_local(local: datetime, zone: ZoneInfo) -> datetime | 0 | active |
| `jarvis_v2.backend.scheduler._local_datetime` | function | `src/jarvis_v2/backend/scheduler.py:119-131` | def _local_datetime(value: datetime \| str, zone: ZoneInfo) -> tuple[datetime, datetime] | 0 | active |
| `jarvis_v2.backend.scheduler._local_time` | function | `src/jarvis_v2/backend/scheduler.py:134-137` | def _local_time(value: time) -> time | 0 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler` | class | `src/jarvis_v2/backend/scheduler.py:140-358` | class ReminderScheduler() | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.__init__` | method | `src/jarvis_v2/backend/scheduler.py:143-172` | def __init__(self, database: str \| Path \| sqlite3.Connection, *, clock: Callable[[], datetime] \| None=None) -> None | 5 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.__enter__` | method | `src/jarvis_v2/backend/scheduler.py:174-175` | def __enter__(self) -> 'ReminderScheduler' | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.__exit__` | method | `src/jarvis_v2/backend/scheduler.py:177-178` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.create_reminder` | method | `src/jarvis_v2/backend/scheduler.py:180-194` | def create_reminder(self, reminder_id: str, message: str, due_at: datetime \| str, *, timezone_name: str='UTC') -> Reminder | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.create_daily_reminder` | method | `src/jarvis_v2/backend/scheduler.py:196-217` | def create_daily_reminder(self, reminder_id: str, message: str, local_time: time, *, timezone_name: str, start_date: date \| None=None) -> Reminder | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.get` | method | `src/jarvis_v2/backend/scheduler.py:221-227` | def get(self, reminder_id: str) -> Reminder | 27 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.due_reminders` | method | `src/jarvis_v2/backend/scheduler.py:229-238` | def due_reminders(self, now: datetime \| None=None, *, limit: int=100) -> list[Reminder] | 1 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.acknowledge` | method | `src/jarvis_v2/backend/scheduler.py:242-278` | def acknowledge(self, reminder_id: str) -> Reminder | 4 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.cancel` | method | `src/jarvis_v2/backend/scheduler.py:282-295` | def cancel(self, reminder_id: str) -> Reminder | 0 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler.close` | method | `src/jarvis_v2/backend/scheduler.py:297-299` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler._insert` | method | `src/jarvis_v2/backend/scheduler.py:301-344` | def _insert(self, reminder_id: str, message: str, timezone_name: str, recurrence: str, scheduled_local: str, next_due_utc: datetime) -> Reminder | 0 | active |
| `jarvis_v2.backend.scheduler.ReminderScheduler._snapshot` | method | `src/jarvis_v2/backend/scheduler.py:347-358` | def _snapshot(row: sqlite3.Row) -> Reminder | 0 | active |
| `jarvis_v2.backend.secrets.SecretBoundaryError` | class | `src/jarvis_v2/backend/secrets.py:16-17` | class SecretBoundaryError(ValueError) | 1 | active |
| `jarvis_v2.backend.secrets.SecretUnavailable` | class | `src/jarvis_v2/backend/secrets.py:20-21` | class SecretUnavailable(SecretBoundaryError) | 1 | active |
| `jarvis_v2.backend.secrets._name` | function | `src/jarvis_v2/backend/secrets.py:24-27` | def _name(value: str) -> str | 0 | active |
| `jarvis_v2.backend.secrets._names` | function | `src/jarvis_v2/backend/secrets.py:30-36` | def _names(values: Iterable[str]) -> frozenset[str] | 0 | active |
| `jarvis_v2.backend.secrets.SecretValue` | class | `src/jarvis_v2/backend/secrets.py:40-65` | class SecretValue() | 0 | active |
| `jarvis_v2.backend.secrets.SecretValue.digest` | method | `src/jarvis_v2/backend/secrets.py:47-48` | def digest(self) -> str | 17 | active |
| `jarvis_v2.backend.secrets.SecretValue.length` | method | `src/jarvis_v2/backend/secrets.py:51-52` | def length(self) -> int | 3 | active |
| `jarvis_v2.backend.secrets.SecretValue.reveal` | method | `src/jarvis_v2/backend/secrets.py:54-56` | def reveal(self) -> str | 1 | active |
| `jarvis_v2.backend.secrets.SecretValue.__str__` | method | `src/jarvis_v2/backend/secrets.py:58-59` | def __str__(self) -> str | 0 | active |
| `jarvis_v2.backend.secrets.SecretValue.__repr__` | method | `src/jarvis_v2/backend/secrets.py:61-62` | def __repr__(self) -> str | 0 | active |
| `jarvis_v2.backend.secrets.SecretValue.__format__` | method | `src/jarvis_v2/backend/secrets.py:64-65` | def __format__(self, format_spec: str) -> str | 0 | active |
| `jarvis_v2.backend.secrets.SecretStore` | class | `src/jarvis_v2/backend/secrets.py:68-116` | class SecretStore() | 1 | active |
| `jarvis_v2.backend.secrets.SecretStore.__init__` | method | `src/jarvis_v2/backend/secrets.py:71-86` | def __init__(self, values: Mapping[str, str], *, allowlist: Iterable[str]) -> None | 5 | active |
| `jarvis_v2.backend.secrets.SecretStore.from_environment` | method | `src/jarvis_v2/backend/secrets.py:89-95` | def from_environment(cls, allowlist: Iterable[str], *, environment: Mapping[str, str] \| None=None) -> 'SecretStore' | 0 | active |
| `jarvis_v2.backend.secrets.SecretStore.get` | method | `src/jarvis_v2/backend/secrets.py:97-104` | def get(self, name: str) -> SecretValue | 27 | active |
| `jarvis_v2.backend.secrets.SecretStore.redact` | method | `src/jarvis_v2/backend/secrets.py:106-112` | def redact(self, text: str) -> str | 1 | active |
| `jarvis_v2.backend.secrets.SecretStore.public_metadata` | method | `src/jarvis_v2/backend/secrets.py:114-116` | def public_metadata(self, name: str) -> dict[str, str \| int] | 13 | active |
| `jarvis_v2.backend.storage.StorageError` | class | `src/jarvis_v2/backend/storage.py:27-28` | class StorageError(RuntimeError) | 0 | active |
| `jarvis_v2.backend.storage.MigrationError` | class | `src/jarvis_v2/backend/storage.py:31-32` | class MigrationError(StorageError) | 1 | active |
| `jarvis_v2.backend.storage.OwnershipError` | class | `src/jarvis_v2/backend/storage.py:35-36` | class OwnershipError(StorageError) | 1 | active |
| `jarvis_v2.backend.storage.Migration` | class | `src/jarvis_v2/backend/storage.py:40-62` | class Migration() | 1 | active |
| `jarvis_v2.backend.storage.Migration.digest` | method | `src/jarvis_v2/backend/storage.py:50-62` | def digest(self) -> str | 17 | active |
| `jarvis_v2.backend.storage._utc_now` | function | `src/jarvis_v2/backend/storage.py:85-88` | def _utc_now() -> str | 0 | active |
| `jarvis_v2.backend.storage._identifier` | function | `src/jarvis_v2/backend/storage.py:91-94` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.storage._quote_identifier` | function | `src/jarvis_v2/backend/storage.py:97-98` | def _quote_identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.storage.ModuleStore` | class | `src/jarvis_v2/backend/storage.py:101-114` | class ModuleStore() | 0 | active |
| `jarvis_v2.backend.storage.ModuleStore.__init__` | method | `src/jarvis_v2/backend/storage.py:104-108` | def __init__(self, manager: 'StorageManager', module: str) -> None | 5 | active |
| `jarvis_v2.backend.storage.ModuleStore.insert` | method | `src/jarvis_v2/backend/storage.py:110-111` | def insert(self, table: str, values: Mapping[str, Any]) -> None | 5 | active |
| `jarvis_v2.backend.storage.ModuleStore.rows` | method | `src/jarvis_v2/backend/storage.py:113-114` | def rows(self, table: str) -> list[dict[str, Any]] | 6 | active |
| `jarvis_v2.backend.storage.StorageManager` | class | `src/jarvis_v2/backend/storage.py:117-402` | class StorageManager() | 4 | active |
| `jarvis_v2.backend.storage.StorageManager.__init__` | method | `src/jarvis_v2/backend/storage.py:120-134` | def __init__(self, path: str \| Path, *, migrations: Sequence[Migration]=DEFAULT_MIGRATIONS) -> None | 5 | active |
| `jarvis_v2.backend.storage.StorageManager.__enter__` | method | `src/jarvis_v2/backend/storage.py:136-137` | def __enter__(self) -> 'StorageManager' | 1 | active |
| `jarvis_v2.backend.storage.StorageManager.__exit__` | method | `src/jarvis_v2/backend/storage.py:139-140` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.backend.storage.StorageManager.close` | method | `src/jarvis_v2/backend/storage.py:142-143` | def close(self) -> None | 34 | active |
| `jarvis_v2.backend.storage.StorageManager.module` | method | `src/jarvis_v2/backend/storage.py:145-146` | def module(self, module: str) -> ModuleStore | 40 | active |
| `jarvis_v2.backend.storage.StorageManager._validate_plan` | method | `src/jarvis_v2/backend/storage.py:148-182` | def _validate_plan(self) -> None | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._bootstrap` | method | `src/jarvis_v2/backend/storage.py:184-215` | def _bootstrap(self) -> None | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._applied` | method | `src/jarvis_v2/backend/storage.py:217-227` | def _applied(self) -> dict[tuple[str, int], sqlite3.Row] | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._plan_by_key` | method | `src/jarvis_v2/backend/storage.py:229-230` | def _plan_by_key(self) -> dict[tuple[str, int], Migration] | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._validate_applied` | method | `src/jarvis_v2/backend/storage.py:232-243` | def _validate_applied(self, applied: Mapping[tuple[str, int], sqlite3.Row]) -> None | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._integrity_check` | method | `src/jarvis_v2/backend/storage.py:245-248` | def _integrity_check(self) -> None | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._table_exists` | method | `src/jarvis_v2/backend/storage.py:250-253` | def _table_exists(self, table: str) -> bool | 0 | active |
| `jarvis_v2.backend.storage.StorageManager._apply_one` | method | `src/jarvis_v2/backend/storage.py:255-284` | def _apply_one(self, migration: Migration) -> None | 0 | active |
| `jarvis_v2.backend.storage.StorageManager.migrate` | method | `src/jarvis_v2/backend/storage.py:286-303` | def migrate(self) -> list[dict[str, Any]] | 4 | active |
| `jarvis_v2.backend.storage.StorageManager.rollback` | method | `src/jarvis_v2/backend/storage.py:305-349` | def rollback(self, module: str, *, target_version: int=0) -> list[dict[str, Any]] | 9 | active |
| `jarvis_v2.backend.storage.StorageManager.applied_migrations` | method | `src/jarvis_v2/backend/storage.py:351-356` | def applied_migrations(self) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.backend.storage.StorageManager.table_owner` | method | `src/jarvis_v2/backend/storage.py:358-364` | def table_owner(self, table: str) -> str \| None | 2 | active |
| `jarvis_v2.backend.storage.StorageManager._assert_owner` | method | `src/jarvis_v2/backend/storage.py:366-375` | def _assert_owner(self, module: str, table: str) -> str | 0 | active |
| `jarvis_v2.backend.storage.StorageManager.insert` | method | `src/jarvis_v2/backend/storage.py:377-395` | def insert(self, module: str, table: str, values: Mapping[str, Any]) -> None | 5 | active |
| `jarvis_v2.backend.storage.StorageManager.rows` | method | `src/jarvis_v2/backend/storage.py:397-402` | def rows(self, module: str, table: str) -> list[dict[str, Any]] | 6 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityError` | class | `src/jarvis_v2/backend/task_capability.py:19-20` | class TaskCapabilityError(ValueError) | 1 | active |
| `jarvis_v2.backend.task_capability._paths` | function | `src/jarvis_v2/backend/task_capability.py:23-45` | def _paths(values: Iterable[str \| Path]) -> tuple[Path, ...] | 0 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest` | class | `src/jarvis_v2/backend/task_capability.py:49-103` | class TaskCapabilityManifest() | 1 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.__post_init__` | method | `src/jarvis_v2/backend/task_capability.py:56-63` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.create` | method | `src/jarvis_v2/backend/task_capability.py:66-73` | def create(cls, operations: Iterable[str], allowed_paths: Iterable[str \| Path]) -> 'TaskCapabilityManifest' | 8 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.as_dict` | method | `src/jarvis_v2/backend/task_capability.py:75-80` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.validate_path` | method | `src/jarvis_v2/backend/task_capability.py:82-98` | def validate_path(self, path: str \| Path) -> Path | 0 | active |
| `jarvis_v2.backend.task_capability.TaskCapabilityManifest.validate_operation` | method | `src/jarvis_v2/backend/task_capability.py:100-103` | def validate_operation(self, operation: str) -> str | 0 | active |
| `jarvis_v2.backend.task_capability.ValidatedTaskRequest` | class | `src/jarvis_v2/backend/task_capability.py:107-112` | class ValidatedTaskRequest() | 0 | active |
| `jarvis_v2.backend.task_capability.validate_task_request` | function | `src/jarvis_v2/backend/task_capability.py:115-127` | def validate_task_request(manifest: TaskCapabilityManifest, operation: str, input_sha256: str, *, path: str \| Path \| None=None) -> ValidatedTaskRequest | 1 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentError` | class | `src/jarvis_v2/backend/windows_agent.py:22-23` | class WindowsAgentError(ValueError) | 1 | active |
| `jarvis_v2.backend.windows_agent._identifier` | function | `src/jarvis_v2/backend/windows_agent.py:26-29` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.windows_agent._model` | function | `src/jarvis_v2/backend/windows_agent.py:32-35` | def _model(value: str) -> str | 1 | active |
| `jarvis_v2.backend.windows_agent._digest` | function | `src/jarvis_v2/backend/windows_agent.py:38-41` | def _digest(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.backend.windows_agent.NodeManifest` | class | `src/jarvis_v2/backend/windows_agent.py:45-71` | class NodeManifest() | 4 | active |
| `jarvis_v2.backend.windows_agent.NodeManifest.__post_init__` | method | `src/jarvis_v2/backend/windows_agent.py:56-71` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.windows_agent.Heartbeat` | class | `src/jarvis_v2/backend/windows_agent.py:75-95` | class Heartbeat() | 0 | active |
| `jarvis_v2.backend.windows_agent.Heartbeat.__post_init__` | method | `src/jarvis_v2/backend/windows_agent.py:83-95` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.windows_agent.LocalAgentJob` | class | `src/jarvis_v2/backend/windows_agent.py:99-124` | class LocalAgentJob() | 5 | active |
| `jarvis_v2.backend.windows_agent.LocalAgentJob.__post_init__` | method | `src/jarvis_v2/backend/windows_agent.py:111-124` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.backend.windows_agent.NodeRoute` | class | `src/jarvis_v2/backend/windows_agent.py:128-132` | class NodeRoute() | 1 | active |
| `jarvis_v2.backend.windows_agent.CapabilityLease` | class | `src/jarvis_v2/backend/windows_agent.py:136-140` | class CapabilityLease() | 0 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry` | class | `src/jarvis_v2/backend/windows_agent.py:143-361` | class WindowsAgentRegistry() | 4 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.__init__` | method | `src/jarvis_v2/backend/windows_agent.py:146-160` | def __init__(self, *, clock: Callable[[], float] \| None=None, heartbeat_age_seconds: int=MAX_HEARTBEAT_AGE_SECONDS) -> None | 5 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.register_node` | method | `src/jarvis_v2/backend/windows_agent.py:162-170` | def register_node(self, manifest: NodeManifest) -> NodeManifest | 3 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.heartbeat` | method | `src/jarvis_v2/backend/windows_agent.py:172-191` | def heartbeat(self, node_id: str, *, status: str='online', observed_at: float \| None=None, cpu_percent: float \| None=None, memory_bytes: int \| None=None, free_vram_bytes: int \| | 5 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.route` | method | `src/jarvis_v2/backend/windows_agent.py:193-223` | def route(self, operation: str, required_scope: str, *, node_id: str \| None=None, requested_model: str \| None=None) -> NodeRoute | 7 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.submit` | method | `src/jarvis_v2/backend/windows_agent.py:225-238` | def submit(self, job: LocalAgentJob) -> LocalAgentJob | 6 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.lease` | method | `src/jarvis_v2/backend/windows_agent.py:240-261` | def lease(self, job_id: str, node_id: str, *, ttl_seconds: int=60) -> CapabilityLease | 17 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.complete` | method | `src/jarvis_v2/backend/windows_agent.py:263-315` | def complete(self, job_id: str, node_id: str, lease_id: str, *, result_sha256: str, error_code: str='') -> dict[str, object] | 9 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.reconcile` | method | `src/jarvis_v2/backend/windows_agent.py:317-329` | def reconcile(self) -> int | 4 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.node_snapshot` | method | `src/jarvis_v2/backend/windows_agent.py:331-345` | def node_snapshot(self, node_id: str) -> dict[str, object] | 1 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry.job_snapshot` | method | `src/jarvis_v2/backend/windows_agent.py:347-358` | def job_snapshot(self, job_id: str) -> dict[str, object] | 1 | active |
| `jarvis_v2.backend.windows_agent.WindowsAgentRegistry._active_leases` | method | `src/jarvis_v2/backend/windows_agent.py:360-361` | def _active_leases(self, node_id: str) -> int | 0 | active |
| `jarvis_v2.cli.main` | function | `src/jarvis_v2/cli.py:13-53` | def main(argv=None) | 155 | active |
| `jarvis_v2.core.budget.ResourceBudgetError` | class | `src/jarvis_v2/core/budget.py:10-11` | class ResourceBudgetError(ValueError) | 1 | active |
| `jarvis_v2.core.budget.ResourceBudget` | class | `src/jarvis_v2/core/budget.py:14-120` | class ResourceBudget() | 2 | active |
| `jarvis_v2.core.budget.ResourceBudget.__init__` | method | `src/jarvis_v2/core/budget.py:17-42` | def __init__(self, capacity: int, *, device_limits: Mapping[str, int] \| None=None, slots: Iterable[str] \| None=None) -> None | 5 | active |
| `jarvis_v2.core.budget.ResourceBudget.capacity` | method | `src/jarvis_v2/core/budget.py:45-46` | def capacity(self) -> int | 1 | active |
| `jarvis_v2.core.budget.ResourceBudget.slots` | method | `src/jarvis_v2/core/budget.py:49-50` | def slots(self) -> tuple[str, ...] | 4 | active |
| `jarvis_v2.core.budget.ResourceBudget.available_slots` | method | `src/jarvis_v2/core/budget.py:53-54` | def available_slots(self) -> tuple[str, ...] | 2 | active |
| `jarvis_v2.core.budget.ResourceBudget.guardian_pending` | method | `src/jarvis_v2/core/budget.py:57-58` | def guardian_pending(self) -> bool | 1 | active |
| `jarvis_v2.core.budget.ResourceBudget.device_limits` | method | `src/jarvis_v2/core/budget.py:61-62` | def device_limits(self) -> Mapping[str, int] | 1 | active |
| `jarvis_v2.core.budget.ResourceBudget.held_slots` | method | `src/jarvis_v2/core/budget.py:65-69` | def held_slots(self) -> dict[str, dict[str, str]] | 3 | active |
| `jarvis_v2.core.budget.ResourceBudget.device_usage` | method | `src/jarvis_v2/core/budget.py:72-76` | def device_usage(self) -> dict[str, int] | 1 | active |
| `jarvis_v2.core.budget.ResourceBudget.guardian_request` | method | `src/jarvis_v2/core/budget.py:78-79` | def guardian_request(self, compatible_slots: Iterable[str] \| None=None) -> None | 4 | active |
| `jarvis_v2.core.budget.ResourceBudget.claim` | method | `src/jarvis_v2/core/budget.py:81-100` | def claim(self, owner: str, *, device: str='default', compatible_slots: Iterable[str] \| None=None, guardian: bool=False) -> str \| None | 21 | active |
| `jarvis_v2.core.budget.ResourceBudget.finish` | method | `src/jarvis_v2/core/budget.py:102-110` | def finish(self, owner: str, slot: str, *, device: str \| None=None) -> None | 12 | active |
| `jarvis_v2.core.budget.ResourceBudget._validate_owner` | method | `src/jarvis_v2/core/budget.py:113-115` | def _validate_owner(owner: str) -> None | 0 | active |
| `jarvis_v2.core.budget.ResourceBudget._validate_device` | method | `src/jarvis_v2/core/budget.py:118-120` | def _validate_device(device: str) -> None | 0 | active |
| `jarvis_v2.core.control.ControlError` | class | `src/jarvis_v2/core/control.py:14-15` | class ControlError(ValueError) | 1 | active |
| `jarvis_v2.core.control._now` | function | `src/jarvis_v2/core/control.py:18-19` | def _now() -> str | 0 | active |
| `jarvis_v2.core.control.CoreControls` | class | `src/jarvis_v2/core/control.py:22-78` | class CoreControls() | 0 | active |
| `jarvis_v2.core.control.CoreControls.__init__` | method | `src/jarvis_v2/core/control.py:25-42` | def __init__(self, database: Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.control.CoreControls.status` | method | `src/jarvis_v2/core/control.py:44-50` | def status(self) -> dict[str, str] | 80 | active |
| `jarvis_v2.core.control.CoreControls.allows_dispatch` | method | `src/jarvis_v2/core/control.py:52-53` | def allows_dispatch(self) -> bool | 0 | active |
| `jarvis_v2.core.control.CoreControls.stop` | method | `src/jarvis_v2/core/control.py:55-56` | def stop(self, *, reason: str='owner_stop') -> dict[str, str] | 4 | active |
| `jarvis_v2.core.control.CoreControls.pause` | method | `src/jarvis_v2/core/control.py:58-59` | def pause(self, *, reason: str='owner_pause') -> dict[str, str] | 1 | active |
| `jarvis_v2.core.control.CoreControls.resume` | method | `src/jarvis_v2/core/control.py:61-62` | def resume(self) -> dict[str, str] | 3 | active |
| `jarvis_v2.core.control.CoreControls._set` | method | `src/jarvis_v2/core/control.py:64-74` | def _set(self, state: str, reason: str) -> dict[str, str] | 0 | active |
| `jarvis_v2.core.control.CoreControls.close` | method | `src/jarvis_v2/core/control.py:76-78` | def close(self) -> None | 34 | active |
| `jarvis_v2.core.dependency.DependencyError` | class | `src/jarvis_v2/core/dependency.py:9-10` | class DependencyError(ValueError) | 1 | active |
| `jarvis_v2.core.dependency.DependencyOrchestrator` | class | `src/jarvis_v2/core/dependency.py:13-61` | class DependencyOrchestrator() | 1 | active |
| `jarvis_v2.core.dependency.DependencyOrchestrator.__init__` | method | `src/jarvis_v2/core/dependency.py:16-18` | def __init__(self, database: sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.dependency.DependencyOrchestrator.dependencies` | method | `src/jarvis_v2/core/dependency.py:21-33` | def dependencies(payload: Mapping[str, object]) -> tuple[str, ...] | 10 | active |
| `jarvis_v2.core.dependency.DependencyOrchestrator.ready` | method | `src/jarvis_v2/core/dependency.py:35-49` | def ready(self, payload: Mapping[str, object]) -> bool | 6 | active |
| `jarvis_v2.core.dependency.DependencyOrchestrator.dependent_ids` | method | `src/jarvis_v2/core/dependency.py:51-61` | def dependent_ids(self, task_id: str) -> list[str] | 1 | active |
| `jarvis_v2.core.dispatch.DispatchError` | class | `src/jarvis_v2/core/dispatch.py:19-20` | class DispatchError(ValueError) | 2 | active |
| `jarvis_v2.core.dispatch._identifier` | function | `src/jarvis_v2/core/dispatch.py:23-26` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.core.dispatch._module` | function | `src/jarvis_v2/core/dispatch.py:29-32` | def _module(value: str) -> str | 0 | active |
| `jarvis_v2.core.dispatch._encode` | function | `src/jarvis_v2/core/dispatch.py:35-52` | def _encode(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.core.dispatch._now` | function | `src/jarvis_v2/core/dispatch.py:55-56` | def _now() -> str | 0 | active |
| `jarvis_v2.core.dispatch.DispatchStore` | class | `src/jarvis_v2/core/dispatch.py:59-255` | class DispatchStore() | 3 | active |
| `jarvis_v2.core.dispatch.DispatchStore.__init__` | method | `src/jarvis_v2/core/dispatch.py:62-95` | def __init__(self, database: Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.dispatch.DispatchStore.create` | method | `src/jarvis_v2/core/dispatch.py:97-142` | def create(self, task_id: str, target_module: str, scope: str \| Sequence[str] \| Mapping[str, object], acceptance: str \| Sequence[str] \| Mapping[str, object], *, correlation_id: | 8 | active |
| `jarvis_v2.core.dispatch.DispatchStore.claim` | method | `src/jarvis_v2/core/dispatch.py:144-167` | def claim(self, dispatch_id: str, executor_id: str, *, claim_id: str \| None=None) -> dict | 21 | active |
| `jarvis_v2.core.dispatch.DispatchStore.acknowledge` | method | `src/jarvis_v2/core/dispatch.py:169-216` | def acknowledge(self, dispatch_id: str, executor_id: str, claim_id: str, *, status: str, result: Mapping[str, object]) -> dict | 4 | active |
| `jarvis_v2.core.dispatch.DispatchStore.get` | method | `src/jarvis_v2/core/dispatch.py:218-223` | def get(self, dispatch_id: str) -> dict | 27 | active |
| `jarvis_v2.core.dispatch.DispatchStore._snapshot` | method | `src/jarvis_v2/core/dispatch.py:225-251` | def _snapshot(self, row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.dispatch.DispatchStore.close` | method | `src/jarvis_v2/core/dispatch.py:253-255` | def close(self) -> None | 34 | active |
| `jarvis_v2.core.event_session.EventSessionError` | class | `src/jarvis_v2/core/event_session.py:20-21` | class EventSessionError(ValueError) | 2 | active |
| `jarvis_v2.core.event_session._identifier` | function | `src/jarvis_v2/core/event_session.py:24-27` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.core.event_session._now` | function | `src/jarvis_v2/core/event_session.py:30-31` | def _now() -> str | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter` | class | `src/jarvis_v2/core/event_session.py:34-329` | class EventSessionInterpreter() | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.__init__` | method | `src/jarvis_v2/core/event_session.py:37-44` | def __init__(self, database: Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter._ensure_schema` | method | `src/jarvis_v2/core/event_session.py:46-101` | def _ensure_schema(self) -> None | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.open_session` | method | `src/jarvis_v2/core/event_session.py:103-136` | def open_session(self, *, name: str, session_id: str \| None=None, correlation_id: str \| None=None) -> dict | 3 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.emit` | method | `src/jarvis_v2/core/event_session.py:138-207` | def emit(self, task_id: str, kind: str, detail: str, *, correlation_id: str \| None=None, causation_id: str \| None=None, event_id: str \| None=None) -> dict | 5 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.causal_chain` | method | `src/jarvis_v2/core/event_session.py:209-217` | def causal_chain(self, correlation_id: str, *, limit: int=MAX_EVENT_BATCH) -> list[dict] | 2 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.replay` | method | `src/jarvis_v2/core/event_session.py:219-234` | def replay(self, *, limit: int=MAX_EVENT_BATCH) -> list[dict] | 13 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.interpret` | method | `src/jarvis_v2/core/event_session.py:236-238` | def interpret(self, *, limit: int=MAX_EVENT_BATCH) -> list[dict] | 1 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.ack` | method | `src/jarvis_v2/core/event_session.py:240-250` | def ack(self, seq: int) -> None | 6 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.record_failure` | method | `src/jarvis_v2/core/event_session.py:252-285` | def record_failure(self, event_id: str, failure_code: str, diagnostic: str) -> dict | 1 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.failure` | method | `src/jarvis_v2/core/event_session.py:287-290` | def failure(self, event_id: str) -> dict \| None | 13 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter._limit` | method | `src/jarvis_v2/core/event_session.py:293-296` | def _limit(limit: int) -> int | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter._metadata` | method | `src/jarvis_v2/core/event_session.py:299-309` | def _metadata(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter._metadata_with_failure` | method | `src/jarvis_v2/core/event_session.py:311-314` | def _metadata_with_failure(self, row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter._failure` | method | `src/jarvis_v2/core/event_session.py:317-325` | def _failure(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.event_session.EventSessionInterpreter.close` | method | `src/jarvis_v2/core/event_session.py:327-329` | def close(self) -> None | 34 | active |
| `jarvis_v2.core.intent.IntentError` | class | `src/jarvis_v2/core/intent.py:22-23` | class IntentError(ValueError) | 1 | active |
| `jarvis_v2.core.intent._identifier` | function | `src/jarvis_v2/core/intent.py:26-29` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.core.intent._encode` | function | `src/jarvis_v2/core/intent.py:32-39` | def _encode(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.core.intent._now` | function | `src/jarvis_v2/core/intent.py:42-43` | def _now() -> str | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter` | class | `src/jarvis_v2/core/intent.py:46-267` | class OwnerIntentRouter() | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter.__init__` | method | `src/jarvis_v2/core/intent.py:49-79` | def __init__(self, database: Path \| sqlite3.Connection, queue=None) | 5 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter.submit` | method | `src/jarvis_v2/core/intent.py:81-130` | def submit(self, intent: Mapping[str, object], *, approval: Mapping[str, object] \| None=None) -> dict | 6 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter.get` | method | `src/jarvis_v2/core/intent.py:132-137` | def get(self, request_id: str) -> dict | 27 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._normalize` | method | `src/jarvis_v2/core/intent.py:139-177` | def _normalize(self, intent: Mapping[str, object]) -> dict | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._requires_approval` | method | `src/jarvis_v2/core/intent.py:180-182` | def _requires_approval(intent: Mapping[str, object]) -> bool | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._safe_decision` | method | `src/jarvis_v2/core/intent.py:185-193` | def _safe_decision(approval: Mapping[str, object] \| None, intent_sha: str) -> str | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._approval_decision` | method | `src/jarvis_v2/core/intent.py:196-210` | def _approval_decision(approval: Mapping[str, object] \| None, intent_sha: str) -> str | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._enqueue` | method | `src/jarvis_v2/core/intent.py:212-230` | def _enqueue(self, intent: Mapping[str, object]) -> None | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._store_approval` | method | `src/jarvis_v2/core/intent.py:232-241` | def _store_approval(self, request_id: str, approval: Mapping[str, object], intent_sha: str, now: str) -> None | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter._snapshot` | method | `src/jarvis_v2/core/intent.py:243-263` | def _snapshot(self, row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.intent.OwnerIntentRouter.close` | method | `src/jarvis_v2/core/intent.py:265-267` | def close(self) -> None | 34 | active |
| `jarvis_v2.core.model_policy.ModelPolicyError` | class | `src/jarvis_v2/core/model_policy.py:12-13` | class ModelPolicyError(ValueError) | 1 | active |
| `jarvis_v2.core.model_policy.ModelResolution` | class | `src/jarvis_v2/core/model_policy.py:17-26` | class ModelResolution() | 0 | active |
| `jarvis_v2.core.model_policy.ModelResolution.as_dict` | method | `src/jarvis_v2/core/model_policy.py:25-26` | def as_dict(self) -> dict[str, str \| None] | 18 | active |
| `jarvis_v2.core.model_policy.ModelPolicy` | class | `src/jarvis_v2/core/model_policy.py:29-73` | class ModelPolicy() | 1 | active |
| `jarvis_v2.core.model_policy.ModelPolicy.__init__` | method | `src/jarvis_v2/core/model_policy.py:36-43` | def __init__(self, available_models: Iterable[str]) -> None | 5 | active |
| `jarvis_v2.core.model_policy.ModelPolicy.available_models` | method | `src/jarvis_v2/core/model_policy.py:46-47` | def available_models(self) -> frozenset[str] | 0 | active |
| `jarvis_v2.core.model_policy.ModelPolicy.resolve` | method | `src/jarvis_v2/core/model_policy.py:49-67` | def resolve(self, requested: str, *, fallback: str \| None=None, allow_fallback: bool=False) -> ModelResolution | 18 | active |
| `jarvis_v2.core.model_policy.ModelPolicy._alias` | method | `src/jarvis_v2/core/model_policy.py:70-73` | def _alias(value: str) -> str | 0 | active |
| `jarvis_v2.core.queue.TaskQueue` | class | `src/jarvis_v2/core/queue.py:24-271` | class TaskQueue() | 16 | active |
| `jarvis_v2.core.queue.TaskQueue.__init__` | method | `src/jarvis_v2/core/queue.py:25-63` | def __init__(self, path: Path) | 5 | active |
| `jarvis_v2.core.queue.TaskQueue.add` | method | `src/jarvis_v2/core/queue.py:65-72` | def add(self, *, task_id: str, priority: str, module: str, payload: dict, title: str='') -> None | 28 | active |
| `jarvis_v2.core.queue.TaskQueue.block` | method | `src/jarvis_v2/core/queue.py:74-96` | def block(self, task_id: str, *, reason: str, lease: str \| None=None) -> None | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.unblock` | method | `src/jarvis_v2/core/queue.py:98-109` | def unblock(self, task_id: str) -> None | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.lease_next` | method | `src/jarvis_v2/core/queue.py:111-139` | def lease_next(self, *, guardian_waiting: bool=False, allowed_modules: set[str] \| None=None) -> dict \| None | 12 | active |
| `jarvis_v2.core.queue.TaskQueue.eligible` | method | `src/jarvis_v2/core/queue.py:141-157` | def eligible(self, *, guardian_waiting: bool=False, allowed_modules: set[str] \| None=None) -> list[dict] | 4 | active |
| `jarvis_v2.core.queue.TaskQueue.finish` | method | `src/jarvis_v2/core/queue.py:159-164` | def finish(self, task_id: str, lease: str, *, ok: bool, receipt: str) -> None | 12 | active |
| `jarvis_v2.core.queue.TaskQueue.status` | method | `src/jarvis_v2/core/queue.py:166-167` | def status(self) -> list[dict] | 80 | active |
| `jarvis_v2.core.queue.TaskQueue.history` | method | `src/jarvis_v2/core/queue.py:169-180` | def history(self, task_id: str, *, limit: int=MAX_HISTORY_ENTRIES) -> list[dict] | 12 | active |
| `jarvis_v2.core.queue.TaskQueue.replay_events` | method | `src/jarvis_v2/core/queue.py:182-195` | def replay_events(self, consumer: str, *, limit: int=MAX_EVENT_BATCH) -> list[dict] | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.ack_event` | method | `src/jarvis_v2/core/queue.py:197-209` | def ack_event(self, consumer: str, seq: int) -> None | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.open_session` | method | `src/jarvis_v2/core/queue.py:211-212` | def open_session(self, task_id: str, **kwargs) -> dict | 3 | active |
| `jarvis_v2.core.queue.TaskQueue._emit_event` | method | `src/jarvis_v2/core/queue.py:214-215` | def _emit_event(self, task_id: str, kind: str, detail: str) -> dict | 0 | active |
| `jarvis_v2.core.queue.TaskQueue.restore_session` | method | `src/jarvis_v2/core/queue.py:217-218` | def restore_session(self, task_id: str \| None=None, *, session_id: str \| None=None) -> dict | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.record_decision` | method | `src/jarvis_v2/core/queue.py:220-221` | def record_decision(self, session_id: str, decision_id: str, decision: dict) -> dict | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.record_handoff` | method | `src/jarvis_v2/core/queue.py:223-224` | def record_handoff(self, session_id: str, handoff_id: str, handoff: dict) -> dict | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.record_receipt` | method | `src/jarvis_v2/core/queue.py:226-227` | def record_receipt(self, session_id: str, effect_id: str, receipt: dict) -> dict | 2 | active |
| `jarvis_v2.core.queue.TaskQueue.checkpoint_session` | method | `src/jarvis_v2/core/queue.py:229-230` | def checkpoint_session(self, session_id: str, **kwargs) -> dict | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.dispatch` | method | `src/jarvis_v2/core/queue.py:232-233` | def dispatch(self, task_id: str, target_module: str, scope, acceptance, **kwargs) -> dict | 6 | active |
| `jarvis_v2.core.queue.TaskQueue.claim_dispatch` | method | `src/jarvis_v2/core/queue.py:235-236` | def claim_dispatch(self, dispatch_id: str, executor_id: str, **kwargs) -> dict | 3 | active |
| `jarvis_v2.core.queue.TaskQueue.acknowledge_dispatch` | method | `src/jarvis_v2/core/queue.py:238-239` | def acknowledge_dispatch(self, dispatch_id: str, executor_id: str, claim_id: str, **kwargs) -> dict | 3 | active |
| `jarvis_v2.core.queue.TaskQueue.restore_dispatch` | method | `src/jarvis_v2/core/queue.py:241-242` | def restore_dispatch(self, dispatch_id: str) -> dict | 2 | active |
| `jarvis_v2.core.queue.TaskQueue.submit_intent` | method | `src/jarvis_v2/core/queue.py:244-245` | def submit_intent(self, intent: dict, *, approval: dict \| None=None) -> dict | 2 | active |
| `jarvis_v2.core.queue.TaskQueue.record_event_failure` | method | `src/jarvis_v2/core/queue.py:247-248` | def record_event_failure(self, event_id: str, failure_code: str, diagnostic: str) -> dict | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.event_failure` | method | `src/jarvis_v2/core/queue.py:250-251` | def event_failure(self, event_id: str) -> dict \| None | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.control_status` | method | `src/jarvis_v2/core/queue.py:253-254` | def control_status(self) -> dict[str, str] | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.stop` | method | `src/jarvis_v2/core/queue.py:256-257` | def stop(self, *, reason: str='owner_stop') -> dict[str, str] | 4 | active |
| `jarvis_v2.core.queue.TaskQueue.pause` | method | `src/jarvis_v2/core/queue.py:259-260` | def pause(self, *, reason: str='owner_pause') -> dict[str, str] | 1 | active |
| `jarvis_v2.core.queue.TaskQueue.resume` | method | `src/jarvis_v2/core/queue.py:262-263` | def resume(self) -> dict[str, str] | 3 | active |
| `jarvis_v2.core.queue.TaskQueue.timeline` | method | `src/jarvis_v2/core/queue.py:265-266` | def timeline(self, task_id: str, *, limit: int=MAX_EVENT_BATCH) -> dict | 2 | active |
| `jarvis_v2.core.queue.TaskQueue.progress` | method | `src/jarvis_v2/core/queue.py:268-269` | def progress(self, task_id: str) -> dict | 4 | active |
| `jarvis_v2.core.queue.TaskQueue.close` | method | `src/jarvis_v2/core/queue.py:271-271` | def close(self) | 34 | active |
| `jarvis_v2.core.registry.CoreRegistryError` | class | `src/jarvis_v2/core/registry.py:18-19` | class CoreRegistryError(ValueError) | 1 | active |
| `jarvis_v2.core.registry.ModuleCapability` | class | `src/jarvis_v2/core/registry.py:23-29` | class ModuleCapability() | 0 | active |
| `jarvis_v2.core.registry.ModuleRegistry` | class | `src/jarvis_v2/core/registry.py:32-113` | class ModuleRegistry() | 7 | active |
| `jarvis_v2.core.registry.ModuleRegistry.__init__` | method | `src/jarvis_v2/core/registry.py:35-37` | def __init__(self, capabilities: tuple[ModuleCapability, ...]) -> None | 5 | active |
| `jarvis_v2.core.registry.ModuleRegistry.from_manifests` | method | `src/jarvis_v2/core/registry.py:40-55` | def from_manifests(cls, manifests: list[Mapping[str, Any]] \| tuple[Mapping[str, Any], ...]) -> 'ModuleRegistry' | 0 | active |
| `jarvis_v2.core.registry.ModuleRegistry.from_config` | method | `src/jarvis_v2/core/registry.py:58-89` | def from_config(cls, path: str \| Path) -> 'ModuleRegistry' | 7 | active |
| `jarvis_v2.core.registry.ModuleRegistry.all` | method | `src/jarvis_v2/core/registry.py:91-93` | def all(self) -> tuple[ModuleCapability, ...] | 14 | active |
| `jarvis_v2.core.registry.ModuleRegistry.resolve` | method | `src/jarvis_v2/core/registry.py:95-104` | def resolve(self, module: int \| str) -> ModuleCapability | 18 | active |
| `jarvis_v2.core.registry.ModuleRegistry.authorize` | method | `src/jarvis_v2/core/registry.py:106-109` | def authorize(self, module: int \| str, scope: str) -> bool | 6 | active |
| `jarvis_v2.core.registry.ModuleRegistry.by_id` | method | `src/jarvis_v2/core/registry.py:112-113` | def by_id(self) -> Mapping[int, ModuleCapability] | 1 | active |
| `jarvis_v2.core.registry.CoreService` | class | `src/jarvis_v2/core/registry.py:117-130` | class CoreService() | 1 | active |
| `jarvis_v2.core.registry.CoreService.from_config` | method | `src/jarvis_v2/core/registry.py:123-124` | def from_config(cls, path: str \| Path) -> 'CoreService' | 7 | active |
| `jarvis_v2.core.registry.CoreService.module` | method | `src/jarvis_v2/core/registry.py:126-127` | def module(self, identity: int \| str) -> ModuleCapability | 40 | active |
| `jarvis_v2.core.registry.CoreService.can` | method | `src/jarvis_v2/core/registry.py:129-130` | def can(self, identity: int \| str, scope: str) -> bool | 1 | active |
| `jarvis_v2.core.session.SessionError` | class | `src/jarvis_v2/core/session.py:22-23` | class SessionError(ValueError) | 1 | active |
| `jarvis_v2.core.session._identifier` | function | `src/jarvis_v2/core/session.py:26-29` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.core.session._json` | function | `src/jarvis_v2/core/session.py:32-47` | def _json(value: Mapping[str, object], *, limit: int, label: str) -> str | 0 | active |
| `jarvis_v2.core.session._now` | function | `src/jarvis_v2/core/session.py:50-51` | def _now() -> str | 0 | active |
| `jarvis_v2.core.session.TaskSessionStore` | class | `src/jarvis_v2/core/session.py:54-337` | class TaskSessionStore() | 1 | active |
| `jarvis_v2.core.session.TaskSessionStore.__init__` | method | `src/jarvis_v2/core/session.py:62-98` | def __init__(self, database: Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.session.TaskSessionStore.open_session` | method | `src/jarvis_v2/core/session.py:100-147` | def open_session(self, task_id: str, *, session_id: str \| None=None, correlation_id: str \| None=None, context: Mapping[str, object] \| None=None) -> dict | 3 | active |
| `jarvis_v2.core.session.TaskSessionStore.restore_session` | method | `src/jarvis_v2/core/session.py:149-167` | def restore_session(self, task_id: str \| None=None, *, session_id: str \| None=None) -> dict | 1 | active |
| `jarvis_v2.core.session.TaskSessionStore.append` | method | `src/jarvis_v2/core/session.py:169-221` | def append(self, session_id: str, kind: str, payload: Mapping[str, object], *, idempotency_key: str) -> dict | 31 | active |
| `jarvis_v2.core.session.TaskSessionStore.record_decision` | method | `src/jarvis_v2/core/session.py:223-224` | def record_decision(self, session_id: str, decision_id: str, decision: Mapping[str, object]) -> dict | 1 | active |
| `jarvis_v2.core.session.TaskSessionStore.record_handoff` | method | `src/jarvis_v2/core/session.py:226-227` | def record_handoff(self, session_id: str, handoff_id: str, handoff: Mapping[str, object]) -> dict | 1 | active |
| `jarvis_v2.core.session.TaskSessionStore.record_receipt` | method | `src/jarvis_v2/core/session.py:229-230` | def record_receipt(self, session_id: str, effect_id: str, receipt: Mapping[str, object]) -> dict | 2 | active |
| `jarvis_v2.core.session.TaskSessionStore.checkpoint_session` | method | `src/jarvis_v2/core/session.py:232-297` | def checkpoint_session(self, session_id: str, *, checkpoint: Mapping[str, object], context: Mapping[str, object] \| None=None, status: str='active', checkpoint_id: str \| None=None | 1 | active |
| `jarvis_v2.core.session.TaskSessionStore._snapshot` | method | `src/jarvis_v2/core/session.py:299-321` | def _snapshot(self, row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.session.TaskSessionStore._record` | method | `src/jarvis_v2/core/session.py:324-333` | def _record(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.session.TaskSessionStore.close` | method | `src/jarvis_v2/core/session.py:335-337` | def close(self) -> None | 34 | active |
| `jarvis_v2.core.timeline.TimelineError` | class | `src/jarvis_v2/core/timeline.py:15-16` | class TimelineError(ValueError) | 1 | active |
| `jarvis_v2.core.timeline._identifier` | function | `src/jarvis_v2/core/timeline.py:19-22` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.core.timeline._limit` | function | `src/jarvis_v2/core/timeline.py:25-28` | def _limit(value: int) -> int | 0 | active |
| `jarvis_v2.core.timeline._sha256` | function | `src/jarvis_v2/core/timeline.py:31-32` | def _sha256(value: str) -> str | 0 | active |
| `jarvis_v2.core.timeline.TaskTimeline` | class | `src/jarvis_v2/core/timeline.py:35-197` | class TaskTimeline() | 0 | active |
| `jarvis_v2.core.timeline.TaskTimeline.__init__` | method | `src/jarvis_v2/core/timeline.py:38-45` | def __init__(self, database: Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.core.timeline.TaskTimeline.timeline` | method | `src/jarvis_v2/core/timeline.py:47-132` | def timeline(self, task_id: str, *, limit: int=MAX_TIMELINE_ENTRIES) -> dict | 2 | active |
| `jarvis_v2.core.timeline.TaskTimeline.progress` | method | `src/jarvis_v2/core/timeline.py:134-152` | def progress(self, task_id: str) -> dict | 4 | active |
| `jarvis_v2.core.timeline.TaskTimeline._event` | method | `src/jarvis_v2/core/timeline.py:155-165` | def _event(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.timeline.TaskTimeline._record` | method | `src/jarvis_v2/core/timeline.py:168-177` | def _record(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.timeline.TaskTimeline._dispatch` | method | `src/jarvis_v2/core/timeline.py:180-193` | def _dispatch(row: sqlite3.Row) -> dict | 0 | active |
| `jarvis_v2.core.timeline.TaskTimeline.close` | method | `src/jarvis_v2/core/timeline.py:195-197` | def close(self) -> None | 34 | active |
| `jarvis_v2.finance.advice.FinanceAdviceError` | class | `src/jarvis_v2/finance/advice.py:10-11` | class FinanceAdviceError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.advice.FinanceRecommendation` | class | `src/jarvis_v2/finance/advice.py:15-62` | class FinanceRecommendation() | 0 | active |
| `jarvis_v2.finance.advice.FinanceRecommendation.__post_init__` | method | `src/jarvis_v2/finance/advice.py:26-39` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.advice.FinanceRecommendation.approve` | method | `src/jarvis_v2/finance/advice.py:41-46` | def approve(self, *, consent_granted: bool) -> 'FinanceRecommendation' | 6 | active |
| `jarvis_v2.finance.advice.FinanceRecommendation.suppress` | method | `src/jarvis_v2/finance/advice.py:48-49` | def suppress(self) -> 'FinanceRecommendation' | 2 | active |
| `jarvis_v2.finance.advice.FinanceRecommendation.as_dict` | method | `src/jarvis_v2/finance/advice.py:51-62` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.advice.FinanceNotification` | class | `src/jarvis_v2/finance/advice.py:66-96` | class FinanceNotification() | 0 | active |
| `jarvis_v2.finance.advice.FinanceNotification.__post_init__` | method | `src/jarvis_v2/finance/advice.py:74-81` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.advice.FinanceNotification.deliverable` | method | `src/jarvis_v2/finance/advice.py:84-85` | def deliverable(self) -> bool | 5 | active |
| `jarvis_v2.finance.advice.FinanceNotification.as_dict` | method | `src/jarvis_v2/finance/advice.py:87-96` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.advice.FinanceAdviceService` | class | `src/jarvis_v2/finance/advice.py:99-139` | class FinanceAdviceService() | 1 | active |
| `jarvis_v2.finance.advice.FinanceAdviceService.__init__` | method | `src/jarvis_v2/finance/advice.py:102-106` | def __init__(self, store: FinanceStore) | 5 | active |
| `jarvis_v2.finance.advice.FinanceAdviceService.recommendations` | method | `src/jarvis_v2/finance/advice.py:108-118` | def recommendations(self, source_id: str, scope_id: str, *, consent_granted: bool=False) -> tuple[FinanceRecommendation, ...] | 1 | active |
| `jarvis_v2.finance.advice.FinanceAdviceService.notification` | method | `src/jarvis_v2/finance/advice.py:121-139` | def notification(recommendation: FinanceRecommendation, *, consent_granted: bool=False) -> FinanceNotification | 2 | active |
| `jarvis_v2.finance.alerts.FinanceAlertError` | class | `src/jarvis_v2/finance/alerts.py:11-12` | class FinanceAlertError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.alerts.FinanceAlert` | class | `src/jarvis_v2/finance/alerts.py:16-64` | class FinanceAlert() | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlert.__post_init__` | method | `src/jarvis_v2/finance/alerts.py:29-48` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlert.suppress` | method | `src/jarvis_v2/finance/alerts.py:50-51` | def suppress(self) -> 'FinanceAlert' | 2 | active |
| `jarvis_v2.finance.alerts.FinanceAlert.as_dict` | method | `src/jarvis_v2/finance/alerts.py:53-64` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService` | class | `src/jarvis_v2/finance/alerts.py:67-134` | class FinanceAlertService() | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService.__init__` | method | `src/jarvis_v2/finance/alerts.py:70-73` | def __init__(self, store: FinanceStore) | 5 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService.detect` | method | `src/jarvis_v2/finance/alerts.py:75-92` | def detect(self, source_id: str, scope_id: str, *, unusual_multiplier: int=2) -> tuple[FinanceAlert, ...] | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService.suppress` | method | `src/jarvis_v2/finance/alerts.py:95-101` | def suppress(alerts: tuple[FinanceAlert, ...], alert_id: str) -> tuple[FinanceAlert, ...] | 2 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService._recurring` | method | `src/jarvis_v2/finance/alerts.py:104-120` | def _recurring(source_id: str, scope_id: str, transactions: tuple[FinanceTransaction, ...]) -> tuple[FinanceAlert, ...] | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService._unusual` | method | `src/jarvis_v2/finance/alerts.py:123-129` | def _unusual(source_id: str, scope_id: str, transaction: FinanceTransaction, typical: int, threshold: int) -> FinanceAlert | 0 | active |
| `jarvis_v2.finance.alerts.FinanceAlertService._id` | method | `src/jarvis_v2/finance/alerts.py:132-134` | def _id(kind: str, source_id: str, scope_id: str, transaction_ids: tuple[str, ...]) -> str | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardError` | class | `src/jarvis_v2/finance/dashboard.py:23-24` | class FinanceDashboardError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.dashboard.FinanceBalance` | class | `src/jarvis_v2/finance/dashboard.py:28-71` | class FinanceBalance() | 1 | active |
| `jarvis_v2.finance.dashboard.FinanceBalance.__post_init__` | method | `src/jarvis_v2/finance/dashboard.py:38-45` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceBalance.from_mapping` | method | `src/jarvis_v2/finance/dashboard.py:48-61` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceBalance' | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceBalance.as_dict` | method | `src/jarvis_v2/finance/dashboard.py:63-71` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboard` | class | `src/jarvis_v2/finance/dashboard.py:75-102` | class FinanceDashboard() | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboard.__post_init__` | method | `src/jarvis_v2/finance/dashboard.py:82-91` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboard.person_id` | method | `src/jarvis_v2/finance/dashboard.py:94-95` | def person_id(self) -> str | 1 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboard.as_dict` | method | `src/jarvis_v2/finance/dashboard.py:97-102` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardService` | class | `src/jarvis_v2/finance/dashboard.py:105-178` | class FinanceDashboardService() | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardService.__init__` | method | `src/jarvis_v2/finance/dashboard.py:108-111` | def __init__(self, store: FinanceStore) | 5 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardService.snapshot` | method | `src/jarvis_v2/finance/dashboard.py:113-152` | def snapshot(self, source_id: str, scope_id: str, *, reconciled_balances: Iterable[FinanceBalance \| Mapping[str, object]]=()) -> FinanceDashboard | 17 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardService._coerce_reconciled` | method | `src/jarvis_v2/finance/dashboard.py:157-174` | def _coerce_reconciled(values: Iterable[FinanceBalance \| Mapping[str, object]]) -> dict[str, FinanceBalance] | 0 | active |
| `jarvis_v2.finance.dashboard.FinanceDashboardService._instant` | method | `src/jarvis_v2/finance/dashboard.py:177-178` | def _instant(value: str) -> float | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceIngestionError` | class | `src/jarvis_v2/finance/ingestion.py:26-27` | class FinanceIngestionError(ValueError) | 1 | active |
| `jarvis_v2.finance.ingestion._identifier` | function | `src/jarvis_v2/finance/ingestion.py:30-33` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.finance.ingestion._text` | function | `src/jarvis_v2/finance/ingestion.py:36-44` | def _text(value: object, label: str, maximum: int=_MAX_TEXT_BYTES) -> str | 2 | active |
| `jarvis_v2.finance.ingestion._currency` | function | `src/jarvis_v2/finance/ingestion.py:47-50` | def _currency(value: object) -> str | 0 | active |
| `jarvis_v2.finance.ingestion._timestamp` | function | `src/jarvis_v2/finance/ingestion.py:53-62` | def _timestamp(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.finance.ingestion._date` | function | `src/jarvis_v2/finance/ingestion.py:65-72` | def _date(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.finance.ingestion._satang` | function | `src/jarvis_v2/finance/ingestion.py:75-80` | def _satang(value: object, label: str, *, nonnegative: bool=False) -> int | 0 | active |
| `jarvis_v2.finance.ingestion._pick` | function | `src/jarvis_v2/finance/ingestion.py:83-89` | def _pick(data: Mapping[str, object], label: str, *keys: str, default: object=_MISSING) -> object | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceAccount` | class | `src/jarvis_v2/finance/ingestion.py:93-124` | class FinanceAccount() | 8 | active |
| `jarvis_v2.finance.ingestion.FinanceAccount.__post_init__` | method | `src/jarvis_v2/finance/ingestion.py:101-105` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceAccount.as_dict` | method | `src/jarvis_v2/finance/ingestion.py:107-113` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.ingestion.FinanceAccount.from_mapping` | method | `src/jarvis_v2/finance/ingestion.py:116-124` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceAccount' | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceCategory` | class | `src/jarvis_v2/finance/ingestion.py:128-155` | class FinanceCategory() | 4 | active |
| `jarvis_v2.finance.ingestion.FinanceCategory.__post_init__` | method | `src/jarvis_v2/finance/ingestion.py:135-138` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceCategory.as_dict` | method | `src/jarvis_v2/finance/ingestion.py:140-145` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.ingestion.FinanceCategory.from_mapping` | method | `src/jarvis_v2/finance/ingestion.py:148-155` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceCategory' | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceBudget` | class | `src/jarvis_v2/finance/ingestion.py:159-205` | class FinanceBudget() | 2 | active |
| `jarvis_v2.finance.ingestion.FinanceBudget.__post_init__` | method | `src/jarvis_v2/finance/ingestion.py:170-180` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceBudget.as_dict` | method | `src/jarvis_v2/finance/ingestion.py:182-191` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.ingestion.FinanceBudget.from_mapping` | method | `src/jarvis_v2/finance/ingestion.py:194-205` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceBudget' | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceTransaction` | class | `src/jarvis_v2/finance/ingestion.py:209-258` | class FinanceTransaction() | 8 | active |
| `jarvis_v2.finance.ingestion.FinanceTransaction.__post_init__` | method | `src/jarvis_v2/finance/ingestion.py:221-231` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceTransaction.as_dict` | method | `src/jarvis_v2/finance/ingestion.py:233-243` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.ingestion.FinanceTransaction.from_mapping` | method | `src/jarvis_v2/finance/ingestion.py:246-258` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceTransaction' | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceSyncResult` | class | `src/jarvis_v2/finance/ingestion.py:262-281` | class FinanceSyncResult() | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceSyncResult.total` | method | `src/jarvis_v2/finance/ingestion.py:270-271` | def total(self) -> int | 6 | active |
| `jarvis_v2.finance.ingestion.FinanceSyncResult.as_dict` | method | `src/jarvis_v2/finance/ingestion.py:273-281` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.ingestion.FinanceStore` | class | `src/jarvis_v2/finance/ingestion.py:287-486` | class FinanceStore() | 8 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.__init__` | method | `src/jarvis_v2/finance/ingestion.py:303-309` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._create_tables` | method | `src/jarvis_v2/finance/ingestion.py:311-321` | def _create_tables(self) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.__enter__` | method | `src/jarvis_v2/finance/ingestion.py:323-324` | def __enter__(self) -> 'FinanceStore' | 1 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.__exit__` | method | `src/jarvis_v2/finance/ingestion.py:326-327` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.close` | method | `src/jarvis_v2/finance/ingestion.py:329-331` | def close(self) -> None | 34 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.sync` | method | `src/jarvis_v2/finance/ingestion.py:333-389` | def sync(self, source_id: str, scope_id: str, *, accounts: Iterable[FinanceAccount \| Mapping[str, object]]=(), categories: Iterable[FinanceCategory \| Mapping[str, object]]=(), bu | 13 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._insert` | method | `src/jarvis_v2/finance/ingestion.py:393-397` | def _insert(self, source_id: str, scope_id: str, table: str, columns: tuple[str, ...], record: object, payload: str) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._update` | method | `src/jarvis_v2/finance/ingestion.py:399-403` | def _update(self, source_id: str, scope_id: str, table: str, identity: str, columns: tuple[str, ...], record: object, payload: str) -> None | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._coerce` | method | `src/jarvis_v2/finance/ingestion.py:406-423` | def _coerce(values: Iterable[Record \| Mapping[str, object]], cls: type[Record], label: str) -> tuple[Record, ...] | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._instant` | method | `src/jarvis_v2/finance/ingestion.py:426-427` | def _instant(value: str) -> float | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore._records` | method | `src/jarvis_v2/finance/ingestion.py:429-441` | def _records(self, source_id: str, scope_id: str, cls: type[Record]) -> tuple[Record, ...] | 0 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.accounts` | method | `src/jarvis_v2/finance/ingestion.py:443-444` | def accounts(self, source_id: str, scope_id: str) -> tuple[FinanceAccount, ...] | 8 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.categories` | method | `src/jarvis_v2/finance/ingestion.py:446-447` | def categories(self, source_id: str, scope_id: str) -> tuple[FinanceCategory, ...] | 6 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.budgets` | method | `src/jarvis_v2/finance/ingestion.py:449-450` | def budgets(self, source_id: str, scope_id: str) -> tuple[FinanceBudget, ...] | 3 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.transactions` | method | `src/jarvis_v2/finance/ingestion.py:452-453` | def transactions(self, source_id: str, scope_id: str) -> tuple[FinanceTransaction, ...] | 8 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.dashboard` | method | `src/jarvis_v2/finance/ingestion.py:455-460` | def dashboard(self, source_id: str, scope_id: str, *, reconciled_balances=()) | 3 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.report` | method | `src/jarvis_v2/finance/ingestion.py:462-467` | def report(self, source_id: str, scope_id: str, *, start_date=None, end_date=None) | 14 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.forecast` | method | `src/jarvis_v2/finance/ingestion.py:469-472` | def forecast(self, source_id: str, scope_id: str) | 1 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.alerts` | method | `src/jarvis_v2/finance/ingestion.py:474-479` | def alerts(self, source_id: str, scope_id: str, *, unusual_multiplier=2) | 2 | active |
| `jarvis_v2.finance.ingestion.FinanceStore.recommendations` | method | `src/jarvis_v2/finance/ingestion.py:481-486` | def recommendations(self, source_id: str, scope_id: str, *, consent_granted=False) | 1 | active |
| `jarvis_v2.finance.mira_audit.schema_sha256` | function | `src/jarvis_v2/finance/mira_audit.py:31-40` | def schema_sha256(schema: Mapping[str, str]) -> str | 1 | active |
| `jarvis_v2.finance.mira_audit.MiraAuditSnapshot` | class | `src/jarvis_v2/finance/mira_audit.py:44-129` | class MiraAuditSnapshot() | 1 | active |
| `jarvis_v2.finance.mira_audit.MiraAuditSnapshot.validate` | method | `src/jarvis_v2/finance/mira_audit.py:65-99` | def validate(self) -> None | 2 | active |
| `jarvis_v2.finance.mira_audit.MiraAuditSnapshot.evidence` | method | `src/jarvis_v2/finance/mira_audit.py:101-129` | def evidence(self) -> dict[str, object] | 17 | active |
| `jarvis_v2.finance.mira_audit.authorize_mira_method` | function | `src/jarvis_v2/finance/mira_audit.py:132-134` | def authorize_mira_method(method: str) -> bool | 1 | active |
| `jarvis_v2.finance.mira_connector.MiraExportToken` | class | `src/jarvis_v2/finance/mira_connector.py:29-35` | class MiraExportToken() | 0 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker` | class | `src/jarvis_v2/finance/mira_connector.py:38-85` | class MiraConnectorTokenBroker() | 2 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.__init__` | method | `src/jarvis_v2/finance/mira_connector.py:41-42` | def __init__(self) -> None | 5 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.issue` | method | `src/jarvis_v2/finance/mira_connector.py:44-59` | def issue(self, identity_id: str, *, token_id: str \| None=None, ttl_seconds: int=300) -> MiraExportToken | 3 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.authorize` | method | `src/jarvis_v2/finance/mira_connector.py:61-64` | def authorize(self, identity_id: str, token_id: str, scope: str=MIRA_READ_SCOPE) -> bool | 6 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.revoke` | method | `src/jarvis_v2/finance/mira_connector.py:66-67` | def revoke(self, token_id: str) -> None | 5 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.run_read_sync` | method | `src/jarvis_v2/finance/mira_connector.py:69-78` | def run_read_sync(self, identity_id: str, token_id: str, operation: Callable[[], _Result]) -> _Result | 1 | active |
| `jarvis_v2.finance.mira_connector.MiraConnectorTokenBroker.audit` | method | `src/jarvis_v2/finance/mira_connector.py:80-85` | def audit(self) -> tuple[dict[str, object], ...] | 6 | active |
| `jarvis_v2.finance.paper.PaperLedgerError` | class | `src/jarvis_v2/finance/paper.py:12-13` | class PaperLedgerError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.paper._quantity` | function | `src/jarvis_v2/finance/paper.py:16-19` | def _quantity(value: object, label: str='quantity') -> int | 0 | active |
| `jarvis_v2.finance.paper.PaperFillPolicy` | class | `src/jarvis_v2/finance/paper.py:23-54` | class PaperFillPolicy() | 1 | active |
| `jarvis_v2.finance.paper.PaperFillPolicy.__post_init__` | method | `src/jarvis_v2/finance/paper.py:34-47` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.paper.PaperFillPolicy.validate` | method | `src/jarvis_v2/finance/paper.py:49-54` | def validate(self, filled_at: str) -> None | 2 | active |
| `jarvis_v2.finance.paper.PaperAccount` | class | `src/jarvis_v2/finance/paper.py:58-79` | class PaperAccount() | 1 | active |
| `jarvis_v2.finance.paper.PaperAccount.__post_init__` | method | `src/jarvis_v2/finance/paper.py:65-70` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.paper.PaperAccount.as_dict` | method | `src/jarvis_v2/finance/paper.py:72-79` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.paper.PaperOrder` | class | `src/jarvis_v2/finance/paper.py:83-139` | class PaperOrder() | 1 | active |
| `jarvis_v2.finance.paper.PaperOrder.__post_init__` | method | `src/jarvis_v2/finance/paper.py:96-120` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.paper.PaperOrder.notional_satang` | method | `src/jarvis_v2/finance/paper.py:123-124` | def notional_satang(self) -> int | 0 | active |
| `jarvis_v2.finance.paper.PaperOrder.as_dict` | method | `src/jarvis_v2/finance/paper.py:126-139` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.paper.PaperPosition` | class | `src/jarvis_v2/finance/paper.py:143-164` | class PaperPosition() | 0 | active |
| `jarvis_v2.finance.paper.PaperPosition.__post_init__` | method | `src/jarvis_v2/finance/paper.py:150-155` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.paper.PaperPosition.as_dict` | method | `src/jarvis_v2/finance/paper.py:157-164` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.paper.PaperLedger` | class | `src/jarvis_v2/finance/paper.py:167-343` | class PaperLedger() | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.__init__` | method | `src/jarvis_v2/finance/paper.py:170-202` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.finance.paper.PaperLedger.__enter__` | method | `src/jarvis_v2/finance/paper.py:204-205` | def __enter__(self) -> 'PaperLedger' | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.__exit__` | method | `src/jarvis_v2/finance/paper.py:207-208` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.close` | method | `src/jarvis_v2/finance/paper.py:210-212` | def close(self) -> None | 34 | active |
| `jarvis_v2.finance.paper.PaperLedger.open_account` | method | `src/jarvis_v2/finance/paper.py:214-228` | def open_account(self, account: PaperAccount) -> PaperAccount | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.place_order` | method | `src/jarvis_v2/finance/paper.py:230-246` | def place_order(self, order: PaperOrder) -> PaperOrder | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.fill_order` | method | `src/jarvis_v2/finance/paper.py:248-312` | def fill_order(self, order_id: str, *, filled_at: str, policy: PaperFillPolicy \| None=None) -> PaperOrder | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger.account` | method | `src/jarvis_v2/finance/paper.py:314-319` | def account(self, account_id: str) -> PaperAccount | 3 | active |
| `jarvis_v2.finance.paper.PaperLedger.orders` | method | `src/jarvis_v2/finance/paper.py:321-323` | def orders(self, account_id: str) -> tuple[PaperOrder, ...] | 0 | active |
| `jarvis_v2.finance.paper.PaperLedger.positions` | method | `src/jarvis_v2/finance/paper.py:325-327` | def positions(self, account_id: str) -> tuple[PaperPosition, ...] | 1 | active |
| `jarvis_v2.finance.paper.PaperLedger._account` | method | `src/jarvis_v2/finance/paper.py:330-331` | def _account(row: sqlite3.Row) -> PaperAccount | 0 | active |
| `jarvis_v2.finance.paper.PaperLedger._order` | method | `src/jarvis_v2/finance/paper.py:334-339` | def _order(row: sqlite3.Row) -> PaperOrder | 0 | active |
| `jarvis_v2.finance.paper.PaperLedger._position` | method | `src/jarvis_v2/finance/paper.py:342-343` | def _position(row: sqlite3.Row) -> PaperPosition | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformanceError` | class | `src/jarvis_v2/finance/performance.py:11-12` | class PaperPerformanceError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.performance._quantity` | function | `src/jarvis_v2/finance/performance.py:15-18` | def _quantity(value: object, label: str) -> int | 0 | active |
| `jarvis_v2.finance.performance.PaperTrade` | class | `src/jarvis_v2/finance/performance.py:22-43` | class PaperTrade() | 1 | active |
| `jarvis_v2.finance.performance.PaperTrade.__post_init__` | method | `src/jarvis_v2/finance/performance.py:30-39` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.performance.PaperTrade.notional_satang` | method | `src/jarvis_v2/finance/performance.py:42-43` | def notional_satang(self) -> int | 0 | active |
| `jarvis_v2.finance.performance.PaperMarketMark` | class | `src/jarvis_v2/finance/performance.py:47-57` | class PaperMarketMark() | 1 | active |
| `jarvis_v2.finance.performance.PaperMarketMark.__post_init__` | method | `src/jarvis_v2/finance/performance.py:52-57` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.performance.PaperSplit` | class | `src/jarvis_v2/finance/performance.py:61-71` | class PaperSplit() | 1 | active |
| `jarvis_v2.finance.performance.PaperSplit.__post_init__` | method | `src/jarvis_v2/finance/performance.py:67-71` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformance` | class | `src/jarvis_v2/finance/performance.py:75-101` | class PaperPerformance() | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformance.__post_init__` | method | `src/jarvis_v2/finance/performance.py:83-91` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformance.as_dict` | method | `src/jarvis_v2/finance/performance.py:93-101` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.performance.PaperPerformanceService` | class | `src/jarvis_v2/finance/performance.py:104-192` | class PaperPerformanceService() | 1 | active |
| `jarvis_v2.finance.performance.PaperPerformanceService.evaluate` | method | `src/jarvis_v2/finance/performance.py:108-171` | def evaluate(initial_cash_satang: int, trades: Iterable[PaperTrade], marks: Iterable[PaperMarketMark], corporate_actions: Iterable[PaperSplit]=()) -> PaperPerformance | 2 | active |
| `jarvis_v2.finance.performance.PaperPerformanceService._records` | method | `src/jarvis_v2/finance/performance.py:174-183` | def _records(values: Iterable[object], cls: type[object], label: str) -> tuple[object, ...] | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformanceService._ordered` | method | `src/jarvis_v2/finance/performance.py:186-188` | def _ordered(values: list[str], label: str) -> None | 0 | active |
| `jarvis_v2.finance.performance.PaperPerformanceService._instant` | method | `src/jarvis_v2/finance/performance.py:191-192` | def _instant(value: str) -> float | 0 | active |
| `jarvis_v2.finance.planning.FinancePlanningError` | class | `src/jarvis_v2/finance/planning.py:11-12` | class FinancePlanningError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.planning.FinanceGoal` | class | `src/jarvis_v2/finance/planning.py:16-46` | class FinanceGoal() | 1 | active |
| `jarvis_v2.finance.planning.FinanceGoal.__post_init__` | method | `src/jarvis_v2/finance/planning.py:25-32` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.planning.FinanceGoal.remaining_satang` | method | `src/jarvis_v2/finance/planning.py:35-36` | def remaining_satang(self) -> int | 1 | active |
| `jarvis_v2.finance.planning.FinanceGoal.as_dict` | method | `src/jarvis_v2/finance/planning.py:38-46` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.planning.FinanceForecast` | class | `src/jarvis_v2/finance/planning.py:50-79` | class FinanceForecast() | 0 | active |
| `jarvis_v2.finance.planning.FinanceForecast.__post_init__` | method | `src/jarvis_v2/finance/planning.py:60-69` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.planning.FinanceForecast.as_dict` | method | `src/jarvis_v2/finance/planning.py:71-79` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.planning.FinancePlanningService` | class | `src/jarvis_v2/finance/planning.py:82-114` | class FinancePlanningService() | 1 | active |
| `jarvis_v2.finance.planning.FinancePlanningService.__init__` | method | `src/jarvis_v2/finance/planning.py:85-89` | def __init__(self, store: FinanceStore) | 5 | active |
| `jarvis_v2.finance.planning.FinancePlanningService.forecast` | method | `src/jarvis_v2/finance/planning.py:91-99` | def forecast(self, source_id: str, scope_id: str) -> FinanceForecast | 1 | active |
| `jarvis_v2.finance.planning.FinancePlanningService.goal_progress` | method | `src/jarvis_v2/finance/planning.py:102-114` | def goal_progress(goals: Iterable[FinanceGoal]) -> tuple[FinanceGoal, ...] | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationError` | class | `src/jarvis_v2/finance/reconciliation.py:23-24` | class FinanceReconciliationError(ValueError) | 1 | active |
| `jarvis_v2.finance.reconciliation._pick` | function | `src/jarvis_v2/finance/reconciliation.py:27-33` | def _pick(data: Mapping[str, object], label: str, *keys: str, default: object=_MISSING) -> object | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceOperation` | class | `src/jarvis_v2/finance/reconciliation.py:37-109` | class FinanceOperation() | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceOperation.__post_init__` | method | `src/jarvis_v2/finance/reconciliation.py:49-71` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceOperation.as_dict` | method | `src/jarvis_v2/finance/reconciliation.py:73-83` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.reconciliation.FinanceOperation.from_mapping` | method | `src/jarvis_v2/finance/reconciliation.py:86-99` | def from_mapping(cls, data: Mapping[str, object]) -> 'FinanceOperation' | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceOperation.effects` | method | `src/jarvis_v2/finance/reconciliation.py:101-109` | def effects(self) -> dict[str, int] | 2 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationResult` | class | `src/jarvis_v2/finance/reconciliation.py:113-139` | class FinanceReconciliationResult() | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationResult.total` | method | `src/jarvis_v2/finance/reconciliation.py:122-123` | def total(self) -> int | 6 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationResult.net_effect_satang` | method | `src/jarvis_v2/finance/reconciliation.py:126-127` | def net_effect_satang(self) -> int | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationResult.as_dict` | method | `src/jarvis_v2/finance/reconciliation.py:129-139` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore` | class | `src/jarvis_v2/finance/reconciliation.py:142-310` | class FinanceReconciliationStore() | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.__init__` | method | `src/jarvis_v2/finance/reconciliation.py:145-167` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.__enter__` | method | `src/jarvis_v2/finance/reconciliation.py:169-170` | def __enter__(self) -> 'FinanceReconciliationStore' | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.__exit__` | method | `src/jarvis_v2/finance/reconciliation.py:172-173` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.close` | method | `src/jarvis_v2/finance/reconciliation.py:175-177` | def close(self) -> None | 34 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.sync` | method | `src/jarvis_v2/finance/reconciliation.py:179-224` | def sync(self, source_id: str, scope_id: str, operations: Iterable[FinanceOperation \| Mapping[str, object]]=()) -> FinanceReconciliationResult | 13 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.operations` | method | `src/jarvis_v2/finance/reconciliation.py:228-242` | def operations(self, source_id: str, scope_id: str) -> tuple[FinanceOperation, ...] | 2 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.account_deltas` | method | `src/jarvis_v2/finance/reconciliation.py:244-249` | def account_deltas(self, source_id: str, scope_id: str) -> dict[str, int] | 1 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore.reconcile` | method | `src/jarvis_v2/finance/reconciliation.py:251-263` | def reconcile(self, source_id: str, scope_id: str, opening_balances: Mapping[str, int]) -> dict[str, int] | 4 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._coerce` | method | `src/jarvis_v2/finance/reconciliation.py:266-281` | def _coerce(values: Iterable[FinanceOperation \| Mapping[str, object]]) -> tuple[FinanceOperation, ...] | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._insert` | method | `src/jarvis_v2/finance/reconciliation.py:283-294` | def _insert(self, source_id: str, scope_id: str, operation: FinanceOperation, payload: str) -> None | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._update` | method | `src/jarvis_v2/finance/reconciliation.py:296-306` | def _update(self, source_id: str, scope_id: str, operation: FinanceOperation, payload: str) -> None | 0 | active |
| `jarvis_v2.finance.reconciliation.FinanceReconciliationStore._instant` | method | `src/jarvis_v2/finance/reconciliation.py:309-310` | def _instant(value: str) -> float | 0 | active |
| `jarvis_v2.finance.reports.FinanceReportError` | class | `src/jarvis_v2/finance/reports.py:11-12` | class FinanceReportError(FinanceIngestionError) | 1 | active |
| `jarvis_v2.finance.reports.FinanceReport` | class | `src/jarvis_v2/finance/reports.py:16-64` | class FinanceReport() | 0 | active |
| `jarvis_v2.finance.reports.FinanceReport.total_income_satang` | method | `src/jarvis_v2/finance/reports.py:32-33` | def total_income_satang(self) -> int | 0 | active |
| `jarvis_v2.finance.reports.FinanceReport.total_expense_satang` | method | `src/jarvis_v2/finance/reports.py:36-37` | def total_expense_satang(self) -> int | 0 | active |
| `jarvis_v2.finance.reports.FinanceReport.category_totals` | method | `src/jarvis_v2/finance/reports.py:40-41` | def category_totals(self) -> tuple[tuple[str, int], ...] | 2 | active |
| `jarvis_v2.finance.reports.FinanceReport.merchant_totals` | method | `src/jarvis_v2/finance/reports.py:44-45` | def merchant_totals(self) -> tuple[tuple[str, int], ...] | 2 | active |
| `jarvis_v2.finance.reports.FinanceReport.trend` | method | `src/jarvis_v2/finance/reports.py:48-49` | def trend(self) -> tuple[tuple[str, int], ...] | 1 | active |
| `jarvis_v2.finance.reports.FinanceReport.as_dict` | method | `src/jarvis_v2/finance/reports.py:51-64` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.finance.reports.FinanceReportService` | class | `src/jarvis_v2/finance/reports.py:67-144` | class FinanceReportService() | 0 | active |
| `jarvis_v2.finance.reports.FinanceReportService.__init__` | method | `src/jarvis_v2/finance/reports.py:70-73` | def __init__(self, store: FinanceStore) | 5 | active |
| `jarvis_v2.finance.reports.FinanceReportService.report` | method | `src/jarvis_v2/finance/reports.py:75-128` | def report(self, source_id: str, scope_id: str, *, start_date: str \| None=None, end_date: str \| None=None) -> FinanceReport | 14 | active |
| `jarvis_v2.finance.reports.FinanceReportService._valid_date` | method | `src/jarvis_v2/finance/reports.py:134-140` | def _valid_date(value: str \| None, label: str) -> str \| None | 0 | active |
| `jarvis_v2.finance.reports.FinanceReportService._instant` | method | `src/jarvis_v2/finance/reports.py:143-144` | def _instant(value: str) -> float | 0 | active |
| `jarvis_v2.guardian.controller.GuardianControllerError` | class | `src/jarvis_v2/guardian/controller.py:19-20` | class GuardianControllerError(ValueError) | 1 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager` | class | `src/jarvis_v2/guardian/controller.py:26-151` | class TrustedControllerManager() | 4 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager.__init__` | method | `src/jarvis_v2/guardian/controller.py:35-58` | def __init__(self, executable: str \| Path, expected_sha256: str, *, trusted_root: str \| Path, control_dir: str \| Path \| None=None, command: Sequence[str] \| None=None, runner:  | 5 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager.verify` | method | `src/jarvis_v2/guardian/controller.py:60-101` | def verify(self) -> dict[str, Any] | 4 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager.restart` | method | `src/jarvis_v2/guardian/controller.py:103-117` | def restart(self) -> dict[str, Any] | 6 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager._active_markers` | method | `src/jarvis_v2/guardian/controller.py:119-126` | def _active_markers(self) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager._validate_command` | method | `src/jarvis_v2/guardian/controller.py:128-136` | def _validate_command(self, command: tuple[str, ...]) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.controller.TrustedControllerManager._spawn` | method | `src/jarvis_v2/guardian/controller.py:139-151` | def _spawn(command: tuple[str, ...], cwd: Path) -> int | 0 | active |
| `jarvis_v2.guardian.controller._sha256` | function | `src/jarvis_v2/guardian/controller.py:154-159` | def _sha256(path: Path) -> str | 0 | active |
| `jarvis_v2.guardian.controller.main` | function | `src/jarvis_v2/guardian/controller.py:162-179` | def main(argv: Sequence[str] \| None=None) -> int | 155 | active |
| `jarvis_v2.guardian.cutover.CutoverError` | class | `src/jarvis_v2/guardian/cutover.py:19-20` | class CutoverError(ValueError) | 1 | active |
| `jarvis_v2.guardian.cutover.CutoverDecision` | class | `src/jarvis_v2/guardian/cutover.py:24-39` | class CutoverDecision() | 0 | active |
| `jarvis_v2.guardian.cutover.CutoverDecision.as_dict` | method | `src/jarvis_v2/guardian/cutover.py:36-39` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator` | class | `src/jarvis_v2/guardian/cutover.py:42-171` | class CutoverCoordinator() | 2 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.__init__` | method | `src/jarvis_v2/guardian/cutover.py:45-64` | def __init__(self, fence: WriterFence, *, component_schema: str, state_schema: str, expected_artifact_sha256: str, control_dir: str \| Path \| None=None) -> None | 5 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.prepare` | method | `src/jarvis_v2/guardian/cutover.py:66-107` | def prepare(self, readiness: Mapping[str, object], *, capacity_available: bool) -> CutoverDecision | 10 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.cutover` | method | `src/jarvis_v2/guardian/cutover.py:109-129` | def cutover(self, current: WriterLease, next_owner_id: str, readiness: Mapping[str, object], *, capacity_available: bool, ttl_seconds: int=60) -> dict[str, Any] | 3 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator.failback` | method | `src/jarvis_v2/guardian/cutover.py:131-166` | def failback(self, current: WriterLease, previous_owner_id: str, readiness: Mapping[str, object], *, capacity_available: bool, ttl_seconds: int=60) -> dict[str, Any] | 1 | active |
| `jarvis_v2.guardian.cutover.CutoverCoordinator._active_controls` | method | `src/jarvis_v2/guardian/cutover.py:168-171` | def _active_controls(self) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.cutover._value` | function | `src/jarvis_v2/guardian/cutover.py:174-177` | def _value(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.failure.FailureClassificationError` | class | `src/jarvis_v2/guardian/failure.py:16-17` | class FailureClassificationError(ValueError) | 1 | active |
| `jarvis_v2.guardian.failure.FailureAssessment` | class | `src/jarvis_v2/guardian/failure.py:21-42` | class FailureAssessment() | 0 | active |
| `jarvis_v2.guardian.failure.FailureAssessment.as_dict` | method | `src/jarvis_v2/guardian/failure.py:34-42` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.failure.FailureClassifier` | class | `src/jarvis_v2/guardian/failure.py:45-96` | class FailureClassifier() | 2 | active |
| `jarvis_v2.guardian.failure.FailureClassifier.classify` | method | `src/jarvis_v2/guardian/failure.py:48-96` | def classify(self, component_id: str, *, component: ProbeResult, dependencies: Mapping[str, ProbeResult \| bool] \| None=None, host: ProbeResult \| bool \| None=None, evidence_refs | 4 | active |
| `jarvis_v2.guardian.failure._identifier` | function | `src/jarvis_v2/guardian/failure.py:99-102` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.failure._observation` | function | `src/jarvis_v2/guardian/failure.py:105-112` | def _observation(value: ProbeResult \| bool \| None, *, allow_none: bool=False) -> ProbeResult \| None | 0 | active |
| `jarvis_v2.guardian.failure._dependencies` | function | `src/jarvis_v2/guardian/failure.py:115-123` | def _dependencies(values: Mapping[str, ProbeResult \| bool] \| None) -> tuple[tuple[str, ProbeResult], ...] | 0 | active |
| `jarvis_v2.guardian.failure._references` | function | `src/jarvis_v2/guardian/failure.py:126-139` | def _references(values: Iterable[str]) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.fencing.WriterFenceError` | class | `src/jarvis_v2/guardian/fencing.py:16-17` | class WriterFenceError(ValueError) | 2 | active |
| `jarvis_v2.guardian.fencing.WriterLease` | class | `src/jarvis_v2/guardian/fencing.py:21-30` | class WriterLease() | 0 | active |
| `jarvis_v2.guardian.fencing.WriterLease.as_dict` | method | `src/jarvis_v2/guardian/fencing.py:29-30` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.fencing.WriterFence` | class | `src/jarvis_v2/guardian/fencing.py:33-127` | class WriterFence() | 3 | active |
| `jarvis_v2.guardian.fencing.WriterFence.__init__` | method | `src/jarvis_v2/guardian/fencing.py:41-45` | def __init__(self, *, clock: Callable[[], float] \| None=None) -> None | 5 | active |
| `jarvis_v2.guardian.fencing.WriterFence.acquire` | method | `src/jarvis_v2/guardian/fencing.py:47-59` | def acquire(self, owner_id: str, *, ttl_seconds: int=60) -> WriterLease | 3 | active |
| `jarvis_v2.guardian.fencing.WriterFence.renew` | method | `src/jarvis_v2/guardian/fencing.py:61-70` | def renew(self, lease: WriterLease, *, ttl_seconds: int=60) -> WriterLease | 2 | active |
| `jarvis_v2.guardian.fencing.WriterFence.handoff` | method | `src/jarvis_v2/guardian/fencing.py:72-88` | def handoff(self, current: WriterLease, next_owner_id: str, *, ttl_seconds: int=60) -> WriterLease | 12 | active |
| `jarvis_v2.guardian.fencing.WriterFence.release` | method | `src/jarvis_v2/guardian/fencing.py:90-93` | def release(self, lease: WriterLease) -> None | 12 | active |
| `jarvis_v2.guardian.fencing.WriterFence.assert_current` | method | `src/jarvis_v2/guardian/fencing.py:95-98` | def assert_current(self, lease: WriterLease) -> None | 3 | active |
| `jarvis_v2.guardian.fencing.WriterFence.snapshot` | method | `src/jarvis_v2/guardian/fencing.py:100-109` | def snapshot(self) -> dict[str, Any] | 17 | active |
| `jarvis_v2.guardian.fencing.WriterFence._require` | method | `src/jarvis_v2/guardian/fencing.py:111-117` | def _require(self, lease: WriterLease) -> WriterLease | 0 | active |
| `jarvis_v2.guardian.fencing.WriterFence._expire` | method | `src/jarvis_v2/guardian/fencing.py:119-121` | def _expire(self, now: float) -> None | 0 | active |
| `jarvis_v2.guardian.fencing.WriterFence._now` | method | `src/jarvis_v2/guardian/fencing.py:123-127` | def _now(self) -> float | 0 | active |
| `jarvis_v2.guardian.fencing._identifier` | function | `src/jarvis_v2/guardian/fencing.py:130-133` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.fencing._ttl` | function | `src/jarvis_v2/guardian/fencing.py:136-139` | def _ttl(value: int) -> int | 0 | active |
| `jarvis_v2.guardian.health.GuardianHealthError` | class | `src/jarvis_v2/guardian/health.py:15-16` | class GuardianHealthError(ValueError) | 1 | active |
| `jarvis_v2.guardian.health.ProbeResult` | class | `src/jarvis_v2/guardian/health.py:20-41` | class ProbeResult() | 3 | active |
| `jarvis_v2.guardian.health.ProbeResult.__post_init__` | method | `src/jarvis_v2/guardian/health.py:27-38` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.guardian.health.ProbeResult.as_dict` | method | `src/jarvis_v2/guardian/health.py:40-41` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.guardian.health.HealthEvidence` | class | `src/jarvis_v2/guardian/health.py:45-67` | class HealthEvidence() | 0 | active |
| `jarvis_v2.guardian.health.HealthEvidence.as_dict` | method | `src/jarvis_v2/guardian/health.py:59-67` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator` | class | `src/jarvis_v2/guardian/health.py:70-186` | class GuardianHealthEvaluator() | 1 | active |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator.assess` | method | `src/jarvis_v2/guardian/health.py:73-182` | def assess(self, component_id: str, *, liveness: ProbeResult, readiness: ProbeResult, required_dependencies: Iterable[str]=(), dependencies: Mapping[str, ProbeResult \| bool] \| No | 1 | active |
| `jarvis_v2.guardian.health.GuardianHealthEvaluator._evidence` | method | `src/jarvis_v2/guardian/health.py:185-186` | def _evidence(component_id: str, **values: Any) -> HealthEvidence | 0 | active |
| `jarvis_v2.guardian.health._valid_identifier` | function | `src/jarvis_v2/guardian/health.py:189-190` | def _valid_identifier(value: str) -> bool | 0 | active |
| `jarvis_v2.guardian.health._identifier` | function | `src/jarvis_v2/guardian/health.py:193-196` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.health._identifiers` | function | `src/jarvis_v2/guardian/health.py:199-212` | def _identifiers(values: Iterable[str], label: str) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.health._dependency_result` | function | `src/jarvis_v2/guardian/health.py:215-220` | def _dependency_result(value: ProbeResult \| bool) -> ProbeResult | 0 | active |
| `jarvis_v2.guardian.incidents.IncidentTrackerError` | class | `src/jarvis_v2/guardian/incidents.py:18-19` | class IncidentTrackerError(ValueError) | 1 | active |
| `jarvis_v2.guardian.incidents.IncidentRecord` | class | `src/jarvis_v2/guardian/incidents.py:23-38` | class IncidentRecord() | 0 | active |
| `jarvis_v2.guardian.incidents.IncidentRecord.as_dict` | method | `src/jarvis_v2/guardian/incidents.py:35-38` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.incidents.IncidentNotice` | class | `src/jarvis_v2/guardian/incidents.py:42-54` | class IncidentNotice() | 0 | active |
| `jarvis_v2.guardian.incidents.IncidentNotice.as_dict` | method | `src/jarvis_v2/guardian/incidents.py:49-54` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.incidents.IncidentTracker` | class | `src/jarvis_v2/guardian/incidents.py:57-143` | class IncidentTracker() | 1 | active |
| `jarvis_v2.guardian.incidents.IncidentTracker.__init__` | method | `src/jarvis_v2/guardian/incidents.py:60-75` | def __init__(self, *, max_incidents: int=MAX_INCIDENTS, max_alerts_per_incident: int=3) -> None | 5 | active |
| `jarvis_v2.guardian.incidents.IncidentTracker.records` | method | `src/jarvis_v2/guardian/incidents.py:78-80` | def records(self) -> tuple[IncidentRecord, ...] | 6 | active |
| `jarvis_v2.guardian.incidents.IncidentTracker.record` | method | `src/jarvis_v2/guardian/incidents.py:82-123` | def record(self, assessment: FailureAssessment) -> IncidentNotice | 15 | active |
| `jarvis_v2.guardian.incidents.IncidentTracker.acknowledge` | method | `src/jarvis_v2/guardian/incidents.py:125-143` | def acknowledge(self, fingerprint: str) -> IncidentRecord | 4 | active |
| `jarvis_v2.guardian.incidents._fingerprint` | function | `src/jarvis_v2/guardian/incidents.py:146-154` | def _fingerprint(assessment: FailureAssessment) -> str | 0 | active |
| `jarvis_v2.guardian.integrity.IntegrityScanError` | class | `src/jarvis_v2/guardian/integrity.py:16-17` | class IntegrityScanError(ValueError) | 1 | active |
| `jarvis_v2.guardian.integrity.IntegrityReport` | class | `src/jarvis_v2/guardian/integrity.py:21-39` | class IntegrityReport() | 0 | active |
| `jarvis_v2.guardian.integrity.IntegrityReport.as_dict` | method | `src/jarvis_v2/guardian/integrity.py:33-39` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.integrity.IntegrityScanner` | class | `src/jarvis_v2/guardian/integrity.py:42-96` | class IntegrityScanner() | 1 | active |
| `jarvis_v2.guardian.integrity.IntegrityScanner.__init__` | method | `src/jarvis_v2/guardian/integrity.py:49-60` | def __init__(self, expected_version: str \| int, *, expected_schemas: Mapping[str, str \| int], required_queues: Iterable[str], expected_hashes: Mapping[str, str] \| None=None) ->  | 5 | active |
| `jarvis_v2.guardian.integrity.IntegrityScanner.scan` | method | `src/jarvis_v2/guardian/integrity.py:62-96` | def scan(self, *, version: str \| int, schemas: Mapping[str, str \| int], queues: Mapping[str, int], hashes: Mapping[str, str]) -> IntegrityReport | 2 | active |
| `jarvis_v2.guardian.integrity._version` | function | `src/jarvis_v2/guardian/integrity.py:99-106` | def _version(value: str \| int, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.integrity._identifiers` | function | `src/jarvis_v2/guardian/integrity.py:109-120` | def _identifiers(values: Iterable[str], label: str) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.integrity._versions` | function | `src/jarvis_v2/guardian/integrity.py:123-130` | def _versions(values: Mapping[str, str \| int], label: str) -> dict[str, str] | 0 | active |
| `jarvis_v2.guardian.integrity._queues` | function | `src/jarvis_v2/guardian/integrity.py:133-142` | def _queues(values: Mapping[str, int]) -> dict[str, int] | 0 | active |
| `jarvis_v2.guardian.integrity._hashes` | function | `src/jarvis_v2/guardian/integrity.py:145-154` | def _hashes(values: Mapping[str, str], label: str) -> dict[str, str] | 0 | active |
| `jarvis_v2.guardian.integrity._mapping_findings` | function | `src/jarvis_v2/guardian/integrity.py:157-170` | def _mapping_findings(kind: str, expected: Mapping[str, str], observed: Mapping[str, str]) -> list[str] | 0 | active |
| `jarvis_v2.guardian.integrity._hash_findings` | function | `src/jarvis_v2/guardian/integrity.py:173-182` | def _hash_findings(expected: Mapping[str, str], observed: Mapping[str, str]) -> list[str] | 0 | active |
| `jarvis_v2.guardian.isolation.IsolationError` | class | `src/jarvis_v2/guardian/isolation.py:19-20` | class IsolationError(ValueError) | 2 | active |
| `jarvis_v2.guardian.isolation.EffectRecord` | class | `src/jarvis_v2/guardian/isolation.py:24-32` | class EffectRecord() | 0 | active |
| `jarvis_v2.guardian.isolation.EffectRecord.as_dict` | method | `src/jarvis_v2/guardian/isolation.py:31-32` | def as_dict(self) -> dict[str, str] | 18 | active |
| `jarvis_v2.guardian.isolation.IsolationSnapshot` | class | `src/jarvis_v2/guardian/isolation.py:36-73` | class IsolationSnapshot() | 0 | active |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.in_flight` | method | `src/jarvis_v2/guardian/isolation.py:46-49` | def in_flight(self) -> tuple[str, ...] | 1 | active |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.unresolved` | method | `src/jarvis_v2/guardian/isolation.py:52-57` | def unresolved(self) -> tuple[str, ...] | 1 | active |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.accepts_effects` | method | `src/jarvis_v2/guardian/isolation.py:60-61` | def accepts_effects(self) -> bool | 0 | active |
| `jarvis_v2.guardian.isolation.IsolationSnapshot.as_dict` | method | `src/jarvis_v2/guardian/isolation.py:63-73` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.isolation._ComponentState` | class | `src/jarvis_v2/guardian/isolation.py:77-85` | class _ComponentState() | 0 | active |
| `jarvis_v2.guardian.isolation._ComponentState.__post_init__` | method | `src/jarvis_v2/guardian/isolation.py:83-85` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.guardian.isolation.IsolationController` | class | `src/jarvis_v2/guardian/isolation.py:88-298` | class IsolationController() | 2 | active |
| `jarvis_v2.guardian.isolation.IsolationController.__init__` | method | `src/jarvis_v2/guardian/isolation.py:96-107` | def __init__(self, component_ids: Iterable[str]=()) -> None | 5 | active |
| `jarvis_v2.guardian.isolation.IsolationController.register` | method | `src/jarvis_v2/guardian/isolation.py:109-118` | def register(self, component_id: str) -> IsolationSnapshot | 1 | active |
| `jarvis_v2.guardian.isolation.IsolationController.snapshot` | method | `src/jarvis_v2/guardian/isolation.py:120-129` | def snapshot(self, component_id: str) -> IsolationSnapshot | 17 | active |
| `jarvis_v2.guardian.isolation.IsolationController.can_accept_effect` | method | `src/jarvis_v2/guardian/isolation.py:131-132` | def can_accept_effect(self, component_id: str) -> bool | 1 | active |
| `jarvis_v2.guardian.isolation.IsolationController.begin_effect` | method | `src/jarvis_v2/guardian/isolation.py:134-146` | def begin_effect(self, component_id: str, effect_id: str) -> IsolationSnapshot | 2 | active |
| `jarvis_v2.guardian.isolation.IsolationController.complete_effect` | method | `src/jarvis_v2/guardian/isolation.py:150-166` | def complete_effect(self, component_id: str, effect_id: str, *, status: str='completed', evidence_ref: str='', generation: int \| None=None) -> IsolationSnapshot | 2 | active |
| `jarvis_v2.guardian.isolation.IsolationController.reconcile_effect` | method | `src/jarvis_v2/guardian/isolation.py:170-196` | def reconcile_effect(self, component_id: str, effect_id: str, *, status: str, evidence_ref: str='', generation: int \| None=None) -> IsolationSnapshot | 1 | active |
| `jarvis_v2.guardian.isolation.IsolationController.reconcile` | method | `src/jarvis_v2/guardian/isolation.py:198-224` | def reconcile(self, component_id: str, observations: Mapping[str, str], *, generation: int \| None=None) -> IsolationSnapshot | 4 | active |
| `jarvis_v2.guardian.isolation.IsolationController.drain` | method | `src/jarvis_v2/guardian/isolation.py:226-235` | def drain(self, component_id: str) -> IsolationSnapshot | 4 | active |
| `jarvis_v2.guardian.isolation.IsolationController.quiesce` | method | `src/jarvis_v2/guardian/isolation.py:239-252` | def quiesce(self, component_id: str) -> IsolationSnapshot | 2 | active |
| `jarvis_v2.guardian.isolation.IsolationController.isolate` | method | `src/jarvis_v2/guardian/isolation.py:254-270` | def isolate(self, component_id: str, *, reason: str) -> IsolationSnapshot | 2 | active |
| `jarvis_v2.guardian.isolation.IsolationController.resume` | method | `src/jarvis_v2/guardian/isolation.py:272-287` | def resume(self, component_id: str) -> IsolationSnapshot | 3 | active |
| `jarvis_v2.guardian.isolation.IsolationController._component` | method | `src/jarvis_v2/guardian/isolation.py:289-293` | def _component(self, component_id: str) -> _ComponentState | 0 | active |
| `jarvis_v2.guardian.isolation.IsolationController._check_generation` | method | `src/jarvis_v2/guardian/isolation.py:296-298` | def _check_generation(state: _ComponentState, generation: int \| None) -> None | 0 | active |
| `jarvis_v2.guardian.isolation._identifier` | function | `src/jarvis_v2/guardian/isolation.py:301-304` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.isolation._reason` | function | `src/jarvis_v2/guardian/isolation.py:307-315` | def _reason(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.isolation._evidence_ref` | function | `src/jarvis_v2/guardian/isolation.py:318-321` | def _evidence_ref(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.isolation._effect_status` | function | `src/jarvis_v2/guardian/isolation.py:324-327` | def _effect_status(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.model.GuardianModelError` | class | `src/jarvis_v2/guardian/model.py:15-16` | class GuardianModelError(ValueError) | 1 | active |
| `jarvis_v2.guardian.model.GuardianModelHealth` | class | `src/jarvis_v2/guardian/model.py:20-31` | class GuardianModelHealth() | 0 | active |
| `jarvis_v2.guardian.model.GuardianModelHealth.as_dict` | method | `src/jarvis_v2/guardian/model.py:30-31` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.guardian.model._model` | function | `src/jarvis_v2/guardian/model.py:34-37` | def _model(value: str) -> str | 1 | active |
| `jarvis_v2.guardian.model.LocalGuardianModel` | class | `src/jarvis_v2/guardian/model.py:40-87` | class LocalGuardianModel() | 1 | active |
| `jarvis_v2.guardian.model.LocalGuardianModel.__init__` | method | `src/jarvis_v2/guardian/model.py:43-54` | def __init__(self, model: str=DEFAULT_MODEL, *, runner: Callable[[list[str], int], int] \| None=None, timeout_seconds: int=PROBE_TIMEOUT_SECONDS) -> None | 5 | active |
| `jarvis_v2.guardian.model.LocalGuardianModel.probe` | method | `src/jarvis_v2/guardian/model.py:56-64` | def probe(self, *, verify_inference: bool=True) -> GuardianModelHealth | 6 | active |
| `jarvis_v2.guardian.model.LocalGuardianModel._health` | method | `src/jarvis_v2/guardian/model.py:66-74` | def _health(self, available: bool, inference_verified: bool, reason: str) -> GuardianModelHealth | 0 | active |
| `jarvis_v2.guardian.model.LocalGuardianModel._run` | method | `src/jarvis_v2/guardian/model.py:76-87` | def _run(self, command: list[str], timeout_seconds: int) -> int | 1 | active |
| `jarvis_v2.guardian.priority.SlotPriority` | class | `src/jarvis_v2/guardian/priority.py:7-133` | class SlotPriority() | 2 | active |
| `jarvis_v2.guardian.priority.SlotPriority.__init__` | method | `src/jarvis_v2/guardian/priority.py:17-27` | def __init__(self, slots: Iterable[str]=('default',)) -> None | 5 | active |
| `jarvis_v2.guardian.priority.SlotPriority.slots` | method | `src/jarvis_v2/guardian/priority.py:30-31` | def slots(self) -> tuple[str, ...] | 4 | active |
| `jarvis_v2.guardian.priority.SlotPriority.held_slots` | method | `src/jarvis_v2/guardian/priority.py:34-36` | def held_slots(self) -> dict[str, str] | 3 | active |
| `jarvis_v2.guardian.priority.SlotPriority.available_slots` | method | `src/jarvis_v2/guardian/priority.py:39-40` | def available_slots(self) -> tuple[str, ...] | 2 | active |
| `jarvis_v2.guardian.priority.SlotPriority.guardian_request` | method | `src/jarvis_v2/guardian/priority.py:42-54` | def guardian_request(self, compatible_slots: Iterable[str] \| None=None) -> None | 4 | active |
| `jarvis_v2.guardian.priority.SlotPriority.claim` | method | `src/jarvis_v2/guardian/priority.py:56-93` | def claim(self, name: str, compatible_slots: Iterable[str] \| None=None) -> str \| None | 21 | active |
| `jarvis_v2.guardian.priority.SlotPriority.start` | method | `src/jarvis_v2/guardian/priority.py:95-97` | def start(self, name: str, compatible_slots: Iterable[str] \| None=None) -> bool | 10 | active |
| `jarvis_v2.guardian.priority.SlotPriority.finish` | method | `src/jarvis_v2/guardian/priority.py:99-113` | def finish(self, name: str, slot: str \| None=None) -> None | 12 | active |
| `jarvis_v2.guardian.priority.SlotPriority._normalize_slots` | method | `src/jarvis_v2/guardian/priority.py:115-129` | def _normalize_slots(self, slots: Iterable[str] \| None) -> frozenset[str] \| None | 0 | active |
| `jarvis_v2.guardian.priority.SlotPriority._sync_compatibility_state` | method | `src/jarvis_v2/guardian/priority.py:131-133` | def _sync_compatibility_state(self) -> None | 0 | active |
| `jarvis_v2.guardian.recovery.RecoveryError` | class | `src/jarvis_v2/guardian/recovery.py:14-15` | class RecoveryError(ValueError) | 1 | active |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController` | class | `src/jarvis_v2/guardian/recovery.py:18-108` | class GuardianRecoveryController() | 3 | active |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController.__init__` | method | `src/jarvis_v2/guardian/recovery.py:21-34` | def __init__(self, manager: TrustedControllerManager, budget: RestartBudget, *, control_dir: str \| Path \| None=None) -> None | 5 | active |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController.boot` | method | `src/jarvis_v2/guardian/recovery.py:36-93` | def boot(self, *, reason: str, evidence_ref: str='', approval_required: bool=False) -> dict[str, Any] | 3 | active |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController._controls` | method | `src/jarvis_v2/guardian/recovery.py:95-98` | def _controls(self) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.guardian.recovery.GuardianRecoveryController._safe_mode` | method | `src/jarvis_v2/guardian/recovery.py:101-108` | def _safe_mode(reason: str, controls: tuple[str, ...], approval: bool) -> dict[str, Any] | 0 | active |
| `jarvis_v2.guardian.release.inspect` | function | `src/jarvis_v2/guardian/release.py:13-38` | def inspect(path: Path) -> dict | 10 | active |
| `jarvis_v2.guardian.release.inspect_canary` | function | `src/jarvis_v2/guardian/release.py:41-89` | def inspect_canary(path: Path) -> dict | 2 | active |
| `jarvis_v2.guardian.restart.RestartBudgetError` | class | `src/jarvis_v2/guardian/restart.py:19-20` | class RestartBudgetError(ValueError) | 1 | active |
| `jarvis_v2.guardian.restart.RestartAttempt` | class | `src/jarvis_v2/guardian/restart.py:24-36` | class RestartAttempt() | 0 | active |
| `jarvis_v2.guardian.restart.RestartAttempt.as_dict` | method | `src/jarvis_v2/guardian/restart.py:35-36` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.restart.RestartDecision` | class | `src/jarvis_v2/guardian/restart.py:40-54` | class RestartDecision() | 0 | active |
| `jarvis_v2.guardian.restart.RestartDecision.as_dict` | method | `src/jarvis_v2/guardian/restart.py:53-54` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.restart.RestartBudget` | class | `src/jarvis_v2/guardian/restart.py:57-276` | class RestartBudget() | 4 | active |
| `jarvis_v2.guardian.restart.RestartBudget.__init__` | method | `src/jarvis_v2/guardian/restart.py:66-94` | def __init__(self, component_id: str, *, enabled: bool=True, max_attempts: int=3, cooldown_seconds: int=30, clock: Callable[[], float] \| None=None) -> None | 5 | active |
| `jarvis_v2.guardian.restart.RestartBudget.generation` | method | `src/jarvis_v2/guardian/restart.py:97-98` | def generation(self) -> int | 8 | active |
| `jarvis_v2.guardian.restart.RestartBudget.history` | method | `src/jarvis_v2/guardian/restart.py:101-102` | def history(self) -> tuple[RestartAttempt, ...] | 12 | active |
| `jarvis_v2.guardian.restart.RestartBudget.snapshot` | method | `src/jarvis_v2/guardian/restart.py:104-118` | def snapshot(self, *, now: float \| None=None) -> RestartDecision | 17 | active |
| `jarvis_v2.guardian.restart.RestartBudget.request` | method | `src/jarvis_v2/guardian/restart.py:120-151` | def request(self, *, reason: str, evidence_ref: str='', now: float \| None=None) -> RestartDecision | 23 | active |
| `jarvis_v2.guardian.restart.RestartBudget.record_outcome` | method | `src/jarvis_v2/guardian/restart.py:155-185` | def record_outcome(self, attempt: int, outcome: str, *, evidence_ref: str='', now: float \| None=None) -> RestartDecision | 1 | active |
| `jarvis_v2.guardian.restart.RestartBudget.resolve_unknown` | method | `src/jarvis_v2/guardian/restart.py:187-218` | def resolve_unknown(self, attempt: int, outcome: str, *, evidence_ref: str, now: float \| None=None) -> RestartDecision | 1 | active |
| `jarvis_v2.guardian.restart.RestartBudget.new_generation` | method | `src/jarvis_v2/guardian/restart.py:220-230` | def new_generation(self) -> RestartDecision | 1 | active |
| `jarvis_v2.guardian.restart.RestartBudget._state` | method | `src/jarvis_v2/guardian/restart.py:232-245` | def _state(self, now: float) -> tuple[str, str] | 0 | active |
| `jarvis_v2.guardian.restart.RestartBudget._decision` | method | `src/jarvis_v2/guardian/restart.py:247-258` | def _decision(self, state: str, reason: str, *, allowed: bool) -> RestartDecision | 0 | active |
| `jarvis_v2.guardian.restart.RestartBudget._history_index` | method | `src/jarvis_v2/guardian/restart.py:260-265` | def _history_index(self, attempt: int) -> int | 0 | active |
| `jarvis_v2.guardian.restart.RestartBudget._append` | method | `src/jarvis_v2/guardian/restart.py:267-268` | def _append(self, record: RestartAttempt) -> None | 0 | active |
| `jarvis_v2.guardian.restart.RestartBudget._now` | method | `src/jarvis_v2/guardian/restart.py:270-276` | def _now(self, value: float \| None) -> float | 0 | active |
| `jarvis_v2.guardian.restart._identifier` | function | `src/jarvis_v2/guardian/restart.py:282-285` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.restart._reason` | function | `src/jarvis_v2/guardian/restart.py:288-296` | def _reason(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.restart._evidence_ref` | function | `src/jarvis_v2/guardian/restart.py:299-302` | def _evidence_ref(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.rollback.RollbackError` | class | `src/jarvis_v2/guardian/rollback.py:24-25` | class RollbackError(ValueError) | 1 | active |
| `jarvis_v2.guardian.rollback.RollbackPlan` | class | `src/jarvis_v2/guardian/rollback.py:29-46` | class RollbackPlan() | 0 | active |
| `jarvis_v2.guardian.rollback.RollbackPlan.as_dict` | method | `src/jarvis_v2/guardian/rollback.py:43-46` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.guardian.rollback.select_last_known_good` | function | `src/jarvis_v2/guardian/rollback.py:49-118` | def select_last_known_good(manifest_path: str \| Path, *, canary_status: str) -> RollbackPlan | 3 | active |
| `jarvis_v2.guardian.rollback.restore_last_known_good` | function | `src/jarvis_v2/guardian/rollback.py:121-169` | def restore_last_known_good(plan: RollbackPlan) -> dict[str, Any] | 3 | active |
| `jarvis_v2.guardian.rollback._status` | function | `src/jarvis_v2/guardian/rollback.py:172-175` | def _status(value: str) -> str | 0 | active |
| `jarvis_v2.guardian.rollback._relative` | function | `src/jarvis_v2/guardian/rollback.py:178-184` | def _relative(value: Any, label: str) -> str | 0 | active |
| `jarvis_v2.guardian.rollback._safe_file` | function | `src/jarvis_v2/guardian/rollback.py:187-198` | def _safe_file(root: Path, relative: str, label: str) -> Path | 0 | active |
| `jarvis_v2.guardian.rollback._regular` | function | `src/jarvis_v2/guardian/rollback.py:201-204` | def _regular(path: Path, label: str) -> Path | 0 | active |
| `jarvis_v2.guardian.rollback._root` | function | `src/jarvis_v2/guardian/rollback.py:207-210` | def _root(path: Path) -> Path | 0 | active |
| `jarvis_v2.guardian.rollback._digest` | function | `src/jarvis_v2/guardian/rollback.py:213-218` | def _digest(path: Path) -> str | 0 | active |
| `jarvis_v2.guardian.rollback._checkpoint_digest` | function | `src/jarvis_v2/guardian/rollback.py:221-225` | def _checkpoint_digest(root: Path, plan: RollbackPlan) -> str \| None | 0 | active |
| `jarvis_v2.guardian.rollback._fsync_directory` | function | `src/jarvis_v2/guardian/rollback.py:228-233` | def _fsync_directory(directory: Path) -> None | 0 | active |
| `jarvis_v2.guardian.standby.StandbyError` | class | `src/jarvis_v2/guardian/standby.py:16-17` | class StandbyError(ValueError) | 1 | active |
| `jarvis_v2.guardian.standby.StandbyLauncher` | class | `src/jarvis_v2/guardian/standby.py:20-111` | class StandbyLauncher() | 1 | active |
| `jarvis_v2.guardian.standby.StandbyLauncher.__init__` | method | `src/jarvis_v2/guardian/standby.py:27-50` | def __init__(self, executable: str \| Path, expected_sha256: str, *, trusted_root: str \| Path, component_schema: str, state_schema: str, control_dir: str \| Path \| None=None, com | 5 | active |
| `jarvis_v2.guardian.standby.StandbyLauncher.inspect` | method | `src/jarvis_v2/guardian/standby.py:52-85` | def inspect(self, *, component_schema: str, state_schema: str, capacity_available: bool) -> dict[str, Any] | 10 | active |
| `jarvis_v2.guardian.standby.StandbyLauncher.start` | method | `src/jarvis_v2/guardian/standby.py:87-111` | def start(self, *, component_schema: str, state_schema: str, capacity_available: bool) -> dict[str, Any] | 10 | active |
| `jarvis_v2.guardian.standby._value` | function | `src/jarvis_v2/guardian/standby.py:114-117` | def _value(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.health.HealthError` | class | `src/jarvis_v2/health.py:13-14` | class HealthError(RuntimeError) | 1 | active |
| `jarvis_v2.health._systemd_state` | function | `src/jarvis_v2/health.py:17-26` | def _systemd_state(unit: str) -> str | 1 | active |
| `jarvis_v2.health._git_head` | function | `src/jarvis_v2/health.py:29-39` | def _git_head(repository: Path) -> str | 0 | active |
| `jarvis_v2.health._root_blockers` | function | `src/jarvis_v2/health.py:42-70` | def _root_blockers(rows: list[sqlite3.Row]) -> list[dict[str, Any]] | 0 | active |
| `jarvis_v2.health._native_health` | function | `src/jarvis_v2/health.py:73-137` | def _native_health(*, state_dir: Path, repository: Path) -> dict[str, Any] | 0 | active |
| `jarvis_v2.health.collect_health` | function | `src/jarvis_v2/health.py:140-224` | def collect_health(*, state_dir: Path, repository: Path) -> dict[str, Any] | 1 | active |
| `jarvis_v2.monitor._safe` | function | `src/jarvis_v2/monitor.py:35-43` | def _safe(value: Any, maxlen: int=100) -> str | 1 | active |
| `jarvis_v2.monitor._connect` | function | `src/jarvis_v2/monitor.py:46-55` | def _connect(db_path: Path) -> sqlite3.Connection | 0 | active |
| `jarvis_v2.monitor._columns` | function | `src/jarvis_v2/monitor.py:58-61` | def _columns(db: sqlite3.Connection, table: str) -> set[str] | 0 | active |
| `jarvis_v2.monitor._detect` | function | `src/jarvis_v2/monitor.py:64-70` | def _detect(db: sqlite3.Connection) -> str | 0 | active |
| `jarvis_v2.monitor._parse_time` | function | `src/jarvis_v2/monitor.py:73-82` | def _parse_time(value: str \| None) -> str | 0 | active |
| `jarvis_v2.monitor._age` | function | `src/jarvis_v2/monitor.py:85-101` | def _age(value: str \| None) -> str | 0 | active |
| `jarvis_v2.monitor._fetch_astra` | function | `src/jarvis_v2/monitor.py:104-178` | def _fetch_astra(db: sqlite3.Connection, limit: int, event_limit: int, show_objectives: bool) -> dict | 0 | active |
| `jarvis_v2.monitor._fetch_atlas` | function | `src/jarvis_v2/monitor.py:181-205` | def _fetch_atlas(db: sqlite3.Connection, limit: int, event_limit: int, show_objectives: bool) -> dict | 0 | active |
| `jarvis_v2.monitor.snapshot` | function | `src/jarvis_v2/monitor.py:208-225` | def snapshot(db_path: Path, *, source: str='auto', limit: int=10, event_limit: int=8, show_objectives: bool=False) -> dict | 17 | active |
| `jarvis_v2.monitor._line` | function | `src/jarvis_v2/monitor.py:228-229` | def _line(label: str, value: Any) -> str | 0 | active |
| `jarvis_v2.monitor._task_line` | function | `src/jarvis_v2/monitor.py:232-240` | def _task_line(t: dict, *, active: bool=False) -> str | 0 | active |
| `jarvis_v2.monitor.render` | function | `src/jarvis_v2/monitor.py:243-309` | def render(data: dict, *, ansi: bool=False, title: str='ATLAS Monitor') -> str | 3 | active |
| `jarvis_v2.monitor._choose_db` | function | `src/jarvis_v2/monitor.py:312-325` | def _choose_db(source: str, given: Path \| None) -> Path | 0 | active |
| `jarvis_v2.monitor.main` | function | `src/jarvis_v2/monitor.py:328-365` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `jarvis_v2.monitor_supervision._safe` | function | `src/jarvis_v2/monitor_supervision.py:44-46` | def _safe(value: Any, size: int=64) -> str | 1 | active |
| `jarvis_v2.monitor_supervision._cols` | function | `src/jarvis_v2/monitor_supervision.py:49-60` | def _cols(db: sqlite3.Connection, name: str) -> set[str] | 0 | active |
| `jarvis_v2.monitor_supervision._group` | function | `src/jarvis_v2/monitor_supervision.py:63-69` | def _group(db: sqlite3.Connection, table: str, column: str, where: str='', params: tuple=()) -> dict[str, int] | 0 | active |
| `jarvis_v2.monitor_supervision.safe_failure_code` | function | `src/jarvis_v2/monitor_supervision.py:72-77` | def safe_failure_code(value: Any, size: int=64) -> str | 0 | active |
| `jarvis_v2.monitor_supervision._sha` | function | `src/jarvis_v2/monitor_supervision.py:80-82` | def _sha(value: Any) -> str | 0 | active |
| `jarvis_v2.monitor_supervision._digest` | function | `src/jarvis_v2/monitor_supervision.py:85-87` | def _digest(value: Any) -> str | 0 | active |
| `jarvis_v2.monitor_supervision.collect` | function | `src/jarvis_v2/monitor_supervision.py:90-244` | def collect(db: sqlite3.Connection, limit: int=10) -> dict | 0 | active |
| `jarvis_v2.monitor_supervision.render_lines` | function | `src/jarvis_v2/monitor_supervision.py:247-331` | def render_lines(data: dict) -> list[str] | 0 | active |
| `jarvis_v2.native_controller.NativeControllerError` | class | `src/jarvis_v2/native_controller.py:29-30` | class NativeControllerError(RuntimeError) | 1 | active |
| `jarvis_v2.native_controller._absolute` | function | `src/jarvis_v2/native_controller.py:36-40` | def _absolute(value: str \| Path, label: str) -> Path | 0 | active |
| `jarvis_v2.native_controller._child` | function | `src/jarvis_v2/native_controller.py:43-49` | def _child(root: Path, value: str \| Path, label: str) -> Path | 0 | active |
| `jarvis_v2.native_controller._directory` | function | `src/jarvis_v2/native_controller.py:52-59` | def _directory(path: Path, label: str) -> Path | 0 | active |
| `jarvis_v2.native_controller._receipt` | function | `src/jarvis_v2/native_controller.py:62-72` | def _receipt(task_id: str, value: Mapping[str, Any]) -> str | 0 | active |
| `jarvis_v2.native_controller.NativeController` | class | `src/jarvis_v2/native_controller.py:75-216` | class NativeController() | 1 | active |
| `jarvis_v2.native_controller.NativeController.__init__` | method | `src/jarvis_v2/native_controller.py:78-117` | def __init__(self, state_dir: str \| Path, *, queue_path: str \| Path \| None=None, control_dir: str \| Path \| None=None, owner_id: str='archon-native', executor: Executor \| None | 5 | active |
| `jarvis_v2.native_controller.NativeController._acquire_lock` | method | `src/jarvis_v2/native_controller.py:119-136` | def _acquire_lock(self) | 0 | active |
| `jarvis_v2.native_controller.NativeController._release_lock` | method | `src/jarvis_v2/native_controller.py:138-149` | def _release_lock(self) -> None | 0 | active |
| `jarvis_v2.native_controller.NativeController.active_controls` | method | `src/jarvis_v2/native_controller.py:151-152` | def active_controls(self) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.native_controller.NativeController.snapshot` | method | `src/jarvis_v2/native_controller.py:154-164` | def snapshot(self) -> dict[str, Any] | 17 | active |
| `jarvis_v2.native_controller.NativeController.run_once` | method | `src/jarvis_v2/native_controller.py:166-198` | def run_once(self) -> dict[str, Any] | 1 | active |
| `jarvis_v2.native_controller.NativeController.run_forever` | method | `src/jarvis_v2/native_controller.py:200-203` | def run_forever(self, stop: Any) -> None | 0 | active |
| `jarvis_v2.native_controller.NativeController.close` | method | `src/jarvis_v2/native_controller.py:205-210` | def close(self) -> None | 34 | active |
| `jarvis_v2.native_controller.NativeController.__enter__` | method | `src/jarvis_v2/native_controller.py:212-213` | def __enter__(self) -> 'NativeController' | 1 | active |
| `jarvis_v2.native_controller.NativeController.__exit__` | method | `src/jarvis_v2/native_controller.py:215-216` | def __exit__(self, *_: object) -> None | 1 | active |
| `jarvis_v2.native_controller._default_state` | function | `src/jarvis_v2/native_controller.py:219-220` | def _default_state() -> Path | 0 | active |
| `jarvis_v2.native_controller.main` | function | `src/jarvis_v2/native_controller.py:223-253` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `jarvis_v2.research.analysis.MediaAnalysisError` | class | `src/jarvis_v2/research/analysis.py:20-21` | class MediaAnalysisError(ValueError) | 0 | active |
| `jarvis_v2.research.analysis._text` | function | `src/jarvis_v2/research/analysis.py:24-32` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.analysis._timestamp` | function | `src/jarvis_v2/research/analysis.py:35-39` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisEvidence` | class | `src/jarvis_v2/research/analysis.py:43-88` | class MediaAnalysisEvidence() | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisEvidence.__post_init__` | method | `src/jarvis_v2/research/analysis.py:56-73` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisEvidence.as_dict` | method | `src/jarvis_v2/research/analysis.py:75-88` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.analysis.MediaAnalysisResult` | class | `src/jarvis_v2/research/analysis.py:92-101` | class MediaAnalysisResult() | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisResult.__post_init__` | method | `src/jarvis_v2/research/analysis.py:96-98` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisResult.as_dict` | method | `src/jarvis_v2/research/analysis.py:100-101` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore` | class | `src/jarvis_v2/research/analysis.py:104-186` | class MediaAnalysisStore() | 1 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.__init__` | method | `src/jarvis_v2/research/analysis.py:107-127` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.__enter__` | method | `src/jarvis_v2/research/analysis.py:129-130` | def __enter__(self) -> 'MediaAnalysisStore' | 1 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.__exit__` | method | `src/jarvis_v2/research/analysis.py:132-133` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.save` | method | `src/jarvis_v2/research/analysis.py:135-147` | def save(self, evidence: MediaAnalysisEvidence) -> None | 5 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.latest` | method | `src/jarvis_v2/research/analysis.py:149-164` | def latest(self, media_id: str) -> MediaAnalysisEvidence \| None | 10 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore._evidence` | method | `src/jarvis_v2/research/analysis.py:167-182` | def _evidence(data: Mapping[str, object]) -> MediaAnalysisEvidence | 0 | active |
| `jarvis_v2.research.analysis.MediaAnalysisStore.close` | method | `src/jarvis_v2/research/analysis.py:184-186` | def close(self) -> None | 34 | active |
| `jarvis_v2.research.analysis.MediaAnalysisService` | class | `src/jarvis_v2/research/analysis.py:192-243` | class MediaAnalysisService() | 1 | active |
| `jarvis_v2.research.analysis.MediaAnalysisService.__init__` | method | `src/jarvis_v2/research/analysis.py:195-200` | def __init__(self, store: MediaAnalysisStore, *, analyzer: Analyzer \| None=None, clock: Callable[[], datetime] \| None=None) | 5 | active |
| `jarvis_v2.research.analysis.MediaAnalysisService.analyze` | method | `src/jarvis_v2/research/analysis.py:202-230` | def analyze(self, media_id: str, media_kind: str, start_ms: int, end_ms: int, *, modality: str, permission_granted: bool) -> MediaAnalysisResult | 1 | active |
| `jarvis_v2.research.analysis.MediaAnalysisService._save` | method | `src/jarvis_v2/research/analysis.py:232-243` | def _save(self, media_id: str, media_kind: str, start_ms: int, end_ms: int, modality: str, permission: bool, observed_at: str, status: str, finding: str \| None, failure: str \| No | 0 | active |
| `jarvis_v2.research.comparison.ComparisonError` | class | `src/jarvis_v2/research/comparison.py:15-16` | class ComparisonError(ValueError) | 1 | active |
| `jarvis_v2.research.comparison._identifier` | function | `src/jarvis_v2/research/comparison.py:19-22` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.comparison._text` | function | `src/jarvis_v2/research/comparison.py:25-33` | def _text(value: object, label: str, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.comparison._confidence` | function | `src/jarvis_v2/research/comparison.py:36-41` | def _confidence(value: object) -> float \| None | 0 | active |
| `jarvis_v2.research.comparison.SourceClaim` | class | `src/jarvis_v2/research/comparison.py:45-67` | class SourceClaim() | 1 | active |
| `jarvis_v2.research.comparison.SourceClaim.__post_init__` | method | `src/jarvis_v2/research/comparison.py:56-64` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.comparison.SourceClaim.evidence_ref` | method | `src/jarvis_v2/research/comparison.py:66-67` | def evidence_ref(self) -> str | 6 | active |
| `jarvis_v2.research.comparison.ResearchFinding` | class | `src/jarvis_v2/research/comparison.py:71-119` | class ResearchFinding() | 0 | active |
| `jarvis_v2.research.comparison.ResearchFinding.__post_init__` | method | `src/jarvis_v2/research/comparison.py:84-106` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.comparison.ResearchFinding.as_dict` | method | `src/jarvis_v2/research/comparison.py:108-119` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.comparison.SourceComparisonResult` | class | `src/jarvis_v2/research/comparison.py:123-134` | class SourceComparisonResult() | 0 | active |
| `jarvis_v2.research.comparison.SourceComparisonResult.__post_init__` | method | `src/jarvis_v2/research/comparison.py:127-131` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.comparison.SourceComparisonResult.as_dict` | method | `src/jarvis_v2/research/comparison.py:133-134` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.comparison.SourceComparator` | class | `src/jarvis_v2/research/comparison.py:137-182` | class SourceComparator() | 1 | active |
| `jarvis_v2.research.comparison.SourceComparator.compare` | method | `src/jarvis_v2/research/comparison.py:140-182` | def compare(self, claims: Iterable[SourceClaim]) -> SourceComparisonResult | 1 | active |
| `jarvis_v2.research.github.GitHubSourceError` | class | `src/jarvis_v2/research/github.py:26-27` | class GitHubSourceError(ValueError) | 1 | active |
| `jarvis_v2.research.github._text` | function | `src/jarvis_v2/research/github.py:30-38` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.github._sha` | function | `src/jarvis_v2/research/github.py:41-44` | def _sha(value: object) -> str | 0 | active |
| `jarvis_v2.research.github._timestamp` | function | `src/jarvis_v2/research/github.py:47-51` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.research.github._safe_path` | function | `src/jarvis_v2/research/github.py:54-61` | def _safe_path(path: object) -> str | 0 | active |
| `jarvis_v2.research.github.RepositoryPolicy` | class | `src/jarvis_v2/research/github.py:65-94` | class RepositoryPolicy() | 2 | active |
| `jarvis_v2.research.github.RepositoryPolicy.__post_init__` | method | `src/jarvis_v2/research/github.py:74-87` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.RepositoryPolicy.repository` | method | `src/jarvis_v2/research/github.py:90-91` | def repository(self) -> str | 9 | active |
| `jarvis_v2.research.github.RepositoryPolicy.allows_path` | method | `src/jarvis_v2/research/github.py:93-94` | def allows_path(self, path: str) -> bool | 0 | active |
| `jarvis_v2.research.github.SourceFile` | class | `src/jarvis_v2/research/github.py:98-118` | class SourceFile() | 0 | active |
| `jarvis_v2.research.github.SourceFile.__post_init__` | method | `src/jarvis_v2/research/github.py:104-110` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.SourceFile.as_dict` | method | `src/jarvis_v2/research/github.py:112-118` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.github.PinnedCommit` | class | `src/jarvis_v2/research/github.py:122-152` | class PinnedCommit() | 0 | active |
| `jarvis_v2.research.github.PinnedCommit.__post_init__` | method | `src/jarvis_v2/research/github.py:131-141` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.PinnedCommit.as_dict` | method | `src/jarvis_v2/research/github.py:143-152` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.github.GitHubSearchHit` | class | `src/jarvis_v2/research/github.py:156-177` | class GitHubSearchHit() | 0 | active |
| `jarvis_v2.research.github.GitHubSearchHit.__post_init__` | method | `src/jarvis_v2/research/github.py:163-168` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.GitHubSearchHit.as_dict` | method | `src/jarvis_v2/research/github.py:170-177` | def as_dict(self) -> dict[str, str] | 18 | active |
| `jarvis_v2.research.github.GitHubSearchResult` | class | `src/jarvis_v2/research/github.py:181-202` | class GitHubSearchResult() | 0 | active |
| `jarvis_v2.research.github.GitHubSearchResult.__post_init__` | method | `src/jarvis_v2/research/github.py:187-194` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.GitHubSearchResult.as_dict` | method | `src/jarvis_v2/research/github.py:196-202` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.github.GitHubCommitResult` | class | `src/jarvis_v2/research/github.py:206-227` | class GitHubCommitResult() | 0 | active |
| `jarvis_v2.research.github.GitHubCommitResult.__post_init__` | method | `src/jarvis_v2/research/github.py:212-219` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.github.GitHubCommitResult.as_dict` | method | `src/jarvis_v2/research/github.py:221-227` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter` | class | `src/jarvis_v2/research/github.py:234-401` | class GitHubSourceAdapter() | 2 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter.__init__` | method | `src/jarvis_v2/research/github.py:237-261` | def __init__(self, repositories: Iterable[RepositoryPolicy], *, search_transport: SearchTransport \| None=None, commit_transport: CommitTransport \| None=None, clock: Callable[[],  | 5 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter.search` | method | `src/jarvis_v2/research/github.py:263-304` | def search(self, query: str, *, limit: int=10) -> GitHubSearchResult | 9 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter.inspect_commit` | method | `src/jarvis_v2/research/github.py:306-348` | def inspect_commit(self, repository: str, commit_sha: str) -> GitHubCommitResult | 2 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter._repository_uri` | method | `src/jarvis_v2/research/github.py:353-367` | def _repository_uri(uri: object, repository: str) -> bool | 0 | active |
| `jarvis_v2.research.github.GitHubSourceAdapter._files` | method | `src/jarvis_v2/research/github.py:370-401` | def _files(value: object, policy: RepositoryPolicy) -> tuple[SourceFile, ...] | 0 | active |
| `jarvis_v2.research.handbook.HandbookGovernanceError` | class | `src/jarvis_v2/research/handbook.py:32-33` | class HandbookGovernanceError(ValueError) | 1 | active |
| `jarvis_v2.research.handbook.sha256_text` | function | `src/jarvis_v2/research/handbook.py:36-40` | def sha256_text(value: str) -> str | 1 | active |
| `jarvis_v2.research.handbook._identifier` | function | `src/jarvis_v2/research/handbook.py:43-46` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.handbook._sha` | function | `src/jarvis_v2/research/handbook.py:49-52` | def _sha(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.handbook._text` | function | `src/jarvis_v2/research/handbook.py:55-63` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.handbook._markdown` | function | `src/jarvis_v2/research/handbook.py:66-74` | def _markdown(value: object) -> str | 0 | active |
| `jarvis_v2.research.handbook._timestamp` | function | `src/jarvis_v2/research/handbook.py:77-86` | def _timestamp(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.handbook._strict_dict` | function | `src/jarvis_v2/research/handbook.py:89-92` | def _strict_dict(data: object, expected: set[str], label: str) -> Mapping[str, object] | 0 | active |
| `jarvis_v2.research.handbook.HandbookEditProposalV1` | class | `src/jarvis_v2/research/handbook.py:96-174` | class HandbookEditProposalV1() | 1 | active |
| `jarvis_v2.research.handbook.HandbookEditProposalV1.__post_init__` | method | `src/jarvis_v2/research/handbook.py:115-141` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.handbook.HandbookEditProposalV1.as_dict` | method | `src/jarvis_v2/research/handbook.py:143-160` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.handbook.HandbookEditProposalV1.from_dict` | method | `src/jarvis_v2/research/handbook.py:163-174` | def from_dict(cls, data: object) -> 'HandbookEditProposalV1' | 3 | active |
| `jarvis_v2.research.handbook.HandbookReviewReceipt` | class | `src/jarvis_v2/research/handbook.py:178-216` | class HandbookReviewReceipt() | 1 | active |
| `jarvis_v2.research.handbook.HandbookReviewReceipt.__post_init__` | method | `src/jarvis_v2/research/handbook.py:191-203` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.handbook.HandbookReviewReceipt.as_dict` | method | `src/jarvis_v2/research/handbook.py:205-216` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.handbook.HandbookOwnerApproval` | class | `src/jarvis_v2/research/handbook.py:220-243` | class HandbookOwnerApproval() | 1 | active |
| `jarvis_v2.research.handbook.HandbookOwnerApproval.__post_init__` | method | `src/jarvis_v2/research/handbook.py:229-234` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.handbook.HandbookOwnerApproval.as_dict` | method | `src/jarvis_v2/research/handbook.py:236-243` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.handbook.HandbookProposalRecord` | class | `src/jarvis_v2/research/handbook.py:247-265` | class HandbookProposalRecord() | 0 | active |
| `jarvis_v2.research.handbook.HandbookProposalRecord.__post_init__` | method | `src/jarvis_v2/research/handbook.py:254-256` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.handbook.HandbookProposalRecord.as_dict` | method | `src/jarvis_v2/research/handbook.py:258-265` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.handbook._StoredProposal` | class | `src/jarvis_v2/research/handbook.py:269-279` | class _StoredProposal() | 0 | active |
| `jarvis_v2.research.handbook._StoredProposal.snapshot` | method | `src/jarvis_v2/research/handbook.py:276-279` | def snapshot(self) -> HandbookProposalRecord | 17 | active |
| `jarvis_v2.research.handbook._proposer_allowed` | function | `src/jarvis_v2/research/handbook.py:282-289` | def _proposer_allowed(proposal: HandbookEditProposalV1) -> bool | 0 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow` | class | `src/jarvis_v2/research/handbook.py:292-406` | class HandbookProposalWorkflow() | 1 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.__init__` | method | `src/jarvis_v2/research/handbook.py:300-301` | def __init__(self) -> None | 5 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.submit` | method | `src/jarvis_v2/research/handbook.py:303-323` | def submit(self, proposal: HandbookEditProposalV1, *, candidate_content: str \| None=None) -> HandbookProposalRecord | 6 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.get` | method | `src/jarvis_v2/research/handbook.py:325-330` | def get(self, proposal_id: str) -> HandbookProposalRecord | 27 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.review` | method | `src/jarvis_v2/research/handbook.py:332-350` | def review(self, proposal_id: str, receipt: HandbookReviewReceipt) -> HandbookProposalRecord | 6 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.owner_approve` | method | `src/jarvis_v2/research/handbook.py:352-363` | def owner_approve(self, proposal_id: str, approval: HandbookOwnerApproval) -> HandbookProposalRecord | 1 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.queue_for_merge` | method | `src/jarvis_v2/research/handbook.py:365-376` | def queue_for_merge(self, proposal_id: str, *, current_base_digest: str) -> HandbookProposalRecord | 1 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow.merge` | method | `src/jarvis_v2/research/handbook.py:378-399` | def merge(self, proposal_id: str, *, merger_id: str, current_base_digest: str, applied_candidate_digest: str) -> HandbookProposalRecord | 5 | active |
| `jarvis_v2.research.handbook.HandbookProposalWorkflow._stored` | method | `src/jarvis_v2/research/handbook.py:401-406` | def _stored(self, proposal_id: str) -> _StoredProposal | 0 | active |
| `jarvis_v2.research.instagram.InstagramResearchError` | class | `src/jarvis_v2/research/instagram.py:21-22` | class InstagramResearchError(ValueError) | 0 | active |
| `jarvis_v2.research.instagram._text` | function | `src/jarvis_v2/research/instagram.py:25-33` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.instagram._timestamp` | function | `src/jarvis_v2/research/instagram.py:36-40` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.research.instagram.instagram_reel_id_from_url` | function | `src/jarvis_v2/research/instagram.py:43-61` | def instagram_reel_id_from_url(value: str) -> str | 1 | active |
| `jarvis_v2.research.instagram.InstagramReelRecord` | class | `src/jarvis_v2/research/instagram.py:65-101` | class InstagramReelRecord() | 0 | active |
| `jarvis_v2.research.instagram.InstagramReelRecord.__post_init__` | method | `src/jarvis_v2/research/instagram.py:75-89` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.instagram.InstagramReelRecord.as_dict` | method | `src/jarvis_v2/research/instagram.py:91-101` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.instagram.InstagramResult` | class | `src/jarvis_v2/research/instagram.py:105-123` | class InstagramResult() | 0 | active |
| `jarvis_v2.research.instagram.InstagramResult.__post_init__` | method | `src/jarvis_v2/research/instagram.py:110-116` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.instagram.InstagramResult.as_dict` | method | `src/jarvis_v2/research/instagram.py:118-123` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.instagram.InstagramReelStore` | class | `src/jarvis_v2/research/instagram.py:126-218` | class InstagramReelStore() | 2 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.__init__` | method | `src/jarvis_v2/research/instagram.py:129-150` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.__enter__` | method | `src/jarvis_v2/research/instagram.py:152-153` | def __enter__(self) -> 'InstagramReelStore' | 1 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.__exit__` | method | `src/jarvis_v2/research/instagram.py:155-156` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.save` | method | `src/jarvis_v2/research/instagram.py:158-172` | def save(self, record: InstagramReelRecord) -> None | 5 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.latest` | method | `src/jarvis_v2/research/instagram.py:174-189` | def latest(self, reel_id: str) -> InstagramReelRecord \| None | 10 | active |
| `jarvis_v2.research.instagram.InstagramReelStore._record` | method | `src/jarvis_v2/research/instagram.py:192-214` | def _record(data: Mapping[str, object]) -> InstagramReelRecord | 0 | active |
| `jarvis_v2.research.instagram.InstagramReelStore.close` | method | `src/jarvis_v2/research/instagram.py:216-218` | def close(self) -> None | 34 | active |
| `jarvis_v2.research.instagram.InstagramReelService` | class | `src/jarvis_v2/research/instagram.py:225-312` | class InstagramReelService() | 2 | active |
| `jarvis_v2.research.instagram.InstagramReelService.__init__` | method | `src/jarvis_v2/research/instagram.py:228-241` | def __init__(self, store: InstagramReelStore, *, metadata_transport: MetadataTransport \| None=None, audio_transport: AudioTransport \| None=None, clock: Callable[[], datetime] \|  | 5 | active |
| `jarvis_v2.research.instagram.InstagramReelService.fetch` | method | `src/jarvis_v2/research/instagram.py:243-289` | def fetch(self, source_url: str) -> InstagramResult | 8 | active |
| `jarvis_v2.research.instagram.InstagramReelService._save` | method | `src/jarvis_v2/research/instagram.py:291-296` | def _save(self, reel_id: str, source_url: str, observed_at: str, status: str, failure: str \| None, title: str='', caption: str='', segments: tuple[TranscriptSegment, ...]=()) -> I | 0 | active |
| `jarvis_v2.research.instagram.InstagramReelService._segments` | method | `src/jarvis_v2/research/instagram.py:299-312` | def _segments(values: Iterable[Mapping[str, object]], source_url: str) -> tuple[TranscriptSegment, ...] | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGError` | class | `src/jarvis_v2/research/media_rag.py:28-29` | class MediaRAGError(ValueError) | 0 | active |
| `jarvis_v2.research.media_rag._text` | function | `src/jarvis_v2/research/media_rag.py:32-40` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.media_rag._id` | function | `src/jarvis_v2/research/media_rag.py:43-46` | def _id(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.media_rag._int` | function | `src/jarvis_v2/research/media_rag.py:49-52` | def _int(value: object, label: str) -> int | 0 | active |
| `jarvis_v2.research.media_rag._offsets` | function | `src/jarvis_v2/research/media_rag.py:55-58` | def _offsets(start_ms: object, end_ms: object) -> tuple[int, int] | 0 | active |
| `jarvis_v2.research.media_rag.SourceSpan` | class | `src/jarvis_v2/research/media_rag.py:62-84` | class SourceSpan() | 0 | active |
| `jarvis_v2.research.media_rag.SourceSpan.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:71-75` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag.SourceSpan.as_dict` | method | `src/jarvis_v2/research/media_rag.py:77-84` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.media_rag.VideoChunk` | class | `src/jarvis_v2/research/media_rag.py:88-120` | class VideoChunk() | 0 | active |
| `jarvis_v2.research.media_rag.VideoChunk.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:99-109` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag.VideoChunk.as_dict` | method | `src/jarvis_v2/research/media_rag.py:111-120` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.media_rag.Topic` | class | `src/jarvis_v2/research/media_rag.py:124-145` | class Topic() | 0 | active |
| `jarvis_v2.research.media_rag.Topic.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:132-137` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag.Topic.as_dict` | method | `src/jarvis_v2/research/media_rag.py:139-145` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.media_rag.IndexedVideo` | class | `src/jarvis_v2/research/media_rag.py:149-166` | class IndexedVideo() | 0 | active |
| `jarvis_v2.research.media_rag.IndexedVideo.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:154-159` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag.IndexedVideo.as_dict` | method | `src/jarvis_v2/research/media_rag.py:161-166` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.media_rag.VideoSummary` | class | `src/jarvis_v2/research/media_rag.py:170-197` | class VideoSummary() | 0 | active |
| `jarvis_v2.research.media_rag.VideoSummary.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:178-187` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag.VideoSummary.as_dict` | method | `src/jarvis_v2/research/media_rag.py:189-197` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.media_rag.MediaRAGResult` | class | `src/jarvis_v2/research/media_rag.py:201-212` | class MediaRAGResult() | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGResult.__post_init__` | method | `src/jarvis_v2/research/media_rag.py:206-212` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.media_rag._split_text` | function | `src/jarvis_v2/research/media_rag.py:215-244` | def _split_text(value: str, maximum: int) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.research.media_rag.chunk_video` | function | `src/jarvis_v2/research/media_rag.py:247-295` | def chunk_video(record: VideoRecord, *, max_bytes: int=MAX_CHUNK_BYTES) -> tuple[VideoChunk, ...] | 1 | active |
| `jarvis_v2.research.media_rag.chunk_video.flush` | function | `src/jarvis_v2/research/media_rag.py:258-278` | def flush() -> None | 3 | active |
| `jarvis_v2.research.media_rag.extract_topics` | function | `src/jarvis_v2/research/media_rag.py:298-324` | def extract_topics(chunks: Iterable[VideoChunk], *, limit: int=MAX_TOPICS) -> tuple[Topic, ...] | 1 | active |
| `jarvis_v2.research.media_rag._sentences` | function | `src/jarvis_v2/research/media_rag.py:327-329` | def _sentences(text: str) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore` | class | `src/jarvis_v2/research/media_rag.py:332-393` | class MediaRAGStore() | 1 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.__init__` | method | `src/jarvis_v2/research/media_rag.py:335-351` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.__enter__` | method | `src/jarvis_v2/research/media_rag.py:353-354` | def __enter__(self) -> 'MediaRAGStore' | 1 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.__exit__` | method | `src/jarvis_v2/research/media_rag.py:356-357` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.save_chunks` | method | `src/jarvis_v2/research/media_rag.py:359-367` | def save_chunks(self, chunks: Iterable[VideoChunk]) -> None | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.save_summary` | method | `src/jarvis_v2/research/media_rag.py:369-375` | def save_summary(self, summary: VideoSummary) -> None | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.chunks_for` | method | `src/jarvis_v2/research/media_rag.py:377-382` | def chunks_for(self, video_id: str) -> tuple[VideoChunk, ...] | 1 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.summary` | method | `src/jarvis_v2/research/media_rag.py:384-389` | def summary(self, summary_id: str) -> VideoSummary \| None | 6 | active |
| `jarvis_v2.research.media_rag.MediaRAGStore.close` | method | `src/jarvis_v2/research/media_rag.py:391-393` | def close(self) -> None | 34 | active |
| `jarvis_v2.research.media_rag._span_from_dict` | function | `src/jarvis_v2/research/media_rag.py:396-401` | def _span_from_dict(value: Mapping[str, object]) -> SourceSpan | 0 | active |
| `jarvis_v2.research.media_rag._chunk_from_dict` | function | `src/jarvis_v2/research/media_rag.py:404-415` | def _chunk_from_dict(value: Mapping[str, object]) -> VideoChunk | 0 | active |
| `jarvis_v2.research.media_rag._summary_from_dict` | function | `src/jarvis_v2/research/media_rag.py:418-429` | def _summary_from_dict(value: Mapping[str, object]) -> VideoSummary | 0 | active |
| `jarvis_v2.research.media_rag.MediaRAGService` | class | `src/jarvis_v2/research/media_rag.py:432-501` | class MediaRAGService() | 2 | active |
| `jarvis_v2.research.media_rag.MediaRAGService.__init__` | method | `src/jarvis_v2/research/media_rag.py:435-438` | def __init__(self, store: MediaRAGStore \| None=None) | 5 | active |
| `jarvis_v2.research.media_rag.MediaRAGService.index` | method | `src/jarvis_v2/research/media_rag.py:440-445` | def index(self, record: VideoRecord) -> IndexedVideo | 15 | active |
| `jarvis_v2.research.media_rag.MediaRAGService.summarize` | method | `src/jarvis_v2/research/media_rag.py:447-501` | def summarize(self, records: Iterable[VideoRecord]) -> MediaRAGResult | 7 | active |
| `jarvis_v2.research.subscriptions.SubscriptionError` | class | `src/jarvis_v2/research/subscriptions.py:21-22` | class SubscriptionError(ValueError) | 1 | active |
| `jarvis_v2.research.subscriptions._text` | function | `src/jarvis_v2/research/subscriptions.py:25-33` | def _text(value: object, label: str, maximum: int=128) -> str | 2 | active |
| `jarvis_v2.research.subscriptions._identifier` | function | `src/jarvis_v2/research/subscriptions.py:36-39` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.research.subscriptions._cadence` | function | `src/jarvis_v2/research/subscriptions.py:42-45` | def _cadence(value: object) -> int | 0 | active |
| `jarvis_v2.research.subscriptions._clock_value` | function | `src/jarvis_v2/research/subscriptions.py:48-52` | def _clock_value(clock: Callable[[], int]) -> int | 0 | active |
| `jarvis_v2.research.subscriptions.Subscription` | class | `src/jarvis_v2/research/subscriptions.py:56-103` | class Subscription() | 1 | active |
| `jarvis_v2.research.subscriptions.Subscription.__post_init__` | method | `src/jarvis_v2/research/subscriptions.py:69-88` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.subscriptions.Subscription.as_dict` | method | `src/jarvis_v2/research/subscriptions.py:90-103` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.subscriptions.RefreshResult` | class | `src/jarvis_v2/research/subscriptions.py:107-120` | class RefreshResult() | 0 | active |
| `jarvis_v2.research.subscriptions.RefreshResult.__post_init__` | method | `src/jarvis_v2/research/subscriptions.py:113-120` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore` | class | `src/jarvis_v2/research/subscriptions.py:123-263` | class SubscriptionStore() | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.__init__` | method | `src/jarvis_v2/research/subscriptions.py:126-152` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.__enter__` | method | `src/jarvis_v2/research/subscriptions.py:154-155` | def __enter__(self) -> 'SubscriptionStore' | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.__exit__` | method | `src/jarvis_v2/research/subscriptions.py:157-158` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.close` | method | `src/jarvis_v2/research/subscriptions.py:160-162` | def close(self) -> None | 34 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.save` | method | `src/jarvis_v2/research/subscriptions.py:164-207` | def save(self, source_id: str, channel: str, topic: str, cadence_seconds: int, *, now: int, next_refresh_at: int \| None=None) -> Subscription | 5 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.get` | method | `src/jarvis_v2/research/subscriptions.py:209-216` | def get(self, subscription_id: str) -> Subscription | 27 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.due` | method | `src/jarvis_v2/research/subscriptions.py:218-229` | def due(self, now: int, *, limit: int=MAX_REFRESH_BATCH) -> list[Subscription] | 4 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.record_refresh` | method | `src/jarvis_v2/research/subscriptions.py:231-246` | def record_refresh(self, subscription_id: str, *, now: int, status: str, failure: str \| None=None) -> Subscription | 0 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore.disable` | method | `src/jarvis_v2/research/subscriptions.py:248-255` | def disable(self, subscription_id: str) -> None | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionStore._row` | method | `src/jarvis_v2/research/subscriptions.py:258-263` | def _row(row: sqlite3.Row) -> Subscription | 0 | active |
| `jarvis_v2.research.subscriptions.SubscriptionService` | class | `src/jarvis_v2/research/subscriptions.py:269-318` | class SubscriptionService() | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionService.__init__` | method | `src/jarvis_v2/research/subscriptions.py:272-278` | def __init__(self, store: SubscriptionStore, *, clock: Callable[[], int] \| None=None) -> None | 5 | active |
| `jarvis_v2.research.subscriptions.SubscriptionService.follow` | method | `src/jarvis_v2/research/subscriptions.py:280-293` | def follow(self, source_id: str, channel: str, topic: str, cadence_seconds: int, *, next_refresh_at: int \| None=None) -> Subscription | 1 | active |
| `jarvis_v2.research.subscriptions.SubscriptionService.refresh_due` | method | `src/jarvis_v2/research/subscriptions.py:295-318` | def refresh_due(self, transport: RefreshTransport, *, limit: int=MAX_REFRESH_BATCH) -> tuple[RefreshResult, ...] | 1 | active |
| `jarvis_v2.research.web.ResearchError` | class | `src/jarvis_v2/research/web.py:23-24` | class ResearchError(ValueError) | 1 | active |
| `jarvis_v2.research.web._identifier` | function | `src/jarvis_v2/research/web.py:27-30` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.research.web._text` | function | `src/jarvis_v2/research/web.py:33-41` | def _text(value: str, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.web._content` | function | `src/jarvis_v2/research/web.py:44-52` | def _content(value: str) -> str | 0 | active |
| `jarvis_v2.research.web._timestamp` | function | `src/jarvis_v2/research/web.py:55-59` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.research.web.SourcePolicy` | class | `src/jarvis_v2/research/web.py:63-93` | class SourcePolicy() | 3 | active |
| `jarvis_v2.research.web.SourcePolicy.__post_init__` | method | `src/jarvis_v2/research/web.py:70-75` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.web.SourcePolicy.allows` | method | `src/jarvis_v2/research/web.py:77-93` | def allows(self, uri: str) -> bool | 1 | active |
| `jarvis_v2.research.web.SearchHit` | class | `src/jarvis_v2/research/web.py:97-127` | class SearchHit() | 0 | active |
| `jarvis_v2.research.web.SearchHit.__post_init__` | method | `src/jarvis_v2/research/web.py:108-116` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.web.SearchHit.as_dict` | method | `src/jarvis_v2/research/web.py:118-127` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.web.SearchResult` | class | `src/jarvis_v2/research/web.py:131-154` | class SearchResult() | 0 | active |
| `jarvis_v2.research.web.SearchResult.__post_init__` | method | `src/jarvis_v2/research/web.py:139-146` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.web.SearchResult.as_dict` | method | `src/jarvis_v2/research/web.py:148-154` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.web.FetchedDocument` | class | `src/jarvis_v2/research/web.py:158-192` | class FetchedDocument() | 0 | active |
| `jarvis_v2.research.web.FetchedDocument.__post_init__` | method | `src/jarvis_v2/research/web.py:170-180` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.web.FetchedDocument.as_dict` | method | `src/jarvis_v2/research/web.py:182-192` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.web.FetchResult` | class | `src/jarvis_v2/research/web.py:196-219` | class FetchResult() | 0 | active |
| `jarvis_v2.research.web.FetchResult.__post_init__` | method | `src/jarvis_v2/research/web.py:204-211` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.web.FetchResult.as_dict` | method | `src/jarvis_v2/research/web.py:213-219` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.web.WebDiscoveryService` | class | `src/jarvis_v2/research/web.py:226-363` | class WebDiscoveryService() | 2 | active |
| `jarvis_v2.research.web.WebDiscoveryService.__init__` | method | `src/jarvis_v2/research/web.py:229-262` | def __init__(self, sources: Iterable[SourcePolicy], *, search_transport: SearchTransport \| None=None, fetch_transport: FetchTransport \| None=None, clock: Callable[[], datetime] \ | 5 | active |
| `jarvis_v2.research.web.WebDiscoveryService.search` | method | `src/jarvis_v2/research/web.py:264-300` | def search(self, query: str, *, source_id: str \| None=None, limit: int=10) -> SearchResult | 9 | active |
| `jarvis_v2.research.web.WebDiscoveryService.fetch` | method | `src/jarvis_v2/research/web.py:302-335` | def fetch(self, source_id: str, uri: str) -> FetchResult | 8 | active |
| `jarvis_v2.research.web.WebDiscoveryService._policies` | method | `src/jarvis_v2/research/web.py:337-342` | def _policies(self, source_id: str \| None) -> tuple[SourcePolicy, ...] | 0 | active |
| `jarvis_v2.research.web.WebDiscoveryService._hit` | method | `src/jarvis_v2/research/web.py:345-363` | def _hit(item: Mapping[str, object], policy: SourcePolicy, observed_at: str) -> SearchHit \| None | 0 | active |
| `jarvis_v2.research.youtube.YouTubeResearchError` | class | `src/jarvis_v2/research/youtube.py:21-22` | class YouTubeResearchError(ValueError) | 0 | active |
| `jarvis_v2.research.youtube._text` | function | `src/jarvis_v2/research/youtube.py:25-33` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.research.youtube._timestamp` | function | `src/jarvis_v2/research/youtube.py:36-40` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.research.youtube.video_id_from_url` | function | `src/jarvis_v2/research/youtube.py:43-69` | def video_id_from_url(value: str) -> str | 1 | active |
| `jarvis_v2.research.youtube.TranscriptSegment` | class | `src/jarvis_v2/research/youtube.py:73-90` | class TranscriptSegment() | 2 | active |
| `jarvis_v2.research.youtube.TranscriptSegment.__post_init__` | method | `src/jarvis_v2/research/youtube.py:79-87` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.youtube.TranscriptSegment.as_dict` | method | `src/jarvis_v2/research/youtube.py:89-90` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.youtube.VideoRecord` | class | `src/jarvis_v2/research/youtube.py:94-171` | class VideoRecord() | 2 | active |
| `jarvis_v2.research.youtube.VideoRecord.__post_init__` | method | `src/jarvis_v2/research/youtube.py:104-119` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.youtube.VideoRecord.as_dict` | method | `src/jarvis_v2/research/youtube.py:121-131` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.youtube.VideoRecord.from_dict` | method | `src/jarvis_v2/research/youtube.py:134-171` | def from_dict(cls, data: Mapping[str, object]) -> 'VideoRecord' | 3 | active |
| `jarvis_v2.research.youtube.VideoResult` | class | `src/jarvis_v2/research/youtube.py:175-193` | class VideoResult() | 0 | active |
| `jarvis_v2.research.youtube.VideoResult.__post_init__` | method | `src/jarvis_v2/research/youtube.py:180-186` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.research.youtube.VideoResult.as_dict` | method | `src/jarvis_v2/research/youtube.py:188-193` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.research.youtube.VideoResearchStore` | class | `src/jarvis_v2/research/youtube.py:196-263` | class VideoResearchStore() | 2 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.__init__` | method | `src/jarvis_v2/research/youtube.py:199-220` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.__enter__` | method | `src/jarvis_v2/research/youtube.py:222-223` | def __enter__(self) -> 'VideoResearchStore' | 1 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.__exit__` | method | `src/jarvis_v2/research/youtube.py:225-226` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.save` | method | `src/jarvis_v2/research/youtube.py:228-242` | def save(self, record: VideoRecord) -> None | 5 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.latest` | method | `src/jarvis_v2/research/youtube.py:244-259` | def latest(self, video_id: str) -> VideoRecord \| None | 10 | active |
| `jarvis_v2.research.youtube.VideoResearchStore.close` | method | `src/jarvis_v2/research/youtube.py:261-263` | def close(self) -> None | 34 | active |
| `jarvis_v2.research.youtube.YouTubeResearchService` | class | `src/jarvis_v2/research/youtube.py:270-355` | class YouTubeResearchService() | 1 | active |
| `jarvis_v2.research.youtube.YouTubeResearchService.__init__` | method | `src/jarvis_v2/research/youtube.py:273-286` | def __init__(self, store: VideoResearchStore, *, metadata_transport: MetadataTransport \| None=None, transcript_transport: TranscriptTransport \| None=None, clock: Callable[[], dat | 5 | active |
| `jarvis_v2.research.youtube.YouTubeResearchService.fetch` | method | `src/jarvis_v2/research/youtube.py:288-329` | def fetch(self, source_url: str) -> VideoResult | 8 | active |
| `jarvis_v2.research.youtube.YouTubeResearchService._save` | method | `src/jarvis_v2/research/youtube.py:331-336` | def _save(self, video_id: str, source_url: str, observed_at: str, status: str, failure: str \| None, title: str='', published_at: str \| None=None, transcript: tuple[TranscriptSegm | 0 | active |
| `jarvis_v2.research.youtube.YouTubeResearchService._segments` | method | `src/jarvis_v2/research/youtube.py:339-355` | def _segments(values: Iterable[Mapping[str, object]], source_url: str) -> tuple[TranscriptSegment, ...] | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileError` | class | `src/jarvis_v2/runtime/browser.py:32-33` | class BrowserProfileError(ValueError) | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolError` | class | `src/jarvis_v2/runtime/browser.py:36-37` | class BrowserToolError(ValueError) | 1 | active |
| `jarvis_v2.runtime.browser._identifier` | function | `src/jarvis_v2/runtime/browser.py:40-43` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.browser._site` | function | `src/jarvis_v2/runtime/browser.py:46-49` | def _site(value: str) -> str | 0 | active |
| `jarvis_v2.runtime.browser._actions` | function | `src/jarvis_v2/runtime/browser.py:52-63` | def _actions(values: Iterable[str], label: str='actions') -> tuple[str, ...] | 0 | active |
| `jarvis_v2.runtime.browser._json` | function | `src/jarvis_v2/runtime/browser.py:66-70` | def _json(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.browser._now` | function | `src/jarvis_v2/runtime/browser.py:73-77` | def _now(clock: Callable[[], float]) -> str | 0 | active |
| `jarvis_v2.runtime.browser._digest` | function | `src/jarvis_v2/runtime/browser.py:80-81` | def _digest(value: str) -> str | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfile` | class | `src/jarvis_v2/runtime/browser.py:85-102` | class BrowserProfile() | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfile.model_context` | method | `src/jarvis_v2/runtime/browser.py:95-102` | def model_context(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.runtime.browser.LoginHandoff` | class | `src/jarvis_v2/runtime/browser.py:106-121` | class LoginHandoff() | 0 | active |
| `jarvis_v2.runtime.browser.LoginHandoff.model_context` | method | `src/jarvis_v2/runtime/browser.py:115-121` | def model_context(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.runtime.browser.BrowserActionReceipt` | class | `src/jarvis_v2/runtime/browser.py:125-145` | class BrowserActionReceipt() | 0 | active |
| `jarvis_v2.runtime.browser.BrowserActionReceipt.model_context` | method | `src/jarvis_v2/runtime/browser.py:136-145` | def model_context(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.runtime.browser.BrowserAdapter` | class | `src/jarvis_v2/runtime/browser.py:148-159` | class BrowserAdapter(Protocol) | 0 | active |
| `jarvis_v2.runtime.browser.BrowserAdapter.navigate` | method | `src/jarvis_v2/runtime/browser.py:151-151` | def navigate(self, profile_dir: str, target_ref: str) -> Mapping[str, object] | 1 | active |
| `jarvis_v2.runtime.browser.BrowserAdapter.read` | method | `src/jarvis_v2/runtime/browser.py:153-153` | def read(self, profile_dir: str, target_ref: str) -> Mapping[str, object] | 32 | active |
| `jarvis_v2.runtime.browser.BrowserAdapter.click` | method | `src/jarvis_v2/runtime/browser.py:155-155` | def click(self, profile_dir: str, target_ref: str) -> Mapping[str, object] | 1 | active |
| `jarvis_v2.runtime.browser.BrowserAdapter.form` | method | `src/jarvis_v2/runtime/browser.py:157-159` | def form(self, profile_dir: str, target_ref: str, fields: Mapping[str, str]) -> Mapping[str, object] | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolResult` | class | `src/jarvis_v2/runtime/browser.py:163-176` | class BrowserToolResult() | 0 | active |
| `jarvis_v2.runtime.browser.BrowserToolResult.model_context` | method | `src/jarvis_v2/runtime/browser.py:170-176` | def model_context(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.runtime.browser.BrowserToolService` | class | `src/jarvis_v2/runtime/browser.py:179-281` | class BrowserToolService() | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolService.__init__` | method | `src/jarvis_v2/runtime/browser.py:182-186` | def __init__(self, profiles: 'BrowserProfileService', adapter: BrowserAdapter) -> None | 5 | active |
| `jarvis_v2.runtime.browser.BrowserToolService.navigate` | method | `src/jarvis_v2/runtime/browser.py:188-194` | def navigate(self, profile_id: str, request_id: str, *, target_ref: str, confirmed: bool=False) -> BrowserToolResult | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolService.read` | method | `src/jarvis_v2/runtime/browser.py:196-202` | def read(self, profile_id: str, request_id: str, *, target_ref: str) -> BrowserToolResult | 32 | active |
| `jarvis_v2.runtime.browser.BrowserToolService.click` | method | `src/jarvis_v2/runtime/browser.py:204-210` | def click(self, profile_id: str, request_id: str, *, target_ref: str, confirmed: bool=False) -> BrowserToolResult | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolService.form` | method | `src/jarvis_v2/runtime/browser.py:212-225` | def form(self, profile_id: str, request_id: str, *, target_ref: str, fields: Mapping[str, str], confirmed: bool=False) -> BrowserToolResult | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolService._run` | method | `src/jarvis_v2/runtime/browser.py:227-247` | def _run(self, profile_id: str, request_id: str, operation: str, target_ref: str, confirmed: bool, call: Callable[[str], Mapping[str, object]]) -> BrowserToolResult | 1 | active |
| `jarvis_v2.runtime.browser.BrowserToolService._fields` | method | `src/jarvis_v2/runtime/browser.py:250-262` | def _fields(fields: Mapping[str, str]) -> dict[str, str] | 0 | active |
| `jarvis_v2.runtime.browser.BrowserToolService._result` | method | `src/jarvis_v2/runtime/browser.py:265-281` | def _result(result: Mapping[str, object]) -> Mapping[str, object] | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService` | class | `src/jarvis_v2/runtime/browser.py:284-555` | class BrowserProfileService() | 2 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.__init__` | method | `src/jarvis_v2/runtime/browser.py:287-340` | def __init__(self, database: str \| Path \| sqlite3.Connection, profile_root: str \| Path, *, site_actions: Mapping[str, Iterable[str]], read_only_actions: Iterable[str]=('read', ' | 5 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.__enter__` | method | `src/jarvis_v2/runtime/browser.py:342-343` | def __enter__(self) -> 'BrowserProfileService' | 1 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.__exit__` | method | `src/jarvis_v2/runtime/browser.py:345-346` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.create_profile` | method | `src/jarvis_v2/runtime/browser.py:348-378` | def create_profile(self, profile_id: str, site: str, *, allowed_actions: Iterable[str] \| None=None) -> BrowserProfile | 2 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.begin_login` | method | `src/jarvis_v2/runtime/browser.py:380-406` | def begin_login(self, profile_id: str, handoff_id: str) -> LoginHandoff | 2 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.complete_login` | method | `src/jarvis_v2/runtime/browser.py:408-436` | def complete_login(self, profile_id: str, handoff_id: str, *, proof_ref: str) -> LoginHandoff | 2 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.revoke_profile` | method | `src/jarvis_v2/runtime/browser.py:438-447` | def revoke_profile(self, profile_id: str) -> BrowserProfile | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.authorize_action` | method | `src/jarvis_v2/runtime/browser.py:449-494` | def authorize_action(self, profile_id: str, request_id: str, *, action: str, target_ref: str, confirmed: bool=False) -> BrowserActionReceipt | 1 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.get_profile` | method | `src/jarvis_v2/runtime/browser.py:496-503` | def get_profile(self, profile_id: str) -> BrowserProfile | 1 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.adapter_context` | method | `src/jarvis_v2/runtime/browser.py:505-515` | def adapter_context(self, profile_id: str) -> dict[str, object] | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService._normalize_policies` | method | `src/jarvis_v2/runtime/browser.py:518-524` | def _normalize_policies(site_actions: Mapping[str, Iterable[str]]) -> dict[str, tuple[str, ...]] | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService._profile` | method | `src/jarvis_v2/runtime/browser.py:526-537` | def _profile(self, row: sqlite3.Row) -> BrowserProfile | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService._handoff` | method | `src/jarvis_v2/runtime/browser.py:540-543` | def _handoff(row: sqlite3.Row, site: str) -> LoginHandoff | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService._receipt` | method | `src/jarvis_v2/runtime/browser.py:546-551` | def _receipt(row: sqlite3.Row) -> BrowserActionReceipt | 0 | active |
| `jarvis_v2.runtime.browser.BrowserProfileService.close` | method | `src/jarvis_v2/runtime/browser.py:553-555` | def close(self) -> None | 34 | active |
| `jarvis_v2.runtime.calendar.CalendarError` | class | `src/jarvis_v2/runtime/calendar.py:22-23` | class CalendarError(ValueError) | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarAuthorizationError` | class | `src/jarvis_v2/runtime/calendar.py:26-27` | class CalendarAuthorizationError(CalendarError) | 1 | active |
| `jarvis_v2.runtime.calendar._identifier` | function | `src/jarvis_v2/runtime/calendar.py:30-33` | def _identifier(value: str, label: str='event id') -> str | 0 | active |
| `jarvis_v2.runtime.calendar._zone` | function | `src/jarvis_v2/runtime/calendar.py:36-42` | def _zone(value: str) -> ZoneInfo | 0 | active |
| `jarvis_v2.runtime.calendar._timestamp` | function | `src/jarvis_v2/runtime/calendar.py:45-53` | def _timestamp(value: datetime \| str, label: str) -> datetime | 0 | active |
| `jarvis_v2.runtime.calendar._text` | function | `src/jarvis_v2/runtime/calendar.py:56-63` | def _text(value: str, label: str, maximum: int, *, required: bool=True) -> str | 2 | active |
| `jarvis_v2.runtime.calendar.CalendarEvent` | class | `src/jarvis_v2/runtime/calendar.py:67-102` | class CalendarEvent() | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarEvent.__post_init__` | method | `src/jarvis_v2/runtime/calendar.py:77-92` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarEvent.as_dict` | method | `src/jarvis_v2/runtime/calendar.py:94-102` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.calendar.CalendarAdapter` | class | `src/jarvis_v2/runtime/calendar.py:105-114` | class CalendarAdapter(Protocol) | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarAdapter.read_events` | method | `src/jarvis_v2/runtime/calendar.py:108-110` | def read_events(self, start_utc: datetime, end_utc: datetime, *, limit: int) -> Sequence[CalendarEvent] | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarAdapter.create_event` | method | `src/jarvis_v2/runtime/calendar.py:112-112` | def create_event(self, event: CalendarEvent) -> CalendarEvent | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarAdapter.update_event` | method | `src/jarvis_v2/runtime/calendar.py:114-114` | def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarService` | class | `src/jarvis_v2/runtime/calendar.py:117-232` | class CalendarService() | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarService.__init__` | method | `src/jarvis_v2/runtime/calendar.py:120-126` | def __init__(self, adapter: CalendarAdapter, authorize: Callable[[str], bool]) -> None | 5 | active |
| `jarvis_v2.runtime.calendar.CalendarService.read_events` | method | `src/jarvis_v2/runtime/calendar.py:128-149` | def read_events(self, start: datetime \| str, end: datetime \| str, *, limit: int=MAX_EVENTS) -> tuple[CalendarEvent, ...] | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarService.create_event` | method | `src/jarvis_v2/runtime/calendar.py:153-171` | def create_event(self, event_id: str, title: str, start: datetime \| str, end: datetime \| str, *, timezone_name: str='UTC', description: str='', confirmed: bool=False) -> Calendar | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarService.update_event` | method | `src/jarvis_v2/runtime/calendar.py:173-192` | def update_event(self, event_id: str, title: str, start: datetime \| str, end: datetime \| str, *, timezone_name: str='UTC', description: str='', confirmed: bool=False) -> Calendar | 1 | active |
| `jarvis_v2.runtime.calendar.CalendarService._require` | method | `src/jarvis_v2/runtime/calendar.py:194-200` | def _require(self, scope: str) -> None | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarService._require_write` | method | `src/jarvis_v2/runtime/calendar.py:202-205` | def _require_write(self, confirmed: bool) -> None | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarService._range` | method | `src/jarvis_v2/runtime/calendar.py:208-213` | def _range(start: datetime \| str, end: datetime \| str) -> tuple[datetime, datetime] | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarService._build` | method | `src/jarvis_v2/runtime/calendar.py:216-226` | def _build(event_id: str, title: str, start: datetime \| str, end: datetime \| str, timezone_name: str, description: str) -> CalendarEvent | 0 | active |
| `jarvis_v2.runtime.calendar.CalendarService._returned` | method | `src/jarvis_v2/runtime/calendar.py:229-232` | def _returned(value: object) -> CalendarEvent | 0 | active |
| `jarvis_v2.runtime.chat.ChatServiceError` | class | `src/jarvis_v2/runtime/chat.py:22-23` | class ChatServiceError(ValueError) | 0 | active |
| `jarvis_v2.runtime.chat.ChatService` | class | `src/jarvis_v2/runtime/chat.py:29-171` | class ChatService() | 2 | active |
| `jarvis_v2.runtime.chat.ChatService.__init__` | method | `src/jarvis_v2/runtime/chat.py:32-35` | def __init__(self, conversations: ConversationStore) | 5 | active |
| `jarvis_v2.runtime.chat.ChatService.stream` | method | `src/jarvis_v2/runtime/chat.py:37-135` | async def stream(self, conversation_id: str, message: str, provider: Provider, *, provider_id: str='runtime', model: str='', cancel_event: Any=None, idempotency_key: str \| None=No | 5 | active |
| `jarvis_v2.runtime.chat.ChatService._validate_request` | method | `src/jarvis_v2/runtime/chat.py:138-154` | def _validate_request(conversation_id: str, message: str, provider_id: str, model: str, provider: Provider) -> None | 0 | active |
| `jarvis_v2.runtime.chat.ChatService._delta_content` | method | `src/jarvis_v2/runtime/chat.py:157-163` | def _delta_content(delta: Any) -> str | 0 | active |
| `jarvis_v2.runtime.chat.ChatService._cancelled` | method | `src/jarvis_v2/runtime/chat.py:166-167` | def _cancelled(cancel_event: Any) -> bool | 0 | active |
| `jarvis_v2.runtime.chat.ChatService._error` | method | `src/jarvis_v2/runtime/chat.py:170-171` | def _error(code: str, message: str) -> dict[str, Any] | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardError` | class | `src/jarvis_v2/runtime/dashboard.py:16-17` | class DashboardError(ValueError) | 1 | active |
| `jarvis_v2.runtime.dashboard._code` | function | `src/jarvis_v2/runtime/dashboard.py:20-23` | def _code(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.dashboard._text` | function | `src/jarvis_v2/runtime/dashboard.py:26-31` | def _text(value: str, label: str, maximum: int=256) -> str | 2 | active |
| `jarvis_v2.runtime.dashboard._timestamp` | function | `src/jarvis_v2/runtime/dashboard.py:34-37` | def _timestamp(value: datetime) -> datetime | 0 | active |
| `jarvis_v2.runtime.dashboard._now` | function | `src/jarvis_v2/runtime/dashboard.py:40-41` | def _now(clock: Callable[[], datetime]) -> datetime | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardRecord` | class | `src/jarvis_v2/runtime/dashboard.py:45-70` | class DashboardRecord() | 1 | active |
| `jarvis_v2.runtime.dashboard.DashboardRecord.__post_init__` | method | `src/jarvis_v2/runtime/dashboard.py:54-61` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardRecord.as_dict` | method | `src/jarvis_v2/runtime/dashboard.py:63-70` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.dashboard.DashboardSnapshot` | class | `src/jarvis_v2/runtime/dashboard.py:74-95` | class DashboardSnapshot() | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardSnapshot.__post_init__` | method | `src/jarvis_v2/runtime/dashboard.py:80-87` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardSnapshot.as_dict` | method | `src/jarvis_v2/runtime/dashboard.py:89-95` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.dashboard.DashboardService` | class | `src/jarvis_v2/runtime/dashboard.py:101-157` | class DashboardService() | 1 | active |
| `jarvis_v2.runtime.dashboard.DashboardService.__init__` | method | `src/jarvis_v2/runtime/dashboard.py:104-118` | def __init__(self, *, system: DashboardReader \| None=None, projects: DashboardReader \| None=None, activity: DashboardReader \| None=None, clock: Callable[[], datetime] \| None=No | 5 | active |
| `jarvis_v2.runtime.dashboard.DashboardService.snapshot` | method | `src/jarvis_v2/runtime/dashboard.py:120-127` | def snapshot(self) -> DashboardSnapshot | 17 | active |
| `jarvis_v2.runtime.dashboard.DashboardService._read` | method | `src/jarvis_v2/runtime/dashboard.py:131-147` | def _read(self, category: str) -> tuple[DashboardRecord, ...] | 0 | active |
| `jarvis_v2.runtime.dashboard.DashboardService._unavailable` | method | `src/jarvis_v2/runtime/dashboard.py:150-157` | def _unavailable(category: str, observed_at: datetime, failure: str) -> DashboardRecord | 0 | active |
| `jarvis_v2.runtime.email.EmailError` | class | `src/jarvis_v2/runtime/email.py:27-28` | class EmailError(ValueError) | 0 | active |
| `jarvis_v2.runtime.email.EmailAuthorizationError` | class | `src/jarvis_v2/runtime/email.py:31-32` | class EmailAuthorizationError(EmailError) | 1 | active |
| `jarvis_v2.runtime.email.EmailReconciliationRequired` | class | `src/jarvis_v2/runtime/email.py:35-36` | class EmailReconciliationRequired(EmailError) | 1 | active |
| `jarvis_v2.runtime.email.EmailTimeout` | class | `src/jarvis_v2/runtime/email.py:39-40` | class EmailTimeout(EmailError) | 1 | active |
| `jarvis_v2.runtime.email._identifier` | function | `src/jarvis_v2/runtime/email.py:43-46` | def _identifier(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.email._text` | function | `src/jarvis_v2/runtime/email.py:49-56` | def _text(value: str, label: str, maximum: int, *, required: bool=True) -> str | 2 | active |
| `jarvis_v2.runtime.email._recipients` | function | `src/jarvis_v2/runtime/email.py:59-73` | def _recipients(values: Sequence[str]) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.runtime.email._payload_sha` | function | `src/jarvis_v2/runtime/email.py:76-83` | def _payload_sha(message: 'EmailMessage') -> str | 0 | active |
| `jarvis_v2.runtime.email.EmailMessage` | class | `src/jarvis_v2/runtime/email.py:87-101` | class EmailMessage() | 0 | active |
| `jarvis_v2.runtime.email.EmailMessage.__post_init__` | method | `src/jarvis_v2/runtime/email.py:92-97` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.email.EmailMessage.payload_sha256` | method | `src/jarvis_v2/runtime/email.py:100-101` | def payload_sha256(self) -> str | 0 | active |
| `jarvis_v2.runtime.email.EmailSummary` | class | `src/jarvis_v2/runtime/email.py:105-127` | class EmailSummary() | 1 | active |
| `jarvis_v2.runtime.email.EmailSummary.__post_init__` | method | `src/jarvis_v2/runtime/email.py:113-119` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.email.EmailSummary.model_context` | method | `src/jarvis_v2/runtime/email.py:121-127` | def model_context(self) -> dict[str, str] | 3 | active |
| `jarvis_v2.runtime.email.EmailReceipt` | class | `src/jarvis_v2/runtime/email.py:131-145` | class EmailReceipt() | 0 | active |
| `jarvis_v2.runtime.email.EmailReceipt.model_context` | method | `src/jarvis_v2/runtime/email.py:138-145` | def model_context(self) -> dict[str, str] | 3 | active |
| `jarvis_v2.runtime.email.EmailAdapter` | class | `src/jarvis_v2/runtime/email.py:148-155` | class EmailAdapter(Protocol) | 0 | active |
| `jarvis_v2.runtime.email.EmailAdapter.search` | method | `src/jarvis_v2/runtime/email.py:151-151` | def search(self, query: str, *, limit: int) -> Sequence[EmailSummary] | 9 | active |
| `jarvis_v2.runtime.email.EmailAdapter.create_draft` | method | `src/jarvis_v2/runtime/email.py:153-153` | def create_draft(self, draft_id: str, message: EmailMessage) -> str | 1 | active |
| `jarvis_v2.runtime.email.EmailAdapter.send` | method | `src/jarvis_v2/runtime/email.py:155-155` | def send(self, send_id: str, message: EmailMessage) -> str | 3 | active |
| `jarvis_v2.runtime.email.EmailService` | class | `src/jarvis_v2/runtime/email.py:158-312` | class EmailService() | 1 | active |
| `jarvis_v2.runtime.email.EmailService.__init__` | method | `src/jarvis_v2/runtime/email.py:161-176` | def __init__(self, database: str, adapter: EmailAdapter, authorize: Callable[[str, str], bool], *, task_id: str='RUN-015', mailbox: str='primary') -> None | 5 | active |
| `jarvis_v2.runtime.email.EmailService.__enter__` | method | `src/jarvis_v2/runtime/email.py:178-179` | def __enter__(self) -> 'EmailService' | 1 | active |
| `jarvis_v2.runtime.email.EmailService.__exit__` | method | `src/jarvis_v2/runtime/email.py:181-182` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.runtime.email.EmailService.search` | method | `src/jarvis_v2/runtime/email.py:184-202` | def search(self, query: str, *, limit: int=MAX_SEARCH_RESULTS) -> tuple[EmailSummary, ...] | 9 | active |
| `jarvis_v2.runtime.email.EmailService.create_draft` | method | `src/jarvis_v2/runtime/email.py:204-215` | def create_draft(self, draft_id: str, recipients: Sequence[str], subject: str, body: str) -> EmailReceipt | 1 | active |
| `jarvis_v2.runtime.email.EmailService.send` | method | `src/jarvis_v2/runtime/email.py:219-238` | def send(self, send_id: str, recipients: Sequence[str], subject: str, body: str, *, owner_approved: bool=False) -> EmailReceipt | 3 | active |
| `jarvis_v2.runtime.email.EmailService.reconcile` | method | `src/jarvis_v2/runtime/email.py:240-241` | def reconcile(self) -> list[dict[str, object]] | 4 | active |
| `jarvis_v2.runtime.email.EmailService._require` | method | `src/jarvis_v2/runtime/email.py:243-249` | def _require(self, scope: str, payload_sha256: str) -> None | 0 | active |
| `jarvis_v2.runtime.email.EmailService._execute` | method | `src/jarvis_v2/runtime/email.py:251-285` | def _execute(self, request_id: str, operation: str, payload_sha256: str, call: Callable[[], str]) -> EmailReceipt | 0 | active |
| `jarvis_v2.runtime.email.EmailService._summary` | method | `src/jarvis_v2/runtime/email.py:288-291` | def _summary(value: object) -> EmailSummary | 0 | active |
| `jarvis_v2.runtime.email.EmailService._receipt` | method | `src/jarvis_v2/runtime/email.py:294-309` | def _receipt(effect: Mapping[str, object], request_id: str, operation: str, payload_sha256: str) -> EmailReceipt | 0 | active |
| `jarvis_v2.runtime.email.EmailService.close` | method | `src/jarvis_v2/runtime/email.py:311-312` | def close(self) -> None | 34 | active |
| `jarvis_v2.runtime.file_actions.FileActionError` | class | `src/jarvis_v2/runtime/file_actions.py:35-36` | class FileActionError(ValueError) | 1 | active |
| `jarvis_v2.runtime.file_actions.FileIdentity` | class | `src/jarvis_v2/runtime/file_actions.py:40-49` | class FileIdentity() | 0 | active |
| `jarvis_v2.runtime.file_actions.FileIdentity.digest` | method | `src/jarvis_v2/runtime/file_actions.py:47-49` | def digest(self) -> str | 17 | active |
| `jarvis_v2.runtime.file_actions.FileActionRequest` | class | `src/jarvis_v2/runtime/file_actions.py:53-70` | class FileActionRequest() | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionRequest.model_context` | method | `src/jarvis_v2/runtime/file_actions.py:62-70` | def model_context(self) -> dict[str, object] | 3 | active |
| `jarvis_v2.runtime.file_actions.FileActionService` | class | `src/jarvis_v2/runtime/file_actions.py:73-550` | class FileActionService() | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.__init__` | method | `src/jarvis_v2/runtime/file_actions.py:76-148` | def __init__(self, database: str \| Path, *, allowed_roots: tuple[Path, ...] \| list[Path], trash_root: str \| Path, audit_log: str \| Path, ttl_seconds: int=300, clock: Callable[[ | 5 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.__enter__` | method | `src/jarvis_v2/runtime/file_actions.py:150-151` | def __enter__(self) -> 'FileActionService' | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.__exit__` | method | `src/jarvis_v2/runtime/file_actions.py:153-154` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.preview` | method | `src/jarvis_v2/runtime/file_actions.py:156-167` | def preview(self, target: Path) -> dict[str, object] | 4 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_trash` | method | `src/jarvis_v2/runtime/file_actions.py:169-172` | def propose_trash(self, target: Path, reason: str) -> FileActionRequest | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_directory` | method | `src/jarvis_v2/runtime/file_actions.py:174-176` | def propose_directory(self, target: Path, reason: str) -> None | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.decide` | method | `src/jarvis_v2/runtime/file_actions.py:178-195` | def decide(self, request_id: str, approved: bool) -> FileActionRequest | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.trash_file` | method | `src/jarvis_v2/runtime/file_actions.py:197-246` | def trash_file(self, request_id: str) -> Path | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.propose_restore` | method | `src/jarvis_v2/runtime/file_actions.py:248-263` | def propose_restore(self, trash_request_id: str, reason: str) -> FileActionRequest | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.restore_file` | method | `src/jarvis_v2/runtime/file_actions.py:265-313` | def restore_file(self, request_id: str) -> Path | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.get_request` | method | `src/jarvis_v2/runtime/file_actions.py:315-316` | def get_request(self, request_id: str) -> FileActionRequest | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.trash_manifest` | method | `src/jarvis_v2/runtime/file_actions.py:318-321` | def trash_manifest(self, request_id: str) -> dict[str, object] \| None | 1 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.audit` | method | `src/jarvis_v2/runtime/file_actions.py:323-330` | def audit(self, limit: int=100) -> list[dict[str, object]] | 6 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._insert_request` | method | `src/jarvis_v2/runtime/file_actions.py:332-345` | def _insert_request(self, action: str, identity: FileIdentity, reason: str, *, restore_target: str \| None=None) -> FileActionRequest | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._authorized` | method | `src/jarvis_v2/runtime/file_actions.py:347-353` | def _authorized(self, request_id: str, action: str) -> sqlite3.Row | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._row` | method | `src/jarvis_v2/runtime/file_actions.py:355-359` | def _row(self, request_id: str) -> sqlite3.Row | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._request_from_row` | method | `src/jarvis_v2/runtime/file_actions.py:362-367` | def _request_from_row(row: sqlite3.Row) -> FileActionRequest | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._identity` | method | `src/jarvis_v2/runtime/file_actions.py:370-371` | def _identity(row: sqlite3.Row) -> FileIdentity | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._request_id` | method | `src/jarvis_v2/runtime/file_actions.py:374-377` | def _request_id(value: object) -> str | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._reason` | method | `src/jarvis_v2/runtime/file_actions.py:380-385` | def _reason(value: object) -> str | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._capture_allowed_file` | method | `src/jarvis_v2/runtime/file_actions.py:387-402` | def _capture_allowed_file(self, target: Path) -> FileIdentity | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._validate_restore_target` | method | `src/jarvis_v2/runtime/file_actions.py:404-414` | def _validate_restore_target(self, target: Path) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._assert_identity` | method | `src/jarvis_v2/runtime/file_actions.py:416-423` | def _assert_identity(self, path: Path, expected: FileIdentity) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._assert_fd_identity` | method | `src/jarvis_v2/runtime/file_actions.py:426-431` | def _assert_fd_identity(fd: int, expected: FileIdentity) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._normalize_roots` | method | `src/jarvis_v2/runtime/file_actions.py:434-446` | def _normalize_roots(roots: tuple[Path, ...] \| list[Path]) -> tuple[Path, ...] | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._inside` | method | `src/jarvis_v2/runtime/file_actions.py:449-453` | def _inside(path: Path, roots: tuple[Path, ...]) -> bool | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._is_protected` | method | `src/jarvis_v2/runtime/file_actions.py:456-460` | def _is_protected(path: Path) -> bool | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._open_directory` | method | `src/jarvis_v2/runtime/file_actions.py:463-464` | def _open_directory(path: Path) -> int | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._checksum_at` | method | `src/jarvis_v2/runtime/file_actions.py:467-475` | def _checksum_at(directory_fd: int, name: str) -> str | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._checksum_path` | method | `src/jarvis_v2/runtime/file_actions.py:478-483` | def _checksum_path(cls, path: Path) -> str | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._rename_noreplace` | method | `src/jarvis_v2/runtime/file_actions.py:486-498` | def _rename_noreplace(cls, source_dir_fd: int, source_name: str, target_dir_fd: int, target_name: str) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._restore_move` | method | `src/jarvis_v2/runtime/file_actions.py:501-511` | def _restore_move(cls, source: Path, target: Path) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._audit_db` | method | `src/jarvis_v2/runtime/file_actions.py:513-518` | def _audit_db(self, row: sqlite3.Row \| dict[str, object], decision: str, result: str) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._append_log` | method | `src/jarvis_v2/runtime/file_actions.py:520-538` | def _append_log(self, request_id: str, action: str, event: str, original: Path, destination: Path) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService._write_all` | method | `src/jarvis_v2/runtime/file_actions.py:541-546` | def _write_all(fd: int, data: bytes) -> None | 0 | active |
| `jarvis_v2.runtime.file_actions.FileActionService.close` | method | `src/jarvis_v2/runtime/file_actions.py:548-550` | def close(self) -> None | 34 | active |
| `jarvis_v2.runtime.offline.OfflineChatServiceError` | class | `src/jarvis_v2/runtime/offline.py:16-17` | class OfflineChatServiceError(ValueError) | 0 | active |
| `jarvis_v2.runtime.offline.OfflineChatService` | class | `src/jarvis_v2/runtime/offline.py:23-141` | class OfflineChatService() | 1 | active |
| `jarvis_v2.runtime.offline.OfflineChatService.__init__` | method | `src/jarvis_v2/runtime/offline.py:26-57` | def __init__(self, chat: ChatService, available_models: set[str] \| frozenset[str], *, adapter: LocalAdapter \| None=None, fallback_model: str \| None=None, allow_fallback: bool=Fa | 5 | active |
| `jarvis_v2.runtime.offline.OfflineChatService.stream` | method | `src/jarvis_v2/runtime/offline.py:59-125` | async def stream(self, conversation_id: str, message: str, requested_model: str, *, cancel_event: Any=None, idempotency_key: str \| None=None) -> AsyncIterator[dict[str, Any]] | 5 | active |
| `jarvis_v2.runtime.offline.OfflineChatService.stream.provider` | function | `src/jarvis_v2/runtime/offline.py:105-106` | def provider(prompt: str) -> Any | 11 | active |
| `jarvis_v2.runtime.offline.OfflineChatService._paused` | method | `src/jarvis_v2/runtime/offline.py:128-141` | def _paused(requested_model: str, selected_model: str \| None, reason: str, message: str) -> dict[str, Any] | 0 | active |
| `jarvis_v2.runtime.qualification.HostQualificationError` | class | `src/jarvis_v2/runtime/qualification.py:21-22` | class HostQualificationError(ValueError) | 1 | active |
| `jarvis_v2.runtime.qualification._text` | function | `src/jarvis_v2/runtime/qualification.py:25-33` | def _text(value: str, label: str, maximum: int) -> str | 2 | active |
| `jarvis_v2.runtime.qualification.HostAcceptanceRecord` | class | `src/jarvis_v2/runtime/qualification.py:37-82` | class HostAcceptanceRecord() | 1 | active |
| `jarvis_v2.runtime.qualification.HostAcceptanceRecord.__post_init__` | method | `src/jarvis_v2/runtime/qualification.py:47-72` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.qualification.HostAcceptanceRecord.as_dict` | method | `src/jarvis_v2/runtime/qualification.py:74-82` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.qualification.HostQualificationReport` | class | `src/jarvis_v2/runtime/qualification.py:86-137` | class HostQualificationReport() | 0 | active |
| `jarvis_v2.runtime.qualification.HostQualificationReport.__post_init__` | method | `src/jarvis_v2/runtime/qualification.py:95-118` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.qualification.HostQualificationReport.all_passed` | method | `src/jarvis_v2/runtime/qualification.py:121-122` | def all_passed(self) -> bool | 1 | active |
| `jarvis_v2.runtime.qualification.HostQualificationReport.unresolved_gates` | method | `src/jarvis_v2/runtime/qualification.py:125-126` | def unresolved_gates(self) -> tuple[str, ...] | 1 | active |
| `jarvis_v2.runtime.qualification.HostQualificationReport.as_dict` | method | `src/jarvis_v2/runtime/qualification.py:128-137` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.qualification.build_host_qualification_report` | function | `src/jarvis_v2/runtime/qualification.py:140-156` | def build_host_qualification_report(host: str, platform: str, source_sha: str, checks: Iterable[HostAcceptanceRecord], *, captured_at: datetime \| None=None) -> HostQualificationRe | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderServiceError` | class | `src/jarvis_v2/runtime/reminders.py:19-20` | class ReminderServiceError(ValueError) | 1 | active |
| `jarvis_v2.runtime.reminders._now` | function | `src/jarvis_v2/runtime/reminders.py:23-27` | def _now(clock: Callable[[], datetime], value: datetime \| None=None) -> datetime | 0 | active |
| `jarvis_v2.runtime.reminders._zone` | function | `src/jarvis_v2/runtime/reminders.py:30-36` | def _zone(name: str) -> ZoneInfo | 0 | active |
| `jarvis_v2.runtime.reminders.NotificationPreferences` | class | `src/jarvis_v2/runtime/reminders.py:40-84` | class NotificationPreferences() | 1 | active |
| `jarvis_v2.runtime.reminders.NotificationPreferences.__post_init__` | method | `src/jarvis_v2/runtime/reminders.py:48-60` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.reminders.NotificationPreferences._time` | method | `src/jarvis_v2/runtime/reminders.py:63-68` | def _time(value: time \| None) -> time \| None | 0 | active |
| `jarvis_v2.runtime.reminders.NotificationPreferences.is_quiet` | method | `src/jarvis_v2/runtime/reminders.py:70-76` | def is_quiet(self, current: datetime) -> bool | 0 | active |
| `jarvis_v2.runtime.reminders.NotificationPreferences.as_dict` | method | `src/jarvis_v2/runtime/reminders.py:78-84` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.reminders.ReminderNotification` | class | `src/jarvis_v2/runtime/reminders.py:88-99` | class ReminderNotification() | 0 | active |
| `jarvis_v2.runtime.reminders.ReminderNotification.__post_init__` | method | `src/jarvis_v2/runtime/reminders.py:92-94` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.runtime.reminders.ReminderNotification.as_dict` | method | `src/jarvis_v2/runtime/reminders.py:96-99` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.reminders.ReminderService` | class | `src/jarvis_v2/runtime/reminders.py:102-269` | class ReminderService() | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderService.__init__` | method | `src/jarvis_v2/runtime/reminders.py:105-139` | def __init__(self, database: str \| Path \| sqlite3.Connection, *, clock: Callable[[], datetime] \| None=None) -> None | 5 | active |
| `jarvis_v2.runtime.reminders.ReminderService.__enter__` | method | `src/jarvis_v2/runtime/reminders.py:141-142` | def __enter__(self) -> 'ReminderService' | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderService.__exit__` | method | `src/jarvis_v2/runtime/reminders.py:144-145` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderService.preferences` | method | `src/jarvis_v2/runtime/reminders.py:147-164` | def preferences(self) -> NotificationPreferences | 2 | active |
| `jarvis_v2.runtime.reminders.ReminderService.set_preferences` | method | `src/jarvis_v2/runtime/reminders.py:166-188` | def set_preferences(self, *, enabled: bool=True, timezone_name: str='UTC', quiet_start: time \| None=None, quiet_end: time \| None=None) -> NotificationPreferences | 2 | active |
| `jarvis_v2.runtime.reminders.ReminderService.schedule` | method | `src/jarvis_v2/runtime/reminders.py:190-204` | def schedule(self, reminder_id: str, message: str, due_at: datetime \| str, *, timezone_name: str='UTC') -> Reminder | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderService.schedule_daily` | method | `src/jarvis_v2/runtime/reminders.py:208-224` | def schedule_daily(self, reminder_id: str, message: str, local_time: time, *, timezone_name: str, start_date: date \| None=None) -> Reminder | 2 | active |
| `jarvis_v2.runtime.reminders.ReminderService.due_notifications` | method | `src/jarvis_v2/runtime/reminders.py:228-240` | def due_notifications(self, now: datetime \| None=None, *, limit: int=100) -> tuple[ReminderNotification, ...] | 1 | active |
| `jarvis_v2.runtime.reminders.ReminderService.get` | method | `src/jarvis_v2/runtime/reminders.py:244-245` | def get(self, reminder_id: str) -> Reminder | 27 | active |
| `jarvis_v2.runtime.reminders.ReminderService.acknowledge` | method | `src/jarvis_v2/runtime/reminders.py:247-248` | def acknowledge(self, reminder_id: str) -> Reminder | 4 | active |
| `jarvis_v2.runtime.reminders.ReminderService.cancel` | method | `src/jarvis_v2/runtime/reminders.py:252-253` | def cancel(self, reminder_id: str) -> Reminder | 0 | active |
| `jarvis_v2.runtime.reminders.ReminderService.close` | method | `src/jarvis_v2/runtime/reminders.py:255-258` | def close(self) -> None | 34 | active |
| `jarvis_v2.runtime.reminders.ReminderService._backend` | method | `src/jarvis_v2/runtime/reminders.py:261-265` | def _backend(call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any | 0 | active |
| `jarvis_v2.runtime.reminders.ReminderService._format` | method | `src/jarvis_v2/runtime/reminders.py:268-269` | def _format(value: datetime) -> str | 0 | active |
| `jarvis_v2.runtime.security.RuntimeSecurityError` | class | `src/jarvis_v2/runtime/security.py:34-40` | class RuntimeSecurityError(ValueError) | 0 | active |
| `jarvis_v2.runtime.security.RuntimeSecurityError.__init__` | method | `src/jarvis_v2/runtime/security.py:37-40` | def __init__(self, code: str, status: int) -> None | 5 | active |
| `jarvis_v2.runtime.security.OwnerSession` | class | `src/jarvis_v2/runtime/security.py:44-58` | class OwnerSession() | 0 | active |
| `jarvis_v2.runtime.security.OwnerSession.as_dict` | method | `src/jarvis_v2/runtime/security.py:52-58` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.runtime.security._opaque` | function | `src/jarvis_v2/runtime/security.py:61-64` | def _opaque(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.security._authority` | function | `src/jarvis_v2/runtime/security.py:67-80` | def _authority(value: str, label: str) -> str | 0 | active |
| `jarvis_v2.runtime.security._origin` | function | `src/jarvis_v2/runtime/security.py:83-100` | def _origin(value: str, allowed: frozenset[str], label: str='origin') -> str | 0 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity` | class | `src/jarvis_v2/runtime/security.py:103-234` | class RuntimeSecurity() | 1 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.__init__` | method | `src/jarvis_v2/runtime/security.py:111-137` | def __init__(self, *, expected_host: str='127.0.0.1:8765', allowed_origins: Iterable[str] \| None=None, ttl_seconds: int=SESSION_TTL_SECONDS, clock=time.time) -> None | 5 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.response_headers` | method | `src/jarvis_v2/runtime/security.py:140-142` | def response_headers() -> dict[str, str] | 0 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.issue` | method | `src/jarvis_v2/runtime/security.py:144-156` | def issue(self, identity_id: str, *, now: float \| None=None) -> OwnerSession | 3 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.validate` | method | `src/jarvis_v2/runtime/security.py:158-197` | def validate(self, *, session_id: str, identity_id: str, method: str, host: str, origin: str \| None=None, csrf_token: str \| None=None, now: float \| None=None) -> OwnerSession | 2 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.rotate` | method | `src/jarvis_v2/runtime/security.py:199-220` | def rotate(self, *, session_id: str, identity_id: str, method: str, host: str, origin: str \| None=None, csrf_token: str \| None=None, now: float \| None=None) -> OwnerSession | 2 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity.revoke` | method | `src/jarvis_v2/runtime/security.py:222-225` | def revoke(self, session_id: str) -> None | 5 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity._expired` | method | `src/jarvis_v2/runtime/security.py:227-228` | def _expired(self, session: OwnerSession, now: float \| None) -> bool | 0 | active |
| `jarvis_v2.runtime.security.RuntimeSecurity._now` | method | `src/jarvis_v2/runtime/security.py:230-234` | def _now(self, now: float \| None) -> float | 0 | active |
| `jarvis_v2.runtime.service.RuntimeServiceError` | class | `src/jarvis_v2/runtime/service.py:28-29` | class RuntimeServiceError(ValueError) | 0 | active |
| `jarvis_v2.runtime.service.RuntimeResponse` | class | `src/jarvis_v2/runtime/service.py:33-41` | class RuntimeResponse() | 0 | active |
| `jarvis_v2.runtime.service.RuntimeResponse.as_dict` | method | `src/jarvis_v2/runtime/service.py:40-41` | def as_dict(self) -> dict[str, Any] | 18 | active |
| `jarvis_v2.runtime.service.RuntimeService` | class | `src/jarvis_v2/runtime/service.py:44-283` | class RuntimeService() | 3 | active |
| `jarvis_v2.runtime.service.RuntimeService.__init__` | method | `src/jarvis_v2/runtime/service.py:47-65` | def __init__(self, registry: ModuleRegistry, authorization: AuthorizationServer, dispatch: DispatchStore, events: EventBus, security: RuntimeSecurity \| None=None) -> None | 5 | active |
| `jarvis_v2.runtime.service.RuntimeService.handle` | method | `src/jarvis_v2/runtime/service.py:67-112` | def handle(self, request: Mapping[str, Any]) -> RuntimeResponse | 3 | active |
| `jarvis_v2.runtime.service.RuntimeService.issue_owner_session` | method | `src/jarvis_v2/runtime/service.py:114-119` | def issue_owner_session(self, identity_id: str) -> dict[str, object] | 1 | active |
| `jarvis_v2.runtime.service.RuntimeService.rotate_owner_session` | method | `src/jarvis_v2/runtime/service.py:121-137` | def rotate_owner_session(self, request: Mapping[str, Any]) -> dict[str, object] | 1 | active |
| `jarvis_v2.runtime.service.RuntimeService.revoke_owner_session` | method | `src/jarvis_v2/runtime/service.py:139-140` | def revoke_owner_session(self, session_id: str) -> None | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService.close` | method | `src/jarvis_v2/runtime/service.py:142-144` | def close(self) -> None | 34 | active |
| `jarvis_v2.runtime.service.RuntimeService._create_task` | method | `src/jarvis_v2/runtime/service.py:146-181` | def _create_task(self, request: Mapping[str, Any]) -> RuntimeResponse | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._events` | method | `src/jarvis_v2/runtime/service.py:183-196` | def _events(self, request: Mapping[str, Any]) -> RuntimeResponse | 1 | active |
| `jarvis_v2.runtime.service.RuntimeService._claim` | method | `src/jarvis_v2/runtime/service.py:198-207` | def _claim(self, request: Mapping[str, Any], dispatch_id: str) -> RuntimeResponse | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._acknowledge` | method | `src/jarvis_v2/runtime/service.py:209-222` | def _acknowledge(self, request: Mapping[str, Any], dispatch_id: str) -> RuntimeResponse | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._authorized` | method | `src/jarvis_v2/runtime/service.py:224-230` | def _authorized(self, identity_id: str \| None, scope: str \| None, required: str) -> bool | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._auth_failure` | method | `src/jarvis_v2/runtime/service.py:233-234` | def _auth_failure(identity_id: str \| None) -> RuntimeResponse | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._has_owner_transport` | method | `src/jarvis_v2/runtime/service.py:237-238` | def _has_owner_transport(request: Mapping[str, Any]) -> bool | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._request_identity` | method | `src/jarvis_v2/runtime/service.py:241-250` | def _request_identity(request: Mapping[str, Any]) -> tuple[str, str, str, str] | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._body` | method | `src/jarvis_v2/runtime/service.py:253-257` | def _body(request: Mapping[str, Any], allowed: set[str]) -> Mapping[str, Any] | 1 | active |
| `jarvis_v2.runtime.service.RuntimeService._scopes` | method | `src/jarvis_v2/runtime/service.py:260-266` | def _scopes(value: Any) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.runtime.service.RuntimeService._event_dict` | method | `src/jarvis_v2/runtime/service.py:269-283` | def _event_dict(event: Any) -> dict[str, Any] | 0 | active |
| `jarvis_v2.runtime.speech.SpeechServiceError` | class | `src/jarvis_v2/runtime/speech.py:18-19` | class SpeechServiceError(ValueError) | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService` | class | `src/jarvis_v2/runtime/speech.py:25-149` | class SpeechService() | 1 | active |
| `jarvis_v2.runtime.speech.SpeechService.__init__` | method | `src/jarvis_v2/runtime/speech.py:28-32` | def __init__(self, adapter: SpeechAdapter, *, default_voice: str='en_GB') -> None | 5 | active |
| `jarvis_v2.runtime.speech.SpeechService.stream` | method | `src/jarvis_v2/runtime/speech.py:34-90` | async def stream(self, text: str, *, voice: str \| None=None, cancel_event: Any=None) -> AsyncIterator[dict[str, Any]] | 5 | active |
| `jarvis_v2.runtime.speech.SpeechService._chunks` | method | `src/jarvis_v2/runtime/speech.py:93-105` | async def _chunks(produced: Any) -> AsyncIterator[Any] | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService._text` | method | `src/jarvis_v2/runtime/speech.py:108-111` | def _text(value: str) -> str | 2 | active |
| `jarvis_v2.runtime.speech.SpeechService._voice` | method | `src/jarvis_v2/runtime/speech.py:114-117` | def _voice(value: str) -> str | 1 | active |
| `jarvis_v2.runtime.speech.SpeechService._audio_chunk` | method | `src/jarvis_v2/runtime/speech.py:120-126` | def _audio_chunk(value: Any) -> bytes | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService._stop_adapter` | method | `src/jarvis_v2/runtime/speech.py:128-137` | async def _stop_adapter(self) -> None | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService._cancelled` | method | `src/jarvis_v2/runtime/speech.py:140-141` | def _cancelled(value: Any) -> bool | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService._cancelled_event` | method | `src/jarvis_v2/runtime/speech.py:144-145` | def _cancelled_event() -> dict[str, Any] | 0 | active |
| `jarvis_v2.runtime.speech.SpeechService._error` | method | `src/jarvis_v2/runtime/speech.py:148-149` | def _error(code: str, message: str) -> dict[str, Any] | 0 | active |
| `jarvis_v2.sda.handoff.HandoffEvidence` | class | `src/jarvis_v2/sda/handoff.py:21-48` | class HandoffEvidence() | 2 | active |
| `jarvis_v2.sda.handoff.HandoffEvidence.report` | method | `src/jarvis_v2/sda/handoff.py:31-48` | def report(self) -> dict | 14 | active |
| `jarvis_v2.system_inventory.InventoryError` | class | `src/jarvis_v2/system_inventory.py:16-17` | class InventoryError(RuntimeError) | 0 | active |
| `jarvis_v2.system_inventory._command` | function | `src/jarvis_v2/system_inventory.py:40-51` | def _command(args: list[str]) -> tuple[int, str, str] | 0 | active |
| `jarvis_v2.system_inventory._command_summary` | function | `src/jarvis_v2/system_inventory.py:54-61` | def _command_summary(args: list[str], runner: CommandRunner) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory._optional_command_summary` | function | `src/jarvis_v2/system_inventory.py:64-71` | def _optional_command_summary(args: list[str], runner: CommandRunner) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory._metadata` | function | `src/jarvis_v2/system_inventory.py:74-84` | def _metadata(path: Path, info: os.stat_result, kind: str) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory.scan_filesystem` | function | `src/jarvis_v2/system_inventory.py:87-159` | def scan_filesystem(root: Path=Path('/'), *, max_entries: int=10000) -> dict[str, Any] | 1 | active |
| `jarvis_v2.system_inventory._hardware` | function | `src/jarvis_v2/system_inventory.py:162-170` | def _hardware(runner: CommandRunner) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory._software` | function | `src/jarvis_v2/system_inventory.py:173-183` | def _software(runner: CommandRunner) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory._runtime_capabilities` | function | `src/jarvis_v2/system_inventory.py:186-204` | def _runtime_capabilities(runner: CommandRunner) -> dict[str, Any] | 0 | active |
| `jarvis_v2.system_inventory.collect_inventory` | function | `src/jarvis_v2/system_inventory.py:207-238` | def collect_inventory(*, root: Path=Path('/'), max_entries: int=10000, runner: CommandRunner=_command) -> dict[str, Any] | 1 | active |
| `jarvis_v2.system_inventory.inventory_digest` | function | `src/jarvis_v2/system_inventory.py:241-246` | def inventory_digest(inventory: Mapping[str, Any]) -> str | 1 | active |
| `jarvis_v2.system_inventory.compare_inventories` | function | `src/jarvis_v2/system_inventory.py:249-271` | def compare_inventories(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any] | 1 | active |
| `jarvis_v2.system_inventory.write_inventory` | function | `src/jarvis_v2/system_inventory.py:274-280` | def write_inventory(path: Path, inventory: Mapping[str, Any]) -> None | 0 | active |
| `jarvis_v2.tws.__init__.TWSStoreError` | class | `src/jarvis_v2/tws/__init__.py:27-28` | class TWSStoreError(ValueError) | 7 | active |
| `jarvis_v2.tws.__init__._identifier` | function | `src/jarvis_v2/tws/__init__.py:31-34` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.tws.__init__._text` | function | `src/jarvis_v2/tws/__init__.py:37-45` | def _text(value: object, label: str) -> str | 2 | active |
| `jarvis_v2.tws.__init__._now` | function | `src/jarvis_v2/tws/__init__.py:48-51` | def _now() -> str | 0 | active |
| `jarvis_v2.tws.__init__._evidence` | function | `src/jarvis_v2/tws/__init__.py:54-66` | def _evidence(value: object) -> tuple[str, str] | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore` | class | `src/jarvis_v2/tws/__init__.py:287-1184` | class QuestStore() | 8 | active |
| `jarvis_v2.tws.__init__.QuestStore.__init__` | method | `src/jarvis_v2/tws/__init__.py:290-293` | def __init__(self, database: str \| Path) -> None | 5 | active |
| `jarvis_v2.tws.__init__.QuestStore.__enter__` | method | `src/jarvis_v2/tws/__init__.py:295-296` | def __enter__(self) -> 'QuestStore' | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.__exit__` | method | `src/jarvis_v2/tws/__init__.py:298-299` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.close` | method | `src/jarvis_v2/tws/__init__.py:301-302` | def close(self) -> None | 34 | active |
| `jarvis_v2.tws.__init__.QuestStore.schema_version` | method | `src/jarvis_v2/tws/__init__.py:305-309` | def schema_version(self) -> int | 10 | active |
| `jarvis_v2.tws.__init__.QuestStore.applied_migrations` | method | `src/jarvis_v2/tws/__init__.py:311-315` | def applied_migrations(self) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore._one` | method | `src/jarvis_v2/tws/__init__.py:317-319` | def _one(self, query: str, values: tuple[object, ...]) -> dict[str, Any] \| None | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.add_wing` | method | `src/jarvis_v2/tws/__init__.py:321-336` | def add_wing(self, wing_id: str, name: str, *, state: str='active') -> dict[str, Any] | 7 | active |
| `jarvis_v2.tws.__init__.QuestStore.create_quest` | method | `src/jarvis_v2/tws/__init__.py:338-373` | def create_quest(self, quest_id: str, wing_id: str, title: str, *, kind: str='skill', cadence: str='once') -> dict[str, Any] | 6 | active |
| `jarvis_v2.tws.__init__.QuestStore.import_tasks_as_quests` | method | `src/jarvis_v2/tws/__init__.py:375-492` | def import_tasks_as_quests(self, tasks: Sequence[Mapping[str, Any]], *, consent_id: str, consent_scope: str) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.propose_task_quests` | method | `src/jarvis_v2/tws/__init__.py:494-504` | def propose_task_quests(self, tasks: Sequence[Mapping[str, Any]], *, consent_id: str, consent_scope: str) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.task_quest_proposals` | method | `src/jarvis_v2/tws/__init__.py:506-516` | def task_quest_proposals(self, source_task_id: str \| None=None) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.transition_quest` | method | `src/jarvis_v2/tws/__init__.py:518-541` | def transition_quest(self, quest_id: str, state: str) -> dict[str, Any] | 5 | active |
| `jarvis_v2.tws.__init__.QuestStore.catalog` | method | `src/jarvis_v2/tws/__init__.py:543-566` | def catalog(self, *, kind: str \| None=None, state: str \| None=None) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.append_proof` | method | `src/jarvis_v2/tws/__init__.py:568-601` | def append_proof(self, proof_id: str, quest_id: str, evidence: Mapping[str, object], *, privacy_scope: str='internal_metadata') -> dict[str, Any] | 5 | active |
| `jarvis_v2.tws.__init__.QuestStore.review_proof` | method | `src/jarvis_v2/tws/__init__.py:603-621` | def review_proof(self, proof_id: str, decision: str, reviewer_id: str) -> dict[str, Any] | 4 | active |
| `jarvis_v2.tws.__init__.QuestStore.define_realm` | method | `src/jarvis_v2/tws/__init__.py:623-659` | def define_realm(self, realm_id: str, name: str, *, min_xp: int=0, prerequisites: tuple[str, ...]=()) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.xp_total` | method | `src/jarvis_v2/tws/__init__.py:661-666` | def xp_total(self, profile_id: str) -> int | 3 | active |
| `jarvis_v2.tws.__init__.QuestStore.award_xp` | method | `src/jarvis_v2/tws/__init__.py:668-727` | def award_xp(self, profile_id: str, reward_id: str, quest_id: str, proof_id: str, xp: int, sync_id: str) -> dict[str, Any] | 3 | active |
| `jarvis_v2.tws.__init__.QuestStore.unlock_realm` | method | `src/jarvis_v2/tws/__init__.py:729-756` | def unlock_realm(self, profile_id: str, realm_id: str) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.record_achievement` | method | `src/jarvis_v2/tws/__init__.py:758-831` | def record_achievement(self, profile_id: str, achievement_id: str, skill_id: str, pattern: str, quest_id: str, proof_id: str, sync_id: str) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.achievements` | method | `src/jarvis_v2/tws/__init__.py:833-852` | def achievements(self, profile_id: str, *, skill_id: str \| None=None) -> list[dict[str, Any]] | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.cultivation_progress` | method | `src/jarvis_v2/tws/__init__.py:854-874` | def cultivation_progress(self, profile_id: str, skill_id: str) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.adapt_skill` | method | `src/jarvis_v2/tws/__init__.py:876-943` | def adapt_skill(self, profile_id: str, adaptation_id: str, skill_id: str, *, pattern: str \| None=None) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.set_aurelia_state` | method | `src/jarvis_v2/tws/__init__.py:945-983` | def set_aurelia_state(self, profile_id: str, *, personality: str='aurelia', mood: str='calm', narrative_node: str='sanctuary') -> dict[str, Any] | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.record_aurelia_turn` | method | `src/jarvis_v2/tws/__init__.py:985-1036` | def record_aurelia_turn(self, profile_id: str, turn_id: str, line: str, *, personality: str='aurelia', mood: str='calm', narrative_node: str='sanctuary') -> dict[str, Any] | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.aurelia_state` | method | `src/jarvis_v2/tws/__init__.py:1038-1042` | def aurelia_state(self, profile_id: str) -> dict[str, Any] \| None | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.aurelia_turns` | method | `src/jarvis_v2/tws/__init__.py:1044-1053` | def aurelia_turns(self, profile_id: str) -> list[dict[str, Any]] | 0 | active |
| `jarvis_v2.tws.__init__.QuestStore.set_preferences` | method | `src/jarvis_v2/tws/__init__.py:1055-1097` | def set_preferences(self, profile_id: str, *, immersive_mode: str \| None=None, reduced_motion: str \| None=None, fallback_mode: str \| None=None) -> dict[str, Any] | 2 | active |
| `jarvis_v2.tws.__init__.QuestStore.preferences` | method | `src/jarvis_v2/tws/__init__.py:1099-1103` | def preferences(self, profile_id: str) -> dict[str, Any] \| None | 2 | active |
| `jarvis_v2.tws.__init__.QuestStore.set_onboarding` | method | `src/jarvis_v2/tws/__init__.py:1105-1124` | def set_onboarding(self, profile_id: str, state: str) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.onboarding` | method | `src/jarvis_v2/tws/__init__.py:1126-1127` | def onboarding(self, profile_id: str) -> dict[str, Any] \| None | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.wings` | method | `src/jarvis_v2/tws/__init__.py:1129-1137` | def wings(self) -> list[dict[str, Any]] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.sanctuary_snapshot` | method | `src/jarvis_v2/tws/__init__.py:1139-1169` | def sanctuary_snapshot(self, profile_id: str \| None=None) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.QuestStore.wing` | method | `src/jarvis_v2/tws/__init__.py:1171-1172` | def wing(self, wing_id: str) -> dict[str, Any] \| None | 7 | active |
| `jarvis_v2.tws.__init__.QuestStore.quest` | method | `src/jarvis_v2/tws/__init__.py:1174-1175` | def quest(self, quest_id: str) -> dict[str, Any] \| None | 8 | active |
| `jarvis_v2.tws.__init__.QuestStore.proofs` | method | `src/jarvis_v2/tws/__init__.py:1177-1184` | def proofs(self, quest_id: str) -> list[dict[str, Any]] | 2 | active |
| `jarvis_v2.tws.__init__.AureliaDialogue` | class | `src/jarvis_v2/tws/__init__.py:1187-1216` | class AureliaDialogue() | 1 | active |
| `jarvis_v2.tws.__init__.AureliaDialogue.__init__` | method | `src/jarvis_v2/tws/__init__.py:1190-1191` | def __init__(self, store: QuestStore) -> None | 5 | active |
| `jarvis_v2.tws.__init__.AureliaDialogue.record_turn` | method | `src/jarvis_v2/tws/__init__.py:1193-1210` | def record_turn(self, profile_id: str, turn_id: str, line: str, *, personality: str='aurelia', mood: str='calm', narrative_node: str='sanctuary') -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.__init__.AureliaDialogue.state` | method | `src/jarvis_v2/tws/__init__.py:1212-1213` | def state(self, profile_id: str) -> dict[str, Any] \| None | 56 | active |
| `jarvis_v2.tws.__init__.AureliaDialogue.turns` | method | `src/jarvis_v2/tws/__init__.py:1215-1216` | def turns(self, profile_id: str) -> list[dict[str, Any]] | 4 | active |
| `jarvis_v2.tws.aurelia_model.ModelValidationError` | class | `src/jarvis_v2/tws/aurelia_model.py:19-20` | class ModelValidationError(ValueError) | 2 | active |
| `jarvis_v2.tws.aurelia_model._identifier` | function | `src/jarvis_v2/tws/aurelia_model.py:23-26` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.tws.aurelia_model._positive_int` | function | `src/jarvis_v2/tws/aurelia_model.py:29-32` | def _positive_int(value: object, label: str, maximum: int) -> int | 0 | active |
| `jarvis_v2.tws.aurelia_model._number` | function | `src/jarvis_v2/tws/aurelia_model.py:35-38` | def _number(value: object, label: str) -> float | 0 | active |
| `jarvis_v2.tws.aurelia_model._validate_payload` | function | `src/jarvis_v2/tws/aurelia_model.py:41-166` | def _validate_payload(payload: object) -> dict[str, Any] | 0 | active |
| `jarvis_v2.tws.aurelia_model.build_portable_model` | function | `src/jarvis_v2/tws/aurelia_model.py:169-182` | def build_portable_model(spec: Mapping[str, object]) -> bytes | 1 | active |
| `jarvis_v2.tws.aurelia_model.validate_portable_model` | function | `src/jarvis_v2/tws/aurelia_model.py:185-205` | def validate_portable_model(package: bytes \| bytearray) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.aurelia_model.validate_visual_qa_manifest` | function | `src/jarvis_v2/tws/aurelia_model.py:208-260` | def validate_visual_qa_manifest(manifest: Mapping[str, object]) -> dict[str, Any] | 1 | active |
| `jarvis_v2.tws.aurelia_model.default_aurelia_spec` | function | `src/jarvis_v2/tws/aurelia_model.py:263-291` | def default_aurelia_spec() -> dict[str, Any] | 1 | active |
| `jarvis_v2.wic.__init__.WICError` | class | `src/jarvis_v2/wic/__init__.py:35-36` | class WICError(ValueError) | 8 | active |
| `jarvis_v2.wic.__init__._identifier` | function | `src/jarvis_v2/wic/__init__.py:39-42` | def _identifier(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.wic.__init__._text` | function | `src/jarvis_v2/wic/__init__.py:45-53` | def _text(value: object, label: str, maximum: int, *, empty: bool=False) -> str | 2 | active |
| `jarvis_v2.wic.__init__._string` | function | `src/jarvis_v2/wic/__init__.py:56-59` | def _string(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.wic.__init__._optional_string` | function | `src/jarvis_v2/wic/__init__.py:62-65` | def _optional_string(value: object, label: str) -> str \| None | 0 | active |
| `jarvis_v2.wic.__init__._categories` | function | `src/jarvis_v2/wic/__init__.py:68-79` | def _categories(values: Iterable[str]) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.wic.__init__._url` | function | `src/jarvis_v2/wic/__init__.py:82-99` | def _url(value: object, label: str) -> str | 0 | active |
| `jarvis_v2.wic.__init__._timestamp` | function | `src/jarvis_v2/wic/__init__.py:102-106` | def _timestamp(clock: Callable[[], datetime]) -> str | 0 | active |
| `jarvis_v2.wic.__init__._stored_timestamp` | function | `src/jarvis_v2/wic/__init__.py:109-119` | def _stored_timestamp(value: object, label: str, *, optional: bool=False) -> str \| None | 0 | active |
| `jarvis_v2.wic.__init__.normalize_url` | function | `src/jarvis_v2/wic/__init__.py:122-135` | def normalize_url(value: str) -> str | 1 | active |
| `jarvis_v2.wic.__init__.SourceObservation` | class | `src/jarvis_v2/wic/__init__.py:139-199` | class SourceObservation() | 3 | active |
| `jarvis_v2.wic.__init__.SourceObservation.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:151-159` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.SourceObservation.as_dict` | method | `src/jarvis_v2/wic/__init__.py:161-171` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.SourceObservation.from_dict` | method | `src/jarvis_v2/wic/__init__.py:174-199` | def from_dict(cls, data: Mapping[str, object]) -> 'SourceObservation' | 3 | active |
| `jarvis_v2.wic.__init__.IngestionResult` | class | `src/jarvis_v2/wic/__init__.py:203-232` | class IngestionResult() | 1 | active |
| `jarvis_v2.wic.__init__.IngestionResult.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:212-223` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.IngestionResult.as_dict` | method | `src/jarvis_v2/wic/__init__.py:225-232` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.SourceHealth` | class | `src/jarvis_v2/wic/__init__.py:236-261` | class SourceHealth() | 1 | active |
| `jarvis_v2.wic.__init__.SourceHealth.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:245-252` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.SourceHealth.as_dict` | method | `src/jarvis_v2/wic/__init__.py:254-261` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.SourceStore` | class | `src/jarvis_v2/wic/__init__.py:264-427` | class SourceStore() | 1 | active |
| `jarvis_v2.wic.__init__.SourceStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:267-299` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.SourceStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:301-302` | def __enter__(self) -> 'SourceStore' | 1 | active |
| `jarvis_v2.wic.__init__.SourceStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:304-305` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.SourceStore.save` | method | `src/jarvis_v2/wic/__init__.py:307-328` | def save(self, observation: SourceObservation) -> bool | 5 | active |
| `jarvis_v2.wic.__init__.SourceStore.observations` | method | `src/jarvis_v2/wic/__init__.py:330-348` | def observations(self, source_id: str \| None=None) -> tuple[SourceObservation, ...] | 1 | active |
| `jarvis_v2.wic.__init__.SourceStore.latest` | method | `src/jarvis_v2/wic/__init__.py:350-361` | def latest(self, article_url: str) -> SourceObservation \| None | 10 | active |
| `jarvis_v2.wic.__init__.SourceStore.record_health` | method | `src/jarvis_v2/wic/__init__.py:363-395` | def record_health(self, source_id: str, attempted_at: str, *, success: bool, failure: str \| None=None) -> SourceHealth | 0 | active |
| `jarvis_v2.wic.__init__.SourceStore.health` | method | `src/jarvis_v2/wic/__init__.py:397-423` | def health(self, source_id: str, *, now: str \| None=None, stale_after_seconds: int=DEFAULT_STALE_AFTER_SECONDS) -> SourceHealth | 18 | active |
| `jarvis_v2.wic.__init__.SourceStore.close` | method | `src/jarvis_v2/wic/__init__.py:425-427` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.StoryCluster` | class | `src/jarvis_v2/wic/__init__.py:431-469` | class StoryCluster() | 0 | active |
| `jarvis_v2.wic.__init__.StoryCluster.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:441-459` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.StoryCluster.as_dict` | method | `src/jarvis_v2/wic/__init__.py:461-469` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore` | class | `src/jarvis_v2/wic/__init__.py:472-578` | class StoryClusterStore() | 2 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:475-500` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:502-503` | def __enter__(self) -> 'StoryClusterStore' | 1 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:505-506` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.add` | method | `src/jarvis_v2/wic/__init__.py:508-544` | def add(self, cluster_key: str, observations: Iterable[SourceObservation]) -> StoryCluster | 28 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.get` | method | `src/jarvis_v2/wic/__init__.py:546-566` | def get(self, cluster_key: str) -> StoryCluster \| None | 27 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.clusters` | method | `src/jarvis_v2/wic/__init__.py:568-574` | def clusters(self) -> tuple[StoryCluster, ...] | 0 | active |
| `jarvis_v2.wic.__init__.StoryClusterStore.close` | method | `src/jarvis_v2/wic/__init__.py:576-578` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.StoryClusterer` | class | `src/jarvis_v2/wic/__init__.py:581-605` | class StoryClusterer() | 2 | active |
| `jarvis_v2.wic.__init__.StoryClusterer.__init__` | method | `src/jarvis_v2/wic/__init__.py:584-587` | def __init__(self, store: StoryClusterStore) | 5 | active |
| `jarvis_v2.wic.__init__.StoryClusterer.cluster` | method | `src/jarvis_v2/wic/__init__.py:589-605` | def cluster(self, observations: Iterable[SourceObservation], *, incident_key: str \| None=None) -> StoryCluster | 2 | active |
| `jarvis_v2.wic.__init__.ClaimRecord` | class | `src/jarvis_v2/wic/__init__.py:609-690` | class ClaimRecord() | 0 | active |
| `jarvis_v2.wic.__init__.ClaimRecord.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:623-646` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.ClaimRecord.as_dict` | method | `src/jarvis_v2/wic/__init__.py:648-660` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.ClaimRecord.from_dict` | method | `src/jarvis_v2/wic/__init__.py:663-690` | def from_dict(cls, data: Mapping[str, object]) -> 'ClaimRecord' | 3 | active |
| `jarvis_v2.wic.__init__.ClaimLedger` | class | `src/jarvis_v2/wic/__init__.py:693-866` | class ClaimLedger() | 1 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.__init__` | method | `src/jarvis_v2/wic/__init__.py:696-716` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.__enter__` | method | `src/jarvis_v2/wic/__init__.py:718-719` | def __enter__(self) -> 'ClaimLedger' | 1 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.__exit__` | method | `src/jarvis_v2/wic/__init__.py:721-722` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.create` | method | `src/jarvis_v2/wic/__init__.py:724-737` | def create(self, claim_id: str, cluster: StoryCluster, statement_digest: str, recorded_at: str, confidence: float \| None=None) -> ClaimRecord | 8 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.corroborate` | method | `src/jarvis_v2/wic/__init__.py:739-756` | def corroborate(self, claim_id: str, cluster: StoryCluster, recorded_at: str, confidence: float \| None) -> ClaimRecord | 1 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.verify` | method | `src/jarvis_v2/wic/__init__.py:758-771` | def verify(self, claim_id: str, recorded_at: str) -> ClaimRecord | 4 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.retract` | method | `src/jarvis_v2/wic/__init__.py:773-784` | def retract(self, claim_id: str, reason: str, recorded_at: str) -> ClaimRecord | 1 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.correct` | method | `src/jarvis_v2/wic/__init__.py:786-800` | def correct(self, claim_id: str, cluster: StoryCluster, statement_digest: str, reason: str, recorded_at: str, confidence: float \| None=None) -> ClaimRecord | 3 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.get` | method | `src/jarvis_v2/wic/__init__.py:802-810` | def get(self, claim_id: str) -> ClaimRecord \| None | 27 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.history` | method | `src/jarvis_v2/wic/__init__.py:812-821` | def history(self, claim_id: str) -> tuple[ClaimRecord, ...] | 12 | active |
| `jarvis_v2.wic.__init__.ClaimLedger._insert_new` | method | `src/jarvis_v2/wic/__init__.py:823-839` | def _insert_new(self, record: ClaimRecord) -> ClaimRecord | 0 | active |
| `jarvis_v2.wic.__init__.ClaimLedger._append` | method | `src/jarvis_v2/wic/__init__.py:841-855` | def _append(self, record: ClaimRecord) -> ClaimRecord | 0 | active |
| `jarvis_v2.wic.__init__.ClaimLedger._payload` | method | `src/jarvis_v2/wic/__init__.py:858-862` | def _payload(record: ClaimRecord) -> str | 0 | active |
| `jarvis_v2.wic.__init__.ClaimLedger.close` | method | `src/jarvis_v2/wic/__init__.py:864-866` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.CategoryAssignment` | class | `src/jarvis_v2/wic/__init__.py:870-918` | class CategoryAssignment() | 0 | active |
| `jarvis_v2.wic.__init__.CategoryAssignment.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:880-890` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.CategoryAssignment.as_dict` | method | `src/jarvis_v2/wic/__init__.py:892-900` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.CategoryAssignment.from_dict` | method | `src/jarvis_v2/wic/__init__.py:903-918` | def from_dict(cls, data: Mapping[str, object]) -> 'CategoryAssignment' | 3 | active |
| `jarvis_v2.wic.__init__.CategoryStore` | class | `src/jarvis_v2/wic/__init__.py:921-1055` | class CategoryStore() | 1 | active |
| `jarvis_v2.wic.__init__.CategoryStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:924-947` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.CategoryStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:949-950` | def __enter__(self) -> 'CategoryStore' | 1 | active |
| `jarvis_v2.wic.__init__.CategoryStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:952-953` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.CategoryStore.assign` | method | `src/jarvis_v2/wic/__init__.py:955-959` | def assign(self, cluster_id: str, categories: Iterable[str], recorded_at: str) -> CategoryAssignment | 4 | active |
| `jarvis_v2.wic.__init__.CategoryStore.correct` | method | `src/jarvis_v2/wic/__init__.py:961-972` | def correct(self, cluster_id: str, categories: Iterable[str], reason: str, recorded_at: str) -> CategoryAssignment | 3 | active |
| `jarvis_v2.wic.__init__.CategoryStore.get` | method | `src/jarvis_v2/wic/__init__.py:974-985` | def get(self, cluster_id: str) -> CategoryAssignment \| None | 27 | active |
| `jarvis_v2.wic.__init__.CategoryStore.search` | method | `src/jarvis_v2/wic/__init__.py:987-999` | def search(self, category: str) -> tuple[CategoryAssignment, ...] | 9 | active |
| `jarvis_v2.wic.__init__.CategoryStore.history` | method | `src/jarvis_v2/wic/__init__.py:1001-1010` | def history(self, cluster_id: str) -> tuple[CategoryAssignment, ...] | 12 | active |
| `jarvis_v2.wic.__init__.CategoryStore._insert_new` | method | `src/jarvis_v2/wic/__init__.py:1012-1028` | def _insert_new(self, record: CategoryAssignment) -> CategoryAssignment | 0 | active |
| `jarvis_v2.wic.__init__.CategoryStore._append` | method | `src/jarvis_v2/wic/__init__.py:1030-1044` | def _append(self, record: CategoryAssignment) -> CategoryAssignment | 0 | active |
| `jarvis_v2.wic.__init__.CategoryStore._payload` | method | `src/jarvis_v2/wic/__init__.py:1047-1051` | def _payload(record: CategoryAssignment) -> str | 0 | active |
| `jarvis_v2.wic.__init__.CategoryStore.close` | method | `src/jarvis_v2/wic/__init__.py:1053-1055` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.SummarySegment` | class | `src/jarvis_v2/wic/__init__.py:1063-1107` | class SummarySegment() | 1 | active |
| `jarvis_v2.wic.__init__.SummarySegment.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1073-1083` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.SummarySegment.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1085-1093` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.SummarySegment.from_dict` | method | `src/jarvis_v2/wic/__init__.py:1096-1107` | def from_dict(cls, data: Mapping[str, object]) -> 'SummarySegment' | 3 | active |
| `jarvis_v2.wic.__init__.SituationSummary` | class | `src/jarvis_v2/wic/__init__.py:1111-1170` | class SituationSummary() | 0 | active |
| `jarvis_v2.wic.__init__.SituationSummary.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1122-1140` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.SituationSummary.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1142-1151` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.SituationSummary.from_dict` | method | `src/jarvis_v2/wic/__init__.py:1154-1170` | def from_dict(cls, data: Mapping[str, object]) -> 'SituationSummary' | 3 | active |
| `jarvis_v2.wic.__init__.CitedSummaryComposer` | class | `src/jarvis_v2/wic/__init__.py:1173-1200` | class CitedSummaryComposer() | 1 | active |
| `jarvis_v2.wic.__init__.CitedSummaryComposer.compose` | method | `src/jarvis_v2/wic/__init__.py:1176-1200` | def compose(self, summary_id: str, segments: Iterable[SummarySegment], created_at: str, *, freshness: str='dated') -> SituationSummary | 1 | active |
| `jarvis_v2.wic.__init__.SummaryStore` | class | `src/jarvis_v2/wic/__init__.py:1203-1254` | class SummaryStore() | 1 | active |
| `jarvis_v2.wic.__init__.SummaryStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:1206-1218` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.SummaryStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:1220-1221` | def __enter__(self) -> 'SummaryStore' | 1 | active |
| `jarvis_v2.wic.__init__.SummaryStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:1223-1224` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.SummaryStore.save` | method | `src/jarvis_v2/wic/__init__.py:1226-1240` | def save(self, summary: SituationSummary) -> bool | 5 | active |
| `jarvis_v2.wic.__init__.SummaryStore.get` | method | `src/jarvis_v2/wic/__init__.py:1242-1250` | def get(self, summary_id: str) -> SituationSummary \| None | 27 | active |
| `jarvis_v2.wic.__init__.SummaryStore.close` | method | `src/jarvis_v2/wic/__init__.py:1252-1254` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__._watchlist_values` | function | `src/jarvis_v2/wic/__init__.py:1257-1269` | def _watchlist_values(values: Iterable[str], label: str) -> tuple[str, ...] | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistPreferences` | class | `src/jarvis_v2/wic/__init__.py:1273-1322` | class WatchlistPreferences() | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistPreferences.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1283-1293` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistPreferences.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1295-1303` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.WatchlistPreferences.from_dict` | method | `src/jarvis_v2/wic/__init__.py:1306-1322` | def from_dict(cls, data: Mapping[str, object]) -> 'WatchlistPreferences' | 3 | active |
| `jarvis_v2.wic.__init__.WatchlistStore` | class | `src/jarvis_v2/wic/__init__.py:1325-1426` | class WatchlistStore() | 1 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:1328-1348` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:1350-1351` | def __enter__(self) -> 'WatchlistStore' | 1 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:1353-1354` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.save` | method | `src/jarvis_v2/wic/__init__.py:1356-1385` | def save(self, owner_id: str, countries: Iterable[str], regions: Iterable[str], topics: Iterable[str], updated_at: str, *, requester_id: str) -> WatchlistPreferences | 5 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.get` | method | `src/jarvis_v2/wic/__init__.py:1387-1388` | def get(self, owner_id: str, *, requester_id: str) -> WatchlistPreferences \| None | 27 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.history` | method | `src/jarvis_v2/wic/__init__.py:1390-1398` | def history(self, owner_id: str, *, requester_id: str) -> tuple[WatchlistPreferences, ...] | 12 | active |
| `jarvis_v2.wic.__init__.WatchlistStore._get` | method | `src/jarvis_v2/wic/__init__.py:1400-1407` | def _get(self, owner_id: str) -> WatchlistPreferences \| None | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistStore._assert_owner` | method | `src/jarvis_v2/wic/__init__.py:1410-1415` | def _assert_owner(owner_id: str, requester_id: str) -> str | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistStore._payload` | method | `src/jarvis_v2/wic/__init__.py:1418-1422` | def _payload(record: WatchlistPreferences) -> str | 0 | active |
| `jarvis_v2.wic.__init__.WatchlistStore.close` | method | `src/jarvis_v2/wic/__init__.py:1424-1426` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.AlertPolicy` | class | `src/jarvis_v2/wic/__init__.py:1430-1490` | class AlertPolicy() | 1 | active |
| `jarvis_v2.wic.__init__.AlertPolicy.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1442-1461` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.AlertPolicy.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1463-1473` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.AlertPolicy.from_dict` | method | `src/jarvis_v2/wic/__init__.py:1476-1490` | def from_dict(cls, data: Mapping[str, object]) -> 'AlertPolicy' | 3 | active |
| `jarvis_v2.wic.__init__.AlertDecision` | class | `src/jarvis_v2/wic/__init__.py:1494-1527` | class AlertDecision() | 0 | active |
| `jarvis_v2.wic.__init__.AlertDecision.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1505-1516` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.AlertDecision.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1518-1527` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.AlertStore` | class | `src/jarvis_v2/wic/__init__.py:1530-1673` | class AlertStore() | 1 | active |
| `jarvis_v2.wic.__init__.AlertStore.__init__` | method | `src/jarvis_v2/wic/__init__.py:1533-1556` | def __init__(self, database: str \| Path \| sqlite3.Connection) | 5 | active |
| `jarvis_v2.wic.__init__.AlertStore.__enter__` | method | `src/jarvis_v2/wic/__init__.py:1558-1559` | def __enter__(self) -> 'AlertStore' | 1 | active |
| `jarvis_v2.wic.__init__.AlertStore.__exit__` | method | `src/jarvis_v2/wic/__init__.py:1561-1562` | def __exit__(self, exc_type: object, exc: object, tb: object) -> None | 1 | active |
| `jarvis_v2.wic.__init__.AlertStore.save_policy` | method | `src/jarvis_v2/wic/__init__.py:1564-1581` | def save_policy(self, policy: AlertPolicy, *, requester_id: str) -> AlertPolicy | 1 | active |
| `jarvis_v2.wic.__init__.AlertStore.get_policy` | method | `src/jarvis_v2/wic/__init__.py:1583-1595` | def get_policy(self, policy_id: str, *, requester_id: str) -> AlertPolicy \| None | 1 | active |
| `jarvis_v2.wic.__init__.AlertStore.evaluate` | method | `src/jarvis_v2/wic/__init__.py:1597-1645` | def evaluate(self, policy_id: str, change_digest: str, observed_at: str, *, material_change: bool, requester_id: str, evaluated_at: str \| None=None) -> AlertDecision | 2 | active |
| `jarvis_v2.wic.__init__.AlertStore.history` | method | `src/jarvis_v2/wic/__init__.py:1647-1657` | def history(self, policy_id: str, *, requester_id: str) -> tuple[AlertDecision, ...] | 12 | active |
| `jarvis_v2.wic.__init__.AlertStore._assert_owner` | method | `src/jarvis_v2/wic/__init__.py:1660-1662` | def _assert_owner(owner_id: str, requester_id: str) -> None | 0 | active |
| `jarvis_v2.wic.__init__.AlertStore._quiet` | method | `src/jarvis_v2/wic/__init__.py:1665-1669` | def _quiet(policy: AlertPolicy, minute: int) -> bool | 0 | active |
| `jarvis_v2.wic.__init__.AlertStore.close` | method | `src/jarvis_v2/wic/__init__.py:1671-1673` | def close(self) -> None | 34 | active |
| `jarvis_v2.wic.__init__.WorldCard` | class | `src/jarvis_v2/wic/__init__.py:1677-1739` | class WorldCard() | 1 | active |
| `jarvis_v2.wic.__init__.WorldCard.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1689-1706` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.WorldCard.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1708-1718` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.WorldCard.from_dict` | method | `src/jarvis_v2/wic/__init__.py:1721-1739` | def from_dict(cls, data: Mapping[str, object]) -> 'WorldCard' | 3 | active |
| `jarvis_v2.wic.__init__.WorldTimeline` | class | `src/jarvis_v2/wic/__init__.py:1743-1771` | class WorldTimeline() | 1 | active |
| `jarvis_v2.wic.__init__.WorldTimeline.__post_init__` | method | `src/jarvis_v2/wic/__init__.py:1748-1754` | def __post_init__(self) -> None | 0 | active |
| `jarvis_v2.wic.__init__.WorldTimeline.from_cards` | method | `src/jarvis_v2/wic/__init__.py:1757-1762` | def from_cards(cls, cards: Iterable[WorldCard]) -> 'WorldTimeline' | 1 | active |
| `jarvis_v2.wic.__init__.WorldTimeline._sort_key` | method | `src/jarvis_v2/wic/__init__.py:1765-1768` | def _sort_key(card: WorldCard) -> tuple[datetime, str] | 0 | active |
| `jarvis_v2.wic.__init__.WorldTimeline.as_dict` | method | `src/jarvis_v2/wic/__init__.py:1770-1771` | def as_dict(self) -> dict[str, object] | 18 | active |
| `jarvis_v2.wic.__init__.PublicSourceIngestion` | class | `src/jarvis_v2/wic/__init__.py:1782-1893` | class PublicSourceIngestion() | 1 | active |
| `jarvis_v2.wic.__init__.PublicSourceIngestion.__init__` | method | `src/jarvis_v2/wic/__init__.py:1785-1820` | def __init__(self, store: SourceStore, sources: Iterable[SourcePolicy], *, feed_transport: FeedTransport \| None=None, clock: Callable[[], datetime] \| None=None, timeout_seconds:  | 5 | active |
| `jarvis_v2.wic.__init__.PublicSourceIngestion.ingest` | method | `src/jarvis_v2/wic/__init__.py:1822-1860` | def ingest(self, source_id: str, feed_url: str) -> IngestionResult | 5 | active |
| `jarvis_v2.wic.__init__.PublicSourceIngestion._result` | method | `src/jarvis_v2/wic/__init__.py:1862-1871` | def _result(self, source_id: str, fetched_at: str, status: str, observations: tuple[SourceObservation, ...]=(), rejected_items: int=0, failure: str \| None=None) -> IngestionResult | 0 | active |
| `jarvis_v2.wic.__init__.PublicSourceIngestion._observation` | method | `src/jarvis_v2/wic/__init__.py:1874-1893` | def _observation(item: Mapping[str, object], policy: SourcePolicy, feed_url: str, fetched_at: str) -> SourceObservation | 0 | active |
| `test_acceptance_evidence.AcceptanceEvidenceTests` | class | `tests/test_acceptance_evidence.py:21-234` | class AcceptanceEvidenceTests(unittest.TestCase) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.setUp` | method | `tests/test_acceptance_evidence.py:22-28` | def setUp(self) | 35 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.seed_history` | method | `tests/test_acceptance_evidence.py:30-40` | def seed_history(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_history_sorts_before_limiting_and_filters_task` | method | `tests/test_acceptance_evidence.py:42-53` | def test_history_sorts_before_limiting_and_filters_task(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_history_limit_boundary_and_invalid_types` | method | `tests/test_acceptance_evidence.py:55-69` | def test_history_limit_boundary_and_invalid_types(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_invalid_history_requests_are_rejected_before_sql` | method | `tests/test_acceptance_evidence.py:71-81` | def test_invalid_history_requests_are_rejected_before_sql(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_restart_stale_and_duplicate_completion_expose_only_metadata` | method | `tests/test_acceptance_evidence.py:83-107` | def test_restart_stale_and_duplicate_completion_expose_only_metadata(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_evidence_rejects_duplicate_missing_and_private_fields` | method | `tests/test_acceptance_evidence.py:109-124` | def test_evidence_rejects_duplicate_missing_and_private_fields(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_ci_shape_bounds_and_unavailable_are_not_success_claims` | method | `tests/test_acceptance_evidence.py:126-151` | def test_ci_shape_bounds_and_unavailable_are_not_success_claims(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.manifest` | method | `tests/test_acceptance_evidence.py:154-161` | def manifest(module_id) | 16 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_explicit_module_local_permissions_and_typed_compatibility` | method | `tests/test_acceptance_evidence.py:163-184` | def test_explicit_module_local_permissions_and_typed_compatibility(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_manifest_malformed_shapes_and_inferred_permissions_rejected` | method | `tests/test_acceptance_evidence.py:186-204` | def test_manifest_malformed_shapes_and_inferred_permissions_rejected(self) | 1 | test |
| `test_acceptance_evidence.AcceptanceEvidenceTests.test_gate_and_milestone_evidence_fields_are_complete` | method | `tests/test_acceptance_evidence.py:206-234` | def test_gate_and_milestone_evidence_fields_are_complete(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests` | class | `tests/test_aegis_slots.py:8-95` | class AegisSlotTests(unittest.TestCase) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_in_flight_work_is_not_preempted` | method | `tests/test_aegis_slots.py:9-18` | def test_in_flight_work_is_not_preempted(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_overlapping_lower_priority_request_remains_fenced` | method | `tests/test_aegis_slots.py:20-27` | def test_overlapping_lower_priority_request_remains_fenced(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_guardian_blocks_lower_priority_until_next_compatible_slot` | method | `tests/test_aegis_slots.py:29-35` | def test_guardian_blocks_lower_priority_until_next_compatible_slot(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_guardian_uses_stable_configured_slot_order` | method | `tests/test_aegis_slots.py:37-40` | def test_guardian_uses_stable_configured_slot_order(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_request_sequence_is_idempotent_and_release_is_strict` | method | `tests/test_aegis_slots.py:42-52` | def test_request_sequence_is_idempotent_and_release_is_strict(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_invalid_request_does_not_change_state` | method | `tests/test_aegis_slots.py:54-61` | def test_invalid_request_does_not_change_state(self) | 1 | test |
| `test_aegis_slots.AegisSlotTests.test_bounded_sequences_do_not_leak_or_starve_guardian` | method | `tests/test_aegis_slots.py:63-95` | def test_bounded_sequences_do_not_leak_or_starve_guardian(self) | 1 | test |
| `test_astra_watchdog.load_watchdog` | function | `tests/test_astra_watchdog.py:9-15` | def load_watchdog() | 1 | test |
| `test_astra_watchdog.WatchdogTests` | class | `tests/test_astra_watchdog.py:18-139` | class WatchdogTests(unittest.TestCase) | 1 | test |
| `test_astra_watchdog.WatchdogTests.test_rollback_is_fenced_and_durable_pending_without_pointer` | method | `tests/test_astra_watchdog.py:19-52` | def test_rollback_is_fenced_and_durable_pending_without_pointer(self) | 1 | test |
| `test_astra_watchdog.WatchdogTests.test_activation_fast_forwards_and_records_verified_receipt` | method | `tests/test_astra_watchdog.py:54-104` | def test_activation_fast_forwards_and_records_verified_receipt(self) | 1 | test |
| `test_astra_watchdog.WatchdogTests.test_activation_refuses_control_marker_without_moving_head` | method | `tests/test_astra_watchdog.py:106-139` | def test_activation_refuses_control_marker_without_moving_head(self) | 1 | test |
| `test_atlas_core_events.AtlasCoreEventHistoryTests` | class | `tests/test_atlas_core_events.py:8-44` | class AtlasCoreEventHistoryTests(unittest.TestCase) | 1 | test |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_history_is_ordered_bounded_and_excludes_private_values` | method | `tests/test_atlas_core_events.py:9-28` | def test_history_is_ordered_bounded_and_excludes_private_values(self) | 1 | test |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_history_for_unknown_task_is_empty` | method | `tests/test_atlas_core_events.py:30-34` | def test_history_for_unknown_task_is_empty(self) | 1 | test |
| `test_atlas_core_events.AtlasCoreEventHistoryTests.test_duplicate_completion_is_rejected` | method | `tests/test_atlas_core_events.py:36-44` | def test_duplicate_completion_is_rejected(self) | 1 | test |
| `test_automation_devices.manifest` | function | `tests/test_automation_devices.py:14-21` | def manifest() -> NodeManifest | 16 | test |
| `test_automation_devices.job` | function | `tests/test_automation_devices.py:24-33` | def job(job_id: str='job-1') -> LocalAgentJob | 10 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests` | class | `tests/test_automation_devices.py:36-92` | class AuthenticatedDeviceRegistryTests(unittest.TestCase) | 1 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.setUp` | method | `tests/test_automation_devices.py:37-46` | def setUp(self) | 35 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.test_registration_is_idempotent_and_snapshot_contains_only_digest` | method | `tests/test_automation_devices.py:48-53` | def test_registration_is_idempotent_and_snapshot_contains_only_digest(self) | 1 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.test_claim_requires_authentication_and_online_device` | method | `tests/test_automation_devices.py:55-61` | def test_claim_requires_authentication_and_online_device(self) | 1 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.test_revoked_device_cannot_claim_even_with_old_proof` | method | `tests/test_automation_devices.py:63-68` | def test_revoked_device_cannot_claim_even_with_old_proof(self) | 1 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.test_rotation_requires_current_key_and_fences_old_key` | method | `tests/test_automation_devices.py:70-80` | def test_rotation_requires_current_key_and_fences_old_key(self) | 1 | test |
| `test_automation_devices.AuthenticatedDeviceRegistryTests.test_complete_is_bound_to_authenticated_device_lease` | method | `tests/test_automation_devices.py:82-92` | def test_complete_is_bound_to_authenticated_device_lease(self) | 1 | test |
| `test_automation_dispatcher.payload` | function | `tests/test_automation_dispatcher.py:10-19` | def payload(task_id: str) -> dict[str, object] | 32 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests` | class | `tests/test_automation_dispatcher.py:22-73` | class ReconnectDispatcherTests(unittest.TestCase) | 1 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.setUp` | method | `tests/test_automation_dispatcher.py:23-27` | def setUp(self) | 35 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.tearDown` | method | `tests/test_automation_dispatcher.py:29-30` | def tearDown(self) | 12 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.test_offline_host_leaves_job_pending_without_handoff` | method | `tests/test_automation_dispatcher.py:32-41` | def test_offline_host_leaves_job_pending_without_handoff(self) | 1 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.test_online_host_with_capacity_is_the_only_dispatch_path` | method | `tests/test_automation_dispatcher.py:43-52` | def test_online_host_with_capacity_is_the_only_dispatch_path(self) | 1 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.test_failed_handoff_is_requeued_and_can_retry` | method | `tests/test_automation_dispatcher.py:54-62` | def test_failed_handoff_is_requeued_and_can_retry(self) | 1 | test |
| `test_automation_dispatcher.ReconnectDispatcherTests.test_invalid_job_payload_is_not_claimed` | method | `tests/test_automation_dispatcher.py:64-73` | def test_invalid_job_payload_is_not_claimed(self) | 1 | test |
| `test_automation_leases.CoordinatorLeaseTests` | class | `tests/test_automation_leases.py:8-43` | class CoordinatorLeaseTests(unittest.TestCase) | 1 | test |
| `test_automation_leases.CoordinatorLeaseTests.setUp` | method | `tests/test_automation_leases.py:9-10` | def setUp(self) | 35 | test |
| `test_automation_leases.CoordinatorLeaseTests.test_renewal_extends_a_live_lease_and_completion_is_idempotent` | method | `tests/test_automation_leases.py:12-19` | def test_renewal_extends_a_live_lease_and_completion_is_idempotent(self) | 1 | test |
| `test_automation_leases.CoordinatorLeaseTests.test_expired_lease_is_requeued_and_old_owner_cannot_complete` | method | `tests/test_automation_leases.py:21-29` | def test_expired_lease_is_requeued_and_old_owner_cannot_complete(self) | 1 | test |
| `test_automation_leases.CoordinatorLeaseTests.test_stale_or_invalid_renewals_do_not_change_the_queue` | method | `tests/test_automation_leases.py:31-43` | def test_stale_or_invalid_renewals_do_not_change_the_queue(self) | 1 | test |
| `test_automation_queue_api.CoordinatorQueueTests` | class | `tests/test_automation_queue_api.py:15-65` | class CoordinatorQueueTests(unittest.TestCase) | 1 | test |
| `test_automation_queue_api.CoordinatorQueueTests.test_versioned_envelope_round_trip_and_unknown_fields_are_rejected` | method | `tests/test_automation_queue_api.py:16-23` | def test_versioned_envelope_round_trip_and_unknown_fields_are_rejected(self) | 1 | test |
| `test_automation_queue_api.CoordinatorQueueTests.test_existing_task_queue_reopens_without_migration_or_data_loss` | method | `tests/test_automation_queue_api.py:25-34` | def test_existing_task_queue_reopens_without_migration_or_data_loss(self) | 1 | test |
| `test_automation_queue_api.CoordinatorQueueTests.test_lease_completion_and_duplicate_enqueue_preserve_state` | method | `tests/test_automation_queue_api.py:36-45` | def test_lease_completion_and_duplicate_enqueue_preserve_state(self) | 1 | test |
| `test_automation_queue_api.CoordinatorQueueTests.test_reopen_requeues_expired_lease_and_duplicate_receipt_is_idempotent` | method | `tests/test_automation_queue_api.py:47-65` | def test_reopen_requeues_expired_lease_and_duplicate_receipt_is_idempotent(self) | 1 | test |
| `test_automation_recovery_drill.RecoveryDrillTests` | class | `tests/test_automation_recovery_drill.py:9-81` | class RecoveryDrillTests(unittest.TestCase) | 1 | test |
| `test_automation_recovery_drill.RecoveryDrillTests.test_restored_completed_event_is_not_applied_twice` | method | `tests/test_automation_recovery_drill.py:10-41` | def test_restored_completed_event_is_not_applied_twice(self) | 1 | test |
| `test_automation_recovery_drill.RecoveryDrillTests.test_replay_after_restore_keeps_effect_idempotent` | method | `tests/test_automation_recovery_drill.py:43-71` | def test_replay_after_restore_keeps_effect_idempotent(self) | 1 | test |
| `test_automation_recovery_drill.RecoveryDrillTests.test_replay_limit_is_bounded` | method | `tests/test_automation_recovery_drill.py:73-81` | def test_replay_limit_is_bounded(self) | 1 | test |
| `test_automation_scheduler.AutomationScheduleTests` | class | `tests/test_automation_scheduler.py:13-50` | class AutomationScheduleTests(unittest.TestCase) | 1 | test |
| `test_automation_scheduler.AutomationScheduleTests.test_schedule_survives_offline_reopen_and_uses_utc` | method | `tests/test_automation_scheduler.py:14-27` | def test_schedule_survives_offline_reopen_and_uses_utc(self) | 1 | test |
| `test_automation_scheduler.AutomationScheduleTests.test_dst_transition_and_replay_use_backend_contract` | method | `tests/test_automation_scheduler.py:29-41` | def test_dst_transition_and_replay_use_backend_contract(self) | 1 | test |
| `test_automation_scheduler.AutomationScheduleTests.test_once_schedule_is_idempotent_and_conflicts_fail` | method | `tests/test_automation_scheduler.py:43-50` | def test_once_schedule_is_idempotent_and_conflicts_fail(self) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests` | class | `tests/test_backend_acceptance.py:33-233` | class BackendAcceptanceTests(unittest.TestCase) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests.test_scoped_authorization_and_context_reject_cross_scope_data` | method | `tests/test_backend_acceptance.py:34-66` | def test_scoped_authorization_and_context_reject_cross_scope_data(self) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests.test_offline_node_requeues_and_second_node_completes_job` | method | `tests/test_backend_acceptance.py:68-105` | def test_offline_node_requeues_and_second_node_completes_job(self) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests.test_linux_authenticated_inference_roundtrip_preserves_context_and_audit` | method | `tests/test_backend_acceptance.py:107-148` | def test_linux_authenticated_inference_roundtrip_preserves_context_and_audit(self) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests.test_backup_restore_preserves_owned_backend_state` | method | `tests/test_backend_acceptance.py:150-181` | def test_backup_restore_preserves_owned_backend_state(self) | 1 | test |
| `test_backend_acceptance.BackendAcceptanceTests.test_create_only_migration_records_provenance_without_touching_source` | method | `tests/test_backend_acceptance.py:183-233` | def test_create_only_migration_records_provenance_without_touching_source(self) | 1 | test |
| `test_backend_authorization.BackendAuthorizationTests` | class | `tests/test_backend_authorization.py:12-56` | class BackendAuthorizationTests(unittest.TestCase) | 1 | test |
| `test_backend_authorization.BackendAuthorizationTests.setUp` | method | `tests/test_backend_authorization.py:13-15` | def setUp(self) | 35 | test |
| `test_backend_authorization.BackendAuthorizationTests.test_each_module_can_only_use_its_own_read_and_health_grant` | method | `tests/test_backend_authorization.py:17-29` | def test_each_module_can_only_use_its_own_read_and_health_grant(self) | 1 | test |
| `test_backend_authorization.BackendAuthorizationTests.test_cross_module_grant_requires_exact_owner_approval` | method | `tests/test_backend_authorization.py:31-38` | def test_cross_module_grant_requires_exact_owner_approval(self) | 1 | test |
| `test_backend_authorization.BackendAuthorizationTests.test_approval_and_identity_conflicts_fail_closed` | method | `tests/test_backend_authorization.py:40-47` | def test_approval_and_identity_conflicts_fail_closed(self) | 1 | test |
| `test_backend_authorization.BackendAuthorizationTests.test_revoke_and_expiry_remove_access` | method | `tests/test_backend_authorization.py:49-56` | def test_revoke_and_expiry_remove_access(self) | 1 | test |
| `test_backend_backup.TestCipher` | class | `tests/test_backend_backup.py:10-20` | class TestCipher() | 1 | test |
| `test_backend_backup.TestCipher.seal` | method | `tests/test_backend_backup.py:13-14` | def seal(self, payload: bytes) -> bytes | 1 | test |
| `test_backend_backup.TestCipher.unseal` | method | `tests/test_backend_backup.py:16-20` | def unseal(self, payload: bytes) -> bytes | 1 | test |
| `test_backend_backup.BackendBackupTests` | class | `tests/test_backend_backup.py:23-101` | class BackendBackupTests(unittest.TestCase) | 1 | test |
| `test_backend_backup.BackendBackupTests.make_database` | method | `tests/test_backend_backup.py:24-31` | def make_database(self, path: Path) -> None | 1 | test |
| `test_backend_backup.BackendBackupTests.test_backup_and_restore_preserve_schema_data_and_wal_state` | method | `tests/test_backend_backup.py:33-60` | def test_backup_and_restore_preserve_schema_data_and_wal_state(self) | 1 | test |
| `test_backend_backup.BackendBackupTests.test_destination_is_never_overwritten_and_source_is_not_mutated` | method | `tests/test_backend_backup.py:62-74` | def test_destination_is_never_overwritten_and_source_is_not_mutated(self) | 1 | test |
| `test_backend_backup.BackendBackupTests.test_explicit_cipher_round_trip_and_digest_fence` | method | `tests/test_backend_backup.py:76-92` | def test_explicit_cipher_round_trip_and_digest_fence(self) | 1 | test |
| `test_backend_backup.BackendBackupTests.test_wal_sidecar_mismatch_fails_closed` | method | `tests/test_backend_backup.py:94-101` | def test_wal_sidecar_mismatch_fails_closed(self) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests` | class | `tests/test_backend_cloudflare_jobs.py:9-68` | class CloudflareJobAdapterTests(unittest.TestCase) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.setUp` | method | `tests/test_backend_cloudflare_jobs.py:10-38` | def setUp(self) | 35 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.setUp.transport` | function | `tests/test_backend_cloudflare_jobs.py:14-32` | def transport(request) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_create_claim_complete_uses_durable_metadata_and_https_only` | method | `tests/test_backend_cloudflare_jobs.py:40-50` | def test_create_claim_complete_uses_durable_metadata_and_https_only(self) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_invalid_url_and_token_fail_closed_without_network` | method | `tests/test_backend_cloudflare_jobs.py:52-58` | def test_invalid_url_and_token_fail_closed_without_network(self) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_response_and_transport_failures_do_not_expose_secret` | method | `tests/test_backend_cloudflare_jobs.py:60-68` | def test_response_and_transport_failures_do_not_expose_secret(self) | 1 | test |
| `test_backend_cloudflare_jobs.CloudflareJobAdapterTests.test_response_and_transport_failures_do_not_expose_secret.failure` | function | `tests/test_backend_cloudflare_jobs.py:61-62` | def failure(request) | 13 | test |
| `test_backend_code_index.BackendCodeIndexTests` | class | `tests/test_backend_code_index.py:12-58` | class BackendCodeIndexTests(unittest.TestCase) | 1 | test |
| `test_backend_code_index.BackendCodeIndexTests.test_python_symbols_imports_tests_and_provenance_are_searchable` | method | `tests/test_backend_code_index.py:13-27` | def test_python_symbols_imports_tests_and_provenance_are_searchable(self) | 1 | test |
| `test_backend_code_index.BackendCodeIndexTests.test_sensitive_sources_are_excluded_without_becoming_searchable` | method | `tests/test_backend_code_index.py:29-40` | def test_sensitive_sources_are_excluded_without_becoming_searchable(self) | 1 | test |
| `test_backend_code_index.BackendCodeIndexTests.test_reindex_replaces_old_blob_and_preserves_source_binding` | method | `tests/test_backend_code_index.py:42-49` | def test_reindex_replaces_old_blob_and_preserves_source_binding(self) | 1 | test |
| `test_backend_code_index.BackendCodeIndexTests.test_invalid_provenance_and_python_fail_without_partial_index` | method | `tests/test_backend_code_index.py:51-58` | def test_invalid_provenance_and_python_fail_without_partial_index(self) | 1 | test |
| `test_backend_connectors.BackendConnectorTests` | class | `tests/test_backend_connectors.py:10-55` | class BackendConnectorTests(unittest.TestCase) | 1 | test |
| `test_backend_connectors.BackendConnectorTests.test_each_connector_is_independently_revocable` | method | `tests/test_backend_connectors.py:11-25` | def test_each_connector_is_independently_revocable(self) | 1 | test |
| `test_backend_connectors.BackendConnectorTests.test_connector_revoke_does_not_cross_identities_or_connectors` | method | `tests/test_backend_connectors.py:27-35` | def test_connector_revoke_does_not_cross_identities_or_connectors(self) | 1 | test |
| `test_backend_connectors.BackendConnectorTests.test_invalid_scope_connector_and_credential_value_fail_closed` | method | `tests/test_backend_connectors.py:37-46` | def test_invalid_scope_connector_and_credential_value_fail_closed(self) | 1 | test |
| `test_backend_connectors.BackendConnectorTests.test_idempotent_grant_and_unknown_revoke` | method | `tests/test_backend_connectors.py:48-55` | def test_idempotent_grant_and_unknown_revoke(self) | 1 | test |
| `test_backend_context.BackendContextTests` | class | `tests/test_backend_context.py:6-48` | class BackendContextTests(unittest.TestCase) | 1 | test |
| `test_backend_context.BackendContextTests.test_protected_sections_survive_history_reduction` | method | `tests/test_backend_context.py:7-22` | def test_protected_sections_survive_history_reduction(self) | 1 | test |
| `test_backend_context.BackendContextTests.test_protected_content_fails_closed_when_budget_is_too_small` | method | `tests/test_backend_context.py:24-26` | def test_protected_content_fails_closed_when_budget_is_too_small(self) | 1 | test |
| `test_backend_context.BackendContextTests.test_packet_digest_is_deterministic_and_empty_history_is_valid` | method | `tests/test_backend_context.py:28-34` | def test_packet_digest_is_deterministic_and_empty_history_is_valid(self) | 1 | test |
| `test_backend_context.BackendContextTests.test_restricted_fields_and_invalid_budgets_are_rejected` | method | `tests/test_backend_context.py:36-42` | def test_restricted_fields_and_invalid_budgets_are_rejected(self) | 1 | test |
| `test_backend_context.BackendContextTests.test_oversized_context_rejects_repeatedly_without_a_retry_loop` | method | `tests/test_backend_context.py:44-48` | def test_oversized_context_rejects_repeatedly_without_a_retry_loop(self) | 1 | test |
| `test_backend_conversation.BackendConversationTests` | class | `tests/test_backend_conversation.py:11-102` | class BackendConversationTests(unittest.TestCase) | 1 | test |
| `test_backend_conversation.BackendConversationTests.test_backend_exports_are_safe_when_core_is_imported_first` | method | `tests/test_backend_conversation.py:12-22` | def test_backend_exports_are_safe_when_core_is_imported_first(self) | 1 | test |
| `test_backend_conversation.BackendConversationTests.test_turns_are_durable_ordered_and_provider_neutral` | method | `tests/test_backend_conversation.py:24-53` | def test_turns_are_durable_ordered_and_provider_neutral(self) | 1 | test |
| `test_backend_conversation.BackendConversationTests.test_turn_replay_is_idempotent_and_conflicts_are_rejected` | method | `tests/test_backend_conversation.py:55-83` | def test_turn_replay_is_idempotent_and_conflicts_are_rejected(self) | 1 | test |
| `test_backend_conversation.BackendConversationTests.test_invalid_and_unbounded_values_are_rejected_without_partial_turn` | method | `tests/test_backend_conversation.py:85-95` | def test_invalid_and_unbounded_values_are_rejected_without_partial_turn(self) | 1 | test |
| `test_backend_conversation.BackendConversationTests.test_explicit_conversation_creation_is_idempotent_but_metadata_is_bound` | method | `tests/test_backend_conversation.py:97-102` | def test_explicit_conversation_creation_is_idempotent_but_metadata_is_bound(self) | 1 | test |
| `test_backend_effects.BackendEffectJournalTests` | class | `tests/test_backend_effects.py:8-79` | class BackendEffectJournalTests(unittest.TestCase) | 1 | test |
| `test_backend_effects.BackendEffectJournalTests.test_completed_effect_is_not_executed_again_after_restart` | method | `tests/test_backend_effects.py:9-25` | def test_completed_effect_is_not_executed_again_after_restart(self) | 1 | test |
| `test_backend_effects.BackendEffectJournalTests.test_unfinished_effect_requires_reconciliation_before_retry` | method | `tests/test_backend_effects.py:27-45` | def test_unfinished_effect_requires_reconciliation_before_retry(self) | 1 | test |
| `test_backend_effects.BackendEffectJournalTests.test_effect_identity_and_result_replays_are_bound` | method | `tests/test_backend_effects.py:47-64` | def test_effect_identity_and_result_replays_are_bound(self) | 1 | test |
| `test_backend_effects.BackendEffectJournalTests.test_invalid_effects_do_not_create_records` | method | `tests/test_backend_effects.py:66-79` | def test_invalid_effects_do_not_create_records(self) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests` | class | `tests/test_backend_event_bus.py:8-75` | class BackendEventBusTests(unittest.TestCase) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests.test_publish_is_durable_and_idempotent` | method | `tests/test_backend_event_bus.py:9-24` | def test_publish_is_durable_and_idempotent(self) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests.test_conflicting_idempotency_payload_is_rejected` | method | `tests/test_backend_event_bus.py:26-31` | def test_conflicting_idempotency_payload_is_rejected(self) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests.test_successful_effect_receipt_prevents_duplicate_effect` | method | `tests/test_backend_event_bus.py:33-47` | def test_successful_effect_receipt_prevents_duplicate_effect(self) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests.test_failed_effect_is_retryable_then_completes` | method | `tests/test_backend_event_bus.py:49-64` | def test_failed_effect_is_retryable_then_completes(self) | 1 | test |
| `test_backend_event_bus.BackendEventBusTests.test_invalid_envelopes_are_rejected_before_outbox_write` | method | `tests/test_backend_event_bus.py:66-75` | def test_invalid_envelopes_are_rejected_before_outbox_write(self) | 1 | test |
| `test_backend_generation_scheduler.GenerationSchedulerTests` | class | `tests/test_backend_generation_scheduler.py:10-39` | class GenerationSchedulerTests(unittest.TestCase) | 1 | test |
| `test_backend_generation_scheduler.GenerationSchedulerTests.test_priority_interactive_and_single_generation_fencing` | method | `tests/test_backend_generation_scheduler.py:11-21` | def test_priority_interactive_and_single_generation_fencing(self) | 1 | test |
| `test_backend_generation_scheduler.GenerationSchedulerTests.test_guardian_reservation_and_finish_are_fenced` | method | `tests/test_backend_generation_scheduler.py:23-32` | def test_guardian_reservation_and_finish_are_fenced(self) | 1 | test |
| `test_backend_generation_scheduler.GenerationSchedulerTests.test_quota_and_invalid_requests_fail_closed` | method | `tests/test_backend_generation_scheduler.py:34-39` | def test_quota_and_invalid_requests_fail_closed(self) | 1 | test |
| `test_backend_handoff.BackendHandoffTests` | class | `tests/test_backend_handoff.py:8-58` | class BackendHandoffTests(unittest.TestCase) | 1 | test |
| `test_backend_handoff.BackendHandoffTests.test_handoff_preserves_task_permissions_effects_and_context_after_restart` | method | `tests/test_backend_handoff.py:9-28` | def test_handoff_preserves_task_permissions_effects_and_context_after_restart(self) | 1 | test |
| `test_backend_handoff.BackendHandoffTests.test_handoff_replay_is_idempotent_and_conflicts_fail_closed` | method | `tests/test_backend_handoff.py:30-42` | def test_handoff_replay_is_idempotent_and_conflicts_fail_closed(self) | 1 | test |
| `test_backend_handoff.BackendHandoffTests.test_handoff_rejects_invalid_or_unbounded_inputs_without_a_record` | method | `tests/test_backend_handoff.py:44-58` | def test_handoff_rejects_invalid_or_unbounded_inputs_without_a_record(self) | 1 | test |
| `test_backend_linux_service.LinuxServiceTests` | class | `tests/test_backend_linux_service.py:6-34` | class LinuxServiceTests(unittest.TestCase) | 1 | test |
| `test_backend_linux_service.LinuxServiceTests.setUp` | method | `tests/test_backend_linux_service.py:7-11` | def setUp(self) | 35 | test |
| `test_backend_linux_service.LinuxServiceTests.test_unit_is_shell_free_and_hardened` | method | `tests/test_backend_linux_service.py:13-19` | def test_unit_is_shell_free_and_hardened(self) | 1 | test |
| `test_backend_linux_service.LinuxServiceTests.test_startup_does_not_duplicate_a_healthy_service` | method | `tests/test_backend_linux_service.py:21-26` | def test_startup_does_not_duplicate_a_healthy_service(self) | 1 | test |
| `test_backend_linux_service.LinuxServiceTests.test_invalid_profile_inputs_fail_closed` | method | `tests/test_backend_linux_service.py:28-34` | def test_invalid_profile_inputs_fail_closed(self) | 1 | test |
| `test_backend_manifest.manifest` | function | `tests/test_backend_manifest.py:11-25` | def manifest(module_id, *, dependencies=None, scopes=None, label=None) | 16 | test |
| `test_backend_manifest.BackendManifestTests` | class | `tests/test_backend_manifest.py:28-55` | class BackendManifestTests(unittest.TestCase) | 1 | test |
| `test_backend_manifest.BackendManifestTests.test_complete_active_set_is_typed_and_stable` | method | `tests/test_backend_manifest.py:29-33` | def test_complete_active_set_is_typed_and_stable(self) | 1 | test |
| `test_backend_manifest.BackendManifestTests.test_malformed_and_incomplete_manifests_are_rejected` | method | `tests/test_backend_manifest.py:35-41` | def test_malformed_and_incomplete_manifests_are_rejected(self) | 1 | test |
| `test_backend_manifest.BackendManifestTests.test_unknown_dependency_and_permission_escalation_are_rejected` | method | `tests/test_backend_manifest.py:43-47` | def test_unknown_dependency_and_permission_escalation_are_rejected(self) | 1 | test |
| `test_backend_manifest.BackendManifestTests.test_health_label_and_identity_are_bound_to_stable_key` | method | `tests/test_backend_manifest.py:49-55` | def test_health_label_and_identity_are_bound_to_stable_key(self) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests` | class | `tests/test_backend_ollama_profile.py:13-91` | class OllamaProfileTests(unittest.TestCase) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests.test_default_profile_is_reproducible_and_linux_only` | method | `tests/test_backend_ollama_profile.py:14-22` | def test_default_profile_is_reproducible_and_linux_only(self) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests.test_measured_linux_probe_is_redacted_and_bound_to_profile` | method | `tests/test_backend_ollama_profile.py:24-37` | def test_measured_linux_probe_is_redacted_and_bound_to_profile(self) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests.test_invalid_profile_and_probe_states_are_rejected` | method | `tests/test_backend_ollama_profile.py:39-61` | def test_invalid_profile_and_probe_states_are_rejected(self) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests.test_linux_telemetry_reports_rates_limits_and_unavailable_accelerator` | method | `tests/test_backend_ollama_profile.py:63-80` | def test_linux_telemetry_reports_rates_limits_and_unavailable_accelerator(self) | 1 | test |
| `test_backend_ollama_profile.OllamaProfileTests.test_error_attribution_requires_a_bounded_category` | method | `tests/test_backend_ollama_profile.py:82-91` | def test_error_attribution_requires_a_bounded_category(self) | 1 | test |
| `test_backend_protocol_adapters.request` | function | `tests/test_backend_protocol_adapters.py:12-22` | def request() | 23 | test |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests` | class | `tests/test_backend_protocol_adapters.py:25-81` | class BackendProtocolAdapterTests(unittest.TestCase) | 1 | test |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests.test_responses_adapter_encodes_and_decodes_compatible_wire_shape` | method | `tests/test_backend_protocol_adapters.py:26-39` | def test_responses_adapter_encodes_and_decodes_compatible_wire_shape(self) | 1 | test |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests.test_chat_adapter_encodes_and_decodes_tool_arguments` | method | `tests/test_backend_protocol_adapters.py:41-62` | def test_chat_adapter_encodes_and_decodes_tool_arguments(self) | 1 | test |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests.test_invalid_wire_responses_are_rejected` | method | `tests/test_backend_protocol_adapters.py:64-73` | def test_invalid_wire_responses_are_rejected(self) | 1 | test |
| `test_backend_protocol_adapters.BackendProtocolAdapterTests.test_request_boundaries_are_checked_before_transport` | method | `tests/test_backend_protocol_adapters.py:75-81` | def test_request_boundaries_are_checked_before_transport(self) | 1 | test |
| `test_backend_provider_registry.capability` | function | `tests/test_backend_provider_registry.py:11-22` | def capability(**overrides) | 7 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests` | class | `tests/test_backend_provider_registry.py:25-79` | class BackendProviderRegistryTests(unittest.TestCase) | 1 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests.setUp` | method | `tests/test_backend_provider_registry.py:26-27` | def setUp(self) | 35 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_compatible_request_is_selected` | method | `tests/test_backend_provider_registry.py:29-39` | def test_compatible_request_is_selected(self) | 1 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_each_dispatch_requirement_blocks_incompatible_provider` | method | `tests/test_backend_provider_registry.py:41-60` | def test_each_dispatch_requirement_blocks_incompatible_provider(self) | 1 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_requested_identity_does_not_silently_fallback` | method | `tests/test_backend_provider_registry.py:62-71` | def test_requested_identity_does_not_silently_fallback(self) | 1 | test |
| `test_backend_provider_registry.BackendProviderRegistryTests.test_invalid_capabilities_and_requirements_are_rejected` | method | `tests/test_backend_provider_registry.py:73-79` | def test_invalid_capabilities_and_requirements_are_rejected(self) | 1 | test |
| `test_backend_reranking.candidate` | function | `tests/test_backend_reranking.py:7-8` | def candidate(document_id, snippet) | 17 | test |
| `test_backend_reranking.BackendRerankingTests` | class | `tests/test_backend_reranking.py:11-65` | class BackendRerankingTests(unittest.TestCase) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_local_embedding_reranks_with_stable_ties` | method | `tests/test_backend_reranking.py:12-20` | def test_local_embedding_reranks_with_stable_ties(self) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_budget_falls_back_to_keyword_order` | method | `tests/test_backend_reranking.py:22-32` | def test_budget_falls_back_to_keyword_order(self) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_model_failure_falls_back_without_provider_substitution` | method | `tests/test_backend_reranking.py:34-44` | def test_model_failure_falls_back_without_provider_substitution(self) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_model_failure_falls_back_without_provider_substitution.broken` | function | `tests/test_backend_reranking.py:35-36` | def broken(_text) | 5 | test |
| `test_backend_reranking.BackendRerankingTests.test_slow_model_is_time_bounded_and_falls_back` | method | `tests/test_backend_reranking.py:46-58` | def test_slow_model_is_time_bounded_and_falls_back(self) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_slow_model_is_time_bounded_and_falls_back.slow` | function | `tests/test_backend_reranking.py:47-49` | def slow(_text) | 1 | test |
| `test_backend_reranking.BackendRerankingTests.test_invalid_vectors_fall_back` | method | `tests/test_backend_reranking.py:60-65` | def test_invalid_vectors_fall_back(self) | 1 | test |
| `test_backend_retrieval.BackendRetrievalTests` | class | `tests/test_backend_retrieval.py:8-77` | class BackendRetrievalTests(unittest.TestCase) | 1 | test |
| `test_backend_retrieval.BackendRetrievalTests.test_search_returns_scope_source_timestamp_and_citation` | method | `tests/test_backend_retrieval.py:9-29` | def test_search_returns_scope_source_timestamp_and_citation(self) | 1 | test |
| `test_backend_retrieval.BackendRetrievalTests.test_source_filter_and_replay_are_deterministic` | method | `tests/test_backend_retrieval.py:31-43` | def test_source_filter_and_replay_are_deterministic(self) | 1 | test |
| `test_backend_retrieval.BackendRetrievalTests.test_invalid_queries_and_unbounded_documents_are_rejected` | method | `tests/test_backend_retrieval.py:45-57` | def test_invalid_queries_and_unbounded_documents_are_rejected(self) | 1 | test |
| `test_backend_retrieval.BackendRetrievalTests.test_optional_reranker_preserves_search_result_shape` | method | `tests/test_backend_retrieval.py:59-77` | def test_optional_reranker_preserves_search_result_shape(self) | 1 | test |
| `test_backend_routing.capability` | function | `tests/test_backend_routing.py:15-25` | def capability(provider_id='codex', *, available=True, quota_remaining=100) | 7 | test |
| `test_backend_routing.requirements` | function | `tests/test_backend_routing.py:28-37` | def requirements(**changes) | 8 | test |
| `test_backend_routing.BackendRoutingTests` | class | `tests/test_backend_routing.py:40-93` | class BackendRoutingTests(unittest.TestCase) | 1 | test |
| `test_backend_routing.BackendRoutingTests.test_sticky_route_requires_explicit_handoff` | method | `tests/test_backend_routing.py:41-50` | def test_sticky_route_requires_explicit_handoff(self) | 1 | test |
| `test_backend_routing.BackendRoutingTests.test_budget_blocks_without_selecting_another_provider` | method | `tests/test_backend_routing.py:52-64` | def test_budget_blocks_without_selecting_another_provider(self) | 1 | test |
| `test_backend_routing.BackendRoutingTests.test_circuit_opens_and_allows_one_timed_probe` | method | `tests/test_backend_routing.py:66-79` | def test_circuit_opens_and_allows_one_timed_probe(self) | 1 | test |
| `test_backend_routing.BackendRoutingTests.test_budget_reservation_can_be_released` | method | `tests/test_backend_routing.py:81-87` | def test_budget_reservation_can_be_released(self) | 1 | test |
| `test_backend_routing.BackendRoutingTests.test_registry_quota_becomes_a_consumable_default_budget` | method | `tests/test_backend_routing.py:89-93` | def test_registry_quota_becomes_a_consumable_default_budget(self) | 1 | test |
| `test_backend_scheduler.BackendSchedulerTests` | class | `tests/test_backend_scheduler.py:13-67` | class BackendSchedulerTests(unittest.TestCase) | 1 | test |
| `test_backend_scheduler.BackendSchedulerTests.test_one_shot_survives_reopen_and_uses_utc` | method | `tests/test_backend_scheduler.py:14-25` | def test_one_shot_survives_reopen_and_uses_utc(self) | 1 | test |
| `test_backend_scheduler.BackendSchedulerTests.test_daily_wall_time_survives_fall_dst_transition` | method | `tests/test_backend_scheduler.py:27-40` | def test_daily_wall_time_survives_fall_dst_transition(self) | 1 | test |
| `test_backend_scheduler.BackendSchedulerTests.test_spring_gap_moves_forward_and_replay_is_idempotent` | method | `tests/test_backend_scheduler.py:42-59` | def test_spring_gap_moves_forward_and_replay_is_idempotent(self) | 1 | test |
| `test_backend_scheduler.BackendSchedulerTests.test_invalid_timezone_and_message_are_rejected` | method | `tests/test_backend_scheduler.py:61-67` | def test_invalid_timezone_and_message_are_rejected(self) | 1 | test |
| `test_backend_secrets.BackendSecretTests` | class | `tests/test_backend_secrets.py:7-40` | class BackendSecretTests(unittest.TestCase) | 1 | test |
| `test_backend_secrets.BackendSecretTests.test_allowlisted_value_is_redacted_outside_explicit_use` | method | `tests/test_backend_secrets.py:8-15` | def test_allowlisted_value_is_redacted_outside_explicit_use(self) | 1 | test |
| `test_backend_secrets.BackendSecretTests.test_metadata_is_safe_for_external_telemetry` | method | `tests/test_backend_secrets.py:17-23` | def test_metadata_is_safe_for_external_telemetry(self) | 1 | test |
| `test_backend_secrets.BackendSecretTests.test_unallowlisted_and_missing_values_fail_closed` | method | `tests/test_backend_secrets.py:25-30` | def test_unallowlisted_and_missing_values_fail_closed(self) | 1 | test |
| `test_backend_secrets.BackendSecretTests.test_names_values_and_allowlist_are_bounded` | method | `tests/test_backend_secrets.py:32-40` | def test_names_values_and_allowlist_are_bounded(self) | 1 | test |
| `test_backend_storage.migration` | function | `tests/test_backend_storage.py:13-24` | def migration(module: str, version: int, table: str, *, bad_sql: bool=False) -> Migration | 11 | test |
| `test_backend_storage.BackendStorageTests` | class | `tests/test_backend_storage.py:27-106` | class BackendStorageTests(unittest.TestCase) | 1 | test |
| `test_backend_storage.BackendStorageTests.test_default_migration_is_idempotent_and_backend_owns_rows` | method | `tests/test_backend_storage.py:28-45` | def test_default_migration_is_idempotent_and_backend_owns_rows(self) | 1 | test |
| `test_backend_storage.BackendStorageTests.test_module_ownership_fences_cross_module_writes` | method | `tests/test_backend_storage.py:47-59` | def test_module_ownership_fences_cross_module_writes(self) | 1 | test |
| `test_backend_storage.BackendStorageTests.test_failed_migration_rolls_back_table_and_ledger` | method | `tests/test_backend_storage.py:61-71` | def test_failed_migration_rolls_back_table_and_ledger(self) | 1 | test |
| `test_backend_storage.BackendStorageTests.test_rollback_removes_owned_table_and_preserves_integrity` | method | `tests/test_backend_storage.py:73-83` | def test_rollback_removes_owned_table_and_preserves_integrity(self) | 1 | test |
| `test_backend_storage.BackendStorageTests.test_changed_definition_and_invalid_plan_fail_closed` | method | `tests/test_backend_storage.py:85-106` | def test_changed_definition_and_invalid_plan_fail_closed(self) | 1 | test |
| `test_backend_task_capability.TaskCapabilityTests` | class | `tests/test_backend_task_capability.py:12-54` | class TaskCapabilityTests(unittest.TestCase) | 1 | test |
| `test_backend_task_capability.TaskCapabilityTests.test_manifest_allows_only_granted_operation_and_path` | method | `tests/test_backend_task_capability.py:13-20` | def test_manifest_allows_only_granted_operation_and_path(self) | 1 | test |
| `test_backend_task_capability.TaskCapabilityTests.test_disallowed_operation_and_path_fail_closed` | method | `tests/test_backend_task_capability.py:22-31` | def test_disallowed_operation_and_path_fail_closed(self) | 1 | test |
| `test_backend_task_capability.TaskCapabilityTests.test_relative_and_symlink_escape_paths_are_rejected` | method | `tests/test_backend_task_capability.py:33-45` | def test_relative_and_symlink_escape_paths_are_rejected(self) | 1 | test |
| `test_backend_task_capability.TaskCapabilityTests.test_sensitive_paths_are_rejected_even_inside_an_allowed_root` | method | `tests/test_backend_task_capability.py:47-54` | def test_sensitive_paths_are_rejected_even_inside_an_allowed_root(self) | 1 | test |
| `test_backend_windows_agent.node` | function | `tests/test_backend_windows_agent.py:16-25` | def node(**changes) | 6 | test |
| `test_backend_windows_agent.job` | function | `tests/test_backend_windows_agent.py:28-39` | def job(**changes) | 10 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests` | class | `tests/test_backend_windows_agent.py:42-105` | class BackendWindowsAgentTests(unittest.TestCase) | 1 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.setUp` | method | `tests/test_backend_windows_agent.py:43-47` | def setUp(self) | 35 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.test_identity_heartbeat_and_capability_routing` | method | `tests/test_backend_windows_agent.py:49-55` | def test_identity_heartbeat_and_capability_routing(self) | 1 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.test_stale_or_incompatible_nodes_are_not_used` | method | `tests/test_backend_windows_agent.py:57-64` | def test_stale_or_incompatible_nodes_are_not_used(self) | 1 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.test_bounded_job_idempotency_lease_and_checksum_completion` | method | `tests/test_backend_windows_agent.py:66-83` | def test_bounded_job_idempotency_lease_and_checksum_completion(self) | 1 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.test_disconnect_requeues_and_duplicate_or_foreign_leases_fail` | method | `tests/test_backend_windows_agent.py:85-92` | def test_disconnect_requeues_and_duplicate_or_foreign_leases_fail(self) | 1 | test |
| `test_backend_windows_agent.BackendWindowsAgentTests.test_invalid_manifest_and_job_schema_fail_closed` | method | `tests/test_backend_windows_agent.py:94-105` | def test_invalid_manifest_and_job_schema_fail_closed(self) | 1 | test |
| `test_batch_cycle.BatchCycleFailurePropagationTests` | class | `tests/test_batch_cycle.py:13-69` | class BatchCycleFailurePropagationTests(unittest.TestCase) | 1 | test |
| `test_batch_cycle.BatchCycleFailurePropagationTests.run_fixture` | method | `tests/test_batch_cycle.py:14-55` | def run_fixture(self, *, batch_status: str, batch_status_rc: int=0, qc_rc: int=0) | 1 | test |
| `test_batch_cycle.BatchCycleFailurePropagationTests.test_batch_status_failure_is_not_hidden` | method | `tests/test_batch_cycle.py:57-61` | def test_batch_status_failure_is_not_hidden(self) | 1 | test |
| `test_batch_cycle.BatchCycleFailurePropagationTests.test_qc_failure_stops_before_publication` | method | `tests/test_batch_cycle.py:63-69` | def test_qc_failure_stops_before_publication(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests` | class | `tests/test_ci_workflow.py:18-187` | class CIWorkflowTests(unittest.TestCase) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_python_and_ios_jobs_have_runners_and_test_commands` | method | `tests/test_ci_workflow.py:19-36` | def test_python_and_ios_jobs_have_runners_and_test_commands(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_fallback_receipt_runs_without_prerequisite_checkout` | method | `tests/test_ci_workflow.py:38-47` | def test_fallback_receipt_runs_without_prerequisite_checkout(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_workflow_pins_actions_and_uploads_bounded_receipt` | method | `tests/test_ci_workflow.py:49-64` | def test_workflow_pins_actions_and_uploads_bounded_receipt(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_report_rejects_raw_payloads_and_extra_fields` | method | `tests/test_ci_workflow.py:66-79` | def test_report_rejects_raw_payloads_and_extra_fields(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_report_rejects_escape_and_symlink_without_writing` | method | `tests/test_ci_workflow.py:81-94` | def test_report_rejects_escape_and_symlink_without_writing(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_cli_writes_complete_bounded_receipt` | method | `tests/test_ci_workflow.py:96-135` | def test_cli_writes_complete_bounded_receipt(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_public_check_and_report_clis` | method | `tests/test_ci_workflow.py:137-177` | def test_public_check_and_report_clis(self) | 1 | test |
| `test_ci_workflow.CIWorkflowTests.test_secret_and_workflow_boundaries_reject_common_unsafe_inputs` | method | `tests/test_ci_workflow.py:179-187` | def test_secret_and_workflow_boundaries_reject_common_unsafe_inputs(self) | 1 | test |
| `test_cloudflare_dashboard.call` | function | `tests/test_cloudflare_dashboard.mjs:32-32` | async function call(path, token = "") { | 7 | test |
| `test_cloudflare_heartbeat.call` | function | `tests/test_cloudflare_heartbeat.mjs:36-36` | async function call(path, method = "GET", body, token = "") { | 7 | test |
| `test_cloudflare_rate_limit.request` | function | `tests/test_cloudflare_rate_limit.mjs:26-26` | const request = (ip) => new Request("https://worker.test/api", { headers: { "CF-Connecting-IP": ip } }); | 23 | test |
| `test_core_budget.CoreBudgetTests` | class | `tests/test_core_budget.py:6-77` | class CoreBudgetTests(unittest.TestCase) | 1 | test |
| `test_core_budget.CoreBudgetTests.test_global_capacity_and_device_limits` | method | `tests/test_core_budget.py:7-14` | def test_global_capacity_and_device_limits(self) | 1 | test |
| `test_core_budget.CoreBudgetTests.test_guardian_reservation_blocks_lower_priority_without_preemption` | method | `tests/test_core_budget.py:16-23` | def test_guardian_reservation_blocks_lower_priority_without_preemption(self) | 1 | test |
| `test_core_budget.CoreBudgetTests.test_guardian_lock_preserves_disjoint_budget_capacity` | method | `tests/test_core_budget.py:25-40` | def test_guardian_lock_preserves_disjoint_budget_capacity(self) | 1 | test |
| `test_core_budget.CoreBudgetTests.test_guardian_reservation_is_not_starved_by_repeated_safe_work` | method | `tests/test_core_budget.py:42-62` | def test_guardian_reservation_is_not_starved_by_repeated_safe_work(self) | 1 | test |
| `test_core_budget.CoreBudgetTests.test_release_is_fenced_and_invalid_configuration_is_rejected` | method | `tests/test_core_budget.py:64-77` | def test_release_is_fenced_and_invalid_configuration_is_rejected(self) | 1 | test |
| `test_core_controls.CoreControlTests` | class | `tests/test_core_controls.py:9-64` | class CoreControlTests(unittest.TestCase) | 1 | test |
| `test_core_controls.CoreControlTests.test_stop_blocks_dispatch_and_survives_restart` | method | `tests/test_core_controls.py:10-25` | def test_stop_blocks_dispatch_and_survives_restart(self) | 1 | test |
| `test_core_controls.CoreControlTests.test_pause_and_resume_preserve_pending_approval` | method | `tests/test_core_controls.py:27-57` | def test_pause_and_resume_preserve_pending_approval(self) | 1 | test |
| `test_core_controls.CoreControlTests.test_control_reason_is_bounded` | method | `tests/test_core_controls.py:59-64` | def test_control_reason_is_bounded(self) | 1 | test |
| `test_core_dependencies.CoreDependencyTests` | class | `tests/test_core_dependencies.py:9-39` | class CoreDependencyTests(unittest.TestCase) | 1 | test |
| `test_core_dependencies.CoreDependencyTests.test_pending_dependency_does_not_block_ready_work_and_resumes_after_result` | method | `tests/test_core_dependencies.py:10-19` | def test_pending_dependency_does_not_block_ready_work_and_resumes_after_result(self) | 1 | test |
| `test_core_dependencies.CoreDependencyTests.test_missing_and_cyclic_dependencies_are_not_claimed` | method | `tests/test_core_dependencies.py:21-29` | def test_missing_and_cyclic_dependencies_are_not_claimed(self) | 1 | test |
| `test_core_dependencies.CoreDependencyTests.test_dependency_declarations_are_validated_and_dependents_are_discoverable` | method | `tests/test_core_dependencies.py:31-39` | def test_dependency_declarations_are_validated_and_dependents_are_discoverable(self) | 1 | test |
| `test_core_dispatch.CoreDispatchTests` | class | `tests/test_core_dispatch.py:9-69` | class CoreDispatchTests(unittest.TestCase) | 1 | test |
| `test_core_dispatch.CoreDispatchTests.test_dispatch_contains_scope_acceptance_and_correlation_and_reconstructs` | method | `tests/test_core_dispatch.py:10-33` | def test_dispatch_contains_scope_acceptance_and_correlation_and_reconstructs(self) | 1 | test |
| `test_core_dispatch.CoreDispatchTests.test_one_claim_and_one_ack_are_fenced_and_idempotent` | method | `tests/test_core_dispatch.py:35-58` | def test_one_claim_and_one_ack_are_fenced_and_idempotent(self) | 1 | test |
| `test_core_dispatch.CoreDispatchTests.test_dispatch_payload_conflicts_and_unbounded_values_are_rejected` | method | `tests/test_core_dispatch.py:60-69` | def test_dispatch_payload_conflicts_and_unbounded_values_are_rejected(self) | 1 | test |
| `test_core_event_guard.CoreEventGuardTests` | class | `tests/test_core_event_guard.py:12-57` | class CoreEventGuardTests(unittest.TestCase) | 1 | test |
| `test_core_event_guard.CoreEventGuardTests.test_duplicate_event_id_is_idempotent_and_storm_is_bounded` | method | `tests/test_core_event_guard.py:13-30` | def test_duplicate_event_id_is_idempotent_and_storm_is_bounded(self) | 1 | test |
| `test_core_event_guard.CoreEventGuardTests.test_repeated_failures_quarantine_and_redact_diagnostics` | method | `tests/test_core_event_guard.py:32-57` | def test_repeated_failures_quarantine_and_redact_diagnostics(self) | 1 | test |
| `test_core_event_sessions.CoreEventSessionTests` | class | `tests/test_core_event_sessions.py:9-57` | class CoreEventSessionTests(unittest.TestCase) | 1 | test |
| `test_core_event_sessions.CoreEventSessionTests.test_event_session_is_separate_and_reconstructs_causal_chain` | method | `tests/test_core_event_sessions.py:10-31` | def test_event_session_is_separate_and_reconstructs_causal_chain(self) | 1 | test |
| `test_core_event_sessions.CoreEventSessionTests.test_event_replay_ack_is_durable_and_event_ids_are_idempotent` | method | `tests/test_core_event_sessions.py:33-47` | def test_event_replay_ack_is_durable_and_event_ids_are_idempotent(self) | 1 | test |
| `test_core_event_sessions.CoreEventSessionTests.test_event_session_rejects_unbounded_detail_and_invalid_replay_limit` | method | `tests/test_core_event_sessions.py:49-57` | def test_event_session_rejects_unbounded_detail_and_invalid_replay_limit(self) | 1 | test |
| `test_core_fault_injection.CoreFaultInjectionTests` | class | `tests/test_core_fault_injection.py:9-55` | class CoreFaultInjectionTests(unittest.TestCase) | 1 | test |
| `test_core_fault_injection.CoreFaultInjectionTests.test_committed_completion_survives_reopen_without_phantom_replay` | method | `tests/test_core_fault_injection.py:10-25` | def test_committed_completion_survives_reopen_without_phantom_replay(self) | 1 | test |
| `test_core_fault_injection.CoreFaultInjectionTests.test_priority_fifo_is_stable_after_a_failed_claim` | method | `tests/test_core_fault_injection.py:27-37` | def test_priority_fifo_is_stable_after_a_failed_claim(self) | 1 | test |
| `test_core_fault_injection.CoreFaultInjectionTests.test_dispatch_claim_is_isolated_and_wrong_executor_cannot_ack` | method | `tests/test_core_fault_injection.py:39-55` | def test_dispatch_claim_is_isolated_and_wrong_executor_cannot_ack(self) | 1 | test |
| `test_core_intents.intent` | function | `tests/test_core_intents.py:9-21` | def intent(*, request_id='REQ-1', risk='safe', action='inspect', **extra) | 1 | test |
| `test_core_intents.CoreIntentTests` | class | `tests/test_core_intents.py:24-69` | class CoreIntentTests(unittest.TestCase) | 1 | test |
| `test_core_intents.CoreIntentTests.test_safe_owner_intent_is_idempotently_enqueued` | method | `tests/test_core_intents.py:25-33` | def test_safe_owner_intent_is_idempotently_enqueued(self) | 1 | test |
| `test_core_intents.CoreIntentTests.test_ambiguous_or_sensitive_intent_waits_for_exact_explicit_approval` | method | `tests/test_core_intents.py:35-48` | def test_ambiguous_or_sensitive_intent_waits_for_exact_explicit_approval(self) | 1 | test |
| `test_core_intents.CoreIntentTests.test_rejected_sensitive_intent_is_recorded_without_a_task` | method | `tests/test_core_intents.py:50-59` | def test_rejected_sensitive_intent_is_recorded_without_a_task(self) | 1 | test |
| `test_core_intents.CoreIntentTests.test_intent_conflicts_and_invalid_contracts_are_rejected` | method | `tests/test_core_intents.py:61-69` | def test_intent_conflicts_and_invalid_contracts_are_rejected(self) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests` | class | `tests/test_core_model_policy.py:6-55` | class CoreModelPolicyTests(unittest.TestCase) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests.setUp` | method | `tests/test_core_model_policy.py:7-8` | def setUp(self) | 35 | test |
| `test_core_model_policy.CoreModelPolicyTests.test_available_requested_alias_is_selected` | method | `tests/test_core_model_policy.py:10-15` | def test_available_requested_alias_is_selected(self) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests.test_unsupported_alias_blocks_without_silent_fallback` | method | `tests/test_core_model_policy.py:17-22` | def test_unsupported_alias_blocks_without_silent_fallback(self) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests.test_fallback_requires_explicit_opt_in_and_target` | method | `tests/test_core_model_policy.py:24-40` | def test_fallback_requires_explicit_opt_in_and_target(self) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests.test_unavailable_fallback_is_blocked` | method | `tests/test_core_model_policy.py:42-49` | def test_unavailable_fallback_is_blocked(self) | 1 | test |
| `test_core_model_policy.CoreModelPolicyTests.test_alias_validation_is_bounded` | method | `tests/test_core_model_policy.py:51-55` | def test_alias_validation_is_bounded(self) | 1 | test |
| `test_core_priority.CorePriorityTests` | class | `tests/test_core_priority.py:8-38` | class CorePriorityTests(unittest.TestCase) | 1 | test |
| `test_core_priority.CorePriorityTests.test_priority_fifo_and_blocked_work` | method | `tests/test_core_priority.py:9-23` | def test_priority_fifo_and_blocked_work(self) | 1 | test |
| `test_core_priority.CorePriorityTests.test_leased_block_requires_current_lease_and_can_reenter_fifo` | method | `tests/test_core_priority.py:25-38` | def test_leased_block_requires_current_lease_and_can_reenter_fifo(self) | 1 | test |
| `test_core_queue_replay.CoreQueueReplayTests` | class | `tests/test_core_queue_replay.py:8-42` | class CoreQueueReplayTests(unittest.TestCase) | 1 | test |
| `test_core_queue_replay.CoreQueueReplayTests.test_events_survive_restart_and_are_replayed_once_after_ack` | method | `tests/test_core_queue_replay.py:9-31` | def test_events_survive_restart_and_are_replayed_once_after_ack(self) | 1 | test |
| `test_core_queue_replay.CoreQueueReplayTests.test_replay_is_consumer_scoped_and_bounded` | method | `tests/test_core_queue_replay.py:33-42` | def test_replay_is_consumer_scoped_and_bounded(self) | 1 | test |
| `test_core_registry.CoreRegistryTests` | class | `tests/test_core_registry.py:12-47` | class CoreRegistryTests(unittest.TestCase) | 1 | test |
| `test_core_registry.CoreRegistryTests.test_config_registers_ten_stable_modules_without_business` | method | `tests/test_core_registry.py:13-23` | def test_config_registers_ten_stable_modules_without_business(self) | 1 | test |
| `test_core_registry.CoreRegistryTests.test_registry_and_capabilities_are_immutable` | method | `tests/test_core_registry.py:25-31` | def test_registry_and_capabilities_are_immutable(self) | 1 | test |
| `test_core_registry.CoreRegistryTests.test_invalid_identity_scope_and_business_config_are_rejected` | method | `tests/test_core_registry.py:33-47` | def test_invalid_identity_scope_and_business_config_are_rejected(self) | 1 | test |
| `test_core_sessions.CoreSessionTests` | class | `tests/test_core_sessions.py:9-67` | class CoreSessionTests(unittest.TestCase) | 1 | test |
| `test_core_sessions.CoreSessionTests.test_parent_session_reconstructs_decisions_handoffs_and_receipts_after_restart` | method | `tests/test_core_sessions.py:10-42` | def test_parent_session_reconstructs_decisions_handoffs_and_receipts_after_restart(self) | 1 | test |
| `test_core_sessions.CoreSessionTests.test_receipt_and_checkpoint_replays_are_idempotent_and_conflicts_are_rejected` | method | `tests/test_core_sessions.py:44-57` | def test_receipt_and_checkpoint_replays_are_idempotent_and_conflicts_are_rejected(self) | 1 | test |
| `test_core_sessions.CoreSessionTests.test_store_reuses_an_existing_connection_and_bounds_inputs` | method | `tests/test_core_sessions.py:59-67` | def test_store_reuses_an_existing_connection_and_bounds_inputs(self) | 1 | test |
| `test_core_timeline.CoreTimelineTests` | class | `tests/test_core_timeline.py:9-61` | class CoreTimelineTests(unittest.TestCase) | 1 | test |
| `test_core_timeline.CoreTimelineTests.test_timeline_joins_sources_states_and_hashed_outcomes` | method | `tests/test_core_timeline.py:10-43` | def test_timeline_joins_sources_states_and_hashed_outcomes(self) | 1 | test |
| `test_core_timeline.CoreTimelineTests.test_progress_is_bounded_and_query_is_read_only` | method | `tests/test_core_timeline.py:45-61` | def test_progress_is_bounded_and_query_is_read_only(self) | 1 | test |
| `test_finance_acceptance.FinanceAcceptanceTests` | class | `tests/test_finance_acceptance.py:21-49` | class FinanceAcceptanceTests(unittest.TestCase) | 1 | test |
| `test_finance_acceptance.FinanceAcceptanceTests.test_revocation_stops_sync_and_fixture_budget_report_remain_stable` | method | `tests/test_finance_acceptance.py:22-49` | def test_revocation_stops_sync_and_fixture_budget_report_remain_stable(self) | 1 | test |
| `test_finance_advice.FinanceAdviceTests` | class | `tests/test_finance_advice.py:19-68` | class FinanceAdviceTests(unittest.TestCase) | 1 | test |
| `test_finance_advice.FinanceAdviceTests.store` | method | `tests/test_finance_advice.py:20-31` | def store(self) | 44 | test |
| `test_finance_advice.FinanceAdviceTests.test_without_consent_advice_is_bounded_and_requires_consent` | method | `tests/test_finance_advice.py:33-43` | def test_without_consent_advice_is_bounded_and_requires_consent(self) | 1 | test |
| `test_finance_advice.FinanceAdviceTests.test_explicit_consent_then_approval_makes_notification_ready` | method | `tests/test_finance_advice.py:45-56` | def test_explicit_consent_then_approval_makes_notification_ready(self) | 1 | test |
| `test_finance_advice.FinanceAdviceTests.test_approval_without_consent_and_suppression_fail_closed` | method | `tests/test_finance_advice.py:58-68` | def test_approval_without_consent_and_suppression_fail_closed(self) | 1 | test |
| `test_finance_alerts.FinanceAlertTests` | class | `tests/test_finance_alerts.py:19-61` | class FinanceAlertTests(unittest.TestCase) | 1 | test |
| `test_finance_alerts.FinanceAlertTests.test_recurring_alert_is_explainable_source_linked_and_suppressible` | method | `tests/test_finance_alerts.py:20-37` | def test_recurring_alert_is_explainable_source_linked_and_suppressible(self) | 1 | test |
| `test_finance_alerts.FinanceAlertTests.test_unusual_alert_uses_a_bounded_explainable_threshold` | method | `tests/test_finance_alerts.py:39-53` | def test_unusual_alert_uses_a_bounded_explainable_threshold(self) | 1 | test |
| `test_finance_alerts.FinanceAlertTests.test_scope_isolation_and_invalid_multiplier_are_enforced` | method | `tests/test_finance_alerts.py:55-61` | def test_scope_isolation_and_invalid_multiplier_are_enforced(self) | 1 | test |
| `test_finance_dashboard.FinanceDashboardTests` | class | `tests/test_finance_dashboard.py:19-59` | class FinanceDashboardTests(unittest.TestCase) | 1 | test |
| `test_finance_dashboard.FinanceDashboardTests.test_estimated_balances_are_scoped_labeled_and_timestamped` | method | `tests/test_finance_dashboard.py:20-32` | def test_estimated_balances_are_scoped_labeled_and_timestamped(self) | 1 | test |
| `test_finance_dashboard.FinanceDashboardTests.test_reconciled_balance_overrides_estimate_without_leaking_scope` | method | `tests/test_finance_dashboard.py:34-45` | def test_reconciled_balance_overrides_estimate_without_leaking_scope(self) | 1 | test |
| `test_finance_dashboard.FinanceDashboardTests.test_authoritative_balance_must_match_a_known_account_and_status` | method | `tests/test_finance_dashboard.py:47-59` | def test_authoritative_balance_must_match_a_known_account_and_status(self) | 1 | test |
| `test_finance_ingestion.snapshot` | function | `tests/test_finance_ingestion.py:20-28` | def snapshot() | 17 | test |
| `test_finance_ingestion.FinanceIngestionTests` | class | `tests/test_finance_ingestion.py:31-91` | class FinanceIngestionTests(unittest.TestCase) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_sync_preserves_original_ids_timestamps_and_integer_satang` | method | `tests/test_finance_ingestion.py:32-39` | def test_sync_preserves_original_ids_timestamps_and_integer_satang(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_replaying_identical_snapshot_is_idempotent` | method | `tests/test_finance_ingestion.py:41-46` | def test_replaying_identical_snapshot_is_idempotent(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_newer_source_revision_updates_one_row_without_duplication` | method | `tests/test_finance_ingestion.py:48-54` | def test_newer_source_revision_updates_one_row_without_duplication(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_scope_isolation_is_required_for_reads` | method | `tests/test_finance_ingestion.py:56-59` | def test_scope_isolation_is_required_for_reads(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_source_mappings_are_normalized_without_losing_original_ids` | method | `tests/test_finance_ingestion.py:61-73` | def test_source_mappings_are_normalized_without_losing_original_ids(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_invalid_precision_and_timestamps_fail_closed` | method | `tests/test_finance_ingestion.py:75-79` | def test_invalid_precision_and_timestamps_fail_closed(self) | 1 | test |
| `test_finance_ingestion.FinanceIngestionTests.test_conflicting_revision_rolls_back_the_whole_snapshot` | method | `tests/test_finance_ingestion.py:81-91` | def test_conflicting_revision_rolls_back_the_whole_snapshot(self) | 1 | test |
| `test_finance_mira_audit.MiraAuditTests` | class | `tests/test_finance_mira_audit.py:10-64` | class MiraAuditTests(unittest.TestCase) | 1 | test |
| `test_finance_mira_audit.MiraAuditTests.snapshot` | method | `tests/test_finance_mira_audit.py:11-40` | def snapshot(self) | 17 | test |
| `test_finance_mira_audit.MiraAuditTests.test_valid_snapshot_is_bounded_and_read_only` | method | `tests/test_finance_mira_audit.py:42-45` | def test_valid_snapshot_is_bounded_and_read_only(self) | 1 | test |
| `test_finance_mira_audit.MiraAuditTests.test_worker_write_capability_does_not_expand_archon_scope` | method | `tests/test_finance_mira_audit.py:47-50` | def test_worker_write_capability_does_not_expand_archon_scope(self) | 1 | test |
| `test_finance_mira_audit.MiraAuditTests.test_binding_and_auth_boundary_mismatch_is_rejected` | method | `tests/test_finance_mira_audit.py:52-56` | def test_binding_and_auth_boundary_mismatch_is_rejected(self) | 1 | test |
| `test_finance_mira_audit.MiraAuditTests.test_secret_values_are_not_part_of_evidence` | method | `tests/test_finance_mira_audit.py:58-64` | def test_secret_values_are_not_part_of_evidence(self) | 1 | test |
| `test_finance_mira_connector.MiraConnectorTokenTests` | class | `tests/test_finance_mira_connector.py:9-41` | class MiraConnectorTokenTests(unittest.TestCase) | 1 | test |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_issue_is_short_lived_scoped_and_identity_bound` | method | `tests/test_finance_mira_connector.py:10-17` | def test_issue_is_short_lived_scoped_and_identity_bound(self) | 1 | test |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_revoke_is_immediate_and_audit_is_redacted` | method | `tests/test_finance_mira_connector.py:19-29` | def test_revoke_is_immediate_and_audit_is_redacted(self) | 1 | test |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_token_registration_is_idempotent_but_conflicts_fail` | method | `tests/test_finance_mira_connector.py:31-36` | def test_token_registration_is_idempotent_but_conflicts_fail(self) | 1 | test |
| `test_finance_mira_connector.MiraConnectorTokenTests.test_ttl_is_bounded_by_the_shared_connector_policy` | method | `tests/test_finance_mira_connector.py:38-41` | def test_ttl_is_bounded_by_the_shared_connector_policy(self) | 1 | test |
| `test_finance_paper.FinancePaperTests` | class | `tests/test_finance_paper.py:21-74` | class FinancePaperTests(unittest.TestCase) | 1 | test |
| `test_finance_paper.FinancePaperTests.test_paper_cash_and_positions_are_separate_from_finance_store` | method | `tests/test_finance_paper.py:22-36` | def test_paper_cash_and_positions_are_separate_from_finance_store(self) | 1 | test |
| `test_finance_paper.FinancePaperTests.test_duplicate_order_is_idempotent_and_insufficient_cash_fails` | method | `tests/test_finance_paper.py:38-47` | def test_duplicate_order_is_idempotent_and_insufficient_cash_fails(self) | 1 | test |
| `test_finance_paper.FinancePaperTests.test_sell_cannot_create_a_position_or_touch_real_accounts` | method | `tests/test_finance_paper.py:49-54` | def test_sell_cannot_create_a_position_or_touch_real_accounts(self) | 1 | test |
| `test_finance_paper.FinancePaperTests.test_fill_policy_records_spread_slippage_and_fee` | method | `tests/test_finance_paper.py:56-65` | def test_fill_policy_records_spread_slippage_and_fee(self) | 1 | test |
| `test_finance_paper.FinancePaperTests.test_market_hours_and_liquidity_reject_invalid_fills` | method | `tests/test_finance_paper.py:67-74` | def test_market_hours_and_liquidity_reject_invalid_fills(self) | 1 | test |
| `test_finance_performance.FinancePerformanceTests` | class | `tests/test_finance_performance.py:17-48` | class FinancePerformanceTests(unittest.TestCase) | 1 | test |
| `test_finance_performance.FinancePerformanceTests.test_pnl_and_drawdown_replay_is_reproducible` | method | `tests/test_finance_performance.py:18-26` | def test_pnl_and_drawdown_replay_is_reproducible(self) | 1 | test |
| `test_finance_performance.FinancePerformanceTests.test_future_trade_is_not_used_at_an_earlier_mark` | method | `tests/test_finance_performance.py:28-35` | def test_future_trade_is_not_used_at_an_earlier_mark(self) | 1 | test |
| `test_finance_performance.FinancePerformanceTests.test_split_and_invalid_future_or_missing_evidence_fail_closed` | method | `tests/test_finance_performance.py:37-48` | def test_split_and_invalid_future_or_missing_evidence_fail_closed(self) | 1 | test |
| `test_finance_planning.FinancePlanningTests` | class | `tests/test_finance_planning.py:20-54` | class FinancePlanningTests(unittest.TestCase) | 1 | test |
| `test_finance_planning.FinancePlanningTests.test_forecast_is_uncertain_and_uses_historical_net` | method | `tests/test_finance_planning.py:21-34` | def test_forecast_is_uncertain_and_uses_historical_net(self) | 1 | test |
| `test_finance_planning.FinancePlanningTests.test_goal_progress_does_not_double_debit_transaction_totals` | method | `tests/test_finance_planning.py:36-47` | def test_goal_progress_does_not_double_debit_transaction_totals(self) | 1 | test |
| `test_finance_planning.FinancePlanningTests.test_invalid_goal_and_duplicate_goal_fail_closed` | method | `tests/test_finance_planning.py:49-54` | def test_invalid_goal_and_duplicate_goal_fail_closed(self) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests` | class | `tests/test_finance_reconciliation.py:17-59` | class FinanceReconciliationTests(unittest.TestCase) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests.test_transfer_is_applied_once_and_has_zero_net_effect` | method | `tests/test_finance_reconciliation.py:18-25` | def test_transfer_is_applied_once_and_has_zero_net_effect(self) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests.test_savings_has_transfer_semantics_and_adjustment_is_applied_once` | method | `tests/test_finance_reconciliation.py:27-35` | def test_savings_has_transfer_semantics_and_adjustment_is_applied_once(self) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests.test_newer_revision_replaces_effect_without_creating_a_second_operation` | method | `tests/test_finance_reconciliation.py:37-42` | def test_newer_revision_replaces_effect_without_creating_a_second_operation(self) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests.test_scope_isolation_and_mapping_input_are_enforced` | method | `tests/test_finance_reconciliation.py:44-50` | def test_scope_isolation_and_mapping_input_are_enforced(self) | 1 | test |
| `test_finance_reconciliation.FinanceReconciliationTests.test_invalid_transfer_and_stale_conflict_fail_closed` | method | `tests/test_finance_reconciliation.py:52-59` | def test_invalid_transfer_and_stale_conflict_fail_closed(self) | 1 | test |
| `test_finance_reports.FinanceReportTests` | class | `tests/test_finance_reports.py:19-53` | class FinanceReportTests(unittest.TestCase) | 1 | test |
| `test_finance_reports.FinanceReportTests.test_summary_totals_breakdowns_and_trend_match_fixture_ledger` | method | `tests/test_finance_reports.py:20-37` | def test_summary_totals_breakdowns_and_trend_match_fixture_ledger(self) | 1 | test |
| `test_finance_reports.FinanceReportTests.test_period_filter_and_person_scope_are_applied_before_aggregation` | method | `tests/test_finance_reports.py:39-46` | def test_period_filter_and_person_scope_are_applied_before_aggregation(self) | 1 | test |
| `test_finance_reports.FinanceReportTests.test_reversed_period_and_bad_date_fail_closed` | method | `tests/test_finance_reports.py:48-53` | def test_reversed_period_and_bad_date_fail_closed(self) | 1 | test |
| `test_foundation.FoundationTests` | class | `tests/test_foundation.py:10-62` | class FoundationTests(unittest.TestCase) | 1 | test |
| `test_foundation.FoundationTests.test_fifo_same_priority` | method | `tests/test_foundation.py:11-18` | def test_fifo_same_priority(self) | 1 | test |
| `test_foundation.FoundationTests.test_priority` | method | `tests/test_foundation.py:19-25` | def test_priority(self) | 1 | test |
| `test_foundation.FoundationTests.test_lease_receipt` | method | `tests/test_foundation.py:26-35` | def test_lease_receipt(self) | 1 | test |
| `test_foundation.FoundationTests.test_guardian_waits_for_active` | method | `tests/test_foundation.py:36-45` | def test_guardian_waits_for_active(self) | 1 | test |
| `test_foundation.FoundationTests.test_guardian_waiting_blocks_background_claim` | method | `tests/test_foundation.py:46-53` | def test_guardian_waiting_blocks_background_claim(self) | 1 | test |
| `test_foundation.FoundationTests.test_release_example_blocked` | method | `tests/test_foundation.py:54-58` | def test_release_example_blocked(self) | 1 | test |
| `test_foundation.FoundationTests.test_handoff_requires_every_gate` | method | `tests/test_foundation.py:59-62` | def test_handoff_requires_every_gate(self) | 1 | test |
| `test_git_policy.PolicyTests` | class | `tests/test_git_policy.py:3-15` | class PolicyTests(unittest.TestCase) | 1 | test |
| `test_git_policy.PolicyTests.test_good_branch` | method | `tests/test_git_policy.py:4-6` | def test_good_branch(self) | 1 | test |
| `test_git_policy.PolicyTests.test_bad_branch` | method | `tests/test_git_policy.py:7-9` | def test_bad_branch(self) | 1 | test |
| `test_git_policy.PolicyTests.test_good_commit` | method | `tests/test_git_policy.py:10-12` | def test_good_commit(self) | 1 | test |
| `test_git_policy.PolicyTests.test_bad_commit` | method | `tests/test_git_policy.py:13-15` | def test_bad_commit(self) | 1 | test |
| `test_guardian_controller.GuardianControllerTests` | class | `tests/test_guardian_controller.py:9-86` | class GuardianControllerTests(unittest.TestCase) | 1 | test |
| `test_guardian_controller.GuardianControllerTests._manager` | method | `tests/test_guardian_controller.py:10-22` | def _manager(self, root: Path, *, runner=None, control_dir=None) | 1 | test |
| `test_guardian_controller.GuardianControllerTests.test_verified_artifact_is_the_only_launchable_controller` | method | `tests/test_guardian_controller.py:24-37` | def test_verified_artifact_is_the_only_launchable_controller(self) | 1 | test |
| `test_guardian_controller.GuardianControllerTests.test_digest_change_and_symlink_fail_closed` | method | `tests/test_guardian_controller.py:39-51` | def test_digest_change_and_symlink_fail_closed(self) | 1 | test |
| `test_guardian_controller.GuardianControllerTests.test_control_markers_are_honored_before_artifact_execution` | method | `tests/test_guardian_controller.py:53-62` | def test_control_markers_are_honored_before_artifact_execution(self) | 1 | test |
| `test_guardian_controller.GuardianControllerTests.test_command_must_be_direct_and_artifact_must_be_private_to_group` | method | `tests/test_guardian_controller.py:64-86` | def test_command_must_be_direct_and_artifact_must_be_private_to_group(self) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests` | class | `tests/test_guardian_cutover.py:10-107` | class GuardianCutoverTests(unittest.TestCase) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.setUp` | method | `tests/test_guardian_cutover.py:11-20` | def setUp(self) | 35 | test |
| `test_guardian_cutover.GuardianCutoverTests._readiness` | method | `tests/test_guardian_cutover.py:22-33` | def _readiness(self, **changes) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.test_ready_cutover_fences_old_writer_and_keeps_one_authority` | method | `tests/test_guardian_cutover.py:35-46` | def test_ready_cutover_fences_old_writer_and_keeps_one_authority(self) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.test_unverified_sync_degrades_without_handoff` | method | `tests/test_guardian_cutover.py:48-61` | def test_unverified_sync_degrades_without_handoff(self) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.test_capacity_and_schema_mismatch_do_not_fabricate_readiness` | method | `tests/test_guardian_cutover.py:63-70` | def test_capacity_and_schema_mismatch_do_not_fabricate_readiness(self) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.test_failback_requires_failed_health_and_fences_bad_standby` | method | `tests/test_guardian_cutover.py:72-88` | def test_failback_requires_failed_health_and_fences_bad_standby(self) | 1 | test |
| `test_guardian_cutover.GuardianCutoverTests.test_control_marker_blocks_cutover` | method | `tests/test_guardian_cutover.py:90-107` | def test_control_marker_blocks_cutover(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests` | class | `tests/test_guardian_failure.py:10-87` | class GuardianFailureTests(unittest.TestCase) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.setUp` | method | `tests/test_guardian_failure.py:11-14` | def setUp(self) | 35 | test |
| `test_guardian_failure.GuardianFailureTests.test_component_failure_requires_healthy_upstream_observations` | method | `tests/test_guardian_failure.py:16-28` | def test_component_failure_requires_healthy_upstream_observations(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.test_dependency_failure_correlates_to_the_first_upstream_root` | method | `tests/test_guardian_failure.py:30-41` | def test_dependency_failure_correlates_to_the_first_upstream_root(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.test_host_failure_takes_precedence_over_component_and_dependency` | method | `tests/test_guardian_failure.py:43-54` | def test_host_failure_takes_precedence_over_component_and_dependency(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.test_unknown_upstream_state_is_not_called_a_component_failure` | method | `tests/test_guardian_failure.py:56-66` | def test_unknown_upstream_state_is_not_called_a_component_failure(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.test_healthy_observations_are_not_failures` | method | `tests/test_guardian_failure.py:68-79` | def test_healthy_observations_are_not_failures(self) | 1 | test |
| `test_guardian_failure.GuardianFailureTests.test_malformed_observations_and_evidence_are_rejected` | method | `tests/test_guardian_failure.py:81-87` | def test_malformed_observations_and_evidence_are_rejected(self) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests` | class | `tests/test_guardian_fault_injection.py:16-165` | class GuardianFaultInjectionTests(unittest.TestCase) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests._controller` | method | `tests/test_guardian_fault_injection.py:17-27` | def _controller(self, root: Path, controls: Path, runner) | 2 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p0_controls_survive_recovery_denial` | method | `tests/test_guardian_fault_injection.py:29-45` | def test_p0_controls_survive_recovery_denial(self) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p1_crash_loop_is_bounded_and_history_is_retained` | method | `tests/test_guardian_fault_injection.py:47-71` | def test_p1_crash_loop_is_bounded_and_history_is_retained(self) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p1_crash_loop_is_bounded_and_history_is_retained.crash` | function | `tests/test_guardian_fault_injection.py:51-53` | def crash(*args) | 5 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p2_stale_writer_cannot_survive_cutover` | method | `tests/test_guardian_fault_injection.py:73-100` | def test_p2_stale_writer_cannot_survive_cutover(self) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_p3_bad_canary_restores_artifact_without_state_loss` | method | `tests/test_guardian_fault_injection.py:102-149` | def test_p3_bad_canary_restores_artifact_without_state_loss(self) | 1 | test |
| `test_guardian_fault_injection.GuardianFaultInjectionTests.test_unverified_cutover_degrades_without_changing_authority` | method | `tests/test_guardian_fault_injection.py:151-165` | def test_unverified_cutover_degrades_without_changing_authority(self) | 1 | test |
| `test_guardian_fencing.GuardianFencingTests` | class | `tests/test_guardian_fencing.py:6-43` | class GuardianFencingTests(unittest.TestCase) | 1 | test |
| `test_guardian_fencing.GuardianFencingTests.setUp` | method | `tests/test_guardian_fencing.py:7-9` | def setUp(self) | 35 | test |
| `test_guardian_fencing.GuardianFencingTests.test_only_one_writer_and_stale_lease_is_rejected_after_handoff` | method | `tests/test_guardian_fencing.py:11-20` | def test_only_one_writer_and_stale_lease_is_rejected_after_handoff(self) | 1 | test |
| `test_guardian_fencing.GuardianFencingTests.test_expiry_allows_new_generation_but_old_lease_cannot_return` | method | `tests/test_guardian_fencing.py:22-28` | def test_expiry_allows_new_generation_but_old_lease_cannot_return(self) | 1 | test |
| `test_guardian_fencing.GuardianFencingTests.test_renew_and_release_require_current_lease` | method | `tests/test_guardian_fencing.py:30-37` | def test_renew_and_release_require_current_lease(self) | 1 | test |
| `test_guardian_fencing.GuardianFencingTests.test_invalid_ttl_and_owner_fail_closed` | method | `tests/test_guardian_fencing.py:39-43` | def test_invalid_ttl_and_owner_fail_closed(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests` | class | `tests/test_guardian_health.py:10-101` | class GuardianHealthTests(unittest.TestCase) | 1 | test |
| `test_guardian_health.GuardianHealthTests.setUp` | method | `tests/test_guardian_health.py:11-14` | def setUp(self) | 35 | test |
| `test_guardian_health.GuardianHealthTests.test_failed_probe_waits_when_dependency_was_not_checked` | method | `tests/test_guardian_health.py:16-27` | def test_failed_probe_waits_when_dependency_was_not_checked(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests.test_failed_dependency_blocks_restart_after_failed_probe` | method | `tests/test_guardian_health.py:29-39` | def test_failed_dependency_blocks_restart_after_failed_probe(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests.test_failed_probe_is_restartable_only_after_healthy_dependencies` | method | `tests/test_guardian_health.py:41-52` | def test_failed_probe_is_restartable_only_after_healthy_dependencies(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests.test_healthy_component_does_not_request_restart` | method | `tests/test_guardian_health.py:54-64` | def test_healthy_component_does_not_request_restart(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests.test_restart_policy_and_budget_are_bounded` | method | `tests/test_guardian_health.py:66-83` | def test_restart_policy_and_budget_are_bounded(self) | 1 | test |
| `test_guardian_health.GuardianHealthTests.test_malformed_observations_and_dependency_sets_are_rejected` | method | `tests/test_guardian_health.py:85-101` | def test_malformed_observations_and_dependency_sets_are_rejected(self) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests` | class | `tests/test_guardian_incidents.py:11-80` | class GuardianIncidentTests(unittest.TestCase) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests.setUp` | method | `tests/test_guardian_incidents.py:12-20` | def setUp(self) | 35 | test |
| `test_guardian_incidents.GuardianIncidentTests.test_repeated_failure_is_one_incident` | method | `tests/test_guardian_incidents.py:22-33` | def test_repeated_failure_is_one_incident(self) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests.test_alerts_are_rate_limited_without_losing_occurrences` | method | `tests/test_guardian_incidents.py:35-41` | def test_alerts_are_rate_limited_without_losing_occurrences(self) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests.test_acknowledgment_suppresses_future_alerts_and_keeps_history` | method | `tests/test_guardian_incidents.py:43-52` | def test_acknowledgment_suppresses_future_alerts_and_keeps_history(self) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests.test_distinct_root_causes_are_distinct_incidents` | method | `tests/test_guardian_incidents.py:54-66` | def test_distinct_root_causes_are_distinct_incidents(self) | 1 | test |
| `test_guardian_incidents.GuardianIncidentTests.test_unverified_or_invalid_operations_are_rejected` | method | `tests/test_guardian_incidents.py:68-80` | def test_unverified_or_invalid_operations_are_rejected(self) | 1 | test |
| `test_guardian_integrity.GuardianIntegrityTests` | class | `tests/test_guardian_integrity.py:6-57` | class GuardianIntegrityTests(unittest.TestCase) | 1 | test |
| `test_guardian_integrity.GuardianIntegrityTests.setUp` | method | `tests/test_guardian_integrity.py:7-14` | def setUp(self) | 35 | test |
| `test_guardian_integrity.GuardianIntegrityTests.test_healthy_snapshot_is_read_only_and_serializable` | method | `tests/test_guardian_integrity.py:16-27` | def test_healthy_snapshot_is_read_only_and_serializable(self) | 1 | test |
| `test_guardian_integrity.GuardianIntegrityTests.test_mismatches_are_reported_without_raw_values` | method | `tests/test_guardian_integrity.py:29-49` | def test_mismatches_are_reported_without_raw_values(self) | 1 | test |
| `test_guardian_integrity.GuardianIntegrityTests.test_malformed_snapshots_are_rejected_before_comparison` | method | `tests/test_guardian_integrity.py:51-57` | def test_malformed_snapshots_are_rejected_before_comparison(self) | 1 | test |
| `test_guardian_isolation.GuardianIsolationTests` | class | `tests/test_guardian_isolation.py:6-63` | class GuardianIsolationTests(unittest.TestCase) | 1 | test |
| `test_guardian_isolation.GuardianIsolationTests.test_drain_reconciles_effects_and_preserves_unaffected_modules` | method | `tests/test_guardian_isolation.py:7-29` | def test_drain_reconciles_effects_and_preserves_unaffected_modules(self) | 1 | test |
| `test_guardian_isolation.GuardianIsolationTests.test_unknown_effect_blocks_resume_until_resolved` | method | `tests/test_guardian_isolation.py:31-42` | def test_unknown_effect_blocks_resume_until_resolved(self) | 1 | test |
| `test_guardian_isolation.GuardianIsolationTests.test_stale_generation_and_duplicate_effects_are_rejected` | method | `tests/test_guardian_isolation.py:44-54` | def test_stale_generation_and_duplicate_effects_are_rejected(self) | 1 | test |
| `test_guardian_isolation.GuardianIsolationTests.test_invalid_transition_does_not_mutate_other_state` | method | `tests/test_guardian_isolation.py:56-63` | def test_invalid_transition_does_not_mutate_other_state(self) | 1 | test |
| `test_guardian_model.GuardianModelTests` | class | `tests/test_guardian_model.py:9-49` | class GuardianModelTests(unittest.TestCase) | 1 | test |
| `test_guardian_model.GuardianModelTests.test_local_model_and_inference_are_probed_without_retaining_output` | method | `tests/test_guardian_model.py:10-25` | def test_local_model_and_inference_are_probed_without_retaining_output(self) | 1 | test |
| `test_guardian_model.GuardianModelTests.test_local_model_and_inference_are_probed_without_retaining_output.runner` | function | `tests/test_guardian_model.py:13-15` | def runner(command, timeout) | 14 | test |
| `test_guardian_model.GuardianModelTests.test_missing_model_does_not_fallback_and_stop_remains_available` | method | `tests/test_guardian_model.py:27-35` | def test_missing_model_does_not_fallback_and_stop_remains_available(self) | 1 | test |
| `test_guardian_model.GuardianModelTests.test_inference_failure_is_distinct_from_model_presence` | method | `tests/test_guardian_model.py:37-43` | def test_inference_failure_is_distinct_from_model_presence(self) | 1 | test |
| `test_guardian_model.GuardianModelTests.test_inference_failure_is_distinct_from_model_presence.runner` | function | `tests/test_guardian_model.py:38-39` | def runner(command, timeout) | 14 | test |
| `test_guardian_model.GuardianModelTests.test_model_and_timeout_are_bounded` | method | `tests/test_guardian_model.py:45-49` | def test_model_and_timeout_are_bounded(self) | 1 | test |
| `test_guardian_recovery.GuardianRecoveryTests` | class | `tests/test_guardian_recovery.py:11-94` | class GuardianRecoveryTests(unittest.TestCase) | 1 | test |
| `test_guardian_recovery.GuardianRecoveryTests._controller` | method | `tests/test_guardian_recovery.py:12-22` | def _controller(self, root: Path, runner, controls: Path) | 2 | test |
| `test_guardian_recovery.GuardianRecoveryTests.test_one_verified_boot_attempt_starts_controller` | method | `tests/test_guardian_recovery.py:24-37` | def test_one_verified_boot_attempt_starts_controller(self) | 1 | test |
| `test_guardian_recovery.GuardianRecoveryTests.test_crash_loop_enters_safe_mode_at_bounded_attempt_limit` | method | `tests/test_guardian_recovery.py:39-62` | def test_crash_loop_enters_safe_mode_at_bounded_attempt_limit(self) | 1 | test |
| `test_guardian_recovery.GuardianRecoveryTests.test_crash_loop_enters_safe_mode_at_bounded_attempt_limit.crash` | function | `tests/test_guardian_recovery.py:43-45` | def crash(command, cwd) | 5 | test |
| `test_guardian_recovery.GuardianRecoveryTests.test_stop_quota_and_approval_are_preserved` | method | `tests/test_guardian_recovery.py:64-84` | def test_stop_quota_and_approval_are_preserved(self) | 1 | test |
| `test_guardian_recovery.GuardianRecoveryTests.test_invalid_request_fails_closed` | method | `tests/test_guardian_recovery.py:86-94` | def test_invalid_request_fails_closed(self) | 1 | test |
| `test_guardian_release.GuardianReleaseTests` | class | `tests/test_guardian_release.py:10-76` | class GuardianReleaseTests(unittest.TestCase) | 1 | test |
| `test_guardian_release.GuardianReleaseTests._manifest` | method | `tests/test_guardian_release.py:11-41` | def _manifest(self, root: Path) -> Path | 2 | test |
| `test_guardian_release.GuardianReleaseTests.test_only_evidence_bound_candidate_with_closed_route_is_eligible` | method | `tests/test_guardian_release.py:43-47` | def test_only_evidence_bound_candidate_with_closed_route_is_eligible(self) | 1 | test |
| `test_guardian_release.GuardianReleaseTests.test_missing_qc_evidence_is_not_accepted` | method | `tests/test_guardian_release.py:49-57` | def test_missing_qc_evidence_is_not_accepted(self) | 1 | test |
| `test_guardian_release.GuardianReleaseTests.test_open_or_extended_route_gate_is_rejected` | method | `tests/test_guardian_release.py:59-67` | def test_open_or_extended_route_gate_is_rejected(self) | 1 | test |
| `test_guardian_release.GuardianReleaseTests.test_artifact_change_invalidates_canary` | method | `tests/test_guardian_release.py:69-76` | def test_artifact_change_invalidates_canary(self) | 1 | test |
| `test_guardian_restart.GuardianRestartTests` | class | `tests/test_guardian_restart.py:6-65` | class GuardianRestartTests(unittest.TestCase) | 1 | test |
| `test_guardian_restart.GuardianRestartTests.setUp` | method | `tests/test_guardian_restart.py:7-11` | def setUp(self) | 35 | test |
| `test_guardian_restart.GuardianRestartTests.test_cooldown_and_repeated_failures_escalate_without_replay` | method | `tests/test_guardian_restart.py:13-31` | def test_cooldown_and_repeated_failures_escalate_without_replay(self) | 1 | test |
| `test_guardian_restart.GuardianRestartTests.test_pending_attempt_is_fenced_until_outcome_is_recorded` | method | `tests/test_guardian_restart.py:33-44` | def test_pending_attempt_is_fenced_until_outcome_is_recorded(self) | 1 | test |
| `test_guardian_restart.GuardianRestartTests.test_success_requires_explicit_generation_reset_and_preserves_history` | method | `tests/test_guardian_restart.py:46-55` | def test_success_requires_explicit_generation_reset_and_preserves_history(self) | 1 | test |
| `test_guardian_restart.GuardianRestartTests.test_disabled_and_invalid_policies_fail_closed` | method | `tests/test_guardian_restart.py:57-65` | def test_disabled_and_invalid_policies_fail_closed(self) | 1 | test |
| `test_guardian_rollback.GuardianRollbackTests` | class | `tests/test_guardian_rollback.py:14-104` | class GuardianRollbackTests(unittest.TestCase) | 1 | test |
| `test_guardian_rollback.GuardianRollbackTests._manifest` | method | `tests/test_guardian_rollback.py:15-60` | def _manifest(self, root: Path) -> Path | 2 | test |
| `test_guardian_rollback.GuardianRollbackTests.test_failed_canary_restores_last_known_good_and_preserves_state` | method | `tests/test_guardian_rollback.py:62-76` | def test_failed_canary_restores_last_known_good_and_preserves_state(self) | 1 | test |
| `test_guardian_rollback.GuardianRollbackTests.test_healthy_canary_cannot_trigger_rollback` | method | `tests/test_guardian_rollback.py:78-81` | def test_healthy_canary_cannot_trigger_rollback(self) | 1 | test |
| `test_guardian_rollback.GuardianRollbackTests.test_tampered_last_known_good_is_rejected` | method | `tests/test_guardian_rollback.py:83-89` | def test_tampered_last_known_good_is_rejected(self) | 1 | test |
| `test_guardian_rollback.GuardianRollbackTests.test_unsafe_path_and_target_mismatch_are_rejected` | method | `tests/test_guardian_rollback.py:91-104` | def test_unsafe_path_and_target_mismatch_are_rejected(self) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests` | class | `tests/test_guardian_standby.py:9-94` | class GuardianStandbyTests(unittest.TestCase) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests._launcher` | method | `tests/test_guardian_standby.py:10-21` | def _launcher(self, root: Path, runner) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests.test_matching_schema_and_explicit_capacity_start_is_isolated` | method | `tests/test_guardian_standby.py:23-41` | def test_matching_schema_and_explicit_capacity_start_is_isolated(self) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests.test_matching_schema_and_explicit_capacity_start_is_isolated.runner` | function | `tests/test_guardian_standby.py:26-28` | def runner(command, cwd) | 14 | test |
| `test_guardian_standby.GuardianStandbyTests.test_capacity_is_not_assumed_or_probed` | method | `tests/test_guardian_standby.py:43-55` | def test_capacity_is_not_assumed_or_probed(self) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests.test_schema_and_state_mismatch_do_not_start` | method | `tests/test_guardian_standby.py:57-67` | def test_schema_and_state_mismatch_do_not_start(self) | 1 | test |
| `test_guardian_standby.GuardianStandbyTests.test_active_control_marker_blocks_start` | method | `tests/test_guardian_standby.py:69-94` | def test_active_control_marker_blocks_start(self) | 1 | test |
| `test_health.HealthTests` | class | `tests/test_health.py:14-82` | class HealthTests(unittest.TestCase) | 1 | test |
| `test_health.HealthTests.test_health_reads_without_creating_or_mutating_database` | method | `tests/test_health.py:15-48` | def test_health_reads_without_creating_or_mutating_database(self) | 1 | test |
| `test_health.HealthTests.test_health_rejects_missing_canonical_database` | method | `tests/test_health.py:50-53` | def test_health_rejects_missing_canonical_database(self) | 1 | test |
| `test_health.HealthTests.test_health_reads_fresh_native_runtime_without_historical_ledger` | method | `tests/test_health.py:55-74` | def test_health_reads_fresh_native_runtime_without_historical_ledger(self) | 1 | test |
| `test_health.HealthTests.test_cli_health_returns_structured_state` | method | `tests/test_health.py:76-82` | def test_cli_health_returns_structured_state(self) | 1 | test |
| `test_importer.ImporterTests` | class | `tests/test_importer.py:8-38` | class ImporterTests(unittest.TestCase) | 1 | test |
| `test_importer.ImporterTests.test_fixture_import_dry_run_then_apply` | method | `tests/test_importer.py:9-28` | def test_fixture_import_dry_run_then_apply(self) | 1 | test |
| `test_importer.ImporterTests.test_unsafe_target` | method | `tests/test_importer.py:29-38` | def test_unsafe_target(self) | 1 | test |
| `test_mig_015_acceptance.Mig015AcceptanceTests` | class | `tests/test_mig_015_acceptance.py:16-52` | class Mig015AcceptanceTests(unittest.TestCase) | 1 | test |
| `test_mig_015_acceptance.Mig015AcceptanceTests.test_identity_manifest_and_operator_docs_use_approved_roles` | method | `tests/test_mig_015_acceptance.py:17-28` | def test_identity_manifest_and_operator_docs_use_approved_roles(self) | 1 | test |
| `test_mig_015_acceptance.Mig015AcceptanceTests.test_native_snapshot_is_read_only_and_does_not_invoke_runner` | method | `tests/test_mig_015_acceptance.py:30-52` | def test_native_snapshot_is_read_only_and_does_not_invoke_runner(self) | 1 | test |
| `test_mig_016_identity.Mig016IdentityTests` | class | `tests/test_mig_016_identity.py:17-72` | class Mig016IdentityTests(unittest.TestCase) | 1 | test |
| `test_mig_016_identity.Mig016IdentityTests.test_contract_keeps_module_ids_and_documents_legacy_names` | method | `tests/test_mig_016_identity.py:18-25` | def test_contract_keeps_module_ids_and_documents_legacy_names(self) | 1 | test |
| `test_mig_016_identity.Mig016IdentityTests.test_receipts_add_atlas_identity_without_rewriting_records` | method | `tests/test_mig_016_identity.py:27-72` | def test_receipts_add_atlas_identity_without_rewriting_records(self) | 1 | test |
| `test_migration_compatibility.MigrationCompatibilityTests` | class | `tests/test_migration_compatibility.py:16-50` | class MigrationCompatibilityTests(unittest.TestCase) | 1 | test |
| `test_migration_compatibility.MigrationCompatibilityTests.test_snapshot_maps_all_three_contract_areas` | method | `tests/test_migration_compatibility.py:17-24` | def test_snapshot_maps_all_three_contract_areas(self) | 1 | test |
| `test_migration_compatibility.MigrationCompatibilityTests.test_snapshot_contains_no_legacy_source_content` | method | `tests/test_migration_compatibility.py:26-30` | def test_snapshot_contains_no_legacy_source_content(self) | 1 | test |
| `test_migration_compatibility.MigrationCompatibilityTests.test_tampered_staged_blob_fails_closed` | method | `tests/test_migration_compatibility.py:32-39` | def test_tampered_staged_blob_fails_closed(self) | 1 | test |
| `test_migration_compatibility.MigrationCompatibilityTests.test_incomplete_contract_fails_closed` | method | `tests/test_migration_compatibility.py:41-50` | def test_incomplete_contract_fails_closed(self) | 1 | test |
| `test_migration_guardrails.MigrationGuardrailTests` | class | `tests/test_migration_guardrails.py:10-80` | class MigrationGuardrailTests(unittest.TestCase) | 1 | test |
| `test_migration_guardrails.MigrationGuardrailTests.setUp` | method | `tests/test_migration_guardrails.py:11-33` | def setUp(self) | 35 | test |
| `test_migration_guardrails.MigrationGuardrailTests.setUp.git` | function | `tests/test_migration_guardrails.py:18-22` | def git(*args) | 19 | test |
| `test_migration_guardrails.MigrationGuardrailTests.tearDown` | method | `tests/test_migration_guardrails.py:35-36` | def tearDown(self) | 12 | test |
| `test_migration_guardrails.MigrationGuardrailTests.manifest` | method | `tests/test_migration_guardrails.py:38-42` | def manifest(self, **entry) | 16 | test |
| `test_migration_guardrails.MigrationGuardrailTests.test_dry_run_and_apply_preserve_commit_provenance` | method | `tests/test_migration_guardrails.py:44-56` | def test_dry_run_and_apply_preserve_commit_provenance(self) | 1 | test |
| `test_migration_guardrails.MigrationGuardrailTests.test_mismatched_commit_fails_before_writing` | method | `tests/test_migration_guardrails.py:58-62` | def test_mismatched_commit_fails_before_writing(self) | 1 | test |
| `test_migration_guardrails.MigrationGuardrailTests.test_case_only_collisions_fail_before_writing` | method | `tests/test_migration_guardrails.py:64-69` | def test_case_only_collisions_fail_before_writing(self) | 1 | test |
| `test_migration_guardrails.MigrationGuardrailTests.test_case_only_collisions_between_entries_fail_closed` | method | `tests/test_migration_guardrails.py:71-80` | def test_case_only_collisions_between_entries_fail_closed(self) | 1 | test |
| `test_monitor.MonitorTests` | class | `tests/test_monitor.py:36-196` | class MonitorTests(unittest.TestCase) | 1 | test |
| `test_monitor.MonitorTests._astra` | method | `tests/test_monitor.py:37-61` | def _astra(self, db_path) | 1 | test |
| `test_monitor.MonitorTests.test_missing_database_never_created` | method | `tests/test_monitor.py:63-68` | def test_missing_database_never_created(self) | 1 | test |
| `test_monitor.MonitorTests.test_astra_status_worker_slot_progress_and_controls` | method | `tests/test_monitor.py:70-93` | def test_astra_status_worker_slot_progress_and_controls(self) | 1 | test |
| `test_monitor.MonitorTests.test_old_run_events_do_not_fabricate_current_worker_slot` | method | `tests/test_monitor.py:95-108` | def test_old_run_events_do_not_fabricate_current_worker_slot(self) | 1 | test |
| `test_monitor.MonitorTests.test_astra_runtime_version_comes_from_read_only_settings` | method | `tests/test_monitor.py:110-118` | def test_astra_runtime_version_comes_from_read_only_settings(self) | 1 | test |
| `test_monitor.MonitorTests.test_no_raw_spec_in_json_and_no_objectives` | method | `tests/test_monitor.py:120-131` | def test_no_raw_spec_in_json_and_no_objectives(self) | 1 | test |
| `test_monitor.MonitorTests.test_wal_updates_seen_without_writes` | method | `tests/test_monitor.py:133-145` | def test_wal_updates_seen_without_writes(self) | 1 | test |
| `test_monitor.MonitorTests.test_native_atlas_queue_and_auto_detection` | method | `tests/test_monitor.py:147-165` | def test_native_atlas_queue_and_auto_detection(self) | 1 | test |
| `test_monitor.MonitorTests.test_unrecognized_db_refused` | method | `tests/test_monitor.py:167-172` | def test_unrecognized_db_refused(self) | 1 | test |
| `test_monitor.MonitorTests.test_cli_one_snapshot_prints_json_and_is_not_runner` | method | `tests/test_monitor.py:174-185` | def test_cli_one_snapshot_prints_json_and_is_not_runner(self) | 1 | test |
| `test_monitor.MonitorTests.test_terminal_escape_sanitized` | method | `tests/test_monitor.py:187-192` | def test_terminal_escape_sanitized(self) | 1 | test |
| `test_monitor.MonitorTests.test_cli_rejects_simultaneous_watch_and_json` | method | `tests/test_monitor.py:194-196` | def test_cli_rejects_simultaneous_watch_and_json(self) | 1 | test |
| `test_monitor_supervision.SupervisorTelemetryTests` | class | `tests/test_monitor_supervision.py:28-170` | class SupervisorTelemetryTests(unittest.TestCase) | 1 | test |
| `test_monitor_supervision.SupervisorTelemetryTests._fixture` | method | `tests/test_monitor_supervision.py:29-106` | def _fixture(self, path, *, extended) | 1 | test |
| `test_monitor_supervision.SupervisorTelemetryTests.test_legacy_astra_db_gracefully_reports_missing_lanes` | method | `tests/test_monitor_supervision.py:108-122` | def test_legacy_astra_db_gracefully_reports_missing_lanes(self) | 1 | test |
| `test_monitor_supervision.SupervisorTelemetryTests.test_new_lanes_queues_failures_and_upgrade_without_private_data` | method | `tests/test_monitor_supervision.py:124-150` | def test_new_lanes_queues_failures_and_upgrade_without_private_data(self) | 1 | test |
| `test_monitor_supervision.SupervisorTelemetryTests.test_unknown_event_and_failure_values_are_redacted` | method | `tests/test_monitor_supervision.py:152-170` | def test_unknown_event_and_failure_values_are_redacted(self) | 1 | test |
| `test_native_controller.NativeControllerTests` | class | `tests/test_native_controller.py:8-82` | class NativeControllerTests(unittest.TestCase) | 1 | test |
| `test_native_controller.NativeControllerTests.test_empty_native_cycle_is_a_safe_idle_without_an_executor` | method | `tests/test_native_controller.py:9-14` | def test_empty_native_cycle_is_a_safe_idle_without_an_executor(self) | 1 | test |
| `test_native_controller.NativeControllerTests.test_process_lock_fences_a_second_native_controller_and_releases_on_close` | method | `tests/test_native_controller.py:16-25` | def test_process_lock_fences_a_second_native_controller_and_releases_on_close(self) | 1 | test |
| `test_native_controller.NativeControllerTests.test_controls_stop_admission_before_a_task_is_claimed` | method | `tests/test_native_controller.py:27-37` | def test_controls_stop_admission_before_a_task_is_claimed(self) | 1 | test |
| `test_native_controller.NativeControllerTests.test_executor_completion_and_failure_are_digest_only_and_durable` | method | `tests/test_native_controller.py:39-59` | def test_executor_completion_and_failure_are_digest_only_and_durable(self) | 1 | test |
| `test_native_controller.NativeControllerTests.test_executor_exception_is_recorded_as_failed_without_raw_error` | method | `tests/test_native_controller.py:61-74` | def test_executor_exception_is_recorded_as_failed_without_raw_error(self) | 1 | test |
| `test_native_controller.NativeControllerTests.test_native_user_unit_points_only_to_the_native_controller` | method | `tests/test_native_controller.py:76-82` | def test_native_user_unit_points_only_to_the_native_controller(self) | 1 | test |
| `test_packaging_policy.load_script` | function | `tests/test_packaging_policy.py:15-26` | def load_script(name: str) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests` | class | `tests/test_packaging_policy.py:33-147` | class PackagingPolicyTests(unittest.TestCase) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.make_package` | method | `tests/test_packaging_policy.py:34-37` | def make_package(self) -> Path | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.write_manifest` | method | `tests/test_packaging_policy.py:39-48` | def write_manifest(self, root: Path, names: list[str]) -> None | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_actual_case_collision_is_rejected` | method | `tests/test_packaging_policy.py:50-55` | def test_actual_case_collision_is_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_actual_generated_directory_is_rejected` | method | `tests/test_packaging_policy.py:57-63` | def test_actual_generated_directory_is_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_actual_case_colliding_directories_are_rejected` | method | `tests/test_packaging_policy.py:65-71` | def test_actual_case_colliding_directories_are_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_unlisted_file_is_rejected` | method | `tests/test_packaging_policy.py:73-78` | def test_unlisted_file_is_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_symlink_is_rejected_without_following_it` | method | `tests/test_packaging_policy.py:80-91` | def test_symlink_is_rejected_without_following_it(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_preexisting_build_output_is_preserved` | method | `tests/test_packaging_policy.py:93-101` | def test_preexisting_build_output_is_preserved(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_generated_manifest_entries_and_wrangle_directories_are_rejected` | method | `tests/test_packaging_policy.py:103-113` | def test_generated_manifest_entries_and_wrangle_directories_are_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_windows_unsafe_manifest_and_import_components_are_rejected` | method | `tests/test_packaging_policy.py:115-129` | def test_windows_unsafe_manifest_and_import_components_are_rejected(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_package_tools_do_not_forward_inherited_environment` | method | `tests/test_packaging_policy.py:131-147` | def test_package_tools_do_not_forward_inherited_environment(self) | 1 | test |
| `test_packaging_policy.PackagingPolicyTests.test_package_tools_do_not_forward_inherited_environment.fake_run` | function | `tests/test_packaging_policy.py:136-137` | def fake_run(command, cwd, env) | 3 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests` | class | `tests/test_rel003_core_sda_delegation.py:17-171` | class Rel003CoreSdaDelegationTests(unittest.TestCase) | 1 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.setUp` | method | `tests/test_rel003_core_sda_delegation.py:18-32` | def setUp(self) | 35 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.tearDown` | method | `tests/test_rel003_core_sda_delegation.py:34-37` | def tearDown(self) | 12 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.request` | method | `tests/test_rel003_core_sda_delegation.py:40-47` | def request(path, scope='runtime:read', **extra) | 23 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests._delegate` | method | `tests/test_rel003_core_sda_delegation.py:49-108` | def _delegate(self) | 1 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_single_builder_delegates_to_core_and_records_completion_event` | method | `tests/test_rel003_core_sda_delegation.py:110-116` | def test_single_builder_delegates_to_core_and_records_completion_event(self) | 1 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_restart_preserves_result_and_delivery_is_idempotent` | method | `tests/test_rel003_core_sda_delegation.py:118-139` | def test_restart_preserves_result_and_delivery_is_idempotent(self) | 1 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_restart_preserves_result_and_delivery_is_idempotent.consume` | function | `tests/test_rel003_core_sda_delegation.py:130-132` | def consume(event) | 2 | test |
| `test_rel003_core_sda_delegation.Rel003CoreSdaDelegationTests.test_scope_claim_and_completion_idempotency_fail_closed` | method | `tests/test_rel003_core_sda_delegation.py:141-171` | def test_scope_claim_and_completion_idempotency_fail_closed(self) | 1 | test |
| `test_rel004_cross_device.Rel004CrossDeviceTests` | class | `tests/test_rel004_cross_device.py:19-104` | class Rel004CrossDeviceTests(unittest.TestCase) | 1 | test |
| `test_rel004_cross_device.Rel004CrossDeviceTests.test_context_handoff_and_tool_effects_reconstruct_without_replay` | method | `tests/test_rel004_cross_device.py:20-57` | def test_context_handoff_and_tool_effects_reconstruct_without_replay(self) | 1 | test |
| `test_rel004_cross_device.Rel004CrossDeviceTests.test_explicit_provider_handoff_and_windows_job_idempotency` | method | `tests/test_rel004_cross_device.py:59-104` | def test_explicit_provider_handoff_and_windows_job_idempotency(self) | 1 | test |
| `test_rel006_guardian_priority.GuardianPriorityQualificationTests` | class | `tests/test_rel006_guardian_priority.py:8-53` | class GuardianPriorityQualificationTests(unittest.TestCase) | 1 | test |
| `test_rel006_guardian_priority.GuardianPriorityQualificationTests.test_guardian_uses_next_slot_without_preempting_active_inference` | method | `tests/test_rel006_guardian_priority.py:11-53` | def test_guardian_uses_next_slot_without_preempting_active_inference(self) -> None | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests` | class | `tests/test_rel013_recovery_drills.py:19-247` | class Rel013RecoveryDrillTests(unittest.TestCase) | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._git` | method | `tests/test_rel013_recovery_drills.py:20-26` | def _git(self, repository: Path, *args: str) -> str | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._legacy_source` | method | `tests/test_rel013_recovery_drills.py:28-40` | def _legacy_source(self, root: Path) -> tuple[Path, str] | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._destination` | method | `tests/test_rel013_recovery_drills.py:42-51` | def _destination(self, root: Path) -> tuple[Path, str] | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests._release_manifest` | method | `tests/test_rel013_recovery_drills.py:53-97` | def _release_manifest(self, root: Path) -> Path | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_pinned_migration_dry_run_apply_and_verified_rollback` | method | `tests/test_rel013_recovery_drills.py:99-136` | def test_pinned_migration_dry_run_apply_and_verified_rollback(self) | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_recovery_backup_replay_and_corruption_are_bounded` | method | `tests/test_rel013_recovery_drills.py:138-179` | def test_recovery_backup_replay_and_corruption_are_bounded(self) | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_provider_outage_crash_and_stop_controls_fence_restart` | method | `tests/test_rel013_recovery_drills.py:181-223` | def test_provider_outage_crash_and_stop_controls_fence_restart(self) | 1 | test |
| `test_rel013_recovery_drills.Rel013RecoveryDrillTests.test_unsafe_migration_and_rollback_inputs_fail_before_writes` | method | `tests/test_rel013_recovery_drills.py:225-247` | def test_unsafe_migration_and_rollback_inputs_fail_before_writes(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests` | class | `tests/test_rel017_installation.py:16-74` | class Rel017InstallationTests(unittest.TestCase) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_manifest_declares_complete_platform_boundary` | method | `tests/test_rel017_installation.py:17-26` | def test_manifest_declares_complete_platform_boundary(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_manifest_artifacts_are_real_regular_files` | method | `tests/test_rel017_installation.py:28-34` | def test_manifest_artifacts_are_real_regular_files(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_linux_units_are_hardened_and_qc_only` | method | `tests/test_rel017_installation.py:36-45` | def test_linux_units_are_hardened_and_qc_only(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_windows_script_has_no_embedded_credentials_or_remote_queue` | method | `tests/test_rel017_installation.py:47-52` | def test_windows_script_has_no_embedded_credentials_or_remote_queue(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_cloudflare_contract_names_only_secure_secrets` | method | `tests/test_rel017_installation.py:54-59` | def test_cloudflare_contract_names_only_secure_secrets(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_verifier_cli_is_read_only_and_green` | method | `tests/test_rel017_installation.py:61-71` | def test_verifier_cli_is_read_only_and_green(self) | 1 | test |
| `test_rel017_installation.Rel017InstallationTests.test_controller_allows_installation_manifest_suffixes` | method | `tests/test_rel017_installation.py:73-74` | def test_controller_allows_installation_manifest_suffixes(self) | 1 | test |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests` | class | `tests/test_rel_cross_module_contracts.py:14-76` | class ReleaseCrossModuleContractTests(unittest.TestCase) | 1 | test |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests.setUpClass` | method | `tests/test_rel_cross_module_contracts.py:16-18` | def setUpClass(cls) | 2 | test |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests.test_every_configured_module_has_a_valid_identity_and_permission_fixture` | method | `tests/test_rel_cross_module_contracts.py:20-42` | def test_every_configured_module_has_a_valid_identity_and_permission_fixture(self) | 1 | test |
| `test_rel_cross_module_contracts.ReleaseCrossModuleContractTests.test_each_module_can_publish_and_deliver_the_versioned_event_fixture` | method | `tests/test_rel_cross_module_contracts.py:44-76` | def test_each_module_can_publish_and_deliver_the_versioned_event_fixture(self) | 1 | test |
| `test_rel_fault_isolation.ReleaseFaultIsolationTests` | class | `tests/test_rel_fault_isolation.py:11-43` | class ReleaseFaultIsolationTests(unittest.TestCase) | 1 | test |
| `test_rel_fault_isolation.ReleaseFaultIsolationTests.test_one_fault_isolated_without_stopping_the_other_nine_modules` | method | `tests/test_rel_fault_isolation.py:12-43` | def test_one_fault_isolated_without_stopping_the_other_nine_modules(self) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests` | class | `tests/test_research_analysis.py:12-79` | class ResearchAnalysisTests(unittest.TestCase) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests.store` | method | `tests/test_research_analysis.py:13-14` | def store(self, directory) | 44 | test |
| `test_research_analysis.ResearchAnalysisTests.test_permission_and_modality_are_recorded_with_timestamped_finding` | method | `tests/test_research_analysis.py:16-31` | def test_permission_and_modality_are_recorded_with_timestamped_finding(self) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests.test_permission_denial_is_persisted_without_analyzer_call` | method | `tests/test_research_analysis.py:33-45` | def test_permission_denial_is_persisted_without_analyzer_call(self) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests.test_missing_analyzer_and_empty_finding_are_explicit` | method | `tests/test_research_analysis.py:47-58` | def test_missing_analyzer_and_empty_finding_are_explicit(self) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests.test_provider_failure_is_redacted_and_persisted` | method | `tests/test_research_analysis.py:60-70` | def test_provider_failure_is_redacted_and_persisted(self) | 1 | test |
| `test_research_analysis.ResearchAnalysisTests.test_invalid_offsets_or_modality_are_rejected` | method | `tests/test_research_analysis.py:72-79` | def test_invalid_offsets_or_modality_are_rejected(self) | 1 | test |
| `test_research_comparison.ResearchComparisonTests` | class | `tests/test_research_comparison.py:10-55` | class ResearchComparisonTests(unittest.TestCase) | 1 | test |
| `test_research_comparison.ResearchComparisonTests.claim` | method | `tests/test_research_comparison.py:11-20` | def claim(self, source_id, assertion, confidence=None) | 21 | test |
| `test_research_comparison.ResearchComparisonTests.test_matching_sources_preserve_provenance_and_supplied_confidence` | method | `tests/test_research_comparison.py:22-32` | def test_matching_sources_preserve_provenance_and_supplied_confidence(self) | 1 | test |
| `test_research_comparison.ResearchComparisonTests.test_contradictory_sources_are_uncertain_without_invented_confidence` | method | `tests/test_research_comparison.py:34-44` | def test_contradictory_sources_are_uncertain_without_invented_confidence(self) | 1 | test |
| `test_research_comparison.ResearchComparisonTests.test_missing_confidence_stays_unknown_even_when_sources_match` | method | `tests/test_research_comparison.py:46-48` | def test_missing_confidence_stays_unknown_even_when_sources_match(self) | 1 | test |
| `test_research_comparison.ResearchComparisonTests.test_empty_and_malformed_inputs_are_bounded` | method | `tests/test_research_comparison.py:50-55` | def test_empty_and_malformed_inputs_are_bounded(self) | 1 | test |
| `test_research_github.ResearchGitHubTests` | class | `tests/test_research_github.py:16-133` | class ResearchGitHubTests(unittest.TestCase) | 1 | test |
| `test_research_github.ResearchGitHubTests.policy` | method | `tests/test_research_github.py:17-23` | def policy(self) | 16 | test |
| `test_research_github.ResearchGitHubTests.adapter` | method | `tests/test_research_github.py:25-26` | def adapter(self, **kwargs) | 9 | test |
| `test_research_github.ResearchGitHubTests.test_pinned_commit_requires_allowlisted_license_and_preserves_pin` | method | `tests/test_research_github.py:28-50` | def test_pinned_commit_requires_allowlisted_license_and_preserves_pin(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_pinned_commit_requires_allowlisted_license_and_preserves_pin.inspect` | function | `tests/test_research_github.py:29-41` | def inspect(repository, commit_sha, policy) | 10 | test |
| `test_research_github.ResearchGitHubTests.test_repository_allowlist_blocks_before_transport` | method | `tests/test_research_github.py:52-61` | def test_repository_allowlist_blocks_before_transport(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_repository_allowlist_blocks_before_transport.inspect` | function | `tests/test_research_github.py:55-57` | def inspect(*_args) | 10 | test |
| `test_research_github.ResearchGitHubTests.test_license_and_execution_barriers_fail_closed` | method | `tests/test_research_github.py:63-78` | def test_license_and_execution_barriers_fail_closed(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_license_and_execution_barriers_fail_closed.unlicensed` | function | `tests/test_research_github.py:64-65` | def unlicensed(*_args) | 2 | test |
| `test_research_github.ResearchGitHubTests.test_license_and_execution_barriers_fail_closed.executable` | function | `tests/test_research_github.py:72-73` | def executable(*_args) | 14 | test |
| `test_research_github.ResearchGitHubTests.test_path_allowlist_and_pinned_sha_are_enforced` | method | `tests/test_research_github.py:80-103` | def test_path_allowlist_and_pinned_sha_are_enforced(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_path_allowlist_and_pinned_sha_are_enforced.unsafe` | function | `tests/test_research_github.py:81-86` | def unsafe(*_args) | 5 | test |
| `test_research_github.ResearchGitHubTests.test_path_allowlist_and_pinned_sha_are_enforced.inspect` | function | `tests/test_research_github.py:95-97` | def inspect(*_args) | 10 | test |
| `test_research_github.ResearchGitHubTests.test_search_returns_only_allowlisted_exact_github_repositories` | method | `tests/test_research_github.py:105-116` | def test_search_returns_only_allowlisted_exact_github_repositories(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_search_returns_only_allowlisted_exact_github_repositories.search` | function | `tests/test_research_github.py:106-112` | def search(query, limit) | 9 | test |
| `test_research_github.ResearchGitHubTests.test_missing_transport_and_provider_failures_are_bounded` | method | `tests/test_research_github.py:118-129` | def test_missing_transport_and_provider_failures_are_bounded(self) | 1 | test |
| `test_research_github.ResearchGitHubTests.test_missing_transport_and_provider_failures_are_bounded.timeout` | function | `tests/test_research_github.py:122-123` | def timeout(*_args) | 16 | test |
| `test_research_github.ResearchGitHubTests.test_policy_rejects_empty_license_allowlist` | method | `tests/test_research_github.py:131-133` | def test_policy_rejects_empty_license_allowlist(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests` | class | `tests/test_research_handbook.py:18-135` | class ResearchHandbookTests(unittest.TestCase) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.proposal` | method | `tests/test_research_handbook.py:19-35` | def proposal(self, *, proposal_id='proposal-1', section='tips', role='research', candidate='# tip\n') | 4 | test |
| `test_research_handbook.ResearchHandbookTests.review` | method | `tests/test_research_handbook.py:37-47` | def review(self, proposal, *, reviewer='qc-1', decision='approved') | 6 | test |
| `test_research_handbook.ResearchHandbookTests.test_research_tip_round_trip_requires_review_and_merger` | method | `tests/test_research_handbook.py:49-70` | def test_research_tip_round_trip_requires_review_and_merger(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_research_is_the_only_proposer_for_tips` | method | `tests/test_research_handbook.py:72-76` | def test_research_is_the_only_proposer_for_tips(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_review_cannot_self_approve_or_use_stale_candidate` | method | `tests/test_research_handbook.py:78-89` | def test_review_cannot_self_approve_or_use_stale_candidate(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_constitution_requires_distinct_owner_receipt` | method | `tests/test_research_handbook.py:91-105` | def test_constitution_requires_distinct_owner_receipt(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_stale_base_blocks_without_mutating_the_candidate` | method | `tests/test_research_handbook.py:107-116` | def test_stale_base_blocks_without_mutating_the_candidate(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_replay_is_idempotent_and_conflicting_payload_is_rejected` | method | `tests/test_research_handbook.py:118-126` | def test_replay_is_idempotent_and_conflicting_payload_is_rejected(self) | 1 | test |
| `test_research_handbook.ResearchHandbookTests.test_proposal_envelope_rejects_aliases_and_unknown_fields` | method | `tests/test_research_handbook.py:128-135` | def test_proposal_envelope_rejects_aliases_and_unknown_fields(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests` | class | `tests/test_research_instagram.py:13-102` | class ResearchInstagramTests(unittest.TestCase) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.store` | method | `tests/test_research_instagram.py:14-15` | def store(self, directory) | 44 | test |
| `test_research_instagram.ResearchInstagramTests.test_public_metadata_caption_audio_and_source_links_persist` | method | `tests/test_research_instagram.py:17-33` | def test_public_metadata_caption_audio_and_source_links_persist(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.test_private_content_is_blocked_without_audio_access` | method | `tests/test_research_instagram.py:35-48` | def test_private_content_is_blocked_without_audio_access(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.test_login_required_content_is_blocked_transparently` | method | `tests/test_research_instagram.py:50-59` | def test_login_required_content_is_blocked_transparently(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.test_audio_unavailable_is_partial_with_persisted_reason` | method | `tests/test_research_instagram.py:61-71` | def test_audio_unavailable_is_partial_with_persisted_reason(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.test_invalid_url_is_blocked_before_provider_calls` | method | `tests/test_research_instagram.py:73-84` | def test_invalid_url_is_blocked_before_provider_calls(self) | 2 | test |
| `test_research_instagram.ResearchInstagramTests.test_invalid_audio_offsets_are_failed_and_persisted` | method | `tests/test_research_instagram.py:86-97` | def test_invalid_audio_offsets_are_failed_and_persisted(self) | 1 | test |
| `test_research_instagram.ResearchInstagramTests.test_supported_reel_url_forms` | method | `tests/test_research_instagram.py:99-102` | def test_supported_reel_url_forms(self) | 1 | test |
| `test_research_media_rag.record` | function | `tests/test_research_media_rag.py:18-27` | def record(video_id, text, observed=OBSERVED) | 15 | test |
| `test_research_media_rag.ResearchMediaRAGTests` | class | `tests/test_research_media_rag.py:30-69` | class ResearchMediaRAGTests(unittest.TestCase) | 1 | test |
| `test_research_media_rag.ResearchMediaRAGTests.test_chunking_is_bounded_reproducible_and_source_linked` | method | `tests/test_research_media_rag.py:31-38` | def test_chunking_is_bounded_reproducible_and_source_linked(self) | 1 | test |
| `test_research_media_rag.ResearchMediaRAGTests.test_topics_are_stable_and_retain_provenance` | method | `tests/test_research_media_rag.py:40-43` | def test_topics_are_stable_and_retain_provenance(self) | 1 | test |
| `test_research_media_rag.ResearchMediaRAGTests.test_cross_video_summary_is_sorted_extractive_and_persistent` | method | `tests/test_research_media_rag.py:45-58` | def test_cross_video_summary_is_sorted_extractive_and_persistent(self) | 1 | test |
| `test_research_media_rag.ResearchMediaRAGTests.test_empty_summary_is_explicit` | method | `tests/test_research_media_rag.py:60-62` | def test_empty_summary_is_explicit(self) | 1 | test |
| `test_research_media_rag.ResearchMediaRAGTests.test_invalid_chunk_size_and_duplicate_videos_are_rejected` | method | `tests/test_research_media_rag.py:64-69` | def test_invalid_chunk_size_and_duplicate_videos_are_rejected(self) | 1 | test |
| `test_research_safety.ResearchSafetyTests` | class | `tests/test_research_safety.py:25-143` | class ResearchSafetyTests(unittest.TestCase) | 1 | test |
| `test_research_safety.ResearchSafetyTests.test_instruction_like_web_content_stays_data_and_scope_is_allowlisted` | method | `tests/test_research_safety.py:26-51` | def test_instruction_like_web_content_stays_data_and_scope_is_allowlisted(self) | 1 | test |
| `test_research_safety.ResearchSafetyTests.test_instruction_like_web_content_stays_data_and_scope_is_allowlisted.fetch` | function | `tests/test_research_safety.py:30-36` | def fetch(uri, policy, timeout) | 8 | test |
| `test_research_safety.ResearchSafetyTests.test_private_media_requires_explicit_access_and_does_not_call_audio` | method | `tests/test_research_safety.py:53-67` | def test_private_media_requires_explicit_access_and_does_not_call_audio(self) | 1 | test |
| `test_research_safety.ResearchSafetyTests.test_media_instruction_like_text_is_extractive_and_source_linked` | method | `tests/test_research_safety.py:69-83` | def test_media_instruction_like_text_is_extractive_and_source_linked(self) | 1 | test |
| `test_research_safety.ResearchSafetyTests.test_video_observations_are_immutable_and_replayed_without_overwrite` | method | `tests/test_research_safety.py:85-111` | def test_video_observations_are_immutable_and_replayed_without_overwrite(self) | 1 | test |
| `test_research_safety.ResearchSafetyTests.test_pinned_license_and_execution_barriers_are_independent` | method | `tests/test_research_safety.py:113-143` | def test_pinned_license_and_execution_barriers_are_independent(self) | 1 | test |
| `test_research_subscriptions.ResearchSubscriptionTests` | class | `tests/test_research_subscriptions.py:14-72` | class ResearchSubscriptionTests(unittest.TestCase) | 1 | test |
| `test_research_subscriptions.ResearchSubscriptionTests.service` | method | `tests/test_research_subscriptions.py:15-16` | def service(self, path: Path, clock) | 27 | test |
| `test_research_subscriptions.ResearchSubscriptionTests.test_follow_is_stable_and_enforces_provider_terms` | method | `tests/test_research_subscriptions.py:18-31` | def test_follow_is_stable_and_enforces_provider_terms(self) | 1 | test |
| `test_research_subscriptions.ResearchSubscriptionTests.test_only_due_subscriptions_refresh_and_next_cadence_is_recorded` | method | `tests/test_research_subscriptions.py:33-48` | def test_only_due_subscriptions_refresh_and_next_cadence_is_recorded(self) | 1 | test |
| `test_research_subscriptions.ResearchSubscriptionTests.test_provider_failure_is_bounded_and_does_not_leak_exception_text` | method | `tests/test_research_subscriptions.py:50-63` | def test_provider_failure_is_bounded_and_does_not_leak_exception_text(self) | 1 | test |
| `test_research_subscriptions.ResearchSubscriptionTests.test_disabled_subscription_is_not_refreshed_after_restart` | method | `tests/test_research_subscriptions.py:65-72` | def test_disabled_subscription_is_not_refreshed_after_restart(self) | 1 | test |
| `test_research_web.ResearchWebTests` | class | `tests/test_research_web.py:15-104` | class ResearchWebTests(unittest.TestCase) | 1 | test |
| `test_research_web.ResearchWebTests.policy` | method | `tests/test_research_web.py:16-17` | def policy(self) | 16 | test |
| `test_research_web.ResearchWebTests.service` | method | `tests/test_research_web.py:19-20` | def service(self, **kwargs) | 27 | test |
| `test_research_web.ResearchWebTests.test_search_preserves_source_and_observation_dates` | method | `tests/test_research_web.py:22-36` | def test_search_preserves_source_and_observation_dates(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_search_preserves_source_and_observation_dates.search` | function | `tests/test_research_web.py:23-31` | def search(query, source, limit) | 9 | test |
| `test_research_web.ResearchWebTests.test_fetch_is_bounded_and_hashes_content` | method | `tests/test_research_web.py:38-49` | def test_fetch_is_bounded_and_hashes_content(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_fetch_is_bounded_and_hashes_content.fetch` | function | `tests/test_research_web.py:39-44` | def fetch(uri, source, timeout) | 8 | test |
| `test_research_web.ResearchWebTests.test_unallowlisted_source_is_blocked_before_transport` | method | `tests/test_research_web.py:51-61` | def test_unallowlisted_source_is_blocked_before_transport(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_unallowlisted_source_is_blocked_before_transport.fetch` | function | `tests/test_research_web.py:54-56` | def fetch(*_args) | 8 | test |
| `test_research_web.ResearchWebTests.test_foreign_search_results_are_not_returned` | method | `tests/test_research_web.py:63-73` | def test_foreign_search_results_are_not_returned(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_foreign_search_results_are_not_returned.search` | function | `tests/test_research_web.py:64-68` | def search(*_args) | 9 | test |
| `test_research_web.ResearchWebTests.test_provider_failures_are_explicit_and_redacted` | method | `tests/test_research_web.py:75-85` | def test_provider_failures_are_explicit_and_redacted(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_provider_failures_are_explicit_and_redacted.timeout` | function | `tests/test_research_web.py:76-77` | def timeout(*_args) | 16 | test |
| `test_research_web.ResearchWebTests.test_invalid_content_and_requests_fail_closed` | method | `tests/test_research_web.py:87-98` | def test_invalid_content_and_requests_fail_closed(self) | 1 | test |
| `test_research_web.ResearchWebTests.test_invalid_content_and_requests_fail_closed.invalid` | function | `tests/test_research_web.py:93-94` | def invalid(*_args) | 27 | test |
| `test_research_web.ResearchWebTests.test_source_policy_rejects_non_https_and_userinfo` | method | `tests/test_research_web.py:100-104` | def test_source_policy_rejects_non_https_and_userinfo(self) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests` | class | `tests/test_research_youtube.py:17-95` | class ResearchYouTubeTests(unittest.TestCase) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests.store` | method | `tests/test_research_youtube.py:18-19` | def store(self, directory) | 44 | test |
| `test_research_youtube.ResearchYouTubeTests.test_metadata_offsets_source_links_and_record_persist` | method | `tests/test_research_youtube.py:21-42` | def test_metadata_offsets_source_links_and_record_persist(self) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests.test_transcript_failure_reason_is_persisted` | method | `tests/test_research_youtube.py:44-57` | def test_transcript_failure_reason_is_persisted(self) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests.test_invalid_url_is_blocked_before_provider_calls` | method | `tests/test_research_youtube.py:59-70` | def test_invalid_url_is_blocked_before_provider_calls(self) | 2 | test |
| `test_research_youtube.ResearchYouTubeTests.test_invalid_offsets_are_failed_and_persisted` | method | `tests/test_research_youtube.py:72-83` | def test_invalid_offsets_are_failed_and_persisted(self) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests.test_missing_metadata_transport_is_persisted` | method | `tests/test_research_youtube.py:85-90` | def test_missing_metadata_transport_is_persisted(self) | 1 | test |
| `test_research_youtube.ResearchYouTubeTests.test_supported_url_forms_return_the_same_id` | method | `tests/test_research_youtube.py:92-95` | def test_supported_url_forms_return_the_same_id(self) | 1 | test |
| `test_runtime_browser.BrowserProfileServiceTests` | class | `tests/test_runtime_browser.py:9-83` | class BrowserProfileServiceTests(unittest.TestCase) | 1 | test |
| `test_runtime_browser.BrowserProfileServiceTests.make_service` | method | `tests/test_runtime_browser.py:10-16` | def make_service(self, root: str) | 1 | test |
| `test_runtime_browser.BrowserProfileServiceTests.test_profile_and_human_handoff_persist_without_raw_session_value` | method | `tests/test_runtime_browser.py:18-36` | def test_profile_and_human_handoff_persist_without_raw_session_value(self) | 1 | test |
| `test_runtime_browser.BrowserProfileServiceTests.test_actions_are_allowlisted_confirmed_and_target_is_not_retained` | method | `tests/test_runtime_browser.py:38-64` | def test_actions_are_allowlisted_confirmed_and_target_is_not_retained(self) | 1 | test |
| `test_runtime_browser.BrowserProfileServiceTests.test_idempotency_and_invalid_login_reference_fail_closed` | method | `tests/test_runtime_browser.py:66-83` | def test_idempotency_and_invalid_login_reference_fail_closed(self) | 1 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter` | class | `tests/test_runtime_browser_tools.py:8-29` | class FakeBrowserAdapter() | 1 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter.__init__` | method | `tests/test_runtime_browser_tools.py:9-11` | def __init__(self) | 5 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter.navigate` | method | `tests/test_runtime_browser_tools.py:13-15` | def navigate(self, profile_dir, target_ref) | 1 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter.read` | method | `tests/test_runtime_browser_tools.py:17-21` | def read(self, profile_dir, target_ref) | 32 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter.click` | method | `tests/test_runtime_browser_tools.py:23-25` | def click(self, profile_dir, target_ref) | 1 | test |
| `test_runtime_browser_tools.FakeBrowserAdapter.form` | method | `tests/test_runtime_browser_tools.py:27-29` | def form(self, profile_dir, target_ref, fields) | 1 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests` | class | `tests/test_runtime_browser_tools.py:32-82` | class BrowserToolServiceTests(unittest.TestCase) | 1 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests.setUp` | method | `tests/test_runtime_browser_tools.py:33-45` | def setUp(self) | 35 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests.tearDown` | method | `tests/test_runtime_browser_tools.py:47-49` | def tearDown(self) | 12 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests.test_typed_operations_use_policy_and_mark_page_data_untrusted` | method | `tests/test_runtime_browser_tools.py:51-63` | def test_typed_operations_use_policy_and_mark_page_data_untrusted(self) | 1 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests.test_form_rejects_sensitive_fields_and_allows_bounded_typed_fields` | method | `tests/test_runtime_browser_tools.py:65-76` | def test_form_rejects_sensitive_fields_and_allows_bounded_typed_fields(self) | 1 | test |
| `test_runtime_browser_tools.BrowserToolServiceTests.test_adapter_output_is_bounded_and_no_generic_operation_exists` | method | `tests/test_runtime_browser_tools.py:78-82` | def test_adapter_output_is_bounded_and_no_generic_operation_exists(self) | 1 | test |
| `test_runtime_calendar.FakeCalendar` | class | `tests/test_runtime_calendar.py:18-35` | class FakeCalendar() | 1 | test |
| `test_runtime_calendar.FakeCalendar.__init__` | method | `tests/test_runtime_calendar.py:19-21` | def __init__(self) | 5 | test |
| `test_runtime_calendar.FakeCalendar.read_events` | method | `tests/test_runtime_calendar.py:23-25` | def read_events(self, start_utc, end_utc, *, limit) | 1 | test |
| `test_runtime_calendar.FakeCalendar.create_event` | method | `tests/test_runtime_calendar.py:27-30` | def create_event(self, event) | 1 | test |
| `test_runtime_calendar.FakeCalendar.update_event` | method | `tests/test_runtime_calendar.py:32-35` | def update_event(self, event_id, event) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests` | class | `tests/test_runtime_calendar.py:38-109` | class RuntimeCalendarTests(unittest.TestCase) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_and_writes_use_separate_scopes_and_confirmation` | method | `tests/test_runtime_calendar.py:39-53` | def test_read_and_writes_use_separate_scopes_and_confirmation(self) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_timezone_is_aware_and_normalized_to_utc` | method | `tests/test_runtime_calendar.py:55-71` | def test_timezone_is_aware_and_normalized_to_utc(self) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results` | method | `tests/test_runtime_calendar.py:73-99` | def test_read_rejects_bad_ranges_and_adapter_results(self) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results.BadAdapter` | class | `tests/test_runtime_calendar.py:81-83` | class BadAdapter(FakeCalendar) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results.BadAdapter.read_events` | method | `tests/test_runtime_calendar.py:82-83` | def read_events(self, start_utc, end_utc, *, limit) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results.InfiniteAdapter` | class | `tests/test_runtime_calendar.py:90-94` | class InfiniteAdapter(FakeCalendar) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_rejects_bad_ranges_and_adapter_results.InfiniteAdapter.read_events` | method | `tests/test_runtime_calendar.py:91-94` | def read_events(self, start_utc, end_utc, *, limit) | 1 | test |
| `test_runtime_calendar.RuntimeCalendarTests.test_read_and_write_scopes_are_independently_required` | method | `tests/test_runtime_calendar.py:101-109` | def test_read_and_write_scopes_are_independently_required(self) | 1 | test |
| `test_runtime_chat._deltas` | function | `tests/test_runtime_chat.py:10-12` | async def _deltas(*values) | 1 | test |
| `test_runtime_chat.RuntimeChatTests` | class | `tests/test_runtime_chat.py:15-96` | class RuntimeChatTests(unittest.TestCase) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_completed_stream_persists_only_after_done` | method | `tests/test_runtime_chat.py:16-31` | def test_completed_stream_persists_only_after_done(self) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_completed_stream_persists_only_after_done.run` | function | `tests/test_runtime_chat.py:17-23` | async def run(store) | 36 | test |
| `test_runtime_chat.RuntimeChatTests._with_conversation` | method | `tests/test_runtime_chat.py:33-35` | async def _with_conversation(self, store, callback) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_cancellation_does_not_persist_a_successful_turn` | method | `tests/test_runtime_chat.py:37-54` | def test_cancellation_does_not_persist_a_successful_turn(self) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_cancellation_does_not_persist_a_successful_turn.run` | function | `tests/test_runtime_chat.py:38-46` | async def run(store, cancel_event) | 36 | test |
| `test_runtime_chat.RuntimeChatTests.test_cancellation_does_not_persist_a_successful_turn.run.provider` | function | `tests/test_runtime_chat.py:40-43` | async def provider(_message) | 11 | test |
| `test_runtime_chat.RuntimeChatTests.test_provider_failures_are_precise_and_not_persisted` | method | `tests/test_runtime_chat.py:56-73` | def test_provider_failures_are_precise_and_not_persisted(self) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_provider_failures_are_precise_and_not_persisted.run` | function | `tests/test_runtime_chat.py:57-63` | async def run(store, failure) | 36 | test |
| `test_runtime_chat.RuntimeChatTests.test_provider_failures_are_precise_and_not_persisted.run.provider` | function | `tests/test_runtime_chat.py:58-60` | async def provider(_message) | 11 | test |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes` | method | `tests/test_runtime_chat.py:75-96` | def test_invalid_delta_and_empty_response_are_not_successes(self) | 1 | test |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes.run` | function | `tests/test_runtime_chat.py:76-82` | async def run(provider) | 36 | test |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes.invalid` | function | `tests/test_runtime_chat.py:84-85` | async def invalid(_message) | 27 | test |
| `test_runtime_chat.RuntimeChatTests.test_invalid_delta_and_empty_response_are_not_successes.empty` | function | `tests/test_runtime_chat.py:87-89` | async def empty(_message) | 5 | test |
| `test_runtime_dashboard.RuntimeDashboardTests` | class | `tests/test_runtime_dashboard.py:10-63` | class RuntimeDashboardTests(unittest.TestCase) | 1 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.setUpClass` | method | `tests/test_runtime_dashboard.py:12-16` | def setUpClass(cls) | 2 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.tearDownClass` | method | `tests/test_runtime_dashboard.py:19-22` | def tearDownClass(cls) | 1 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.get` | method | `tests/test_runtime_dashboard.py:24-31` | def get(self, path) | 27 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.test_all_dashboard_routes_open_and_reload` | method | `tests/test_runtime_dashboard.py:33-39` | def test_all_dashboard_routes_open_and_reload(self) | 1 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.test_assets_and_unknown_routes_are_bounded` | method | `tests/test_runtime_dashboard.py:41-47` | def test_assets_and_unknown_routes_are_bounded(self) | 1 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.test_responses_include_browser_hardening_headers` | method | `tests/test_runtime_dashboard.py:49-54` | def test_responses_include_browser_hardening_headers(self) | 1 | test |
| `test_runtime_dashboard.RuntimeDashboardTests.test_world_overview_is_source_backed_and_date_explicit` | method | `tests/test_runtime_dashboard.py:56-63` | def test_world_overview_is_source_backed_and_date_explicit(self) | 1 | test |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests` | class | `tests/test_runtime_dashboard_service.py:11-44` | class RuntimeDashboardServiceTests(unittest.TestCase) | 1 | test |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests.test_snapshot_preserves_source_timestamps_and_failures` | method | `tests/test_runtime_dashboard_service.py:12-23` | def test_snapshot_preserves_source_timestamps_and_failures(self) | 1 | test |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests.test_missing_and_failing_sources_are_visible_not_healthy` | method | `tests/test_runtime_dashboard_service.py:25-34` | def test_missing_and_failing_sources_are_visible_not_healthy(self) | 1 | test |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests.test_reader_output_is_bounded_and_records_are_validated` | method | `tests/test_runtime_dashboard_service.py:36-44` | def test_reader_output_is_bounded_and_records_are_validated(self) | 1 | test |
| `test_runtime_dashboard_service.RuntimeDashboardServiceTests.test_reader_output_is_bounded_and_records_are_validated.too_many` | function | `tests/test_runtime_dashboard_service.py:37-39` | def too_many() | 1 | test |
| `test_runtime_email.FakeEmail` | class | `tests/test_runtime_email.py:18-35` | class FakeEmail() | 1 | test |
| `test_runtime_email.FakeEmail.__init__` | method | `tests/test_runtime_email.py:19-21` | def __init__(self) | 5 | test |
| `test_runtime_email.FakeEmail.search` | method | `tests/test_runtime_email.py:23-25` | def search(self, query, *, limit) | 9 | test |
| `test_runtime_email.FakeEmail.create_draft` | method | `tests/test_runtime_email.py:27-29` | def create_draft(self, draft_id, message) | 1 | test |
| `test_runtime_email.FakeEmail.send` | method | `tests/test_runtime_email.py:31-35` | def send(self, send_id, message) | 3 | test |
| `test_runtime_email.RuntimeEmailTests` | class | `tests/test_runtime_email.py:38-92` | class RuntimeEmailTests(unittest.TestCase) | 1 | test |
| `test_runtime_email.RuntimeEmailTests.test_scopes_and_owner_approval_gate_operations` | method | `tests/test_runtime_email.py:39-53` | def test_scopes_and_owner_approval_gate_operations(self) | 1 | test |
| `test_runtime_email.RuntimeEmailTests.test_send_receipt_is_idempotent_after_reopen` | method | `tests/test_runtime_email.py:55-65` | def test_send_receipt_is_idempotent_after_reopen(self) | 1 | test |
| `test_runtime_email.RuntimeEmailTests.test_timeout_is_fenced_and_receipt_survives_reconciliation` | method | `tests/test_runtime_email.py:67-80` | def test_timeout_is_fenced_and_receipt_survives_reconciliation(self) | 1 | test |
| `test_runtime_email.RuntimeEmailTests.test_effect_journal_does_not_store_message_body` | method | `tests/test_runtime_email.py:82-92` | def test_effect_journal_does_not_store_message_body(self) | 1 | test |
| `test_runtime_file_actions.FileActionServiceTests` | class | `tests/test_runtime_file_actions.py:8-87` | class FileActionServiceTests(unittest.TestCase) | 1 | test |
| `test_runtime_file_actions.FileActionServiceTests.setUp` | method | `tests/test_runtime_file_actions.py:9-21` | def setUp(self) | 35 | test |
| `test_runtime_file_actions.FileActionServiceTests.tearDown` | method | `tests/test_runtime_file_actions.py:23-25` | def tearDown(self) | 12 | test |
| `test_runtime_file_actions.FileActionServiceTests.test_preview_requires_one_file_and_directory_approval_is_forbidden` | method | `tests/test_runtime_file_actions.py:27-35` | def test_preview_requires_one_file_and_directory_approval_is_forbidden(self) | 1 | test |
| `test_runtime_file_actions.FileActionServiceTests.test_each_file_requires_approval_and_trash_is_recoverable` | method | `tests/test_runtime_file_actions.py:37-59` | def test_each_file_requires_approval_and_trash_is_recoverable(self) | 1 | test |
| `test_runtime_file_actions.FileActionServiceTests.test_identity_change_and_protected_or_outside_paths_fail_closed` | method | `tests/test_runtime_file_actions.py:61-76` | def test_identity_change_and_protected_or_outside_paths_fail_closed(self) | 1 | test |
| `test_runtime_file_actions.FileActionServiceTests.test_audit_is_redacted_and_no_direct_delete_operation_exists` | method | `tests/test_runtime_file_actions.py:78-87` | def test_audit_is_redacted_and_no_direct_delete_operation_exists(self) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests` | class | `tests/test_runtime_offline.py:10-102` | class RuntimeOfflineTests(unittest.TestCase) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests._service` | method | `tests/test_runtime_offline.py:11-22` | def _service(self, directory, *, adapter=None, allow_fallback=False) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_unavailable_model_pauses_without_calling_adapter` | method | `tests/test_runtime_offline.py:24-45` | def test_unavailable_model_pauses_without_calling_adapter(self) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_unavailable_model_pauses_without_calling_adapter.adapter` | function | `tests/test_runtime_offline.py:27-29` | def adapter(message, model) | 9 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_unavailable_model_pauses_without_calling_adapter.run` | function | `tests/test_runtime_offline.py:31-34` | async def run(service) | 36 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_explicit_fallback_uses_authorized_adapter` | method | `tests/test_runtime_offline.py:47-65` | def test_explicit_fallback_uses_authorized_adapter(self) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_explicit_fallback_uses_authorized_adapter.adapter` | function | `tests/test_runtime_offline.py:48-49` | async def adapter(_message, model) | 9 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_explicit_fallback_uses_authorized_adapter.run` | function | `tests/test_runtime_offline.py:51-54` | async def run(service) | 36 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_fallback_requires_explicit_opt_in` | method | `tests/test_runtime_offline.py:67-87` | def test_fallback_requires_explicit_opt_in(self) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_fallback_requires_explicit_opt_in.adapter` | function | `tests/test_runtime_offline.py:70-73` | async def adapter(_message, _model) | 9 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_fallback_requires_explicit_opt_in.run` | function | `tests/test_runtime_offline.py:75-78` | async def run(service) | 36 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_registered_model_without_adapter_stays_paused` | method | `tests/test_runtime_offline.py:89-102` | def test_registered_model_without_adapter_stays_paused(self) | 1 | test |
| `test_runtime_offline.RuntimeOfflineTests.test_registered_model_without_adapter_stays_paused.run` | function | `tests/test_runtime_offline.py:90-93` | async def run(service) | 36 | test |
| `test_runtime_qualification.RuntimeQualificationTests` | class | `tests/test_runtime_qualification.py:12-55` | class RuntimeQualificationTests(unittest.TestCase) | 1 | test |
| `test_runtime_qualification.RuntimeQualificationTests.checks` | method | `tests/test_runtime_qualification.py:13-23` | def checks(self, status='passed') | 5 | test |
| `test_runtime_qualification.RuntimeQualificationTests.test_report_requires_all_gates_and_preserves_unresolved_host_evidence` | method | `tests/test_runtime_qualification.py:25-35` | def test_report_requires_all_gates_and_preserves_unresolved_host_evidence(self) | 1 | test |
| `test_runtime_qualification.RuntimeQualificationTests.test_missing_or_duplicate_gate_is_rejected` | method | `tests/test_runtime_qualification.py:37-45` | def test_missing_or_duplicate_gate_is_rejected(self) | 1 | test |
| `test_runtime_qualification.RuntimeQualificationTests.test_passed_record_cannot_hide_failed_command` | method | `tests/test_runtime_qualification.py:47-51` | def test_passed_record_cannot_hide_failed_command(self) | 1 | test |
| `test_runtime_qualification.RuntimeQualificationTests.test_raw_multiline_output_is_not_accepted_as_evidence` | method | `tests/test_runtime_qualification.py:53-55` | def test_raw_multiline_output_is_not_accepted_as_evidence(self) | 1 | test |
| `test_runtime_reminders.RuntimeReminderTests` | class | `tests/test_runtime_reminders.py:16-50` | class RuntimeReminderTests(unittest.TestCase) | 1 | test |
| `test_runtime_reminders.RuntimeReminderTests.test_schedule_and_preferences_survive_restart` | method | `tests/test_runtime_reminders.py:17-32` | def test_schedule_and_preferences_survive_restart(self) | 1 | test |
| `test_runtime_reminders.RuntimeReminderTests.test_daily_schedule_and_disabled_notifications_are_safe` | method | `tests/test_runtime_reminders.py:34-42` | def test_daily_schedule_and_disabled_notifications_are_safe(self) | 1 | test |
| `test_runtime_reminders.RuntimeReminderTests.test_invalid_quiet_hours_are_rejected` | method | `tests/test_runtime_reminders.py:44-50` | def test_invalid_quiet_hours_are_rejected(self) | 1 | test |
| `test_runtime_security.RuntimeSecurityTests` | class | `tests/test_runtime_security.py:15-98` | class RuntimeSecurityTests(unittest.TestCase) | 1 | test |
| `test_runtime_security.RuntimeSecurityTests.setUp` | method | `tests/test_runtime_security.py:16-34` | def setUp(self) | 35 | test |
| `test_runtime_security.RuntimeSecurityTests.tearDown` | method | `tests/test_runtime_security.py:36-38` | def tearDown(self) | 12 | test |
| `test_runtime_security.RuntimeSecurityTests.request` | method | `tests/test_runtime_security.py:40-49` | def request(self, path='/events', *, identity_id='owner', method='GET', **extra) | 23 | test |
| `test_runtime_security.RuntimeSecurityTests.test_owner_session_requires_matching_identity_and_csrf_for_mutations` | method | `tests/test_runtime_security.py:51-68` | def test_owner_session_requires_matching_identity_and_csrf_for_mutations(self) | 1 | test |
| `test_runtime_security.RuntimeSecurityTests.test_host_origin_and_malformed_values_fail_closed` | method | `tests/test_runtime_security.py:70-80` | def test_host_origin_and_malformed_values_fail_closed(self) | 1 | test |
| `test_runtime_security.RuntimeSecurityTests.test_rotation_invalidates_old_session_and_responses_are_hardened` | method | `tests/test_runtime_security.py:82-98` | def test_rotation_invalidates_old_session_and_responses_are_hardened(self) | 1 | test |
| `test_runtime_service.RuntimeServiceTests` | class | `tests/test_runtime_service.py:16-138` | class RuntimeServiceTests(unittest.TestCase) | 1 | test |
| `test_runtime_service.RuntimeServiceTests.setUp` | method | `tests/test_runtime_service.py:17-31` | def setUp(self) | 35 | test |
| `test_runtime_service.RuntimeServiceTests.tearDown` | method | `tests/test_runtime_service.py:33-35` | def tearDown(self) | 12 | test |
| `test_runtime_service.RuntimeServiceTests.request` | method | `tests/test_runtime_service.py:38-45` | def request(path, scope='runtime:read', **extra) | 23 | test |
| `test_runtime_service.RuntimeServiceTests.test_authenticated_health_and_scope_denial` | method | `tests/test_runtime_service.py:47-59` | def test_authenticated_health_and_scope_denial(self) | 1 | test |
| `test_runtime_service.RuntimeServiceTests.test_task_handoff_claim_ack_and_event_stream` | method | `tests/test_runtime_service.py:61-102` | def test_task_handoff_claim_ack_and_event_stream(self) | 1 | test |
| `test_runtime_service.RuntimeServiceTests.test_duplicate_handoff_is_idempotent_and_foreign_scope_is_rejected` | method | `tests/test_runtime_service.py:104-122` | def test_duplicate_handoff_is_idempotent_and_foreign_scope_is_rejected(self) | 1 | test |
| `test_runtime_service.RuntimeServiceTests.test_invalid_target_and_ack_claim_are_fail_closed` | method | `tests/test_runtime_service.py:124-138` | def test_invalid_target_and_ack_claim_are_fail_closed(self) | 1 | test |
| `test_runtime_speech._Adapter` | class | `tests/test_runtime_speech.py:10-21` | class _Adapter() | 1 | test |
| `test_runtime_speech._Adapter.__init__` | method | `tests/test_runtime_speech.py:11-12` | def __init__(self) | 5 | test |
| `test_runtime_speech._Adapter.__call__` | method | `tests/test_runtime_speech.py:14-18` | def __call__(self, _text, _voice) | 1 | test |
| `test_runtime_speech._Adapter.__call__.audio` | function | `tests/test_runtime_speech.py:15-17` | async def audio() | 2 | test |
| `test_runtime_speech._Adapter.stop` | method | `tests/test_runtime_speech.py:20-21` | def stop(self) | 4 | test |
| `test_runtime_speech.RuntimeSpeechTests` | class | `tests/test_runtime_speech.py:24-71` | class RuntimeSpeechTests(unittest.TestCase) | 1 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_streams_bounded_audio_and_completes` | method | `tests/test_runtime_speech.py:25-31` | def test_streams_bounded_audio_and_completes(self) | 1 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_interruption_stops_adapter_without_persisting_speech` | method | `tests/test_runtime_speech.py:33-51` | def test_interruption_stops_adapter_without_persisting_speech(self) | 1 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_interruption_stops_adapter_without_persisting_speech.run` | function | `tests/test_runtime_speech.py:34-42` | async def run(store) | 36 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_adapter_failure_does_not_report_success` | method | `tests/test_runtime_speech.py:53-60` | def test_adapter_failure_does_not_report_success(self) | 1 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_adapter_failure_does_not_report_success.broken` | function | `tests/test_runtime_speech.py:54-55` | def broken(_text, _voice) | 5 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_invalid_audio_is_rejected` | method | `tests/test_runtime_speech.py:62-67` | def test_invalid_audio_is_rejected(self) | 1 | test |
| `test_runtime_speech.RuntimeSpeechTests.test_invalid_audio_is_rejected.broken` | function | `tests/test_runtime_speech.py:63-64` | def broken(_text, _voice) | 5 | test |
| `test_runtime_speech.RuntimeSpeechTests._events` | method | `tests/test_runtime_speech.py:70-71` | async def _events(stream) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests` | class | `tests/test_sda_003_profiles.py:17-154` | class SDA003ProfileTests(unittest.TestCase) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.setUp` | method | `tests/test_sda_003_profiles.py:18-21` | def setUp(self) | 35 | test |
| `test_sda_003_profiles.SDA003ProfileTests.events` | method | `tests/test_sda_003_profiles.py:24-30` | def events(marker) | 24 | test |
| `test_sda_003_profiles.SDA003ProfileTests.fake_run` | method | `tests/test_sda_003_profiles.py:32-46` | def fake_run(self, calls, *, denied_model='', failure_reason='') | 3 | test |
| `test_sda_003_profiles.SDA003ProfileTests.fake_run.run` | function | `tests/test_sda_003_profiles.py:33-45` | def run(command, **kwargs) | 36 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_default_is_pending_and_validation_does_not_launch` | method | `tests/test_sda_003_profiles.py:48-61` | def test_default_is_pending_and_validation_does_not_launch(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_event_protocol_rejects_incomplete_duplicate_corrupt_and_tool_events` | method | `tests/test_sda_003_profiles.py:63-77` | def test_event_protocol_rejects_incomplete_duplicate_corrupt_and_tool_events(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_profile_commands_are_read_only_and_preserve_each_requested_alias` | method | `tests/test_sda_003_profiles.py:79-95` | def test_profile_commands_are_read_only_and_preserve_each_requested_alias(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_unavailable_alias_stops_without_fallback_or_later_roles` | method | `tests/test_sda_003_profiles.py:97-105` | def test_unavailable_alias_stops_without_fallback_or_later_roles(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_controls_and_authentication_stop_before_model_calls` | method | `tests/test_sda_003_profiles.py:107-130` | def test_controls_and_authentication_stop_before_model_calls(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_controls_and_authentication_stop_before_model_calls.denied_login` | function | `tests/test_sda_003_profiles.py:119-123` | def denied_login(command, **kwargs) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_model_failure_reasons_propagate_without_fallback` | method | `tests/test_sda_003_profiles.py:132-140` | def test_model_failure_reasons_propagate_without_fallback(self) | 1 | test |
| `test_sda_003_profiles.SDA003ProfileTests.test_process_timeout_and_output_limit_are_bounded` | method | `tests/test_sda_003_profiles.py:142-154` | def test_process_timeout_and_output_limit_are_bounded(self) | 1 | test |
| `test_sda_shadow_handoff.ShadowHandoffTests` | class | `tests/test_sda_shadow_handoff.py:6-30` | class ShadowHandoffTests(unittest.TestCase) | 1 | test |
| `test_sda_shadow_handoff.ShadowHandoffTests.test_missing_prerequisites_have_stable_keys` | method | `tests/test_sda_shadow_handoff.py:7-12` | def test_missing_prerequisites_have_stable_keys(self) | 1 | test |
| `test_sda_shadow_handoff.ShadowHandoffTests.test_owner_approval_is_required_for_readiness` | method | `tests/test_sda_shadow_handoff.py:14-22` | def test_owner_approval_is_required_for_readiness(self) | 1 | test |
| `test_sda_shadow_handoff.ShadowHandoffTests.test_shadow_mode_cannot_claim_or_promote` | method | `tests/test_sda_shadow_handoff.py:24-30` | def test_shadow_mode_cannot_claim_or_promote(self) | 1 | test |
| `test_system_inventory.SystemInventoryTests` | class | `tests/test_system_inventory.py:9-51` | class SystemInventoryTests(unittest.TestCase) | 1 | test |
| `test_system_inventory.SystemInventoryTests.test_scan_is_metadata_only_bounded_and_does_not_follow_symlinks` | method | `tests/test_system_inventory.py:10-21` | def test_scan_is_metadata_only_bounded_and_does_not_follow_symlinks(self) | 1 | test |
| `test_system_inventory.SystemInventoryTests.test_digest_and_comparison_ignore_collection_time` | method | `tests/test_system_inventory.py:23-29` | def test_digest_and_comparison_ignore_collection_time(self) | 1 | test |
| `test_system_inventory.SystemInventoryTests.test_inventory_reports_model_and_acceleration_capability_slots` | method | `tests/test_system_inventory.py:31-40` | def test_inventory_reports_model_and_acceleration_capability_slots(self) | 1 | test |
| `test_system_inventory.SystemInventoryTests.test_inventory_cli_writes_private_output_and_returns_summary` | method | `tests/test_system_inventory.py:42-51` | def test_inventory_cli_writes_private_output_and_returns_summary(self) | 1 | test |
| `test_tws_aurelia_model.TWSAureliaModelTests` | class | `tests/test_tws_aurelia_model.py:12-41` | class TWSAureliaModelTests(unittest.TestCase) | 1 | test |
| `test_tws_aurelia_model.TWSAureliaModelTests.test_generation_and_validation_are_deterministic` | method | `tests/test_tws_aurelia_model.py:13-25` | def test_generation_and_validation_are_deterministic(self) | 1 | test |
| `test_tws_aurelia_model.TWSAureliaModelTests.test_validator_rejects_deformation_and_clip_corruption` | method | `tests/test_tws_aurelia_model.py:27-35` | def test_validator_rejects_deformation_and_clip_corruption(self) | 1 | test |
| `test_tws_aurelia_model.TWSAureliaModelTests.test_builder_rejects_unknown_deformation_bone` | method | `tests/test_tws_aurelia_model.py:37-41` | def test_builder_rejects_unknown_deformation_bone(self) | 1 | test |
| `test_tws_ci_local.TWSCILocalTests` | class | `tests/test_tws_ci_local.py:8-31` | class TWSCILocalTests(unittest.TestCase) | 1 | test |
| `test_tws_ci_local.TWSCILocalTests.test_python_and_ios_jobs_have_executable_local_equivalents` | method | `tests/test_tws_ci_local.py:9-22` | def test_python_and_ios_jobs_have_executable_local_equivalents(self) | 1 | test |
| `test_tws_ci_local.TWSCILocalTests.test_fallback_receipt_preserves_failure_visibility_without_checkout` | method | `tests/test_tws_ci_local.py:24-31` | def test_fallback_receipt_preserves_failure_visibility_without_checkout(self) | 1 | test |
| `test_tws_cultivation.TWSCultivationTests` | class | `tests/test_tws_cultivation.py:8-74` | class TWSCultivationTests(unittest.TestCase) | 1 | test |
| `test_tws_cultivation.TWSCultivationTests._submitted` | method | `tests/test_tws_cultivation.py:9-19` | def _submitted(self, store: QuestStore, suffix: str='1') -> tuple[str, str] | 1 | test |
| `test_tws_cultivation.TWSCultivationTests._verified_with_reward` | method | `tests/test_tws_cultivation.py:21-28` | def _verified_with_reward(self, store: QuestStore, suffix: str, xp: int=5) -> tuple[str, str] | 1 | test |
| `test_tws_cultivation.TWSCultivationTests.test_progression_requires_independent_proof_acceptance` | method | `tests/test_tws_cultivation.py:30-40` | def test_progression_requires_independent_proof_acceptance(self) | 1 | test |
| `test_tws_cultivation.TWSCultivationTests.test_achievement_and_adaptation_are_idempotent_and_fair` | method | `tests/test_tws_cultivation.py:42-74` | def test_achievement_and_adaptation_are_idempotent_and_fair(self) | 1 | test |
| `test_tws_dialogue.TWSDialogueTests` | class | `tests/test_tws_dialogue.py:8-53` | class TWSDialogueTests(unittest.TestCase) | 1 | test |
| `test_tws_dialogue.TWSDialogueTests._rewarded` | method | `tests/test_tws_dialogue.py:9-18` | def _rewarded(self, store: QuestStore) -> None | 1 | test |
| `test_tws_dialogue.TWSDialogueTests.test_dialogue_state_and_turns_are_idempotent_without_reward_side_effects` | method | `tests/test_tws_dialogue.py:20-45` | def test_dialogue_state_and_turns_are_idempotent_without_reward_side_effects(self) | 1 | test |
| `test_tws_dialogue.TWSDialogueTests.test_dialogue_inputs_are_bounded_and_mood_is_allowlisted` | method | `tests/test_tws_dialogue.py:47-53` | def test_dialogue_inputs_are_bounded_and_mood_is_allowlisted(self) | 1 | test |
| `test_tws_lifecycle.TWSLifecycleTests` | class | `tests/test_tws_lifecycle.py:8-37` | class TWSLifecycleTests(unittest.TestCase) | 1 | test |
| `test_tws_lifecycle.TWSLifecycleTests.test_catalog_metadata_and_lifecycle` | method | `tests/test_tws_lifecycle.py:9-26` | def test_catalog_metadata_and_lifecycle(self) | 1 | test |
| `test_tws_lifecycle.TWSLifecycleTests.test_invalid_transition_and_missing_proof_fail_closed` | method | `tests/test_tws_lifecycle.py:28-37` | def test_invalid_transition_and_missing_proof_fail_closed(self) | 1 | test |
| `test_tws_preferences.TWSPreferenceTests` | class | `tests/test_tws_preferences.py:8-36` | class TWSPreferenceTests(unittest.TestCase) | 1 | test |
| `test_tws_preferences.TWSPreferenceTests.test_onboarding_and_presentation_choices_are_independent` | method | `tests/test_tws_preferences.py:9-25` | def test_onboarding_and_presentation_choices_are_independent(self) | 1 | test |
| `test_tws_preferences.TWSPreferenceTests.test_invalid_preferences_and_onboarding_states_fail_closed` | method | `tests/test_tws_preferences.py:27-36` | def test_invalid_preferences_and_onboarding_states_fail_closed(self) | 1 | test |
| `test_tws_rewards.TWSRewardTests` | class | `tests/test_tws_rewards.py:8-56` | class TWSRewardTests(unittest.TestCase) | 1 | test |
| `test_tws_rewards.TWSRewardTests._verified_quest` | method | `tests/test_tws_rewards.py:9-16` | def _verified_quest(self, store: QuestStore, suffix: str='1') -> tuple[str, str] | 1 | test |
| `test_tws_rewards.TWSRewardTests.test_review_gate_and_reward_retry_are_idempotent` | method | `tests/test_tws_rewards.py:18-32` | def test_review_gate_and_reward_retry_are_idempotent(self) | 1 | test |
| `test_tws_rewards.TWSRewardTests.test_rejected_proof_and_invalid_scope_cannot_be_rewarded` | method | `tests/test_tws_rewards.py:34-43` | def test_rejected_proof_and_invalid_scope_cannot_be_rewarded(self) | 1 | test |
| `test_tws_rewards.TWSRewardTests.test_realm_prerequisites_and_xp_thresholds_are_enforced` | method | `tests/test_tws_rewards.py:45-56` | def test_realm_prerequisites_and_xp_thresholds_are_enforced(self) | 1 | test |
| `test_tws_sanctuary.TWSSanctuaryTests` | class | `tests/test_tws_sanctuary.py:8-27` | class TWSSanctuaryTests(unittest.TestCase) | 1 | test |
| `test_tws_sanctuary.TWSSanctuaryTests.test_sanctuary_snapshot_reads_current_wing_and_quest_ledger` | method | `tests/test_tws_sanctuary.py:9-27` | def test_sanctuary_snapshot_reads_current_wing_and_quest_ledger(self) | 1 | test |
| `test_tws_storage.TWSStorageTests` | class | `tests/test_tws_storage.py:9-59` | class TWSStorageTests(unittest.TestCase) | 1 | test |
| `test_tws_storage.TWSStorageTests.test_versioned_upgrade_preserves_wings_and_proofs` | method | `tests/test_tws_storage.py:10-35` | def test_versioned_upgrade_preserves_wings_and_proofs(self) | 1 | test |
| `test_tws_storage.TWSStorageTests.test_retries_are_idempotent_and_duplicate_proofs_are_rejected` | method | `tests/test_tws_storage.py:37-48` | def test_retries_are_idempotent_and_duplicate_proofs_are_rejected(self) | 1 | test |
| `test_tws_storage.TWSStorageTests.test_rejects_unknown_references_and_invalid_evidence` | method | `tests/test_tws_storage.py:50-59` | def test_rejects_unknown_references_and_invalid_evidence(self) | 1 | test |
| `test_tws_task_import.TWSTaskImportTests` | class | `tests/test_tws_task_import.py:9-64` | class TWSTaskImportTests(unittest.TestCase) | 1 | test |
| `test_tws_task_import.TWSTaskImportTests._task` | method | `tests/test_tws_task_import.py:10-20` | def _task(self, task_id='CORE-IMPORT-1', source_module='core') | 1 | test |
| `test_tws_task_import.TWSTaskImportTests.test_import_is_consent_bound_idempotent_and_draft_only` | method | `tests/test_tws_task_import.py:22-37` | def test_import_is_consent_bound_idempotent_and_draft_only(self) | 1 | test |
| `test_tws_task_import.TWSTaskImportTests.test_import_rejects_missing_consent_or_same_task_mutation` | method | `tests/test_tws_task_import.py:39-50` | def test_import_rejects_missing_consent_or_same_task_mutation(self) | 1 | test |
| `test_tws_task_import.TWSTaskImportTests.test_import_accepts_only_known_cross_module_sources` | method | `tests/test_tws_task_import.py:52-64` | def test_import_accepts_only_known_cross_module_sources(self) | 1 | test |
| `test_tws_visual_qa.manifest` | function | `tests/test_tws_visual_qa.py:6-19` | def manifest() | 16 | test |
| `test_tws_visual_qa.TWSVisualQATests` | class | `tests/test_tws_visual_qa.py:22-38` | class TWSVisualQATests(unittest.TestCase) | 1 | test |
| `test_tws_visual_qa.TWSVisualQATests.test_manifest_requires_24_views_and_motion_samples` | method | `tests/test_tws_visual_qa.py:23-26` | def test_manifest_requires_24_views_and_motion_samples(self) | 1 | test |
| `test_tws_visual_qa.TWSVisualQATests.test_manifest_rejects_static_motion` | method | `tests/test_tws_visual_qa.py:28-32` | def test_manifest_rejects_static_motion(self) | 1 | test |
| `test_tws_visual_qa.TWSVisualQATests.test_manifest_rejects_duplicate_view_index` | method | `tests/test_tws_visual_qa.py:34-38` | def test_manifest_rejects_duplicate_view_index(self) | 1 | test |
| `test_wic_alerts.digest` | function | `tests/test_wic_alerts.py:12-13` | def digest(value) | 17 | test |
| `test_wic_alerts.WICAlertTests` | class | `tests/test_wic_alerts.py:16-91` | class WICAlertTests(unittest.TestCase) | 1 | test |
| `test_wic_alerts.WICAlertTests.policy` | method | `tests/test_wic_alerts.py:17-26` | def policy(self, **changes) | 16 | test |
| `test_wic_alerts.WICAlertTests.test_material_change_is_queued_once_and_persists` | method | `tests/test_wic_alerts.py:28-44` | def test_material_change_is_queued_once_and_persists(self) | 1 | test |
| `test_wic_alerts.WICAlertTests.test_non_material_change_does_not_create_alert` | method | `tests/test_wic_alerts.py:46-55` | def test_non_material_change_does_not_create_alert(self) | 1 | test |
| `test_wic_alerts.WICAlertTests.test_quiet_hours_and_cadence_suppress_without_delivery` | method | `tests/test_wic_alerts.py:57-79` | def test_quiet_hours_and_cadence_suppress_without_delivery(self) | 1 | test |
| `test_wic_alerts.WICAlertTests.test_owner_scope_and_disabled_policy_fail_closed` | method | `tests/test_wic_alerts.py:81-91` | def test_owner_scope_and_disabled_policy_fail_closed(self) | 1 | test |
| `test_wic_categories.WICCategoryTests` | class | `tests/test_wic_categories.py:12-48` | class WICCategoryTests(unittest.TestCase) | 1 | test |
| `test_wic_categories.WICCategoryTests.test_assignments_are_searchable` | method | `tests/test_wic_categories.py:13-19` | def test_assignments_are_searchable(self) | 1 | test |
| `test_wic_categories.WICCategoryTests.test_correction_replaces_current_search_and_preserves_history` | method | `tests/test_wic_categories.py:21-29` | def test_correction_replaces_current_search_and_preserves_history(self) | 1 | test |
| `test_wic_categories.WICCategoryTests.test_invalid_category_and_duplicate_assignment_fail_closed` | method | `tests/test_wic_categories.py:31-38` | def test_invalid_category_and_duplicate_assignment_fail_closed(self) | 1 | test |
| `test_wic_categories.WICCategoryTests.test_history_survives_reopen` | method | `tests/test_wic_categories.py:40-48` | def test_history_survives_reopen(self) | 1 | test |
| `test_wic_clusters.observation` | function | `tests/test_wic_clusters.py:14-18` | def observation(observation_id, source_id, article_url) | 3 | test |
| `test_wic_clusters.WICClusterTests` | class | `tests/test_wic_clusters.py:21-68` | class WICClusterTests(unittest.TestCase) | 1 | test |
| `test_wic_clusters.WICClusterTests.test_normalize_url_removes_tracking_and_fragment_variants` | method | `tests/test_wic_clusters.py:22-26` | def test_normalize_url_removes_tracking_and_fragment_variants(self) | 1 | test |
| `test_wic_clusters.WICClusterTests.test_same_incident_keeps_both_sources_in_one_cluster` | method | `tests/test_wic_clusters.py:28-39` | def test_same_incident_keeps_both_sources_in_one_cluster(self) | 1 | test |
| `test_wic_clusters.WICClusterTests.test_cluster_membership_survives_reopen_and_replay` | method | `tests/test_wic_clusters.py:41-51` | def test_cluster_membership_survives_reopen_and_replay(self) | 1 | test |
| `test_wic_clusters.WICClusterTests.test_different_urls_require_explicit_incident_key` | method | `tests/test_wic_clusters.py:53-59` | def test_different_urls_require_explicit_incident_key(self) | 1 | test |
| `test_wic_clusters.WICClusterTests.test_one_observation_cannot_be_assigned_to_two_incidents` | method | `tests/test_wic_clusters.py:61-68` | def test_one_observation_cannot_be_assigned_to_two_incidents(self) | 1 | test |
| `test_wic_sources.WICSourceTests` | class | `tests/test_wic_sources.py:19-174` | class WICSourceTests(unittest.TestCase) | 1 | test |
| `test_wic_sources.WICSourceTests.policy` | method | `tests/test_wic_sources.py:20-21` | def policy(self) | 16 | test |
| `test_wic_sources.WICSourceTests.service` | method | `tests/test_wic_sources.py:23-24` | def service(self, store, **kwargs) | 27 | test |
| `test_wic_sources.WICSourceTests.test_ingestion_retains_authorized_urls_and_separate_timestamps` | method | `tests/test_wic_sources.py:26-50` | def test_ingestion_retains_authorized_urls_and_separate_timestamps(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_observations_survive_store_reopen` | method | `tests/test_wic_sources.py:52-62` | def test_observations_survive_store_reopen(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_replay_is_idempotent` | method | `tests/test_wic_sources.py:64-73` | def test_replay_is_idempotent(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_foreign_items_are_rejected_without_persistence` | method | `tests/test_wic_sources.py:75-84` | def test_foreign_items_are_rejected_without_persistence(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_unallowlisted_feed_is_blocked_before_transport` | method | `tests/test_wic_sources.py:86-95` | def test_unallowlisted_feed_is_blocked_before_transport(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_provider_failure_is_bounded` | method | `tests/test_wic_sources.py:97-105` | def test_provider_failure_is_bounded(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_health_becomes_stale_after_successful_snapshot_age` | method | `tests/test_wic_sources.py:107-122` | def test_health_becomes_stale_after_successful_snapshot_age(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_provider_outage_preserves_last_success_and_marks_outage` | method | `tests/test_wic_sources.py:124-140` | def test_provider_outage_preserves_last_success_and_marks_outage(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_unknown_health_has_no_false_timestamp` | method | `tests/test_wic_sources.py:142-149` | def test_unknown_health_has_no_false_timestamp(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_invalid_dates_are_rejected_and_valid_items_remain` | method | `tests/test_wic_sources.py:151-161` | def test_invalid_dates_are_rejected_and_valid_items_remain(self) | 1 | test |
| `test_wic_sources.WICSourceTests.test_non_public_policy_and_bad_observation_fail_closed` | method | `tests/test_wic_sources.py:163-174` | def test_non_public_policy_and_bad_observation_fail_closed(self) | 1 | test |
| `test_wic_summaries.WICSummariesTests` | class | `tests/test_wic_summaries.py:11-49` | class WICSummariesTests(unittest.TestCase) | 1 | test |
| `test_wic_summaries.WICSummariesTests.segment` | method | `tests/test_wic_summaries.py:12-16` | def segment(self, claim_id, certainty='verified', note=None) | 2 | test |
| `test_wic_summaries.WICSummariesTests.test_citations_and_uncertainty_survive_synthesis` | method | `tests/test_wic_summaries.py:18-29` | def test_citations_and_uncertainty_survive_synthesis(self) | 1 | test |
| `test_wic_summaries.WICSummariesTests.test_live_freshness_is_rejected` | method | `tests/test_wic_summaries.py:31-33` | def test_live_freshness_is_rejected(self) | 1 | test |
| `test_wic_summaries.WICSummariesTests.test_unsupported_certainty_cannot_be_composed` | method | `tests/test_wic_summaries.py:35-39` | def test_unsupported_certainty_cannot_be_composed(self) | 1 | test |
| `test_wic_summaries.WICSummariesTests.test_summary_store_is_idempotent_and_survives_reopen` | method | `tests/test_wic_summaries.py:41-49` | def test_summary_store_is_idempotent_and_survives_reopen(self) | 1 | test |
| `test_wic_verification.observation` | function | `tests/test_wic_verification.py:18-22` | def observation(observation_id, source_id, article_number) | 3 | test |
| `test_wic_verification.digest` | function | `tests/test_wic_verification.py:25-26` | def digest(value) | 17 | test |
| `test_wic_verification.WICVerificationTests` | class | `tests/test_wic_verification.py:29-100` | class WICVerificationTests(unittest.TestCase) | 1 | test |
| `test_wic_verification.WICVerificationTests.cluster` | method | `tests/test_wic_verification.py:30-34` | def cluster(self, path, include_second=True) | 2 | test |
| `test_wic_verification.WICVerificationTests.test_uncertain_claim_cannot_be_verified` | method | `tests/test_wic_verification.py:36-44` | def test_uncertain_claim_cannot_be_verified(self) | 1 | test |
| `test_wic_verification.WICVerificationTests.test_corroboration_is_required_before_verification` | method | `tests/test_wic_verification.py:46-56` | def test_corroboration_is_required_before_verification(self) | 1 | test |
| `test_wic_verification.WICVerificationTests.test_retraction_is_visible_and_blocks_verification` | method | `tests/test_wic_verification.py:58-70` | def test_retraction_is_visible_and_blocks_verification(self) | 1 | test |
| `test_wic_verification.WICVerificationTests.test_correction_preserves_retraction_history` | method | `tests/test_wic_verification.py:72-89` | def test_correction_preserves_retraction_history(self) | 1 | test |
| `test_wic_verification.WICVerificationTests.test_claim_history_survives_reopen` | method | `tests/test_wic_verification.py:91-100` | def test_claim_history_survives_reopen(self) | 1 | test |
| `test_wic_watchlists.WICWatchlistTests` | class | `tests/test_wic_watchlists.py:11-53` | class WICWatchlistTests(unittest.TestCase) | 1 | test |
| `test_wic_watchlists.WICWatchlistTests.test_owner_can_save_and_reopen_preferences` | method | `tests/test_wic_watchlists.py:12-25` | def test_owner_can_save_and_reopen_preferences(self) | 1 | test |
| `test_wic_watchlists.WICWatchlistTests.test_preferences_are_owner_scoped` | method | `tests/test_wic_watchlists.py:27-33` | def test_preferences_are_owner_scoped(self) | 1 | test |
| `test_wic_watchlists.WICWatchlistTests.test_unchanged_save_is_idempotent_and_changes_are_revisioned` | method | `tests/test_wic_watchlists.py:35-47` | def test_unchanged_save_is_idempotent_and_changes_are_revisioned(self) | 1 | test |
| `test_wic_watchlists.WICWatchlistTests.test_invalid_duplicate_preferences_fail_closed` | method | `tests/test_wic_watchlists.py:49-53` | def test_invalid_duplicate_preferences_fail_closed(self) | 1 | test |
| `test_wic_world.card` | function | `tests/test_wic_world.py:9-19` | def card(card_id, event_at, *, status='active', correction=None) | 1 | test |
| `test_wic_world.WICWorldTests` | class | `tests/test_wic_world.py:22-55` | class WICWorldTests(unittest.TestCase) | 1 | test |
| `test_wic_world.WICWorldTests.test_card_preserves_source_and_independent_dates` | method | `tests/test_wic_world.py:23-31` | def test_card_preserves_source_and_independent_dates(self) | 1 | test |
| `test_wic_world.WICWorldTests.test_correction_is_visible_and_retraction_is_not_silent` | method | `tests/test_wic_world.py:33-40` | def test_correction_is_visible_and_retraction_is_not_silent(self) | 1 | test |
| `test_wic_world.WICWorldTests.test_timeline_is_bounded_and_newest_first` | method | `tests/test_wic_world.py:42-49` | def test_timeline_is_bounded_and_newest_first(self) | 1 | test |
| `test_wic_world.WICWorldTests.test_empty_timeline_is_explicit_and_duplicates_fail_closed` | method | `tests/test_wic_world.py:51-55` | def test_empty_timeline_is_explicit_and_duplicates_fail_closed(self) | 1 | test |
| `astra_watchdog._regular` | function | `tools/astra_watchdog.py:34-38` | def _regular(path: Path, label: str) -> Path | 0 | active |
| `astra_watchdog._read_settings` | function | `tools/astra_watchdog.py:41-42` | def _read_settings(db: sqlite3.Connection) -> dict[str, str] | 0 | active |
| `astra_watchdog._git_commit_exists` | function | `tools/astra_watchdog.py:45-51` | def _git_commit_exists(repository: Path, sha: str) -> None | 0 | active |
| `astra_watchdog._git_head` | function | `tools/astra_watchdog.py:54-59` | def _git_head(repository: Path) -> str | 0 | active |
| `astra_watchdog._git_clean` | function | `tools/astra_watchdog.py:62-69` | def _git_clean(repository: Path) -> None | 0 | active |
| `astra_watchdog._git_fast_forward` | function | `tools/astra_watchdog.py:72-79` | def _git_fast_forward(repository: Path, sha: str) -> None | 0 | active |
| `astra_watchdog._git_restore` | function | `tools/astra_watchdog.py:82-91` | def _git_restore(repository: Path, sha: str) -> None | 0 | active |
| `astra_watchdog._activation_journal` | function | `tools/astra_watchdog.py:94-97` | def _activation_journal(state_dir: Path, batch_id: str) -> Path | 0 | active |
| `astra_watchdog._write_journal` | function | `tools/astra_watchdog.py:100-106` | def _write_journal(path: Path, payload: dict) -> str | 0 | active |
| `astra_watchdog._read_journal` | function | `tools/astra_watchdog.py:109-128` | def _read_journal(path: Path) -> dict | 0 | active |
| `astra_watchdog._open_readonly` | function | `tools/astra_watchdog.py:131-135` | def _open_readonly(db_path: Path) -> sqlite3.Connection | 0 | active |
| `astra_watchdog._verified_backup` | function | `tools/astra_watchdog.py:138-147` | def _verified_backup(state_dir: Path, db_path: Path, batch_id: str) -> tuple[Path, str] | 0 | active |
| `astra_watchdog.check` | function | `tools/astra_watchdog.py:150-189` | def check(state_dir: Path) -> dict | 23 | active |
| `astra_watchdog._activation_ready` | function | `tools/astra_watchdog.py:192-221` | def _activation_ready(db: sqlite3.Connection, batch_id: str) -> sqlite3.Row | 0 | active |
| `astra_watchdog._require_no_controls` | function | `tools/astra_watchdog.py:224-227` | def _require_no_controls(state_dir: Path) -> None | 0 | active |
| `astra_watchdog.activate` | function | `tools/astra_watchdog.py:230-391` | def activate(state_dir: Path, batch_id: str) -> dict | 1 | active |
| `astra_watchdog.rollback` | function | `tools/astra_watchdog.py:394-480` | def rollback(state_dir: Path, batch_id: str) -> dict | 9 | active |
| `astra_watchdog.main` | function | `tools/astra_watchdog.py:483-502` | def main() -> int | 155 | active |
| `build_final_audit.git` | function | `tools/build_final_audit.py:79-85` | def git(repo: Path, *args: str) -> str | 19 | active |
| `build_final_audit.sha256` | function | `tools/build_final_audit.py:88-89` | def sha256(data: bytes) -> str | 28 | active |
| `build_final_audit.read_text` | function | `tools/build_final_audit.py:92-93` | def read_text(path: Path) -> str | 28 | active |
| `build_final_audit.relative` | function | `tools/build_final_audit.py:96-97` | def relative(repo: Path, path: Path) -> str | 2 | active |
| `build_final_audit.excluded` | function | `tools/build_final_audit.py:100-106` | def excluded(repo: Path, path: Path) -> bool | 5 | active |
| `build_final_audit.iter_files` | function | `tools/build_final_audit.py:109-117` | def iter_files(repo: Path, suffixes: set[str]) -> list[Path] | 0 | active |
| `build_final_audit.module_name` | function | `tools/build_final_audit.py:120-130` | def module_name(rel: str) -> str | 0 | active |
| `build_final_audit.expr_name` | function | `tools/build_final_audit.py:133-139` | def expr_name(node: ast.AST \| None) -> str | 0 | active |
| `build_final_audit.ast_signature` | function | `tools/build_final_audit.py:142-147` | def ast_signature(node: ast.FunctionDef \| ast.AsyncFunctionDef) -> str | 0 | active |
| `build_final_audit.body_text` | function | `tools/build_final_audit.py:150-153` | def body_text(source: str, node: ast.AST) -> str | 0 | active |
| `build_final_audit.side_effects` | function | `tools/build_final_audit.py:156-157` | def side_effects(text: str) -> list[str] | 0 | active |
| `build_final_audit.security_reasons` | function | `tools/build_final_audit.py:160-172` | def security_reasons(path: str, name: str, text: str) -> list[str] | 0 | active |
| `build_final_audit.maintenance_status` | function | `tools/build_final_audit.py:175-182` | def maintenance_status(path: str) -> str | 0 | active |
| `build_final_audit.recommendation` | function | `tools/build_final_audit.py:185-193` | def recommendation(path: str, name: str) -> str | 1 | active |
| `build_final_audit.make_record` | function | `tools/build_final_audit.py:196-239` | def make_record(*, path: str, module: str, symbol: str, qualified_name: str, kind: str, start: int, end: int, signature: str, purpose: str, inputs: list[str], outputs: list[str], b | 0 | active |
| `build_final_audit.parse_python` | function | `tools/build_final_audit.py:242-338` | def parse_python(repo: Path, path: Path) -> tuple[list[dict[str, Any]], list[str], str \| None] | 0 | active |
| `build_final_audit.parse_python.visit` | function | `tools/build_final_audit.py:258-333` | def visit(node: ast.AST, prefix: str='', parent: str='') -> None | 0 | active |
| `build_final_audit.parse_other` | function | `tools/build_final_audit.py:341-385` | def parse_other(repo: Path, path: Path) -> tuple[list[dict[str, Any]], list[str], str \| None] | 0 | active |
| `build_final_audit.parse_code` | function | `tools/build_final_audit.py:388-420` | def parse_code(repo: Path, paths: Iterable[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]] | 0 | active |
| `build_final_audit.resolve_relations` | function | `tools/build_final_audit.py:423-474` | def resolve_relations(records: list[dict[str, Any]], all_text: dict[str, str]) -> dict[str, Any] | 0 | active |
| `build_final_audit.markdown_table` | function | `tools/build_final_audit.py:477-484` | def markdown_table(rows: list[list[str]]) -> str | 0 | active |
| `build_final_audit.md_code` | function | `tools/build_final_audit.py:487-488` | def md_code(value: object) -> str | 0 | active |
| `build_final_audit.build_call_graph` | function | `tools/build_final_audit.py:491-500` | def build_call_graph(symbols: list[dict[str, Any]]) -> str | 0 | active |
| `build_final_audit.build_module_dependencies` | function | `tools/build_final_audit.py:503-514` | def build_module_dependencies(symbols: list[dict[str, Any]]) -> str | 0 | active |
| `build_final_audit.build_unused` | function | `tools/build_final_audit.py:517-530` | def build_unused(catalog: dict[str, Any]) -> str | 0 | active |
| `build_final_audit.build_security` | function | `tools/build_final_audit.py:533-542` | def build_security(symbols: list[dict[str, Any]]) -> str | 0 | active |
| `build_final_audit.build_markdown` | function | `tools/build_final_audit.py:545-587` | def build_markdown(catalog: dict[str, Any]) -> dict[str, str] | 0 | active |
| `build_final_audit.index_files` | function | `tools/build_final_audit.py:590-630` | def index_files(repo: Path, paths: list[Path], source_sha: str, database: Path) -> dict[str, Any] | 0 | active |
| `build_final_audit.write_json` | function | `tools/build_final_audit.py:633-634` | def write_json(path: Path, payload: Any) -> None | 0 | active |
| `build_final_audit.main` | function | `tools/build_final_audit.py:637-730` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `check_git_policy.check_branch` | function | `tools/check_git_policy.py:7-12` | def check_branch(name: str) | 1 | active |
| `check_git_policy.check_commit` | function | `tools/check_git_policy.py:13-16` | def check_commit(s: str) | 1 | active |
| `check_git_policy.main` | function | `tools/check_git_policy.py:18-27` | def main(argv=None) | 155 | active |
| `ci_checks._quiet_run` | function | `tools/ci_checks.py:48-63` | def _quiet_run(args: list[str], *, cwd: Path \| None=None, timeout: int=60, env: dict[str, str] \| None=None) -> int | 0 | active |
| `ci_checks._build_local_wheel` | function | `tools/ci_checks.py:66-124` | def _build_local_wheel(root: Path, project: dict, requirements: list[str], output: Path) -> bool | 0 | active |
| `ci_checks.dependency_scan` | function | `tools/ci_checks.py:127-213` | def dependency_scan() -> int | 1 | active |
| `ci_checks._contains_secret` | function | `tools/ci_checks.py:216-217` | def _contains_secret(data: bytes) -> bool | 1 | active |
| `ci_checks._workspace_files` | function | `tools/ci_checks.py:220-239` | def _workspace_files() -> Iterable[str] | 0 | active |
| `ci_checks._read_workspace_file` | function | `tools/ci_checks.py:242-274` | def _read_workspace_file(relative: str) -> bytes | 0 | active |
| `ci_checks.secret_scan` | function | `tools/ci_checks.py:277-290` | def secret_scan() -> int | 1 | active |
| `ci_checks._workflow_is_safe` | function | `tools/ci_checks.py:293-354` | def _workflow_is_safe(text: str) -> bool | 1 | active |
| `ci_checks._workflow_files` | function | `tools/ci_checks.py:357-358` | def _workflow_files() -> Iterable[Path] | 0 | active |
| `ci_checks.security_scan` | function | `tools/ci_checks.py:361-378` | def security_scan() -> int | 1 | active |
| `ci_checks.main` | function | `tools/ci_checks.py:381-390` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `ci_report.normalize_report` | function | `tools/ci_report.py:54-111` | def normalize_report(checks: list[Mapping[str, object]], *, profile: str='python', commit: str=ZERO_SHA, run_id: str='0', remote_status: str='DEFERRED_QUOTA', provenance: Mapping[s | 2 | active |
| `ci_report._safe_target` | function | `tools/ci_report.py:114-135` | def _safe_target(path: Path, root: Path) -> Path | 0 | active |
| `ci_report._open_directory` | function | `tools/ci_report.py:138-154` | def _open_directory(path: Path) -> int | 0 | active |
| `ci_report._write_report` | function | `tools/ci_report.py:157-191` | def _write_report(path: Path, checks: list[Mapping[str, object]], root: Path, *, profile: str='python', commit: str=ZERO_SHA, run_id: str='0', remote_status: str='DEFERRED_QUOTA',  | 1 | active |
| `ci_report.write_report` | function | `tools/ci_report.py:194-209` | def write_report(path: Path, checks: list[Mapping[str, object]], *, root: Path, profile: str='python', commit: str=ZERO_SHA, run_id: str='0', remote_status: str='DEFERRED_QUOTA', p | 1 | active |
| `ci_report.main` | function | `tools/ci_report.py:212-266` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `import_legacy.git` | function | `tools/import_legacy.py:9-11` | def git(repo, *args) | 19 | active |
| `import_legacy.safe_relative` | function | `tools/import_legacy.py:13-19` | def safe_relative(value) | 0 | active |
| `import_legacy._casefold_parts` | function | `tools/import_legacy.py:21-22` | def _casefold_parts(path) | 0 | active |
| `import_legacy._check_existing_path` | function | `tools/import_legacy.py:24-43` | def _check_existing_path(dest, relative) | 0 | active |
| `import_legacy._validate_commit_pin` | function | `tools/import_legacy.py:45-49` | def _validate_commit_pin(value) | 0 | active |
| `import_legacy.prepare_manifest` | function | `tools/import_legacy.py:51-107` | def prepare_manifest(repo: Path, dest: Path, manifest: dict, *, apply: bool=False, allow_fixture_origin: bool=False) | 5 | active |
| `import_legacy.main` | function | `tools/import_legacy.py:109-118` | def main(argv=None) | 155 | active |
| `verify_codex_profiles._control` | function | `tools/verify_codex_profiles.py:33-34` | def _control(home: Path) -> str | 0 | active |
| `verify_codex_profiles._bounded_run` | function | `tools/verify_codex_profiles.py:37-109` | def _bounded_run(command: list[str], *, cwd: Path, home: Path, timeout: int, prompt: str='') -> tuple[dict, str, str] | 1 | active |
| `verify_codex_profiles._event_reason` | function | `tools/verify_codex_profiles.py:112-162` | def _event_reason(stdout: str, stderr: str, exit_code: int \| None, marker: str) -> tuple[str, list[str]] | 1 | active |
| `verify_codex_profiles._profile_command` | function | `tools/verify_codex_profiles.py:165-174` | def _profile_command(worktree: Path, model: str, effort: str) -> list[str] | 0 | active |
| `verify_codex_profiles._valid_profiles` | function | `tools/verify_codex_profiles.py:177-187` | def _valid_profiles(models: dict[str, str], efforts: dict[str, str], timeout: int) -> bool | 0 | active |
| `verify_codex_profiles.verify_profiles` | function | `tools/verify_codex_profiles.py:190-265` | def verify_profiles(*, models: dict[str, str], efforts: dict[str, str] \| None=None, execute: bool=False, home: Path=DEFAULT_HOME, timeout: int=60) -> dict | 1 | active |
| `verify_codex_profiles.main` | function | `tools/verify_codex_profiles.py:268-287` | def main(argv: list[str] \| None=None) -> int | 155 | active |
| `verify_foundation._validate_windows_component` | function | `tools/verify_foundation.py:16-20` | def _validate_windows_component(part: str) -> None | 0 | active |
| `verify_foundation.safe_import_target` | function | `tools/verify_foundation.py:23-34` | def safe_import_target(value: object) -> PurePosixPath | 1 | active |
| `verify_foundation.verify_foundation` | function | `tools/verify_foundation.py:37-58` | def verify_foundation() -> str | 1 | active |
