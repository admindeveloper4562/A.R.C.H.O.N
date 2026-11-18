"""Deterministic progression, persistence and quest processing."""
from __future__ import annotations
import json
import math
import sqlite3
from urllib.parse import quote
from pathlib import Path

FIRST_QUEST = "quest_first_covenant"

def xp_to_next_level(level: int) -> int:
    if level < 1:
        raise ValueError("level must be >= 1")
    return math.ceil(100 * level ** 1.5)

def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY CHECK(id=1), level INTEGER NOT NULL,
            xp INTEGER NOT NULL, total_xp INTEGER NOT NULL,
            spiritual INTEGER NOT NULL, power INTEGER NOT NULL,
            constitution INTEGER NOT NULL, speed INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS companion (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, wings INTEGER NOT NULL,
            bond INTEGER NOT NULL, trust INTEGER NOT NULL,
            fragments INTEGER NOT NULL, story_chapter INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quests (
            id TEXT PRIMARY KEY, status TEXT NOT NULL,
            evidence TEXT
        );
        CREATE TABLE IF NOT EXISTS reward_ledger (
            quest_id TEXT PRIMARY KEY, xp INTEGER NOT NULL,
            ruleset TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS narrative_events (
            id TEXT PRIMARY KEY, text TEXT NOT NULL, seen INTEGER NOT NULL DEFAULT 0
        );
    """)
    db.commit()
    return db

def connect_readonly(path: str | Path) -> sqlite3.Connection:
    """Open an existing database without ever creating or modifying files."""
    resolved=Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError("Database not initialized")
    encoded=quote(str(resolved),safe="/")
    db=sqlite3.connect(f"file:{encoded}?mode=ro",uri=True)
    db.execute("PRAGMA query_only=ON")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def initialize(db: sqlite3.Connection) -> None:
    with db:
        db.execute("INSERT OR IGNORE INTO player VALUES (1,1,0,0,10,10,10,10)")
        db.execute("INSERT OR IGNORE INTO companion VALUES ('aurelia','Aurelia',2,0,0,0,0)")
        db.execute("INSERT OR IGNORE INTO quests (id,status) VALUES (?,?)", (FIRST_QUEST,"available"))
        db.execute("INSERT OR IGNORE INTO narrative_events(id,text) VALUES (?,?)", (
            "prologue", "Aurelia: The Astral Archive is broken. Can you hear me?"))
        
def status(db: sqlite3.Connection) -> dict:
    row = db.execute("SELECT level,xp,total_xp,spiritual,power,constitution,speed FROM player WHERE id=1").fetchone()
    if row is None:
        raise RuntimeError("Run tws init first")
    return dict(zip(("level","xp","total_xp","spiritual","power","constitution","speed"),row))

def companion(db: sqlite3.Connection) -> dict:
    row = db.execute("SELECT name,wings,bond,trust,fragments,story_chapter FROM companion WHERE id='aurelia'").fetchone()
    if row is None:
        raise RuntimeError("Run tws init first")
    return dict(zip(("name","wings","bond","trust","fragments","story_chapter"),row))

def quests(db: sqlite3.Connection) -> list[dict]:
    return [{"id":a,"status":b,"evidence":c} for a,b,c in db.execute("SELECT id,status,evidence FROM quests")]

def accept(db: sqlite3.Connection, quest_id: str) -> None:
    with db:
        row = db.execute("UPDATE quests SET status='accepted' WHERE id=? AND status='available'",(quest_id,))
        if row.rowcount != 1:
            raise ValueError("Quest unavailable or already accepted")

def submit(db: sqlite3.Connection, quest_id: str, note: str) -> None:
    if not note.strip():
        raise ValueError("Evidence note required")
    with db:
        row = db.execute("UPDATE quests SET status='submitted',evidence=? WHERE id=? AND status='accepted'",(note,quest_id))
        if row.rowcount != 1:
            raise ValueError("Accept the quest before submitting evidence")

def complete(db: sqlite3.Connection, quest_id: str) -> dict:
    if quest_id != FIRST_QUEST:
        raise ValueError("Unknown quest")
    with db:
        row = db.execute("SELECT status,evidence FROM quests WHERE id=?",(quest_id,)).fetchone()
        if not row or row[0] != "submitted" or not row[1]:
            raise ValueError("Quest must have submitted evidence")
        db.execute("INSERT INTO reward_ledger(quest_id,xp,ruleset) VALUES (?,50,'0.001.000')",(quest_id,))
        level,xp,total = db.execute("SELECT level,xp,total_xp FROM player WHERE id=1").fetchone()
        xp += 50
        while xp >= xp_to_next_level(level):
            xp -= xp_to_next_level(level)
            level += 1
        db.execute("UPDATE player SET level=?,xp=?,total_xp=?,spiritual=spiritual+1 WHERE id=1",(level,xp,total+50))
        db.execute("UPDATE companion SET bond=bond+5,fragments=fragments+1,story_chapter=1 WHERE id='aurelia'")
        db.execute("UPDATE quests SET status='completed' WHERE id=?",(quest_id,))
        db.execute("INSERT OR IGNORE INTO narrative_events(id,text) VALUES (?,?)",(
            "chapter_one","Aurelia: A memory fragment has returned. Our Covenant is growing stronger."))
    return status(db)

def next_story(db: sqlite3.Connection) -> str | None:
    with db:
        row = db.execute("SELECT id,text FROM narrative_events WHERE seen=0 ORDER BY rowid LIMIT 1").fetchone()
        if not row:
            return None
        db.execute("UPDATE narrative_events SET seen=1 WHERE id=?",(row[0],))
        return row[1]
