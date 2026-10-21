import json, re, sys, urllib.request, urllib.parse, time, unicodedata
# Geocodifica las VUT del registro GVA (València ciudad) con el geocodificador municipal (ArcGIS), por lotes, con validación de nombre de vía.
base = "https://geoportal.valencia.es/server/rest/services/Geocodificadores/Callejero_Municipal/GeocodeServer/geocodeAddresses"
rows = json.load(open("gva_valencia.json", encoding="utf-8"))
TIPO = {"C": "CARRER", "CL": "CARRER", "AV": "AVINGUDA", "PZ": "PLAÇA", "PL": "PLAÇA", "PS": "PASSEIG", "CM": "CAMI", "GV": "GRAN VIA", "CR": "CARRETERA", "RD": "RONDA", "TR": "TRAVESSERA", "PJ": "PASSATGE", "PQ": "PARC", "GL": "GLORIETA", "PD": "PARTIDA", "UR": "URBANITZACIO", "AL": "ALAMEDA", "CJ": "CALLEJON", "CT": "CUESTA", "LG": "LUGAR", "PO": "POLIGON", "SD": "SENDA", "BO": "BARRI", "CN": "CAMI", "JR": "JARDINS", "RB": "RAMBLA", "VI": "VIA", "CS": "CASERIA", "BL": "BLOC"}
STOP = {"DE", "DEL", "LA", "EL", "LES", "LOS", "LAS", "D", "L", "DELS", "DE LA", "Y", "I", "EN", "SANT", "SAN", "SANTA", "CALLE", "CARRER", "AVENIDA", "AVINGUDA", "PLAZA", "PLAÇA", "PASEO", "PASSEIG", "CAMINO", "CAMI", "GRAN", "VIA", "DOCTOR", "DR", "PINTOR", "POETA", "MUSICO", "MUSIC", "ARQUITECTO", "ARQUITECTE", "ESCULTOR", "MAESTRO", "MESTRE", "PADRE", "PARE", "GENERAL", "MARQUES", "CONDE", "COMTE", "DUQUE", "DUC", "OBISPO", "BISBE", "ALCALDE", "INGENIERO", "ENGINYER", "VALENCIA", "VALÈNCIA"}
def strip_acc(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().upper()
def norm(d):
    d = re.sub(r"\s+(Es|Pl|Pt|Bl|Esc|Pta):\S+", "", d or "").strip().rstrip(", ")
    m = re.match(r"^([A-Z]{1,2})\s+(.*?),\s*(\d+)\b", d)
    if m:
        return f"{TIPO.get(m.group(1), m.group(1))} {m.group(2)} {m.group(3)}"
    m = re.match(r"^([A-Z]{1,2})\s+(.*)$", d)
    if m:
        return f"{TIPO.get(m.group(1), m.group(1))} {m.group(2)}"
    return d
def toks(s):
    return {t for t in re.split(r"[^A-Z0-9]+", strip_acc(s)) if len(t) >= 3 and t not in STOP}
def valid(q, cand):
    tq, tc = toks(re.sub(r"\s\d+$", "", q)), toks(re.sub(r"\s\d+$", "", cand))
    if not tq: return True
    inter = len(tq & tc)
    return inter >= 1 and inter >= len(tq) / 2
keys = {}
for r in rows:
    k = norm(r["direccion"])
    if k: keys.setdefault(k, []).append(r["signatura"])
addrs = list(keys)
print(len(rows), "VUT,", len(addrs), "direcciones unicas")
out = {}
B = 100
for i in range(0, len(addrs), B):
    batch = addrs[i:i+B]
    recs = {"records": [{"attributes": {"OBJECTID": j, "SingleLine": a + ", VALENCIA"}} for j, a in enumerate(batch)]}
    data = urllib.parse.urlencode({"addresses": json.dumps(recs, ensure_ascii=False), "outSR": 4326, "f": "json"}).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(base, data=data), timeout=120) as resp:
            j = json.load(resp)
        for loc in j.get("locations", []):
            a = loc["attributes"]; idx = a.get("ResultID", a.get("OBJECTID"))
            if idx is None or idx >= len(batch): continue
            sc = loc.get("score", 0); g = loc.get("location") or {}; cand = loc.get("address", "")
            ok = sc >= 70 and g.get("x") and valid(batch[idx], cand)
            out[batch[idx]] = [round(g.get("y", 0), 6), round(g.get("x", 0), 6), sc, cand] if ok else None
    except Exception as e:
        print("batch error", i, e)
    json.dump(out, open("addr_xy.json", "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.3)
ok = sum(1 for v in out.values() if v)
print("hecho:", ok, "de", len(addrs), "direcciones geocodificadas")
bad = [a for a, v in out.items() if not v]
print("fallidas (muestra):", bad[:15])
