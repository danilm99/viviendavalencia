#!/usr/bin/env python3
"""Fusiona anuario.json, atlas_renta_vlc.json, atlas_demo_vlc.json, gini_vlc.json, fianzas.json, cgpj_valencia.json, demo.json
en data_ext.json (clave 'ext' del informe)."""
import json, pathlib, statistics, csv, glob, collections
ROOT = pathlib.Path(__file__).parent
L = lambda n: json.load(open(ROOT / n, encoding="utf-8"))
AN, AR, AD, GI, FI, CG, DM = (L(n) for n in ("anuario.json", "atlas_renta_vlc.json", "atlas_demo_vlc.json", "gini_vlc.json", "fianzas.json", "cgpj_valencia.json", "demo.json"))

DIST = ["Ciutat Vella", "l'Eixample", "Extramurs", "Campanar", "la Saïdia", "el Pla del Real", "l'Olivereta", "Patraix", "Jesús", "Quatre Carreres",
        "Poblats Marítims", "Camins al Grau", "Algirós", "Benimaclet", "Rascanya", "Benicalap", "Pobles del Nord", "Pobles de l'Oest", "Pobles del Sud"]
def dname(k):
    if k == "MUNICIPIO": return "València"
    n = int(k.split("distrito")[-1]); return DIST[n - 1]

E = {}
# ---- renta (Atlas INE) ----
E["renta"] = {"city": {ind: {y: v for y, v in sorted(s.items())} for ind, s in AR["MUNICIPIO"].items()},
              "dist": {dname(k): {ind: dict(sorted(s.items())) for ind, s in v.items()} for k, v in AR.items() if k != "MUNICIPIO"},
              "gini": GI, "src": "INE, Atlas de distribución de renta de los hogares (tablas 31250, 37721), ejercicios fiscales 2015-2024"}
E["demo_atlas"] = {"city": {ind: dict(sorted(s.items())) for ind, s in AD["MUNICIPIO"].items()},
                   "dist": {dname(k): {ind: dict(sorted(s.items())) for ind, s in v.items()} for k, v in AD.items() if k != "MUNICIPIO"}}
# ---- anuario ----
for k in ("serpavi_city", "serpavi_district", "serpavi_barrio_2023", "transacciones", "idealista_district_rent", "idealista_district_sale",
          "catastro_barrio", "catastro_valor_distrito", "catastro_uso_distrito", "poblacion_distrito", "hogares_distrito", "licencias_distrito",
          "tasado_trim", "esfuerzo_distrito", "censo2011_barrio", "censo2011_distrito"):
    E[k] = AN[k]
# ---- fianzas ----
E["fianzas"] = {y: {k: v for k, v in d.items() if k != "cp"} for y, d in FI.items()}
E["fianzas_cp"] = {y: d["cp"] for y, d in FI.items()}
# mediana por CP 2021 y 2025 (viviendas en València)
def cp_median(year):
    f = ROOT / "raw" / "vivienda_raw" / f"gva_fianzas_{year}.csv"
    if not f.exists(): return {}
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(f, encoding="utf-8-sig"), delimiter=";"):
        if r["municipio"].strip().upper() != "VALENCIA": continue
        try: v = float(r["importe_fianza"].replace(",", "."))
        except: continue
        if 50 <= v <= 20000 and r["cp"].startswith("460"): by[r["cp"]].append(v)
    return {cp: [len(v), statistics.median(v)] for cp, v in by.items() if len(v) >= 40}
E["fianzas_cp_med"] = {"2021": cp_median(2021), "2025": cp_median(2025)}
# ---- cgpj ----
E["cgpj"] = CG
# ---- demografía ----
E["nacimientos"] = DM["nacimientos"]; E["natalidad_ind"] = DM["natalidad_ind"]; E["hojas_tamano"] = DM["hojas_tamano"]
E["hojas_comp_2025"] = {k: {" ".join(kk.split()): vv for kk, vv in v.items()} for k, v in DM["hojas_comp_2025"].items()}; E["nac_def_distrito"] = DM["nac_def_distrito"]; E["nac_def_distrito_hdr"] = DM["nac_def_distrito_hdr"]
E["hojas_tamano_distrito_2025"] = DM.get("hojas_tamano_distrito_2025", {})
# censo 2021 hogares por tipo (INE 59544)
E["censo21_hogares_tipo"] = {"Unipersonal": 96493, "Multipersonal sin familia": 12213, "Una familia, sin núcleo": 4110, "Una familia, un núcleo": 177808,
                             "Un núcleo y otras personas": 10334, "Dos o más núcleos": 6614, "Una familia con otras personas": 14795, "Dos o más familias": 804, "total": 323171}

json.dump(E, open(ROOT / "data_ext.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ok", round((ROOT / "data_ext.json").stat().st_size / 1e3), "kB", "fianzas cp 2025:", len(E["fianzas_cp_med"]["2025"]))
