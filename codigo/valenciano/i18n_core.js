(function(){
const INL=new Set(['B','STRONG','I','EM','A','SMALL','SPAN','MARK','SUP','SUB','BR','ABBR','U','S','Q','TIME','WBR']);
const SKIP=new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','CODE','PRE']);
const norm=s=>s.replace(/\s+/g,' ').trim();
const hasL=s=>/[A-Za-zÀ-ÿ]{2,}/.test(s.replace(/<[^>]*>/g,' ').replace(/&[a-z]+;/g,' '));
const NUM=/[−\-+]?\d[\d.,]*/g;
function keyOf(s){ const nums=[]; let i=0; const k=norm(s).replace(NUM,m=>{ nums.push(m); return '{'+(i++)+'}'; }); return [k,nums]; }
function fill(t,nums){ return t.replace(/\{(\d+)\}/g,(m,i)=>nums[+i]!=null?nums[+i]:m); }
function isUnit(el){ if(el.querySelector('[data-notr]')) return false; let txt=false; for(const n of el.childNodes){ if(n.nodeType===3){ if(n.nodeValue.trim()) txt=true; } else if(n.nodeType===1){ if(!INL.has(n.tagName)) return false; if(n.querySelector('button,input,select,svg,textarea,img')) return false; if(n.tagName==='SPAN'&&n.childElementCount&&!txt) {} } }
  if(!txt) return false; return hasL(el.textContent); }
window.__I18N={INL,SKIP,norm,hasL,isUnit,keyOf,fill,NUM};
})();
