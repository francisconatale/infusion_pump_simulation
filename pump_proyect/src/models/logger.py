import csv
from pypdevs.DEVS import AtomicDEVS
from math import inf as infinity
from src.models.controller_pump import PumpOutput
from src.models.alarm_module import AlarmStatus

def _serialize_action_item(item):
    if isinstance(item, tuple):
        if len(item) == 2 and isinstance(item[0], PumpOutput):
            act, val = item
            name = act.value
            if act == PumpOutput.ADJUST_FLOW:
                return f"{name}(delta={val:.3f})" if isinstance(val, (int, float)) else name
            elif act == PumpOutput.RECORD_EVENT:
                return name
            else:
                return name
        elif len(item) == 2:
            inner, delay = item
            inner_str = _serialize_action_item(inner)
            return inner_str
        else:
            return str(item)
    elif isinstance(item, PumpOutput):
        return item.value
    return str(item)

def _serialize_actions(actions):
    if not actions:
        return ""
    return "; ".join(_serialize_action_item(a) for a in actions)

class Logger(AtomicDEVS):
    HEADER = [
        "time", "event_type",
        "flow_state", "tolerance_count",
        "bag_state", "bag_time_remaining",
        "actual_flow", "target_flow",
        "medical_order", "actions_count", "actions",
        "alarm_state"
    ]

    def __init__(self, initial_accumulated_time=0.0, log_filename="resultados.csv", initial_last_data=None):
        super().__init__("Logger")
        self.in_state_control = self.addInPort("in_state_control")
        self.in_alarm_module = self.addInPort("in_alarm_module")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")

        self.log_file = open(log_filename, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.log_file)
        self.writer.writerow(self.HEADER)
        self.log_file.flush()

        if initial_last_data is None:
            self.last_data = {
                "flow_state": "NORMAL_FLOW", "tolerance_count": 0,
                "bag_state": "NORMAL_BAG", "bag_time": infinity,
                "actual_flow": 0.0, "target_flow": 0.0,
                "medical_order": 0, "actions_count": 0, "actions": "",
                "alarm_state": "no_alarm"
            }
        else:
            self.last_data = initial_last_data.copy()

        self.state = {
            "accumulated_time": initial_accumulated_time
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
            self.last_data["actions_count"],
            self.last_data["actions"],
            self.last_data["alarm_state"],
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
        raw_actions = data.get("actions", [])
        self.last_data["actions_count"] = len(raw_actions)
        self.last_data["actions"] = _serialize_actions(raw_actions)

    def extTransition(self, inputs) -> dict:
        e = self.elapsed
        self.state["accumulated_time"] += e

        if self.in_state_control in inputs:
            msg = inputs[self.in_state_control]
            data = msg[0] if isinstance(msg, list) and msg else msg
            self._apply_controller_state(data)
            self._write_row("control", self.last_data["actual_flow"])

        if self.in_alarm_module in inputs:
            alarm_msg = inputs[self.in_alarm_module][0]
            if hasattr(alarm_msg, "value"):
                alarm_type = alarm_msg.value
            else:
                alarm_type = str(alarm_msg)
            self.last_data["alarm_state"] = alarm_type
            self._write_row("alarm", self.last_data["actual_flow"])

        if self.in_nurse_confirmation in inputs:
            self._write_row("nurse_confirmation", self.last_data["actual_flow"])

        return self.state

    def intTransition(self) -> dict:
        return self.state

    def timeAdvance(self) -> float:
        return infinity

    def __del__(self):
        if hasattr(self, "log_file") and self.log_file:
            self.log_file.close()

    
    
