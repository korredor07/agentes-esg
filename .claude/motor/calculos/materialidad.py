# -*- coding: utf-8 -*-
"""Doble materialidad: que asuntos ESG son importantes, por impacto y por dinero.

Que es:

- La doble materialidad responde dos preguntas distintas sobre el mismo asunto.
  1. Materialidad de impacto ("de adentro hacia afuera"): que efectos tiene la
     empresa, con su operacion y su cadena de valor, sobre las personas y el
     medio ambiente.
  2. Materialidad financiera ("de afuera hacia adentro"): que riesgos y
     oportunidades de sostenibilidad pueden afectar los resultados, la posicion
     financiera, el costo del credito o el acceso a financiamiento.
- Un asunto es material si lo es por CUALQUIERA de las dos vias: basta con una.
  Fuente del concepto: docs/investigacion/06-marcos-reporte-metas-greenwashing.md,
  seccion 5.2 (marco europeo ESRS 1) [VERIFICADO].

Como se calcula aqui (convencion de este motor, no del estandar):

    Las dos escalas van de 1 a 5, donde 1 es muy bajo y 5 muy alto.

    Eje de impacto
        gravedad = promedio de escala, alcance e irremediabilidad
        puntaje  = 0,7 x gravedad + 0,3 x probabilidad
        En los asuntos de derechos humanos la gravedad manda: el puntaje nunca
        queda por debajo de la gravedad, aunque la probabilidad sea baja.

    Eje financiero
        puntaje = raiz cuadrada de (magnitud x probabilidad)
        Es el producto "magnitud por probabilidad" devuelto a la escala 1 a 5.

    Es material si el puntaje de impacto O el financiero llega al umbral.

Que decide la empresa y no el motor:

- Que asuntos entran en la lista (la de aqui es una propuesta inicial por rubro).
- Que nota de 1 a 5 lleva cada criterio.
- Donde se pone el umbral. El estandar europeo no fija un numero: exige un
  metodo explicado y consistente. Por eso el umbral es un parametro y el
  resultado siempre viaja con el umbral usado.

Esto ordena la conversacion. No reemplaza la consulta a los grupos de interes
ni la aprobacion del resultado por la direccion de la empresa.
"""

import math
import unicodedata

from nucleo.salida import Problema

ESCALA_MINIMA = 1.0
ESCALA_MAXIMA = 5.0
UMBRAL_POR_DEFECTO = 3.0

PESO_GRAVEDAD = 0.7
PESO_PROBABILIDAD_IMPACTO = 0.3

FUENTE = "docs/investigacion/06-marcos-reporte-metas-greenwashing.md"

CRITERIOS_IMPACTO = ("escala", "alcance", "irremediabilidad", "probabilidad_impacto")
CRITERIOS_FINANCIEROS = ("magnitud_financiera", "probabilidad_financiera")
CRITERIOS = CRITERIOS_IMPACTO + CRITERIOS_FINANCIEROS

ETIQUETAS = {
    "escala": "escala del impacto",
    "alcance": "alcance del impacto",
    "irremediabilidad": "irremediabilidad del impacto",
    "probabilidad_impacto": "probabilidad del impacto",
    "magnitud_financiera": "magnitud del efecto financiero",
    "probabilidad_financiera": "probabilidad del efecto financiero",
}

OPCIONES = {
    "escala": "--escala",
    "alcance": "--alcance",
    "irremediabilidad": "--irremediabilidad",
    "probabilidad_impacto": "--probabilidad-impacto",
    "magnitud_financiera": "--magnitud-financiera",
    "probabilidad_financiera": "--probabilidad-financiera",
}

PREGUNTAS = [
    {"criterio": "escala", "eje": "impacto",
     "pregunta": "¿Que tan grave es el efecto cuando ocurre?",
     "ancla_1": "Apenas se nota.", "ancla_3": "Se nota y molesta, pero se vive con eso.",
     "ancla_5": "Es un daño grave para la salud, el ambiente o los derechos de alguien."},
    {"criterio": "alcance", "eje": "impacto",
     "pregunta": "¿A cuanta gente o a que superficie alcanza?",
     "ancla_1": "A unas pocas personas o a un rincon de la operacion.",
     "ancla_3": "A un area completa, un turno o un barrio.",
     "ancla_5": "A toda la comunidad, a toda la cadena o a un territorio extenso."},
    {"criterio": "irremediabilidad", "eje": "impacto",
     "pregunta": "Si pasa, ¿se puede reparar?",
     "ancla_1": "Se arregla rapido y sin costo mayor.",
     "ancla_3": "Se puede reparar, pero cuesta tiempo y plata.",
     "ancla_5": "No tiene vuelta atras."},
    {"criterio": "probabilidad_impacto", "eje": "impacto",
     "pregunta": "¿Cada cuanto ocurre o podria ocurrir?",
     "ancla_1": "Seria muy raro.", "ancla_3": "Puede pasar en cualquier año.",
     "ancla_5": "Ya esta ocurriendo hoy."},
    {"criterio": "magnitud_financiera", "eje": "financiera",
     "pregunta": "Si el asunto se les viene encima, ¿cuanta plata esta en juego?",
     "ancla_1": "Un monto que no mueve la aguja.",
     "ancla_3": "Un monto que obliga a reordenar el presupuesto del año.",
     "ancla_5": "Un monto que pone en riesgo el negocio o un cliente grande."},
    {"criterio": "probabilidad_financiera", "eje": "financiera",
     "pregunta": "¿Que tan probable es que ese efecto en la plata ocurra en los proximos años?",
     "ancla_1": "Muy poco probable.", "ancla_3": "Es posible, depende de como se den las cosas.",
     "ancla_5": "Es practicamente seguro o ya esta pasando."},
]

