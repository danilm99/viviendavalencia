#!/usr/bin/env python3
"""Construye data/listings.json (Inside Airbnb detallado o resumen) y data/extra.json (CATAV, barrios).
Uso: python3 -I build_data.py raw/detailed_listings.csv "etiqueta"
"""
import csv, json, re, sys, html, pathlib, statistics

csv.field_size_limit(10**9)
ROOT = pathlib.Path(__file__).parent
ROOM = {"Entire home/apt": 0, "Private room": 1, "Shared room": 2, "Hotel room": 3}
VT_RE = re.compile(r"\bVT[\s\-]?(\d{3,6})[\s\-]?([A-Z]?)\b", re.I)
CVVUT_RE = re.compile(r"\b(CV-?VUT-?\d{3,7})\b", re.I)
NAT_RE = re.compile(r"\b(ES[A-Z]{4}\d{6,}[A-Z0-9]*)\b")
# clase de licencia: 0 sin registro · 1 VT/CV-VUT Generalitat · 2 solo nacional turístico (ESFCTU/ESHFTU)
#                    3 nacional NO turístico / temporada (ESFCNT/ESHFNT) · 4 exento (hotel, hostal...) · 5 otro texto
LIC_LABELS = ["Sin nº de registro", "Registro turístico GVA (VT)", "Solo nº nacional turístico", "Nº nacional de temporada (no turístico)", "Exento (hotel/hostal/otros)", "Otro texto"]


def lic_class(s):
    if not s or not s.strip():
        return 0, "", ""
    s = html.unescape(s).replace("<br />", " ").replace("<br>", " ")
    vt = VT_RE.search(s); cv = CVVUT_RE.search(s); nat = NAT_RE.search(s)
    vtn = f"VT-{vt.group(1)}-{(vt.group(2) or 'V').upper()}" if vt else (cv.group(1).upper() if cv else "")
    natn = nat.group(1) if nat else ""
    if vtn:
        return 1, vtn, natn
    if natn:
        code = natn[2:6]
        if code in ("FCTU", "HFTU"):
            return 2, "", natn
        if code in ("FCNT", "HFNT"):
            return 3, "", natn
    if "exempt" in s.lower() or "exent" in s.lower():
        return 4, "", natn
    return 5, "", natn


def num(s):
    if s is None:
        return None
    s = str(s).strip().replace("$", "").replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def ival(s, d=0):
    v = num(s)
    return int(v) if v is not None else d


