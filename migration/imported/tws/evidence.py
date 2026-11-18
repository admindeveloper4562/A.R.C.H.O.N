"""Evidence records and review-gated trial progression.

User notes are never automatically treated as verified proof.
"""
from __future__ import annotations
import json
from . import progression

def migrate(db):
    progression.migrate(db)
    with db:
        db.execute("""CREATE TABLE IF NOT EXISTS tws_evidence(
            id TEXT PRIMARY KEY, trial_id TEXT NOT NULL,
            note TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending'
            CHECK(status IN ('pending','approved','rejected')),
            reviewed_at TEXT
        )""")

def submit(db, evidence_id: str, trial_id: str, note: str):
    if not all((evidence_id,trial_id,note.strip())):
        raise ValueError("Evidence ID, trial and note required")
    migrate(db)
    with db:
        existing=db.execute("SELECT trial_id,note FROM tws_evidence WHERE id=?",(evidence_id,)).fetchone()
        if existing:
            if existing != (trial_id,note):
                raise ValueError("Evidence ID collision")
            return
        db.execute("INSERT INTO tws_evidence(id,trial_id,note) VALUES (?,?,?)",(evidence_id,trial_id,note))

def review(db, evidence_id: str, approved: bool, reviewer: str):
    if not reviewer.strip():
        raise ValueError("Reviewer required")
    with db:
        result=db.execute("""UPDATE tws_evidence SET status=?,reviewed_at=CURRENT_TIMESTAMP
             WHERE id=? AND status='pending'""",("approved" if approved else "rejected",evidence_id))
        if result.rowcount != 1:
            raise ValueError("Evidence not pending or missing")

def verified_count(db, trial_id: str) -> int:
    return db.execute("SELECT COUNT(*) FROM tws_evidence WHERE trial_id=? AND status='approved'",(trial_id,)).fetchone()[0]

def advance(db, event_id: str, trial):
    from .engine import status
    migrate(db)
    # Always derive level and approved evidence from storage, never caller arguments.
    return progression.record_trial(db,event_id,trial,status(db)["level"],verified_count(db,trial.id))
