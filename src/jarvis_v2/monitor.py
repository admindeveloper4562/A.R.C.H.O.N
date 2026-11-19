"""ATLAS terminal monitor: independent, read-only view of Astra One or native ATLAS.

No runner imports, no subprocesses, no daemon, no database initialization.
Every SQLite connection uses mode=ro and PRAGMA query_only=ON. Compatible with
Astra One Linux v0.2/v0.3 sda.sqlite3 databases and the JARVIS v2 foundation
Core queue.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
import sys
import time
from typing import Any

from .monitor_supervision import collect as collect_supervision, render_lines as render_supervision, safe_failure_code

ARCHON_DEFAULT = Path.home() / '.local' / 'state' / 'archon' / 'sda.sqlite3'
ASTRA_DEFAULT = Path.home() / '.local' / 'state' / 'archon-astra' / 'sda.sqlite3'
ASTRA_LEGACY = Path.home() / '.local' / 'state' / 'astra-one-linux' / 'sda.sqlite3'
ATLAS_DEFAULT = Path.home() / '.local' / 'state' / 'archon' / 'atlas.sqlite3'
ACTIVE = {'preflight', 'coding', 'verifying', 'leased', 'running'}
WAITING_REVIEW = {'awaiting_review'}
WAITING_MERGE = {'approved'}
DONE = {'completed'}
BLOCKED = {'failed', 'conflict', 'interrupted', 'stopped', 'cancelled'}


def _safe(value: Any, maxlen: int = 100) -> str:
    """Render untrusted task text without terminal escapes or private payload dumps."""
    text = str(value) if value is not None else ''
    text = ''.join(c if c.isprintable() else ' ' for c in text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(?i)\b(token|api[_-]?key|password|secret|bearer)\b\s*[:=]\s*[^ ]+', r'\1=<redacted>', text)
    if maxlen >= 4 and len(text) > maxlen:
        text = text[:maxlen - 1] + '…'
    return text


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open an existing SQLite DB, fail closed on missing path, never create files."""
    db_path = Path(db_path).expanduser().absolute()
    if not db_path.is_file() or db_path.is_symlink():
        raise ValueError(f'no existing regular SQLite database at {db_path}')
    db = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True, timeout=0.6)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    db.execute('PRAGMA busy_timeout=500')
    return db


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    if table not in {'tasks', 'runs', 'events', 'settings'}:
        return set()
    return {r['name'] for r in db.execute('PRAGMA table_info(' + table + ')')}


def _detect(db: sqlite3.Connection) -> str:
    columns = _columns(db, 'tasks')
    if {'id', 'spec', 'status', 'attempt', 'branch', 'last_run'} <= columns and _columns(db, 'runs'):
        return 'astra'
    if {'id', 'module', 'state', 'created_id'} <= columns:
        return 'atlas'
    raise ValueError('unrecognized task schema; pass a supported Astra One or ATLAS database')


def _parse_time(value: str | None) -> str:
    if not value:
        return '—'
    try:
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    except (ValueError, TypeError):
        return _safe(value, 26)


def _age(value: str | None) -> str:
    if not value:
        return '—'
    try:
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        seconds = max(0, int((datetime.now(timezone.utc) - d.astimezone(timezone.utc)).total_seconds()))
        if seconds < 60:
            return f'{seconds}s'
        if seconds < 3600:
            return f'{seconds // 60}m {seconds % 60}s'
        if seconds < 86400:
            return f'{seconds // 3600}h {(seconds % 3600) // 60}m'
        return f'{seconds // 86400}d {(seconds % 86400) // 3600}h'
    except (ValueError, TypeError):
        return '—'


