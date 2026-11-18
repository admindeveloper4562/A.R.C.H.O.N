from __future__ import annotations

import asyncio
import html
import json
import os
import re
import secrets
import string
import sqlite3
import time
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .inventory import (add_configured_root, cleanup_preview, configured_roots,
                         organization_preview,
                         duplicate_groups, mounted_volumes, refresh_status, scan, search, store,
                         verified_duplicate_groups, discover_projects)
from .inventory_scheduler import InventoryRefreshScheduler
from .permissions import ApprovalBroker, ApprovalError
from .storage import connect, ensure_schema
from .colibri import ColibriClient
from .tasks import TaskStore
from .worker import WorkerDispatcher, default_dispatcher
from .diagnostics import read_only_diagnostics, recent_error_history
from .calendar import proposal_event_ids, sample_calendar
from .email import SampleEmailProvider
from .voice import local_adapters

HOST = "127.0.0.1"
PORT = int(os.environ.get("JARVIS_PORT", "8765"))
DB_PATH = Path(os.environ.get("JARVIS_DB", Path.home() / ".local/share/jarvis/jarvis.db"))
BOOTSTRAP_TOKEN = os.environ.get("JARVIS_OWNER_TOKEN", "")
SESSION_TTL = 3600
MAX_BODY = 64 * 1024
MAX_REQUEST_LINE = 8 * 1024
MAX_HEADER_LINE = 8 * 1024
MAX_HEADERS = 64 * 1024
MAX_HEADER_COUNT = 100
REQUEST_READ_TIMEOUT = 5.0
HTTP_TOKEN_CHARS = frozenset(string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~")
ENCODED_TARGET_CONTROLS = frozenset(
    f"%{value:02x}" for value in (*range(0x00, 0x20), 0x7f)
)
OPAQUE_PATH_ID = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
ROUTES = ["/", "/calendar", "/email", "/actions", "/files", "/system", "/projects", "/voice", "/activity", "/settings"]


def _action_form(body: bytes, allowed: set[str], required: set[str]) -> dict[str, str]:
    """Parse one exact Actions form without silently dropping attacker fields."""
    try:
        fields = parse_qs(body.decode("utf-8", "strict"), keep_blank_values=True, strict_parsing=True)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("malformed form") from exc
    if set(fields) - allowed or any(len(values) != 1 for values in fields.values()):
        raise ValueError("unsupported or duplicate form field")
    missing = required - set(fields)
    if missing or any(not values[0] for key, values in fields.items() if key in required):
        raise ValueError("required form field missing")
    result = {key: values[0] for key, values in fields.items()}
    # Form decoding is a shared control-plane boundary.  Reject decoded
    # controls and disproportionate individual values before any route-specific
    # trimming, persistence, authentication decision, or capability dispatch.
    if any(len(value) > MAX_BODY or any(ord(char) < 32 or ord(char) == 127 for char in value)
           for value in result.values()):
        raise ValueError("form value is invalid")
    return result


def _csrf_form(body: bytes, fields: set[str] = frozenset()) -> dict[str, str]:
    """Parse an exact authenticated form; never collapse duplicate attacker input."""
    return _action_form(body, set(fields) | {"csrf"}, set(fields) | {"csrf"})


def _query(target: str, allowed: set[str]) -> dict[str, str]:
    """Parse control-plane query fields exactly; never select an attacker value."""
    if not isinstance(target, str) or not isinstance(allowed, set):
        raise ValueError("malformed query")
    if len(target) > MAX_REQUEST_LINE:
        raise ValueError("query too long")
    try:
        fields = parse_qs(urlsplit(target).query, keep_blank_values=True, strict_parsing=True)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("malformed query") from exc
    if set(fields) - allowed or any(len(values) != 1 for values in fields.values()):
        raise ValueError("unsupported or duplicate query field")
    result = {key: values[0] for key, values in fields.items()}
    if any(len(value) > 2048 or any(ord(char) < 32 or ord(char) == 127 for char in value)
           for value in result.values()):
        raise ValueError("query value is invalid")
    return result


def _opaque_path_id(value: str, label: str) -> str:
    """Validate a generated identifier before any route-specific lookup."""
    if not isinstance(value, str) or not OPAQUE_PATH_ID.fullmatch(value):
        raise ValueError(f"malformed {label}")
    return value


def init_db(path: Path | None = None) -> None:
    path = path or DB_PATH
    ensure_schema(path)


def chat_history(path: Path, limit: int = 40) -> list[dict]:
    """Return recent local chat messages in chronological order."""
    bounded = max(1, min(int(limit), 100))
    with connect(path) as db:
        rows = db.execute(
            "SELECT role, content, model, created FROM chat_messages "
            "ORDER BY id DESC LIMIT ?", (bounded,)
        ).fetchall()
    return [
        {"role": row[0], "content": row[1], "model": row[2], "created": row[3]}
        for row in reversed(rows)
    ]


def save_chat_turn(path: Path, message: str, answer: dict) -> None:
    """Persist one completed local turn; retain a bounded recent history."""
    with connect(path) as db:
        now = time.time()
        db.execute(
            "INSERT INTO chat_messages(role, content, model, created) VALUES (?, ?, ?, ?)",
            ("user", message, None, now),
        )
        db.execute(
            "INSERT INTO chat_messages(role, content, model, created) VALUES (?, ?, ?, ?)",
            ("assistant", answer["content"], answer.get("model"), now),
        )
        db.execute(
            "DELETE FROM chat_messages WHERE id NOT IN "
            "(SELECT id FROM chat_messages ORDER BY id DESC LIMIT 100)"
        )


def home_summary(app: "App") -> dict:
    """Build a truthful, read-only Home dashboard snapshot from local state."""
    tasks = app.tasks.list(limit=100)
    return {
        "colibri": probe_colibri(),
        "voice": {"state": "unavailable", "mode": "text_only", "reason": "local voice adapter is not configured"},
        "active_tasks": [app.task_json(task) for task in tasks if task.state not in {"done", "failed", "cancelled"}],
        "alerts": [{"kind": "task_failure", "message": task.error or f"{task.kind} failed", "task_id": task.task_id}
                   for task in tasks if task.state == "failed"][:20],
        "quick_actions": [
            {"label": "Find files", "href": "/files", "state": "available"},
            {"label": "Review actions", "href": "/actions", "state": "available"},
            {"label": "View activity", "href": "/activity", "state": "available"},
        ],
    }


def voice_summary() -> dict:
    """Describe the deliberately disconnected local voice boundary.

    Microphone permission is a browser-owned capability, so the server cannot
    claim it is granted.  The UI reports the actual browser permission state.
    """
    adapters = local_adapters()
    configured = adapters["configured"]
    return {
        "state": "available" if configured else "unavailable",
        "mode": "local" if configured else "text_only",
        "microphone": {"permission": "unknown", "capture": "push_to_talk"},
        "voices": [{"id": "configured-local", "label": "Configured local voice"}] if configured else [],
        "outputs": [],
        "message": ("Configured local speech adapter discovered; playback/capture is not enabled in this slice."
                    if configured else "Local speech adapters are not configured; text chat remains available."),
        "adapters": adapters,
        "writes": "disabled",
    }


def calendar_summary(app: "App" | None = None) -> dict:
    """Expose disconnected calendar state without fabricating events."""
    if app is not None and app.calendar_provider == "sample":
        return sample_calendar(app.calendar_timezone)
    return {
        "state": "disconnected",
        "provider": None,
        "timezone": time.tzname[0] if time.tzname else "unknown",
        "events": [],
        "message": "No calendar connector is configured; no events were loaded.",
        "writes": "disabled",
        "proposals": "disabled",
    }


def calendar_proposals(path: Path) -> list[dict]:
    with connect(path) as db:
        rows = db.execute(
            "SELECT proposal_id, event_id, operation, payload, state, created, decided "
            "FROM calendar_proposals ORDER BY created DESC"
        ).fetchall()
    return [{"proposal_id": r[0], "event_id": r[1], "operation": r[2],
             "payload": json.loads(r[3]), "state": r[4], "created": r[5], "decided": r[6]}
            for r in rows]


def email_drafts(path: Path | None = None) -> list[dict]:
    ensure_schema(path or DB_PATH)
    with connect(path or DB_PATH) as db:
        rows = db.execute("SELECT draft_id, recipient, subject, body, created FROM email_drafts ORDER BY created DESC").fetchall()
    return [{"draft_id": row[0], "to": row[1], "subject": row[2], "body": row[3],
             "created": row[4], "send": "disabled"} for row in rows]


def email_summary(path: Path | None = None) -> dict:
    """Expose the safe disconnected email contract without inventing mailbox data."""
    return {
        "state": "disconnected",
        "provider": None,
        "account": None,
        "messages": [],
        "query": "",
        "message": "No email connector is configured; no messages were loaded.",
        "drafts": email_drafts(path),
        "send": "disabled",
    }


def email_search(query: str = "") -> dict:
    """Return the connector-free search contract without inventing mailbox data."""
    if not isinstance(query, str) or len(query) > 500:
        raise ValueError("email search query must be a bounded string")
    if any(ord(char) < 32 or ord(char) == 127 for char in query):
        raise ValueError("email search query contains control characters")
    query = query.strip()
    return {"state": "disconnected", "provider": None, "query": query,
            "messages": [], "search": "disabled",
            "message": "Email OAuth is not configured; inbox search is unavailable."}


def email_draft_preview(fields: dict[str, str], path: Path | None = None) -> dict:
    """Persist a local-only draft preview; this never sends mail."""
    if not isinstance(fields, dict) or set(fields) != {"to", "subject", "body"}:
        raise ValueError("draft fields must contain only to, subject and body")
    if any(not isinstance(value, str) for value in fields.values()):
        raise ValueError("draft fields must be strings")
    recipient = fields.get("to", "").strip()
    subject = fields.get("subject", "").strip()
    body = fields.get("body", "")
    if any(ord(char) < 32 or ord(char) == 127 for value in fields.values() for char in value):
        raise ValueError("draft fields contain control characters")
    if (not recipient or not subject or not body.strip() or len(recipient) > 320
            or len(subject) > 200 or len(body) > 100_000):
        raise ValueError("to, subject and body are required and bounded")
    draft_id = secrets.token_urlsafe(18)
    ensure_schema(path or DB_PATH)
    with connect(path or DB_PATH) as db:
        db.execute("INSERT INTO email_drafts(draft_id, recipient, subject, body, created) VALUES (?, ?, ?, ?, ?)",
                   (draft_id, recipient, subject, body, time.time()))
    return {"state": "preview", "provider": None, "draft_id": draft_id, "to": recipient,
            "subject": subject, "body": body, "send": "disabled",
            "message": "Draft saved locally for preview only; email OAuth is not configured and nothing was sent."}


def probe_colibri() -> dict:
    # Deliberately use a subprocess-free socket probe. The supervisor owns lifecycle.
    return ColibriClient().status()


def page(route: str, csrf: str, csp_nonce: str = "static-test-nonce") -> bytes:
    title = route.strip("/").replace("/", " ").title() or "Home"
    # Python 3.11 does not permit backslash escapes inside f-string expressions.
    # Build the active-page attribute outside an f-string for cross-version support.
    nav = " ".join(
        '<a href="{}"{}>{}</a>'.format(
            r, ' aria-current="page"' if r == route else "", r.strip("/").title() or "Home"
        )
        for r in ROUTES
    )
    content = {
        "/": '''<h1>JARVIS</h1><p>Local-first assistant dashboard.</p><section aria-labelledby="status-heading"><h2 id="status-heading">Current status</h2><dl id="home-status"><dt>Model</dt><dd id="model-status">Loading…</dd><dt>Voice</dt><dd id="voice-status">Loading…</dd></dl><p id="colibri" role="status">Checking Colibri…</p></section><section aria-labelledby="alerts-heading"><h2 id="alerts-heading">Alerts</h2><div id="home-alerts" aria-live="polite"><p>Loading alerts…</p></div></section><section aria-labelledby="actions-heading"><h2 id="actions-heading">Quick actions</h2><div id="quick-actions"><p>Loading quick actions…</p></div></section><section aria-labelledby="tasks-heading"><h2 id="tasks-heading">Active tasks</h2><div id="active-tasks"><p>No active tasks reported.</p></div></section><section aria-labelledby="chat-heading"><h2 id="chat-heading">Local chat</h2><div id="chat-history" aria-live="polite"><p>Loading local history…</p></div><form id="chat-form"><label for="chat-message">Message</label><input id="chat-message" name="message" aria-label="Message" placeholder="Ask JARVIS" required><button type="submit">Send</button><button type="button" id="chat-cancel" hidden>Stop response</button></form><p id="chat-status" role="status"></p><p id="chat-live" aria-live="polite"></p></section><script>
const chatForm=document.querySelector('#chat-form'), chatStatus=document.querySelector('#chat-status'), chatHistory=document.querySelector('#chat-history');
function text(id,value){const node=document.querySelector(id);if(node)node.textContent=value}
function renderHome(data){text('#model-status',data.colibri.model||'No local model discovered');text('#voice-status',(data.voice.state||'unknown')+' — '+(data.voice.mode||'unknown'));text('#colibri','Colibri: '+data.colibri.state+(data.colibri.reason?' ('+data.colibri.reason+')':''));const alerts=document.querySelector('#home-alerts');alerts.replaceChildren();if(!data.alerts.length)alerts.append(document.createTextNode('No active alerts.'));for(const alert of data.alerts){const p=document.createElement('p');p.textContent=alert.message;alerts.append(p)}const actions=document.querySelector('#quick-actions');actions.replaceChildren();for(const action of data.quick_actions){const a=document.createElement('a');a.href=action.href;a.textContent=action.label+' ('+action.state+')';actions.append(a,document.createTextNode(' '))}const tasks=document.querySelector('#active-tasks');tasks.replaceChildren();if(!data.active_tasks.length)tasks.append(document.createTextNode('No active tasks reported.'));for(const task of data.active_tasks){const p=document.createElement('p');p.textContent=task.kind+': '+task.state;tasks.append(p)}}
async function loadHome(){try{const r=await fetch('/api/home');if(!r.ok)throw new Error('status '+r.status);renderHome(await r.json())}catch{ text('#model-status','Home status unavailable');text('#voice-status','Home status unavailable');text('#colibri','Home status unavailable');text('#home-alerts','Unable to load local alerts.');text('#quick-actions','Unable to load quick actions.');text('#active-tasks','Unable to load active tasks.')}}
function renderHistory(items){chatHistory.replaceChildren();if(!items.length){chatHistory.innerHTML='<p>No local chat history yet.</p>';return}for(const item of items){const p=document.createElement('p');p.textContent=(item.role==='user'?'You: ':'JARVIS: ')+item.content;chatHistory.append(p)}}
async function loadHistory(){const r=await fetch('/api/chat/history');if(r.ok)renderHistory((await r.json()).messages)}
const chatCancel=document.querySelector('#chat-cancel'),chatLive=document.querySelector('#chat-live');let chatController=null;
chatCancel.onclick=()=>{if(chatController)chatController.abort()};
chatForm.addEventListener('submit',async event=>{event.preventDefault();if(chatController)return;const message=chatForm.elements.message.value.trim();if(!message)return;const controller=new AbortController();chatController=controller;chatCancel.hidden=false;chatLive.textContent='';chatStatus.textContent='Asking local Colibri…';let completed=false;
try{const response=await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({message,csrf:document.querySelector('meta[name=csrf-token]').content}),signal:controller.signal});if(!response.ok||!response.body)throw new Error('Local chat unavailable ('+response.status+')');const reader=response.body.getReader(),decoder=new TextDecoder();let pending='';
while(true){const part=await reader.read();pending+=decoder.decode(part.value||new Uint8Array(),{stream:!part.done}).replaceAll('\\r\\n','\\n');let boundary;while((boundary=pending.indexOf('\\n\\n'))>=0){const frame=pending.slice(0,boundary);pending=pending.slice(boundary+2);const kind=frame.match(/^event: (.+)$/m),data=frame.match(/^data: (.+)$/m);if(!kind||!data)continue;const payload=JSON.parse(data[1]);if(kind[1]==='delta'){chatLive.textContent+=payload.content||''}else if(kind[1]==='error'){throw new Error(payload.error||'Local chat unavailable')}else if(kind[1]==='done'){completed=true;chatStatus.textContent='Answer received from '+(payload.model||'local model');chatForm.reset();await loadHistory();await loadHome();break}}if(completed||part.done)break}if(!completed)throw new Error('Response ended before completion')}
catch(error){chatStatus.textContent=controller.signal.aborted?'Response stopped.':String(error.message||error);chatLive.textContent=''}finally{chatController=null;chatCancel.hidden=true}});loadHistory();loadHome();
</script>''' ,
        "/calendar": '<h1>Calendar</h1><p id="calendar-state" role="status">Loading calendar connection…</p><p id="calendar-message"></p><form id="sample-calendar"><label>Timezone <input name="timezone" value="UTC" required></label><input type="hidden" name="provider" value="sample"><button>Connect owner-approved sample calendar</button></form><p>External OAuth and calendar writes are unavailable. Sample data is deterministic and clearly labelled. No calendar changes can be made here.</p><section aria-labelledby="events-heading"><h2 id="events-heading">Events</h2><div id="calendar-events">No events loaded.</div></section><section aria-labelledby="proposal-heading"><h2 id="proposal-heading">Propose a calendar change</h2><form id="calendar-proposal"><label>Event ID <input name="event_id" value="sample-1" required></label><label>Operation <select name="operation"><option>update</option><option>create</option><option>cancel</option></select></label><label>Title <input name="title" value="Proposed change"></label><button>Submit proposal</button></form><div id="calendar-proposals">No proposals.</div></section><script>const calendarForm=document.querySelector("#sample-calendar"),calendarToken=document.querySelector("meta[name=csrf-token]").content;async function loadCalendar(){const r=await fetch("/api/calendar");if(!r.ok)throw new Error("calendar unavailable");const x=await r.json();document.querySelector("#calendar-state").textContent="Calendar: "+x.state+" / "+x.provider;document.querySelector("#calendar-message").textContent=x.message;const box=document.querySelector("#calendar-events");box.replaceChildren();if(!x.events.length){box.textContent="No events loaded."}else for(const event of x.events){const p=document.createElement("p");p.textContent=event.title+" — "+event.start_local+" to "+event.end_local+(event.conflict_with?" (conflicts with "+event.conflict_with.join(", ")+")":"");box.append(p)}const pr=await fetch("/api/calendar/proposals");const px=await pr.json();document.querySelector("#calendar-proposals").textContent=px.proposals.length?px.proposals.map(p=>p.proposal_id+" — "+p.operation+" "+p.state+" (external write disabled)").join("; "):"No proposals."}calendarForm.onsubmit=async e=>{e.preventDefault();const r=await fetch("/api/calendar",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({...Object.fromEntries(new FormData(calendarForm)),csrf:calendarToken})});if(!r.ok){document.querySelector("#calendar-message").textContent="Connector request failed: "+await r.text();return}await loadCalendar()};document.querySelector("#calendar-proposal").onsubmit=async e=>{e.preventDefault();const r=await fetch("/api/calendar/proposals",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({...Object.fromEntries(new FormData(e.target)),csrf:calendarToken})});document.querySelector("#calendar-message").textContent=await r.text();if(r.ok){e.target.reset();await loadCalendar()}};loadCalendar().catch(()=>document.querySelector("#calendar-state").textContent="Calendar status unavailable")</script>',
        "/email": """<h1>Email</h1><p id="email-state" role="status">Loading email connection…</p><p id="email-message"></p><p>Email OAuth is not configured. Search, drafts and sending remain unavailable; no mailbox data is fabricated.</p><form id="email-search"><label for="email-query">Search inbox</label><input id="email-query" name="q" placeholder="Search unavailable until connected"><button disabled>Search</button></form><section aria-labelledby="inbox-heading"><h2 id="inbox-heading">Inbox</h2><div id="email-messages">No messages loaded.</div></section><section aria-labelledby="draft-heading"><h2 id="draft-heading">Draft preview</h2><p>Local preview is allowed; sending stays disabled until an owner-approved connector exists.</p><form id="email-draft"><label>To <input name="to" required></label><label>Subject <input name="subject" required></label><label>Body <textarea name="body" required></textarea></label><button>Preview draft</button></form><p id="draft-result" role="status"></p></section><script>const emailToken=document.querySelector('meta[name=csrf-token]').content;const emailSearchEndpoint='/api/email/search';const emailSendEndpoint='/api/email/send';fetch('/api/email').then(r=>r.json()).then(x=>{document.querySelector('#email-state').textContent='Email: '+x.state;document.querySelector('#email-message').textContent=x.message;document.querySelector('#email-messages').textContent=x.messages.length?'Messages available':'No messages loaded.'}).catch(()=>document.querySelector('#email-state').textContent='Email status unavailable');document.querySelector('#email-draft').onsubmit=async e=>{e.preventDefault();const r=await fetch('/api/email/draft',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({...Object.fromEntries(new FormData(e.target)),csrf:emailToken})});document.querySelector('#draft-result').textContent=await r.text()}</script>""",
        "/voice": '''<h1>Voice</h1><p id="voice-state" role="status">Loading voice status…</p><p id="mic-permission">Microphone permission: checking…</p><section aria-labelledby="ptt-heading"><h2 id="ptt-heading">Push to talk</h2><button id="push-to-talk" type="button" aria-pressed="false">Hold to talk</button> <button id="cancel-capture" type="button" disabled>Cancel capture</button><p id="mic-indicator" role="status">Microphone idle.</p><p>Audio capture starts only after this explicit button is pressed. Audio stays in this page and is not uploaded.</p></section><section aria-labelledby="voice-controls"><h2 id="voice-controls">Voice and audio output</h2><label for="voice-choice">Voice <select id="voice-choice" disabled><option>Text-only mode</option></select></label><label for="audio-output">Audio output <select id="audio-output" disabled><option>Browser default</option></select></label><p id="voice-message"></p></section><script>
const state=document.querySelector('#voice-state'),permission=document.querySelector('#mic-permission'),indicator=document.querySelector('#mic-indicator'),button=document.querySelector('#push-to-talk'),output=document.querySelector('#audio-output');
const cancelButton=document.querySelector('#cancel-capture');
async function loadVoice(){try{const response=await fetch('/api/voice');if(!response.ok)throw new Error();const data=await response.json();state.textContent='Voice: '+data.state+' / '+data.mode;document.querySelector('#voice-message').textContent=data.message;permission.textContent='Microphone permission: '+data.microphone.permission;}catch{state.textContent='Voice status unavailable';permission.textContent='Microphone permission: unavailable';}}
async function browserPermission(){if(!navigator.permissions)return;try{const status=await navigator.permissions.query({name:'microphone'});permission.textContent='Microphone permission: '+status.state;status.onchange=()=>permission.textContent='Microphone permission: '+status.state;}catch{permission.textContent='Microphone permission: not reported by this browser';}}
async function discoverOutputs(){if(!navigator.mediaDevices?.enumerateDevices){output.options[0].textContent='Browser default (device discovery unavailable)';return;}try{const devices=await navigator.mediaDevices.enumerateDevices();const outputs=devices.filter(device=>device.kind==='audiooutput');output.replaceChildren(new Option('Browser default','default'));for(const device of outputs){const label=device.label||('Audio output '+(output.options.length));output.add(new Option(label,device.deviceId));}output.disabled=false;output.title=outputs.length?'Output selection applies when a local player is connected.':'No named output devices reported; browser default remains available.';}catch{output.options[0].textContent='Browser default (device discovery unavailable)';}}
let stream=null;
let captureGeneration=0;
async function stopCapture(){captureGeneration++;const active=stream;stream=null;if(active){for(const track of active.getTracks())track.stop();}button.releasePointerCapture?.(button.dataset.pointerId);delete button.dataset.pointerId;button.setAttribute('aria-pressed','false');cancelButton.disabled=true;indicator.textContent='Microphone idle.';}
async function startCapture(event){if(stream)return;const generation=++captureGeneration;try{if(!navigator.mediaDevices?.getUserMedia)throw new Error('browser microphone API unavailable');if(event?.pointerId!==undefined){button.dataset.pointerId=String(event.pointerId);button.setPointerCapture?.(event.pointerId);}const pending=await navigator.mediaDevices.getUserMedia({audio:true});if(generation!==captureGeneration){for(const track of pending.getTracks())track.stop();return;}stream=pending;button.setAttribute('aria-pressed','true');cancelButton.disabled=false;indicator.textContent='Microphone active — release to stop. No audio is uploaded.';permission.textContent='Microphone permission: granted';}catch(error){if(generation!==captureGeneration)return;await stopCapture();indicator.textContent='Microphone unavailable; voice remains text-only.';permission.textContent='Microphone permission: denied or unavailable';}}
button.addEventListener('pointerdown',event=>{event.preventDefault();startCapture(event)});button.addEventListener('pointerup',stopCapture);button.addEventListener('pointercancel',stopCapture);button.addEventListener('lostpointercapture',stopCapture);button.addEventListener('pointerleave',event=>{if(event.buttons)stopCapture()});button.addEventListener('keydown',event=>{if((event.key===' '||event.key==='Enter')&&!event.repeat){event.preventDefault();startCapture()}});button.addEventListener('keyup',event=>{if(event.key===' '||event.key==='Enter'){event.preventDefault();stopCapture()}});cancelButton.addEventListener('click',stopCapture);window.addEventListener('blur',stopCapture);document.addEventListener('visibilitychange',()=>{if(document.hidden)stopCapture()});document.addEventListener('keydown',event=>{if(event.key==='Escape')stopCapture()});navigator.mediaDevices?.addEventListener?.('devicechange',discoverOutputs);loadVoice();browserPermission();discoverOutputs();
</script>''',
        "/system": '<h1>System</h1><p>Read-only health observations. Repairs are not enabled.</p><pre id="status"></pre><h2>Recent errors</h2><p id="errors">Loading error history…</p><pre id="diagnostics">Loading diagnostics…</pre><script>fetch("/api/diagnostics").then(r=>r.json()).then(x=>{document.querySelector("#diagnostics").textContent=JSON.stringify(x,null,2);const errors=document.querySelector("#errors");errors.textContent=x.error_history.length?x.error_history.map(e=>e.kind+": "+e.error).join("; "):"No recent task errors recorded."}).catch(()=>{document.querySelector("#diagnostics").textContent="Diagnostics unavailable";document.querySelector("#errors").textContent="Error history unavailable"})</script>',
        "/projects": '''<h1>Projects</h1><p>Local repository discovery is read-only and limited to owner-selected scan roots.</p><p id="projects-status" role="status">Loading projects…</p><div id="projects"></div><section aria-labelledby="milestones-heading"><h2 id="milestones-heading">Local task milestones</h2><p>These are JARVIS task events; they are not linked to a discovered repository. Coding worker and test results are unavailable until recorded by a connected worker.</p><p id="milestones-status" role="status">Loading local tasks…</p><div id="project-milestones"></div></section><script>
async function loadProjects(){const response=await fetch('/api/projects');if(!response.ok)throw new Error('projects unavailable');const data=await response.json();document.querySelector('#projects-status').textContent=data.projects.length+' local project(s) found; remote and mutation actions are disabled.';const box=document.querySelector('#projects');box.replaceChildren();for(const project of data.projects){const row=document.createElement('article'),title=document.createElement('h2'),details=document.createElement('p'),milestones=document.createElement('p');title.textContent=project.path;details.textContent='Branch: '+project.branch+' — checkpoint: '+project.checkpoint+' — '+project.status+' — tests: '+project.test_result+' — Codex: '+project.codex_progress;milestones.textContent=(project.task_milestones||[]).length+' linked local milestone(s)';row.append(title,details,milestones);box.append(row)}}
async function loadMilestones(){const response=await fetch('/api/tasks');if(!response.ok)throw new Error('tasks unavailable');const data=await response.json(),box=document.querySelector('#project-milestones');box.replaceChildren();document.querySelector('#milestones-status').textContent=data.tasks.length+' local task(s) recorded.';for(const task of data.tasks){const card=document.createElement('article'),title=document.createElement('h3'),state=document.createElement('p'),events=document.createElement('ol');title.textContent=task.kind;state.textContent='State: '+task.state+(task.error?' — '+task.error:'');for(const event of task.events||[]){const item=document.createElement('li');item.textContent=new Date(event.created*1000).toLocaleString()+' — '+event.state+': '+event.detail;events.append(item)}card.append(title,state,events);box.append(card)}}
loadProjects().catch(()=>document.querySelector('#projects-status').textContent='Project discovery unavailable');loadMilestones().catch(()=>document.querySelector('#milestones-status').textContent='Local task milestones unavailable');
</script>''',
        "/activity": '''<h1>Activity</h1><p id="task-connection" role="status">Connecting to task events…</p><section aria-labelledby="tasks-heading"><h2 id="tasks-heading">Guarded tasks</h2><form id="task-search"><label for="task-query">Search tasks, approvals, errors or event detail</label><input id="task-query" name="q" maxlength="200" autocomplete="off"><button type="submit">Search activity</button></form><div id="tasks"><p>Loading tasks…</p></div></section><section aria-labelledby="activity-heading"><h2 id="activity-heading">Approval activity</h2><p id="activity-status">Loading redacted approval events…</p><ol id="activity-events"></ol></section><script>
const taskBox=document.querySelector('#tasks'), connection=document.querySelector('#task-connection');
let lastEvent=0, source;
function esc(value){return String(value).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]))}
function render(tasks){taskBox.replaceChildren();if(!tasks.length){taskBox.innerHTML='<p>No tasks recorded.</p>';return}for(const task of tasks){const card=document.createElement('article');card.dataset.taskId=task.task_id;card.innerHTML='<h3></h3><p class="state"></p><p class="provenance"></p><p class="error"></p><ul class="events"></ul><button type="button" class="cancel">Cancel task</button>';card.querySelector('h3').textContent=task.kind;card.querySelector('.state').textContent='State: '+task.state;card.querySelector('.provenance').textContent=task.provenance?'Source: '+task.provenance.source+'; risk: '+task.provenance.risk:'Provenance unavailable';card.querySelector('.error').textContent=task.error||'';for(const event of task.events||[]){const item=document.createElement('li');item.textContent=event.state+': '+event.detail;card.querySelector('.events').append(item)}const button=card.querySelector('.cancel');button.disabled=['done','failed','cancelled'].includes(task.state);button.onclick=async()=>{button.disabled=true;const response=await fetch('/api/tasks/'+encodeURIComponent(task.task_id)+'/cancel',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf:document.querySelector('meta[name=csrf-token]').content})});if(!response.ok) connection.textContent='Task cancellation failed; refresh to retry.';else await load()};taskBox.append(card)}}
let taskQuery='';
async function load(){const suffix=taskQuery?'?q='+encodeURIComponent(taskQuery):'';const response=await fetch('/api/tasks'+suffix);if(!response.ok){connection.textContent='Task list unavailable; retrying…';return}render((await response.json()).tasks);const activity=await fetch('/api/activity'+suffix);if(!activity.ok)return;const data=await activity.json(),box=document.querySelector('#activity-events');box.replaceChildren();document.querySelector('#activity-status').textContent=data.events.length+' local activity event(s); approval targets and reasons are redacted.';for(const event of data.events){const item=document.createElement('li');const label=event.type==='task'?(event.kind+' — '+event.state+' — '+event.detail+' — '+(event.provenance||'provenance unavailable')):(event.capability+' — '+event.decision+' — '+event.result);item.textContent=new Date(event.created*1000).toLocaleString()+' — '+label;box.append(item)}}
document.querySelector('#task-search').onsubmit=async event=>{event.preventDefault();taskQuery=event.target.q.value.trim();await load()};
function connect(){if(source)source.close();source=new EventSource('/api/events?since='+lastEvent);source.onopen=()=>connection.textContent='Connected to task events';source.onerror=()=>{connection.textContent='Task events disconnected; reconnecting…';source.close();setTimeout(connect,1000)};source.addEventListener('task',event=>{const item=JSON.parse(event.data);lastEvent=Math.max(lastEvent,Number(event.lastEventId)||Number(item.id)||0);load()})}
load();connect();
</script>''',
        "/files": '<h1>Files</h1><p>Read-only metadata inventory. No scan or deletion is automatic.</p><section aria-labelledby="volumes-heading"><h2 id="volumes-heading">Mounted volumes</h2><div id="volumes">Loading volume facts…</div></section><section aria-labelledby="roots-heading"><h2 id="roots-heading">Owner-selected scan roots</h2><p id="roots-status">Loading configured roots…</p><form id="root-form"><label>Exact directory path <input name="path" required placeholder="/home/you/Documents"></label><button>Add this scan root</button></form><div id="roots"></div><h3>Index freshness</h3><div id="freshness" role="status">Loading freshness…</div></section><button id="scan" disabled>Preview dry-run scan</button><p id="scan-status" role="status"></p><script>const csrf=document.querySelector("meta[name=csrf-token]").content;async function roots(){const r=await fetch("/api/scan-roots"),x=await r.json();document.querySelector("#roots-status").textContent=x.configured?"Only these owner-selected roots can be scanned.":"No owner-selected roots; scanning is blocked.";document.querySelector("#roots").textContent=x.roots.length?x.roots.join(", "):"None configured";document.querySelector("#scan").disabled=!x.configured}async function freshness(){const r=await fetch("/api/inventory/status"),x=await r.json(),box=document.querySelector("#freshness");box.replaceChildren();if(!x.scans.length){box.textContent="No completed scan yet; freshness is unknown.";return}for(const item of x.scans){const p=document.createElement("p");p.textContent=item.path+" — last seen "+new Date(item.last_seen*1000).toLocaleString()+" — "+item.record_count+" records — "+(item.complete?"complete":"bounded limit reached; incomplete");box.append(p)}}async function volumes(){const r=await fetch("/api/mounts"),x=await r.json(),box=document.querySelector("#volumes");box.replaceChildren();for(const v of x.volumes){const p=document.createElement("p");p.textContent=v.mountpoint+" — "+v.filesystem+" — "+v.free_bytes+" bytes free of "+v.total_bytes;box.append(p)}}document.querySelector("#root-form").onsubmit=async e=>{e.preventDefault();const r=await fetch("/api/scan-roots",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({csrf,path:e.target.path.value})});if(r.ok)e.target.reset();await roots();await freshness()};document.querySelector("#scan").onclick=async()=>{const r=await fetch("/api/scan",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({csrf})});document.querySelector("#scan-status").textContent=await r.text();await freshness()};roots();volumes();freshness();</script>',
        "/actions": '''<h1>Actions</h1><p id="actions-status">Loading pending actions…</p><p>Each file is reviewed separately. Only an individually approved Move to Trash or restore can execute; permanent delete, overwrite and move remain disabled.</p><button id="emergency-stop" type="button">Emergency stop and deny pending approvals</button><section aria-labelledby="pending-heading"><h2 id="pending-heading">Pending owner decisions</h2><div id="pending-actions"></div></section><section aria-labelledby="trash-heading"><h2 id="trash-heading">Trash and restore</h2><p id="trash-status">Loading Trash…</p><div id="trash-items"></div></section><form method="post" action="/api/actions/propose"><h2>Request review</h2><label>Absolute file path <input name="path" required></label><label>Action <select name="action"><option value="trash_file">Move to Trash</option><option value="delete_file">Permanent delete</option><option value="overwrite_file">Overwrite</option><option value="move_file">Move</option></select></label><label>Reason <input name="reason" required></label><input type="hidden" name="csrf" value="%s"><button>Request approval</button></form><script>const token=document.querySelector('meta[name=csrf-token]').content;async function execute(item){const endpoint=item.action==='restore_file'?'/api/trash/restore':'/api/actions/authorize';const r=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf:token,request_id:item.request_id})});if(!r.ok)alert(await r.text());else alert(item.action==='restore_file'?'File restored.':'File moved to recoverable Trash.');await loadActions();await loadTrash()}async function decide(id,approved){const r=await fetch('/api/actions/decide',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf:token,request_id:id,approved})});if(!r.ok)alert(await r.text());await loadActions()}async function loadActions(){const r=await fetch('/api/actions');const x=await r.json();const box=document.querySelector('#pending-actions');box.replaceChildren();document.querySelector('#actions-status').textContent=x.pending.length+' individual action(s) pending';for(const item of x.pending){const card=document.createElement('article');card.innerHTML='<h3></h3><p><strong>Path:</strong> <code></code></p><p><strong>Reason:</strong> <span class="reason"></span></p><p>Exact identity: device '+item.device+', inode '+item.inode+', size '+item.size+' bytes.</p><button class="approve">Approve this file</button> <button class="deny">Deny this file</button> <button class="execute" hidden></button>';card.querySelector('h3').textContent=item.action;card.querySelector('code').textContent=item.path;card.querySelector('.reason').textContent=item.reason;const approve=card.querySelector('.approve'),deny=card.querySelector('.deny'),executeButton=card.querySelector('.execute');approve.onclick=()=>decide(item.request_id,'true');deny.onclick=()=>decide(item.request_id,'false');if(item.approved){approve.hidden=true;deny.hidden=true;executeButton.hidden=false;executeButton.textContent=item.action==='restore_file'?'Execute approved restore':'Execute approved Trash move';executeButton.onclick=()=>execute(item)}box.append(card)}}async function loadTrash(){const x=await (await fetch('/api/trash')).json(),box=document.querySelector('#trash-items');box.replaceChildren();document.querySelector('#trash-status').textContent=x.entries.length+' Trash entr'+(x.entries.length===1?'y':'ies');for(const item of x.entries.filter(e=>!e.restored)){const card=document.createElement('article');card.innerHTML='<p><code></code></p><button>Propose one-file restore</button>';card.querySelector('code').textContent=item.original_path;card.querySelector('button').onclick=async()=>{const r=await fetch('/api/trash/restore/propose',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf:token,request_id:item.request_id,reason:'owner requested restore from Actions'})});if(!r.ok)alert(await r.text());else alert('Restore proposed; review it above before any restore is considered.');await loadActions()};box.append(card)}}document.querySelector('#emergency-stop').onclick=async()=>{if(!confirm('Deny all pending approvals and cancel guarded tasks?'))return;const r=await fetch('/api/emergency-stop',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf:token})});alert(await r.text());await loadActions()};loadActions();loadTrash();</script>''' % csrf,
    }.get(route, f"<h1>{html.escape(title)}</h1><p>Not connected. This page is intentionally honest about unavailable integrations.</p>")
    if route == "/actions":
        content = content.replace(
            '</div></section><form method="post" action="/api/actions/propose">',
            '</div></section><section aria-labelledby="audit-heading"><h2 id="audit-heading">Approval audit</h2><p id="audit-status" role="status">Loading approval history…</p><ol id="audit-items"></ol></section><form method="post" action="/api/actions/propose">',
        )
        content = content.replace("async function loadActions()", "async function loadAudit(){const response=await fetch('/api/actions/audit');if(!response.ok)return;const data=await response.json();document.querySelector('#audit-status').textContent=data.audit.length+' durable approval event(s); target paths and reasons are redacted.';const box=document.querySelector('#audit-items');box.replaceChildren();for(const item of data.audit){const row=document.createElement('li');row.textContent=item.capability+' — '+item.decision+' — '+item.result;box.append(row)}}async function loadActions()")
        content = content.replace("loadActions();loadTrash();", "loadActions();loadTrash();loadAudit();/* await loadAudit() */")
    if route == "/files":
        content = content.replace(
            '<h1>Files</h1>',
            '<h1>Files</h1><section aria-labelledby="search-heading"><h2 id="search-heading">Find indexed files</h2><form id="file-search"><label for="file-query">Name or path</label><input id="file-query" name="q" maxlength="200" autocomplete="off"><button type="submit">Search index</button></form><p id="file-search-status" role="status">Search runs only against metadata already indexed in the local database.</p><div id="file-results"></div></section>'
        )
        content = content.replace(
            'roots();volumes();freshness();</script>',
            'roots();volumes();freshness();async function previews(){const response=await fetch("/api/files/duplicates");if(!response.ok)return;const data=await response.json();document.querySelector("#duplicate-status").textContent=data.groups.length+" unverified candidate group(s); content is not hash-verified.";const preview=await (await fetch("/api/files/cleanup-preview")).json();document.querySelector("#cleanup-status").textContent=preview.candidates.length+" candidate file(s), estimated "+preview.estimated_bytes+" bytes; no changes made.";const organization=await (await fetch("/api/files/organization-preview")).json();const organizationStatus=document.querySelector("#organization-status");organizationStatus.textContent=organization.plans.length+" proposed path change(s), estimated "+organization.estimated_bytes+" bytes; all mutations are disabled.";const organizationBox=document.querySelector("#organization-plans");organizationBox.replaceChildren();for(const item of organization.plans){const row=document.createElement("p");row.textContent=item.before+" → "+item.after+" — "+(item.collision?"blocked: destination exists":"would require separate owner approval");organizationBox.append(row)}}document.querySelector("#file-search").onsubmit=async event=>{event.preventDefault();const query=event.target.q.value.trim();const status=document.querySelector("#file-search-status"),box=document.querySelector("#file-results");box.replaceChildren();if(!query){status.textContent="Enter a name or path to search indexed metadata.";return}status.textContent="Searching local metadata…";const response=await fetch("/api/files?q="+encodeURIComponent(query));if(!response.ok){status.textContent="Search unavailable.";return}const result=await response.json();status.textContent=result.results.length+" result(s) from the local metadata index.";for(const item of result.results){const p=document.createElement("p");p.textContent=item.path+" — "+item.kind+" — "+item.size+" bytes — "+(item.stale?"stale: "+item.stale_reason:"current");box.append(p)}};previews();</script>'
        )
        content = content.replace('</section><button id="scan"', '<section aria-labelledby="duplicates-heading"><h2 id="duplicates-heading">Duplicate candidates</h2><p id="duplicate-status">Loading metadata candidates…</p><p id="cleanup-status">Loading cleanup preview…</p><p>Preview only: content hashes are not computed and no file changes are enabled.</p></section><section aria-labelledby="organization-heading"><h2 id="organization-heading">Organization preview</h2><p id="organization-status">Loading exact before/after paths…</p><div id="organization-plans"></div><p>These are proposals only. No move, rename, approval or other filesystem change is performed.</p></section></section><button id="scan"')
    if route == "/files":
        content = content.replace(
            '<p id="duplicate-status">Loading metadata candidates…</p>',
            '<p id="duplicate-status">Loading metadata candidates…</p><button id="verify-duplicates" type="button">Verify duplicate content hashes</button><section aria-labelledby="scheduler-heading"><h2 id="scheduler-heading">Bounded refresh</h2><p id="scheduler-status">Loading refresh scheduler…</p><button id="scheduler-start" type="button">Start periodic refresh</button> <button id="scheduler-stop" type="button">Stop periodic refresh</button><button id="scheduler-once" type="button">Refresh once now</button></section>'
        )
        content = content.replace(
            'roots();volumes();freshness();',
            'roots();volumes();freshness();async function scheduler(){const response=await fetch("/api/inventory/scheduler");if(!response.ok)return;const data=await response.json();document.querySelector("#scheduler-status").textContent=data.running?"Periodic refresh is running for selected roots.":"Periodic refresh is stopped; no scan runs implicitly."}async function schedulerAction(action){const response=await fetch("/api/inventory/scheduler",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({csrf,action})});document.querySelector("#scheduler-status").textContent=response.ok?(await response.json()).running?"Periodic refresh is running for selected roots.":"Periodic refresh is stopped; no scan runs implicitly.":"Refresh request failed.";await freshness()}document.querySelector("#scheduler-start").onclick=()=>schedulerAction("start");document.querySelector("#scheduler-stop").onclick=()=>schedulerAction("stop");document.querySelector("#scheduler-once").onclick=()=>schedulerAction("run_once");scheduler();document.querySelector("#verify-duplicates").onclick=async()=>{const status=document.querySelector("#duplicate-status");status.textContent="Hash verification is running…";const response=await fetch("/api/files/duplicates?verify=1");if(!response.ok){status.textContent="Hash verification unavailable.";return}const data=await response.json();status.textContent=data.groups.length+" verified duplicate group(s); SHA-256 was computed only after this request."};'
        )
    content = content.replace("<script>", f'<script nonce="{csp_nonce}">')
    body = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="csrf-token" content="{csrf}"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JARVIS — {html.escape(title)}</title><style>:root{{--surface:#f4f6f8;--text:#17202a;--link:#075985;--focus:#b45309}}*{{box-sizing:border-box}}body{{font:16px/1.5 system-ui,sans-serif;color:var(--text);max-width:1000px;margin:auto;padding:clamp(.75rem,3vw,2rem)}}nav{{display:flex;gap:.5rem .8rem;flex-wrap:wrap;margin:1rem 0 2rem;padding:.75rem 0;border-block:1px solid #9ca3af}}nav a{{color:var(--link);padding:.35rem .5rem;border-radius:.25rem}}nav a[aria-current="page"]{{font-weight:700;text-decoration-thickness:3px;text-underline-offset:.2em}}main{{min-width:0}}button,input,select{{font:inherit;min-height:2.5rem}}button{{padding:.4rem .8rem;cursor:pointer}}label{{display:block;margin:.75rem 0}}input,select{{max-width:100%;padding:.35rem}}pre{{background:var(--surface);padding:1rem;overflow:auto;max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere}}:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}.skip-link{{position:absolute;left:-9999px;padding:.5rem;background:var(--surface)}}.skip-link:focus{{left:.75rem;top:.75rem;z-index:2}}@media (max-width:480px){{body{{padding:.75rem}}nav{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.25rem;margin-bottom:1.25rem}}nav a{{padding:.55rem .4rem}}}}@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important}}}}</style></head><body><a class="skip-link" href="#main-content">Skip to main content</a><nav aria-label="Primary navigation">{nav}</nav><main id="main-content" tabindex="-1">{content}</main><script nonce="{csp_nonce}">fetch('/api/status').then(r=>r.json()).then(x=>{{let e=document.querySelector('#colibri');if(e)e.textContent='Colibri: '+x.colibri.state;let s=document.querySelector('#status');if(s)s.textContent=JSON.stringify(x,null,2)}}).catch(()=>{{let e=document.querySelector('#colibri');if(e)e.textContent='Colibri status unavailable'}})</script></body></html>'''
    return body.encode()


class App:
    def __init__(self) -> None:
        self.sessions: dict[str, tuple[str, float]] = {}
        self.db_path = DB_PATH
        init_db(self.db_path)
        with connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS calendar_settings (id INTEGER PRIMARY KEY CHECK (id=1), provider TEXT, timezone TEXT NOT NULL DEFAULT 'UTC')")
            row = db.execute("SELECT provider, timezone FROM calendar_settings WHERE id=1").fetchone()
        self.calendar_provider = row[0] if row else None
        self.calendar_timezone = row[1] if row else "UTC"
        with connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS email_settings (id INTEGER PRIMARY KEY CHECK (id=1), provider TEXT, account TEXT)")
            email_row = db.execute("SELECT provider FROM email_settings WHERE id=1").fetchone()
        self.email_provider = SampleEmailProvider() if email_row and email_row[0] == "sample" else None
        self.broker = ApprovalBroker(self.db_path)
        self.tasks = TaskStore(self.db_path)
        self.tasks.recover_running()
        self.dispatcher = default_dispatcher(self.tasks)
        self._worker_tasks: set[asyncio.Task] = set()
        self.inventory_scheduler = InventoryRefreshScheduler(self.db_path)

    @property
    def owner_bootstrapped(self) -> bool:
        with connect(self.db_path) as db:
            row = db.execute("SELECT bootstrapped FROM owner_state WHERE id = 1").fetchone()
            return bool(row and row[0])

    def issue_owner_session(self, token: str, now: float | None = None) -> tuple[str, str] | None:
        """Exchange the one-time local bootstrap token for an owner session."""
        if self.owner_bootstrapped or not BOOTSTRAP_TOKEN or not secrets.compare_digest(token, BOOTSTRAP_TOKEN):
            return None
        session = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        self.sessions[session] = (csrf, (now if now is not None else time.time()) + SESSION_TTL)
        with connect(self.db_path) as db:
            db.execute("INSERT OR REPLACE INTO owner_state(id, bootstrapped) VALUES (1, 1)")
        return session, csrf

    def rotate_session(self, session: str, now: float | None = None) -> tuple[str, str] | None:
        """Replace a live session with a fresh, one-use credential pair."""
        old = self.sessions.get(session)
        if not old or self.session_csrf(session, now) is None:
            return None
        self.sessions.pop(session, None)
        issued_at = now if now is not None else time.time()
        replacement = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        self.sessions[replacement] = (csrf, issued_at + SESSION_TTL)
        return replacement, csrf

    def session_csrf(self, session: str, now: float | None = None) -> str | None:
        record = self.sessions.get(session)
        if not record:
            return None
        csrf, expires = record
        if (now if now is not None else time.time()) >= expires:
            self.sessions.pop(session, None)
            return None
        return csrf

    @staticmethod
    def origin_allowed(origin: str | None) -> bool:
        """Require an explicit same-origin value for state-changing requests."""
        return origin in (f"http://{HOST}:{PORT}", f"http://localhost:{PORT}")

    @staticmethod
    def request_origin_allowed(host: str, origin: str | None) -> bool:
        """Require the Origin authority to match the request Host authority.

        Loopback aliases are intentionally separate browser origins.  Allowing
        either alias independently would let a page loaded from ``localhost``
        submit state-changing requests to a ``127.0.0.1`` Host (or vice versa).
        Parse the full origin so userinfo, paths, queries and alternate ports
        cannot be smuggled through a string-prefix check.
        """
        if not origin or not App.origin_allowed(origin):
            return False
        parsed = urlsplit(origin)
        return parsed.scheme == "http" and parsed.netloc == host and not parsed.path and not parsed.query and not parsed.fragment

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            try:
                line = await asyncio.wait_for(reader.readline(), REQUEST_READ_TIMEOUT)
            except asyncio.TimeoutError:
                await self.respond(writer, 408, b"request read timeout"); return
            if not line: return
            if len(line) > MAX_REQUEST_LINE:
                await self.respond(writer, 431, b"request line too large"); return
            try:
                request_line = line.decode("ascii")
            except UnicodeDecodeError:
                await self.respond(writer, 400, b"bad request line"); return
            # Accept only the unambiguous HTTP/1 request-line grammar.  Using
            # str.split() here would silently accept tabs or repeated spaces,
            # allowing a proxy and this control parser to disagree about the
            # request target before authentication.
            if not request_line.endswith("\r\n"):
                await self.respond(writer, 400, b"bad request line"); return
            fields = request_line[:-2].split(" ")
            if len(fields) != 3 or any(not field for field in fields):
                await self.respond(writer, 400, b"bad request line"); return
            method, target, version = fields
            # Accept origin-form targets only.  A leading double slash is
            # authority-form-shaped and may be interpreted as //host/path by
            # another HTTP component. Reject it and control characters before
            # URL parsing or route dispatch.
            if (not method or any(char not in HTTP_TOKEN_CHARS for char in method)
                    # Keep one explicit fixed-length framing contract; HTTP/1.0
                    # connection semantics are not supported by this control plane.
                    or version != "HTTP/1.1"
                    or not target.startswith("/") or target.startswith("//")
                    # Backslashes are not valid origin-form path separators,
                    # but some clients/intermediaries normalize them. Reject
                    # them before URL parsing so authenticated route meaning
                    # cannot differ across the loopback request path.
                    or "\\" in target
                    # Percent escapes must be syntactically complete before
                    # any intermediary is allowed to decode the target.
                    # Reject malformed escapes so raw and decoded routers
                    # cannot assign different authenticated route meaning.
                    or any(char == "%" and
                            (index + 2 >= len(target) or
                             any(digit not in string.hexdigits
                                 for digit in target[index + 1:index + 3]))
                            for index, char in enumerate(target))
                    # Reject percent-encoded path delimiters and controls.
                    # A proxy may decode these before forwarding while the
                    # local router does not, which could change the
                    # authenticated resource or request boundary.
                    or any(encoded in target.split("?", 1)[0].lower()
                           for encoded in (
                               "%2f", "%5c", "%23", "%3f", "%00", "%0a", "%0d",
                               # Query delimiters must not be hidden in the
                               # path: a decoding intermediary could turn
                               # these into a different authenticated route
                               # or control-field parse.
                               "%26", "%3d",
                           ))
                    # Reject every percent-encoded C0 control and DEL in the
                    # raw target, not only the common NUL/CR/LF cases. A
                    # decoding intermediary must not be able to introduce
                    # whitespace or another control delimiter after this
                    # parser has authenticated and routed the request.
                    or any(
                        target[index:index + 3].lower() in ENCODED_TARGET_CONTROLS
                        for index in range(len(target) - 2)
                        if target[index] == "%"
                    )
                    # URI fragments are client-side metadata and must not be
                    # sent in an HTTP request-target. Reject them before
                    # urlsplit/route dispatch so another intermediary cannot
                    # disagree about the authenticated resource.
                    or "#" in target
                    or any(ord(char) < 0x20 or ord(char) == 0x7f for char in target)):
                await self.respond(writer, 400, b"bad request target"); return
            headers: dict[str, str] = {}
            header_bytes = 0
            header_count = 0
            while True:
                try:
                    line = await asyncio.wait_for(reader.readline(), REQUEST_READ_TIMEOUT)
                except asyncio.TimeoutError:
                    await self.respond(writer, 408, b"request read timeout"); return
                if line == b"":
                    # EOF is not an HTTP header terminator.  Treating a
                    # truncated request as complete can make intermediaries
                    # disagree about the authenticated request boundary.
                    await self.respond(writer, 400, b"incomplete headers"); return
                if line in (b"\r\n", b"\n"):
                    break
                # Require the same CRLF framing for every non-empty header
                # line. Accepting bare LF here while requiring CRLF for the
                # request line leaves room for a proxy and this parser to
                # disagree about where security-sensitive headers end.
                if not line.endswith(b"\r\n"):
                    await self.respond(writer, 400, b"bad header line ending"); return
                header_count += 1
                header_bytes += len(line)
                if (header_count > MAX_HEADER_COUNT or len(line) > MAX_HEADER_LINE
                        or header_bytes > MAX_HEADERS):
                    await self.respond(writer, 431, b"headers too large"); return
                # Obsolete folded headers can make intermediaries disagree
                # about header meaning. The local control parser rejects them.
                if line[:1] in {b" ", b"\t"}:
                    await self.respond(writer, 400, b"folded header unsupported"); return
                try:
                    k, v = line.decode("ascii").split(":", 1)
                except (UnicodeDecodeError, ValueError):
                    await self.respond(writer, 400, b"bad header"); return
                # Header field-names are RFC token values. Do not strip or
                # normalize malformed names: security-relevant parsers must
                # agree about Host and Origin.
                if not k or any(char not in HTTP_TOKEN_CHARS for char in k):
                    await self.respond(writer, 400, b"bad header name"); return
                key = k.lower()
                if key in headers:
                    await self.respond(writer, 400, b"duplicate or bad header"); return
                raw_value = v.rstrip("\r\n")
                # Header values are metadata, never an opaque data channel.
                # Reject controls before authentication so alternate parsers
                # cannot disagree about delimiters or smuggle a second field.
                if any(ord(char) < 0x20 or ord(char) == 0x7F for char in raw_value):
                    await self.respond(writer, 400, b"control character in header"); return
                # One conventional SP after the colon is normal HTTP OWS.
                # Reject extra leading/trailing OWS for every field rather
                # than normalizing it, so parsers cannot disagree about
                # security-sensitive Host, Origin, Cookie or framing values.
                if (raw_value.startswith(("  ", "\t"))
                        or raw_value.endswith((" ", "\t"))):
                    await self.respond(writer, 400, b"ambiguous header whitespace"); return
                headers[key] = raw_value.strip()
            # The local parser intentionally supports fixed-length bodies only.
            # Refuse transfer framing rather than ignoring it and interpreting a
            # chunked request through Content-Length semantics.
            if "transfer-encoding" in headers:
                await self.respond(writer, 400, b"transfer encoding unsupported"); return
            # This control plane is a bounded request/response endpoint, not a
            # protocol-upgrade or expect/continue tunnel.  Refuse negotiation
            # rather than letting a proxy/browser disagree about when the body
            # is dispatched or treating an upgraded connection as authenticated
            # control traffic.
            if "expect" in headers or "upgrade" in headers:
                await self.respond(writer, 400, b"unsupported connection negotiation"); return
            # TE is hop-by-hop framing negotiation.  This control plane only
            # accepts a fixed Content-Length body; accepting even an
            # otherwise harmless trailer token leaves room for a proxy and
            # this parser to disagree about request framing.
            if "te" in headers:
                await self.respond(writer, 400, b"unsupported transfer negotiation"); return
            # Browsers send the exact keep-alive token even though this server
            # closes each response. Accept that harmless spelling, but never
            # honor upgrade, extra tokens or proxy-specific hop metadata.
            if headers.get("connection") not in {None, "keep-alive"}:
                await self.respond(writer, 400, b"unsupported connection negotiation"); return
            # The control plane consumes urlencoded bytes exactly as received.
            # Reject metadata for transformations, partial ranges, trailers or
            # proxy-specific connection handling rather than silently applying
            # different semantics from an intermediary.
            if any(field in headers for field in
                   {"content-encoding", "content-range", "trailer", "proxy-connection"}):
                await self.respond(writer, 400, b"unsupported request metadata"); return
            # All POST handlers below consume one exact urlencoded control
            # form.  Refuse a different declared media type rather than
            # parsing JSON/multipart bytes as a form while an intermediary or
            # browser applies different semantics.  A missing type remains
            # accepted for compatibility with the minimal local bootstrap
            # client; the body parser is still strict about fields.
            if method == "POST" and headers.get("content-type") not in {
                    None, "application/x-www-form-urlencoded"}:
                await self.respond(writer, 415, b"unsupported content type"); return
            if method == "POST" and "content-length" not in headers:
                # Every mutating control request must have an explicit fixed
                # body boundary.  Treating an unframed POST as an empty body
                # can make a proxy and this parser disagree about which bytes
                # belong to an authenticated request.
                await self.respond(writer, 411, b"content length required"); return
            content_length = headers.get("content-length", "0")
            # Content-Length is an unsigned decimal field.  Do not let
            # Python's permissive int() accept signs or other spellings that
            # a browser/proxy/parser may interpret differently.
            if (not content_length.isdecimal()
                    or any(char not in string.digits for char in content_length)
                    # Require one canonical spelling.  A proxy/parser that
                    # normalizes leading zeroes must not disagree with the
                    # control plane about the framed request length.
                    or (len(content_length) > 1 and content_length.startswith("0"))):
                await self.respond(writer, 400, b"bad content length"); return
            # Bound the decimal spelling before conversion.  Otherwise a
            # client can force Python's integer parser to reject an enormous
            # digit string (or spend disproportionate work parsing it) and
            # escape the normal fail-closed HTTP response path.
            if len(content_length) > len(str(MAX_BODY)):
                await self.respond(writer, 413, b"request too large"); return
            try:
                length = int(content_length)
            except ValueError:
                await self.respond(writer, 400, b"bad content length"); return
            if length < 0 or length > MAX_BODY:
                await self.respond(writer, 413, b"request too large"); return
            if method == "GET" and length:
                # GET has no control-plane body contract.  Refuse one before
                # consuming bytes so a client/proxy cannot disagree about
                # where this request ends and where a following request
                # begins.
                await self.respond(writer, 400, b"GET body unsupported"); return
            try:
                body = (await asyncio.wait_for(reader.readexactly(length), REQUEST_READ_TIMEOUT)
                        if length else b"")
            except asyncio.TimeoutError:
                await self.respond(writer, 408, b"request read timeout"); return
            except asyncio.IncompleteReadError:
                # A declared fixed-length body that ends early is not a
                # complete control request.  Fail closed before host,
                # authentication, CSRF or route dispatch rather than leaking
                # an uncaught parser exception or accepting a prefix.
                await self.respond(writer, 400, b"incomplete body"); return
            host = headers.get("host", "")
            origin = headers.get("origin")
            allowed_hosts = {f"{HOST}:{PORT}", f"localhost:{PORT}"}
            # Header parsing strips surrounding OWS.  Reject any remaining
            # whitespace/control or authority-shaped spelling explicitly so a
            # proxy/browser disagreement cannot turn a near-match into a
            # control-plane request.  The exact allow-list remains the final
            # decision; no DNS lookup is performed.
            if (not host or any(char.isspace() or ord(char) < 0x20 for char in host)
                    or host not in allowed_hosts
                    or (origin and not self.request_origin_allowed(host, origin))):
                await self.respond(writer, 403, b"forbidden"); return
            if method not in {"GET", "POST"}:
                await self.respond(writer, 405, b"method not allowed"); return
            if method == "POST" and not self.request_origin_allowed(host, origin):
                await self.respond(writer, 403, b"same-origin required"); return
            cookies = headers.get("cookie", "")
            sid = self._session_cookie(cookies)
            path = urlsplit(target).path
            if method == "POST" and path == "/api/bootstrap":
                try:
                    fields = _action_form(body, {"token"}, {"token"})
                except ValueError:
                    await self.respond(writer, 403, b"bootstrap denied")
                    return
                issued = self.issue_owner_session(fields["token"])
                if not issued:
                    await self.respond(writer, 403, b"bootstrap denied")
                    return
                sid, _ = issued
                await self.respond(writer, 204, b"", sid)
                return
            csrf = self.session_csrf(sid) if sid else None
            if not sid or not csrf:
                await self.respond(writer, 401, b"owner authentication required")
                return
            if method == "POST" and path == "/api/chat":
                try:
                    fields = _csrf_form(body, {"message"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf: await self.respond(writer, 403, b"csrf"); return
                message = fields["message"]
                try:
                    answer = await ColibriClient().complete_async(message)
                except (ConnectionError, OSError, TimeoutError, ValueError) as exc:
                    result = json.dumps({"status": "unavailable", "error": str(exc)}).encode()
                    await self.respond(writer, 503, result, sid); return
                save_chat_turn(self.db_path, message.strip(), answer)
                result = json.dumps({"status": "complete", **answer}).encode(); await self.respond(writer, 200, result, sid); return
            if method == "POST" and path == "/api/chat/stream":
                try:
                    fields = _csrf_form(body, {"message"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                message = fields["message"].strip()
                if not message:
                    await self.respond(writer, 400, json.dumps({"error": "message must not be empty"}).encode(), sid); return
                # The stream is a response-only capability.  Persist the turn
                # only after [DONE], so cancellation or a provider failure
                # cannot create a false successful history entry.
                await self._respond_stream_headers(writer, sid)
                chunks: list[str] = []
                model = None
                # A browser AbortController closes the request socket. Watch
                # it independently of provider output so a quiet model cannot
                # keep working until its next delta or socket timeout.
                disconnected = asyncio.create_task(reader.read(1))
                stream = ColibriClient().complete_stream_async(message)
                try:
                    while True:
                        next_delta = asyncio.create_task(anext(stream, None))
                        done, _ = await asyncio.wait(
                            {next_delta, disconnected}, return_when=asyncio.FIRST_COMPLETED
                        )
                        if disconnected in done:
                            next_delta.cancel()
                            try:
                                await next_delta
                            except asyncio.CancelledError:
                                pass
                            break
                        delta = next_delta.result()
                        if delta is None:
                            if not disconnected.done() and not writer.is_closing():
                                answer = {"model": model or "unknown", "content": "".join(chunks)}
                                writer.write(f"event: done\ndata: {json.dumps(answer, separators=(',', ':'))}\n\n".encode())
                                await writer.drain()
                                save_chat_turn(self.db_path, message, answer)
                            break
                        model = delta.get("model") or model
                        chunks.append(delta["content"])
                        event = json.dumps({"model": model, "content": delta["content"]}, separators=(",", ":"))
                        writer.write(f"event: delta\ndata: {event}\n\n".encode())
                        await writer.drain()
                except (ConnectionError, OSError, TimeoutError, ValueError, asyncio.CancelledError) as exc:
                    if not isinstance(exc, asyncio.CancelledError) and not writer.is_closing():
                        error = json.dumps({"error": str(exc) or "chat stream unavailable"}, separators=(",", ":"))
                        try:
                            writer.write(f"event: error\ndata: {error}\n\n".encode())
                            await writer.drain()
                        except (ConnectionError, OSError):
                            pass
                finally:
                    disconnected.cancel()
                    await asyncio.gather(disconnected, return_exceptions=True)
                    await stream.aclose()
                return
            if method == "GET" and path == "/api/chat/history":
                await self.respond(writer, 200, json.dumps({"messages": chat_history(self.db_path)}).encode(), sid); return
            if method == "GET" and path == "/api/home":
                await self.respond(writer, 200, json.dumps(home_summary(self)).encode(), sid); return
            if method == "GET" and path == "/api/voice":
                await self.respond(writer, 200, json.dumps(voice_summary()).encode(), sid); return
            if path == "/api/calendar":
                if method == "POST":
                    try:
                        fields = _csrf_form(body, {"provider", "timezone"})
                    except ValueError as exc:
                        await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                    if fields["csrf"] != csrf:
                        await self.respond(writer, 403, b"csrf"); return
                    if fields["provider"] != "sample":
                        await self.respond(writer, 400, json.dumps({"error": "only the explicit sample connector is available"}).encode(), sid); return
                    timezone_name = fields["timezone"]
                    try:
                        sample_calendar(timezone_name)
                    except ValueError as exc:
                        await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                    with connect(self.db_path) as db:
                        db.execute("INSERT OR REPLACE INTO calendar_settings(id, provider, timezone) VALUES (1, 'sample', ?)", (timezone_name,))
                    self.calendar_provider, self.calendar_timezone = "sample", timezone_name
                    await self.respond(writer, 200, json.dumps(calendar_summary(self)).encode(), sid); return
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps(calendar_summary(self)).encode(), sid); return
            if path == "/api/email":
                if method == "POST":
                    try:
                        fields = _csrf_form(body, {"provider"})
                    except ValueError as exc:
                        await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                    if fields["csrf"] != csrf or fields["provider"] != "sample":
                        await self.respond(writer, 400, b"only the explicit sample connector is available", sid); return
                    self.email_provider = SampleEmailProvider()
                    with connect(self.db_path) as db:
                        db.execute("INSERT OR REPLACE INTO email_settings(id, provider, account) VALUES (1, 'sample', ?)", (self.email_provider.account,))
                    await self.respond(writer, 200, json.dumps({"state": "connected", "provider": "sample", "account": self.email_provider.account, "messages": [m.__dict__ for m in self.email_provider.search("")], "send": "approval_required"}).encode(), sid); return
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                if self.email_provider is None:
                    await self.respond(writer, 200, json.dumps(email_summary(self.db_path)).encode(), sid); return
                await self.respond(writer, 200, json.dumps({"state": "connected", "provider": "sample", "account": self.email_provider.account, "messages": [m.__dict__ for m in self.email_provider.search("")], "query": "", "drafts": email_drafts(self.db_path), "send": "approval_required"}).encode(), sid); return
            if path == "/api/email/search":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    query = _query(target, {"q"}).get("q", "")
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if self.email_provider is None:
                    await self.respond(writer, 200, json.dumps(email_search(query)).encode(), sid); return
                await self.respond(writer, 200, json.dumps({"state": "connected", "provider": "sample", "query": query, "messages": [m.__dict__ for m in self.email_provider.search(query)], "search": "enabled"}).encode(), sid); return
            if path == "/api/email/draft":
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _action_form(body, {"csrf", "to", "subject", "body"},
                                          {"csrf", "to", "subject", "body"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    preview = email_draft_preview({key: value for key, value in fields.items() if key != "csrf"}, self.db_path)
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 200, json.dumps(preview).encode(), sid); return
            if path == "/api/email/send":
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _action_form(body, {"csrf", "draft_id"}, {"csrf"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                if self.email_provider is None:
                    await self.respond(writer, 409, json.dumps({"state": "disconnected", "send": "disabled", "message": "Email OAuth is not configured; no message was sent."}).encode(), sid); return
                with connect(self.db_path) as db:
                    draft = db.execute("SELECT recipient, subject, body FROM email_drafts WHERE draft_id=?", (fields["draft_id"],)).fetchone()
                if not draft:
                    await self.respond(writer, 404, b"draft not found", sid); return
                message_id = self.email_provider.send(*draft)
                await self.respond(writer, 200, json.dumps({"state": "sent", "provider": "sample", "message_id": message_id, "message": "Sample message recorded locally after explicit approval."}).encode(), sid); return
            if path == "/api/calendar/proposals":
                if method == "GET":
                    await self.respond(writer, 200, json.dumps({"proposals": calendar_proposals(self.db_path)}).encode(), sid); return
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body, {"event_id", "operation", "title"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                if self.calendar_provider != "sample":
                    await self.respond(writer, 409, json.dumps({
                        "state": "disconnected", "proposals": "disabled",
                        "message": "Connect the explicit owner-approved calendar view before proposing a change.",
                    }).encode(), sid); return
                event_id = fields["event_id"].strip()
                operation = fields["operation"]
                title = fields["title"].strip()
                if (not event_id or len(event_id) > 128 or operation not in {"create", "update", "cancel"}
                        or len(title) > 200 or (operation in {"update", "cancel"}
                                                and event_id not in proposal_event_ids(self.calendar_timezone))):
                    await self.respond(writer, 400, b"invalid calendar proposal"); return
                proposal_id = uuid.uuid4().hex
                payload = {"title": title}
                with connect(self.db_path) as db:
                    db.execute("INSERT INTO calendar_proposals(proposal_id,event_id,operation,payload,state,created) VALUES (?,?,?,?,?,?)",
                               (proposal_id, event_id, operation, json.dumps(payload), "pending", time.time()))
                await self.respond(writer, 201, json.dumps({"proposal": calendar_proposals(self.db_path)[0]}).encode(), sid); return
            if path.startswith("/api/calendar/proposals/") and path.endswith("/decide"):
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body, {"decision"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                proposal_id = path.removeprefix("/api/calendar/proposals/").removesuffix("/decide")
                try:
                    proposal_id = _opaque_path_id(proposal_id, "proposal id")
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                decision = fields["decision"]
                if decision not in {"approved", "denied"}:
                    await self.respond(writer, 400, b"invalid decision"); return
                with connect(self.db_path) as db:
                    row = db.execute("SELECT state FROM calendar_proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
                    if not row or row[0] != "pending":
                        await self.respond(writer, 409, b"proposal is not pending"); return
                    db.execute("UPDATE calendar_proposals SET state=?, decided=? WHERE proposal_id=?", (decision, time.time(), proposal_id))
                await self.respond(writer, 200, json.dumps({"proposal_id": proposal_id, "state": decision,
                    "writes": "disabled", "message": "Recorded locally; no external calendar write was performed."}).encode(), sid); return
            if path == "/api/tasks":
                if method == "GET":
                    try:
                        query = _query(target, {"q"}).get("q", "")
                    except ValueError as exc:
                        await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                    tasks = [self.task_json(task) for task in self.tasks.list(query=query)]
                    await self.respond(writer, 200, json.dumps({"tasks": tasks}).encode(), sid); return
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body, {"kind", "idempotency_key", "payload"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    kind = fields["kind"]
                    key = fields["idempotency_key"]
                    payload = json.loads(fields["payload"])
                    spec = self.dispatcher.spec(kind)
                    if spec is None:
                        raise ValueError("task kind is not an allowlisted read_only tool")
                    # The worker may persist only the app-owned database path;
                    # callers cannot redirect an inventory write elsewhere.
                    if kind == "inventory.scan":
                        if not isinstance(payload, dict):
                            raise ValueError("task payload must be an object")
                        payload = {**payload, "db_path": str(self.db_path)}
                    payload = self.dispatcher.validate(kind, payload)
                    task = self.tasks.create(kind, payload, key)
                except (ValueError, json.JSONDecodeError, TypeError) as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if task.state == "queued":
                    worker_task = asyncio.create_task(self.dispatcher.run(task.task_id))
                    self._worker_tasks.add(worker_task)
                    worker_task.add_done_callback(self._worker_tasks.discard)
                await self.respond(writer, 201, json.dumps(self.task_json(task)).encode(), sid); return
            if path == "/api/activity":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    query = _query(target, {"q"}).get("q", "").strip()[:200].casefold()
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                # Activity is a single local timeline. Keep task details bounded and approval records redacted.
                events = []
                for event in self.tasks.events_since(0, 200):
                    task = self.tasks.get(event["task_id"])
                    spec = self.dispatcher.spec(task.kind)
                    events.append({"type": "task", "created": event["created"], "kind": task.kind,
                                   "state": event["state"], "detail": event["detail"],
                                   "provenance": spec.provenance if spec else None})
                events.extend({"type": "approval", **event} for event in self.broker.audit())
                events.sort(key=lambda event: event.get("created", 0), reverse=True)
                if query:
                    events = [event for event in events if any(
                        query in str(event.get(field, "")).casefold()
                        for field in ("type", "kind", "state", "detail", "provenance", "capability", "decision", "result")
                    )]
                await self.respond(writer, 200, json.dumps({"events": events[:100]}).encode(), sid); return
            if path.startswith("/api/tasks/") and path.endswith("/cancel"):
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body)
                except ValueError:
                    await self.respond(writer, 403, b"csrf", sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    task_id = _opaque_path_id(path.removeprefix("/api/tasks/").removesuffix("/cancel"), "task id")
                    self.dispatcher.cancel(task_id)
                    task = self.tasks.cancel(task_id)
                except (KeyError, ValueError) as exc:
                    await self.respond(writer, 409, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 200, json.dumps(self.task_json(task)).encode(), sid); return
            if method == "POST" and path == "/api/emergency-stop":
                try:
                    fields = _csrf_form(body)
                except ValueError:
                    await self.respond(writer, 403, b"csrf", sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                cancelled = 0
                for task in self.tasks.list():
                    if task.state not in {"done", "failed", "cancelled"}:
                        try:
                            self.dispatcher.cancel(task.task_id)
                            self.tasks.cancel(task.task_id)
                            cancelled += 1
                        except (KeyError, ValueError):
                            pass
                denied = self.broker.emergency_stop()
                await self.respond(writer, 200, json.dumps({"status": "stopped", "cancelled_tasks": cancelled, "denied_approvals": denied}).encode(), sid); return
            if path == "/api/events":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    query = _query(target, {"since", "follow"})
                    since = int(query.get("since", "0"))
                    follow_value = query.get("follow", "0")
                    if follow_value not in {"0", "1"}:
                        raise ValueError("invalid follow")
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                events = self.tasks.events_since(since)
                follow = follow_value == "1"
                stream = "".join(self._sse_event(event) for event in events)
                if not follow:
                    await self.respond(writer, 200, stream.encode(), sid, "text/event-stream; charset=utf-8"); return
                # Follow mode is an authenticated, bounded-poll stream.  It
                # replays durable events first, then waits for new rows.  No
                # task payload or control capability is exposed on this path.
                await self._respond_stream_headers(writer, sid)
                if stream:
                    writer.write(stream.encode()); await writer.drain()
                    since = events[-1]["id"]
                idle = 0
                while idle < 300 and not writer.is_closing():
                    await asyncio.sleep(0.1)
                    fresh = self.tasks.events_since(since)
                    if fresh:
                        try:
                            writer.write("".join(self._sse_event(event) for event in fresh).encode())
                            await writer.drain()
                        except (ConnectionError, OSError):
                            return
                        since = fresh[-1]["id"]
                        idle = 0
                    else:
                        idle += 1
                        if idle % 5 == 0:
                            try:
                                writer.write(b": keep-alive\n\n"); await writer.drain()
                            except (ConnectionError, OSError):
                                return
                return
            if path == "/api/actions":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                pending = []
                for request in self.broker._requests.values():
                    if request.request_id not in self.broker._consumed and (
                        request.request_id not in self.broker._decisions or request.request_id in self.broker._approved
                    ):
                        pending.append({"request_id": request.request_id, "action": request.action,
                                        "path": request.identity.path, "size": request.identity.size,
                                        "device": request.identity.device, "inode": request.identity.inode,
                                        "mtime_ns": request.identity.mtime_ns,
                                        "reason": request.reason, "expires_at": request.expires_at,
                                        "approved": request.request_id in self.broker._approved})
                await self.respond(writer, 200, json.dumps({"pending": pending}).encode(), sid); return
            if path == "/api/scan-roots":
                if method == "GET":
                    roots = [str(root) for root in configured_roots(self.db_path)]
                    await self.respond(writer, 200, json.dumps({"roots": roots, "configured": bool(roots)}).encode(), sid); return
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body, {"path"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    root = add_configured_root(Path(fields["path"]), self.db_path)
                except (OSError, ValueError) as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 201, json.dumps({"status": "configured", "path": str(root)}).encode(), sid); return
            if path == "/api/inventory/status":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps({"scans": refresh_status(self.db_path)}).encode(), sid); return
            if path == "/api/inventory/scheduler":
                if method == "GET":
                    await self.respond(writer, 200, json.dumps({
                        "running": self.inventory_scheduler.running,
                        "interval_seconds": self.inventory_scheduler.interval_seconds,
                        "limit": self.inventory_scheduler.limit,
                        "last_result": self.inventory_scheduler.last_result,
                    }).encode(), sid); return
                if method != "POST":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    fields = _csrf_form(body, {"action"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                action = fields["action"]
                if action == "start":
                    changed = self.inventory_scheduler.start()
                    result = {"started": changed, "running": self.inventory_scheduler.running}
                elif action == "stop":
                    await self.inventory_scheduler.stop()
                    result = {"stopped": True, "running": False}
                elif action == "run_once":
                    result = await self.inventory_scheduler.run_once()
                    result["running"] = self.inventory_scheduler.running
                else:
                    await self.respond(writer, 400, b"invalid scheduler action", sid); return
                await self.respond(writer, 200, json.dumps(result).encode(), sid); return
            if path == "/api/actions/audit":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps({"audit": self.broker.audit()}).encode(), sid); return
            if path == "/api/trash":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                with connect(self.db_path) as db:
                    db.row_factory = sqlite3.Row
                    rows = db.execute("SELECT request_id, trash_path, original_path, checksum, size, created, restored FROM trash_manifests ORDER BY created DESC").fetchall()
                await self.respond(writer, 200, json.dumps({"entries": [dict(row) for row in rows]}).encode(), sid); return
            if method == "POST" and path == "/api/actions/propose":
                try:
                    fields = _action_form(body, {"csrf", "path", "action", "reason"}, {"csrf", "path", "action", "reason"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    request = self.broker.propose(Path(fields["path"]), fields["action"], fields["reason"])
                except (ApprovalError, OSError, ValueError) as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                result = {"status": "pending_owner_decision", "request_id": request.request_id,
                          "action": request.action, "path": request.identity.path, "size": request.identity.size,
                          "reason": request.reason, "expires_at": request.expires_at}
                await self.respond(writer, 201, json.dumps(result).encode(), sid); return
            if method == "POST" and path == "/api/actions/decide":
                try:
                    fields = _action_form(body, {"csrf", "request_id", "approved"}, {"csrf", "request_id", "approved"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    if fields["approved"] not in {"true", "false"}:
                        raise ApprovalError("approved must be true or false")
                    approved = fields["approved"] == "true"
                    self.broker.decide(fields["request_id"], approved)
                except ApprovalError as exc:
                    await self.respond(writer, 403, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 200, json.dumps({"status": "approved" if approved else "denied"}).encode(), sid); return
            if method == "POST" and path == "/api/trash/restore/propose":
                try:
                    fields = _action_form(body, {"csrf", "request_id", "reason"}, {"csrf", "request_id", "reason"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    request = self.broker.propose_restore(fields["request_id"], fields["reason"])
                except (ApprovalError, OSError, ValueError) as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 201, json.dumps({"status": "pending_owner_decision", "request_id": request.request_id, "action": request.action, "path": request.identity.path, "expires_at": request.expires_at}).encode(), sid); return
            if method == "POST" and path == "/api/trash/restore":
                try:
                    fields = _action_form(body, {"csrf", "request_id"}, {"csrf", "request_id"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    restored = self.broker.restore_file(fields["request_id"])
                except ApprovalError as exc:
                    await self.respond(writer, 403, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 200, json.dumps({"status": "restored", "path": str(restored)}).encode(), sid); return
            if method == "POST" and path == "/api/actions/authorize":
                try:
                    fields = _action_form(body, {"csrf", "request_id"}, {"csrf", "request_id"})
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                try:
                    request_id = fields["request_id"]
                    request = self.broker._requests.get(request_id)
                    if not request or request.action != "trash_file":
                        await self.respond(writer, 403, json.dumps({"error": "only approved Trash moves are executable"}).encode(), sid); return
                    moved = self.broker.trash_file(request_id)
                except ApprovalError as exc:
                    await self.respond(writer, 403, json.dumps({"error": str(exc)}).encode(), sid); return
                await self.respond(writer, 200, json.dumps({"status": "completed", "mutation": "trash",
                    "request_id": request.request_id, "path": request.identity.path, "trash_path": str(moved),
                    "action": request.action}).encode(), sid); return
            if method == "POST" and path == "/api/logout":
                try:
                    fields = _csrf_form(body)
                except ValueError:
                    await self.respond(writer, 403, b"csrf", sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                self.sessions.pop(sid, None)
                await self.respond(writer, 204, b"", None, clear_cookie=True); return
            if method == "POST" and path == "/api/session/rotate":
                try:
                    fields = _csrf_form(body)
                except ValueError:
                    await self.respond(writer, 403, b"csrf", sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                rotated = self.rotate_session(sid)
                if not rotated:
                    await self.respond(writer, 401, b"session expired"); return
                new_sid, new_csrf = rotated
                await self.respond(writer, 200, json.dumps({"status": "rotated", "csrf": new_csrf}).encode(), new_sid); return
            if path == "/api/status":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                result = json.dumps({"ok": True, "backend": "running", "colibri": probe_colibri(), "routes": ROUTES}).encode(); await self.respond(writer, 200, result, sid); return
            if path == "/api/mounts":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps({"volumes": mounted_volumes()}).encode(), sid); return
            if path == "/api/projects":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps({"projects": discover_projects(self.db_path)}).encode(), sid); return
            if path == "/api/diagnostics":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                colibri = probe_colibri()
                await self.respond(writer, 200, json.dumps(read_only_diagnostics(service_states={
                    "backend": "running",
                    "colibri": colibri.get("state", "unavailable"),
                    "repairs": "disabled",
                }, storage_reader=mounted_volumes,
                   error_history=recent_error_history(self.db_path))).encode(), sid); return
            if method == "POST" and path == "/api/colibri/warmup":
                try:
                    fields = _csrf_form(body)
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                result = json.dumps({"status": "warmup_probe", "colibri": ColibriClient().warmup()}).encode()
                await self.respond(writer, 200, result, sid); return
            if method == "POST" and path == "/api/scan":
                try:
                    fields = _csrf_form(body)
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if fields["csrf"] != csrf:
                    await self.respond(writer, 403, b"csrf"); return
                roots = configured_roots(self.db_path)
                if not roots:
                    await self.respond(writer, 409, json.dumps({"error": "no scan roots configured by owner"}).encode(), sid); return
                records, truncated = scan(roots, limit=2000)
                stored = store(records, self.db_path, roots)
                result = json.dumps({"dry_run": True, "status":"metadata_indexed", "roots":[str(r) for r in roots], "records":stored, "truncated":truncated}).encode(); await self.respond(writer, 200, result, sid); return
            if path == "/api/scan" and method != "POST":
                await self.respond(writer, 405, b"method not allowed"); return
            if path == "/api/files":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    query = _query(target, {"q"}).get("q", "").strip()
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                result = json.dumps({"query": query, "results": search(query, self.db_path) if query else []}).encode(); await self.respond(writer, 200, result, sid); return
            if path == "/api/files/duplicates":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                try:
                    verify_value = _query(target, {"verify"}).get("verify", "")
                except ValueError as exc:
                    await self.respond(writer, 400, json.dumps({"error": str(exc)}).encode(), sid); return
                if verify_value not in {"", "0", "1"}:
                    await self.respond(writer, 400, json.dumps({"error": "verify must be 0 or 1"}).encode(), sid); return
                verify = verify_value == "1"
                groups = verified_duplicate_groups(self.db_path) if verify else duplicate_groups(self.db_path)
                await self.respond(writer, 200, json.dumps({"groups": groups, "verified": verify}).encode(), sid); return
            if path == "/api/files/cleanup-preview":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps(cleanup_preview(self.db_path)).encode(), sid); return
            if path == "/api/files/organization-preview":
                if method != "GET":
                    await self.respond(writer, 405, b"method not allowed"); return
                await self.respond(writer, 200, json.dumps(organization_preview(self.db_path)).encode(), sid); return
            if path.startswith("/api/"):
                await self.respond(writer, 404, b"not found"); return
            if method != "GET" or path not in ROUTES:
                await self.respond(writer, 404, b"not found"); return
            nonce = secrets.token_urlsafe(18)
            await self.respond(writer, 200, page(path, csrf, nonce), sid, "text/html; charset=utf-8", csp_nonce=nonce)
        except Exception:
            await self.respond(writer, 400, b"bad request")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass

    async def respond(self, writer: asyncio.StreamWriter, status: int, body: bytes, sid: str | None = None, content_type: str = "application/json", clear_cookie: bool = False, csp_nonce: str | None = None) -> None:
        # Do not set Secure: the supported dashboard transport is loopback HTTP.
        # Host-only, HttpOnly and Strict SameSite prevent reuse on other hosts/tabs.
        extra = f"Set-Cookie: jarvis_session={sid}; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Strict; Path=/\r\n" if sid else ""
        if clear_cookie:
            extra = "Set-Cookie: jarvis_session=; Max-Age=0; HttpOnly; SameSite=Strict; Path=/\r\n"
        script_policy = "'self'" + (f" 'nonce-{csp_nonce}'" if csp_nonce else "")
        headers = (f"Content-Type: {content_type}\r\nContent-Length: {len(body)}\r\n"
                   "Cache-Control: no-store\r\n"
                   f"Content-Security-Policy: default-src 'self'; script-src {script_policy}; "
                   "style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; "
                   "base-uri 'none'; form-action 'self'; manifest-src 'none'; worker-src 'none'; "
                   "frame-ancestors 'none'\r\n"
                   "Referrer-Policy: no-referrer\r\n"
                   "Cross-Origin-Resource-Policy: same-origin\r\n"
                   "Cross-Origin-Opener-Policy: same-origin\r\n"
                   # Authenticated dashboard responses have no cross-origin
                   # resource dependency; prevent embedding by other contexts.
                   "Cross-Origin-Embedder-Policy: require-corp\r\n"
                   "X-Permitted-Cross-Domain-Policies: none\r\n"
                   "Permissions-Policy: accelerometer=(), ambient-light-sensor=(), autoplay=(), camera=(), "
                   "clipboard-read=(), clipboard-write=(), geolocation=(), gyroscope=(), microphone=(self), "
                   "payment=(), usb=()\r\n"
                   "X-Content-Type-Options: nosniff\r\n"
                   "X-Frame-Options: DENY\r\n")
        writer.write(f"HTTP/1.1 {status} OK\r\n{headers}{extra}\r\n".encode() + body); await writer.drain()

    @staticmethod
    def _session_cookie(header: str) -> str | None:
        """Return one well-formed session cookie, or fail closed on ambiguity."""
        if any(ord(char) < 0x20 or ord(char) == 0x7f for char in header):
            return None
        values: list[str] = []
        for part in header.split(";"):
            name, separator, value = part.strip().partition("=")
            if not separator:
                continue
            if name == "jarvis_session":
                if not value or any(char.isspace() or char in ",;\r\n" for char in value):
                    return None
                values.append(value)
        if len(values) != 1:
            return values[0] if len(values) == 1 else None
        return values[0]

    @staticmethod
    def _sse_event(event: dict) -> str:
        return f"id: {event['id']}\nevent: task\ndata: {json.dumps(event, separators=(',', ':'))}\n\n"

    async def _respond_stream_headers(self, writer: asyncio.StreamWriter, sid: str) -> None:
        writer.write((f"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream; charset=utf-8\r\n"
                      f"Cache-Control: no-store\r\nConnection: keep-alive\r\n"
                      "Content-Security-Policy: default-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; manifest-src 'none'; worker-src 'none'; frame-ancestors 'none'\r\n"
                      "Referrer-Policy: no-referrer\r\nX-Content-Type-Options: nosniff\r\nX-Frame-Options: DENY\r\n"
                      "Cross-Origin-Resource-Policy: same-origin\r\nCross-Origin-Opener-Policy: same-origin\r\n"
                      "Permissions-Policy: accelerometer=(), ambient-light-sensor=(), autoplay=(), camera=(), clipboard-read=(), "
                      "clipboard-write=(), geolocation=(), gyroscope=(), microphone=(self), payment=(), usb=()\r\n"
                      f"Set-Cookie: jarvis_session={sid}; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Strict; Path=/\r\n\r\n").encode())
        await writer.drain()

    def task_json(self, task) -> dict:
        spec = self.dispatcher.spec(task.kind)
        return {"task_id": task.task_id, "idempotency_key": task.idempotency_key,
                "kind": task.kind, "payload": task.payload, "state": task.state,
                "result": task.result, "error": task.error,
                "provenance": {"source": spec.provenance, "risk": spec.risk} if spec else None,
                "events": self.tasks.events_for(task.task_id)}


async def run() -> None:
    app = App(); server = await asyncio.start_server(app.handle, HOST, PORT)
    async with server: await server.serve_forever()


if __name__ == "__main__": asyncio.run(run())