CUADRANTES = {
    "doble": "Material por impacto y por dinero",
    "impacto": "Material por lo que la empresa causa",
    "financiera": "Material por lo que puede afectar a la empresa",
    "no_material": "No material por ahora",
}

COLOR_DIMENSION = {"ambiental": "#2D6A4F", "social": "#457B9D", "gobernanza": "#D9A441"}

METODOLOGIA = (
    "Cada asunto se evalua en dos ejes de 1 a 5. Eje de impacto: la gravedad es el promedio de escala, "
    "alcance e irremediabilidad, y el puntaje es 70% gravedad mas 30% probabilidad; en los asuntos de "
    "derechos humanos la gravedad manda y el puntaje nunca baja de ella. Eje financiero: magnitud por "
    "probabilidad, devuelto a la escala 1 a 5 con la raiz cuadrada. Un asunto es material si cualquiera "
    "de los dos puntajes llega al umbral."
)

AVISO = (
    "Que asuntos entran a la lista, que nota lleva cada uno y donde se pone el umbral son decisiones de "
    "la empresa, no resultados automaticos. Este calculo ordena la conversacion: no reemplaza la consulta "
    "a los grupos de interes ni la aprobacion del resultado por la direccion."
)


# --------------------------------------------------------------------------
# Catalogo de asuntos por tipo de actividad
# --------------------------------------------------------------------------

COMUNES = [
    {"id": "clima-energia", "dimension": "ambiental", "nombre": "Cambio climatico y energia",
     "que_impacta": "Las emisiones de gases de efecto invernadero de la operacion y de la cadena de valor.",
     "que_arriesga": "Precio de la energia, impuestos al carbono y clientes que exigen la huella medida.",
     "marcos": "ESRS E1, GRI 305, NIIF S2"},
    {"id": "residuos", "dimension": "ambiental", "nombre": "Residuos y uso de materiales",
     "que_impacta": "Lo que se bota, a donde va y cuanto material nuevo se usa.",
     "que_arriesga": "Costo de retiro y disposicion, obligaciones de reciclaje y multas.",
     "marcos": "ESRS E5, GRI 306"},
    {"id": "agua", "dimension": "ambiental", "nombre": "Agua: consumo y descargas",
     "que_impacta": "El agua que se extrae y la calidad del agua que se devuelve.",
     "que_arriesga": "Restricciones en zonas con escasez, costo del agua y permisos de descarga.",
     "marcos": "ESRS E3, GRI 303"},
    {"id": "salud-seguridad", "dimension": "social", "nombre": "Salud y seguridad de quienes trabajan",
     "que_impacta": "Accidentes, enfermedades laborales y exposicion a riesgos.",
     "que_arriesga": "Dias perdidos, cotizaciones, demandas y paralizacion de faenas.",
     "derechos_humanos": True, "marcos": "ESRS S1, GRI 403"},
    {"id": "condiciones-laborales", "dimension": "social", "nombre": "Condiciones de trabajo y remuneraciones",
     "que_impacta": "Contratos, jornadas, sueldos y estabilidad de las personas del equipo.",
     "que_arriesga": "Fiscalizaciones laborales, rotacion y dificultad para contratar.",
     "derechos_humanos": True, "marcos": "ESRS S1, GRI 401"},
    {"id": "igualdad-diversidad", "dimension": "social", "nombre": "Igualdad, diversidad y no discriminacion",
     "que_impacta": "Quien accede a los cargos, a que sueldo y en que condiciones.",
     "que_arriesga": "Denuncias, brecha salarial expuesta y exigencias de clientes y licitaciones.",
     "derechos_humanos": True, "marcos": "ESRS S1, GRI 405 y 406"},
    {"id": "acoso-violencia", "dimension": "social", "nombre": "Acoso laboral, acoso sexual y violencia en el trabajo",
     "que_impacta": "La dignidad y la salud mental de las personas del equipo.",
     "que_arriesga": "Procedimientos con plazos legales, multas y daño reputacional inmediato.",
     "derechos_humanos": True, "marcos": "ESRS S1, GRI 406"},
    {"id": "cadena-suministro", "dimension": "social", "nombre": "Condiciones laborales en la cadena de suministro",
     "que_impacta": "Como trabajan las personas de proveedores y contratistas.",
     "que_arriesga": "Auditorias de clientes, perdida de contratos y responsabilidad solidaria.",
     "derechos_humanos": True, "marcos": "ESRS S2, GRI 414"},
    {"id": "comunidad", "dimension": "social", "nombre": "Relacion con la comunidad vecina",
     "que_impacta": "Ruido, olores, transito, empleo local y uso del espacio compartido.",
     "que_arriesga": "Oposicion a proyectos, reclamos y retrasos en permisos.",
     "marcos": "ESRS S3, GRI 413"},
    {"id": "etica-anticorrupcion", "dimension": "gobernanza", "nombre": "Etica, anticorrupcion y conflictos de interes",
     "que_impacta": "La forma en que la empresa compite, compra y se relaciona con la autoridad.",
     "que_arriesga": "Responsabilidad penal de la empresa, exclusion de licitaciones y perdida de clientes.",
     "marcos": "ESRS G1, GRI 205"},
    {"id": "datos-personales", "dimension": "gobernanza", "nombre": "Proteccion de datos personales",
     "que_impacta": "Los datos de trabajadores, clientes y proveedores que la empresa maneja.",
     "que_arriesga": "Multas, demandas y perdida de confianza tras una filtracion.",
     "marcos": "ESRS G1, GRI 418"},
    {"id": "cumplimiento-permisos", "dimension": "gobernanza", "nombre": "Cumplimiento normativo y permisos al dia",
     "que_impacta": "El respeto de las reglas que protegen al entorno y a las personas.",
     "que_arriesga": "Multas, clausuras y suspension de la operacion.",
     "marcos": "ESRS G1, GRI 2-27"},
    {"id": "transparencia", "dimension": "gobernanza",
     "nombre": "Transparencia de la informacion y afirmaciones ambientales",
     "que_impacta": "Lo que la empresa dice en publico sobre su desempeño y lo que la gente cree.",
     "que_arriesga": "Sanciones por publicidad engañosa y perdida de credibilidad ante clientes y bancos.",
     "marcos": "ESRS G1, GRI 2-5"},
]

