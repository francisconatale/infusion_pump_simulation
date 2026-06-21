# Revisión modelos vs documentación — Decisiones

## Resumen del proceso

Se compararon los 8 modelos atómicos DEVS (`pump_proyect/src/models/`) contra sus secciones correspondientes en `docs/inform_dev/secciones/`. Se identificaron diferencias, se clasificaron por criticidad y se decidió en cada caso si corregir el código o la documentación.

---

## Decisiones por modelo

### 1. `gen_medical_order.py` — 01_generador_med.tex

| Aspecto | Doc | Código | Decisión |
|---------|-----|--------|----------|
| Estado | `(c, t)` | `{sigma, order}` | Código bien. Sigma necesario para DEVS |
| Unidad timeAdvance | horas | segundos (via `hours_to_seconds`) | Equivalente, DEVS usa números abstractos |
| Formato salida | `(c, t, 0)` | `[(hours, ml)]` | Consumido correctamente por controller y end_bag |
| Primer evento | en `t₀` | inmediato (`sigma=0.0`) | Intencional, arranca la simulación |
| `hours`/`ml` en estado | no existen | redundantes | ✅ **Eliminados del código** (solo `order` y `sigma`) |

### 2. `gen_bag_end.py` — 02_fin_bolsa.tex

| Aspecto | Doc | Código | Decisión |
|---------|-----|--------|----------|
| Puerto `in_nurse_confirmation` | no existe | sí existe | Pendiente |
| Salida | `(finBolsa, 0)` | `("end_bag",)` | Pendiente |
| RESTA de elapsed en PROGRAMMED+ACTIVE | no modifica σ | `hours = hours - e` | Pendiente |

### 3. `gen_nurse.py` — 03_enfermero.tex

| Aspecto | Doc | Código | Decisión |
|---------|-----|--------|----------|
| Salida | `(confirmacionEnfermero, 0)` | `["CONFIRMATION_NURSE"]` | Pendiente (cosmético) |
| Nombres | español | inglés | Pendiente (cosmético) |

### 4. `sensor_flow.py` — 04_sensor.tex

| Aspecto | Doc | Código | Decisión |
|---------|-----|--------|----------|
| Caso σ=∞ en extTransition | no existe | pone σ=0.0 | Pendiente |
| Clamp σ-e | no existe | `max(0.0, σ-e)` | Pendiente |
| Rango [0,200] | exigido | no validado | Pendiente (baja) |

### 5. `controller_pump.py` — 05_controlador.tex

| # | Aspecto | Doc original | Código | Decisión |
|---|---------|-------------|--------|----------|
| 1 | Absorción global EMPTY_BAG | Ignora toda entrada | Orden c>0 resetea bolsa | ✅ **Doc actualizada** |
| 2 | Guardia CRITICAL_FLOW | No existe | Bloquea ajustes en alarma crítica | ✅ **Doc actualizada** |
| 3 | Sensor tol<5 | `actions = []` | Encola ADJUST_FLOW + RECORD_EVENT | ✅ **Doc actualizada** |
| 4 | Confirmación enfermero | No cambia est_bolsa | Resetea a NORMAL_BAG | ✅ **Doc actualizada** |
| 5 | intTransition cola | Vacía cola | Solo pop(0) — RECORD_EVENT se consume en paso siguiente | Equivalente |
| 6 | τ_bolsa se decrementa siempre | No en bolsaBaja/esperando/vacia | Siempre se decrementa | Pendiente |
| 7 | Caso extra tol≥5 + CRITICAL_FLOW | No existe | Encola CRITICAL_ALARM | Pendiente |

### 6. `actuator_pump.py` — 06_bomba.tex

| Aspecto | Doc original | Código | Decisión |
|---------|-------------|--------|----------|
| Saturación | `sat(cR + Δ)` (suma directa) | `sat(cR + α·Δ)` con `α ~ U(0.10, 0.30)` | ✅ **Doc actualizada** (modela inercia) |
| Sigma post-ajuste | `random_truncado(0.5)` | `random.uniform(0, 5)` | ✅ **Doc actualizada** |
| OffBomb resetea caudal | `cR = 0` | No resetea `currentCaudal` | Pendiente |
| Puerto entrada ajuste | inconsistente (`-1` vs `1`) | Sin puerto explícito | ✅ **Doc corregida** |

### 7. `alarm_module.py` — 07_alarmas.tex

| Aspecto | Doc | Código | Decisión |
|---------|-----|--------|----------|
| Clamp σ-e | no existe | `max(0.0, hours-e)` | Pendiente (baja) |
| Lógica de estados | idéntica | idéntica | ✅ **Sin cambios** — modelo más fiel |

### 8. `logger.py` — 08_logger.tex

| Aspecto | Doc original | Código | Decisión |
|---------|-------------|--------|----------|
| Arquitectura | Lista en memoria `L(S_ctrl × R≥0)` | Escritura directa a CSV | ✅ **Doc reescrita** |
| Puertos | 1: `(registrarEvento, 9)` | 3: `in_state_control`, `in_alarm_module`, `in_nurse_confirmation` | ✅ **Doc reescrita** |
| Estado formal | `(lista, t_acum, μ)` | Solo `{accumulated_time}` + `last_data` auxiliar | ✅ **Doc reescrita** |

---

## Documentos modificados

| Archivo | Cambio |
|---------|--------|
| `src/models/gen_medical_order.py` | Eliminados `hours`, `ml` del estado (redundantes) |
| `src/scenarios/initial_states_factory.py` | Eliminados `initial_hours`, `initial_ml` de `med_order` |
| `docs/inform_dev/secciones/05_controlador.tex` | Caso EMPTY_BAG (no absorbente), guardia CRITICAL_FLOW, sensor tol<5 encola, confirmación resetea bolsa |
| `docs/inform_dev/secciones/06_bomba.tex` | Función ajustar con atenuación aleatoria, sigma corregido, puerto consistente |
| `docs/inform_dev/secciones/08_logger.tex` | Reescrito completo (3 puertos, CSV, last_data) |

---

## Principio aplicado

> El código es la fuente de verdad. Cuando hay discrepancia entre la documentación y la implementación, se actualiza la documentación para reflejar el comportamiento real del código, a menos que se identifique un bug en el código.
