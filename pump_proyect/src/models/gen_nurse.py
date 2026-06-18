from enum import Enum
import random
from copy import deepcopy
from pypdevs.DEVS import AtomicDEVS


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
        state = deepcopy(self.state)

        if self.in_alarm in inputs:
            x = inputs[self.in_alarm]

            if state["phase"] == NurseState.IDLE:
                state["phase"] = NurseState.WAITING_CONFIRMATION
                state["sigma"] = random.uniform(5, 75)

            else:
                state["sigma"] -= self.elapsed

        return state

    def intTransition(self):
        state = deepcopy(self.state)

        state["phase"] = NurseState.IDLE
        state["sigma"] = float("inf")

        return state

    def outputFnc(self):
        if self.state["phase"] == NurseState.WAITING_CONFIRMATION:
            return {
                self.out_nurse_confirmation: "CONFIRMATION_NURSE"
            }
        return {}

    def timeAdvance(self):
        return self.state["sigma"]