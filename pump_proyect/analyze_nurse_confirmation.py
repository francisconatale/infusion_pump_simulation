#!/usr/bin/env python3
import csv
import sys

CSV_PATH = "resultados.csv"

def main():
    try:
        with open(CSV_PATH) as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: {CSV_PATH} not found")
        sys.exit(1)

    if "nurse_response_time" not in rows[0]:
        print("Error: CSV does not have the expected columns.")
        print("Run the simulation with the instrumented logger.")
        sys.exit(1)

    bag_end = []
    medium = []
    critical = []

    for row in rows:
        rt = row.get("nurse_response_time", "").strip()
        if not rt:
            continue
        t = float(row["time"])
        val = float(rt)
        alarm = row.get("responds_to_alarm", "")
        if alarm == "low_alarm":
            bag_end.append((t, val))
        elif alarm == "medium_alarm":
            medium.append((t, val))
        elif alarm == "critical_alarm":
            critical.append((t, val))

    def display_stats(title, data, alarm_label):
        if not data:
            print(f"\n{title}: no data")
            return
        print(f"\n{title}")
        print("-" * 55)
        print(f"{'No.':>4s}  {'Event T':>10s}  {'Resp. T':>9s}  {'Delay':>8s}")
        print("-" * 55)
        for i, (t, v) in enumerate(data, 1):
            print(f"{i:>4d}  {t - v:>8.3f}s  {t:>8.3f}s  {v:>7.3f}s")
        vals = [v for _, v in data]
        print("-" * 55)
        print(f"  Average: {sum(vals)/len(vals):.3f}s")
        print(f"  Minimum:   {min(vals):.3f}s")
        print(f"  Maximum:   {max(vals):.3f}s")
        print(f"  Samples: {len(vals)}")

    display_stats("Response time for BAG END (low_alarm)", bag_end, "low_alarm")
    display_stats("Response time for MEDIUM ALARM (medium_alarm)", medium, "medium_alarm")
    display_stats("Response time for CRITICAL ALARM (critical_alarm)", critical, "critical_alarm")

    print(f"\nTheoretical range (gen_nurse.py): random.uniform(5, 75) seconds")


if __name__ == "__main__":
    main()