def _fetch_astra(db: sqlite3.Connection, limit: int, event_limit: int, show_objectives: bool) -> dict:
    settings = {r['key']: r['value'] for r in db.execute('SELECT key,value FROM settings')}
    taskrows = [dict(r) for r in db.execute('''
        SELECT id,spec,status,attempt,branch,base_sha,candidate_sha,last_error,
               last_run,updated_at,created_at
        FROM tasks ORDER BY created_at,id''')]
    counts = Counter(x['status'] for x in taskrows)
    runs = [dict(r) for r in db.execute('''
        SELECT id,task_id,attempt,role,status,started_at,finished_at,model,tool_count,error_code
        FROM runs ORDER BY started_at DESC, id DESC LIMIT ?''', (max(limit * 3, 15),))]
    events = [dict(r) for r in db.execute('''
        SELECT task_id,run_id,time,stage,step,branch,tool_count,result,attempt
        FROM events ORDER BY time DESC, rowid DESC LIMIT ?''', (max(100, event_limit * 8),))]
    # Events can outlive a retry. Resolve progress and slot ONLY from the
    # task's current run, never from a previous failed attempt.
    by_run: dict[str, list[dict]] = {}
    for event in events:
        by_run.setdefault(event['run_id'], []).append(event)
    current = []
    for task in taskrows:
        try:
            spec = json.loads(task['spec'])
            if not isinstance(spec, dict):
                spec = {}
        except (TypeError, json.JSONDecodeError):
            spec = {}
        task.pop('spec', None)  # Never disclose full prompt, acceptance criteria or hidden details in --json.
        task['objective'] = _safe(spec.get('objective', ''), 150) if show_objectives else '(hidden)'
        task['area'] = _safe(spec.get('area', ''), 24)
        task['branch'] = _safe(task.get('branch', ''), 75)
        task['last_error'] = safe_failure_code(task.get('last_error', ''), 85)
        current_events = [e for e in by_run.get(task.get('last_run') or '', [])
                          if e['task_id'] == task['id']]
        slot = None
        for event in current_events:
            m = re.fullmatch(r'(?:worker|repairer)_(\d+)_(?:leased|codex_start)', event.get('step', ''))
            if m:
                slot = m.group(1)
                break
        task['slot'] = slot
        ev = current_events[0] if current_events else None
        task['step'] = _safe(ev.get('step') if ev else '', 70)
        task['stage'] = _safe(ev.get('stage') if ev else task['status'], 22)
        current.append(task)
    active = [x for x in current if x['status'] in ACTIVE]
    review = [x for x in current if x['status'] in WAITING_REVIEW]
    merging = [x for x in current if x['status'] in WAITING_MERGE]
    blocked = [x for x in current if x['status'] in BLOCKED]
    queued = [x for x in current if x['status'] == 'queued']
    run_by_id = {x['id']: x for x in runs}
    for t in active:
        r = run_by_id.get(t['last_run'], {})
        t['model'] = _safe(r.get('model', '—'), 35)
        t['role'] = _safe(r.get('role', 'worker'), 20)
        t['tools'] = r.get('tool_count', 0)
        t['elapsed'] = _age(r.get('started_at'))
    sha = settings.get('architecture_sha', '')
    version = _safe(settings.get('version', '0.2.0'), 20)
    if not version.startswith('v'):
        version = 'v' + version
    return {
        'engine': 'astra', 'schema': f'Astra One Linux {version}',
        'architecture_approved': bool(sha and settings.get('approved_architecture_sha') == sha),
        'source_sha': settings.get('source_sha', ''),
        'integration_sha': settings.get('integration_sha', ''),
        'integration_branch': _safe(settings.get('integration_branch', ''), 80),
        'counts': dict(counts), 'total': len(current),
        'active': active[:limit], 'queued': queued[:limit],
        'review': review[:limit], 'merging': merging[:limit],
        'blocked': blocked[:limit],
        'events': [{k: (safe_failure_code(e.get(k,''), 70) if k == 'result' else _safe(e.get(k,''), 90))
                    for k in ('task_id','time','stage','step','result')} for e in events[:event_limit]],
        'recent_runs': [{k: (safe_failure_code(r.get(k,''), 70) if k == 'error_code' else _safe(r.get(k,''), 70)) for k in ('task_id','role','status','model','started_at','finished_at','error_code')} for r in runs[:limit]],
        'supervision': collect_supervision(db, limit),
    }


def _fetch_atlas(db: sqlite3.Connection, limit: int, event_limit: int, show_objectives: bool) -> dict:
    # The v0 foundation queue stores `payload`, which is never printed by default.
    title_expr = 'title' if 'title' in _columns(db, 'tasks') else "'' AS title"
    tasks = [dict(r) for r in db.execute(f'''
        SELECT id,priority,module,state,created_id,{title_expr} FROM tasks ORDER BY created_id''')]
    statuses = Counter(x['state'] for x in tasks)
    for t in tasks:
        t['status'] = t.pop('state')
        t['priority'] = 'P' + str(t['priority'])
        t['module'] = _safe(t['module'], 30)
        title = t.pop('title', '')
        t['objective'] = (_safe(title, 150) or '(title not recorded)') if show_objectives else '(hidden)'
    events = [dict(r) for r in db.execute('''
        SELECT task_id,kind FROM events ORDER BY seq DESC LIMIT ?''', (event_limit,))]
    return {
        'engine': 'atlas', 'schema': 'ATLAS native Core seed',
        'architecture_approved': None, 'source_sha': '', 'integration_sha': '',
        'integration_branch': '', 'counts': dict(statuses), 'total': len(tasks),
        'active': [t for t in tasks if t['status'] in ACTIVE][:limit],
        'queued': [t for t in tasks if t['status'] == 'pending'][:limit],
        'review': [], 'merging': [],
        'blocked': [t for t in tasks if t['status'] in BLOCKED][:limit],
        'events': [{'task_id': _safe(e['task_id'], 64), 'stage': _safe(e['kind'], 32), 'step': 'event recorded', 'time': '—', 'result': ''} for e in events],
        'recent_runs': [],
    }


