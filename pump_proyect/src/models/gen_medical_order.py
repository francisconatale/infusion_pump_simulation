from pypdevs.DEVS import AtomicDEVS
from src.utils.medical_order_factory.factory_medical_order import MedicalOrderFactory
from src.utils.random_utils import hours_to_seconds


class MedicalOrderGenerator(AtomicDEVS):
    """DEVS Generator for medical orders.
    
    Emits medical orders (hours, ml) tuples at regular intervals determined
    by the MedicalOrderFactory parametrized by client criticality.
    
    Ports:
      - out_medical_order: output port emitting (hours_interval, flow_ml_h) tuples
    
    Usage:
      gen = MedicalOrderGenerator(client_criticality=k)
      # In DEVS simulation, will emit orders on 'out_medical_order' port
    """

    def __init__(self,
                 client_criticality: float = 1.0,
                 initial_sigma: float = 0.0,
                 initial_order: tuple = None,
                 initial_hours: float = None,
                 initial_ml: float = None):
        super().__init__("MedicalOrderGenerator")

        self.out_medical_order = self.addOutPort("out_medical_order")

        self.factory = MedicalOrderFactory(client_criticality)

        if initial_order is None:
            order = self.factory.next_order()
        else:
            order = initial_order

        if initial_hours is None:
            hours = order[0]
        else:
            hours = initial_hours

        if initial_ml is None:
            ml = order[1]
        else:
            ml = initial_ml

        self.state = {
            "sigma": initial_sigma,
            "order": order,
            "hours": hours,
            "ml": ml
        }

    def intTransition(self) -> dict:
        self.state["order"] = self.factory.next_order()
        self.state["hours"], self.state["ml"] = self.state["order"]
        self.state["sigma"] = hours_to_seconds(self.state["hours"])
        return self.state

    def outputFnc(self) -> dict:
        return {
            self.out_medical_order: [self.state["order"]]
        }

    def timeAdvance(self) -> float:
        return self.state["sigma"]
