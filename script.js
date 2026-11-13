/* ==========================================================================
   Smart Schedule Builder - app logic
   Sections: constants & helpers | storage | CSV | scheduling | UI | init
   ========================================================================== */
"use strict";

/* ---------- constants & helpers ---------- */
const DAYS=["M","T","W","R","F"],NAME={M:"Mon",T:"Tue",W:"Wed",R:"Thu",F:"Fri"};
const SAMPLE=`course,section,days,start,end
CSE 360,1,MW,10:30,11:45
CSE 360,2,TR,09:00,10:15
CSE 365,1,MW,11:00,12:15
CSE 365,2,TR,10:30,11:45
MAT 343,1,MW,13:00,14:15
MAT 343,2,TR,13:00,14:15`;
const $=id=>document.getElementById(id);
const tm=t=>{const[h,m]=t.split(":").map(Number);return h*60+m};
const f12=m=>{const h=Math.floor(m/60),mm=m%60;return`${(h%12)||12}:${String(mm).padStart(2,"0")} ${h<12?"AM":"PM"}`};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let catalog={},ranked=[],sel=0,order=[],prefs={};

/* ---------- storage (optional) ---------- */
const store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};

/* ---------- CSV ---------- */
function parseCSV(text){
  const errors=[],cat={};
  const lines=text.split(/\r?\n/).map(l=>l.trim()).filter(Boolean);
  if(!lines.length)return{cat,errors:["The CSV is empty."]};
  const cells=l=>l.split(",").map(c=>c.trim().replace(/^"|"$/g,""));
  const head=cells(lines[0]).map(h=>h.toLowerCase());
  const idx={};
  for(const k of["course","section","days","start","end"]){idx[k]=head.indexOf(k);if(idx[k]<0)errors.push(`Missing column: ${k}`)}
  if(errors.length)return{cat,errors};
  lines.slice(1).forEach((line,i)=>{
    const c=cells(line),n=i+2,r={};
    for(const k in idx)r[k]=c[idx[k]]||"";
    const t=/^([01]?\d|2[0-3]):[0-5]\d$/;
    if(!r.course){errors.push(`Row ${n}: course is blank`);return}
    if(!r.days||[...r.days.toUpperCase()].some(d=>!DAYS.includes(d))){errors.push(`Row ${n}: days must use only M T W R F`);return}
    if(!t.test(r.start)||!t.test(r.end)){errors.push(`Row ${n}: times must look like 09:30`);return}
    const s=tm(r.start),e=tm(r.end);
    if(e<=s){errors.push(`Row ${n}: end must be after start`);return}
    (cat[r.course]=cat[r.course]||[]).push({course:r.course,section:r.section,days:[...new Set(r.days.toUpperCase())].join(""),start:r.start,end:r.end,s,e});
  });
  return{cat,errors};
}

/* ---------- scheduling ---------- */
const conflict=(a,b)=>[...a.days].some(d=>b.days.includes(d))&&a.s<b.e&&b.s<a.e;
function generate(lists,limit=100000){
  const out=[],cur=[];let capped=false;
  const sorted=[...lists].sort((a,b)=>a.length-b.length);
  (function rec(i){
    if(capped)return;
    if(i===sorted.length){out.push(cur.slice());if(out.length>=limit)capped=true;return}
    for(const s of sorted[i]){if(cur.every(c=>!conflict(c,s))){cur.push(s);rec(i+1);cur.pop()}}
  })(0);
  return{out,capped};
}
const onDay=(sch,d)=>sch.filter(s=>s.days.includes(d)).sort((a,b)=>a.s-b.s);
function score(sch,p){
  const parts=[];let total=100;
  const add=(label,detail,pts,ok)=>{parts.push({label,detail,pts,ok});total-=pts};
  const early=sch.filter(s=>s.s<p.start),late=sch.filter(s=>s.e>p.end);
  add("Start time",early.length?`${early.length} class(es) before ${f12(p.start)}`:"Nothing before your earliest start",early.length*5,!early.length);
  add("Finish time",late.length?`${late.length} class(es) end after ${f12(p.end)}`:"Everything ends in time",late.length*5,!late.length);
  if(p.fri){const n=sch.filter(s=>s.days.includes("F")).length;add("Fridays",n?`${n} Friday class(es)`:"Fridays are free",n*10,!n)}
  let gapMin=0,gapPen=0;
  for(const d of DAYS){const ds=onDay(sch,d);for(let i=0;i<ds.length-1;i++){const g=ds[i+1].s-ds[i].e;if(g>0)gapMin+=g;
    if(g>120)gapPen+=12;else if(g>90)gapPen+=8;else if(g>60)gapPen+=5;else if(g>30)gapPen+=2}}
  add("Gaps between classes",gapMin?`${gapMin} min of waiting in total`:"No gaps",gapPen,gapPen<=2);
  const nd=DAYS.filter(d=>onDay(sch,d).length).length;
  add("Days on campus",`${nd} day(s)`,nd<=2?0:nd===3?3:nd===4?7:12,nd<=3);
  let over=0,worst=0;
  for(const d of DAYS){const n=onDay(sch,d).length;worst=Math.max(worst,n);if(n>p.max)over+=(n-p.max)*8}
  add("Daily load",`Busiest day: ${worst} class(es), limit ${p.max}`,over,!over);
  return{score:Math.max(0,Math.min(100,total)),parts,gapMin};
}