def snapshot(db_path: Path, *, source: str = 'auto', limit: int = 10,
             event_limit: int = 8, show_objectives: bool = False) -> dict:
    """Snapshot one transactionally consistent read-only view. Never creates DB."""
    if not (1 <= limit <= 100 and 0 <= event_limit <= 100):
        raise ValueError('invalid display limit')
    with closing(_connect(db_path)) as db:
        db.execute('BEGIN')
        detected = _detect(db)
        if source != 'auto' and source != detected:
            raise ValueError(f'schema mismatch: requested {source} but found {detected}')
        data = (_fetch_astra if detected == 'astra' else _fetch_atlas)(db, limit, event_limit, show_objectives)
        db.execute('ROLLBACK')
    home = Path(db_path).expanduser().absolute().parent
    data['controls'] = [s for s in ('STOP', 'PAUSE', 'PAUSED_QUOTA', 'PAUSE_NORMAL', 'PAUSE_RECOVERY')
                        if (home / s).is_file()]
    data['db'] = str(Path(db_path).expanduser().absolute())
    data['updated_at'] = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    return data


def _line(label: str, value: Any) -> str:
    return f'  {label:<16} {value}'


def _task_line(t: dict, *, active: bool = False) -> str:
    task_id = _safe(t.get('id', ''), 42)
    status = _safe(t.get('status', ''), 20)
    area = _safe(t.get('area', t.get('module','')), 18)
    slot = t.get('slot')
    run = f'W{slot}' if slot else ('unmapped' if active else '—')
    extra = ' | ' + _safe(t.get('step', ''), 58) if active and t.get('step') else ''
    title = _safe(t.get('objective', ''), 93)
    return f'  {task_id:<17.17} {status:<17.17} {area:<12.12} {run:<8.8} {title}{extra}'


def render(data: dict, *, ansi: bool = False, title: str = 'ATLAS Monitor') -> str:
    """Produce a stable human-readable report (never fabricates worker slots)."""
    counts = data['counts']
    count = lambda group: sum(counts.get(key, 0) for key in group)
    done, total = count(DONE), data['total']
    pct = (100 * done / total) if total else 0
    width = 26
    filled = min(width, round(width * done / total)) if total else 0
    bar = '█' * filled + '░' * (width - filled)
    state = ' / '.join(data['controls']) if data['controls'] else 'none'
    if data['engine'] == 'astra':
        approval = 'yes' if data['architecture_approved'] else 'no'
    else:
        approval = 'not tracked by native seed'
    heading = f'{title}  |  ARCHON AI · AEGIS Guardian · ATLAS Infrastructure'
    out = [heading, '═' * min(105, len(heading)),
           _line('Captured', data['updated_at']),
           _line('Source', data['schema']),
           _line('Controls', state),
           _line('Architecture', f'approved: {approval}'),
           _line('Progress', f'{bar} {done}/{total} observed completed ({pct:.1f}%)'),
           _line('Task states', f"queued {count({'queued','pending'})} · active {count(ACTIVE)} · review {count(WAITING_REVIEW)} · merge-ready {count(WAITING_MERGE)} · blocked {count(BLOCKED)}"),
           _line('Integration', _safe(data.get('integration_branch') or '—', 72)),
           _line('Commit', _safe(data.get('integration_sha', '')[:12] or '—', 30))]
    if data['engine'] == 'astra':
        out.extend(render_supervision(data.get('supervision', {})))
        out.extend(['', 'FIVE-WORKER SNAPSHOT (recorded slots; not a process-liveness check)'])
        by_slot = {str(x.get('slot')): x for x in data['active'] if x.get('slot')}
        for n in range(1,6):
            t = by_slot.get(str(n))
            if t:
                out.append(f"  W{n}  {_safe(t.get('id',''), 17):<17} {_safe(t.get('model',''), 24):<24} elapsed {_safe(t.get('elapsed',''), 12):<12} tools {t.get('tools',0)}")
            else:
                out.append(f'  W{n}  no active slot record (may be idle, blocked, or not yet reported)')
    out.extend(['', 'ACTIVE DEVELOPMENT / CODEX RUNS',
           '  TASK              STATUS            AREA         SLOT     WHAT IS BEING DEVELOPED'])
    if data['active']:
        out.extend(_task_line(t, active=True) for t in data['active'])
    else:
        out.append('  No active task recorded.')
    if data['engine'] == 'astra':
        out.append('  Slot mapping appears only when the runner emitted worker_N events; no fabricated slot assignment.')
    for label, key in [('REVIEW QUEUE', 'review'), ('MERGE-READY QUEUE', 'merging'), ('UP NEXT', 'queued'), ('BLOCKERS / FAILURES', 'blocked')]:
        out.extend(['',label])
        values = data[key]
        if values:
            for task in values:
                out.append(_task_line(task))
                if key == 'blocked' and task.get('last_error'):
                    out.append('    Reason: ' + _safe(task['last_error'], 120))
        else:
            out.append('  None recorded.')
    if data['recent_runs']:
        out.extend(['', 'RECENT CODEX RUNS'])
        for run in data['recent_runs'][:5]:
            out.append('  ' + _safe(run.get('task_id',''), 22) + ' | ' + _safe(run.get('role',''),12) + ' | ' + _safe(run.get('status',''),15) + ' | ' + _safe(run.get('model',''), 26))
    out.extend(['', 'LATEST EVENTS'])
    for e in data['events']:
        out.append('  ' + _safe(e.get('time',''), 30) + ' | ' + _safe(e.get('task_id',''), 25) + ' | ' + _safe(e.get('stage',''), 18) + ' / ' + _safe(e.get('step',''), 48))
    if not data['events']:
        out.append('  No events recorded.')
    out.extend(['', 'Read-only recorded state (not confirmed process liveness) · No model calls, Git actions, or runner control'])
    text = '\n'.join(out)
    if ansi:
        # Only add known, constant ANSI codes; never render arbitrary control sequences from data.
        text = '\033[1;36m' + text.split('\n',1)[0] + '\033[0m\n' + text.split('\n',1)[1]
    return text


