# Atlas — Cálculo de Disponibilidad por Slot

**Alcance de este documento:** el mecanismo específico para calcular, de forma eficiente, qué horarios de inicio tienen cupo disponible para un servicio en un día dado. Complementa el diseño general de entidades (Servicio, ObjetoReservable, TarifaServicio, Reserva, AgentMetadata) definido en el documento de diseño Padel/Golf/Restaurante — aquí se detalla únicamente el algoritmo de disponibilidad.

**No cubre:** prevención de condiciones de carrera al escribir una reserva (eso se resuelve con un exclusion constraint GiST sobre la tabla `reserva`, documentado aparte) — este documento trata exclusivamente el cálculo de **lectura** de disponibilidad.

---

## 1. Principio general

Los slots **no se persisten** — se derivan dinámicamente a partir de tres parámetros del servicio:

- `horarioLaboral` (inicio/fin del día operativo)
- `duracionOcupacionMinutos` + `bufferMinutos` (cuánto tiempo real ocupa una reserva sobre el objeto reservable)
- `intervaloParrilla` (cada cuánto se ofrece una hora de inicio)

`intervaloParrilla` es **independiente** de la duración — puede ser menor, igual, o mayor que `duracionOcupacionMinutos + bufferMinutos`. Esto es intencional: permite que un servicio como Restaurante ofrezca horas de entrada cada 30 minutos aunque una mesa tarde 90 minutos en liberarse, mientras que un servicio como Padel puede configurarse con `intervaloParrilla == duración total` si no le interesa esa granularidad.

## 2. Generación de la parrilla de slots

```python
def generar_parrilla(horario_inicio, horario_fin, intervalo_parrilla_min, fecha):
    slots = []
    t = combinar(fecha, horario_inicio)
    fin_dia = combinar(fecha, horario_fin)
    while t < fin_dia:
        slots.append(t)
        t += timedelta(minutes=intervalo_parrilla_min)
    return slots
```

Cada slot candidato `T` representa una hora de inicio posible. Su rango de ocupación, si se reservara, sería `[T, T + duracionOcupacionMinutos + bufferMinutos]`.

## 3. Recuperación de datos desde PostgreSQL

En vez de traer cada reserva individual y compararla fila por fila contra cada slot (caro: `slots × reservas` comparaciones), se recupera la ocupación ya **agrupada por su rango exacto** — todas las reservas que comparten `(hora_inicio, hora_fin)` colapsan en una sola fila con su conteo:

```sql
SELECT hora_inicio, hora_fin, COUNT(*) AS reservas_count
FROM reserva
WHERE objeto_reservable_id IN (:ids_calificados)
  AND estado IN ('confirmada', 'pendiente_bloqueante')
  AND hora_inicio < :dia_fin
  AND hora_fin > :dia_inicio
GROUP BY hora_inicio, hora_fin;
```

`:ids_calificados` es el resultado de filtrar `ObjetoReservable` activos cuyo `[capacidadMin, capacidadMax]` cubra la cantidad de personas solicitada. Un índice B-tree normal sobre `(objeto_reservable_id, hora_inicio)` es suficiente — no se requiere índice GiST para esta consulta (el GiST solo es necesario para el exclusion constraint de escritura, fuera del alcance de este documento).

Este único query trae toda la información de ocupación del día en un conjunto pequeño de filas — no una fila por reserva individual, sino una fila por combinación distinta de horario ya agrupada por la base de datos.

## 4. El error a evitar: comparar cada grupo de forma aislada

Una primera intuición razonable es: "si algún grupo de reservas que se solapa con el slot tiene un conteo igual a la cantidad de objetos calificados, el slot está lleno". **Esto es insuficiente** — la ocupación real de un instante es la **suma** de todos los grupos activos en ese instante, no el máximo de un solo grupo, porque cada reserva ocupa un objeto reservable distinto (garantizado por el exclusion constraint de escritura).

### Contraejemplo

Capacidad total: 4 objetos calificados. Duración total (ocupación + buffer): 90 min. `intervaloParrilla`: 30 min.

| Grupo | Rango | Conteo |
|---|---|---|
| A | 6:30–8:00 | 2 |
| B | 7:00–8:30 | 2 |

