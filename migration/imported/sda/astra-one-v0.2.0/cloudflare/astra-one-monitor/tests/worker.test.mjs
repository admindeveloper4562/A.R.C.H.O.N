import { test } from 'node:test';
import assert from 'node:assert/strict';
import worker from '../.test-output/index.js';

class MockDB {
  constructor(){ this.events=[]; this.runs=[]; }
  prepare(sql){
    const db=this;
    return {
      bind(...params){this.params=params;return this;},
      async run(){
        const p=this.params||[];
        if(sql.includes('INSERT OR IGNORE INTO astra_events')){
          if(!db.events.some(e=>e.event_id===p[0] || (e.run_id===p[1]&&e.seq===p[3]))) db.events.push({event_id:p[0],run_id:p[1],task_id:p[2],seq:p[3],time:p[4],stage:p[5],step:p[6],tool_count:p[7],result:p[8],elapsed_s:p[9],attempt:p[10]});
        }else if(sql.includes('INSERT INTO astra_runs')){
          const value={run_id:p[0],task_id:p[1],stage:p[2],step:p[3],branch:p[4],base_sha:p[5],tool_count:p[6],seq:p[7],result:p[8],elapsed_s:p[9],attempt:p[10],first_seen_at:p[11],last_seen_at:p[12]};
          const existing=db.runs.find(r=>r.run_id===value.run_id);
          if(existing){if(value.seq>existing.seq)Object.assign(existing,value)}else{db.runs.push(value)}
        }else throw Error('unexpected SQL '+sql);
        return {};
      },
      async all(){
        if(sql.includes('SELECT r.stage')){
          const latest=new Map(); for(const r of db.runs){const old=latest.get(r.task_id); if(!old||r.last_seen_at>old.last_seen_at)latest.set(r.task_id,r)}
          const totals={};for(const row of latest.values()) totals[row.stage]=(totals[row.stage]||0)+1;
          return {results:Object.entries(totals).map(([stage,count])=>({stage,count}))};
        }
        if(sql.includes('SELECT * FROM astra_runs'))return {results:db.runs.slice().reverse()};
        if(sql.includes('FROM astra_events WHERE run_id'))return {results:db.events.filter(e=>e.run_id===this.params[0]).sort((a,b)=>b.seq-a.seq).slice(0,100)};
        throw Error('unexpected SQL SELECT '+sql);
      }
    };
  }
}
const env={DB:new MockDB(),ASTRA_INGEST_TOKEN:'private-ingest',ASTRA_VIEW_TOKEN:'private-view'};
const uuid=()=> '123e4567-e89b-42d3-a456-426614174000';
const message=(seq,stage)=>({event_id:seq===1?uuid():'123e4567-e89b-42d3-a456-426614174001',run_id:'123e4567-e89b-42d3-a456-426614174999',task_id:'ASTRA-101',seq,time:'2026-11-13T10:00:00+00:00',stage,step:'test_event',branch:'feature/astra-test',base_sha:'a'.repeat(40),tool_count:seq,result:'',elapsed_s:seq*10,attempt:1});
async function call(path,method='GET',body=null,token=''){
  const req=new Request('https://example.workers.dev'+path,{method,headers:{...(token?{authorization:'Bearer '+token}:{}),...(body?{'content-type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const res=await worker.fetch(req,env);
  const text=await res.text();
  return {status:res.status,body:text,headers:res.headers};
}
test('browser assets and CSP are served but task data is gated',async()=>{
  const r=await call('/');assert.equal(r.status,200);assert.match(r.body,/ASTRA ONE/);assert.equal(r.headers.get('x-frame-options'),'DENY');
  const js=await call('/app.js');assert.equal(js.status,200);new Function(js.body);
  assert.equal((await call('/api/runs')).status,401);
});
test('ingest token is distinct from view token',async()=>{
  assert.equal((await call('/api/events','POST',message(1,'coding'),'private-view')).status,401);
  assert.equal((await call('/api/runs','GET',null,'private-ingest')).status,401);
  assert.equal((await call('/api/events','POST',message(1,'coding'),'private-ingest')).status,201);
});
test('idempotent replay and no state rewind',async()=>{
  await call('/api/events','POST',message(2,'awaiting_review'),'private-ingest');
  await call('/api/events','POST',message(1,'coding'),'private-ingest');
  const result=await call('/api/runs','GET',null,'private-view');
  const data=JSON.parse(result.body);
  assert.equal(data.runs.length,1);
  assert.equal(data.runs[0].stage,'awaiting_review');
  const timeLine=await call('/api/events?run_id='+message(1,'coding').run_id,'GET',null,'private-view');
  assert.equal(JSON.parse(timeLine.body).events.length,2);
});
test('invalid event rejected and read APIs require authentication',async()=>{
  assert.equal((await call('/api/events','POST',{bad:'key'},'private-ingest')).status,400);
  assert.equal((await call('/api/events?run_id=not-a-uuid','GET',null,'private-view')).status,400);
  const stats=await call('/api/summary','GET',null,'private-view');
  assert.equal(JSON.parse(stats.body).counts.total,1);
});
