# Ciclo de Bolsa — Análisis y Modelado DEVS

## Problema

La simulación se corta antes de llegar al tiempo de terminación (`setTerminationTime(100000)`). El log muestra que el sistema entra en `await_stop_bag` y nunca vuelve a generar eventos, aunque el `MedicalOrderGenerator` sigue produciendo órdenes nuevas.

## Causa

En `controller_pump.py`, el `extTransition` tiene una guarda que retorna temprano cuando `bag_state == EMPTY_BAG`:

```python
if state["bag_state"][0] == BagState.EMPTY_BAG:
    return state
```

Esto ignora **todas** las entradas externas, incluyendo nuevas órdenes médicas. El flujo queda:

```
EMPTY_BAG ──(llega orden médica)──▶ [ignorada]
```

El `MedicalOrderGenerator` sigue generando órdenes y el `EndBagGenerator` programa fines de bolsa, pero el controlador las ignora. El Logger deja de recibir `RECORD_EVENT` y el archivo de log se queda estancado en el último estado registrado (~20673s).

## Solución

Modificar la guarda de `EMPTY_BAG` para que acepte nuevas órdenes médicas con `c > 0` y reinicie el ciclo de la bolsa:

```python
if state["bag_state"][0] == BagState.EMPTY_BAG:
    if self.in_medical_order in inputs:
        _, c = inputs[self.in_medical_order][0]
        if c > 0:
            # Reiniciar ciclo: nueva bolsa, nuevo flujo
            state["bag_state"] = (BagState.NORMAL_BAG, float('inf'))
            state["flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
            delay = random.uniform(0.0, 3.0)
            state["actions"] = conLog(
                state_before,
                [((PumpOutput.ADJUST_FLOW, c - state["last_sensor_medition"]), delay)]
            )
            state["medical_order"] = c
        else:
            # Orden de detención: mantener bomba parada
            state["medical_order"] = c
            state["actions"] = conLog(
                state_before,
                [(PumpOutput.STOP_PUMP, 0.0)]
            )
    return state
```

## Diagrama DEVS del Ciclo Completo

```
                     ┌──────────────────────────────────────────────┐
                     │                                              │
                     ▼                                              │
              ┌─────────────┐    end_bag      ┌──────────┐         │
              │  NORMAL_BAG │───────────────▶  │ END_BAG  │         │
              │  (τ = ∞)    │                  │ (τ = ∞)  │         │
              └─────────────┘                  └─────┬────┘         │
                     ▲                              │               │
                     │                     intTransition:           │
                     │                     pop LOW_ALARM            │
                     │                              │               │
                     │                              ▼               │
                     │                       ┌──────────────┐       │
                     │                       │AWAIT_STOP_BAG│       │
                     │                       │   (τ = 60)   │       │
                     │                       └──────┬───────┘       │
                     │                              │               │
                     │                     intTransition:           │
                     │                     sin acciones, τ expira   │
                     │                              │               │
                     │                              ▼               │
                     │                       ┌──────────────┐       │
                     │                       │  EMPTY_BAG   │       │
                     │                       │   (τ = ∞)    │       │
                     │                       └──────┬───────┘       │
                     │                              │               │
                     │              ┌───────────────┘               │
                     │              │  nueva orden médica (c > 0)   │
                     └──────────────┘                               │
                                                                    │
              (los otros inputs: sensor_flow,                        │
               end_bag, nurse_confirmation                          │
               se ignoran en EMPTY_BAG)                             │
                                                                    │
              ┌─────────────────────────────────────────────────────┘
              │
              ▼
      Simulación continúa hasta
      setTerminationTime(100000)
```

## Transiciones entre Estados de Bolsa

| Desde | Evento | Acción | Siguiente Estado |
|---|---|---|---|
| `NORMAL_BAG` | `in_end_bag` | `LOW_ALARM` + `conLog` | `END_BAG` |
| `END_BAG` | `intTransition` (pop `LOW_ALARM`) | `τ = 60.0` | `AWAIT_STOP_BAG` |
| `AWAIT_STOP_BAG` | `intTransition` (sin acciones, τ expira) | `STOP_PUMP` + `conLog` | `EMPTY_BAG` |
| `EMPTY_BAG` | `in_medical_order` con `c > 0` | `ADJUST_FLOW` + `conLog` | `NORMAL_BAG` |
| `EMPTY_BAG` | `in_medical_order` con `c ≤ 0` | `STOP_PUMP` + `conLog` | `EMPTY_BAG` |
| `EMPTY_BAG` | cualquier otro input | ignorado | `EMPTY_BAG` |

## Consideraciones DEVS

- `timeAdvance` retorna `∞` para `NORMAL_BAG` y `EMPTY_BAG` → el controlador solo avanza por eventos externos.
- `AWAIT_STOP_BAG` tiene `τ = 60.0` como timeout: si no llegan eventos externos, el `intTransition` lo captura automáticamente.
- `conLog(state_before, actions)` captura el estado **previo** a la transición, por eso en el log se ve el timer antes del decremento.
- `EndBagGenerator` recibe la misma orden médica que el controlador (conexión `IC` en `PumpSystem`), así que al reiniciar el ciclo también programa un nuevo `end_bag` automáticamente.
