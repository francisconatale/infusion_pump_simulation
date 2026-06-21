from math import inf

from pypdevs.DEVS import AtomicDEVS

from src.utils.medical_order_factory.factory_medical_order import (
    MedicalOrderFactory
)
from src.utils.random_utils import hours_to_seconds


class MedicalOrderGenerator(AtomicDEVS):
    """DEVS Generator for medical orders.
    
    - Non Deterministic
    Emits medical orders (hours, ml) tuples at regular intervals determined
    by the MedicalOrderFactory parametrized by client criticality.

    - Deterministic: active == False
    Does the same, but with a list of orders given by the user 
        orders = [
            (0, 50),
            (100, 80),
            (200, 0)
        ]

    Every tuple: (time_simulation, ml)
    
    Ports:
      - out_medical_order: output port emitting (hours_interval, flow_ml_h) tuples
    
    Usage:
      gen = MedicalOrderGenerator(client_criticality=k)
      # In DEVS simulation, will emit orders on 'out_medical_order' port
    """

    def __init__(self, client_criticality: float = 1.0, active=True, orders=None):
        super().__init__("MedicalOrderGenerator")

        self.out_medical_order = self.addOutPort(
            "out_medical_order"
        )

        self.active = active
        self.orders = orders or []

        # Non Deterministic
        if self.active:

            self.factory = MedicalOrderFactory(
                client_criticality
            )

            order = self.factory.next_order()
            hours, ml = order

            self.state = {
                "sigma": 0.0,
                "order": order,
                "hours": hours,
                "ml": ml
            }

        # Deterministic
        else:

            if not self.orders:
                raise ValueError(
                    "orders must be provided when active=False"
                )

            self.index = 0

            first_time, first_flow = (
                self.orders[0]
            )

            self.state = {
                "sigma": first_time,
                "order": (0, first_flow),
                "hours": 0,
                "ml": first_flow
            }

    def intTransition(self) -> dict:

        # Non deterministic
        if self.active:

            self.state["order"] = (
                self.factory.next_order()
            )

            self.state["hours"], self.state["ml"] = (
                self.state["order"]
            )

            self.state["sigma"] = hours_to_seconds(
                self.state["hours"]
            )

            return self.state

        # Deterministic
        self.index += 1

        if self.index >= len(self.orders):
            self.state["sigma"] = inf
            return self.state

        current_time, flow = (
            self.orders[self.index]
        )

        previous_time, _ = (
            self.orders[self.index - 1]
        )

        self.state["order"] = (0, flow)
        self.state["hours"] = 0
        self.state["ml"] = flow

        self.state["sigma"] = (
            current_time - previous_time
        )

        return self.state

    def outputFnc(self) -> dict:
        return {
            self.out_medical_order: [self.state["order"]]
        }

    def timeAdvance(self) -> float:
        return self.state["sigma"]