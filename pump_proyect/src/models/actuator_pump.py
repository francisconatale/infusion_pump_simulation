import copy
import random
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
                "currentCaudal": 0,
                "status": ActuatorStatus.IDLE,
                "sigma": float('inf')
                } 

    def extTransition(self, inputs):
        state = copy.copy(self.state)

        if self.in_controller in inputs:
            (action, delta) = inputs[self.in_controller]

        if action == "AdjustFlow":
            newCaudal = saturation(state["currentCaudal"] + delta)
            state["currentCaudal"] = newCaudal
            state["status"] = ActuatorStatus.RUNNING 
            state["sigma"] = random.uniform(0, 5)
        elif action == "OffBomb"
            state["status"] = ActuatorStatus.IDLE
            state["sigma"] = 0.0
        return state

    def intTransition(self):
        state = copy(self.state)
        state["sigma"] = float('inf')

    def outputFnc(self):
        return {self.out_sensor_flow: currentCaudal}

    def timeAdvance(self):
        return self.state["sigma"]
    
    def saturation(x, delta, alpha=0.2):
        x_next = x + alpha * delta
        return max(0, min(200, x_next))
