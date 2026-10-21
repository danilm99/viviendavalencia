# Genera elecciones-29n.html (página estática) a partir de data_elecciones.py (E29) y data_historial.py (H).
import re, html, pathlib
ROOT = pathlib.Path(__file__).parent
OUT = ROOT.parent / "elecciones-29n.html"

def load(fname, var):
    ns = {}
    exec(open(ROOT / fname, encoding="utf-8").read(), ns)
    return ns[var]

E = load("data_elecciones.py", "E29")
H = load("data_historial.py", "H") if (ROOT / "data_historial.py").exists() else None
head_tpl = open(ROOT / "tpl/01_head.html", encoding="utf-8").read()
base_css = head_tpl.split("<style>", 1)[1].split("/* otras ciudades */", 1)[0]
apply_js = open(ROOT.parent / "valenciano/apply.js", encoding="utf-8").read()

def esc(s):
    s = re.sub(r"(\d) (%|€|M€)", "\\1\u00a0\\2", s)
    return html.escape(s, quote=True)

def rich(s):
    """Escapa y pone en cursiva las citas «…»."""
    s = esc(s)
    return re.sub(r"«([^»]+)»", r"<q>\1</q>", s)

def srcs(lst):
    return '<p class="src">Fuentes: ' + " · ".join(f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(t)}</a>' for t, u in lst) + "</p>"

KIND = {"doc": ("Documento oficial del partido", "k-doc"), "dec": ("Declaración", "k-dec"), "gov": ("Medida del Gobierno que el partido promete mantener", "k-gov")}
STATUS = {"ok": ("Cumplida", "st-ok"), "part": ("Cumplida en parte", "st-part"), "no": ("No cumplida", "st-no"),
          "revert": ("Cumplida y luego revertida", "st-part"), "curso": ("En curso", "st-curso"), "interr": ("Interrumpida por cambio de gobierno", "st-nv"), "nv": ("Sin datos públicos", "st-nv"),
          "hecho": ("Medida aprobada", "st-m"), "dec": ("Decisión de gobierno", "st-m"), "vote": ("Votación", "st-m"), "bal": ("Balance", "st-m")}