/* ---------- UI ---------- */
function renderCourses(checked){
  const box=$("courses");box.innerHTML="";
  Object.keys(catalog).forEach(c=>{
    const l=document.createElement("label");l.className="checkbox-row";
    l.innerHTML=`<input type="checkbox" value="${esc(c)}"><span>${esc(c)}</span><small>${catalog[c].length} section(s)</small>`;
    l.querySelector("input").checked=checked?checked.includes(c):true;
    l.querySelector("input").addEventListener("change",updateCombos);
    box.appendChild(l);
  });
  updateCombos();
}
const chosen=()=>[...document.querySelectorAll("#courses input:checked")].map(i=>i.value);
function updateCombos(){
  const c=chosen();const n=c.reduce((a,k)=>a*catalog[k].length,1);
  $("combos").textContent=c.length?`${c.length} course(s), up to ${n.toLocaleString()} section combinations to check.`:"Select at least one course.";
  $("go").disabled=!c.length;
}
function readPrefs(){
  const max=Math.max(1,parseInt($("pMax").value,10)||3);
  return{start:tm($("pStart").value||"09:00"),end:tm($("pEnd").value||"16:00"),fri:$("pFri").checked,max};
}
function blockedPairs(names){
  const bad=[];
  for(let i=0;i<names.length;i++)for(let j=i+1;j<names.length;j++){
    const ok=catalog[names[i]].some(a=>catalog[names[j]].some(b=>!conflict(a,b)));
    if(!ok)bad.push(`${names[i]} and ${names[j]}`);
  }
  return bad;
}
function build(){
  const names=chosen();order=names;
  prefs=readPrefs();
  store.set("ssb",JSON.stringify({csv:$("csv").value,names,pStart:$("pStart").value,pEnd:$("pEnd").value,fri:prefs.fri,max:prefs.max}));
  const {out,capped}=generate(names.map(n=>catalog[n]));
  const out$=$("out");
  if(!out.length){
    const bad=blockedPairs(names);
    out$.innerHTML=`<div class="panel empty-state"><h2>No conflict-free schedule exists</h2><p>${bad.length?`Every section of ${bad.map(esc).join("; ")} overlaps.`:"Three or more of these courses clash in every combination."} Try dropping one course or adding another section.</p></div>`;
    return;
  }
  ranked=out.map(s=>({sch:s,...score(s,prefs)})).sort((a,b)=>b.score-a.score||a.gapMin-b.gapMin);
  sel=0;draw(out.length,capped);
}
function draw(total,capped){
  const top=ranked.slice(0,8),r=ranked[sel];
  const o=$("out");
  o.innerHTML=`<div class="panel results-panel">
    <p class="hint">${total.toLocaleString()} valid schedule(s) found${capped?" (stopped at the 100,000 limit)":""}. Showing the best ${top.length}.</p>
    <div class="option-tabs no-print" role="group" aria-label="Schedule options">${top.map((t,i)=>`<button class="option-tab" data-i="${i}" aria-pressed="${i===sel}">Option ${i+1}: ${t.score}</button>`).join("")}</div>
    <div class="result-header"><div class="score">${r.score}<small>/100</small></div>
      <div><h2>${sel===0?"Best match for your preferences":`Option ${sel+1}`}</h2><p class="hint">${r.parts.filter(p=>!p.ok).length?"Trade-offs are listed below.":"No trade-offs: this one hits every preference."}</p></div>
      <div class="result-actions no-print"><button id="copy">Copy</button><button id="print">Print</button></div></div>
    ${grid(r.sch)}
    <div class="two-column">
      <div><h3>Why this score</h3><ul class="plain-list analysis-list">${r.parts.map(p=>`<li><span class="${p.ok?"is-ok":"is-warning"}" aria-hidden="true">${p.ok?"✓":"!"}</span><span><b>${p.label}</b><br><span class="hint">${esc(p.detail)}</span></span><span class="points">${p.pts?"−"+p.pts:"0"}</span></li>`).join("")}</ul></div>
      <div><h3>Sections to register</h3><ul class="plain-list sections-list">${[...r.sch].sort((a,b)=>order.indexOf(a.course)-order.indexOf(b.course)).map(s=>`<li><b>${esc(s.course)}</b> section ${esc(s.section)}<br><span class="hint">${s.days.split("").map(d=>NAME[d]).join(", ")}, ${f12(s.s)} to ${f12(s.e)}</span></li>`).join("")}</ul></div>
    </div></div>`;
  o.querySelectorAll(".option-tab").forEach(b=>b.onclick=()=>{sel=+b.dataset.i;draw(total,capped)});
  $("copy").onclick=copyText;$("print").onclick=()=>window.print();
}
function grid(sch){
  const H=54;
  const lo=Math.floor((Math.min(...sch.map(s=>s.s))-30)/60)*60,hi=Math.ceil((Math.max(...sch.map(s=>s.e))+30)/60)*60;
  const h=(hi-lo)/60*H;
  let ticks="";for(let m=lo;m<=hi;m+=60)ticks+=`<span style="top:${(m-lo)/60*H}px">${f12(m).replace(":00","")}</span>`;
  const cols=DAYS.map(d=>`<div class="grid-day" style="--hour-height:${H}px;height:${h}px">${onDay(sch,d).map(s=>{
    const hue=(order.indexOf(s.course)*67+222)%360;
    return`<div class="class-block" style="--hue:${hue};top:${(s.s-lo)/60*H}px;height:${(s.e-s.s)/60*H-2}px"><b>${esc(s.course)}</b>Sec ${esc(s.section)}<br>${f12(s.s)}</div>`}).join("")}</div>`).join("");
  return`<div class="grid-scroll"><div class="week-grid"><div class="grid-header"></div>${DAYS.map(d=>`<div class="grid-header">${NAME[d]}</div>`).join("")}<div class="grid-times" style="height:${h}px">${ticks}</div>${cols}</div></div>`;
}
function copyText(){
  const r=ranked[sel];
  const t=`My schedule (score ${r.score}/100)\n`+r.sch.map(s=>`${s.course} section ${s.section}: ${s.days} ${s.start}-${s.end}`).join("\n");
  const done=()=>{$("copy").textContent="Copied"};
  const fb=()=>{const a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy");done()}catch(e){$("copy").textContent="Copy blocked"}a.remove()};
  try{navigator.clipboard.writeText(t).then(done,fb)}catch(e){fb()}
}
function loadCSV(text,checked){
  const {cat,errors}=parseCSV(text);
  $("csvErr").textContent=errors.slice(0,6).join("\n")+(errors.length>6?`\n…and ${errors.length-6} more`:"");
  if(!Object.keys(cat).length)return false;
  catalog=cat;$("csv").value=text;renderCourses(checked);
  $("out").innerHTML='<div class="panel empty-state">Choose your courses and press <b>Build schedules</b>.</div>';
  return true;
}
$("go").onclick=build;
$("load").onclick=()=>loadCSV($("csv").value);
$("reset").onclick=()=>{$("csv").value=SAMPLE;loadCSV(SAMPLE)};
$("file").onchange=e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=()=>loadCSV(String(r.result));r.readAsText(f)};
/* ---------- init ---------- */
(function(){
  let s=null;try{s=JSON.parse(store.get("ssb"))}catch(e){}
  if(s&&typeof s.csv==="string"&&loadCSV(s.csv,Array.isArray(s.names)?s.names:undefined)){
    if(s.pStart)$("pStart").value=s.pStart;if(s.pEnd)$("pEnd").value=s.pEnd;$("pFri").checked=!!s.fri;if(s.max)$("pMax").value=s.max;
  }else loadCSV(SAMPLE);
})();