FAMILIAS = [
    ("alimentos", "Alimentos, bebidas y agroindustria",
     ["agroindustria", "agricola", "agropecuaria", "agro", "alimento", "bebida", "conserva", "lacteo",
      "vitivinicola", "viña", "vina", "frutic", "hortal", "packing", "frigorif", "molino", "panader"],
     [
         {"id": "biodiversidad-suelo", "dimension": "ambiental",
          "nombre": "Suelo, biodiversidad y uso de agroquimicos",
          "que_impacta": "Fertilidad del suelo, polinizadores y cursos de agua cercanos a los predios.",
          "que_arriesga": "Restricciones de mercado, rechazo de embarques y limites de residuos.",
          "marcos": "ESRS E4"},
         {"id": "desperdicio-alimentos", "dimension": "ambiental", "nombre": "Perdida y desperdicio de alimentos",
          "que_impacta": "Comida que se produce y no se come, con toda su huella detras.",
          "que_arriesga": "Margen perdido en cada kilo botado y costo de disposicion.",
          "marcos": "ESRS E5"},
         {"id": "inocuidad", "dimension": "social", "nombre": "Inocuidad y seguridad de los alimentos",
          "que_impacta": "La salud de quien consume el producto.",
          "que_arriesga": "Retiros de producto, cierre de mercados y demandas.",
          "marcos": "ESRS S4, GRI 416"},
         {"id": "envases", "dimension": "ambiental", "nombre": "Envases y responsabilidad del productor",
          "que_impacta": "Los envases que quedan en manos del consumidor y en el sistema de residuos.",
          "que_arriesga": "Obligaciones de recoleccion y valorizacion, y su costo anual.",
          "marcos": "ESRS E5"},
         {"id": "trabajo-temporada", "dimension": "social", "nombre": "Trabajo de temporada y contratistas",
          "que_impacta": "Las condiciones de quienes trabajan solo unos meses al año.",
          "que_arriesga": "Fiscalizaciones, auditorias de clientes y falta de mano de obra.",
          "derechos_humanos": True, "marcos": "ESRS S2"},
     ]),
    ("mineria", "Mineria y servicios a la mineria",
     ["mineria", "minera", "minero", "cobre", "litio", "extractiv", "concentradora", "faena"],
     [
         {"id": "agua-cuencas", "dimension": "ambiental", "nombre": "Agua en cuencas con escasez",
          "que_impacta": "La disponibilidad de agua para comunidades y ecosistemas del territorio.",
          "que_arriesga": "Permisos, judicializacion de proyectos y costo de desalar o transportar agua.",
          "marcos": "ESRS E3"},
         {"id": "relaves-residuos-masivos", "dimension": "ambiental", "nombre": "Relaves y residuos masivos",
          "que_impacta": "Suelos, aire y agua alrededor de los depositos.",
          "que_arriesga": "Exigencias de estabilidad, cierre y seguros.",
          "marcos": "ESRS E2"},
         {"id": "comunidades-indigenas", "dimension": "social", "nombre": "Comunidades y pueblos indigenas",
          "que_impacta": "El territorio, el agua y el patrimonio cultural de quienes viven alrededor.",
          "que_arriesga": "Oposicion, consultas, paralizaciones y perdida de licencia social.",
          "derechos_humanos": True, "marcos": "ESRS S3"},
         {"id": "cierre-faena", "dimension": "ambiental", "nombre": "Cierre de faena y pasivos ambientales",
          "que_impacta": "Lo que queda en el territorio cuando la operacion termina.",
          "que_arriesga": "Garantias financieras y costo de remediacion.",
          "marcos": "ESRS E4"},
     ]),
    ("manufactura", "Industria y manufactura",
     ["manufactura", "industria", "industrial", "fabrica", "metalmecanic", "plastico", "quimic", "textil",
      "cemento", "acero", "papel", "farmaceutic", "automotriz", "electronica"],
     [
         {"id": "contaminacion", "dimension": "ambiental", "nombre": "Contaminacion del aire, el agua y el suelo",
          "que_impacta": "Emisiones de la chimenea, descargas del proceso y derrames.",
          "que_arriesga": "Declaraciones obligatorias, impuestos, multas y clausuras.",
          "marcos": "ESRS E2, GRI 305"},
         {"id": "sustancias-quimicas", "dimension": "ambiental", "nombre": "Sustancias quimicas peligrosas",
          "que_impacta": "La exposicion de trabajadores, vecinos y ecosistemas.",
          "que_arriesga": "Restricciones de mercado, exigencias de clientes europeos y accidentes.",
          "marcos": "ESRS E2"},
         {"id": "eficiencia-materiales", "dimension": "ambiental", "nombre": "Eficiencia de materiales y circularidad",
          "que_impacta": "Cuanto material virgen entra y cuanto se recupera.",
          "que_arriesga": "Costo de insumos y exigencias de contenido reciclado.",
          "marcos": "ESRS E5"},
         {"id": "envases", "dimension": "ambiental", "nombre": "Envases y responsabilidad del productor",
          "que_impacta": "Los envases que quedan en el sistema de residuos.",
          "que_arriesga": "Obligaciones de recoleccion y valorizacion, y su costo anual.",
          "marcos": "ESRS E5"},
     ]),
    ("construccion", "Construccion e inmobiliaria",
     ["construccion", "constructora", "inmobiliaria", "obras", "edificacion", "ingenieria civil", "montaje"],
     [
         {"id": "residuos-construccion", "dimension": "ambiental", "nombre": "Residuos de construccion y demolicion",
          "que_impacta": "Escombros y materiales que terminan en botaderos.",
          "que_arriesga": "Costo de retiro, fiscalizacion municipal y ambiental.",
          "marcos": "ESRS E5"},
         {"id": "subcontratacion", "dimension": "social", "nombre": "Subcontratacion y trabajadores de obra",
          "que_impacta": "Las condiciones de quienes trabajan a traves de terceros.",
          "que_arriesga": "Responsabilidad solidaria, accidentes graves y paralizacion de la obra.",
          "derechos_humanos": True, "marcos": "ESRS S2"},
         {"id": "ruido-polvo", "dimension": "social", "nombre": "Ruido, polvo y transito durante la obra",
          "que_impacta": "La vida diaria de los vecinos mientras dura la faena.",
          "que_arriesga": "Reclamos, multas municipales y retraso de plazos.",
          "marcos": "ESRS S3"},
         {"id": "suelo-territorio", "dimension": "ambiental", "nombre": "Uso de suelo y entorno natural",
          "que_impacta": "La vegetacion, el agua y el paisaje del terreno intervenido.",
          "que_arriesga": "Permisos ambientales y condiciones de aprobacion.",
          "marcos": "ESRS E4"},
     ]),
    ("transporte", "Transporte y logistica",
     ["transporte", "logistica", "flota", "carga", "naviera", "courier", "reparto", "distribucion fisica"],
     [
         {"id": "emisiones-flota", "dimension": "ambiental", "nombre": "Emisiones y combustible de la flota",
          "que_impacta": "El aire de las rutas y ciudades por donde circulan los vehiculos.",
          "que_arriesga": "Precio del combustible, restricciones de circulacion y exigencias de clientes.",
          "marcos": "ESRS E1"},
         {"id": "seguridad-vial", "dimension": "social", "nombre": "Seguridad vial",
          "que_impacta": "La vida de conductores y de terceros en la ruta.",
          "que_arriesga": "Siniestros, primas de seguro y responsabilidad civil.",
          "derechos_humanos": True, "marcos": "ESRS S1"},
         {"id": "condiciones-conductores", "dimension": "social", "nombre": "Jornadas y descanso de conductores",
          "que_impacta": "La salud y el descanso de quienes manejan.",
          "que_arriesga": "Fiscalizacion laboral y accidentes por fatiga.",
          "derechos_humanos": True, "marcos": "ESRS S1"},
     ]),
    ("comercio", "Comercio y retail",
     ["comercio", "retail", "supermercado", "tienda", "venta", "importadora", "distribuidora", "ecommerce"],
     [
         {"id": "envases", "dimension": "ambiental", "nombre": "Envases y responsabilidad del productor",
          "que_impacta": "Los envases que la empresa pone en el mercado.",
          "que_arriesga": "Obligaciones de recoleccion y valorizacion, y su costo anual.",
          "marcos": "ESRS E5"},
         {"id": "origen-productos", "dimension": "social", "nombre": "Origen y trazabilidad de los productos",
          "que_impacta": "Las condiciones ambientales y laborales de donde viene lo que se vende.",
          "que_arriesga": "Exigencias de clientes y de aduanas, y escandalos de proveedores.",
          "derechos_humanos": True, "marcos": "ESRS S2"},
         {"id": "consumidores", "dimension": "social", "nombre": "Informacion y seguridad para consumidores",
          "que_impacta": "Lo que la gente compra creyendo lo que dice la etiqueta.",
          "que_arriesga": "Sanciones del regulador del consumidor y retiros de producto.",
          "marcos": "ESRS S4, GRI 417"},
     ]),
    ("tecnologia", "Tecnologia, software y telecomunicaciones",
     ["tecnologia", "software", "informatic", "telecomunicac", "datos", "digital", "plataforma", "startup"],
     [
         {"id": "ciberseguridad", "dimension": "gobernanza", "nombre": "Ciberseguridad y continuidad del servicio",
          "que_impacta": "La informacion y el servicio del que dependen los clientes.",
          "que_arriesga": "Interrupciones, rescates, multas y fuga de clientes.",
          "marcos": "ESRS G1"},
         {"id": "consumo-digital", "dimension": "ambiental", "nombre": "Consumo electrico de servidores y nube",
          "que_impacta": "La energia que consume la infraestructura, propia o contratada.",
          "que_arriesga": "Costo de la nube y exigencias de huella de clientes corporativos.",
          "marcos": "ESRS E1"},
         {"id": "residuos-electronicos", "dimension": "ambiental", "nombre": "Equipos y residuos electronicos",
          "que_impacta": "Los aparatos que se renuevan y donde terminan.",
          "que_arriesga": "Obligaciones de gestion de aparatos electricos y electronicos.",
          "marcos": "ESRS E5"},
     ]),
    ("turismo", "Turismo, hoteleria y gastronomia",
     ["turismo", "hotel", "hosteleria", "hoteleria", "restaurant", "gastronom", "hospedaje", "cabaña", "cabana"],
     [
         {"id": "desperdicio-alimentos", "dimension": "ambiental", "nombre": "Desperdicio de alimentos",
          "que_impacta": "La comida preparada que termina en la basura.",
          "que_arriesga": "Costo directo de insumos y de retiro de residuos.",
          "marcos": "ESRS E5"},
         {"id": "empleo-estacional", "dimension": "social", "nombre": "Empleo estacional y rotacion",
          "que_impacta": "La estabilidad de quienes trabajan solo en temporada alta.",
          "que_arriesga": "Rotacion, costo de capacitacion y calidad del servicio.",
          "marcos": "ESRS S1"},
         {"id": "entorno-patrimonio", "dimension": "ambiental", "nombre": "Entorno natural y patrimonio del lugar",
          "que_impacta": "El paisaje, la fauna y el patrimonio que atraen a los visitantes.",
          "que_arriesga": "Perdida del atractivo que sostiene el negocio y conflictos locales.",
          "marcos": "ESRS E4"},
     ]),
    ("salud", "Salud y laboratorios",
     ["salud", "clinica", "hospital", "laboratorio", "medic", "farmacia", "odontolog"],
     [
         {"id": "residuos-sanitarios", "dimension": "ambiental", "nombre": "Residuos sanitarios y peligrosos",
          "que_impacta": "El riesgo sanitario de lo que sale del recinto.",
          "que_arriesga": "Fiscalizacion sanitaria y costo de disposicion especial.",
          "marcos": "ESRS E2"},
         {"id": "datos-pacientes", "dimension": "gobernanza", "nombre": "Datos sensibles de pacientes",
          "que_impacta": "La intimidad de personas en situacion vulnerable.",
          "que_arriesga": "Multas altas, demandas y perdida de confianza.",
          "derechos_humanos": True, "marcos": "ESRS G1, GRI 418"},
         {"id": "acceso-calidad", "dimension": "social", "nombre": "Acceso y calidad de la atencion",
          "que_impacta": "La salud de quienes son atendidos y de quienes no alcanzan a serlo.",
          "que_arriesga": "Reclamos, acreditacion y contratos con aseguradoras.",
          "marcos": "ESRS S4"},
     ]),
    ("pesca", "Pesca y acuicultura",
     ["pesca", "pesquera", "acuicultura", "salmon", "mitilic", "alguer", "marisco"],
     [
         {"id": "biodiversidad-marina", "dimension": "ambiental", "nombre": "Biodiversidad marina y fondo marino",
          "que_impacta": "Las especies y el fondo donde opera el centro o la flota.",
          "que_arriesga": "Restriccion de concesiones, certificaciones y acceso a mercados.",
          "marcos": "ESRS E4"},
         {"id": "uso-farmacos", "dimension": "ambiental", "nombre": "Uso de farmacos y alimento",
          "que_impacta": "La calidad del agua y la resistencia a antibioticos.",
          "que_arriesga": "Limites de residuos, rechazo de embarques y auditorias de compradores.",
          "marcos": "ESRS E2"},
         {"id": "comunidades-costeras", "dimension": "social", "nombre": "Comunidades costeras y pesca artesanal",
          "que_impacta": "El acceso al borde costero y el sustento de quienes viven de el.",
          "que_arriesga": "Conflictos, bloqueos y oposicion a nuevas concesiones.",
          "derechos_humanos": True, "marcos": "ESRS S3"},
     ]),
    ("forestal", "Forestal y madera",
     ["forestal", "madera", "celulosa", "aserradero", "silvicultura", "plantacion"],
     [
         {"id": "biodiversidad-bosques", "dimension": "ambiental", "nombre": "Bosque nativo y biodiversidad",
          "que_impacta": "Los ecosistemas y las especies del area manejada.",
          "que_arriesga": "Certificaciones, permisos y exigencias de compradores europeos.",
          "marcos": "ESRS E4"},
         {"id": "trazabilidad-origen", "dimension": "ambiental", "nombre": "Trazabilidad del origen de la madera",
          "que_impacta": "La presion sobre bosques y suelos de donde sale la materia prima.",
          "que_arriesga": "Bloqueo de exportaciones a mercados que exigen origen libre de deforestacion.",
          "marcos": "ESRS E4"},
         {"id": "incendios", "dimension": "ambiental", "nombre": "Prevencion de incendios",
          "que_impacta": "Bosques, casas y vidas del entorno.",
          "que_arriesga": "Perdida total del activo, seguros y responsabilidad.",
          "marcos": "ESRS E4"},
         {"id": "comunidades-indigenas", "dimension": "social", "nombre": "Comunidades y pueblos indigenas",
          "que_impacta": "El territorio, el agua y el patrimonio cultural de quienes viven alrededor.",
          "que_arriesga": "Conflictos, judicializacion y perdida de licencia social.",
          "derechos_humanos": True, "marcos": "ESRS S3"},
     ]),
    ("energia", "Energia y servicios basicos",
     ["energia", "electric", "generacion", "solar", "eolic", "hidroelectric", "gas", "combustible", "sanitaria"],
     [
         {"id": "territorio-comunidades", "dimension": "social", "nombre": "Territorio y comunidades del proyecto",
          "que_impacta": "El uso del suelo, el paisaje y la vida de quienes viven cerca.",
          "que_arriesga": "Oposicion, judicializacion y retraso de proyectos.",
          "derechos_humanos": True, "marcos": "ESRS S3"},
         {"id": "biodiversidad-territorio", "dimension": "ambiental", "nombre": "Biodiversidad del area de influencia",
          "que_impacta": "Especies y habitats donde se instalan las obras y las lineas.",
          "que_arriesga": "Condiciones ambientales de aprobacion y compensaciones.",
          "marcos": "ESRS E4"},
         {"id": "seguridad-operaciones", "dimension": "social", "nombre": "Seguridad de las operaciones",
          "que_impacta": "El riesgo para trabajadores y para la poblacion cercana.",
          "que_arriesga": "Accidentes mayores, interrupciones y sanciones.",
          "derechos_humanos": True, "marcos": "ESRS S1"},
         {"id": "transicion-justa", "dimension": "social", "nombre": "Transicion justa del empleo",
          "que_impacta": "Los empleos y territorios que dependen de la tecnologia que se deja atras.",
          "que_arriesga": "Conflicto laboral y presion regulatoria.",
          "marcos": "ESRS S1"},
     ]),
    ("financiero", "Banca, seguros y finanzas",
     ["banco", "banca", "seguro", "financiera", "credito", "inversion", "cooperativa de ahorro", "fintech"],
     [
         {"id": "emisiones-financiadas", "dimension": "ambiental", "nombre": "Emisiones de lo que se financia",
          "que_impacta": "Las emisiones de los proyectos y empresas que reciben el credito o la inversion.",
          "que_arriesga": "Exigencias de reguladores e inversionistas sobre la cartera.",
          "marcos": "ESRS E1, NIIF S2"},
         {"id": "criterios-esg-cartera", "dimension": "gobernanza",
          "nombre": "Criterios ambientales y sociales en el financiamiento",
          "que_impacta": "Que actividades se hacen posibles con el dinero prestado.",
          "que_arriesga": "Riesgo de credito no visto y reclamos por financiar daño.",
          "marcos": "ESRS G1"},
         {"id": "inclusion-financiera", "dimension": "social", "nombre": "Inclusion financiera y trato al cliente",
          "que_impacta": "El acceso de personas y pymes a servicios financieros justos.",
          "que_arriesga": "Sanciones por trato al consumidor y reputacion.",
          "marcos": "ESRS S4"},
     ]),
    ("servicios", "Servicios profesionales y oficinas",
     ["servicio", "consultor", "asesor", "estudio juridico", "contabilidad", "oficina", "educacion", "capacitacion",
      "inmobiliario"],
     [
         {"id": "oficina-viajes", "dimension": "ambiental", "nombre": "Energia de oficinas y viajes de trabajo",
          "que_impacta": "El consumo electrico del lugar de trabajo y las emisiones de los viajes.",
          "que_arriesga": "Costo de energia y pasajes, y preguntas de clientes grandes.",
          "marcos": "ESRS E1"},
         {"id": "compras-responsables", "dimension": "gobernanza", "nombre": "Compras y proveedores",
          "que_impacta": "Casi todo el impacto de una empresa de servicios esta en lo que compra.",
          "que_arriesga": "Exigencias de clientes sobre la cadena y riesgo reputacional heredado.",
          "marcos": "ESRS G1, GRI 308"},
         {"id": "bienestar-equipo", "dimension": "social", "nombre": "Bienestar y desarrollo del equipo",
          "que_impacta": "La carga de trabajo, el aprendizaje y la salud mental de las personas.",
          "que_arriesga": "Rotacion de talento, licencias y perdida de conocimiento.",
          "marcos": "ESRS S1, GRI 404"},
     ]),
]


