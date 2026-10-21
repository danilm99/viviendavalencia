# Genera la portada (index.html): presentación, accesos a las secciones, «En un minuto» y cifras clave.
# Las cifras clave se extraen del informe ya generado (extract_kpis.js, necesita Node y Playwright),
# así la portada y el informe muestran siempre las mismas cifras.
import json, re, os, sys, html, pathlib, subprocess, datetime
ROOT = pathlib.Path(__file__).parent
SITE = ROOT.parent
sys.path.insert(0, str(ROOT))
from sitebar import bar

INF = SITE / "informe-vivienda-valencia.html"
OUT = SITE / "index.html"
KJ = ROOT / "kpis_portada.json"
env = dict(os.environ)
for nm in [ROOT / "node_modules", pathlib.Path("/tmp/claude-0/-home-claude/71b84656-6dc8-5a74-99a5-b596aab2a40b/scratchpad/story/node_modules")]:
    if nm.exists():
        env["NODE_PATH"] = str(nm) + (os.pathsep + env["NODE_PATH"] if env.get("NODE_PATH") else "")
subprocess.run(["node", str(ROOT / "extract_kpis.js"), str(INF), str(KJ)], check=True, env=env)
K = json.load(open(KJ, encoding="utf-8"))
D = json.load(open(ROOT / "data.json", encoding="utf-8"))
head_tpl = open(ROOT / "tpl/01_head.html", encoding="utf-8").read()
base_css = head_tpl.split("<style>", 1)[1].split("/* otras ciudades */", 1)[0]
extra_css = head_tpl.split("/* tipo de dato y herramientas de datos */", 1)[1].split("</style>", 1)[0]
apply_js = next(p for p in [ROOT.parent / "valenciano/apply.js", ROOT.parent / "codigo/valenciano/apply.js", ROOT / "apply.js",
                            pathlib.Path("/tmp/claude-0/-home-claude/71b84656-6dc8-5a74-99a5-b596aab2a40b/scratchpad/i18n/apply.js")] if p.exists()).read_text(encoding="utf-8")

MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
up = datetime.date.fromisoformat(D.get("updated", "2026-10-19"))
fecha = f"{MESES[up.month - 1]} de {up.year}"
n_airbnb = f'{D["turistico"]["airbnb_2026"]:,}'.replace(",", ".")

# «En un minuto», tomado de la plantilla del informe con los enlaces apuntando al informe
body_tpl = open(ROOT / "tpl/02_body.html", encoding="utf-8").read()
ol = re.search(r'<section id="minuto"[^>]*>.*?(<ol>.*?</ol>)', body_tpl, re.S).group(1)
ol = re.sub(r'href="#([\w-]+)"', r'href="informe-vivienda-valencia.html#\1"', ol)

tiles = "".join(
    f'<a class="{html.escape(k["cls"])}" href="informe-vivienda-valencia.html#ficha={html.escape(k["key"])}">{k["inner"]}</a>'
    for k in K["kpis"])

CARDS = [
    ("informe-vivienda-valencia.html", "Informe completo", "Precios, rentas, hogares, propietarios, pisos turísticos, vivienda pública y gasto, con una ficha de fuente detrás de cada cifra y un explorador para cruzar indicadores.", "a"),
    ("pisos-turisticos-valencia.html", "Mapa de pisos turísticos", f"Los {n_airbnb} anuncios de Airbnb de la ciudad, uno a uno, con su registro y su anfitrión, y el peso del alquiler turístico en cada barrio.", "b"),
    ("elecciones-29n.html", "Elecciones del 29-N", "Qué dicen los partidos sobre vivienda, qué decide cada administración y qué hizo cada partido cuando gobernó.", "c"),
    ("https://github.com/danilm99/viviendavalencia", "Datos y código abiertos", "Todo el código y los datos de la web, con licencia libre, para comprobar de dónde sale cada cifra o reutilizarlos.", "d"),
]
cards = "".join(
    f'<a class="sec sec-{c}" href="{h}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}><b>{html.escape(t)}</b><span>{html.escape(d)}</span><i aria-hidden="true">→</i></a>'
    for h, t, d, c in CARDS)

