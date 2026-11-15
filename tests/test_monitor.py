"""ATLAS terminal viewer is separate from the runner and opens databases read-only."""
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from jarvis_v2.core.queue import TaskQueue
from jarvis_v2.monitor import snapshot, render, main

ASTRA_SCHEMA = '''
CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE tasks(
  id TEXT PRIMARY KEY, spec TEXT NOT NULL, status TEXT NOT NULL, architecture_sha TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0, available_at INTEGER NOT NULL DEFAULT 0,
  last_run TEXT,last_error TEXT NOT NULL DEFAULT '',candidate_sha TEXT NOT NULL DEFAULT '',
  branch TEXT NOT NULL DEFAULT '',worktree TEXT NOT NULL DEFAULT '',base_sha TEXT NOT NULL DEFAULT '',
  changed_files TEXT NOT NULL DEFAULT '[]',qc_evidence TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE runs(
  id TEXT PRIMARY KEY,task_id TEXT NOT NULL REFERENCES tasks(id),
  attempt INTEGER NOT NULL,role TEXT NOT NULL,status TEXT NOT NULL,
  started_at TEXT NOT NULL,finished_at TEXT,model TEXT NOT NULL,
  tool_count INTEGER NOT NULL DEFAULT 0,error_code TEXT NOT NULL DEFAULT '');
CREATE TABLE events(
  event_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,task_id TEXT NOT NULL,
  seq INTEGER NOT NULL,time TEXT NOT NULL,stage TEXT NOT NULL,step TEXT NOT NULL,
  branch TEXT NOT NULL,base_sha TEXT NOT NULL,tool_count INTEGER NOT NULL,
  result TEXT NOT NULL,elapsed_s INTEGER NOT NULL,attempt INTEGER NOT NULL,
  synced INTEGER NOT NULL DEFAULT 0, UNIQUE(run_id,seq));
'''

