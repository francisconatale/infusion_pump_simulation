#!/usr/bin/env python3
import csv
import sys

def main(csv_path):
    try:
        with open(csv_path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: {csv_path} not found")
        sys.exit(1)

    if not rows:
        print("El archivo CSV está vacío.")
        return

    # Parse numerical columns
    for row in rows:
        row["time"] = float(row["time"])
        row["actual_flow"] = float(row["actual_flow"])
        row["target_flow"] = float(row["target_flow"])
        row["medical_order"] = float(row["medical_order"])
        row["tolerance_count"] = float(row["tolerance_count"])

    # 1 & 2. Registro de alarmas generadas y Tiempos de respuesta
    alarms_log = []  # list of dict: {"time": t, "type": type}
    pending_alarms = []  # list of dict: {"time": t, "type": type}
    
    response_times_flow = []  # list of tuples: (alarm_time, confirm_time, rt, alarm_type)
    response_times_bag = []   # list of tuples: (alarm_time, confirm_time, rt, alarm_type)
    
    prev_alarm_state = "no_alarm"
    
    for row in rows:
        t = row["time"]
        alarm_state = row.get("alarm_state", "no_alarm")
        event_type = row["event_type"]
        
        # Check if a new alarm is generated (state transition)
        if alarm_state in ("low_alarm", "medium_alarm", "critical_alarm"):
            if alarm_state != prev_alarm_state:
                alarm_event = {"time": t, "type": alarm_state}
                alarms_log.append(alarm_event)
                pending_alarms.append(alarm_event)
        
        # Check for nurse confirmation
        if event_type == "nurse_confirmation":
            # Nurse confirmation clears pending alarms
            while pending_alarms:
                p_alarm = pending_alarms.pop(0)  # FIFO matching
                rt = t - p_alarm["time"]
                if p_alarm["type"] in ("medium_alarm", "critical_alarm"):
                    response_times_flow.append((p_alarm["time"], t, rt, p_alarm["type"]))
                elif p_alarm["type"] == "low_alarm":
                    response_times_bag.append((p_alarm["time"], t, rt, p_alarm["type"]))
                    
        prev_alarm_state = alarm_state

    # 3. Cantidad de detenciones preventivas
    preventive_stops = 0
    prev_stopped = False
    for row in rows:
        actions = row.get("actions", "")
        is_stopped = "stop_pump" in actions
        if is_stopped and not prev_stopped:
            preventive_stops += 1
        prev_stopped = is_stopped

    # 4. Porcentaje de tiempo con infusión correcta
    total_time = 0.0
    correct_time_order = 0.0   # actual_flow == medical_order
    correct_time_target = 0.0  # actual_flow == target_flow
    correct_time_state = 0.0   # flow_state == "normal_flow"
    
    for i in range(len(rows) - 1):
        t_curr = rows[i]["time"]
        t_next = rows[i+1]["time"]
        dt = t_next - t_curr
        if dt <= 0:
            continue
            
        total_time += dt
        
        # Definition A: actual_flow == medical_order (tolerance 0.01)
        if abs(rows[i]["actual_flow"] - rows[i]["medical_order"]) < 0.01:
            correct_time_order += dt
            
        # Definition B: actual_flow == target_flow (tolerance 0.01)
        if abs(rows[i]["actual_flow"] - rows[i]["target_flow"]) < 0.01:
            correct_time_target += dt
            
        # Definition C: flow_state == "normal_flow"
        if rows[i]["flow_state"] == "normal_flow":
            correct_time_state += dt

    # Print results formatted beautifully
    print("=" * 70)
    print(f" RESULTADOS DE LA SIMULACIÓN: {csv_path}")
    print("=" * 70)
    
    print("\n1. REGISTRO DE ALARMAS GENERADAS")
    print("-" * 70)
    if not alarms_log:
        print("No se generaron alarmas durante la simulación.")
    else:
        print(f"{'Tiempo (s)':<15} | {'Tipo de Alarma':<25}")
        print("-" * 70)
        for alarm in alarms_log:
            print(f"{alarm['time']:<15.3f} | {alarm['type']:<25}")
        print(f"Total de alarmas generadas: {len(alarms_log)}")

    def print_response_stats(title, data):
        print(f"\n{title}")
        print("-" * 70)
        if not data:
            print("No se registraron confirmaciones para este tipo de alarmas.")
            return
        
        print(f"{'Alarma T (s)':<15} | {'Confirm. T (s)':<15} | {'Resp. T (s)':<12} | {'Tipo':<15}")
        print("-" * 70)
        for alarm_t, confirm_t, rt, alarm_type in data:
            print(f"{alarm_t:<15.3f} | {confirm_t:<15.3f} | {rt:<12.3f} | {alarm_type:<15}")
        
        r_times = [rt for _, _, rt, _ in data]
        avg_rt = sum(r_times) / len(r_times)
        min_rt = min(r_times)
        max_rt = max(r_times)
        
        print("-" * 70)
        print(f"Estadísticas de respuesta:")
        print(f"  - Tiempo de respuesta promedio: {avg_rt:.3f} s")
        print(f"  - Tiempo de respuesta mínimo:   {min_rt:.3f} s")
        print(f"  - Tiempo de respuesta máximo:   {max_rt:.3f} s")
        print(f"  - Muestras confirmadas:         {len(r_times)}")

    print_response_stats("2. TIEMPO DE RESPUESTA ANTE DESVÍOS DE CAUDAL", response_times_flow)
    print_response_stats("3. TIEMPO DE RESPUESTA ANTE FIN DE BOLSA", response_times_bag)

    print("\n4. CANTIDAD DE DETENCIONES PREVENTIVAS")
    print("-" * 70)
    print(f"Cantidad de detenciones preventivas (stop_pump): {preventive_stops}")

    print("\n5. PORCENTAJE DE TIEMPO CON INFUSIÓN CORRECTA")
    print("-" * 70)
    if total_time > 0:
        pct_order = (correct_time_order / total_time) * 100
        pct_target = (correct_time_target / total_time) * 100
        pct_state = (correct_time_state / total_time) * 100
        print(f"Tiempo total de simulación evaluado: {total_time:.3f} s")
        print(f"A) Según Caudal Real vs Orden Médica (el paciente recibe lo ordenado):")
        print(f"   - Tiempo infundiendo correctamente: {correct_time_order:.3f} s ({pct_order:.2f}%)")
        print(f"B) Según Caudal Real vs Caudal Objetivo (la bomba cumple su objetivo):")
        print(f"   - Tiempo infundiendo correctamente: {correct_time_target:.3f} s ({pct_target:.2f}%)")
        print(f"C) Según Estado de Flujo (flow_state == normal_flow):")
        print(f"   - Tiempo en flujo normal:            {correct_time_state:.3f} s ({pct_state:.2f}%)")
    else:
        print("El tiempo total de simulación es 0 o insuficiente para calcular porcentajes.")
    print("=" * 70)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "resultados.csv"
    main(path)