def _choose_db(source: str, given: Path | None) -> Path:
    if given is not None:
        return given
    if source == 'astra':
        for candidate in (ASTRA_DEFAULT, ASTRA_LEGACY):
            if candidate.exists():
                return candidate
        return ASTRA_DEFAULT
    if source == 'atlas':
        return ATLAS_DEFAULT
    for candidate in (ATLAS_DEFAULT, ARCHON_DEFAULT, ASTRA_DEFAULT, ASTRA_LEGACY):
        if candidate.exists():
            return candidate
    return ATLAS_DEFAULT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='ATLAS read-only terminal progress monitor (separate from SDA runner)')
    parser.add_argument('--source', choices=['auto','astra','atlas'], default='auto')
    parser.add_argument('--db', type=Path, help='Existing SQLite database. Opens mode=ro; never created.')
    parser.add_argument('--watch', action='store_true', help='Refresh continuously until Ctrl+C')
    parser.add_argument('--interval', type=float, default=3.0, help='Refresh cadence in seconds (>= 0.5)')
    parser.add_argument('--limit', type=int, default=10, help='Max tasks per section (1..100)')
    parser.add_argument('--events', type=int, default=8, help='Recent events (0..100)')
    parser.add_argument('--json', action='store_true', help='Print one JSON snapshot and exit')
    parser.add_argument('--show-objectives', action='store_true', help='Explicitly show bounded task summaries')
    parser.add_argument('--no-objectives', action='store_true', help='Hide private task descriptions')
    parser.add_argument('--no-color', action='store_true', help='Disable ANSI headings')
    args = parser.parse_args(argv)
    if not (0.5 <= args.interval <= 3600) or not (1 <= args.limit <= 100) or not (0 <= args.events <= 100):
        parser.error('interval/limit/events outside supported bounds')
    if args.json and args.watch:
        parser.error('--json is single-snapshot only; omit --watch')
    path = _choose_db(args.source, args.db)
    while True:
        try:
            data = snapshot(path, source=args.source, limit=args.limit, event_limit=args.events,
                            show_objectives=args.show_objectives and not args.no_objectives)
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                if args.watch and sys.stdout.isatty():
                    sys.stdout.write('\033[2J\033[H')
                print(render(data, ansi=bool(sys.stdout.isatty() and not args.no_color)), flush=True)
        except (OSError, sqlite3.Error, ValueError) as ex:
            print('ATLAS Monitor: ' + _safe(ex, 300), file=sys.stderr)
            return 2
        if not args.watch:
            return 0
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print('\nATLAS monitor stopped (runner unaffected).')
            return 0


if __name__ == '__main__':
    raise SystemExit(main())