CSS = """
/* página de elecciones */
q{quotes:"«" "»"}
.warn{background:var(--mark-soft);border-left:6px solid var(--mark);padding:12px 16px;margin:16px 0;max-width:72ch;font-size:15.5px}
.warn b{font-weight:700}
.party{margin:26px 0 8px;padding-top:12px;border-top:3px solid var(--rule)}
.party h3{margin:0 0 2px;font-size:26px}
.party .full{color:var(--muted);font-size:14px;margin:0 0 10px}
dl.facts{display:grid;grid-template-columns:150px 1fr;gap:6px 14px;margin:10px 0 14px;font-size:14.5px;max-width:78ch}
dl.facts dt{color:var(--muted);font-weight:600}
dl.facts dd{margin:0}
@media (max-width:640px){dl.facts{grid-template-columns:1fr;gap:0}dl.facts dd{margin-bottom:8px}}
.said{list-style:none;padding:0;margin:8px 0;display:grid;gap:10px}
.said li{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--fg);padding:10px 14px 10px}
.said li.k-doc{border-left-color:var(--s3)}.said li.k-dec{border-left-color:var(--s1)}.said li.k-gov{border-left-color:var(--s5)}
.said .hd{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;font-size:12.5px;color:var(--muted);margin-bottom:4px}
.said .hd .ty{font-size:11px}
.said .who{font-weight:600;font-size:14px;margin:0 0 4px;max-width:none}
.said .tx{font-size:15px;margin:0;max-width:none}
.ty.k-doc{color:var(--s3);border-color:color-mix(in srgb,var(--s3) 45%,transparent)}
.ty.k-dec{color:var(--s1);border-color:color-mix(in srgb,var(--s1) 45%,transparent)}
.ty.k-gov{color:var(--s5);border-color:color-mix(in srgb,var(--s5) 50%,transparent)}
table.mx th:first-child{min-width:120px}
table.mx td{font-size:13.5px;min-width:118px}
table.mx td.none{color:var(--muted);font-style:italic}
table.mx td.who{color:var(--muted);font-size:12.5px;min-width:128px}
table.mx tr.vrow td{border-top:2px solid var(--rule);font-weight:600}
table.mx td.gov{background:color-mix(in srgb,var(--s5) 9%,transparent)}
table.st td:first-child{font-weight:700;white-space:nowrap}
.lvls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0}
@media (max-width:820px){.lvls{grid-template-columns:1fr}}
.lvl{background:var(--panel);border:1px solid var(--line);border-top:4px solid var(--fg);padding:12px 14px}
.lvl h4{font:800 19px/1.1 var(--display);margin:0 0 2px}
.lvl .when{font-size:12.5px;color:var(--muted);margin:0 0 8px}
.lvl ul{margin:0;padding-left:18px;font-size:14px}.lvl li{margin:0 0 5px}
.lvl.here{border-top-color:var(--mark);box-shadow:inset 0 0 0 2px var(--mark)}
.tl{margin:12px 0 4px;overflow-x:auto}
.tl svg{width:100%;min-width:620px;height:auto;display:block}
.tl text{font-family:var(--body)}
table.gv td:first-child{white-space:nowrap;font-weight:600}
table.gv td.maj{white-space:nowrap}
.badge{display:inline-block;font:600 11.5px/1 var(--body);padding:4px 8px;border-radius:999px;white-space:nowrap;border:1.5px solid currentColor}
.st-ok{color:var(--s3)}.st-part{color:var(--s5)}.st-no{color:var(--s2)}.st-curso{color:var(--s1)}.st-nv{color:var(--muted)}.st-m{color:var(--fg)}
.rec{margin:22px 0 6px}
.rec h3{margin:0 0 6px}
.rec .gov{font-size:14.5px;margin:0 0 10px;max-width:78ch}
table.pr td{font-size:13.5px}
table.pr td.s{white-space:nowrap}
table.pr td:first-child{min-width:110px;color:var(--muted);font-size:12.5px}
table.vt td{font-size:13.5px}
.ev{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin:12px 0}
.ev a{display:block;background:var(--panel);border:1px solid var(--line);border-top:4px solid var(--fg);padding:10px 14px;text-decoration:none}
.ev a:hover{background:var(--mark-soft)}
.ev b{display:block;font:700 16px/1.2 var(--display)}
.ev span{font-size:13px;color:var(--muted)}
.keyrow{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--muted);margin:6px 0}
@media (max-width:640px){table.cardm.mx tr{padding:10px 0}table.cardm.mx td{min-width:0}table.cardm.mx td::before{content:attr(data-h);display:block;font-weight:600;color:var(--muted);font-size:12px;font-style:normal}table.cardm.mx td:first-child{font:700 17px/1.2 var(--display)}table.cardm.mx td:first-child::before{content:none}
table.cardm td[data-h]::before{content:attr(data-h);display:block;font-weight:600;color:var(--muted);font-size:12px;font-style:normal}}
"""

HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<script>(function(){ var L=null; try{ var q=new URLSearchParams(location.search).get('lang'); if(q==='va'||q==='es'){ L=q; localStorage.setItem('vv.lang',q); } else L=localStorage.getItem('vv.lang'); }catch(e){} window.LANG=L==='va'?'va':'es'; window.T=function(es,va){ return window.LANG==='va'&&va!=null?va:es; }; window.tr=function(s){ return s; }; if(window.LANG==='va'){ document.documentElement.lang='ca-ES-valencia'; document.write('<script src="va-elecciones.js"><\\/script>'); } })();</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Elecciones del 29-N: qué dicen los partidos sobre vivienda</title>
<meta name="description" content="Qué han dicho PP, PSOE, Compromís-Front Valencià y Vox sobre vivienda antes del 29-N, quién ha gobernado cada administración, qué competencias tiene cada una y qué prometió y cumplió cada partido. Con fuentes.">
<meta property="og:title" content="Elecciones del 29-N: qué dicen los partidos sobre vivienda">
<meta property="og:description" content="Ningún partido ha publicado aún su programa. Lo dicho hasta ahora, quién decide qué y qué hizo cada uno cuando gobernó, con la fuente de cada dato.">
<meta property="og:type" content="article">
<meta property="og:image" content="https://viviendavalencia.info/og-elecciones.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="https://viviendavalencia.info/elecciones-29n.html">
<meta property="og:site_name" content="viviendavalencia.info">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://viviendavalencia.info/og-elecciones.jpg">
<link rel="canonical" href="https://viviendavalencia.info/elecciones-29n.html">
<meta name="robots" content="index,follow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>""" + base_css + CSS + """</style>
<script>window.goatcounter={path:function(){return location.pathname||"/"}}</script><script data-goatcounter="https://viviendavalencia.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</head>
"""

