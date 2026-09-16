---
name: logistica-glec
description: Emisiones del transporte de carga según ISO 14083 y el método GLEC, tramo por tramo (camión, tren, barco, avión y paso por puertos y bodegas). Úsala cuando pidan la huella de un envío o de la flota, cuando un cliente o un cargador exija emisiones de transporte, cuando comparen modos o rutas, o cuando pregunten cuánto contamina despachar.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Emisiones del transporte de carga

Cuando un cliente grande pregunta «¿cuánto emite traerme esto?», la respuesta no
es un número del aire: es una cadena partida en tramos, con la masa real, la
distancia correcta y la intensidad de cada vehículo. Eso es **ISO 14083:2023**,
la norma que usan los cargadores y los operadores logísticos de todo el mundo.

## La idea en un dibujo

```
Curicó ──camión──► San Antonio ──[puerto]──► ═══barco═══► Rotterdam ──[puerto]──► ──camión──► Venlo
 tramo 1              tramo 2                  tramo 3       tramo 4                 tramo 5
```

**Se abre un tramo nuevo cada vez que cambia el vehículo o la carga pasa por un
puerto, un terminal o una bodega.** Cada tramo se calcula así:

```
emisiones del tramo = toneladas × kilómetros × intensidad del vehículo
```

Y los puertos y bodegas también emiten: no son un cero, son un dato que falta.

## 1. Empieza por preguntar, no por calcular

Antes de tocar el motor necesitas cinco cosas. Pídelas en lenguaje normal:

1. **Qué se movió y cuánto pesaba** (la mercancía con su caja, sin los pallets
   ni el contenedor). Si solo saben los contenedores, sirve.
2. **Por dónde pasó**: origen, destino y las escalas.
3. **En qué vehículo** cada tramo: camión, camión refrigerado, furgón de
   reparto, tren, barco, avión.
4. **Cuántos kilómetros** por tramo. Si no los saben, se estiman entre ciudades
   o puertos **y se anota como supuesto**.
5. **Si el transportista entrega su propio dato de emisiones.** Si lo entrega,
   ese dato manda: es mucho mejor que cualquier promedio.

## 2. Carga la cadena

```bash
python .claude/motor/esg.py logistica plantilla
```

Queda en `datos/cadenas_transporte.xlsx` con un ejemplo que hay que reemplazar.
Una fila por tramo. Si la persona te dicta el viaje, **llena la planilla tú** y
muéstrale lo que escribiste antes de calcular.

## 3. Calcula

```bash
python .claude/motor/esg.py logistica calcular --cadena "Fruta a Venlo"
python .claude/motor/esg.py logistica informe --cadena "Fruta a Venlo"
```

Para una pregunta suelta, sin planilla:

```bash
python .claude/motor/esg.py logistica tramo --vehiculo "camion refrigerado" --toneladas 12 --km 220
```

## 4. Explica el resultado en este orden

1. **El total** en kg o toneladas de CO2e.
2. **La intensidad**: cuántos gramos por tonelada-kilómetro. Es lo que compara
   un cliente entre proveedores.
3. **Dónde está el bulto.** Casi siempre sorprende: en el ejemplo de arriba el
   barco hace el 98 % de los kilómetros-tonelada pero solo el 81 % de las
   emisiones; los 370 km de camión aportan el 19 %. **La palanca está en el
   tramo terrestre, no en el marítimo.**
4. **Qué falta** para que la cifra sea completa (casi siempre, los puertos).

## Las cuatro cosas que se hacen mal

**1. Reportar solo lo que sale del tubo de escape.** ISO 14083 exige sumar
también lo que costó producir y llevar ese combustible hasta el estanque. Es
entre un 15 % y un 30 % más según el modo, y el motor lo separa:
`de_operacion` y `de_provision_de_energia`. Un camión eléctrico tiene casi cero
por el escape y bastante por la electricidad: sin esa suma, la comparación
miente.

**2. Mezclar tipos de distancia.** La intensidad está calculada sobre la **ruta
más corta practicable**. Si usas la distancia del odómetro sin ajustarla, el
resultado queda inflado. El motor lo corrige solo si le dices qué tipo es:

| Modo | Qué distancia usar | Ajuste |
|---|---|---|
| Carretera | La más corta practicable | +5 % si partes de la línea recta |
| Marítimo | La más corta practicable | +15 % si partes de la línea recta |
| Ferrocarril y fluvial | La real, que es la de la vía | Ninguno |
| Aéreo | Siempre línea recta | +95 km por rodaje, despegue y aproximación |

**3. Contar el peso equivocado.** La masa es la mercancía **con el embalaje del
vendedor** pero **sin los pallets ni el contenedor**. Si solo se sabe cuántos
contenedores, se asumen 10 toneladas por contenedor (6 si la carga es liviana,
14,5 si es pesada) **y se dice que es un supuesto**.

**4. Poner los puertos en cero.** ISO 14083 obliga a incluirlos. No existe un
factor público de terminal que se pueda redistribuir, así que el motor marca el
resultado como **incompleto** y pide el dato al operador. Eso es lo correcto:
«no lo tengo» es una respuesta honesta, «cero» es una mentira.

## Comparar modos

```bash
python .claude/motor/esg.py logistica comparar --toneladas 12 --km 500
```

Sirve para una conversación de decisión: mover 12 toneladas 500 km va de 26 kg
CO2e en granelero a 10.592 kg en avión. **Pero la comparación es solo de
emisiones**: no mira plazo, costo, ni si la ruta existe. Dilo siempre.

## Ver qué vehículos hay

```bash
python .claude/motor/esg.py logistica factores --modo maritimo
```

Cada uno trae su fuente, su año y su licencia. Los factores vienen del gobierno
británico (DESNZ, licencia abierta): son una referencia internacional, no
valores chilenos ni peruanos. **Dilo en el informe.**

## Sobre el GLEC Framework

El método que usa este módulo es el de ISO 14083, que es también la base del
GLEC Framework. **Los valores por defecto del GLEC no están aquí y no pueden
estarlo**: su licencia no permite redistribuirlos. Si la empresa tiene acceso al
GLEC, puede usar sus factores cargándolos ella en la columna «Intensidad
propia». Si alguien pide expresamente «factores GLEC», explícale esto en vez de
pasar los de DESNZ como si lo fueran.

## Cierre

Termina siempre diciendo: el total, la intensidad, qué tramo conviene atacar,
qué quedó fuera y de dónde salen los factores. Y recuerda que para una
declaración ante un cliente exigente o una verificación, los datos de actividad
(pesos y distancias) tienen que estar respaldados: ofrécelo con la skill
`evidencias`.
