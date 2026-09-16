# Catálogo de lo que puedo hacer

Si algo no está aquí, todavía no existe: dilo con honestidad en vez de
improvisar. Este archivo se actualiza cuando se agregan capacidades.

## Empezar y orientarse

| Necesidad de la persona | Skill |
|---|---|
| «Hola», «no sé por dónde empezar», «¿qué puedes hacer?» | `ayuda` |
| Registrar su empresa por primera vez | `inicio` |
| El motor no funciona o falta Python | `preparar-equipo` |
| «¿Cómo vamos?», resumen para la gerencia o el directorio | `tablero` |
| «¿Qué nos falta?», radiografía general con puntaje y brechas | `diagnostico-esg` |

## Datos

| Necesidad | Skill |
|---|---|
| Cargar boletas, facturas, PDF, fotos o planillas | `cargar-datos` |
| Preguntar por los datos cargados, revisar datos raros o meses faltantes | `consultar-datos` |
| Respaldar documentos y verificar que no cambiaron | `evidencias` |

## Huella de carbono y metas

| Necesidad | Skill |
|---|---|
| Medir emisiones propias y de la energía comprada (alcances 1 y 2) | `huella-carbono` |
| Estimar la cadena de valor: compras, fletes, viajes, residuos | `alcance-3` |
| Definir una meta creíble y ver si se puede cumplir | `metas-net-zero` |
| Decidir qué medidas hacer primero y cuánto cuesta cada tonelada | `plan-descarbonizacion` |

## Agua

| Necesidad | Skill |
|---|---|
| Cuánta agua usa la empresa, indicadores GRI 303, huella de escasez | `huella-hidrica` |

## Transporte y cadena de frío

| Necesidad | Skill |
|---|---|
| Cuánto emite un envío o la flota; comparar camión, tren, barco y avión | `logistica-glec` |
| Revisar si se rompió la cadena de frío; a qué temperatura guardar algo | `cadena-frio` |

## Cumplimiento en Chile y Perú

| Necesidad | Skill |
|---|---|
| «¿Qué leyes me aplican?», fiscalizaciones, cartas de la autoridad | `brechas-cumplimiento` |
| Denuncia de acoso o violencia laboral, protocolo de prevención | `ley-karin` |
| Envases y responsabilidad extendida del productor | `ley-rep` |
| Declaraciones ambientales: RETC, residuos, emisiones, riles, impuesto verde | `retc` |
| Modelo de prevención de delitos y gobierno corporativo (Ley 20.393, CMF) | `gobernanza` |
| Datos personales, consentimiento, Ley 21.719 | `proteccion-datos` |
| Faenas mineras: relaves, ventilación, exposición, ruido, altura | `mineria` |
| Activos fijos, vida útil del SII, depreciación y recambio de equipos | `activos-fijos` |

## Personas

| Necesidad | Skill |
|---|---|
| Dotación, rotación, brecha salarial, accidentes, capacitación, inclusión | `social-personas` |
| Capacitar al equipo en temas ESG y dejar constancia | `academia` |

## Exportar a Europa

| Necesidad | Skill |
|---|---|
| «Mi cliente europeo me pide datos»: qué le aplica y qué no | `union-europea` |
| Arancel de carbono en frontera para acero, aluminio, cemento, fertilizantes | `cbam` |
| Costo de carbono del flete marítimo (EU ETS y FuelEU) | `maritimo-ets` |
| Productos libres de deforestación: soya, cacao, café, madera, carne | `eudr` |

## Reportes y comunicación

| Necesidad | Skill |
|---|---|
| Hacer una memoria o reporte (GRI, NIIF S1/S2, CMF, ESRS, VSME) | `reportes` |
| Decidir qué asuntos son relevantes para el reporte | `doble-materialidad` |
| Revisar una afirmación ambiental antes de publicarla | `greenwashing` |
| Prepararse para que un tercero verifique la información | `aseguramiento` |
| Pedir datos a los proveedores y procesar lo que responden | `proveedores` |

## Uso interno de una consultora

| Necesidad | Skill |
|---|---|
| Seguimiento comercial de servicios ESG: prospectos, embudo, bitácora | `crm` |

## Agentes especialistas

Los agentes de `.claude/agents/` hacen trabajo largo en segundo plano y
devuelven un resumen. **Reúne tú los datos antes de delegar**: ellos no pueden
preguntarle nada a la persona.

| Agente | Cuándo delegarle |
|---|---|
| `agente-carbono` | Procesar muchos documentos y calcular una huella completa |
| `agente-datos` | Leer y ordenar decenas de boletas o planillas |
| `agente-auditor` | Revisar algo antes de que salga de la empresa |
| `agente-cumplimiento` | Revisión normativa a fondo de Chile o Perú |
| `agente-ley-karin` | Llevar el procedimiento completo de una denuncia |
| `agente-mineria` | Revisión de seguridad y salud en una faena minera |
| `agente-union-europea` | Evaluar todo lo que Europa le exige a un exportador |
| `agente-finanzas` | Cartera de activos fijos, depreciación y plan de recambio |
| `agente-investigador` | Verificar en fuentes oficiales un dato o un cambio normativo |
| `agente-reportes` | Redactar el borrador de una memoria o reporte |
| `agente-proveedores` | Pedir y procesar datos de la cadena de suministro |
| `agente-academia` | Capacitar a una persona o a un equipo |
| `agente-crm` | Seguimiento comercial de servicios ESG |

## Comandos del motor más usados

```bash
python .claude/motor/esg.py --ayuda                      # todo lo que sabe hacer
python .claude/motor/esg.py empresa listar
python .claude/motor/esg.py plantilla listar
python .claude/motor/esg.py huella factores --uso gasto  # nombres del catálogo
python .claude/motor/esg.py huella calcular --periodo 2025
python .claude/motor/esg.py diagnostico evaluar
python .claude/motor/esg.py tablero generar
```
