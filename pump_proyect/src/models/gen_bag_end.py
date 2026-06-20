from enum import Enum
from pypdevs.DEVS import AtomicDEVS
from src.utils.random_utils import hours_to_seconds
from src.utils.random_utils import RandomGenerator
from math import inf as infinity

class BagState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROGRAMMED = "programmed"

# Generates how much does it take to finish a given bag of medication
class EndBagGenerator(AtomicDEVS):
    """DEVS Generator for end of bag.
    
    Ports:
      - out_end_bag: output port emitting (hours_interval, flow_ml_h) tuples
    """

    def __init__(self):
        super().__init__("EndBagGenerator")

        ## X
        self.in_order = self.addInPort("in_order")

        ## Y
        self.out_end_bag = self.addOutPort("out_end_bag")

        ## Initial state
        self.state = {
            "phase" : BagState.INACTIVE,
            "hours" : infinity
        }

    def extTransition(self, inputs) -> dict:
        e = self.elapsed

        if self.in_order not in inputs:
            return self.state

        hours, caudal = inputs[self.in_order][0]

        sx = BagState.ACTIVE if caudal > 0 else BagState.INACTIVE

        if sx == BagState.ACTIVE and self.state["phase"] == BagState.INACTIVE:
            self.state["phase"] = BagState.PROGRAMMED
            self.state["hours"] = self.time_bag()

        elif sx == BagState.ACTIVE and self.state["phase"] == BagState.PROGRAMMED:
            self.state["hours"] = self.state["hours"] - e

        elif sx == BagState.INACTIVE:
            self.state["phase"] = BagState.INACTIVE
            self.state["hours"] = infinity

        return self.state

    def intTransition(self) -> dict:
        """Internal transition: stay inactive until next call."""
        self.state["phase"] = BagState.INACTIVE   
        self.state["hours"] = infinity

        return self.state

    def outputFnc(self) -> dict:
        if self.state["phase"] == BagState.PROGRAMMED:
            return {
                self.out_end_bag: [("end_bag",)]
            }

        return {}

    def timeAdvance(self) -> float:
        """Time advance: hours until next order."""
        return self.state["hours"]

    def time_bag(self) -> float:
        min_hours = hours_to_seconds(4)
        max_hours = hours_to_seconds(6)

        return RandomGenerator.get_uniform(min_hours, max_hours)