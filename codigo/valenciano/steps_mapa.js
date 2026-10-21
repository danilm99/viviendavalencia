module.exports=async p=>{
 const errs=await p.evaluate(()=>document.querySelectorAll('.leaflet-container').length); console.log('leaflet',errs);
 await p.evaluate(()=>{ const d=document.getElementById('data'); document.getElementById('tabData').click(); __harv(document.documentElement); });
 // menú, ficha de un piso, búsqueda
 await p.evaluate(()=>{ document.getElementById('menuBtn').click(); __harv(document.getElementById('menu')); document.getElementById('menuClose').click(); document.getElementById('tabMap').click(); });
 await p.evaluate(async()=>{ const q=document.getElementById('q'); q.value='russafa'; q.dispatchEvent(new Event('input')); await new Promise(r=>setTimeout(r,400)); __harv(document.getElementById('results')); const rs=[...document.querySelectorAll('#results .res')]; for(let i=0;i<Math.min(rs.length,25);i++){ const all=[...document.querySelectorAll('#results .res')]; if(!all[i]) break; all[i].click(); __harv(document.getElementById('sheet')); q.dispatchEvent(new Event('input')); await new Promise(r=>setTimeout(r,250)); } });
 await p.evaluate(async()=>{ for(const t of ['valencia','vt-','apartment','loft','sl']){ const q=document.getElementById('q'); q.value=t; q.dispatchEvent(new Event('input')); await new Promise(r=>setTimeout(r,300)); const all=[...document.querySelectorAll('#results .res')]; for(let i=0;i<Math.min(all.length,8);i++){ const a=[...document.querySelectorAll('#results .res')]; if(!a[i]) break; a[i].click(); __harv(document.getElementById('sheet')); q.dispatchEvent(new Event('input')); await new Promise(r=>setTimeout(r,200)); } } });
 await p.evaluate(()=>{ document.querySelectorAll('#barrioMode button,#priceMode button').forEach(b=>{ b.click(); __harv(document.getElementById('data')); }); });
};
