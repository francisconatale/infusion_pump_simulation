#!/usr/bin/env python3
import csv
import sys

CSV_PATH = "resultados.csv"

def main():
    try:
        with open(CSV_PATH) as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: no se encuentra {CSV_PATH}")
        sys.exit(1)

    if "nurse_response_time" not in rows[0]:
        print("Error: el CSV no tiene las columnas esperadas.")
        print("Ejecuta la simulacion con el logger instrumentado.")
        sys.exit(1)

    bag_end = []
    flow_dev = []

    for row in rows:
        rt = row.get("nurse_response_time", "").strip()
        if not rt:
            continue
        t = float(row["time"])
        val = float(rt)
        alarm = row.get("responds_to_alarm", "")
        if alarm == "low_alarm":
            bag_end.append((t, val))
        elif alarm in ("medium_alarm", "critical_alarm"):
            flow_dev.append((t, val))

    def mostrar(titulo, datos, alarm_label):
        if not datos:
            print(f"\n{titulo}: sin datos")
            return
        print(f"\n{titulo}")
        print("-" * 55)
        print(f"{'Nro':>4s}  {'T evento':>10s}  {'T resp.':>9s}  {'Demora':>8s}")
        print("-" * 55)
        for i, (t, v) in enumerate(datos, 1):
            print(f"{i:>4d}  {t - v:>8.3f}s  {t:>8.3f}s  {v:>7.3f}s")
        vals = [v for _, v in datos]
        print("-" * 55)
        print(f"  Promedio: {sum(vals)/len(vals):.3f}s")
        print(f"  Minimo:   {min(vals):.3f}s")
        print(f"  Maximo:   {max(vals):.3f}s")
        print(f"  Muestras: {len(vals)}")

    mostrar("Tiempo de respuesta ante FIN DE BOLSA (low_alarm)", bag_end, "low_alarm")
    mostrar("Tiempo de respuesta ante DESVIOS DE CAUDAL (medium/critical)", flow_dev, "flow_dev")

    print(f"\nRango teorico (gen_nurse.py): random.uniform(5, 75) segundos")


if __name__ == "__main__":
    main()
