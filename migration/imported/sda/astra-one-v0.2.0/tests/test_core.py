"""Cross-platform deterministic Astra One tests; never calls a live model/cloud."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid

from astra_one.core import Store, validate_source,validate_task,SCHEMA
from astra_one.runner import event_payload,build_prompt,changes_and_qc,Progress,create_worktree
from astra_one.planner import focused_architecture,validate_plan


def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True).stdout.strip()


class AstraTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.source=self.base/'repository'
        self.source.mkdir()
        git(self.source,'init','-q')
        git(self.source,'config','user.name','Astra Unit Test')
        git(self.source,'config','user.email','astra-test@example.invalid')
        (self.source/'README.md').write_text('baseline\n',encoding='utf8')
        git(self.source,'add','README.md')
        git(self.source,'commit','-qm','first')
        git(self.source,'switch','-qc','feature/lab')
        self.store=Store(self.base/'state')

    def init(self):
        return self.store.init(self.source)

    def architecture(self):
        self.init()
        doc=self.base/'architecture.md'
        doc.write_text('Project JARVIS final architect requirements approved by user\n',encoding='utf8')
        sha=self.store.import_architecture(doc)['sha256']
        self.store.approve_architecture(sha)
        return sha

    def task(self, task_id='ASTRA-101',depends_on=None):
        return {'task_id':task_id,'objective':'Build a safe standalone Python validation module','acceptance':['Python syntax is valid','Tests demonstrate safe behavior'], 'depends_on': depends_on or []}

    def test_init_starts_engine_stopped(self):
        result=self.init()
        self.assertEqual(result['engine'],'stopped')
        self.assertFalse(self.store.config('approved_architecture_sha'))

    def test_refuse_reinitializing_state(self):
        self.init()
        with self.assertRaisesRegex(ValueError,'already initialized'):
            self.init()

    def test_refuse_dirty_source(self):
        (self.source/'new.txt').write_text('untracked')
        with self.assertRaisesRegex(ValueError,'dirty'):
            validate_source(self.source)

    def test_architecture_requires_approval(self):
        self.init()
        doc=self.base/'spec.md';doc.write_text('The full future design is to be approved.',encoding='utf8')
        self.store.import_architecture(doc)
        with self.assertRaisesRegex(ValueError,'approve'):
            self.store.add_task(self.task())

    def test_wrong_architecture_sha_denied(self):
        self.init()
        doc=self.base/'spec.md';doc.write_text('The full future design is to be approved.',encoding='utf8')
        self.store.import_architecture(doc)
        with self.assertRaisesRegex(ValueError,'sha mismatch'):
            self.store.approve_architecture('00'*32)

    def test_approved_architecture_is_still_not_started(self):
        self.architecture()
        self.assertIsNone(self.store.claim())
        self.assertEqual(self.store.overview()['engine'],'manual_start_only')

    def test_task_rejects_unexpected_secret_field(self):
        item=self.task();item['secrets']={'token':'secret'}
        with self.assertRaisesRegex(ValueError,'only'):
            validate_task(item)

    def test_task_requires_acceptance(self):
        item=self.task();item['acceptance']=[]
        with self.assertRaisesRegex(ValueError,'acceptance'):
            validate_task(item)

    def test_enqueue_claim_once(self):
        self.architecture()
        self.store.add_task(self.task())
        claimed=self.store.claim()
        self.assertEqual(claimed['task']['task_id'],'ASTRA-101')
        self.assertEqual(claimed['attempt'],1)
        self.assertIsNone(self.store.claim())

    def test_dependencies_block_claim(self):
        self.architecture()
        self.store.add_task(self.task('ASTRA-101'))
        self.store.add_task(self.task('ASTRA-102',['ASTRA-101']))
        self.assertEqual(self.store.claim()['task']['task_id'],'ASTRA-101')
        self.assertIsNone(self.store.claim())

    def test_dependencies_reject_unknown(self):
        self.architecture()
        with self.assertRaisesRegex(ValueError,'unknown dependency'):
            self.store.add_task(self.task('ASTRA-102',['ASTRA-999']))

    def test_pause_prevents_claim(self):
        self.architecture();self.store.add_task(self.task())
        (self.store.home/'PAUSE').touch()
        self.assertIsNone(self.store.claim())

    def test_stop_prevents_claim(self):
        self.architecture();self.store.add_task(self.task())
        (self.store.home/'STOP').touch()
        self.assertIsNone(self.store.claim())

    def test_architecture_replacement_pauses(self):
        self.architecture()
        replacement=self.base/'new.md';replacement.write_text('New final architecture, needs another approval',encoding='utf8')
        self.store.import_architecture(replacement)
        self.assertFalse(self.store.config('approved_architecture_sha'))

    def test_recover_marks_interrupted(self):
        self.architecture();self.store.add_task(self.task());self.store.claim()
        self.assertEqual(self.store.recover(),['ASTRA-101'])
        self.assertEqual(self.store.tasks()[0]['status'],'interrupted')
        self.assertEqual(self.store.recover(),[])

    def test_retry_requires_explicit_failed_state(self):
        self.architecture();self.store.add_task(self.task())
        with self.assertRaisesRegex(ValueError,'only failed'):
            self.store.retry('ASTRA-101')
        self.store.claim();self.store.recover();self.store.retry('ASTRA-101')
        self.assertEqual(self.store.tasks()[0]['status'],'queued')

    def test_event_metadata_has_no_private_content(self):
        e=event_payload(run_id=str(uuid.uuid4()),task_id='ASTRA-101',seq=1,stage='coding',step='codex_started',branch='feature/astra-test',base_sha='f'*40,elapsed_s=22)
        self.assertEqual(e['elapsed_s'],22)
        self.assertEqual(set(e),{'event_id','run_id','task_id','seq','time','stage','step','branch','base_sha','tool_count','result','elapsed_s','attempt'})
        self.assertNotIn('prompt',e)
        self.assertNotIn('code',e)

    def test_events_persist_and_sync(self):
        self.init()
        e=event_payload(run_id=str(uuid.uuid4()),task_id='ASTRA-101',seq=1,stage='coding',step='codex_started',branch='feature/astra-test',base_sha='f'*40)
        self.store.event(e)
        self.assertEqual(len(self.store.unsynced()),1)
        self.store.event(e)
        self.assertEqual(len(self.store.unsynced()),1)
        self.store.synced(e['event_id'])
        self.assertEqual(len(self.store.unsynced()),0)

    def test_progress_no_monitor_configuration(self):
        self.init()
        p=Progress(self.store)
        if not p.url:
            self.assertEqual(p.flush()['sent'],0)

    def test_prompt_does_not_include_private_architecture(self):
        t=self.task();t['area']='foundation'
        prompt=build_prompt(t,'a'*40,'b'*64)
        self.assertIn(t['objective'],prompt)
        self.assertIn('human separately reviews',prompt)
        self.assertNotIn('PRIVATE_ARCHITECTURE_CONTENT',prompt)

    def test_qc_rejects_no_changes(self):
        passed,reason=changes_and_qc(self.source)
        self.assertFalse(passed)
        self.assertEqual(reason,'no_changes')

    def test_qc_rejects_deletion(self):
        (self.source/'README.md').unlink()
        passed,reason=changes_and_qc(self.source)
        self.assertFalse(passed)
        self.assertIn('deletion',reason)

    def test_qc_rejects_python_syntax(self):
        (self.source/'bad.py').write_text('def bad(\n',encoding='utf8')
        passed,reason=changes_and_qc(self.source)
        self.assertFalse(passed)
        self.assertEqual(reason,'python_syntax_failed')

    def test_qc_passes_python_syntax(self):
        (self.source/'safe.py').write_text('def safe():\n    return True\n',encoding='utf8')
        passed,reason=changes_and_qc(self.source)
        self.assertTrue(passed)
        self.assertIn('review',reason)

    def test_reviewed_candidate_integrates_only_to_local_feature(self):
        self.architecture()
        self.store.add_task(self.task())
        claim=self.store.claim()
        worktree,branch,sha=create_worktree(self.store,claim['task']['task_id'],claim['run_id'])
        self.store.start_run(claim['run_id'],'ASTRA-101',branch,sha,worktree,claim['attempt'])
        (worktree/'safe.py').write_text('def answer():\n    return 42\n',encoding='utf8')
        self.store.update_status('ASTRA-101',claim['run_id'],'awaiting_review',qc_result='passed')
        self.store.approve_task('ASTRA-101')
        result=self.store.integrate('ASTRA-101')
        self.assertEqual(result['status'],'completed')
        self.assertTrue((self.store.home/'integration'/'safe.py').is_file())
        self.assertFalse((self.source/'safe.py').exists())
        self.assertEqual(git(self.source,'branch','--show-current'),'feature/lab')
        self.assertEqual(self.store.tasks()[0]['status'],'completed')
        self.store.add_task(self.task('ASTRA-102',['ASTRA-101']))
        claim2=self.store.claim()
        next_worktree,_,base=create_worktree(self.store,'ASTRA-102',claim2['run_id'])
        self.assertEqual(base,result['integration_commit'])
        self.assertTrue((next_worktree/'safe.py').is_file())

    def test_integration_rejects_unapproved(self):
        self.architecture();self.store.add_task(self.task())
        with self.assertRaisesRegex(ValueError,'owner-approved'):
            self.store.integrate('ASTRA-101')

    def test_planner_focus_selects_one_heading_section(self):
        text='# Intro\nGeneral constraints\n## SDA\nBuild safe agent\n### Worker\nOne worker\n## Finance\nNever trade real funds\n'
        result=focused_architecture(text,'SDA')
        self.assertIn('One worker',result)
        self.assertNotIn('Never trade',result)

    def test_planner_large_architecture_requires_focus(self):
        with self.assertRaisesRegex(ValueError,'--focus'):
            focused_architecture('# Architecture\n'+'x'*19000)

    def test_planner_rejects_forward_dependency(self):
        a=self.task('ASTRA-101',['ASTRA-102']);b=self.task('ASTRA-102')
        with self.assertRaisesRegex(ValueError,'topologically'):
            validate_plan({'tasks':[a,b]})

    def test_atomic_plan_enqueue(self):
        self.architecture()
        a=self.task('ASTRA-101');b=self.task('ASTRA-102',['ASTRA-101'])
        self.store.add_plan({'tasks':[a,b]})
        self.assertEqual(len(self.store.tasks()),2)
        with self.assertRaises(ValueError):
            self.store.add_plan({'tasks':[self.task('ASTRA-103'),self.task('ASTRA-101')]})
        self.assertEqual(len(self.store.tasks()),2)

    def test_cloudflare_schema_valid_sqlite(self):
        sql=(Path(__file__).resolve().parents[1]/'cloudflare'/'astra-one-monitor'/'schema.sql').read_text()
        conn=sqlite3.connect(':memory:')
        conn.executescript(sql)
        self.assertIn('astra_events',[x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")])
        conn.close()

if __name__=='__main__':unittest.main()