def main():
    path, label = sys.argv[1], sys.argv[2]
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lat, lon = num(r.get("latitude")), num(r.get("longitude"))
            if lat is None or lon is None:
                continue
            lc, vt, nat = lic_class(r.get("license", ""))
            price = num(r.get("price"))
            rating = num(r.get("review_scores_rating"))
            rec = [
                int(r["id"]), round(lat, 5), round(lon, 5),
                (r.get("name") or "").strip()[:140],
                ROOM.get(r.get("room_type", ""), 1),
                round(price) if price else None,
                (r.get("neighbourhood_cleansed") or r.get("neighbourhood") or "").strip(),
                (r.get("neighbourhood_group_cleansed") or r.get("neighbourhood_group") or "").strip(),
                vt,
                (r.get("host_name") or "").strip()[:60],
                ival(r.get("calculated_host_listings_count") or r.get("host_listings_count")),
                ival(r.get("number_of_reviews")),
                (r.get("last_review") or "")[:10],
                ival(r.get("availability_365")),
                ival(r.get("minimum_nights")),
                nat,
                ival(r.get("host_id")),
                lc,
                ival(r.get("accommodates")),
                ival(r.get("bedrooms")),
                (r.get("property_type") or "")[:40],
                ival(r.get("estimated_occupancy_l365d")),
                ival(r.get("estimated_revenue_l365d")),
                round(rating, 2) if rating else None,
                (r.get("host_since") or "")[:4],
                ival(r.get("host_total_listings_count")),
                (r.get("host_location") or "")[:40],
                1 if (r.get("host_is_superhost") == "t") else 0,
                ival(r.get("number_of_reviews_ltm")),
                (r.get("first_review") or "")[:4],
            ]
            rows[rec[0]] = rec
    # cruce con el registro de la Generalitat (dataset abierto filtrado a València ciudad)
    gva_rows = json.load(open(ROOT / "raw/gva_valencia.json", encoding="utf-8"))
    gva_keys = {}
    for g in gva_rows:
        m = re.match(r"CV-VUT0*(\d+)-?([A-Z]*)", g["signatura"])
        if m:
            gva_keys[m.group(1) + "-" + (m.group(2) or "V")] = g
    def vt_key(vt):
        m = re.match(r"VT-(\d+)-([A-Z])", vt)
        if m:
            return m.group(1).lstrip("0") + "-" + m.group(2)
        m = re.match(r"CV-?VUT-?0*(\d+)-?([A-Z]*)", vt)
        if m:
            return m.group(1) + "-" + (m.group(2) or "V")
        return vt
    for rec in rows.values():
        rec.append((1 if vt_key(rec[8]) in gva_keys else 0) if rec[8] else None)
    data = sorted(rows.values(), key=lambda x: x[0])
    fields = ["id", "lat", "lon", "name", "room", "price", "barrio", "distrito", "vt", "host", "host_n", "reviews",
              "last_review", "avail365", "min_nights", "nat_reg", "host_id", "lic", "accommodates", "bedrooms",
              "property_type", "occ365", "rev365", "rating", "host_since", "host_total", "host_loc", "superhost", "reviews_ltm", "first_review", "vt_reg"]
    meta = {"source": label, "count": len(data), "fields": fields,
            "room_labels": ["Vivienda completa", "Habitación privada", "Habitación compartida", "Habitación de hotel"],
            "lic_labels": LIC_LABELS}
    (ROOT / "data").mkdir(exist_ok=True)
    with open(ROOT / "data/listings.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "rows": data}, f, ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print(len(data), "anuncios", Counter(d[17] for d in data))

    # ---- extra: CATAV + barrios ----
    raw = ROOT / "raw"
    def load(p):
        return json.load(open(raw / p, encoding="utf-8"))
    def pts(fc, keep):
        out = []
        for ft in fc["features"]:
            g = ft.get("geometry")
            if not g or g.get("type") != "Point":
                continue
            p = ft["properties"]
            vals = []
            for k in keep:
                v = p.get(k)
                if k in ("barrio", "distrito") and isinstance(v, str):
                    v = re.sub(r"^\d+\s*-\s*", "", v).strip()
                if k == "fecha_registro" and isinstance(v, (int, float)):
                    import datetime
                    v = datetime.datetime.utcfromtimestamp(v / 1000).strftime("%Y-%m-%d")
                vals.append(v)
            out.append([round(g["coordinates"][1], 5), round(g["coordinates"][0], 5)] + vals)
        return out
    catav = {
        "vut": {"fields": ["lat", "lon", "barrio", "distrito", "emplazamiento", "num_vut", "num_vut_pb", "plazas", "estado", "tipo_titulo", "fecha"],
                "rows": pts(load("catav_vut.geojson"), ["barrio", "distrito", "emplazamiento", "num_vut", "num_vut_pb", "plazas_alojamiento", "estado", "tipo_titulo", "fecha_registro"])},
        "uat": {"fields": ["lat", "lon", "barrio", "distrito", "emplazamiento", "num_uat", "num_uat_pb", "plazas", "estado", "tipo_titulo", "fecha"],
                "rows": pts(load("catav_uat.geojson"), ["barrio", "distrito", "emplazamiento", "num_uat", "num_uat_pb", "plazas_alojamiento", "estado", "tipo_titulo", "fecha_registro"])},
        "hot": {"fields": ["lat", "lon", "barrio", "distrito", "emplazamiento", "tipo", "plazas", "estado", "tipo_titulo", "fecha"],
                "rows": pts(load("catav_hoteles.geojson"), ["barrio", "distrito", "emplazamiento", "tipo", "plazas_alojamiento", "estado", "tipo_titulo", "fecha_registro"])},
    }
    excl = load("ambitos_excluidos_vut.geojson")
    for ft in excl["features"]:
        ft["properties"] = {"nombre": ft["properties"].get("nombre")}
        def rnd(c):
            return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 5), round(c[1], 5)]
        ft["geometry"]["coordinates"] = rnd(ft["geometry"]["coordinates"])
    barrios = {b["barrio"]: {"pob": b["total_poblacion"], "viv": b["total_viviendas"]} for b in load("barrios_poblacion_viviendas.json")}
    if "MONTOLIVET" in barrios and "MONT-OLIVET" not in barrios:
        barrios["MONT-OLIVET"] = barrios.pop("MONTOLIVET")
    for lay in catav.values():
        bi = lay["fields"].index("barrio")
        for r in lay["rows"]:
            if r[bi] == "MONTOLIVET":
                r[bi] = "MONT-OLIVET"
    used = Counter(vt_key(d[8]) for d in data if d[8])
    gva = {
        "count": len(gva_rows), "plazas": sum(int(g["plazas_totales"] or 0) for g in gva_rows),
        "by_year": dict(Counter((g["fecha_alta"] or "")[-4:] for g in gva_rows)),
        "by_cp": dict(Counter(g["cp"] for g in gva_rows if g["cp"])),
        "airbnb_vt": sum(1 for d in data if d[8]), "airbnb_vt_found": sum(1 for d in data if d[8] and d[-1] == 1),
        "vt_shared": sum(1 for k, n in used.items() if n > 1), "vt_shared_listings": sum(n for k, n in used.items() if n > 1),
        "registry_unused": sum(1 for k in gva_keys if k not in used),
        "meta": "Registro de Turismo de la Comunitat Valenciana, dataset abierto 'Viviendas turísticas' (dadesobertes.gva.es), filtrado al municipio de València, descargado 2026-10-19",
    }
    # capa geolocalizada del registro: geocodificador municipal (direcciones) + Catastro (parcelas) como respaldo
    xy_path = raw / "parcels_xy.json"; ad_path = raw / "addr_xy.json"
    xy = {}; ad = {}
    if xy_path.exists():
        try:
            xy = json.load(open(xy_path, encoding="utf-8"))
        except UnicodeDecodeError:
            xy = json.load(open(xy_path, encoding="cp1252"))
    if ad_path.exists():
        ad = json.load(open(ad_path, encoding="utf-8"))
    TIPO = {"C": "CARRER", "CL": "CARRER", "AV": "AVINGUDA", "PZ": "PLAÇA", "PL": "PLAÇA", "PS": "PASSEIG", "CM": "CAMI", "GV": "GRAN VIA", "CR": "CARRETERA", "RD": "RONDA", "TR": "TRAVESSERA", "PJ": "PASSATGE", "PQ": "PARC", "GL": "GLORIETA", "PD": "PARTIDA", "UR": "URBANITZACIO", "AL": "ALAMEDA", "CJ": "CALLEJON", "CT": "CUESTA", "LG": "LUGAR", "PO": "POLIGON", "SD": "SENDA", "BO": "BARRI", "CN": "CAMI", "JR": "JARDINS", "RB": "RAMBLA", "VI": "VIA", "CS": "CASERIA", "BL": "BLOC"}
    def anorm(d):
        d = re.sub(r"\s+(Es|Pl|Pt|Bl|Esc|Pta):\S+", "", d or "").strip().rstrip(", ")
        m = re.match(r"^([A-Z]{1,2})\s+(.*?),\s*(\d+)\b", d)
        if m:
            return f"{TIPO.get(m.group(1), m.group(1))} {m.group(2)} {m.group(3)}"
        m = re.match(r"^([A-Z]{1,2})\s+(.*)$", d)
        if m:
            return f"{TIPO.get(m.group(1), m.group(1))} {m.group(2)}"
        return d
    parc = {}; n_addr = n_parc = 0
    for g in gva_rows:
        ak = anorm(g["direccion"]); rc = g["ref_catastral"].strip()[:14]
        if ak and ad.get(ak):
            key = "A:" + ak; lat, lon, label = ad[ak][0], ad[ak][1], ad[ak][3]; src = "a"
        elif rc and xy.get(rc):
            key = "P:" + rc; lat, lon, label = xy[rc][0], xy[rc][1], xy[rc][2] or ak; src = "p"
        else:
            continue
        o = parc.setdefault(key, {"lat": lat, "lon": lon, "addr": label or ak, "n": 0, "plazas": 0, "years": [], "sig": [], "ab": 0, "src": src})
        o["n"] += 1; o["plazas"] += int(g["plazas_totales"] or 0)
        y = (g["fecha_alta"] or "")[-4:]
        if y: o["years"].append(y)
        m = re.match(r"CV-VUT0*(\d+)-?([A-Z]*)", g["signatura"])
        k = (m.group(1) + "-" + (m.group(2) or "V")) if m else g["signatura"]
        o["sig"].append(k)
        if k in used: o["ab"] += 1
    gva["fields"] = ["lat", "lon", "addr", "n", "plazas", "year_min", "year_max", "sigs", "airbnb_n"]
    gva["rows"] = [[round(o["lat"], 5), round(o["lon"], 5), (o["addr"] or "")[:80].title(), o["n"], o["plazas"], min(o["years"]) if o["years"] else "", max(o["years"]) if o["years"] else "", " ".join(o["sig"][:12]) + (" …" if len(o["sig"]) > 12 else ""), o["ab"]] for o in parc.values()]
    gva["geocoded"] = sum(o["n"] for o in parc.values())
    print("GVA geolocalizadas", len(parc), "edificios,", gva["geocoded"], "VUT (", sum(o["n"] for o in parc.values() if o["src"] == "a"), "por direccion,", sum(o["n"] for o in parc.values() if o["src"] == "p"), "por parcela )")
    print("GVA", gva["count"], "airbnb VT found", gva["airbnb_vt_found"], "/", gva["airbnb_vt"], "shared", gva["vt_shared"], "unused", gva["registry_unused"])
    with open(ROOT / "data/extra.json", "w", encoding="utf-8") as f:
        json.dump({"catav": catav, "excluidos": excl, "barrios": barrios, "gva": gva,
                   "catav_meta": "Censo de Alojamientos Turísticos del Ayuntamiento de València (CATAV), geoportal municipal, descargado 2026-10-19"},
                  f, ensure_ascii=False, separators=(",", ":"))
    print("catav vut", len(catav["vut"]["rows"]), "uat", len(catav["uat"]["rows"]), "hot", len(catav["hot"]["rows"]), "barrios", len(barrios))
    est = Counter(r[8] for r in catav["vut"]["rows"]); print("estados VUT", est)
    print("num_vut total", sum((r[5] or 0) for r in catav["vut"]["rows"]), "plazas", sum((r[7] or 0) for r in catav["vut"]["rows"]))
    # cruce nombres barrio
    nb = set(d[6] for d in data); print("barrios airbnb no en CATAV:", nb - set(barrios))


if __name__ == "__main__":
    main()
