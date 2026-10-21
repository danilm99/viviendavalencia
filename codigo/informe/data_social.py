# Salarios, emancipación, pisos compartidos y edad de compra. Investigación oct-2026.
EES_CV = {"2008": 19794, "2009": 20490, "2010": 20707, "2011": 21316, "2012": 21224, "2013": 20878, "2014": 20640, "2015": 20935, "2016": 21169, "2017": 21362, "2018": 22121, "2019": 22046, "2020": 22857, "2021": 23448, "2022": 24510, "2023": 25632, "2024": 26817}
EES_ES = {"2008": 21883, "2009": 22511, "2010": 22790, "2011": 22899, "2012": 22726, "2013": 22698, "2014": 22858, "2015": 23106, "2016": 23156, "2017": 23647, "2018": 24009, "2019": 24396, "2020": 25166, "2021": 25897, "2022": 26949, "2023": 28050, "2024": 29540}
SMI = {"2015": 9080, "2016": 9173, "2017": 9908, "2018": 10303, "2019": 12600, "2020": 13300, "2021": 13510, "2022": 14000, "2023": 15120, "2024": 15876, "2025": 16576}
S = {
 "salarios": {
  "title": "Salarios: lo que se cobra frente a lo que cuesta",
  "text": [
   "Los salarios se miden por provincia y por comunidad: Hacienda cifra el salario medio bruto de la provincia de Valencia en 23.359 € en 2023 (1.188.305 asalariados) y el INE la ganancia media por comunidad. En la Comunitat Valenciana la ganancia media anual por trabajador pasó de 20.935 € en 2015 a 26.817 € en 2024 (+28 %), siempre un 8-10 % por debajo de la media española. En la ciudad, la declaración de IRPF media de 2023 tenía una renta bruta de 34.355 € y una renta disponible de 27.217 € (473.618 declaraciones, puesto 258 de España por renta).",
   "El salario mínimo subió un 83 % entre 2015 y 2025 (de 9.080 a 16.576 € al año en 14 pagas); el alquiler anunciado en la ciudad, un 143 % en el mismo periodo. Un salario mínimo neto (unos 1.300 €/mes) no cubre el alquiler medio de oferta de un piso (2.091 €, UPV 4T-2025).",
  ],
  "kpis": [
   ["26.817 €", "ganancia media anual, Comunitat (2024)", "INE EES; 29.540 € en España (−9 %)", "", "s_ees"],
   ["+28 %", "salario medio en la Comunitat, 2015 → 2024", "alquiler anunciado en la ciudad: +129 % (diciembre de 2015 → diciembre de 2024)", "w", "s_var"],
   ["23.359 €", "salario medio bruto, provincia de Valencia (2023)", "AEAT; 1.188.305 asalariados", "", "s_aeat_prov"],
   ["34.355 €", "renta bruta media por declaración de IRPF en la ciudad (2023)", "renta disponible 27.217 €; AEAT, 473.618 declaraciones", "", "s_irpf"],
   ["16.576 €", "salario mínimo anual (2025)", "9.080 € en 2015 (+83 %)", "", "s_smi"],
   ["1.190 €", "salario neto mensual de un joven asalariado (España, 2025)", "Observatorio de Emancipación: alquilar solo cuesta el 98,7 % de ese salario", "w", "s_joven"],
  ],
  "charts": [
   {"title": "Ganancia media anual por trabajador: Comunitat Valenciana y España (2008-2024)", "desc": "Salario bruto anual medio (INE, Encuesta de Estructura Salarial) y salario mínimo anual.", "cap": "Fuente: INE, EES (tabla 28191), ambos sexos; SMI según BOE (14 pagas). No hay dato municipal.",
    "det": "s_ees", "unit": "€", "series": [{"name": "Salario medio Comunitat Valenciana", "unit": "€", "pts": EES_CV, "src": "INE EES"}, {"name": "Salario medio España", "unit": "€", "pts": EES_ES, "src": "INE EES", "label": False}, {"name": "Salario mínimo anual (SMI)", "unit": "€", "pts": SMI, "src": "BOE"}], "y0": 0},
  ],
  "src": "INE EES",
  "srcs": [["INE, Encuesta Anual de Estructura Salarial, ganancia media por comunidad (tabla 28191)", "https://www.ine.es/jaxiT3/Tabla.htm?t=28191"],
           ["AEAT, Mercado de trabajo y pensiones en las fuentes tributarias 2023 (salarios por provincia)", "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/mercado/2023/jrubikf3d224357e1499d47dd9e0a46d09b6bb4802aa63b.html"],
           ["AEAT, Estadística de los declarantes del IRPF por municipios 2023, València", "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2023/jrubikf6181210248013d17a1d51e6526ed207a5068a6d3.html"]],
 },
 "hogares": {
  "title": "Emanciparse, compartir, comprar: cada vez más tarde",
  "text": [
   "Solo el 14,1 % de los jóvenes valencianos de 16 a 29 años vivía fuera de casa de sus padres en el primer semestre de 2024 (14,8 % en España), 1,4 puntos menos que un año antes; en 2025 la tasa española bajó al 14,5 %, la más baja de la serie. Alquilar un piso en solitario exigía el 95,7 % del salario neto de un joven en la Comunitat (98,7 % en España en 2025); compartir piso, el 33,6 %. La edad media de emancipación supera los 30 años y la de compra de la primera vivienda ronda los 41 en España, siete más que la media europea; la proporción de menores de 35 años propietarios cayó del 65 % en 2008 a menos del 40 % en 2022.",
   "Compartir piso es la salida para muchos: en el Censo de 2021, 12.213 hogares de la ciudad (3,8 %) eran personas sin parentesco que comparten vivienda, sin contar a quienes conviven con familiares. La edad media de quien busca habitación en València es de 28 años, la tercera más baja de España (34 de media). La habitación costaba 350 € al mes en 2022 y 375 € en 2023; en el primer trimestre de 2026 la oferta de habitaciones en la ciudad creció un 68 % en un año mientras el precio bajaba un 4 %, señal de que el mercado se ha movido hacia alquilar por habitaciones.",
  ],
  "kpis": [
   ["14,1 %", "jóvenes de 16 a 29 años emancipados en la Comunitat (1S-2024)", "España: 14,8 % en 2024 y 14,5 % en 2025, el mínimo de la serie", "w", "h_eman"],
   ["95,7 %", "del salario joven para alquilar en solitario (Comunitat, 2024)", "98,7 % en España en 2025; compartir piso: 33,6 %", "w", "h_esfj"],
   ["41 años", "edad media de compra de la primera vivienda (España, 2026)", "unos 34 en la media europea", "", "h_edadc"],
   ["<40 %", "menores de 35 años propietarios (2022)", "65 % en 2008 (Fedea)", "w", "h_prop35"],
   ["28 años", "edad media de quien busca habitación en València", "34 en España (idealista, 2023)", "", "h_edadh"],
   ["375 €", "habitación en piso compartido en València (agosto de 2023)", "350 € en 2022 (+18 %); en el 1T-2026 la oferta crece un 68 % y el precio baja un 4 %", "", "h_hab"],
   ["7 %", "de la generación Z tiene hipoteca", "26 % comparte piso, 35 % alquila (pisos.com, 2026)", "", "h_genz"],
   ["12.213", "hogares de personas sin parentesco (Censo 2021)", "3,8 % de los hogares de la ciudad", "a", "h_nofam"],
  ],
  "charts": [],
  "src": "CJE / idealista",
  "srcs": [["Consejo de la Juventud de España, Observatorio de Emancipación (resultados autonómicos 1S-2024; informe 2025)", "https://www.cje.org/download/291/1o-semestre-2024/23295/2024-1sem_principales-resultados-autonomicos.pdf"],
           ["Euronews: alquiler y salario juvenil, Observatorio de Emancipación 2025", "https://es.euronews.com/business/2026/05/22/el-alquiler-consume-el-987-del-salario-juvenil-en-pisos-individuales-y-mas-del-33-en-compa"],
           ["Valencia Plaza / idealista: pisos compartidos en València (2023)", "https://valenciaplaza.com/valenciaplaza/castelloeslacapitalprovincialdeespaaconmayoraumentodeofertadepisocompartido"],
           ["eldiario.es / idealista: precio de la habitación en València (2022)", "https://www.eldiario.es/comunitat-valenciana/valencia/alquilar-habitacion-cuesta-media-valencia-350-euros-18-ano_1_9396740.html"],
           ["Bolsamanía / idealista: oferta de habitaciones 1T-2026", "https://www.bolsamania.com/noticias/economia/oferta-habitaciones-crece-22-precio-aumenta-2-primer-trimestre--22263013.html"],
           ["Infobae: edad de compra de la primera vivienda, Fedea y pisos.com (2026)", "https://www.infobae.com/espana/2026/04/14/comprar-la-primera-casa-a-los-41-anos-convertirse-en-propietario-se-retrasa-y-solo-el-7-de-la-generacion-z-tiene-hipoteca/"]],
 },
}
S["srcs"] = S["salarios"]["srcs"] + S["hogares"]["srcs"]
