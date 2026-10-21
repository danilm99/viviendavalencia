#!/usr/bin/env python3
"""Extrae del Anuario: nacimientos (serie), indicadores natalidad por año, hojas padronales por tamaño (serie), nacimientos por distrito."""
import openpyxl, json, pathlib, re
RAW = pathlib.Path(__file__).parent / "raw" / "anuario"
OUT = {}

def rows(path, sheet):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet]
    return [list(r) for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]

def num(x):
    try:
        return float(x)
    except Exception:
        return None

# ---- nacimientos 2004-2023 (MNP)
r = rows(RAW / "2025/020501_NacimientosMNP.xlsx", "1")
OUT["nacimientos"] = {str(int(x[0])): int(x[1]) for x in r if isinstance(x[0], (int, float))}

# ---- indicadores natalidad por año
IND = {}
files = [(RAW / f"{y}/Cap02.xlsx", "4.9") for y in range(2017, 2023)]
files += [(RAW / "2023/020301_NacimientosMNP.xlsx", "9"), (RAW / "2024/020501_NacimientosMNP.xlsx", "9"), (RAW / "2025/020501_NacimientosMNP.xlsx", "9")]
for p, sh in files:
    try:
        r = rows(p, sh)
    except Exception as e:
        print("skip", p, e); continue
    m = re.search(r"(20\d\d)\s*$", str(r[0][0]).strip())
    y = m.group(1) if m else None
    d = {}
    for x in r[1:]:
        k = str(x[0]).strip().lower()
        v = num(x[1])
        if v is None: continue
        if "bruta de natalidad" in k: d["tbn"] = round(v, 2)
        elif "general de fecundidad" in k: d["tgf"] = round(v, 2)
        elif "descendientes por mujer" in k: d["isf"] = round(v, 3)
        elif "maternidad al primer" in k: d["edad_primer_hijo"] = round(v, 2)
        elif "edad media a la maternidad" in k: d["edad_maternidad"] = round(v, 2)
        elif "no casada" in k: d["pct_no_casada"] = round(v * 100 if v < 1 else v, 1)
    if y: IND[y] = d
OUT["natalidad_ind"] = dict(sorted(IND.items()))

# ---- hojas por tamaño (total ciudad) por año
HT = {}
files = [(RAW / f"{y}/Cap02.xlsx", "3.2", y) for y in range(2017, 2023)]
files += [(RAW / "2023/020201_HojasPadronales.xlsx", "2", 2023), (RAW / "2024/020102_HojasPadronales.xlsx", "2", 2024), (RAW / "2025/020102_HojasPadronales.xlsx", "2", 2025)]
for p, sh, y in files:
    try:
        r = rows(p, sh)
    except Exception as e:
        print("skip", p, e); continue
    m = re.search(r"(20\d\d)\s*$", str(r[0][0]).strip()); yy = m.group(1) if m else str(y)
    hdr = [str(c).strip() if c else "" for c in r[1]]
    tot = next((x for x in r if str(x[0]).strip().lower() == "total"), None)
    if not tot: print("no total", p); continue
    d = {}
    for h, v in zip(hdr[1:], tot[1:]):
        if h and num(v) is not None: d[h.replace("\n", " ")] = num(v)
    HT[yy] = d
    if yy == "2025":
        dist = {}
        for x in r[2:]:
            if x[0] and re.match(r"\s*\d+\.", str(x[0])):
                dist[str(x[0]).strip()] = {h.replace("\n", " "): num(v) for h, v in zip(hdr[1:], x[1:]) if h}
        OUT["hojas_tamano_distrito_2025"] = dist
OUT["hojas_tamano"] = dict(sorted(HT.items()))
print(json.dumps(HT, ensure_ascii=False)[:1500])

# ---- nacimientos padrón por distrito (último)
r = rows(RAW / "2025/020103_AltasBajasPadron.xlsx", "1")
print([str(c)[:30] for c in r[1][:10]])
print(r[2][:10]); print(r[3][:10])
ND = {}
for x in r[2:]:
    if x[0] and re.match(r"\s*\d+\.", str(x[0])):
        ND[str(x[0]).strip()] = [num(c) for c in x[1:9]]
OUT["nac_def_distrito_hdr"] = [str(c).replace("\n", " ") if c else "" for c in r[1][:9]]
OUT["nac_def_distrito"] = ND

# ---- composición hojas 2025 por distrito (solo 0-24, solo 65+, menores)
r = rows(RAW / "2025/020102_HojasPadronales.xlsx", "3")
hdr = [str(c).replace("\n", " ").strip() if c else "" for c in r[1]]
OUT["hojas_comp_2025"] = {str(x[0]).strip(): {h: num(v) for h, v in zip(hdr[1:], x[1:]) if h} for x in r[2:] if x[0] and (re.match(r"\s*\d+\.", str(x[0])) or str(x[0]).strip() == "Total")}

json.dump(OUT, open(pathlib.Path(__file__).parent / "demo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(OUT["natalidad_ind"], ensure_ascii=False))
print(OUT["nacimientos"])