def _sin_acentos(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def _vacio(valor):
    """True si el dato no fue respondido. Ojo: en Python 1 == True, por eso se compara por identidad."""
    return valor is None or isinstance(valor, bool) or (isinstance(valor, str) and not valor.strip())


def familia_de_sector(sector):
    """Devuelve (clave, etiqueta) del tipo de actividad reconocido en el texto del sector."""
    texto = _sin_acentos(sector)
    if texto.strip():
        for clave, etiqueta, palabras, _ in FAMILIAS:
            for palabra in palabras:
                if _sin_acentos(palabra) in texto:
                    return clave, etiqueta
    return "general", "Actividad no identificada"


def asuntos_sugeridos(sector=None):
    """Lista base de asuntos ESG para empezar: los comunes mas los del rubro.

    Es una propuesta para conversar, no una lista cerrada. La empresa agrega,
    saca o renombra asuntos segun su realidad.
    """
    clave, _ = familia_de_sector(sector)
    propuesta = []
    vistos = set()
    for asunto in COMUNES:
        ficha = dict(asunto)
        ficha["origen"] = "comun"
        propuesta.append(ficha)
        vistos.add(ficha["id"])
    for familia, _etiqueta, _palabras, asuntos in FAMILIAS:
        if familia != clave:
            continue
        for asunto in asuntos:
            if asunto["id"] in vistos:
                continue
            ficha = dict(asunto)
            ficha["origen"] = familia
            propuesta.append(ficha)
            vistos.add(ficha["id"])
    for ficha in propuesta:
        ficha.setdefault("derechos_humanos", False)
    return propuesta


# --------------------------------------------------------------------------
# Evaluacion
# --------------------------------------------------------------------------

def _umbral(valor):
    if _vacio(valor):
        return UMBRAL_POR_DEFECTO
    try:
        numero = float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "El umbral «%s» no es un numero." % valor,
            "El umbral es la nota desde la cual un asunto se considera importante, por ejemplo 3.",
        )
    if numero < ESCALA_MINIMA or numero > ESCALA_MAXIMA:
        raise Problema(
            "El umbral %s esta fuera de la escala: las notas van del 1 al 5." % valor,
            "Lo habitual es 3. Subelo a 3,5 o 4 si salen demasiados asuntos materiales.",
        )
    return numero


