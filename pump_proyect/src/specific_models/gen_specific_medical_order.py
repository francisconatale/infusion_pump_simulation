from pypdevs.DEVS import AtomicDEVS
from src.utils.medical_order_factory.factory_medical_order import MedicalOrderFactory
from src.utils.random_utils import hours_to_seconds
from math import inf 

class ScenarioMedicalOrderGenerator(AtomicDEVS):
    """DEVS Generator for medical orders.
    
    Emits medical orders (hours, ml) tuples at regular intervals determined
    by list of orders given by the user 
        orders = [
            (0, 50),
            (100, 80),
            (200, 0)
        ]

    Every tuple: (time_simulation, ml)
    
    Ports:
      - out_medical_order: output port emitting (hours_interval, flow_ml_h) tuples
    """

    def __init__(self, orders=None):
        super().__init__("MedicalOrderGenerator")

        self.out_medical_order = self.addOutPort("out_medical_order")

        self.orders = orders
        
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
