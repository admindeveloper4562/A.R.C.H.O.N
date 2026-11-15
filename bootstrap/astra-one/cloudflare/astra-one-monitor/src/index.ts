/** Private SDA progress monitor. No task prompts, source or raw logs accepted. */
interface ResultSet<T> { results?: T[] }
interface D1Statement {
  bind(...args: unknown[]): D1Statement;
  first<T>(): Promise<T | null>;
  all<T>(): Promise<ResultSet<T>>;
  run(): Promise<unknown>;
}
interface D1Database { prepare(query: string): D1Statement }
interface Env {
  DB: D1Database;
  ASTRA_INGEST_TOKEN: string;
  ASTRA_VIEW_TOKEN: string;
}
const STAGES = new Set(["queued", "preflight", "coding", "verifying", "awaiting_review", "approved", "completed", "failed", "stopped", "interrupted"]);
const MAX_BYTES = 4096;
interface Event {
  event_id: string; run_id: string; task_id: string; seq: number;
  time: string; stage: string; step: string; branch: string;
  base_sha: string; tool_count: number; result: string; elapsed_s: number; attempt: number;
}
const dashboard = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Astra One — Development Monitor</title>
<style>
:root{font-family:system-ui,Arial,sans-serif;color-scheme:dark;background:#0b1020;color:#edf3ff}
*{box-sizing:border-box}body{margin:0;padding:28px;max-width:1100px;margin-inline:auto}
h1{font-size:clamp(23px,4vw,36px);margin:0 0 6px}p,.muted{color:#a6b6cc}
header{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.card{background:#141f36;border:1px solid #30425c;border-radius:14px;padding:18px;margin-top:16px}
input,button{font:inherit;padding:10px 13px;border-radius:9px;color:#edf3ff}
input{background:#0b1020;border:1px solid #3f526f;min-width:230px}
button{background:#4268e8;border:0;cursor:pointer}button:hover{background:#4667e8}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.count{font-size:30px;font-weight:700;margin:6px 0}table{width:100%;border-collapse:collapse}
hr,td,th{border:0;border-bottom:1px solid #293a55}th,td{text-align:left;padding:12px 8px;font-size:14px}
.scroll{overflow:auto}small{color:#a6b6cc}.tag{font-size:12px;padding:4px 8px;border:1px solid #536680;border-radius:14px}
.status-coding{color:#8ebcff}.status-awaiting_review{color:#f4cb75}.status-failed{color:#f39b9b}.status-completed,.status-approved{color:#8de5a7}.status-interrupted{color:#ffb27a}
#message{min-height:20px;color:#f4cb75}tbody tr{cursor:pointer}tbody tr:hover{background:#20304a}
</style></head><body>
<header><div><h1>ASTRA ONE / SDA</h1><p>JARVIS v2 build telemetry · Linux Codex Luna / five-agent SDA · refresh every 4 seconds</p></div><span class="tag">SECURE BUILD FEED</span></header>
<section class="card"><label for="token">Dashboard view token (browser memory only)</label><div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap"><input id="token" type="password" autocomplete="off" placeholder="ASTRA_VIEW_TOKEN"/><button id="connect">Connect</button></div><p id="message">Enter the dashboard view token.</p></section>
<section class="grid" id="counters"></section>
<section class="card"><h2>Recent SDA runs</h2><div class="scroll"><table><thead><tr><th>Task</th><th>Stage</th><th>Step</th><th>Result</th><th>Tools</th><th>Updated (UTC)</th></tr></thead><tbody id="runs"></tbody></table></div></section>
<section class="card"><h2>Selected run events</h2><p class="muted" id="selected">Select a run to inspect its status timeline.</p><div class="scroll"><table><thead><tr><th>#</th><th>Time (UTC)</th><th>Stage</th><th>Step</th><th>Result</th></tr></thead><tbody id="events"></tbody></table></div></section>
<script src="/app.js" defer></script></body></html>`;
const appjs = `(() => {
  let token='',selected='',timer;
  const $ = x => document.getElementById(x);
  const make=(tag,text,cls)=>{const e=document.createElement(tag);e.textContent=String(text);if(cls)e.className=cls;return e};
  async function get(url){const r=await fetch(url,{headers:{authorization:'Bearer '+token},cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()}
  async function refresh(){
    if(!token)return;
    try {
      const [stats,data]=await Promise.all([get('/api/summary'),get('/api/runs')]);
      $('message').textContent='Connected. Last refresh: '+new Date().toLocaleTimeString();
      const counts=$('counters');counts.replaceChildren();
      for(const [label,value] of Object.entries(stats.counts||{})){
        const card=make('div','','card');card.append(make('small',label),make('div',value,'count'));counts.append(card);
      }
      const body=$('runs');body.replaceChildren();
      for(const r of data.runs||[]){const tr=document.createElement('tr');
        for(const [value,cls] of [[r.task_id,''],[r.stage,'status-'+r.stage],[r.step,''],[r.result,''],[r.tool_count,''],[r.last_seen_at,'']]){tr.append(make('td',value,cls))}
        tr.addEventListener('click',()=>{selected=r.run_id;$('selected').textContent='Run '+r.run_id+' · '+r.branch+' · '+r.base_sha.slice(0,10);loadEvents()});body.append(tr);
      }
      if(selected)await loadEvents();
    }catch(e){$('message').textContent='Connection error: '+e.message}
  }
  async function loadEvents(){if(!selected)return;try{const data=await get('/api/events?run_id='+encodeURIComponent(selected));
    const body=$('events');body.replaceChildren();for(const e of data.events||[]){const tr=document.createElement('tr');
      for(const val of [e.seq,e.time,e.stage,e.step,e.result])tr.append(make('td',val));body.append(tr)}
  }catch(e){$('message').textContent='Timeline unavailable: '+e.message}}
  $('connect').addEventListener('click',()=>{token=$('token').value.trim();$('token').value='';if(!token)return;$('message').textContent='Connecting…';refresh();if(timer)clearInterval(timer);timer=setInterval(refresh,4000)});
})();`;

function secureHeaders(contentType: string): HeadersInit {
  return {"content-type": contentType, "cache-control": "no-store",
    "x-content-type-options": "nosniff", "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "content-security-policy": "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'"};
}
function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {status, headers: secureHeaders("application/json; charset=utf-8")});
}
function equal(a: string, b: string): boolean {
  const aa = new TextEncoder().encode(a); const bb = new TextEncoder().encode(b);
  let diff = aa.length ^ bb.length;
  for(let i = 0; i < Math.max(aa.length, bb.length); i++) diff |= (aa[i] || 0) ^ (bb[i] || 0);
  return diff === 0 && aa.length > 0;
}
function authorized(req: Request, secret: string): boolean {
  return Boolean(secret && equal(req.headers.get('authorization') || '', 'Bearer ' + secret));
}
function validStr(v: unknown, max: number, regex: RegExp): v is string {
  return typeof v === "string" && v.length > 0 && v.length <= max && regex.test(v);
}
function validate(body: unknown): Event | null {
  if(!body || typeof body !== 'object' || Array.isArray(body)) return null;
  const e = body as Record<string, unknown>;
  const keys = ["event_id","run_id","task_id","seq","time","stage","step","branch","base_sha","tool_count","result","elapsed_s","attempt"];
  if(Object.keys(e).sort().join(',') !== keys.slice().sort().join(',')) return null;
  if (!validStr(e.event_id,36,/^[a-f\d-]{36}$/i) || !validStr(e.run_id,36,/^[a-f\d-]{36}$/i) ||
      !validStr(e.task_id,48,/^[A-Z][A-Z0-9-]{2,48}$/) ||
      !Number.isSafeInteger(e.seq) || Number(e.seq)<1 || Number(e.seq)>1000000 ||
      !validStr(e.time,40,/^\d{4}-\d\d-\d\dT/) || !Number.isFinite(Date.parse(String(e.time))) ||
      typeof e.stage !== 'string' || !STAGES.has(e.stage) ||
      !validStr(e.step,80,/^[a-z0-9_]+$/) ||
      !validStr(e.branch,100,/^feature\/[a-zA-Z0-9_.\/-]+$/) ||
      !validStr(e.base_sha,40,/^[a-f\d]{40}$/i) ||
      !Number.isSafeInteger(e.tool_count) || Number(e.tool_count)<0 || Number(e.tool_count)>1000000 ||
      typeof e.result !== 'string' || e.result.length>100 ||
      !Number.isSafeInteger(e.elapsed_s) || Number(e.elapsed_s)<0 || Number(e.elapsed_s)>864000 ||
      !Number.isSafeInteger(e.attempt) || Number(e.attempt)<1 || Number(e.attempt)>100) return null;
  return e as unknown as Event;
}
async function postEvent(req: Request, env: Env): Promise<Response> {
  const contentLength = req.headers.get("content-length");
  if(contentLength && Number(contentLength)>MAX_BYTES)return json({error:"payload_too_large"},413);
  const text = await req.text();
  if(new TextEncoder().encode(text).length > MAX_BYTES) return json({error:'payload_too_large'}, 413);
  let parsed: unknown;
  try{parsed=JSON.parse(text)}catch{return json({error:'invalid_json'},400)}
  const e = validate(parsed);
  if(!e)return json({error:'invalid_event'},400);
  // Event ID + per-run sequence are idempotent, so retries won't duplicate timeline.
  await env.DB.prepare(`INSERT OR IGNORE INTO astra_events
     (event_id,run_id,task_id,seq,time,stage,step,tool_count,result,elapsed_s,attempt)
     VALUES (?,?,?,?,?,?,?,?,?,?,?)`).bind(e.event_id,e.run_id,e.task_id,e.seq,e.time,e.stage,e.step,e.tool_count,e.result,e.elapsed_s,e.attempt).run();
  // An out-of-order replay must not rewind the visible state.
  await env.DB.prepare(`INSERT INTO astra_runs
    (run_id,task_id,stage,step,branch,base_sha,tool_count,seq,result,elapsed_s,attempt,first_seen_at,last_seen_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(run_id) DO UPDATE SET
    stage=excluded.stage,step=excluded.step,tool_count=excluded.tool_count,seq=excluded.seq,
    result=excluded.result,elapsed_s=excluded.elapsed_s,attempt=excluded.attempt,last_seen_at=excluded.last_seen_at
    WHERE excluded.seq>astra_runs.seq`)
    .bind(e.run_id,e.task_id,e.stage,e.step,e.branch,e.base_sha,e.tool_count,e.seq,e.result,e.elapsed_s,e.attempt,e.time,e.time).run();
  return json({accepted:true},201);
}
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url); const path = url.pathname;
    if(path==='/' && request.method==='GET')return new Response(dashboard,{headers:secureHeaders('text/html; charset=utf-8')});
    if(path==='/app.js' && request.method==='GET')return new Response(appjs,{headers:secureHeaders('text/javascript; charset=utf-8')});
    if(path==='/api/health' && request.method==='GET')return json({ok:true,service:'astra-one-monitor'});
    if(!env.DB || !env.ASTRA_INGEST_TOKEN || !env.ASTRA_VIEW_TOKEN)return json({error:'not_configured'},503);
    if(path==='/api/events' && request.method==='POST'){
      if(!authorized(request,env.ASTRA_INGEST_TOKEN))return json({error:'unauthorized'},401);
      try{return await postEvent(request,env)}catch{return json({error:'database_error'},500)}
    }
    if(!authorized(request,env.ASTRA_VIEW_TOKEN))return json({error:'unauthorized'},401);
    try {
      if(path==='/api/summary' && request.method==='GET'){
        const stats=await env.DB.prepare(`SELECT r.stage, COUNT(*) AS count FROM astra_runs r WHERE r.run_id=(SELECT s.run_id FROM astra_runs s WHERE s.task_id=r.task_id ORDER BY s.last_seen_at DESC, s.run_id DESC LIMIT 1) GROUP BY r.stage`).all<{stage:string;count:number}>();
        const counts: Record<string,number>={total:0,queued:0,preflight:0,coding:0,verifying:0,awaiting_review:0,approved:0,completed:0,failed:0,stopped:0,interrupted:0};
        for(const r of stats.results||[]){counts[r.stage]=r.count;counts.total+=r.count}
        return json({counts});
      }
      if(path==='/api/runs' && request.method==='GET'){
        const rows=await env.DB.prepare('SELECT * FROM astra_runs ORDER BY last_seen_at DESC LIMIT 50').all();
        return json({runs:rows.results||[]});
      }
      if(path==='/api/events' && request.method==='GET'){
        const run=url.searchParams.get('run_id')||'';
        if(!/^[a-f\d-]{36}$/i.test(run))return json({error:'invalid_run_id'},400);
        const rows=await env.DB.prepare('SELECT seq,time,stage,step,tool_count,result,elapsed_s,attempt FROM astra_events WHERE run_id=? ORDER BY seq DESC LIMIT 100').bind(run).all();
        return json({events:(rows.results||[]).reverse()});
      }
    }catch{return json({error:'database_error'},500)}
    return json({error:'not_found'},404);
  }
};
