from enum import Enum
import random
from copy import deepcopy

class NurseState(Enum):
    IDLE = "idle"
    WAITING_CONFIRMATION = "waiting_confirmation"


class GeneratorNurseConfirmation(AtomicDEVS):

    def __init__(self):
        super().__init__("GeneratorNurseConfirmation")

        self.in_alarm = self.addInPort("in_alarm")
        self.out_nurse_confirmation = self.addOutPort("out_confirmation")

        self.state = {
            "sigma": float("inf"),
            "phase": NurseState.IDLE
        }

    def extTransition(self, inputs):
        # get state
        state = deepcopy(self.state)
        # build new state
        if self.in_alarm in inputs:
            if state["phase"] == NurseState.IDLE:
                state["sigma"] = random.uniform(5, 75)
                state["phase"] = NurseState.WAITING_CONFIRMATION
            else:
                state["sigma"] -= self.elapsed
        # return new state
        return state
    
    def intTransition(self):
        return { "sigma": float("inf"), "phase": NurseState.IDLE }

    def outputFnc(self):
        if (self.state["phase"] == NurseState.WAITING_CONFIRMATION):
            return { self.out_nurse_confirmation: "CONFIRMATION_NURSE" }

    def timeAdvance(self):
	    return self.state["sigma"]