def valor_escala(valor, criterio, asunto="este asunto"):
    """Convierte una nota de 1 a 5 a numero. Devuelve None si no fue respondida."""
    if _vacio(valor):
        return None
    try:
        numero = float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "En «%s», la %s quedo escrita como «%s» y no es un numero."
            % (asunto, ETIQUETAS.get(criterio, criterio), valor),
            "Responde con un numero del 1 al 5: 1 es muy bajo, 3 es medio y 5 es muy alto.",
        )
    if numero < ESCALA_MINIMA or numero > ESCALA_MAXIMA:
        raise Problema(
            "En «%s», la %s quedo en %s y la escala va del 1 al 5."
            % (asunto, ETIQUETAS.get(criterio, criterio), valor),
            "Usa 1 si es muy bajo, 3 si es medio y 5 si es muy alto.",
        )
    return numero


def _leer_criterios(dato, nombre):
    anidados = dato.get("criterios") if isinstance(dato.get("criterios"), dict) else {}
    valores = {}
    for criterio in CRITERIOS:
        crudo = dato.get(criterio)
        if _vacio(crudo):
            crudo = anidados.get(criterio)
        valores[criterio] = valor_escala(crudo, criterio, nombre)
    return valores


def puntaje_impacto(escala, alcance, irremediabilidad, probabilidad, derechos_humanos=False):
    """Gravedad ponderada con la probabilidad. En derechos humanos la gravedad manda."""
    gravedad = (escala + alcance + irremediabilidad) / 3.0
    puntaje = PESO_GRAVEDAD * gravedad + PESO_PROBABILIDAD_IMPACTO * probabilidad
    if derechos_humanos:
        puntaje = max(puntaje, gravedad)
    return round(gravedad, 2), round(puntaje, 2)


