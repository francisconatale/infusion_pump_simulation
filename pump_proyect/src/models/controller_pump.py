import copy
import random
from enum import Enum
from src.models.alarm_module import AlarmStatus
from pypdevs.DEVS import AtomicDEVS

class FlowState(Enum):
    NORMAL_FLOW = "normal_flow"
    MEDIUM_FLOW = "medium_flow"
    CRITICAL_FLOW = "critical_flow"

class BagState(Enum):
    NORMAL_BAG = "normal_bag"
    END_BAG = "end_bag"
    EMPTY_BAG = "empty_bag"
    AWAIT_STOP_BAG = "await_stop_bag"

class PumpOutput(Enum):
    ADJUST_FLOW = "adjust_flow"
    STOP_PUMP = "stop_pump"
    LOW_ALARM = "low_alarm"
    MEDIUM_ALARM = "medium_alarm"
    CRITICAL_ALARM = "critical_alarm"
    RECORD_EVENT = "record_event"

    def get_status(self) -> AlarmStatus:
        if self == PumpOutput.LOW_ALARM:
            return AlarmStatus.LOW_ALARM
        elif self == PumpOutput.MEDIUM_ALARM:
            return AlarmStatus.MEDIUM_ALARM
        elif self == PumpOutput.CRITICAL_ALARM:
            return AlarmStatus.CRITICAL_ALARM
        return AlarmStatus.NO_ALARM


def conLog(state: dict, actions: list) -> list:
    """
    Helper function corresponding to conLog(s, actions) from the LaTeX spec.
    Appends a registrarEvento action with the snapshot of the state before the transition
    immediately after each action in the queue.
    """
    state_copy = copy.deepcopy(state)
    result = []
    for act, delay in actions:
        result.append((act, delay))
        result.append(((PumpOutput.RECORD_EVENT, state_copy), 0.0))
    return result

def no_tolerable(cO: float, uCM: float) -> bool:
    """
    Helper function to check if the difference between objective flow and measured flow exceeds 10%.
    """
    if cO == 0.0:
        return False
    return (abs(cO - uCM)) / cO > 0.10

