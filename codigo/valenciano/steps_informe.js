module.exports=async p=>{
 // fichas de cifras, figuras y casos
 const n=await p.evaluate(()=>document.querySelectorAll('button[data-li]').length);
 for(let i=0;i<n;i++){ await p.evaluate(i=>{ document.querySelectorAll('button[data-li]')[i].click(); __harv(document.getElementById('det')); document.getElementById('detX').click(); },i); }
 const fb=await p.evaluate(()=>[...document.querySelectorAll('figure .t button')].length);
 for(let i=0;i<fb;i++){ await p.evaluate(i=>{ const b=[...document.querySelectorAll('figure .t button')][i]; b.click(); __harv(document.getElementById('det')); document.getElementById('detX').click(); },i); }
 await p.evaluate(()=>{ document.querySelectorAll('#casos button[data-case]').forEach(b=>{ b.click(); __harv(document.getElementById('det')); document.getElementById('detX').click(); }); });
 // tablas de gráficos
 await p.evaluate(()=>{ document.querySelectorAll('.dtools button[data-act=tab]').forEach(b=>{ b.click(); }); document.querySelectorAll('.dtab').forEach(t=>__harv(t)); });
 // explorador: combinaciones
 await p.evaluate(async()=>{ const sx=document.getElementById('exX'), sy=document.getElementById('exY'), m=document.getElementById('exMode'); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  for(const mode of ['t','d']){ m.value=mode; m.dispatchEvent(new Event('change')); await sleep(50); const xs=[...sx.options].map(o=>o.value);
   for(let i=0;i<xs.length;i++){ for(let j=0;j<xs.length;j+=Math.max(1,Math.floor(xs.length/6))){ if(i===j) continue; sx.value=xs[i]; sy.value=xs[j]; sx.dispatchEvent(new Event('change')); __harv(document.getElementById('explorador')); } } } });
};
