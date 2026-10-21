import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, os, sys
parcels = json.load(open('parcels.json'))
out = {}
if os.path.exists('parcels_xy.json'):
    out = json.load(open('parcels_xy.json'))
base = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_CPMRC"
n = 0
for rc in parcels:
    if rc in out: continue
    q = urllib.parse.urlencode({"Provincia": "", "Municipio": "", "SRS": "EPSG:4326", "RC": rc})
    try:
        with urllib.request.urlopen(base + "?" + q, timeout=30) as r:
            xmlt = r.read().decode("utf-8", "replace")
        root = ET.fromstring(xmlt)
        ns = {"c": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
        x = root.find(".//{*}xcen"); y = root.find(".//{*}ycen"); ld = root.find(".//{*}ldt")
        out[rc] = [float(y.text), float(x.text), (ld.text if ld is not None else "")] if x is not None and y is not None else None
    except Exception as e:
        out[rc] = None
    n += 1
    if n % 25 == 0:
        json.dump(out, open('parcels_xy.json', 'w'), ensure_ascii=False)
    time.sleep(0.4)
json.dump(out, open('parcels_xy.json', 'w'), ensure_ascii=False)
open('geocode_done.txt', 'w').write(str(len(out)))
