// Extrae del informe ya generado las cifras clave (HTML de cada ficha) para la portada. Uso: node extract_kpis.js informe.html salida.json
let pw; try { pw = require('playwright'); } catch (e) { pw = require('playwright-core'); }
const fs = require('fs'), path = require('path');
const [, , html, out] = process.argv;
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(html)); await p.waitForFunction(() => window.__LI && document.querySelectorAll('#kpis button').length > 5, null, { timeout: 30000 });
  const r = await p.evaluate(() => ({
    kpis: [...document.querySelectorAll('#kpis button')].map(b => ({ cls: b.className, inner: b.innerHTML, key: window.__LI[+b.dataset.li][4] })),
    legend: (document.querySelector('#claves .klegend') || {}).outerHTML || ''
  }));
  if (errs.length) console.log('errores en el informe:', errs);
  fs.writeFileSync(out, JSON.stringify(r)); console.log('cifras clave', r.kpis.length); await b.close();
})();