def puntaje_financiero(magnitud, probabilidad):
    """Magnitud por probabilidad, devuelto a la escala 1 a 5 con la raiz cuadrada."""
    return round(math.sqrt(magnitud * probabilidad), 2)


def _cuadrante(impacto, financiero, umbral):
    material_impacto = impacto >= umbral
    material_financiera = financiero >= umbral
    if material_impacto and material_financiera:
        return "doble", ["impacto", "financiera"]
    if material_impacto:
        return "impacto", ["impacto"]
    if material_financiera:
        return "financiera", ["financiera"]
    return "no_material", []


def evaluar(asuntos, umbral=UMBRAL_POR_DEFECTO):
    """Calcula los dos puntajes de cada asunto, marca los materiales y los ordena.

    `asuntos` es una lista de diccionarios con el nombre del asunto y sus notas
    de 1 a 5. Los asuntos a los que les falta alguna nota no se puntuan: quedan
    en `pendientes` para terminarlos, nunca se rellenan con supuestos.
    """
    corte = _umbral(umbral)
    evaluados, pendientes = [], []

    for dato in (asuntos or []):
        if not isinstance(dato, dict):
            raise Problema(
                "Uno de los asuntos no tiene el formato esperado.",
                "Cada asunto debe registrarse con: materialidad registrar --asunto «nombre» ...",
            )
        nombre = (dato.get("nombre") or dato.get("asunto") or dato.get("id") or "").strip()
        if not nombre:
            raise Problema(
                "Hay un asunto sin nombre en la lista.",
                "Escribe de que asunto se trata, por ejemplo: --asunto \"Agua: consumo y descargas\".",
            )
        valores = _leer_criterios(dato, nombre)
        ficha = {
            "id": dato.get("id") or nombre,
            "nombre": nombre,
            "dimension": dato.get("dimension") or "",
            "derechos_humanos": bool(dato.get("derechos_humanos")),
            "nota": dato.get("nota") or "",
            "origen": dato.get("origen") or "",
            "criterios": valores,
        }
        faltantes = [criterio for criterio in CRITERIOS if valores[criterio] is None]
        if faltantes:
            ficha["faltan"] = [ETIQUETAS[c] for c in faltantes]
            ficha["faltan_opciones"] = [OPCIONES[c] for c in faltantes]
            pendientes.append(ficha)
            continue

        gravedad, impacto = puntaje_impacto(
            valores["escala"], valores["alcance"], valores["irremediabilidad"],
            valores["probabilidad_impacto"], ficha["derechos_humanos"])
        financiero = puntaje_financiero(valores["magnitud_financiera"], valores["probabilidad_financiera"])
        clave, porque = _cuadrante(impacto, financiero, corte)
        ficha.update({
            "gravedad": gravedad,
            "puntaje_impacto": impacto,
            "puntaje_financiero": financiero,
            "puntaje_maximo": round(max(impacto, financiero), 2),
            "material": clave != "no_material",
            "material_por": porque,
            "cuadrante": clave,
            "resultado": CUADRANTES[clave],
            "color": COLOR_DIMENSION.get(ficha["dimension"], "#6C757D"),
        })
        evaluados.append(ficha)

    evaluados.sort(key=lambda a: (-a["puntaje_maximo"], -a["puntaje_impacto"], a["nombre"]))
    materiales = [a for a in evaluados if a["material"]]
    por_cuadrante = {clave: [a["nombre"] for a in evaluados if a["cuadrante"] == clave] for clave in CUADRANTES}

    if not evaluados:
        resumen = "Todavia no hay ningun asunto con sus seis notas completas."
    else:
        resumen = ("De %d asuntos evaluados, %d resultaron materiales con umbral %s: %d por impacto y por dinero, "
                   "%d solo por impacto y %d solo por dinero."
                   % (len(evaluados), len(materiales), ("%g" % corte),
                      len(por_cuadrante["doble"]), len(por_cuadrante["impacto"]),
                      len(por_cuadrante["financiera"])))

    return {
        "umbral": corte,
        "total_evaluados": len(evaluados),
        "total_materiales": len(materiales),
        "asuntos": evaluados,
        "materiales": materiales,
        "no_materiales": [a for a in evaluados if not a["material"]],
        "pendientes": pendientes,
        "por_cuadrante": por_cuadrante,
        "resumen": resumen,
        "metodologia": METODOLOGIA,
        "aviso": AVISO,
        "fuente": FUENTE,
    }


