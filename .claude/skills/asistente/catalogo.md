# Catálogo de lo que puedo hacer

Si algo no está aquí, todavía no existe: dilo con honestidad en vez de
improvisar. Este archivo se actualiza cuando se agregan capacidades.

## Empezar y orientarse

| Necesidad de la persona | Skill |
|---|---|
| «Hola», «no sé por dónde empezar», «¿qué puedes hacer?» | `ayuda` |
| Registrar su empresa por primera vez | `inicio` |
| El motor no funciona o falta Python | `preparar-equipo` |
| «¿Cómo vamos?», resumen para la gerencia | `tablero` |
| «¿Qué nos falta?», radiografía general | `diagnostico-esg` |

## Datos

| Necesidad | Skill |
|---|---|
| Cargar boletas, facturas, PDF, fotos o planillas | `cargar-datos` |
| Preguntar por los datos cargados, revisar datos raros o meses faltantes | `consultar-datos` |
| Respaldar documentos y verificar que no cambiaron | `evidencias` |

## Huella de carbono y metas

| Necesidad | Skill |
|---|---|
| Medir emisiones propias y de la energía comprada | `huella-carbono` |
| Estimar la cadena de valor: compras, fletes, viajes, residuos | `alcance-3` |
| Definir una meta creíble y ver si se puede cumplir | `metas-net-zero` |
| Decidir qué medidas hacer primero y cuánto cuestan | `plan-descarbonizacion` |

## Cumplimiento

| Necesidad | Skill |
|---|---|
| «¿Qué leyes me aplican?», fiscalizaciones, cartas de la autoridad | `brechas-cumplimiento` |
| Denuncia de acoso o violencia laboral en Chile, protocolo de prevención | `ley-karin` |
| Indicadores de personas: dotación, rotación, brecha salarial, accidentes | `social-personas` |

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
python .claude/motor/esg.py huella calcular --periodo 2025
python .claude/motor/esg.py diagnostico evaluar
python .claude/motor/esg.py tablero generar
```