Ningún grupo individual alcanza 4 — cada uno tiene 2. Pero entre **7:00 y 8:00**, ambos grupos están activos simultáneamente: 2 objetos ocupados por A + 2 objetos ocupados por B = **4 objetos ocupados a la vez**, el total de la capacidad. Un slot que caiga en ese tramo (ej. 7:00 o 7:30) debe marcarse **sin disponibilidad**, aunque ningún grupo individual lo indique por sí solo.

## 5. El algoritmo correcto: sweep de ocupación combinada dentro de la ventana del slot

Para cada slot candidato `T`, se identifican los grupos que se solapan con su ventana `[T, T + duración total)`, y se evalúa la ocupación combinada en cada punto de la rejilla dentro de esa ventana — no solo al inicio:

```python
def slot_disponible(slot_inicio, slot_fin, grupos, capacidad_total, paso_minutos):
    # grupos: lista de (hora_inicio, hora_fin, count) que solapan con [slot_inicio, slot_fin)
    relevantes = [
        g for g in grupos
        if g.hora_inicio < slot_fin and g.hora_fin > slot_inicio
    ]
    if not relevantes:
        return True

    punto = slot_inicio
    while punto < slot_fin:
        ocupacion = sum(
            g.count for g in relevantes
            if g.hora_inicio <= punto < g.hora_fin
        )
        if ocupacion >= capacidad_total:
            return False
        punto += timedelta(minutes=paso_minutos)
    return True
```

`paso_minutos` puede ser `intervaloParrilla` — no se necesita granularidad de segundos, porque la ocupación solo cambia de valor en los puntos de la rejilla (los grupos están alineados a múltiplos de `intervaloParrilla`).

## 6. Por qué esto es barato

El número de grupos relevantes por slot está acotado por `duracionTotal / intervaloParrilla` — en la práctica, un puñado (2 a 6 grupos) incluso en negocios con alto volumen. El sweep sobre esos pocos grupos es trivial en tiempo de cómputo. El costo real del proceso completo es, en orden de magnitud:

1. Un query SQL indexado que trae del orden de decenas de filas ya agrupadas (no cientos de reservas individuales).
2. Un bucle en Python sobre slots de la parrilla (típicamente decenas por día), cada uno evaluando un puñado de grupos.

No se requiere `NOT EXISTS` correlacionado, ni índice GiST, ni traer cada reserva individual a Python para la lectura de disponibilidad.

## 7. Casos particulares que el algoritmo ya cubre sin rama especial

- **`intervaloParrilla == duracionTotal`** (caso Padel/Golf típico, sin ventanas superpuestas): cada slot tiene como máximo un grupo relevante, el sweep se reduce a un único punto de evaluación — se comporta igual que la comparación simple de igualdad, sin necesidad de tratarlo como caso especial en el código.
- **`intervaloParrilla < duracionTotal`** (caso Restaurante típico, entradas más frecuentes que la duración estimada): el sweep evalúa varios puntos dentro de la ventana del slot, capturando la ocupación combinada de varios grupos — el escenario que motivó este diseño.
- **`intervaloParrilla > duracionTotal`**: cada grupo cabe dentro de una sola ventana de slot sin solaparse con la siguiente — se comporta igual que el primer caso.

## 8. Qué queda fuera de este mecanismo (y por qué está bien que quede fuera)

- **Prevención de doble reserva en la escritura:** este algoritmo es de **lectura** — informa al agente qué slots mostrar como disponibles. La garantía final contra condiciones de carrera vive en el exclusion constraint GiST sobre `reserva` al momento del `INSERT`, que es independiente de este cálculo y no se debilita ni se sustituye por él. Es normal, y esperado, que la consulta de disponibilidad pueda quedar levemente desactualizada entre que se muestra al cliente y se confirma la reserva — el constraint es la red de seguridad final.
- **Asignación del objeto específico:** este algoritmo responde "¿hay cupo en este slot?", no "¿cuál objeto se asigna?". La asignación (criterio de capacidad máxima más cercana) es una consulta aparte, dirigida a un solo slot puntual en el momento de crear la reserva.