class MonitorTests(unittest.TestCase):
    def _astra(self, db_path):
        conn = sqlite3.connect(db_path)
        conn.executescript('PRAGMA journal_mode=WAL;' + ASTRA_SCHEMA)
        conn.executemany('INSERT INTO settings VALUES (?,?)', [
            ('architecture_sha','abcd'),('approved_architecture_sha','abcd'),
            ('integration_sha','deadbeef12345678'),('integration_branch','feat/sda/SDA-001-test'),
            ('source_sha','ffeeaa')])
        cases = [
            ('SDA-014','coding','Build independent Codex worker', 'backend'),
            ('SDA-015','queued','Build QC runner', 'sda'),
            ('SDA-016','awaiting_review','Review the tests', 'sda'),
            ('SDA-017','approved','Merge tested candidate', 'sda'),
            ('SDA-018','completed','Shipped safe code', 'core'),
            ('SDA-019','conflict','Resolve integration bug', 'sda'),
        ]
        for n,(tid,status,title,area) in enumerate(cases):
            spec=json.dumps({'task_id':tid,'objective':title,'area':area,'acceptance':['secret spec must stay hidden']})
            conn.execute('INSERT INTO tasks (id,spec,status,architecture_sha,attempt,last_run,created_at,updated_at,branch,last_error) VALUES (?,?,?,?,?,?,?,?,?,?)',
                         (tid,spec,status,'abcd',1,'run1' if n==0 else None,f'2026-11-13T00:00:{n:02d}+00:00',f'2026-11-13T00:00:{n:02d}+00:00', 'feat/sda/SDA-014-worker' if n==0 else '', 'merge failed' if status=='conflict' else ''))
        conn.execute('INSERT INTO runs (id,task_id,attempt,role,status,started_at,model,tool_count) VALUES (?,?,?,?,?,?,?,?)',
                     ('run1','SDA-014',1,'worker','coding','2026-11-13T00:00:00+00:00','gpt-5.6-luna',6))
        conn.execute('INSERT INTO events (event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                     ('evt1','run1','SDA-014',1,'2026-11-13T00:00:01+00:00','coding','worker_3_codex_start','feat/sda/SDA-014-worker','abc',0,'',1,1))
        conn.commit()
        return conn

    def test_missing_database_never_created(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'no.db'
            with self.assertRaisesRegex(ValueError, 'no existing'):
                snapshot(p)
            self.assertFalse(p.exists())

    def test_astra_status_worker_slot_progress_and_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'sda.sqlite3'
            writer=self._astra(p)
            try:
                (p.parent/'PAUSE').touch()
                snap=snapshot(p,source='astra',show_objectives=True)
                self.assertEqual(snap['total'],6)
                self.assertEqual(snap['counts']['coding'],1)
                self.assertTrue(snap['architecture_approved'])
                self.assertEqual(snap['active'][0]['slot'],'3')
                self.assertEqual(snap['active'][0]['model'],'gpt-5.6-luna')
                self.assertEqual(snap['active'][0]['objective'],'Build independent Codex worker')
                self.assertEqual(snap['controls'],['PAUSE'])
                txt=render(snap)
                self.assertIn('ARCHON AI',txt)
                self.assertIn('AEGIS Guardian',txt)
                self.assertIn('ATLAS Infrastructure',txt)
                self.assertIn('completed (16.7%)',txt)
                self.assertIn('Merge tested candidate',txt)
                self.assertIn('W3',txt)
                self.assertNotIn('secret spec',txt)
                self.assertEqual(snap['merging'][0]['id'],'SDA-017')
            finally:writer.close()

    def test_old_run_events_do_not_fabricate_current_worker_slot(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'sda.sqlite3'
            writer=self._astra(p)
            try:
                writer.execute("UPDATE tasks SET last_run='newrun', status='preflight' WHERE id='SDA-014'")
                writer.execute('INSERT INTO runs (id,task_id,attempt,role,status,started_at,model) VALUES (?,?,?,?,?,?,?)',
                               ('newrun','SDA-014',2,'repairer','preflight','2026-11-13T00:00:10+00:00','gpt-5.6-luna'))
                writer.commit()
                task=snapshot(p)['active'][0]
                self.assertIsNone(task['slot'])
                self.assertEqual(task['step'],'')
                self.assertEqual(task['role'],'repairer')
            finally:writer.close()

    def test_no_raw_spec_in_json_and_no_objectives(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'sda.sqlite3'
            writer=self._astra(p)
            try:
                snap=snapshot(p, show_objectives=False)
                raw=json.dumps(snap)
                self.assertNotIn('secret spec must stay hidden', raw)
                self.assertNotIn('Build independent Codex worker', raw)
                self.assertIn('(hidden)',raw)
                self.assertNotIn('spec',snap['active'][0])
            finally:writer.close()

    def test_wal_updates_seen_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'sda.sqlite3'
            writer=self._astra(p)
            try:
                before=writer.execute('SELECT COUNT(*) FROM events').fetchone()[0]
                snapshot(p)
                self.assertEqual(writer.execute('SELECT COUNT(*) FROM events').fetchone()[0],before)
                writer.execute('INSERT INTO events (event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             ('evt2','run1','SDA-014',2,'2026-11-13T00:00:02+00:00','verifying','docker_no_network_tests','','abc',6,'',2,1))
                writer.commit()
                self.assertEqual(snapshot(p)['active'][0]['step'],'docker_no_network_tests')
            finally:writer.close()

    def test_native_atlas_queue_and_auto_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'atlas.sqlite3'
            q=TaskQueue(p)
            q.add(task_id='CORE-004',priority='P2',module='core',payload={'secret':'hidden-data'},title='Build durable task sessions')
            q.add(task_id='BACK-009',priority='P1',module='backend',payload={'secret':'hidden-data'},title='Implement context compression')
            leased=q.lease_next()
            self.assertEqual(leased['id'],'BACK-009')
            snap=snapshot(p,source='auto',show_objectives=True)
            self.assertEqual(snap['engine'],'atlas')
            self.assertEqual(snap['total'],2)
            self.assertEqual(len(snap['queued']),1)
            self.assertEqual(snap['active'][0]['objective'],'Implement context compression')
            self.assertEqual(snap['queued'][0]['objective'],'Build durable task sessions')
            self.assertEqual(len(snap['active']),1)
            self.assertNotIn('hidden-data', json.dumps(snap))
            with self.assertRaisesRegex(ValueError,'schema mismatch'):
                snapshot(p,source='astra')
            q.close()

    def test_unrecognized_db_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'other.db'
            with sqlite3.connect(p) as db: db.execute('CREATE TABLE unrelated(x INTEGER)')
            with self.assertRaisesRegex(ValueError,'unrecognized task schema'):
                snapshot(p)

    def test_cli_one_snapshot_prints_json_and_is_not_runner(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'atlas.sqlite3'
            q=TaskQueue(p);q.add(task_id='CORE-004',priority='P2',module='core',payload={'secret':'hidden'});q.close()
            out=io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(['--db',str(p),'--json','--no-objectives']),0)
            self.assertEqual(json.loads(out.getvalue())['total'],1)
            cmd=[sys.executable,str(Path(__file__).resolve().parents[1]/'tools'/'atlas_monitor.py'),'--db',str(p),'--json']
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['engine'],'atlas')

    def test_terminal_escape_sanitized(self):
        from jarvis_v2.monitor import _safe
        value=_safe('Bad\x1b[2J task\n password=123xyz')
        self.assertNotIn('\x1b',value)
        self.assertNotIn('123xyz',value)
        self.assertIn('<redacted>',value)

    def test_cli_rejects_simultaneous_watch_and_json(self):
        with self.assertRaises(SystemExit):
            main(['--watch','--json'])

if __name__=='__main__':unittest.main()