P = {p["id"]: p for p in E["parties"]}
ORDER = [p["id"] for p in E["parties"]]

def sec_estado():
    rows = "".join(
        f'<tr><td>{esc(p["name"])}</td><td data-h="Programa">{rich(p["program"])}</td><td data-h="Otros documentos">{rich(p["doc"])}</td>'
        f'<td data-h="Cabeza de lista por Valencia">{esc(p["list"])}</td><td data-h="Resultado en 2023 en Valencia">{esc(p["votes23"])}</td></tr>'
        for p in E["parties"])
    return f"""<section id="estado">
<h2>Ningún partido ha publicado su programa</h2>
<p class="lede">{esc(E["intro"])}</p>
<div class="tbl"><table class="st cardm"><thead><tr><th>Candidatura</th><th>Programa electoral</th><th>Otros documentos</th><th>Cabeza de lista por Valencia</th><th>Resultado en 2023 en la provincia</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="src">{esc(E["polls"])}</p>{srcs(E["polls_src"])}
</section>"""

def sec_dicho():
    out = []
    for p in E["parties"]:
        items = []
        dkey = lambda it: tuple(int(x) for x in reversed(it["date"].split("-")))
        for it in sorted(p["said"], key=lambda it: (it["kind"] == "gov", dkey(it))):
            lab, cls = KIND[it["kind"]]
            items.append(f'<li class="{cls}"><div class="hd"><span class="ty {cls}">{esc(lab)}</span><span>{esc(it["date"])}</span></div>'
                         f'<p class="who">{rich(it["who"])}</p><p class="tx">{rich(it["text"])}</p>{srcs(it["src"])}</li>')
        out.append(f'<div class="party" id="p-{p["id"]}"><h3>{esc(p["name"])}</h3><p class="full">{esc(p["full"])}</p>{('<p class="note">'+esc(p["note"])+'</p>') if p.get("note") else ""}<ul class="said">{"".join(items)}</ul></div>')
    key = "".join(f'<span class="ty {c}">{esc(l)}</span>' for l, c in KIND.values())
    return f"""<section id="dicho">
<h2>Qué ha dicho cada partido hasta ahora</h2>
<p>Ordenado por fecha dentro de cada partido; las medidas ya aprobadas por el Gobierno van al final. Cada entrada indica si viene de un documento oficial del partido, de una declaración pública o de una medida ya aprobada por el Gobierno que el partido promete mantener.</p>
<div class="keyrow">{key}</div>
{"".join(out)}
</section>"""

def sec_temas():
    head = "".join(f"<th>{esc(P[i]['name'])}</th>" for i in ORDER)
    rows = []
    for theme, d, who in E["themes"]:
        tds = []
        for i in ORDER:
            v = d.get(i, "")
            if not v:
                tds.append(f'<td class="none" data-h="{esc(P[i]["name"])}">Nada público por ahora</td>')
            else:
                cls = ' class="gov"' if (i == "psoe" and "decreto" in v.lower()) else ""
                tds.append(f'<td{cls} data-h="{esc(P[i]["name"])}">{rich(v)}</td>')
        rows.append(f'<tr><td>{esc(theme)}</td><td class="who" data-h="Quién lo decide">{esc(who)}</td>{"".join(tds)}</tr>')
    V = E["decree_vote"]
    rows.append(f'<tr class="vrow"><td>{esc(V[0])}</td><td class="who" data-h="Quién lo decide">Congreso</td>' + "".join(f'<td data-h="{esc(P[i]["name"])}">{esc(V[1][i])}</td>' for i in ORDER) + "</tr>")
    return f"""<section id="temas">
<h2>Por temas</h2>
<p>Resumen de la sección anterior. «Nada público por ahora» significa que no hemos encontrado ninguna declaración o documento del partido sobre ese tema desde la convocatoria, no que el partido no tenga postura. Las celdas sombreadas son medidas ya aprobadas por el Gobierno, no propuestas nuevas. La columna «Quién lo decide» indica qué administración tiene la competencia: muchas de estas cosas no dependen solo del Congreso que se elige el 29-N.</p>
<div class="tbl"><table class="mx cardm"><thead><tr><th>Tema</th><th>Quién lo decide</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</section>"""

