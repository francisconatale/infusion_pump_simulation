import copy
import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, List, Tuple
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


@dataclass
class PumpState:
    flow_state: Tuple[FlowState, int]
    bag_state: Tuple[BagState, float]
    last_sensor_medition: float
    medical_order: float
    tolerance_exceedance_start_time: float
    actions: List[Any] = field(default_factory=list)

    def copy(self) -> 'PumpState':
        return copy.deepcopy(self)

    def update_bag_time(self, elapsed: float):
        mode, time = self.bag_state
        if time != float('inf'):
            self.bag_state = (mode, max(0.0, time - elapsed))

    def transition_to_bag_state(self, mode: BagState, time: float = float('inf')):
        self.bag_state = (mode, time)

    def transition_to_flow_state(self, mode: FlowState, consecutive_errors: int = 0):
        self.flow_state = (mode, consecutive_errors)

    def increment_flow_errors(self):
        self.flow_state = (self.flow_state[0], self.flow_state[1] + 1)


def conLog(state: PumpState, actions: list) -> list:
    """
    Helper function corresponding to conLog(s, actions) from the LaTeX spec.
    Appends a registrarEvento action with the snapshot of the state before the transition
    immediately after each action in the queue.
    """
    state_copy = state.copy()
    state_copy.actions = list(actions)
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


# Mapping for flow alarm escalation when consecutive errors >= 5
ESCALATION_MAP = {
    FlowState.MEDIUM_FLOW: (
        [(PumpOutput.CRITICAL_ALARM, 0.0), (PumpOutput.STOP_PUMP, 0.0)],
        FlowState.CRITICAL_FLOW
    ),
    FlowState.NORMAL_FLOW: (
        [(PumpOutput.MEDIUM_ALARM, 0.0)],
        FlowState.MEDIUM_FLOW
    ),
    FlowState.CRITICAL_FLOW: (
        [(PumpOutput.CRITICAL_ALARM, 0.0)],
        FlowState.CRITICAL_FLOW
    )
}


