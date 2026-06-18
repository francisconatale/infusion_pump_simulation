from enum import Enum
from typing import Tuple, List

class FlowState(Enum):
    NORMAL_FLOW = 1
    MEDIUM_FLOW = 2
    CRITICAL_FLOW = 3

class BagState(Enum):
    NORMAL_BAG = 1
    END_BAG = 2
    EMPTY_BAG = 3

Action = Tuple[str, float]  

class PumpController(AtomicDEVS):
    def __init__(self):
        super().__init__("PumpController")
        self.max_tolerance_exceedance_seconds = 5
        self.margin_tolerance =  0.1
        self.in_medical_order = self.addInPort("in_medical_order")
        self.in_end_bag = self.addInPort("in_end_bag")
        self.in_sensor_flow = self.addInPort("in_sensor_flow")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        self.out_adjust_flow = self.addOutPort("out_adjust_flow")
        self.out_turn_off_bomb = self.addOutPort("out_turn_off_bomb")
        self.out_alarm = self.addOutPort("out_alarm")
        self.out_log = self.addOutPort("out_log")
        self.state = {
            "flow_state": (FlowState.NORMAL_FLOW, 0.0),
            "bag_state": (BagState.NORMAL_BAG, float('inf')),
            "last_sensor_medition": 0.0,
            "medical_order": 0.0,
            "tolerance_exceedance_start_time": 0.0,
            "actions": []  
        }
    
    def add_action(self, action: str, time: float) -> None:
        """Agregar acción (acción, tiempo) a la cola"""
        self.state["actions"].append((action, time))
    
    def get_next_action(self) -> Action:
        """Obtener siguiente acción"""
        action, time = self.state["actions"].pop(0)
        return action, time

    def tolerance_exceeded(self, last_sensor_medition, objetive):
        return (abs(last_sensor_medition - objetive)) / objetive > self.margin_tolerance
    
    def timeAdvance(self):
        if(not self.state["actions"].isEmpty()):
            return get_next_action()[1]
        else if(self.state["actions"].isEmpty() and self.state["bag_state"].awaiting_stop_bag()):
            return self.state["bag_state"].get_time_to_empty()
        else if(self.state["actions"].isEmpty() and not self.state["bag_state"].awaiting_stop_bag()):
            return float('inf')

    def extTransition(self, inputs):
        if(self.state["medical_order"] == 0.0):
            return {}
    
