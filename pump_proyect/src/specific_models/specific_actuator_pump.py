import copy
import random

from src.models.actuator_pump import ActuatorPump, ActuatorStatus


class ScenarioDeviationPump(ActuatorPump):

    def __init__(
        self,
        deviation_factor: float,
        duration: float = float("inf")
    ):
        super().__init__()

        self.deviation_factor = deviation_factor
        self.duration = duration
        self.elapsed_time = 0.0

    def extTransition(self, inputs):
        state = copy.copy(self.state)

        self.elapsed_time += self.elapsed

        if self.in_controller in inputs:
            action, delta = inputs[self.in_controller][0]

            if action == "AdjustFlow":

                ideal_flow = self.saturation(
                    state["currentCaudal"],
                    delta
                )

                if self.elapsed_time < self.duration:
                    state["currentCaudal"] = (
                        ideal_flow * self.deviation_factor
                    )
                else:
                    state["currentCaudal"] = ideal_flow

                state["status"] = ActuatorStatus.RUNNING
                state["sigma"] = random.uniform(0, 5)

            elif action == "OffBomb":
                state["currentCaudal"] = 0
                state["status"] = ActuatorStatus.IDLE
                state["sigma"] = 0.0

        return state