def sec_evidencia():
    cards = "".join(f'<a href="index.html#fuera" data-g="{g}"><b>{esc(t)}</b><span>{esc(c)}</span></a>' for t, c, g in E["evidence"])
    return f"""<section id="evidencia">
<h2>Qué dice la experiencia de otras ciudades</h2>
<p>Muchas de estas propuestas ya se han probado en otros sitios. En el informe resumimos qué se hizo y qué pasó después en 19 casos, con los estudios que lo evalúan. No es una valoración de los partidos: sirve para saber qué resultados han tenido medidas parecidas.</p>
<div class="ev">{cards}</div>
</section>"""

def sec_metodo():
    lis = "".join(f"<li>{esc(m)}</li>" for m in E["method"] + (H["method"] if H else []))
    return f"""<section id="metodo">
<h2>Cómo hemos hecho esta página</h2>
<ul class="plain">{lis}</ul>
<p>Si ves un error, una omisión o una declaración que falta, escríbenos: lo corregimos y lo anotamos en el registro de cambios del informe. Última actualización: {esc(E["updated"])}.</p>
</section>"""

# ---------- historial ----------
def sec_competencias():
    if not H: return ""
    cards = []
    for L in H["levels"]:
        lis = "".join(f"<li>{rich(x)}</li>" for x in L["can"])
        cards.append(f'<div class="lvl{" here" if L.get("here") else ""}"><h4>{esc(L["name"])}</h4><p class="when">{esc(L["when"])}</p><ul>{lis}</ul></div>')
    return f"""<section id="competencias">
<h2>Quién decide qué en vivienda</h2>
<p class="lede">{esc(H["levels_intro"])}</p>
<div class="lvls">{"".join(cards)}</div>
{"".join(f'<p class="note">{rich(n)}</p>' for n in H.get("levels_notes", []))}
{srcs(H["levels_src"])}
</section>"""

def timeline_svg():
    rows = H["timeline"]  # [{lvl, segs:[[from,to,label,sub]]}]
    y0, y1 = 1995, 2027
    W, lw, rh, gap, top = 860, 132, 40, 12, 24
    X = lambda y: lw + (y - y0) / (y1 - y0) * (W - lw - 6)
    parts = []
    for yr in range(1995, 2027, 5):
        x = X(yr)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top-6}" y2="{top+len(rows)*(rh+gap)-gap}" stroke="var(--grid)"/>'
                     f'<text x="{x:.1f}" y="{top-10}" font-size="12" fill="var(--muted)" text-anchor="middle">{yr}</text>')
    for r, row in enumerate(rows):
        y = top + r * (rh + gap)
        parts.append(f'<text x="0" y="{y+rh/2+5}" font-size="13.5" font-weight="600" fill="var(--fg)">{esc(row["lvl"])}</text>')
        for k, (a, b, lab, sub) in enumerate(row["segs"]):
            xa, xb = X(a), X(b)
            fill = "var(--panel)" if k % 2 == 0 else "var(--grid)"
            parts.append(f'<rect x="{xa:.1f}" y="{y}" width="{max(xb-xa-1.5,1):.1f}" height="{rh}" fill="{fill}" stroke="var(--line)"><title>{esc(lab)} · {esc(sub)}</title></rect>')
            wpx = xb - xa
            short = row.get("short", {}).get(lab)
            if wpx > 7.6 * len(lab) + 8:
                parts.append(f'<text x="{xa+5:.1f}" y="{y+17}" font-size="12.5" font-weight="700" fill="var(--fg)">{esc(lab)}</text>')
                if wpx > 6.3 * len(sub) + 8:
                    parts.append(f'<text x="{xa+5:.1f}" y="{y+32}" font-size="11" fill="var(--muted)">{esc(sub)}</text>')
            elif short and wpx > 6.0 * len(short) + 4:
                parts.append(f'<text x="{(xa+xb)/2:.1f}" y="{y+24}" font-size="11" font-weight="700" fill="var(--fg)" text-anchor="middle">{esc(short)}</text>')
    hgt = top + len(rows) * (rh + gap)
    parts.append(f'<line x1="{X(2026.8):.1f}" x2="{X(2026.8):.1f}" y1="{top-4}" y2="{hgt-gap}" stroke="var(--fg)" stroke-dasharray="3 3"/>')
    return f'<div class="tl" aria-hidden="true"><svg viewBox="0 0 {W} {hgt}" role="img">{"".join(parts)}</svg></div>'

