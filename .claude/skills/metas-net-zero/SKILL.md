---
name: metas-net-zero
description: Definir una meta de reducción de emisiones creíble, calcular su trayectoria año a año y estimar la probabilidad de cumplirla. Úsala cuando hablen de metas, carbono neutralidad, net zero, SBTi, compromisos climáticos, o cuando quieran anunciar públicamente una reducción.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Metas de reducción

Una meta sirve si tiene tres cosas: **un punto de partida medido**, **una
trayectoria año a año** y **un plan que la haga probable**. Sin eso es un
anuncio, y un anuncio sin respaldo hoy es riesgo legal.

## 1. Punto de partida

Necesitas la huella del año base. Si no existe, primero la skill
`huella-carbono`. El año base debe ser 2015 o posterior y tener datos
confiables (no un año raro, como un año de pandemia o de paro de planta).

## 2. Definir la meta

```bash
python .claude/motor/esg.py meta definir --anio-base 2025 --anio-meta 2030 --base 12500
```

Si no indicas `--base`, toma los alcances 1 y 2 de la última huella calculada.
La tasa por defecto es **4,2 % anual lineal** (alineamiento con 1,5 °C para
alcances 1 y 2); para alcance 3 la referencia es 2,5 % anual. Se puede cambiar
con `--tasa`.

Si la persona dice su meta como un porcentaje total («bajar 42 % al 2030»), no
la conviertas tú: pásala tal cual y el motor calcula la tasa lineal.

```bash
python .claude/motor/esg.py meta definir --anio-base 2025 --anio-meta 2030 --reduccion 42
```

Explícale la diferencia que más confunde: la reducción es **lineal, no
compuesta**. Bajar 42 % en 10 años equivale a un 5,3 % compuesto anual, no a un
4,2 %.

## 3. Revisar si la meta se sostiene

```bash
python .claude/motor/esg.py meta validar
```

Revisa los criterios públicos: año base válido, horizonte entre 5 y 10 años,
si el alcance 3 supera el 40 % del total (en ese caso la meta de alcance 3 es
obligatoria y debe cubrir al menos el 67 %), límite de exclusiones del 5 % y la
regla de que **los créditos de carbono no cuentan como reducción**.

Aclara siempre: esto es la matemática de los criterios; **la validación formal
de una meta la hace la propia iniciativa (SBTi), con su proceso y sus costos**.
Nosotros no validamos nada.

## 4. ¿Qué tan probable es cumplirla?

```bash
python .claude/motor/esg.py meta probabilidad
```

Simula miles de escenarios combinando lo que la empresa no controla del todo:
crecimiento del negocio, descarbonización de la red eléctrica, eficiencia
continua y si los proyectos planificados se ejecutan o no.

Cómo se lee el resultado:

| Probabilidad | Qué significa | Qué hacer |
|---|---|---|
| 80 % o más | La meta es creíble con el plan actual | Publicarla con sus supuestos |
| 50–80 % | Alcanzable, pero sin seguridad | Sumar medidas antes de anunciarla |
| Menos de 50 % | No es creíble hoy | **No anunciarla** hasta tener plan |
| «sin estimar» | No hay supuestos: nada que simular | Armar primero el plan con `plan-descarbonizacion` |

Si la persona todavía no tiene medidas ni sabe cuánto va a crecer, el motor
**no inventa supuestos** y devuelve la probabilidad como «sin estimar»: solo
muestra dónde quedan las emisiones si nada cambia. Dilo así, sin convertirlo en
un «0 %», que suena a veredicto cuando en realidad falta información.

La **brecha mediana** que entrega es el número clave: son las toneladas anuales
que hay que cubrir con medidas concretas. Ese número pasa directo a la skill
`plan-descarbonizacion`.

Para cambiar los supuestos, prepara un archivo JSON y pásalo con `--supuestos`:

```json
{
  "crecimiento": {"tipo": "normal", "media": 0.025, "desviacion": 0.015},
  "descarbonizacion_red": {"tipo": "triangular", "min": 0.01, "moda": 0.025, "max": 0.045},
  "eficiencia": {"tipo": "triangular", "min": 0.0, "moda": 0.02, "max": 0.03},
  "proyectos": [{"nombre": "Solar", "probabilidad": 0.7, "anio": 2028,
                 "reduccion": {"tipo": "triangular", "min": 0.03, "moda": 0.06, "max": 0.09}}]
}
```

Conversa los supuestos con la persona: «¿cuánto esperan crecer?», «¿el proyecto
solar está aprobado o todavía se evalúa?». Ella los conoce mejor que nadie.

## 5. Informe

```bash
python .claude/motor/esg.py meta informe
```

## Antes de anunciar la meta en público

Esto es lo que evita una acusación de greenwashing:

- Publicar el **año base, el alcance cubierto y la metodología**.
- Publicar los **supuestos** de la proyección.
- Tener un **plan de implementación** concreto y financiado.
- No usar la palabra «neutral» si la reducción se logra comprando créditos: en
  la Unión Europea las afirmaciones de neutralidad basadas en compensación
  están prohibidas desde el 27 de septiembre de 2026 (Directiva 2024/825), y
  en Chile la publicidad engañosa la sanciona la Ley 19.496.
- Si la probabilidad es baja, decirlo internamente antes de comprometerse.

## Meta de largo plazo

Net zero implica reducir **al menos 90 %** respecto del año base y neutralizar
las emisiones residuales con remociones permanentes. Si la empresa habla de
«carbono neutral el próximo año comprando bonos», explícale la diferencia entre
reducir y compensar, sin sermones.
