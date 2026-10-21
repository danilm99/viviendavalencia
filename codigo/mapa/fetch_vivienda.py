"""Descarga datasets del parque de vivienda de València (ejecutar en el PC):
   python -X utf8 fetch_vivienda.py
Deja todo en .\vivienda_raw\ y escribe vivienda_raw\index.json con el resultado de cada descarga.
"""
import os, re, json, time, urllib.request, urllib.parse

OUT = "vivienda_raw"; os.makedirs(OUT, exist_ok=True)
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36", "Accept": "*/*"}
log = {}

def get(url, dest, binary=True, retries=2):
    p = os.path.join(OUT, dest)
    if os.path.exists(p) and os.path.getsize(p) > 200:
        log[dest] = {"url": url, "ok": True, "bytes": os.path.getsize(p), "cached": True}; return p
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            open(p, "wb").write(data)
            log[dest] = {"url": url, "ok": True, "bytes": len(data)}
            print("OK ", dest, len(data)); time.sleep(0.4); return p
        except Exception as e:
            err = str(e)[:120]; time.sleep(1.5)
    log[dest] = {"url": url, "ok": False, "error": err}; print("ERR", dest, err); return None

def html(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=120).read().decode("utf-8", "replace")
    except Exception as e:
        print("ERR html", url, str(e)[:100]); return ""

# ---------- INE ----------
ine_tables = {  # id jaxiT3 / tpx -> nombre
    "tpx": {"59525": "censo21_tipo_vivienda_municipios", "59527": "censo21_anyo_construccion", "59528": "censo21_tipo_superficie",
            "59529": "censo21_tenencia", "59531": "censo21_consumo_electrico", "59543": "censo21_hogares_tipo", "59544": "censo21_hogares_tamano"},
    "t": {"80271": "ipv_ccaa_anual", "80270": "ipv_ccaa_trimestral", "31097": "atlas_renta_distritos", "6150": "etdp_provincias_mensual",
          "25171": "padron_municipios_serie"},
}
for tpx, name in ine_tables["tpx"].items():
    get(f"https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/{tpx}.csv", f"ine_{name}.csv")
for t, name in ine_tables["t"].items():
    get(f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{t}.csv", f"ine_{name}.csv")
# INE API: hipotecas por provincia (operación H) y ETDP municipio no existen; buscamos tablas de la operación "Hipotecas" (código 'H')
for op in ("EH", "H", "ETDP", "ADRH", "IPV"):
    get(f"https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{op}", f"ine_api_tablas_{op}.json")
get("https://ine.es/prensa/anexo_tablas/es/ADRH2023.xlsx", "ine_adrh2023.xlsx")
get("https://ine.es/prensa/anexo_tablas/es/H1225.xlsx", "ine_hipotecas_dic2025.xlsx")
get("https://ine.es/prensa/anexo_tablas/es/IPV4T25.xlsx", "ine_ipv_4t25.xlsx")
get("https://ine.es/prensa/censo_2021_jun.pdf", "ine_censo2021_viviendas_np.pdf")

# ---------- GVA fianzas 2020-2026 ----------
for y in range(2020, 2027):
    page = html(f"https://dadesobertes.gva.es/es/dataset/viv-reg-fia-{y}")
    links = re.findall(r'href="(https://dadesobertes\.gva\.es/dataset/[^"]+/download/[^"]+\.(?:csv|xlsx|json))"', page, re.I)
    links = [l for l in links if l.lower().endswith(".csv")] or links
    if links:
        get(links[0], f"gva_fianzas_{y}{os.path.splitext(links[0])[1].lower()}")
    else:
        log[f"gva_fianzas_{y}"] = {"ok": False, "error": "sin enlace csv en la página"}; print("ERR fianzas", y)
# GVA otros datasets de vivienda (índice)
get("https://dadesobertes.gva.es/es/api/3/action/package_search?q=vivienda+OR+habitatge+OR+alquiler+OR+lloguer&rows=200", "gva_package_search_vivienda.json")

# ---------- Oficina d'Estadística València ----------
get("https://www.valencia.es/estadistica/UltDatos/PrecioVivienda_cast.xlsx", "vlc_ultdatos_precio_vivienda.xlsx")
for f in ("F04051000", "F04102000", "F04102040", "F04102010", "M06255020C"):
    get(f"https://www.valencia.es/estadistica/IndSoc/{f}.pdf", f"vlc_indsoc_{f}.pdf")
for y in range(2015, 2026):
    get(f"https://www.valencia.es/estadistica/Recull/Recull{y}_Castellano.pdf", f"vlc_recull_{y}.pdf")
get("https://www.valencia.es/estadistica/Padron/2024/Padron2024Cast.pdf", "vlc_padron2024.pdf")

# ---------- CGPJ lanzamientos ----------
get("https://www.poderjudicial.es/stfls/ESTADISTICA/FICHEROS/Crisis/Lanzamientos%20por%20PJs_2013_%202025.xlsx", "cgpj_lanzamientos_pj_2013_2025.xlsx")
page = html("https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estudios-e-Informes/Efecto-de-la-Crisis-en-los-organos-judiciales/")
for l in sorted(set(re.findall(r'href="([^"]+\.xlsx?)"', page, re.I)))[:30]:
    full = urllib.parse.urljoin("https://www.poderjudicial.es/", l)
    get(full, "cgpj_" + re.sub(r"[^A-Za-z0-9_.-]+", "_", os.path.basename(urllib.parse.unquote(l)))[:80])

# ---------- MIVAU transacciones / valor tasado ----------
page = html("https://datos.gob.es/es/catalogo/e05233601-transacciones-inmobiliarias-de-vivienda")
for l in sorted(set(re.findall(r'href="(https?://[^"]+\.(?:xls|xlsx|csv|zip))"', page, re.I)))[:20]:
    get(l, "mivau_" + re.sub(r"[^A-Za-z0-9_.-]+", "_", os.path.basename(l))[:80])
for url, name in [("https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=34000000", "mivau_boletin_transacciones.html"),
                  ("https://apps.fomento.gob.es/BoletinOnline2/?nivel=2&orden=33000000", "mivau_boletin_valor.html")]:
    get(url, name)

# ---------- Informes PDF / HTML ----------
pdfs = {
    "upv_observatorio_4t2024.pdf": "https://observa.webs.upv.es/wp-content/uploads/2025/01/Informe-Final-4T-2024.pdf",
    "upv_observatorio_4t2025.pdf": "https://observa.webs.upv.es/wp-content/uploads/2026/01/Informe-4T-2025-FINAL.pdf",
    "apunt_coapi_2t2025.pdf": "https://static.apuntmedia.es/apunt/public/content/file/original/2025/0829/10/valencia-25t2-pdf-3.pdf",
    "apunt_informe_2t2025.pdf": "https://static.apuntmedia.es/apunt/public/content/file/original/2025/1006/09/informe-immobiliari-valencia-2t-2025.pdf",
    "registradores_eri_4t2025.pdf": "https://www.registradores.org/documents/d/guest/eri_4t_2025",
    "sareb_informe_2025.pdf": "https://www.sareb.es/wp-content/uploads/2025/11/sareb-informe-semestral-2025-final.pdf",
    "gva_plan_estrategico_vivienda_2017_2021.pdf": "https://www.valencia.es/documents/20142/38081/20190501%2520Plan%2520Estrat%25C3%25A9gico%2520de%2520Vivienda%25202017-2021.pdf/94e2229b-b78f-e897-346b-9eab1f55bd1b",
    "mesval_airbnb_2022.pdf": "https://www.uv.es/mesval/Informes-2022/MESVAL_2022_DT_05-AIRBNB.pdf",
    "uv_catedra_coyuntura_2026.pdf": "https://www.uv.es/catpescv/publicacions/informes-coyuntura/2026/Obs-CV-3-1.pdf",
    "aeat_irpf_vivienda_2023_valencia.html": "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfvivienda/2023/jrubikf7a8a5a0b7d1a38d33b94d3d7b460bf326cb77994.html",
    "aeat_irpf_vivienda_2023_grandes.html": "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfvivienda/2023/jrubik5412113159d8a42cdae3e9df25652c2e3fb7f3dc.html",
    "vlc_presupuestos_renta_distritos_2025.pdf": "https://vlcparticipa.valencia.es/docs/modificacion-informe-distribucion-presupuestos-participativos-2025.pdf",
}
for name, url in pdfs.items():
    get(url, name)

json.dump(log, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = sum(1 for v in log.values() if v.get("ok")); print(f"\n{ok} descargas OK de {len(log)}")
