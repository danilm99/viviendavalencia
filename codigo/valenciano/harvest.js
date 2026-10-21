const { chromium } = require('playwright');const path=require('path'),fs=require('fs');
const css=fs.readFileSync(path.join(__dirname,'../story/fonts.css'),'utf8'); const core=fs.readFileSync(path.join(__dirname,'i18n_core.js'),'utf8');
const [,,page,out,extraJs]=process.argv;
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:1280,height:900}});
 await c.route('**/*',r=>{const u=r.request().url(); if(u.includes('fonts.googleapis'))return r.fulfill({body:css,contentType:'text/css'}); const lib={'leaflet.min.js':'leaflet/dist/leaflet.js','leaflet.min.css':'leaflet/dist/leaflet.css','leaflet.markercluster.min.js':'leaflet.markercluster/dist/leaflet.markercluster.js','MarkerCluster.css':'leaflet.markercluster/dist/MarkerCluster.css','MarkerCluster.Default.css':'leaflet.markercluster/dist/MarkerCluster.Default.css','MarkerCluster.Default.min.css':'leaflet.markercluster/dist/MarkerCluster.Default.css','MarkerCluster.min.css':'leaflet.markercluster/dist/MarkerCluster.css','papaparse.min.js':'papaparse/papaparse.min.js'}; for(const [k,v] of Object.entries(lib)) if(u.includes('cdnjs')&&u.endsWith(k)) return r.fulfill({path:path.join(__dirname,'node_modules',v)}); if(u.startsWith('file:'))return r.continue(); return r.abort();});
 const p=await c.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(page)); await p.waitForTimeout(1500); await p.addScriptTag({content:core}); if(process.env.NOSEL) await p.evaluate(s=>window.__NOSEL=s,process.env.NOSEL);
 await p.evaluate(()=>{ const {norm,hasL,isUnit,SKIP}=__I18N; window.__U=new Map(); window.__T=new Map(); window.__A=new Map();
  const NOSEL=window.__NOSEL||''; window.__harv=(root)=>{ const walk=el=>{ if(SKIP.has(el.tagName)) return; if(NOSEL&&el.matches&&el.matches(NOSEL)) return; for(const a of ['title','aria-label','placeholder','alt','content']){ const v=el.getAttribute&&el.getAttribute(a); if(v&&hasL(v)&&(a!=='content'||el.tagName==='META')) __A.set(norm(v),(__A.get(norm(v))||0)+1); }
    if(el.tagName==='OPTION'){ const t=norm(el.textContent); if(hasL(t)) __U.set(t,'opt'); return; }
    if(isUnit(el)){ const k=norm(el.innerHTML); __U.set(k,el.tagName); return; }
    for(const n of el.childNodes){ if(n.nodeType===3){ const t=norm(n.nodeValue); if(hasL(t)) __T.set(t,(__T.get(t)||0)+1); } else if(n.nodeType===1) walk(n); } };
   walk(root); };
  __harv(document.documentElement); __A.set(norm(document.title),1); });
 if(extraJs){ const steps=require(path.resolve(extraJs)); await steps(p); }
 const r=await p.evaluate(()=>{ const K=new Map(); const add=(s,kind)=>{ const [k]=__I18N.keyOf(s); if(__I18N.hasL(k)&&!K.has(k)) K.set(k,kind); }; for(const [k,t] of __U) add(k,t==='opt'?'text':'html'); for(const k of __T.keys()) add(k,'text'); for(const k of __A.keys()) add(k,'text'); return {keys:[...K.entries()]}; });
 fs.writeFileSync(out,JSON.stringify(r,null,0)); console.log('claves',r.keys.length,'errores',errs.slice(0,3)); await b.close(); })();