def matriz(asuntos, umbral=UMBRAL_POR_DEFECTO):
    """Datos para dibujar la matriz: un punto por asunto en los dos ejes.

    Acepta asuntos ya evaluados o sin evaluar (en ese caso los evalua primero).
    El eje horizontal es el impacto en el mundo y el vertical el efecto en el
    negocio; ambos van de 1 a 5.
    """
    lista = list(asuntos or [])
    if any(a.get("puntaje_impacto") is None for a in lista if isinstance(a, dict)):
        calculo = evaluar(lista, umbral)
        lista = calculo["asuntos"]
        corte = calculo["umbral"]
        pendientes = [a["nombre"] for a in calculo["pendientes"]]
    else:
        corte = _umbral(umbral)
        pendientes = []

    puntos = []
    for asunto in lista:
        puntos.append({
            "id": asunto.get("id") or asunto.get("nombre"),
            "nombre": asunto.get("nombre"),
            "dimension": asunto.get("dimension", ""),
            "x": asunto.get("puntaje_impacto"),
            "y": asunto.get("puntaje_financiero"),
            "material": asunto.get("material"),
            "cuadrante": asunto.get("cuadrante"),
            "color": asunto.get("color") or COLOR_DIMENSION.get(asunto.get("dimension"), "#6C757D"),
        })
    puntos.sort(key=lambda p: (-(p["x"] or 0), -(p["y"] or 0), p["nombre"] or ""))

    return {
        "umbral": corte,
        "eje_x": {"clave": "puntaje_impacto", "nombre": "Impacto de la empresa en el mundo",
                  "minimo": ESCALA_MINIMA, "maximo": ESCALA_MAXIMA},
        "eje_y": {"clave": "puntaje_financiero", "nombre": "Efecto del mundo en el negocio",
                  "minimo": ESCALA_MINIMA, "maximo": ESCALA_MAXIMA},
        "puntos": puntos,
        "cuadrantes": CUADRANTES,
        "colores": COLOR_DIMENSION,
        "sin_evaluar": pendientes,
        "leyenda": ("Arriba a la derecha estan los asuntos que importan por las dos razones: son los "
                    "primeros que hay que gestionar y reportar."),
    }