class PumpController(AtomicDEVS):
    def __init__(self,
                 initial_flow_state=(FlowState.NORMAL_FLOW, 0.0),
                 initial_bag_state=(BagState.NORMAL_BAG, float('inf')),
                 initial_last_sensor_medition=0.0,
                 initial_medical_order=0.0,
                 initial_tolerance_exceedance_start_time=0.0,
                 initial_actions=None):
        super().__init__("PumpController")
        
        # Ports
        self.in_medical_order = self.addInPort("in_medical_order")
        self.in_end_bag = self.addInPort("in_end_bag")
        self.in_sensor_flow = self.addInPort("in_sensor_flow")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        
        self.out_flow = self.addOutPort("out_adjust_flow")
        self.out_alarm = self.addOutPort("out_alarm")
        self.out_log = self.addOutPort("out_log")
        
        self.state = PumpState(
            flow_state=initial_flow_state,
            bag_state=initial_bag_state,
            last_sensor_medition=initial_last_sensor_medition,
            medical_order=initial_medical_order,
            tolerance_exceedance_start_time=initial_tolerance_exceedance_start_time,
            actions=initial_actions if initial_actions is not None else []
        )

    def tolerance_exceeded(self, last_sensor_medition: float, objective: float) -> bool:
        return no_tolerable(objective, last_sensor_medition)

    def timeAdvance(self) -> float:
        if self.state.actions:
            return self.state.actions[0][1]
        elif self.state.bag_state[0] == BagState.AWAIT_STOP_BAG:
            return self.state.bag_state[1]
        else:
            return float('inf')

    def _apply_medical_order(self, state: PumpState, state_before: PumpState, c: float):
        state.medical_order = c
        if c > 0:
            delay = random.uniform(0.0, 3.0)
            state.actions = conLog(
                state_before,
                [((PumpOutput.ADJUST_FLOW, c - state.last_sensor_medition), delay)]
            )
        else:
            state.actions = conLog(
                state_before,
                [(PumpOutput.STOP_PUMP, 0.0)]
            )

    def _adjust_flow_preventive(self, state: PumpState, x: float):
        if not state.actions:
            adjust = ((PumpOutput.ADJUST_FLOW, state.medical_order - x), 0.0)
            state.actions = [adjust]
            snapshot = state.copy()
            state.actions.append(((PumpOutput.RECORD_EVENT, snapshot), 0.0))

    def extTransition(self, inputs) -> PumpState:
        state = self.state.copy()
        e = self.elapsed
        state_before = self.state.copy()
       
        if state.bag_state[0] == BagState.EMPTY_BAG:
            if self.in_medical_order in inputs:
                _, c = inputs[self.in_medical_order][0]
                if c > 0:
                    state.transition_to_bag_state(BagState.NORMAL_BAG)
                    state.transition_to_flow_state(FlowState.NORMAL_FLOW)
                self._apply_medical_order(state, state_before, c)
            return state
            
        # common time decrement for tau_bolsa
        state.update_bag_time(e)
        
        # 1. medical order (port 0)
        if self.in_medical_order in inputs:
            _, c = inputs[self.in_medical_order][0]
            if state.flow_state[0] != FlowState.CRITICAL_FLOW:
                self._apply_medical_order(state, state_before, c)
            else:
                state.medical_order = c
            
        # 2. sensor flow (port 1)
        elif self.in_sensor_flow in inputs:
            x = inputs[self.in_sensor_flow][0]
            
            # Check alarm escalation if consecutive errors >= 5
            if state.flow_state[1] >= 5:
                escalated_actions, next_flow_state = ESCALATION_MAP[state.flow_state[0]]
                state.actions = conLog(state_before, escalated_actions)
                state.transition_to_flow_state(next_flow_state)
            
            state.last_sensor_medition = x
            
            # Verify flow tolerance and adjust if not critical
            if state.flow_state[0] != FlowState.CRITICAL_FLOW:
                if self.tolerance_exceeded(x, state.medical_order) and state.flow_state[1] < 5:
                    state.increment_flow_errors()
                else:
                    state.transition_to_flow_state(state.flow_state[0], 0)
                
                self._adjust_flow_preventive(state, x)
                
        # 3. end of bag signal (port 2)
        elif self.in_end_bag in inputs:
            if state.bag_state[0] == BagState.NORMAL_BAG:
                state.actions = conLog(
                    state_before,
                    [(PumpOutput.LOW_ALARM, 0.0)]
                )
                state.transition_to_bag_state(BagState.END_BAG, state.bag_state[1])
            elif state.bag_state[0] in (BagState.END_BAG, BagState.AWAIT_STOP_BAG, BagState.EMPTY_BAG):
                if state.actions:
                    state.actions[0] = (state.actions[0][0], max(0.0, state.actions[0][1] - e))
                
        elif self.in_nurse_confirmation in inputs:
            # en caso de que el enfermero confirme, se retoma normalmente el flujo de la bolsa
            if state.bag_state[0] in (BagState.END_BAG, BagState.AWAIT_STOP_BAG, BagState.EMPTY_BAG):
                state.transition_to_bag_state(BagState.NORMAL_BAG)
            state.actions = conLog(
                state_before,
                [((PumpOutput.ADJUST_FLOW, state.medical_order - state.last_sensor_medition), 0.0)]
            )
            state.transition_to_flow_state(FlowState.NORMAL_FLOW)
            
        return state

    def intTransition(self) -> PumpState:
        state = self.state.copy()
        
        if state.actions:
            action, delay = state.actions.pop(0)
            
            if state.bag_state[0] == BagState.END_BAG and action == PumpOutput.LOW_ALARM:
                state.transition_to_bag_state(BagState.AWAIT_STOP_BAG, 60.0)
                
            elif state.bag_state[0] == BagState.EMPTY_BAG and action == PumpOutput.STOP_PUMP:
                state.transition_to_bag_state(state.bag_state[0], float('inf'))
                
        else:
            if state.bag_state[0] == BagState.AWAIT_STOP_BAG:
                state_snapshot = state.copy()
                state.transition_to_bag_state(BagState.EMPTY_BAG, 0.0)
                state.actions = conLog(
                    state_snapshot,
                    [(PumpOutput.STOP_PUMP, 0.0)]
                )
                
        return state

    def outputFnc(self) -> dict:
        actions = self.state.actions
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
