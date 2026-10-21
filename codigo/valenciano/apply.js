(function(){ if(window.LANG!=='va'||!window.VA_DICT) return; const D=window.VA_DICT;
const INL=new Set(['B','STRONG','I','EM','A','SMALL','SPAN','MARK','SUP','SUB','BR','ABBR','U','S','Q','TIME','WBR']);
const SKIP=new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','CODE','PRE']);
const norm=s=>s.replace(/\s+/g,' ').trim(); const NUM=/[−\-+]?\d[\d.,]*/g;
const hasL=s=>/[A-Za-zÀ-ÿ]{2,}/.test(s.replace(/<[^>]*>/g,' ').replace(/&[a-z]+;/g,' '));
function keyOf(s){ const nums=[]; let i=0; const k=norm(s).replace(NUM,m=>{ nums.push(m); return '{'+(i++)+'}'; }); return [k,nums]; }
const fill=(t,nums)=>t.replace(/\{(\d+)\}/g,(m,i)=>nums[+i]!=null?nums[+i]:m);
function look(s){ if(!s||!hasL(s)) return null; const [k,nums]=keyOf(s); const t=D[k]; return t==null?null:fill(t,nums); }
window.tr=function(s){ const t=look(s); return t==null?s:t; };
const DONE=new WeakSet(), VALS=new Set(Object.values(D).map(norm));
function isUnit(el){ if(el.querySelector('[data-notr]')) return false; let txt=false; for(const n of el.childNodes){ if(n.nodeType===3){ if(n.nodeValue.trim()) txt=true; } else if(n.nodeType===1){ if(!INL.has(n.tagName)) return false; if(n.querySelector('button,input,select,svg,textarea,img')) return false; } } return txt&&hasL(el.textContent); }
function attrs(el){ for(const a of ['title','aria-label','placeholder','alt']){ const v=el.getAttribute&&el.getAttribute(a); if(v){ const t=look(v); if(t!=null&&t!==v) el.setAttribute(a,t); } } }
function walk(el){ if(el.nodeType!==1||SKIP.has(el.tagName)||el.hasAttribute('data-notr')) return; attrs(el);
  if(el.tagName==='OPTION'){ const t=look(el.textContent); if(t!=null) el.textContent=t; return; }
  if(isUnit(el)){ if(DONE.has(el)&&VALS.has(norm(el.innerHTML))) return; const t=look(el.innerHTML); if(t!=null&&t!==el.innerHTML){ el.innerHTML=t; } DONE.add(el); return; }
  for(const n of [...el.childNodes]){ if(n.nodeType===3){ const v=n.nodeValue; if(!v.trim()) continue; const t=look(v); if(t!=null){ const lead=v.match(/^\s*/)[0], trail=v.match(/\s*$/)[0]; const nv=lead+t+trail; if(nv!==v) n.nodeValue=nv; } } else if(n.nodeType===1) walk(n); } }
const doc=()=>{ walk(document.body); const t=look(document.title); if(t) document.title=t; document.querySelectorAll('meta[name=description],meta[property="og:description"],meta[property="og:title"]').forEach(m=>{ const x=look(m.content); if(x) m.content=x; }); };
doc(); let busy=false;
const mo=new MutationObserver(ms=>{ if(busy) return; busy=true; try{ for(const m of ms){ if(m.type==='childList') m.addedNodes.forEach(n=>{ if(n.nodeType===1) walk(n); else if(n.nodeType===3&&n.parentElement) walk(n.parentElement); }); else if(m.type==='characterData'&&m.target.parentElement) walk(m.target.parentElement); } } finally { busy=false; } });
mo.observe(document.body,{childList:true,subtree:true,characterData:true});
})();