def gov_table(rows):
    trs = "".join(f'<tr><td>{esc(r[0])}</td><td data-h="Gobierno">{rich(r[1])}</td><td class="maj" data-h="Mayoría">{rich(r[2])}</td><td data-h="Vivienda">{rich(r[3])}</td></tr>' for r in rows)
    return f'<div class="tbl"><table class="gv cardm"><thead><tr><th>Periodo</th><th>Gobierno</th><th>Mayoría</th><th>Quién llevaba vivienda</th></tr></thead><tbody>{trs}</tbody></table></div>'

def sec_gobiernos():
    if not H: return ""
    blocks = []
    for g in H["govs"]:
        blocks.append(f'<h3 id="g-{g["id"]}">{esc(g["title"])}</h3>{"<p>"+rich(g["note"])+"</p>" if g.get("note") else ""}{gov_table(g["rows"])}{srcs(g["src"])}')
    cc = H["ccaa"]
    trs = "".join(f'<tr><td>{esc(r[0])}</td><td data-h="Presidencia">{esc(r[1])}</td><td data-h="Gobierno">{rich(r[2])}</td><td data-h="Zonas tensionadas (ley 12/2023)">{rich(r[3])}</td></tr>' for r in cc["rows"])
    return f"""<section id="gobiernos">
<h2>Quién ha gobernado cada administración</h2>
<p class="lede">{esc(H["govs_intro"])}</p>
{timeline_svg()}
<p class="src">Cada franja es un periodo de gobierno; el detalle, con la mayoría que tenía y quién llevaba vivienda, está en las tablas.</p>
{"".join(blocks)}
<h3 id="g-ccaa">{esc(cc["title"])}</h3>
<p>{rich(cc["note"])}</p>
<div class="tbl"><table class="gv cardm"><thead><tr><th>Comunidad</th><th>Presidencia</th><th>Partidos en el gobierno</th><th>Zonas tensionadas (ley 12/2023)</th></tr></thead><tbody>{trs}</tbody></table></div>
{srcs(cc["src"])}
</section>"""

def sec_historial():
    if not H: return ""
    out = []
    for r in H["record"]:
        if not r["items"]: continue
        trs = []
        for it in r["items"]:
            lab, cls = STATUS[it["st"]]
            trs.append(f'<tr><td>{esc(it["where"])}</td><td data-h="Qué se prometió o se hizo">{rich(it["what"])}</td>'
                       f'<td data-h="Resultado">{rich(it["res"])}{srcs(it["src"])}</td><td class="s" data-h="Valoración"><span class="badge {cls}">{esc(lab)}</span></td></tr>')
        out.append(f'<div class="rec" id="h-{r["id"]}"><h3>{esc(r["name"])}</h3><p class="gov">{rich(r["gov"])}</p>'
                   f'<div class="tbl"><table class="pr cardm"><thead><tr><th>Dónde y cuándo</th><th>Qué se prometió o se hizo</th><th>Resultado según los datos</th><th>Valoración</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div></div>')
    key = "".join(f'<span class="badge {c}">{esc(l)}</span>' for k, (l, c) in STATUS.items() if True)
    return f"""<section id="historial">
<h2>Qué prometieron y qué hicieron cuando gobernaron</h2>
<p class="lede">{esc(H["record_intro"])}</p>
<div class="keyrow">{key}</div>
{"".join(f'<p class="note">{rich(n)}</p>' for n in H.get("record_notes", []))}
{"".join(out)}
</section>"""

def sec_votos():
    if not H or not H.get("votes"): return ""
    trs = "".join(f'<tr><td>{rich(v[0])}</td><td data-h="A favor">{esc(v[1])}</td><td data-h="En contra">{esc(v[2])}</td><td data-h="Abstención">{esc(v[3])}</td><td data-h="Resultado">{rich(v[4])}</td></tr>' for v in H["votes"])
    return f"""<section id="votaciones">
<h2>Cómo votaron en el Congreso</h2>
<p>Votaciones de las principales normas estatales de vivienda de los últimos años. Los partidos aparecen con el nombre de su grupo en cada momento.</p>
<div class="tbl"><table class="vt cardm"><thead><tr><th>Norma</th><th>A favor</th><th>En contra</th><th>Abstención</th><th>Resultado</th></tr></thead><tbody>{trs}</tbody></table></div>
{srcs(H["votes_src"])}
</section>"""

