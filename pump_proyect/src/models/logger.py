import csv
from pypdevs.DEVS import AtomicDEVS
from math import inf as infinity

class Logger(AtomicDEVS):
    HEADER = [
        "time", "event_type",
        "flow_state", "tolerance_count",
        "bag_state", "bag_time_remaining",
        "actual_flow", "target_flow",
        "medical_order", "actions_count"
    ]

    def __init__(self):
        super().__init__("Logger")
        self.in_state_control = self.addInPort("in_state_control")

        self.log_file = open("resultados.csv", "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.log_file)
        self.writer.writerow(self.HEADER)
        self.log_file.flush()

        self.last_data = {
            "flow_state": "NORMAL_FLOW", "tolerance_count": 0,
            "bag_state": "NORMAL_BAG", "bag_time": infinity,
            "actual_flow": 0.0, "target_flow": 0.0,
            "medical_order": 0, "actions_count": 0
        }

        self.state = {
            "accumulated_time": 0.0
        }

    def _write_row(self, event_type, actual_flow):
        actual_flow = actual_flow if actual_flow is not None else self.last_data["actual_flow"]

        self.writer.writerow([
            f"{self.state['accumulated_time']:.3f}",
            event_type,
            self.last_data["flow_state"],
            self.last_data["tolerance_count"],
            self.last_data["bag_state"],
            f"{self.last_data['bag_time']:.3f}" if isinstance(self.last_data["bag_time"], float) and self.last_data["bag_time"] != infinity else "inf",
            f"{actual_flow:.3f}",
            f"{self.last_data['target_flow']:.3f}",
            self.last_data["medical_order"],
            self.last_data["actions_count"]
        ])
        self.log_file.flush()

    def _apply_controller_state(self, data):
        self.last_data["flow_state"] = data.get("flow_state", ("NORMAL_FLOW", 0))[0].value if hasattr(data.get("flow_state", ("NORMAL_FLOW", 0))[0], "value") else str(data.get("flow_state", ("NORMAL_FLOW", 0))[0])
        self.last_data["tolerance_count"] = data.get("flow_state", ("NORMAL_FLOW", 0))[1]
        self.last_data["bag_state"] = data.get("bag_state", ("NORMAL_BAG", infinity))[0].value if hasattr(data.get("bag_state", ("NORMAL_BAG", infinity))[0], "value") else str(data.get("bag_state", ("NORMAL_BAG", infinity))[0])
        self.last_data["bag_time"] = data.get("bag_state", ("NORMAL_BAG", infinity))[1]
        self.last_data["actual_flow"] = data.get("last_sensor_medition", self.last_data["actual_flow"])
        self.last_data["target_flow"] = data.get("medical_order", self.last_data["target_flow"])
        self.last_data["medical_order"] = data.get("medical_order", self.last_data["medical_order"])
        self.last_data["actions_count"] = len(data.get("actions", []))

    def extTransition(self, inputs) -> dict:
        e = self.elapsed
        self.state["accumulated_time"] += e

        if self.in_state_control in inputs:
            msg = inputs[self.in_state_control]
            data = msg[0] if isinstance(msg, list) and msg else msg
            self._apply_controller_state(data)
            self._write_row("control", self.last_data["actual_flow"])

        return self.state

    def intTransition(self) -> dict:
        return self.state

    def timeAdvance(self) -> float:
        return infinity

    def __del__(self):
        if hasattr(self, "log_file") and self.log_file:
            self.log_file.close()

    
    
