# viviendavalencia.info

Plataforma de código abierto para acercar a la ciudadanía los datos sobre la vivienda en València: <https://viviendavalencia.info>. Incluye un informe completo con la fuente de cada cifra, el mapa de los pisos turísticos de la ciudad y una página sobre lo que dicen los partidos ante las elecciones generales del 29-N.

Este repositorio contiene la web publicada y todo lo necesario para comprobar de dónde sale cada cifra.

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `/` | La web tal como se publica: `index.html` (portada), `informe-vivienda-valencia.html` (informe completo), `pisos-turisticos-valencia.html` (mapa) y `elecciones-29n.html` (elecciones). Los `va-*.js` son los diccionarios de la versión en valenciano. |
| `datos/informe/` | Datos limpios del informe (JSON): series de precios, rentas, Censo, Catastro, fianzas, padrón, CGPJ y demás. |
| `datos/mapa/` | Anuncios de Inside Airbnb ya cruzados con los registros (JSON y CSV), límites de barrio, censo municipal de apartamentos turísticos (CATAV), registro de la Generalitat e investigación sobre grandes anfitriones. |
| `datos/investigacion/` | Notas de investigación por tema. |
| `codigo/informe/` | Scripts que extraen y combinan los datos (`*.py`) y plantillas de la página (`tpl/`). `build_report.py` genera el informe y, al terminar, la portada (`build_landing.py`, que toma las cifras clave del informe con `extract_kpis.js`; necesita Node y Playwright). `build_elecciones.py` genera la página de elecciones a partir de `data_elecciones.py` y `data_historial.py`. `sitebar.py` es la barra de navegación común. |
| `codigo/mapa/` | `build_data.py` procesa el CSV de Inside Airbnb y `build_page.py` genera el mapa. |
| `codigo/valenciano/` | Traducción al valenciano: guía, diccionario completo (`va_all.json`), script que aplica la traducción en la página (`apply.js`) y herramientas para recoger textos nuevos (`harvest.js`) y regenerar los diccionarios (`gendict.py`). |

Cada gráfico de la web también se puede ver como tabla y descargar en CSV desde la propia página.

## Fuentes

Cada cifra enlaza a su fuente original en la ficha que se abre al pulsarla, y la sección «Fuentes y método» del informe las lista todas. Los ficheros de partida más pesados (tablas completas del INE, Anuario Estadístico del Ayuntamiento, registro de fianzas de la Generalitat, CSV de Inside Airbnb) no se incluyen por tamaño: se descargan de esas mismas fuentes.

## Privacidad

En los datos de anuncios, los anfitriones con menos de cinco anuncios y sin ficha de empresa no se publican por su nombre: se eliminan nombre, ubicación y antigüedad, y su identificador se sustituye por uno ficticio. Las visitas a la web se cuentan con [GoatCounter](https://www.goatcounter.com), sin cookies ni datos personales; las estadísticas son públicas en <https://viviendavalencia.goatcounter.com>.

## Correcciones

Si encuentras un error, abre una incidencia en este repositorio. Las correcciones se publican con su fecha en la sección «Sobre la web» del informe.

## Licencias

- Textos y datos elaborados: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Puedes reutilizarlos citando «viviendavalencia.info». Los datos de terceros mantienen la licencia de su fuente original.
- Código: licencia MIT (ver `LICENSE`).
