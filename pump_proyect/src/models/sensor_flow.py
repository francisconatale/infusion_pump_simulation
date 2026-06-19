import copy
from pypdevs.DEVS import AtomicDEVS


class SensorFlow(AtomicDEVS):
    def __init__(self):
        super().__init__("SensorFlow")

        self.in_actuator = self.addInPort("in_actuator")
        self.out_flow_measurement = self.addOutPort("out_flow_measurement")

        self.state = {
            "current_flow": 0.0,
            "sigma": float("inf")
        }

    def extTransition(self, inputs) -> dict:
        state = copy.copy(self.state)

        if self.in_actuator in inputs:
            x = inputs[self.in_actuator]
            state["current_flow"] = x
            if state["sigma"] == float("inf"):
                state["sigma"] = 0.0
            else:
                state["sigma"] = max(0.0, state["sigma"] - self.elapsed)

        return state

    def intTransition(self) -> dict:
        state = copy.copy(self.state)
        state["sigma"] = 1.0
        return state

    def outputFnc(self) -> dict:
        return {
            self.out_flow_measurement: self.state["current_flow"]
        }

    def timeAdvance(self) -> float:
        return self.state["sigma"]