#!/usr/bin/env python3
"""Construye informe-vivienda-valencia.html a partir de vivienda/data.json + data_ext.json + bloques de investigación + template_informe.html"""
import json, pathlib, collections, importlib.util, sys
ROOT = pathlib.Path(__file__).parent
D = json.load(open(ROOT / "data.json", encoding="utf-8"))
D["ext"] = json.load(open(ROOT / "data_ext.json", encoding="utf-8"))
D["ext"]["extranjeros"] = json.load(open(ROOT / "extranjeros_anuario.json", encoding="utf-8"))

def load_var(fname, var):
    p = ROOT / fname
    if not p.exists(): return None
    spec = importlib.util.spec_from_file_location(fname[:-3], p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return getattr(m, var)
D["gasto"] = load_var("data_gasto.py", "G") or {}
D["extranjeros"] = load_var("data_extranjeros.py", "X") or {}
D["social"] = load_var("data_social.py", "S") or {}
D["mundo"] = load_var("data_mundo.py", "W") or {}
_ar = ROOT / "archivo_fuentes.json"
D["arch"] = {u: v["snap"] for u, v in json.load(open(_ar, encoding="utf-8")).items() if v.get("snap")} if _ar.exists() else {}

# ---- derivados del mapa de pisos turísticos (ratio por barrio y distrito) ----
DN = {"CIUTAT VELLA": "Ciutat Vella", "L'EIXAMPLE": "l'Eixample", "EXTRAMURS": "Extramurs", "CAMPANAR": "Campanar", "LA SAIDIA": "la Saïdia", "EL PLA DEL REAL": "el Pla del Real",
      "L'OLIVERETA": "l'Olivereta", "PATRAIX": "Patraix", "JESUS": "Jesús", "QUATRE CARRERES": "Quatre Carreres", "POBLATS MARITIMS": "Poblats Marítims", "CAMINS AL GRAU": "Camins al Grau",
      "ALGIROS": "Algirós", "BENIMACLET": "Benimaclet", "RASCANYA": "Rascanya", "BENICALAP": "Benicalap", "POBLATS DEL NORD": "Pobles del Nord", "POBLATS DE L'OEST": "Pobles de l'Oest", "POBLATS DEL SUD": "Pobles del Sud"}
try:
    L = json.load(open(ROOT.parent / "data/listings.json", encoding="utf-8"))
    E = json.load(open(ROOT.parent / "data/extra.json", encoding="utf-8"))
    F = {k: i for i, k in enumerate(L["meta"]["fields"])}
    cnt = collections.Counter(r[F["barrio"]] for r in L["rows"] if r[F["room"]] == 0)
    rat = []
    for b, n in cnt.items():
        bi = E["barrios"].get(b)
        if bi and bi.get("viv"):
            rat.append([b.title(), n, bi["viv"], round(100 * n / bi["viv"], 1)])
    rat.sort(key=lambda x: -x[3])
    D["turistico"]["ratio_barrios"] = rat[:15]
    D["turistico"]["total_viv_ciudad"] = sum(b.get("viv") or 0 for b in E["barrios"].values())
    D["turistico"]["airbnb_entire"] = sum(cnt.values())
    # por distrito: viviendas del distrito = suma de barrios CATAV con ese distrito
    bd = {}
    for r in L["rows"]:
        if r[F["barrio"]] and r[F["distrito"]]: bd[r[F["barrio"]]] = r[F["distrito"]]
    for grp in E.get("catav", {}).values():
        fi = {k: i for i, k in enumerate(grp["fields"])}
        for r in grp["rows"]:
            if r[fi["barrio"]] and r[fi["distrito"]]: bd[r[fi["barrio"]]] = r[fi["distrito"]]
    vivd = collections.Counter()
    for b, bi in E["barrios"].items():
        d = bd.get(b)
        if d and bi.get("viv"): vivd[d] += bi["viv"]
    cntd = collections.Counter(r[F["distrito"]] for r in L["rows"] if r[F["room"]] == 0)
    rd = {}
    for d, n in cntd.items():
        if vivd.get(d): rd[DN.get(d, d.title())] = [n, vivd[d], round(100 * n / vivd[d], 2)]
    D["turistico"]["ratio_distritos"] = rd
    print("ratio distritos:", len(rd), sorted(rd.items(), key=lambda x: -x[1][2])[:4])
except Exception as e:
    print("sin datos del mapa:", e)

def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")

parts = sorted((ROOT / "tpl").glob("*.html"))
tpl = "".join(p.read_text(encoding="utf-8") for p in parts) if parts else (ROOT / "template_informe.html").read_text(encoding="utf-8")
(ROOT / "template_informe.html").write_text(tpl, encoding="utf-8")
out = tpl.replace("__DATA__", js(D))
p = ROOT.parent / "informe-vivienda-valencia.html"
p.write_text(out, encoding="utf-8")
print(p, round(p.stat().st_size / 1e6, 2), "MB")
