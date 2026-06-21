from enum import Enum
import random
from copy import copy
from pypdevs.DEVS import AtomicDEVS


class NurseState(Enum):
    IDLE = "idle"
    WAITING_CONFIRMATION = "waiting_confirmation"


class GeneratorNurseConfirmation(AtomicDEVS):

    def __init__(self, initial_sigma=float("inf"), initial_phase=NurseState.IDLE):
        super().__init__("GeneratorNurseConfirmation")

        self.in_alarm = self.addInPort("in_alarm")
        self.out_confirmation = self.addOutPort("out_confirmation")

        self.state = {
            "sigma": initial_sigma,
            "phase": initial_phase
        }

    def extTransition(self, inputs) -> dict:
        state = copy(self.state)

        if self.in_alarm in inputs:
            x = inputs[self.in_alarm][0]

            if state["phase"] == NurseState.IDLE:
                state["phase"] = NurseState.WAITING_CONFIRMATION
                state["sigma"] = random.uniform(5, 75)

            else:
                state["sigma"] -= self.elapsed

        return state

    def intTransition(self) -> dict:
        state = copy(self.state)

        state["phase"] = NurseState.IDLE
        state["sigma"] = float("inf")

        return state

    def outputFnc(self) -> dict:
        if self.state["phase"] == NurseState.WAITING_CONFIRMATION:
            return {self.out_confirmation: ["CONFIRMATION_NURSE"]}
        return {}

    def timeAdvance(self) -> float:
        return self.state["sigma"]