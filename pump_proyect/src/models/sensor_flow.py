import copy
from pypdevs.DEVS import AtomicDEVS


class SensorFlow(AtomicDEVS):
    def __init__(self):
        super().__init__("SensorFlow")

        self.in_actuator = self.addInPort("in_actuator")
        self.out_flow_measurement = self.addOutPort("out_flow_measurement")

        self.state = {
            "current_flow": 0,
            "sigma": float("inf")
        }

    def extTransition(self, inputs):
        state = copy.copy(self.state)

        if self.in_actuator in inputs:
            x = inputs[self.in_actuator]

            state["sigma"] -= self.elapsed
            state["current_flow"] = x

        return state

    def intTransition(self):
        state = copy.copy(self.state)

        state["sigma"] = 1

        return state

    def outputFnc(self):
        return {
            self.out_flow_measurement: (self.state["current_flow"])
        }

    def timeAdvance(self):
        return self.state["sigma"]