class PumpController(AtomicDEVS):
    def __init__(self):
        super().__init__("PumpController")
        
        # Ports
        self.in_medical_order = self.addInPort("in_medical_order")
        self.in_end_bag = self.addInPort("in_end_bag")
        self.in_sensor_flow = self.addInPort("in_sensor_flow")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        
        self.out_flow = self.addOutPort("out_adjust_flow")
        self.out_alarm = self.addOutPort("out_alarm")
        self.out_log = self.addOutPort("out_log")
        
        self.state = {
            "flow_state": (FlowState.NORMAL_FLOW, 0.0),       # (Enum, tol)
            "bag_state": (BagState.NORMAL_BAG, float('inf')), # (Enum, tau_bolsa)
            "last_sensor_medition": 0.0,                      # uCM
            "medical_order": 0.0,                             # cO
            "tolerance_exceedance_start_time": 0.0,           
            "actions": []                                     
        }

    def tolerance_exceeded(self, last_sensor_medition: float, objective: float) -> bool:
        return no_tolerable(objective, last_sensor_medition)

    def timeAdvance(self) -> float:
        if self.state["actions"]:
            return self.state["actions"][0][1]
        elif self.state["bag_state"][0] == BagState.AWAIT_STOP_BAG:
            return self.state["bag_state"][1]
        else:
            return float('inf')

    def extTransition(self, inputs) -> dict:
        state = copy.deepcopy(self.state)
        e = self.elapsed
        state_before = copy.deepcopy(self.state) 
       
        if state["bag_state"][0] == BagState.EMPTY_BAG:
            return state
            
        # common time decrement for tau_bolsa
        state["bag_state"] = (
            state["bag_state"][0],
            max(0.0, state["bag_state"][1] - e) if state["bag_state"][1] != float('inf') else float('inf')
        )
        
        # 1. medical order (port 0)
        if self.in_medical_order in inputs:
            _, c = inputs[self.in_medical_order][0]
            
            if c > 0:
                delay = random.uniform(0.0, 3.0)
                state["actions"] = conLog(
                    state_before,
                    [((PumpOutput.ADJUST_FLOW, c - state["last_sensor_medition"]), delay)]
                )
            else:
                state["actions"] = conLog(
                    state_before,
                    [(PumpOutput.STOP_PUMP, 0.0)]
                )
            state["medical_order"] = c
            
        # 2. sensor flow (port 1)
        elif self.in_sensor_flow in inputs:
            x = inputs[self.in_sensor_flow][0]
            
            if state["flow_state"][1] >= 5 and state["flow_state"][0] == FlowState.MEDIUM_FLOW:
                state["actions"] = conLog(
                    state_before,
                    [(PumpOutput.CRITICAL_ALARM, 0.0), (PumpOutput.STOP_PUMP, 0.0)]
                )
                state["last_sensor_medition"] = x
                state["flow_state"] = (FlowState.CRITICAL_FLOW, 0)
            elif state["flow_state"][1] >= 5 and state["flow_state"][0] == FlowState.NORMAL_FLOW:
                state["actions"] = conLog(
                    state_before,
                    [(PumpOutput.MEDIUM_ALARM, 0.0)]
                )
                state["last_sensor_medition"] = x
                state["flow_state"] = (FlowState.MEDIUM_FLOW, 0)
            elif state["flow_state"][1] >= 5 and state["flow_state"][0] == FlowState.CRITICAL_FLOW:
                state["actions"] = conLog(
                    state_before,
                    [(PumpOutput.CRITICAL_ALARM, 0.0)]
                )
                state["last_sensor_medition"] = x
                state["flow_state"] = (FlowState.CRITICAL_FLOW, 0)
            elif self.tolerance_exceeded(x, state["medical_order"]) and state["flow_state"][1] < 5:
                state["last_sensor_medition"] = x
                state["flow_state"] = (state["flow_state"][0], state["flow_state"][1] + 1)
                if not state["actions"]:
                    state["actions"] = [((PumpOutput.RECORD_EVENT, copy.deepcopy(state)), 0.0)]
            else:
                state["last_sensor_medition"] = x
                state["flow_state"] = (state["flow_state"][0], 0)
                if not state["actions"]:
                    state["actions"] = [((PumpOutput.RECORD_EVENT, copy.deepcopy(state)), 0.0)]
                
        # 3. end of bag signal (port 2)
        elif self.in_end_bag in inputs:
            if state["bag_state"][0] == BagState.NORMAL_BAG:
                state["actions"] = conLog(
                    state_before,
                    [(PumpOutput.LOW_ALARM, 0.0)]
                )
                state["bag_state"] = (BagState.END_BAG, state["bag_state"][1])
            elif state["bag_state"][0] in (BagState.END_BAG, BagState.AWAIT_STOP_BAG, BagState.EMPTY_BAG):
                if state["actions"]:
                    state["actions"] = list(state["actions"])
                    state["actions"][0] = (state["actions"][0][0], max(0.0, state["actions"][0][1] - e))
                
        # 4. nurse confirmation (port 3)
        elif self.in_nurse_confirmation in inputs:
            state["actions"] = conLog(
                state_before,
                [((PumpOutput.ADJUST_FLOW, state["medical_order"] - state["last_sensor_medition"]), 0.0)]
            )
            state["flow_state"] = (FlowState.NORMAL_FLOW, 0)
            
        return state

    def intTransition(self) -> dict:
        state = copy.deepcopy(self.state)
        
        if state["actions"]:
            state["actions"] = list(state["actions"])
            action, delay = state["actions"].pop(0)
            
            if state["bag_state"][0] == BagState.END_BAG and action == PumpOutput.LOW_ALARM:
                state["bag_state"] = (BagState.AWAIT_STOP_BAG, 60.0)
                
            elif state["bag_state"][0] == BagState.EMPTY_BAG and action == PumpOutput.STOP_PUMP:
                state["bag_state"] = (state["bag_state"][0], float('inf'))
                
        else:
            if state["bag_state"][0] == BagState.AWAIT_STOP_BAG:
                state_snapshot = copy.deepcopy(state)
                state["bag_state"] = (BagState.EMPTY_BAG, 0.0)
                state["actions"] = conLog(
                    state_snapshot,
                    [(PumpOutput.STOP_PUMP, 0.0)]
                )
                
        return state

    def outputFnc(self) -> dict:
        actions = self.state["actions"]
        if actions:
            action, delay = actions[0]
            if isinstance(action, tuple) and action[0] == PumpOutput.ADJUST_FLOW:
                return {self.out_flow: [("AdjustFlow", action[1])]}
            elif action == PumpOutput.STOP_PUMP:
                return {self.out_flow: [("OffBomb", 0)]}
            elif action in (PumpOutput.LOW_ALARM, PumpOutput.MEDIUM_ALARM, PumpOutput.CRITICAL_ALARM):
                return {self.out_alarm: [action]}
            elif isinstance(action, tuple) and action[0] == PumpOutput.RECORD_EVENT:
                return {self.out_log: [action[1]]}
        return {}
