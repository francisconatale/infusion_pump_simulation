#!/usr/bin/env python3
import csv
import sys

CSV_PATH = "resultados.csv"

def main(csv_path):
    try:
        with open(csv_path) as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Error: {csv_path} not found")
        sys.exit(1)

    # Reconstruct response times from raw alarm + confirmation events
    # Each confirmation is matched to the most recent unconfirmed alarm
    pending_alarms = []
    bag_end = []
    medium = []
    critical = []

    for row in rows:
        event_type = row["event_type"]
        t = float(row["time"])

        if event_type == "alarm":
            alarm_type = row.get("alarm_state", "")
            pending_alarms.append((alarm_type, t))

        elif event_type == "nurse_confirmation":
            if pending_alarms:
                alarm_type, alarm_time = pending_alarms.pop()
                rt = t - alarm_time
                if alarm_type == "low_alarm":
                    bag_end.append((alarm_time, rt))
                elif alarm_type == "medium_alarm":
                    medium.append((alarm_time, rt))
                elif alarm_type == "critical_alarm":
                    critical.append((alarm_time, rt))

    def display_stats(title, data, alarm_label):
        if not data:
            print(f"\n{title}: no data")
            return
        print(f"\n{title}")
        print("-" * 55)
        print(f"{'No.':>4s}  {'Alarm T':>10s}  {'Resp. T':>9s}  {'Delay':>8s}")
        print("-" * 55)
        for i, (alarm_t, rt) in enumerate(data, 1):
            print(f"{i:>4d}  {alarm_t:>8.3f}s  {alarm_t + rt:>8.3f}s  {rt:>7.3f}s")
        vals = [rt for _, rt in data]
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
    path = sys.argv[1] if len(sys.argv) > 1 else "resultados.csv"
    main(path)
