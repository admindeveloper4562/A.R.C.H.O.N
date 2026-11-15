"""Optional local-only task planner. Proposed plans are NEVER executable until imported."""
from __future__ import annotations

import json
from pathlib import Path
import re
import urllib.request

from .core import Store, validate_task

PLAN_TASKS_MAX = 6
PLAN_ARCH_MAX_CHARS = 18000


def focused_architecture(text:str, focus:str="") -> str:
    """Select a bounded section or refuse truncation; never silently omit requirements."""
    if len(text) <= PLAN_ARCH_MAX_CHARS and not focus:
        return text
    if not focus:
        raise ValueError("architecture exceeds planner context cap: specify --focus heading and plan by module")
    if len(focus) < 3 or len(focus)>120:
        raise ValueError("focus must be 3..120 characters")
    lines=text.splitlines(keepends=True)
    heads=[]
    for i,line in enumerate(lines):
        if re.match(r"^#{1,4}\s+",line) and focus.casefold() in line.casefold():
            heads.append(i)
    if not heads:
        raise ValueError("no Markdown section heading matches focus; edit architecture headings or use exact section")
    start=heads[0]
    level=len(re.match(r"^(#+)",lines[start]).group(1))
    end=len(lines)
    for i in range(start+1,len(lines)):
        match=re.match(r"^(#+)\s+",lines[i])
        if match and len(match.group(1))<=level:
            end=i;break
    selected=''.join(lines[start:end])
    if len(selected)>PLAN_ARCH_MAX_CHARS:
        raise ValueError("focused section too large; split the architecture section into smaller headings")
    return selected


def validate_plan(obj:object)->list[dict]:
    if not isinstance(obj,dict) or set(obj)!={"tasks"} or not isinstance(obj['tasks'],list) or not 1<=len(obj['tasks'])<=PLAN_TASKS_MAX:
        raise ValueError("planner output requires 1..6 tasks")
    result=[validate_task(x) for x in obj['tasks']]
    ids=[x['task_id'] for x in result]
    if len(set(ids))!=len(ids):
        raise ValueError("duplicate task IDs in plan")
    # Other dependencies must be defined before use, or already exist in queue
    for i,task in enumerate(result):
        if task['task_id'] in task['depends_on']:
            raise ValueError("self-dependency")
        if any(x in ids[i:] for x in task['depends_on']):
            raise ValueError("dependencies inside plan must be topologically ordered")
    return result


def propose(store:Store,focus:str="",count:int=4,model:str="qwen3:8b",output:Path|None=None)->dict:
    if not 1<=count<=PLAN_TASKS_MAX:
        raise ValueError("count must be 1..6")
    sha=store.config('approved_architecture_sha')
    if not sha or sha!=store.config('architecture_sha'):
        raise ValueError("final architecture must be approved before planning")
    doc=store.home/'private'/f'architecture-{sha[:16]}.md'
    text=focused_architecture(doc.read_text(encoding='utf-8'),focus)
    schema={"type":"object","additionalProperties":False,"required":["tasks"],"properties":{"tasks":{"type":"array","minItems":1,"maxItems":PLAN_TASKS_MAX,"items":{"type":"object","required":["task_id","objective","acceptance","depends_on","area"],"properties":{"task_id":{"type":"string"},"objective":{"type":"string"},"acceptance":{"type":"array","items":{"type":"string"}},"depends_on":{"type":"array","items":{"type":"string"}},"area":{"type":"string"}}}}}}
    payload={"model":model,"stream":False,"think":False,"format":schema,"options":{"temperature":0.2,"num_ctx":16384,"num_predict":2400},"messages":[{"role":"system","content":"You are Astra One, a local JARVIS v2 task planner. Return ONLY JSON matching schema. Propose SMALL sequential coding tasks for a human-approved plan. Do not assume code exists. Each task has explicit testable acceptance, no deployment, no remote access, no self-modification, no deletion, no credentials. Use unique ASTRA-xxx IDs and dependencies ordered before consumers. Do not claim work is done."},{"role":"user","content":f"Approved architecture SHA: {sha}\nFocus: {focus or 'selected full architecture'}\nPropose at most {count} tasks, prioritized small vertical slices.\nArchitecture:\\n{text}"}]}
    body=json.dumps(payload,ensure_ascii=False).encode('utf-8')
    request=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=body,headers={'content-type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=150) as response:
            value=json.load(response)
    except (OSError,ValueError) as exc:
        raise ValueError('local Ollama planner request failed; verify Ollama is running') from exc
    message=value.get('message',{})
    raw=message.get('content','')
    if not isinstance(raw,str) or len(raw)>70000:
        raise ValueError('planner response malformed or oversized')
    try:
        planned=validate_plan(json.loads(raw))
    except (ValueError,TypeError) as exc:
        raise ValueError('planner produced invalid task plan; nothing was enqueued') from exc
    path=output or store.home/'private'/f'proposed-plan-{sha[:8]}-{len(store.tasks())+1}.json'
    if path.exists():raise ValueError('proposed plan path exists; refusing overwrite')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump({"tasks":planned},f,indent=2,ensure_ascii=False)
        f.write('\n')
    return {"proposal_file":str(path),"tasks_proposed":len(planned),"enqueued":0,"engine":"not_started","architecture_sha":sha}
