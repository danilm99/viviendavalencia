#!/usr/bin/env python3
"""Inyecta data/listings.json y data/barrios.geojson en template.html -> pisos-turisticos-valencia.html"""
import json, pathlib

root = pathlib.Path(__file__).parent
tpl = (root / "template.html").read_text(encoding="utf-8")
data = json.load(open(root / "data/listings.json", encoding="utf-8"))
barrios = json.load(open(root / "data/barrios.geojson", encoding="utf-8"))
# reducir precisión del geojson de barrios para aligerar
def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 5), round(c[1], 5)]
for f in barrios["features"]:
    f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    f["properties"] = {"neighbourhood": f["properties"].get("neighbourhood"), "neighbourhood_group": f["properties"].get("neighbourhood_group")}

def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")

extra = json.load(open(root / "data/extra.json", encoding="utf-8"))
research = json.load(open(root / "data/research.json", encoding="utf-8"))
# ---- privacidad: los anfitriones particulares (menos de 5 anuncios y sin ficha de empresa) no se publican por su nombre ----
F = {k: i for i, k in enumerate(data["meta"]["fields"])}
known = set(str(k) for k in (research.get("hosts") or {}).keys())
pseudo, nanon = {}, 0
for r in data["rows"]:
    hid = r[F["host_id"]]
    if (r[F["host_n"]] or 0) < 5 and str(hid) not in known:
        if hid not in pseudo: pseudo[hid] = -(len(pseudo) + 1)
        r[F["host_id"]] = pseudo[hid]; r[F["host"]] = ""; r[F["host_loc"]] = ""; r[F["host_since"]] = ""; nanon += 1
data["meta"]["anon_rule"] = "Anfitriones con menos de 5 anuncios y sin ficha de empresa: nombre, ubicación y antigüedad no publicados; identificador sustituido por uno ficticio."
# ---- aligerar: campos repetitivos como índices de diccionario ----
dic = {}
for k in ("barrio", "distrito", "property_type", "host_loc"):
    vals = sorted({r[F[k]] for r in data["rows"] if r[F[k]] is not None}, key=str); ix = {v: i for i, v in enumerate(vals)}
    for r in data["rows"]:
        if r[F[k]] is not None: r[F[k]] = ix[r[F[k]]]
    dic[k] = vals
data["meta"]["dict"] = dic
print("anonimizados", nanon, "anuncios de", len(pseudo), "anfitriones particulares")
out = tpl.replace("__DATA__", js(data)).replace("__BARRIOS__", js(barrios)).replace("__EXTRA__", js(extra)).replace("__RESEARCH__", js(research))
p = root / "pisos-turisticos-valencia.html"
p.write_text(out, encoding="utf-8")
print(p, round(p.stat().st_size / 1e6, 2), "MB", data["meta"]["count"], "anuncios")