CSS = """
/* portada */
.land{max-width:1040px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-right,0px)) 70px max(16px,env(safe-area-inset-left,0px))}
.land header{padding:56px 0 18px}
.land .kick{font:600 12.5px/1 var(--body);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 14px}
.land h1{margin:0 0 22px;max-width:none;font-size:inherit;line-height:1}
.land h1 .logo{display:inline-block;font:800 clamp(29px,9.6vw,96px)/1 var(--display);font-variation-settings:"wdth" 85;font-stretch:85%;letter-spacing:-.02em;background:var(--mark);color:var(--mark-ink);padding:.2em .26em .13em;white-space:nowrap}
.land .dek{font-size:clamp(19px,2.2vw,24px);line-height:1.38;max-width:34ch;margin:0 0 12px}
.land .sub2{font-size:15px;color:var(--muted);max-width:62ch;margin:0}
.secs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:28px 0 8px}
@media (max-width:980px){.secs{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.secs{grid-template-columns:1fr}}
.sec{--kc:var(--fg);position:relative;display:flex;flex-direction:column;gap:8px;background:var(--panel);border:1px solid var(--line);border-top:5px solid var(--kc);padding:16px 16px 44px;text-decoration:none;color:var(--fg);min-height:170px}
.sec:hover,.sec:focus-visible{background:var(--mark-soft)}
.sec b{font:800 22px/1.08 var(--display);letter-spacing:-.015em}
.sec span{font-size:14.5px;line-height:1.42;color:var(--muted)}
.sec i{position:absolute;left:16px;bottom:12px;font:800 22px/1 var(--display);font-style:normal;color:var(--kc)}
.sec-a{--kc:var(--mark)}.sec-a i{color:var(--fg)}.sec-b{--kc:var(--s2)}.sec-c{--kc:var(--s1)}.sec-d{--kc:var(--s3)}
@media (max-width:560px){.sec{min-height:0;padding:14px 14px 14px 14px}.sec i{position:static;align-self:flex-end;margin-top:-26px}}
.land section{padding:40px 0 6px}
.land section+section{border-top:3px solid var(--rule)}
.land .minuto ol{max-width:78ch}
.ledger a{--kc:var(--s1);position:relative;display:flex;flex-direction:column;gap:4px;width:100%;text-align:left;background:var(--panel);border:1px solid var(--line);border-top:4px solid var(--kc);padding:12px 14px 12px;color:inherit;text-decoration:none;min-height:118px}
.ledger a:hover,.ledger a:focus-visible{background:var(--mark-soft);border-color:var(--kc)}
.ledger a .ic{position:absolute;top:12px;right:12px;width:24px;height:24px;color:var(--kc);opacity:.9}
.ledger a .ic svg{width:100%;height:100%;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.ledger a.w{--kc:var(--s2)}.ledger a.g{--kc:var(--s3)}.ledger a.a{--kc:var(--s5)}.ledger a.n{--kc:var(--fg)}
.ledger a em.tyk{font-style:normal;font-size:10.5px;color:var(--muted);margin-top:auto;padding-top:4px;letter-spacing:.02em}
@media (max-width:640px){.land header{padding:30px 0 8px}.ledger a{padding:10px 10px 10px;min-height:0}.ledger a .ic{top:10px;right:8px;width:20px;height:20px}}
.more{display:inline-block;margin:14px 0 0;font-weight:600}
.land .about{font-size:15px;color:var(--muted);max-width:70ch}
"""

