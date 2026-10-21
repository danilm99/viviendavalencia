Versión en valenciano.

- `va_all.json`: diccionario castellano → valenciano. Las claves son los textos de la página con los números sustituidos por {0}, {1}…
- `harvest.js` + `steps_*.js`: recogen todos los textos visibles de cada página (con Playwright) para detectar los que faltan.
- `apply.js` y `head_lang.html`: código que se incluye en las páginas para traducir en el navegador cuando se elige «Valencià» (?lang=va).
- `GUIA.md`: criterios y glosario de traducción.
- `check.py`: comprueba que cada traducción conserva marcadores y etiquetas.

Los diccionarios publicados son `va-informe.js` y `va-mapa.js`, en la raíz de la web.
