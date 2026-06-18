import copy
import random
from enum import Enum
from pypdevs.DEVS import AtomicDEVS

# Enums retained and respected
class FlowState(Enum):
    NORMAL_FLOW = 1
    MEDIUM_FLOW = 2
    CRITICAL_FLOW = 3

class BagState(Enum):
    NORMAL_BAG = 1
    END_BAG = 2
    EMPTY_BAG = 3
    AWAIT_STOP_BAG = 4

def conLog(state, actions):
    """
    Helper function corresponding to conLog(s, actions) from the LaTeX spec.
    Appends a registrarEvento action with the snapshot of the state before the transition
    immediately after each action in the queue.
    """
    state_copy = copy.deepcopy(state)
    result = []
    for act, delay in actions:
        result.append((act, delay))
        result.append((("registrarEvento", state_copy), 0.0))
    return result

def no_tolerable(cO, uCM):
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
        
        self.out_adjust_flow = self.addOutPort("out_adjust_flow")
        self.out_turn_off_bomb = self.addOutPort("out_turn_off_bomb")
        self.out_alarm = self.addOutPort("out_alarm")
        self.out_log = self.addOutPort("out_log")
        
        self.state = {
            "flow_state": (FlowState.NORMAL_FLOW, 0.0),       # (Enum, tol)
            "bag_state": (BagState.NORMAL_BAG, float('inf')), # (Enum, tau_bolsa)
            "last_sensor_medition": 0.0,                      # uCM
            "medical_order": 0.0,                             # cO
            "tolerance_exceedance_start_time": 0.0,           # untouched helper variable
            "actions": []                                     # queue of pending actions [(action, delay)]
        }

    def get_vars(self):
        uCM = self.state["last_sensor_medition"]
        cO = self.state["medical_order"]
        est_flujo, tol = self.state["flow_state"]
        est_bolsa, tau_bolsa = self.state["bag_state"]
        actions = self.state["actions"]
        return uCM, cO, tol, est_flujo, est_bolsa, tau_bolsa, actions

    def set_vars(self, uCM=None, cO=None, tol=None, est_flujo=None, est_bolsa=None, tau_bolsa=None, actions=None):
        if uCM is not None:
            self.state["last_sensor_medition"] = uCM
        if cO is not None:
            self.state["medical_order"] = cO
            
        current_est_flujo, current_tol = self.state["flow_state"]
        new_est_flujo = est_flujo if est_flujo is not None else current_est_flujo
        new_tol = tol if tol is not None else current_tol
        self.state["flow_state"] = (new_est_flujo, new_tol)
        
        current_est_bolsa, current_tau_bolsa = self.state["bag_state"]
        new_est_bolsa = est_bolsa if est_bolsa is not None else current_est_bolsa
        new_tau_bolsa = tau_bolsa if tau_bolsa is not None else current_tau_bolsa
        self.state["bag_state"] = (new_est_bolsa, new_tau_bolsa)
        
        if actions is not None:
            self.state["actions"] = actions

    def tolerance_exceeded(self, last_sensor_medition, objective):
        return no_tolerable(objective, last_sensor_medition)

    def timeAdvance(self):
        uCM, cO, tol, est_flujo, est_bolsa, tau_bolsa, actions = self.get_vars()
        if actions:
            return actions[0][1]
        elif est_bolsa == BagState.AWAIT_STOP_BAG:
            return tau_bolsa
        else:
            return float('inf')

    def extTransition(self, inputs):
        e = self.elapsed
        state_before = copy.deepcopy(self.state) 
        
        uCM, cO, tol, est_flujo, est_bolsa, tau_bolsa, actions = self.get_vars()
       
        if est_bolsa == BagState.EMPTY_BAG:
            new_tau_bolsa = max(0.0, tau_bolsa - e) if tau_bolsa != float('inf') else float('inf')
            new_actions = list(actions)
            if new_actions:
                action, delay = new_actions[0]
                new_actions[0] = (action, max(0.0, delay - e))
            self.set_vars(tau_bolsa=new_tau_bolsa, actions=new_actions)
            return self.state
            
        # common time decrement for tau_bolsa
        new_tau_bolsa = max(0.0, tau_bolsa - e) if tau_bolsa != float('inf') else float('inf')
        
        # 1. medical order (port 0)
        if self.in_medical_order in inputs:
            # inputs[self.in_medical_order] is tuple (hours_interval, flow_ml_h)
            _, c = inputs[self.in_medical_order]
            
            if c > 0:
                delay = random.uniform(0.0, 3.0)
                new_actions = conLog(
                    state_before,
                    [(("ajustarCaudal", c - uCM), delay)]
                )
            else:
                new_actions = conLog(
                    state_before,
                    [("detenerBomba", 0.0)]
                )
            self.set_vars(cO=c, tau_bolsa=new_tau_bolsa, actions=new_actions)
            
        # 2. sensor flow (port 1)
        elif self.in_sensor_flow in inputs:
            x = inputs[self.in_sensor_flow]
            
            if tol >= 5 and est_flujo == FlowState.MEDIUM_FLOW:
                new_actions = conLog(
                    state_before,
                    [("alarmaCritica", 0.0), ("detenerBomba", 0.0)]
                )
                self.set_vars(uCM=x, tol=0, est_flujo=FlowState.CRITICAL_FLOW, tau_bolsa=new_tau_bolsa, actions=new_actions)
            elif tol >= 5 and est_flujo == FlowState.NORMAL_FLOW:
                new_actions = conLog(
                    state_before,
                    [("alarmaMedia", 0.0)]
                )
                self.set_vars(uCM=x, tol=0, est_flujo=FlowState.MEDIUM_FLOW, tau_bolsa=new_tau_bolsa, actions=new_actions)
            elif self.tolerance_exceeded(x, cO) and tol < 5:
                self.set_vars(uCM=x, tol=tol + 1, tau_bolsa=new_tau_bolsa, actions=[])
            else:
                self.set_vars(uCM=x, tol=0, tau_bolsa=new_tau_bolsa, actions=[])
                
        # 3. end of bag signal (port 2)
        elif self.in_end_bag in inputs:
            if est_bolsa == BagState.NORMAL_BAG:
                new_actions = conLog(
                    state_before,
                    [("alarmaBaja", 0.0)]
                )
                self.set_vars(est_bolsa=BagState.END_BAG, tau_bolsa=new_tau_bolsa, actions=new_actions)
            elif est_bolsa in (BagState.END_BAG, BagState.AWAIT_STOP_BAG, BagState.EMPTY_BAG):
                new_actions = list(actions)
                if new_actions:
                    action, delay = new_actions[0]
                    new_actions[0] = (action, max(0.0, delay - e))
                self.set_vars(tau_bolsa=new_tau_bolsa, actions=new_actions)
                
        # 4. nurse confirmation (port 3)
        elif self.in_nurse_confirmation in inputs:
            new_actions = conLog(
                state_before,
                [(("ajustarCaudal", cO - uCM), 0.0)]
            )
            self.set_vars(tol=0, est_flujo=FlowState.NORMAL_FLOW, tau_bolsa=new_tau_bolsa, actions=new_actions)
            
        return self.state

    def intTransition(self):
        uCM, cO, tol, est_flujo, est_bolsa, tau_bolsa, actions = self.get_vars()
        
        if actions:
            action, delay = actions.pop(0)
            
            if est_bolsa == BagState.END_BAG and action == "alarmaBaja":
                self.set_vars(est_bolsa=BagState.AWAIT_STOP_BAG, tau_bolsa=60.0, actions=[])
                
            elif est_bolsa == BagState.EMPTY_BAG and action == "detenerBomba":
                self.set_vars(tau_bolsa=float('inf'), actions=[])
            else:
                self.set_vars(actions=actions)
                
        else:
            if est_bolsa == BagState.AWAIT_STOP_BAG:
                state_snapshot = copy.deepcopy(self.state)
                new_actions = conLog(
                    state_snapshot,
                    [("detenerBomba", 0.0)]
                )
                self.set_vars(est_bolsa=BagState.EMPTY_BAG, tau_bolsa=0.0, actions=new_actions)
                
        return self.state

    def outputFnc(self):
        uCM, cO, tol, est_flujo, est_bolsa, tau_bolsa, actions = self.get_vars()
        if actions:
            action, delay = actions[0]
            if isinstance(action, tuple) and action[0] == "ajustarCaudal":
                return {self.out_adjust_flow: action[1]}
            elif action == "detenerBomba":
                return {self.out_turn_off_bomb: True}
            elif action in ("alarmaBaja", "alarmaMedia", "alarmaCritica"):
                return {self.out_alarm: action}
            elif isinstance(action, tuple) and action[0] == "registrarEvento":
                return {self.out_log: action[1]}
        return {}
