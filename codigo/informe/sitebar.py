# Barra de navegación común a todas las páginas (salvo el mapa, que usa su barra de pestañas)
PAGES = [
    ("inicio", "./", '<span class="sb-ini">Inicio</span>'),
    ("informe", "informe-vivienda-valencia.html", 'Informe<span class="lg"> completo</span>'),
    ("mapa", "pisos-turisticos-valencia.html", "Mapa"),
    ("elec", "elecciones-29n.html", '<span class="lg">Elecciones </span>29-N'),
]

def bar(cur):
    links = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if k == cur else ""}{" class=\"sb-i\"" if k == "inicio" else ""}>{t}</a>'
        for k, h, t in PAGES)
    return (f'<div class="sitebar"><a class="sb-home" href="./"{" aria-current=\"page\"" if cur == "inicio" else ""}>viviendavalencia.info</a>'
            f'<nav aria-label="Secciones del sitio">{links}<a class="langsw" data-notr href="?lang=va">Valencià</a></nav></div>\n')
