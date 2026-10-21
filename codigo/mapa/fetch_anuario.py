"""Descarga los XLSX del Anuario Estadístico de València (capítulos 2 Demografía y 4 Edificación y vivienda) de todos los años.
Uso (en el PC): python -X utf8 fetch_anuario.py
Deja los archivos en .\anuario\<año>\<nombre>.xlsx y un índice anuario_index.json
"""
import re, json, os, urllib.request, urllib.parse, time, sys

BASE = "https://www.valencia.es/cas/estadistica/anuario-estadistica?capitulo={cap}&anyo={anyo}"
os.makedirs("anuario", exist_ok=True)
index = {}
hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
for anyo in range(2010, 2027):
    for cap in (2, 4):
        url = BASE.format(cap=cap, anyo=anyo)
        try:
            html = urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60).read().decode("utf-8", "replace")
        except Exception as e:
            print(anyo, cap, "ERR página", e); continue
        links = set(re.findall(r'href="([^"]+\.xlsx?)"', html, re.I))
        titles = re.findall(r'<a[^>]+href="([^"]+\.xlsx?)"[^>]*>(.*?)</a>', html, re.I | re.S)
        tmap = {}
        for href, t in titles:
            t = re.sub(r"<[^>]+>", "", t).strip()
            tmap.setdefault(href, []).append(t)
        n = 0
        for href in sorted(links):
            full = urllib.parse.urljoin("https://www.valencia.es/", href.replace("\\", "/"))
            name = os.path.basename(urllib.parse.urlparse(full).path)
            d = os.path.join("anuario", str(anyo)); os.makedirs(d, exist_ok=True)
            dest = os.path.join(d, name)
            key = f"{anyo}/{name}"
            index[key] = {"url": full, "cap": cap, "titles": tmap.get(href, [])}
            if os.path.exists(dest) and os.path.getsize(dest) > 1000:
                n += 1; continue
            try:
                urllib.request.urlretrieve(full, dest); n += 1; time.sleep(0.3)
            except Exception as e:
                print("  ERR", full, e)
        print(anyo, "cap", cap, ":", n, "archivos")
json.dump(index, open("anuario_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("índice:", len(index), "archivos")
