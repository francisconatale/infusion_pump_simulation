from pypdevs.DEVS import AtomicDEVS
from src.utils.random_utils import hours_to_seconds
from src.utils.random_utils import RandomGenerator
from math import inf as infinity

# Generates how much does it take to finish a given bag of medication
class EndBagGenerator(AtomicDEVS):
    """DEVS Generator for end of bag.
	
    Ports:
	  - out_end_bag: output port emitting (hours_interval, flow_ml_h) tuples
	"""

    def __init__(self):
        super().__init__("EndBagGenerator")

        self.in_order = self.addInPort("in_order")
        self.out_end_bag = self.addOutPort("out_end_bag")

        self.current_phase = "inactive"        
        self.current_hours_interval = infinity

        self.update_state(self.current_phase, self.current_hours_interval)

    def extTransition(self, inputs):
        e = self.elapsed

        if self.in_order not in inputs:
            return self.state

        hours, caudal = inputs[self.in_order]

        sx = "active" if caudal > 0 else "inactive"

        if sx == "active" and self.state["phase"] == "inactive":
            self.update_state(
                "programmed",
                self.time_bag()
            )

        elif sx == "active" and self.state["phase"] == "programmed":
            self.update_state(
                "programmed",
                self.state["hours"] - e
            )

        elif sx == "inactive":
            self.update_state(
                "inactive",
                infinity
            )

        return self.state

    def intTransition(self):
        """Internal transition: stay inactive until next call."""
        self.current_phase = "inactive"        
        self.current_hours_interval = infinity

        self.update_state(self.current_phase, self.current_hours_interval)

        return self.state

    def outputFnc(self):
        if self.state["phase"] == "programmed":
            return {
                self.out_end_bag: ("endBag",)
            }

        return {}

    def timeAdvance(self):
        """Time advance: hours until next order."""
        return self.state["hours"]

    def update_state(self,current_phase, hours_interval):
        self.current_phase = current_phase
        self.current_hours_interval = hours_interval

        self.state = {
            "phase": self.current_phase,
            "hours": self.current_hours_interval
        }
    
    def time_bag(self):
        min_hours = hours_to_seconds(4)
        max_hours = hours_to_seconds(6)

        return RandomGenerator.get_uniform(min_hours, max_hours)