NAV = [("estado", "Programas"), ("dicho", "Qué han dicho"), ("temas", "Por temas")]
if H:
    NAV += [("competencias", "Quién decide qué"), ("gobiernos", "Quién ha gobernado"), ("historial", "Prometido y hecho"), ("votaciones", "Votaciones")]
NAV += [("evidencia", "Otras ciudades"), ("metodo", "Método")]

body = f"""<body>
SITEBAR<div class="page">
<nav class="spine" id="spine">
  <div class="brand">Elecciones del 29-N y vivienda</div>
  {"".join(f'<a href="#{i}">{esc(t)}</a>' for i, t in NAV)}
  <div class="foot"><a href="index.html">Informe sobre la vivienda</a> · <a href="pisos-turisticos-valencia.html">Mapa de pisos turísticos</a> · <a class="langsw" data-notr href="?lang=va">Valencià</a></div>
</nav>
<main id="top">
<header class="hero">
  <p class="meta">Actualizado el {esc(E["updated"])} · <a href="index.html">viviendavalencia.info</a> · <a class="langsw" data-notr href="?lang=va">Valencià</a></p>
  <h1>Elecciones del 29-N: qué dicen los partidos sobre vivienda</h1>
  <p class="dek">Lo que han dicho hasta ahora las candidaturas con opciones de escaño en Valencia, qué decide cada administración y qué hizo cada partido cuando tuvo el poder de decidir.</p>
  <div class="warn"><b>Todavía no hay programas.</b> A {esc(E["updated"])} ningún partido ha publicado su programa electoral para el 29-N. Lo que recogemos son documentos y declaraciones; cuando se publiquen los programas, actualizaremos la página.</div>
  <div class="btnrow"><a class="btn primary" href="#dicho">Qué ha dicho cada partido</a>{'<a class="btn" href="#historial">Qué hicieron cuando gobernaron</a><a class="btn" href="#competencias">Quién decide qué</a>' if H else ''}</div>
</header>
{sec_estado()}
{sec_dicho()}
{sec_temas()}
{sec_competencias()}
{sec_gobiernos()}
{sec_historial()}
{sec_votos()}
{sec_evidencia()}
{sec_metodo()}
<p class="foot"><a href="./">Informe sobre la vivienda en València</a> · <a href="pisos-turisticos-valencia.html">Mapa de pisos turísticos</a></p>
<p class="foot">viviendavalencia.info · Página informativa sin afiliación a ningún partido. Datos y código abiertos. Esta web cuenta visitas de forma anónima con GoatCounter, sin cookies.</p>
</main>
</div>
<a class="totop" id="totop" href="#top" aria-label="Volver arriba">↑</a>
<script>(function(){{ const links=[...document.querySelectorAll('nav.spine a[href^="#"]')]; const secs=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
const io=new IntersectionObserver(es=>{{ es.forEach(e=>{{ if(e.isIntersecting){{ links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id)); const on=links.find(a=>a.classList.contains('on')); if(on&&innerWidth<=980) on.scrollIntoView({{inline:'center',block:'nearest'}}); }} }}); }},{{rootMargin:'-40% 0px -55% 0px'}}); secs.forEach(s=>io.observe(s));
const tt=document.getElementById('totop'); addEventListener('scroll',()=>tt.classList.toggle('on',scrollY>900),{{passive:true}}); }})();</script>
<script>(function(){{ document.querySelectorAll('a.langsw').forEach(function(a){{ var va=window.LANG==='va'; a.textContent=va?'Castellano':'Valencià'; a.setAttribute('lang',va?'es':'ca-ES-valencia'); a.addEventListener('click',function(e){{ e.preventDefault(); location.href=location.pathname+'?lang='+(va?'es':'va')+location.hash; }}); }}); }})();</script>
<script>{apply_js}</script>
</body>
</html>
"""

body = body.replace("SITEBAR", '<div class="sitebar"><a class="sb-home" href="./">viviendavalencia.info</a><nav aria-label="Secciones del sitio"><a href="./">Informe</a><a href="pisos-turisticos-valencia.html">Mapa</a><a href="elecciones-29n.html" aria-current="page">Elecciones 29-N</a><a class="langsw" data-notr href="?lang=va">Valencià</a></nav></div>\n', 1)
OUT.write_text(HEAD + body, encoding="utf-8")
print("ok", OUT, len(HEAD + body))
