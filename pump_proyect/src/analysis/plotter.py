import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt

def read_csv(path):
    data = {
        "time": [],
        "actual_flow": [],
        "target_flow": [],
        "medical_order": [],
        "flow_state": [],
        "bag_state": [],
        "tolerance_count": [],
        "actions_count": [],
        "alarm_state": [],
        "event_type": []
    }

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data["time"].append(float(row["time"]))
            data["actual_flow"].append(float(row["actual_flow"]))
            data["target_flow"].append(float(row["target_flow"]))
            data["medical_order"].append(float(row["medical_order"]))
            data["flow_state"].append(row["flow_state"])
            data["bag_state"].append(row["bag_state"])
            data["tolerance_count"].append(float(row["tolerance_count"]))
            data["actions_count"].append(int(row["actions_count"]))
            data["alarm_state"].append(row["alarm_state"])
            data["event_type"].append(row["event_type"])

    return data



# Real flow vs objective flow vs medical order
def plot_flow(data, scenario):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["actual_flow"], label="Actual Flow")
    plt.plot(data["time"], data["target_flow"], label="Target Flow")
    plt.plot(data["time"], data["medical_order"], label="Medical Order", linestyle="--")

    plt.xlabel("Time (s)")
    plt.ylabel("Flow (ml/h)")
    plt.title(f"{scenario} - Flow: actual vs target vs medical order")
    plt.legend()
    plt.grid()


#  Flow state (step plot)
def encode_flow_state(states):
    mapping = {
        "normal_flow": 0,
        "medium_flow": 1,
        "critical_flow": 2
    }
    return [mapping.get(s, -1) for s in states]


def plot_flow_state(data, scenario):
    plt.figure(figsize=(16, 5))

    y = encode_flow_state(data["flow_state"])

    plt.step(data["time"], y, where="post")

    plt.yticks([0, 1, 2], ["normal", "medium", "critical"])
    plt.xlabel("Time (s)")
    plt.ylabel("Flow state")
    plt.title(f"{scenario} - Flow state evolution")
    plt.grid()



# Tolerance counter
def plot_tolerance(data, scenario):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["tolerance_count"])

    plt.xlabel("Time (s)")
    plt.ylabel("Tolerance count")
    plt.title(f"{scenario} - Tolerance counter evolution")
    plt.grid()


# Bag state
def encode_bag_state(states):
    mapping = {
        "normal_bag": 0,
        "bag_low": 1,
        "waiting_stop": 2,
        "empty": 3
    }
    return [mapping.get(s, -1) for s in states]


def plot_bag_state(data, scenario):
    plt.figure(figsize=(16, 5))

    y = encode_bag_state(data["bag_state"])

    plt.step(data["time"], y, where="post")

    plt.yticks([0, 1, 2, 3], ["normal", "low", "waiting stop", "empty"])
    plt.xlabel("Time (s)")
    plt.ylabel("Bag state")
    plt.title(f"{scenario} - Bag state evolution")
    plt.grid()



# Actions counter

def plot_actions(data, scenario):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["actions_count"])

    plt.xlabel("Time (s)")
    plt.ylabel("Actions count")
    plt.title(f"{scenario} - Cumulative actions triggered")
    plt.grid()

def encode_alarm_state(states):
    mapping = {
        "no_alarm": 0,
        "low_alarm": 1,
        "medium_alarm": 2,
        "critical_alarm": 3,
        "long_wait": 4,
        "short_wait": 5,
        "repeat_critical": 6
    }

    return [mapping.get(s, -1) for s in states]


## Alarm states

def plot_alarm_timeline(data, scenario):

    plt.figure(figsize=(18, 5))

    y = encode_alarm_state(data["alarm_state"])

    plt.step(
        data["time"],
        y,
        where="post",
        linewidth=2,
        label="Alarm State"
    )

    for t, event in zip(
        data["time"],
        data["event_type"]
    ):
        if event == "nurse_confirmation":
            plt.axvline(
                x=t,
                linestyle="--",
                linewidth=2,
                label="Nurse Confirmation"
            )

    plt.yticks(
        [0,1,2,3,4,5,6],
        [
            "No Alarm",
            "Low",
            "Medium",
            "Critical",
            "Wait 30s",
            "Wait 10s",
            "Repeat"
        ]
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Alarm Module State")
    plt.title(f"{scenario} - Alarm Evolution and Nurse Confirmations")

    plt.grid()

# generation of every plot for a csv
def generate_plots(csv_file):

    scenario = Path(csv_file).stem

    output_dir = Path("docs") / "plots" / scenario
    output_dir.mkdir(parents=True, exist_ok=True)

    data = read_csv(csv_file)

    plot_flow(data, scenario)
    plt.savefig(output_dir / "flujo.png")
    plt.close()

    plot_flow_state(data, scenario)
    plt.savefig(output_dir / "estado_de_flujo.png")
    plt.close()

    plot_tolerance(data, scenario)
    plt.savefig(output_dir / "tolerancia.png")
    plt.close()

    plot_bag_state(data, scenario)
    plt.savefig(output_dir / "fin_de_bolsa.png")
    plt.close()

    plot_actions(data, scenario)
    plt.savefig(output_dir / "acciones.png")
    plt.close()

    plot_alarm_timeline(data, scenario)
    plt.savefig(output_dir / "alarmas.png")
    plt.close()

    print(f"Plots generated for {scenario}")

# generation of ALL plots 
def main():

    docs_dir = Path("docs")

    csv_files = sorted(
        docs_dir.glob("*.csv")
    )

    if not csv_files:
        print("No CSV files found in docs/")
        return

    for csv_file in csv_files:
        print(f"Processing {csv_file}")
        generate_plots(csv_file)
    

if __name__ == "__main__":
    main()