HEAD = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<script>(function(){{ var L=null; try{{ var q=new URLSearchParams(location.search).get('lang'); if(q==='va'||q==='es'){{ L=q; localStorage.setItem('vv.lang',q); }} else L=localStorage.getItem('vv.lang'); }}catch(e){{}} window.LANG=L==='va'?'va':'es'; window.T=function(es,va){{ return window.LANG==='va'&&va!=null?va:es; }}; window.tr=function(s){{ return s; }}; if(window.LANG==='va'){{ document.documentElement.lang='ca-ES-valencia'; document.write('<script src="va-inicio.js"><\\/script>'); }} }})();</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>viviendavalencia.info · Datos sobre la vivienda en València</title>
<meta name="description" content="Plataforma de código abierto para acercar a la ciudadanía los datos sobre la vivienda en València: informe con la fuente de cada cifra, mapa de pisos turísticos y qué dicen los partidos ante las elecciones del 29-N.">
<meta property="og:title" content="viviendavalencia.info">
<meta property="og:description" content="Plataforma de código abierto para acercar a la ciudadanía los datos sobre la vivienda en València.">
<meta property="og:type" content="website">
<meta property="og:image" content="https://viviendavalencia.info/og-inicio.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="https://viviendavalencia.info/">
<meta property="og:site_name" content="viviendavalencia.info">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://viviendavalencia.info/og-inicio.jpg">
<link rel="canonical" href="https://viviendavalencia.info/">
<meta name="robots" content="index,follow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>{base_css}{extra_css}{CSS}</style>
<script>window.goatcounter={{path:function(){{return location.pathname||"/"}}}}</script><script data-goatcounter="https://viviendavalencia.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</head>
"""

BODY = f"""<body>
{bar("inicio")}<main class="land" id="top">
<header>
  <p class="kick">Datos a {fecha}</p>
  <h1><span class="logo">viviendavalencia.info</span></h1>
  <p class="dek">Plataforma de código abierto para acercar a la ciudadanía los datos sobre la vivienda en València.</p>
  <p class="sub2">Estadísticas oficiales, registros públicos y estudios, con la fuente de cada cifra. Sin publicidad, sin cookies y sin afiliación a ningún partido.</p>
  <nav class="secs" aria-label="Secciones">{cards}</nav>
</header>

<section id="minuto" class="minuto">
  <h2>En un minuto</h2>
  {ol}
</section>

<section id="claves">
  <h2>Las cifras que resumen la década</h2>
  <div class="ledger" id="kpis">{tiles}</div>
  {K["legend"]}
  <p class="sub">Cada cifra abre su ficha en el informe: qué mide, cómo se calcula y de dónde sale.</p>
  <a class="more" href="informe-vivienda-valencia.html">Ir al informe completo →</a>
</section>

<section id="sobre">
  <h2>Sobre esta web</h2>
  <p class="about">viviendavalencia.info es una web informativa e independiente. Reúne datos públicos sobre la vivienda en la ciudad y los presenta con su fuente para que cualquiera pueda comprobarlos. Las visitas se cuentan de forma anónima con GoatCounter, sin cookies. Si encuentras un error, abre una incidencia en el <a href="https://github.com/danilm99/viviendavalencia" target="_blank" rel="noopener">repositorio</a>: las correcciones se publican con su fecha.</p>
  <a class="more" href="informe-vivienda-valencia.html#sobre">Método, fuentes y registro de cambios →</a>
</section>
</main>
<script>(function(){{ document.querySelectorAll('a.langsw').forEach(function(a){{ var va=window.LANG==='va'; a.textContent=va?'Castellano':'Valencià'; a.setAttribute('lang',va?'es':'ca-ES-valencia'); a.setAttribute('href','?lang='+(va?'es':'va')); a.addEventListener('click',function(e){{ e.preventDefault(); location.href=location.pathname+'?lang='+(va?'es':'va')+location.hash; }}); }}); }})();</script>
<script>{apply_js}</script>
</body>
</html>
"""
OUT.write_text(HEAD + BODY, encoding="utf-8")
print(OUT, len(HEAD + BODY), "bytes,", len(K["kpis"]), "cifras clave")
