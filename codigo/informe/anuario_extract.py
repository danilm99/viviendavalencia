#!/usr/bin/env python3
"""Extrae series del Anuario Estadístico de València (xlsx 2017-2025) → vivienda/anuario.json"""
import openpyxl, glob, re, json, pathlib, collections
ROOT = pathlib.Path(__file__).parent
RAW = ROOT / "raw/anuario"

DIST = ["Ciutat Vella", "l'Eixample", "Extramurs", "Campanar", "la Saïdia", "el Pla del Real", "l'Olivereta", "Patraix", "Jesús", "Quatre Carreres", "Poblats Marítims", "Camins al Grau", "Algirós", "Benimaclet", "Rascanya", "Benicalap", "Pobles del Nord", "Pobles de l'Oest", "Pobles del Sud"]
def dname(s):
    s = re.sub(r"^\s*\d+\.\s*", "", str(s))
    s = re.sub(r"\(\s*\d\s*\)|\*", "", s).strip()
    for d in DIST:
        if s.lower() == d.lower(): return d
    return None
def num(v):
    if isinstance(v, (int, float)): return v
    if isinstance(v, str):
        t = v.strip().replace(".", "").replace(",", ".")
        try: return float(t)
        except: return None
    return None

def sheets(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        title = ""
        for r in rows[:4]:
            for v in r:
                if isinstance(v, str) and len(v) > 8: title = v; break
            if title: break
        out[ws.title] = (title, rows)
    return out

def find(all_sheets, pat):
    """devuelve (year_anuario, title, rows) de hojas cuyo título casa con pat"""
    res = []
    for y, book, sh, title, rows in all_sheets:
        if re.search(pat, title, re.I): res.append((y, book, sh, title, rows))
    return res

all_sheets = []
for f in sorted(glob.glob(str(RAW / "*/*.xlsx"))):
    y = int(pathlib.Path(f).parent.name)
    try:
        for sh, (title, rows) in sheets(f).items():
            all_sheets.append((y, pathlib.Path(f).name, sh, title, rows))
    except Exception as e:
        print("ERR", f, e)
print(len(all_sheets), "hojas")

def year_of(title):
    m = re.findall(r"(20\d\d)", title); return int(m[-1]) if m else None
def row_by_label(rows, label_pat, start=0):
    for r in rows[start:]:
        if r and isinstance(r[0], str) and re.search(label_pat, r[0], re.I): return r
    return None
def district_table(rows, ncols=1, first_col=1):
    """filas de distrito → {distrito: [vals]}"""
    out = {}
    for r in rows:
        if not r or r[0] is None: continue
        d = dname(r[0])
        if d:
            vals = [num(v) for v in r[first_col:first_col + ncols]]
            out[d] = vals if ncols > 1 else vals[0]
    return out

A = {}

# ---- 1. Mercado de alquiler SERPAVI: ciudad 2014-2023 ----
for y, book, sh, title, rows in find(all_sheets, r"Evolución del mercado de alquiler de vivienda en la ciudad"):
    yrs = [int(v) for v in rows[2] if isinstance(v, (int, float))]
    def ser(label, start):
        r = row_by_label(rows, label, start); return dict(zip(yrs, [num(v) for v in r[1:1 + len(yrs)]])) if r else None
    A["serpavi_city"] = {"src": "Sistema estatal de referencia del precio del alquiler (MIVAU) vía Anuario Estadístico 2025, tabla 4.10.2",
        "viviendas_alquiladas": ser(r"^Viviendas alquiladas", 0),
        "col_mediana_eur": ser(r"^Mediana", 10), "col_p25_eur": ser(r"^Percentil 25", 10), "col_p75_eur": ser(r"^Percentil 75", 10),
        "col_mediana_m2": ser(r"^Mediana", 14), "col_superficie_mediana": ser(r"^Mediana", 6)}
    break

# ---- 2. SERPAVI por distrito (varios años): cuantía mensual mediana colectivas + nº viviendas ----
A["serpavi_district"] = {}
for y, book, sh, title, rows in find(all_sheets, r"Cuantía total mensual del alquiler según tipo de vivienda.*distrito"):
    yr = year_of(title)
    A["serpavi_district"].setdefault(str(yr), {})["renta_mediana"] = district_table(rows, 3)
for y, book, sh, title, rows in find(all_sheets, r"Número de viviendas alquiladas según tipo por distrito"):
    yr = year_of(title)
    A["serpavi_district"].setdefault(str(yr), {})["viviendas"] = district_table(rows, 1)
for y, book, sh, title, rows in find(all_sheets, r"Superficie de las viviendas alquiladas según tipo por distrito"):
    yr = year_of(title)
    A["serpavi_district"].setdefault(str(yr), {})["superficie_mediana"] = district_table(rows, 1)
# 2022 Cap04 "Cuantía ... Distritos. 2020" has different label order; handled by same pattern

# ---- 3. SERPAVI por barrio 2023 ----
for y, book, sh, title, rows in find(all_sheets, r"Mercado de alquiler de vivienda por barrio"):
    yr = year_of(title); out = {}; dist = None
    for r in rows[4:]:
        if not r or r[0] is None: continue
        s = str(r[0])
        if re.match(r"^\s*\d+\.\s", s) and not re.match(r"^\s{3,}", s): dist = dname(s); continue
        m = re.match(r"^\s+\d+\.\s*(.+)$", s)
        if m and dist and r[1] is not None:
            out[m.group(1).strip()] = {"distrito": dist, "n": num(r[1]), "sup": num(r[2]), "renta": num(r[3]), "m2": num(r[4])}
    A["serpavi_barrio_" + str(yr)] = out

# ---- 4. Transacciones por año ----
tr = {}
for y, book, sh, title, rows in find(all_sheets, r"Transacciones inmobiliarias de viviendas según tipo( de la vivienda)?\.\s*20\d\d"):
    yr = year_of(title)
    hdr = rows[2]; idx = [i for i, v in enumerate(hdr) if v == "València"]
    if not idx: continue
    i = idx[0]
    g = lambda pat: (lambda r: num(r[i]) if r else None)(row_by_label(rows, pat))
    tr[str(yr)] = {"total": g(r"^Total$"), "nueva": g(r"^Vivienda nueva"), "segunda": g(r"^Vivienda segunda"), "libre": g(r"^Vivienda libre"), "protegida": g(r"^Vivienda protegida")}
A["transacciones"] = dict(sorted(tr.items()))

# ---- 5. idealista por distrito: alquiler y venta (media anual y diciembre) ----
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
def monthly_district(rows):
    out = {}
    for r in rows:
        if not r or r[0] is None: continue
        d = dname(r[0]) or ("València" if str(r[0]).strip().startswith("València") else None)
        if d:
            vals = [num(v) for v in r[1:13]]
            vals = [v for v in vals if v is not None]
            if vals: out[d] = {"media": round(sum(vals) / len(vals), 2), "dic": vals[-1], "n": len(vals)}
    return out
A["idealista_district_rent"] = {}; A["idealista_district_sale"] = {}
for y, book, sh, title, rows in find(all_sheets, r"Precio medio( mensual)? de alquiler de las viviendas de segunda mano en el portal inmobiliari[oa]? Idealista.*(Distritos|por distrito)"):
    A["idealista_district_rent"][str(year_of(title))] = monthly_district(rows)
for y, book, sh, title, rows in find(all_sheets, r"Precio medio( mensual)? de venta de las viviendas de segunda mano en el portal inmobiliari[oa]? Idealista.*(Distritos|por distrito)"):
    A["idealista_district_sale"][str(year_of(title))] = monthly_district(rows)
# Cap04 older books: title "3.11. Precio medio de alquiler de las viviendas de segunda mano según distrito. 2016"
for y, book, sh, title, rows in find(all_sheets, r"Precio medio de alquiler de las viviendas de segunda mano(\.| según) (Distritos|distrito)"):
    yr = str(year_of(title))
    if yr not in A["idealista_district_rent"]: A["idealista_district_rent"][yr] = monthly_district(rows)

# ---- 6. Catastro: inmuebles residenciales por barrio y valores por distrito (último) ----
for y, book, sh, title, rows in sorted(find(all_sheets, r"Bienes Inmuebles según uso por barrio"), key=lambda x: x[0]):
    yr = year_of(title); out = {}; dist = None
    for r in rows[3:]:
        if not r or r[0] is None: continue
        s = str(r[0])
        if dname(s) and not re.match(r"^\s{3,}", s): dist = dname(s); continue
        m = re.match(r"^\s+\d+\.\s*(.+)$", s)
        if m and dist and r[1] is not None:
            out[m.group(1).strip()] = {"distrito": dist, "total": num(r[1]), "residencial": num(r[2]), "comercial": num(r[4])}
    A["catastro_barrio"] = {"year": yr, "rows": out}
for y, book, sh, title, rows in sorted(find(all_sheets, r"Valores catastrales medios.*por distrito"), key=lambda x: x[0]):
    A["catastro_valor_distrito"] = {"year": year_of(title), "rows": district_table(rows, 5)}
for y, book, sh, title, rows in sorted(find(all_sheets, r"Bienes Inmuebles según uso por distrito"), key=lambda x: x[0]):
    A["catastro_uso_distrito"] = {"year": year_of(title), "rows": district_table(rows, 6)}

# ---- 7. Padrón por distrito (varios años) y hojas familiares ----
A["poblacion_distrito"] = {}
for y, book, sh, title, rows in find(all_sheets, r"Densidad de población por distrito"):
    yr = year_of(title)
    hdr = rows[2]; col = next((i for i, v in enumerate(hdr) if isinstance(v, str) and v.startswith("Población") and str(yr) in v), 2)
    A["poblacion_distrito"][str(yr)] = district_table(rows, 1, col)
A["hogares_distrito"] = {}
for y, book, sh, title, rows in find(all_sheets, r"Hojas familiares según tamaño\. Distritos"):
    yr = year_of(title)
    A["hogares_distrito"][str(yr)] = district_table(rows, 2)

# ---- 8. Licencias viviendas por distrito (último) y serie VPNC ----
for y, book, sh, title, rows in sorted(find(all_sheets, r"Número de edificios, viviendas y garajes con licencia de construcción por distrito"), key=lambda x: x[0]):
    A["licencias_distrito"] = {"year": year_of(title), "rows": district_table(rows, 3)}
vp = {}
for y, book, sh, title, rows in find(all_sheets, r"Viviendas Protegidas de Nueva Construcción"):
    yr = year_of(title); r = row_by_label(rows, r"Calificaciones definitivas"); p = row_by_label(rows, r"Calificaciones provisionales")
    if r: vp[str(yr)] = {"definitivas": num(r[1]), "provisionales": num(p[1]) if p else None}
A["vpnc"] = dict(sorted(vp.items()))

# ---- 9. Tasación valor medio trimestral (serie) ----
tas = {}
for y, book, sh, title, rows in find(all_sheets, r"Valor de tasación medio de las viviendas libres"):
    yr = year_of(title); hdr = rows[2]; idx = [i for i, v in enumerate(hdr) if v == "València"]
    if not idx: continue
    i = idx[0]; q = 0
    for r in rows[3:12]:
        if r and isinstance(r[0], str) and "trimestre" in r[0].lower() and q < 4:
            q += 1; v = num(r[i])
            if v: tas[f"{yr}T{q}"] = v
A["tasado_trim"] = dict(sorted(tas.items()))

# ---- 10. Esfuerzo financiero por distrito (indicadores tasadas, último) ----
for y, book, sh, title, rows in sorted(find(all_sheets, r"Indicadores del mercado de venta de vivienda por distrito"), key=lambda x: x[0]):
    A["esfuerzo_distrito"] = {"year": year_of(title), "rows": {k: {"precio_4t": v[3], "esfuerzo_4t": v[7]} for k, v in district_table(rows, 12).items()}}

# ---- 11. Censo 2011 por barrio: vacías ----
for y, book, sh, title, rows in find(all_sheets, r"Viviendas según tipo de vivienda\. Barrio\. 2011"):
    out = {}; dist = None
    for r in rows[3:]:
        if not r or r[0] is None: continue
        s = str(r[0]); m = re.match(r"^(\d+)\.(\d+)\.\s*(.+)$", s)
        if m and r[1] is not None: out[m.group(3).strip()] = {"total": num(r[1]), "principales": num(r[2]), "secundarias": num(r[3]), "vacias": num(r[4])}
        elif re.match(r"^\d+\.\s", s): dist = dname(s)
    # por distrito agregando barrios
    A["censo2011_barrio"] = out
    dd = {}; dist = None
    for r in rows[3:]:
        if not r or r[0] is None: continue
        s = str(r[0]); m = re.match(r"^(\d+)\.(\d+)\.\s*(.+)$", s)
        if m and r[1] is not None and dist:
            o = dd.setdefault(dist, {"total": 0, "principales": 0, "secundarias": 0, "vacias": 0})
            for k, i in (("total", 1), ("principales", 2), ("secundarias", 3), ("vacias", 4)): o[k] += num(r[i]) or 0
        elif re.match(r"^\d+\.\s", s) and dname(s): dist = dname(s)
    A["censo2011_distrito"] = dd

json.dump(A, open(ROOT / "anuario.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for k, v in A.items():
    print(k, (len(v) if hasattr(v, "__len__") else v))
