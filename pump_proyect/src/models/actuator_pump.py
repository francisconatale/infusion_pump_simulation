import copy
import random
from enum import Enum
from pypdevs.DEVS import AtomicDEVS

class ActuatorStatus(Enum):
    RUNNING = "running"
    IDLE = "in_controller"

class ActuatorPump(AtomicDEVS):
    def __init__(self):
        super().__init__("ActuatorPump")
        self.in_controller = self.addInPort("in_controller")
        self.out_sensor_flow = self.addOutPort("out_sensor_flow")
        self.state = {
            "currentCaudal": 0.0,
            "status": ActuatorStatus.IDLE,
            "sigma": float('inf')
        } 

    def extTransition(self, inputs) -> dict:
        state = copy.copy(self.state)

        if self.in_controller in inputs:
            (action, delta) = inputs[self.in_controller][0]

            if action == "AdjustFlow":
                newCaudal = self.saturation(state["currentCaudal"], delta)
                state["currentCaudal"] = newCaudal
                state["status"] = ActuatorStatus.RUNNING 
                state["sigma"] = random.uniform(0, 5)
            elif action == "OffBomb":
                state["status"] = ActuatorStatus.IDLE
                state["sigma"] = 0.0
        
        return state

    def intTransition(self) -> dict:
        state = copy.copy(self.state)
        state["sigma"] = float('inf')
        return state

    def outputFnc(self) -> dict:
        return {self.out_sensor_flow: [self.state["currentCaudal"]]}

    def timeAdvance(self) -> float:
        return self.state["sigma"]
    
    @staticmethod
    def saturation(x: float, delta: float) -> float:
        alpha = random.uniform(0.10, 0.30)
        x_next = x + alpha * delta
        return max(0.0, min(200.0, x_next))
