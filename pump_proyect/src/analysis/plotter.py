import csv
import matplotlib.pyplot as plt

CSV_PATH = "resultados.csv"


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
def plot_flow(data):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["actual_flow"], label="Actual Flow")
    plt.plot(data["time"], data["target_flow"], label="Target Flow")
    plt.plot(data["time"], data["medical_order"], label="Medical Order", linestyle="--")

    plt.xlabel("Time (s)")
    plt.ylabel("Flow (ml/h)")
    plt.title("Flow: actual vs target vs medical order")
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


def plot_flow_state(data):
    plt.figure(figsize=(16, 5))

    y = encode_flow_state(data["flow_state"])

    plt.step(data["time"], y, where="post")

    plt.yticks([0, 1, 2], ["normal", "medium", "critical"])
    plt.xlabel("Time (s)")
    plt.ylabel("Flow state")
    plt.title("Flow state evolution")
    plt.grid()



# Tolerance counter
def plot_tolerance(data):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["tolerance_count"])

    plt.xlabel("Time (s)")
    plt.ylabel("Tolerance count")
    plt.title("Tolerance counter evolution")
    plt.grid()


# Bag state
def encode_bag_state(states):
    mapping = {
        "normal_bag": 0,
        "end_bag": 1,
        "await_stop_bag": 2,
        "empty_bag": 3
    }
    return [mapping.get(s, -1) for s in states]


def plot_bag_state(data):
    plt.figure(figsize=(16, 5))

    y = encode_bag_state(data["bag_state"])

    plt.step(data["time"], y, where="post")

    plt.yticks([0, 1, 2, 3], ["normal", "low", "waiting stop", "empty"])
    plt.xlabel("Time (s)")
    plt.ylabel("Bag state")
    plt.title("Bag state evolution")
    plt.grid()



# Actions counter

def plot_actions(data):
    plt.figure(figsize=(16, 5))

    plt.plot(data["time"], data["actions_count"])

    plt.xlabel("Time (s)")
    plt.ylabel("Actions count")
    plt.title("Cumulative actions triggered")
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

def plot_alarm_timeline(data):

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
    plt.title("Alarm Evolution and Nurse Confirmations")

    plt.grid()


import glob
import os
import subprocess

# main for every plot
def main():
    csv_files = glob.glob("resultados/*/resultados.csv")
    
    if not csv_files:
        print("No se encontraron carpetas de escenarios con resultados.csv.")
        return

    for csv_file in csv_files:
        # csv_file es del formato "resultados/nombre_escenario/resultados.csv"
        # El output dir es simplemente el directorio donde esta el csv
        output_dir = os.path.dirname(csv_file)
        scenario_name = os.path.basename(output_dir)
        
        data = read_csv(csv_file)

        plot_flow(data)
        plt.savefig(f"{output_dir}/flujo.png")
        plt.close()
        
        plot_flow_state(data)
        plt.savefig(f"{output_dir}/estado_de_flujo.png")
        plt.close()
        
        plot_tolerance(data)
        plt.savefig(f"{output_dir}/tolerancia.png")
        plt.close()
        
        plot_bag_state(data)
        plt.savefig(f"{output_dir}/fin_de_bolsa.png")
        plt.close()
        
        plot_actions(data)
        plt.savefig(f"{output_dir}/acciones.png")
        plt.close()
        
        plot_alarm_timeline(data)
        plt.savefig(f"{output_dir}/alarmas.png")
        plt.close()

        print(f"Graficos generados para el escenario '{scenario_name}' en: {output_dir}")

        print(f"Corriendo validadores para '{scenario_name}'...")
        
        with open(f"{output_dir}/verify_properties_output.txt", "w") as f:
            subprocess.run(["python", "validators/verify_properties.py", csv_file], stdout=f, stderr=subprocess.STDOUT)
            
        with open(f"{output_dir}/analyze_nurse_confirmation_output.txt", "w") as f:
            subprocess.run(["python", "validators/analyze_nurse_confirmation.py", csv_file], stdout=f, stderr=subprocess.STDOUT)

    

if __name__ == "__main__":
    main()