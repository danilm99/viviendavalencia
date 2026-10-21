#!/usr/bin/env python3
"""Población extranjera del Anuario: nacionalidades frecuentes (serie 2017-2025, con 65+), continente por distrito (2017-2025)."""
import openpyxl, json, pathlib, re
RAW = pathlib.Path(__file__).parent / "raw" / "anuario"
def rows(path, sheet):
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True)[sheet]
    return [list(r) for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
def num(x):
    try: return float(x)
    except: return None
files = [(RAW / f"{y}/Cap02.xlsx", "2.3", "2.6") for y in range(2017, 2023)] + [(RAW / f"{y}/020101_PadronMunicipal.xlsx", "5", "9") for y in (2023, 2024, 2025)]
NAC, CONT = {}, {}
for p, s1, s2 in files:
    r = rows(p, s1)
    y = re.search(r"(20\d\d)\s*$", str(r[0][0]).strip()).group(1)
    hdr = [str(c).strip() if c else "" for c in r[1]]
    d = {}
    for x in r[2:]:
        nm = str(x[0]).strip()
        if nm in ("Hombres", "Mujeres"): break
        if nm.startswith("Fuente"): continue
        tot = num(x[1])
        if tot is None: continue
        # 65+: columnas de edad con límite inferior >=60 ('60-69','70-79','80 y más') -> aproximamos 60+ ; si hay '65' usamos exacto
        age = {}
        for h, v in zip(hdr[1:], x[1:]):
            if h and h != "Total" and num(v) is not None: age[h] = num(v)
        d[nm] = {"total": int(tot), "edad": age}
    NAC[y] = d
    r = rows(p, s2)
    hdr = [str(c).replace("\n", " ").strip() if c else "" for c in r[1]]
    cd = {}
    for x in r[2:]:
        nm = str(x[0]).strip()
        if re.match(r"\d+\.", nm) or nm == "Total":
            cd[re.sub(r"^\d+\.\s*", "", nm)] = {h: num(v) for h, v in zip(hdr[1:], x[1:]) if h}
    CONT[y] = cd
print(list(NAC["2025"]["Total"]["edad"]))
print({y: NAC[y]["Total"]["total"] for y in NAC})
print(CONT["2025"]["Total"], list(CONT["2025"])[:4])
json.dump({"nacionalidades": NAC, "continente_distrito": CONT}, open(pathlib.Path(__file__).parent / "extranjeros_anuario.json", "w", encoding="utf-8"), ensure_ascii=False)
