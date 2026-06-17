import src.utils.utils as Utils
from src.models.gen_medical_order_devs import MedicalOrderGenerator
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS


class PumpSystem(CoupledDEVS):

    def __init__(self, client_criticality=1.0):
        super().__init__("PumpSystem")
        self.client_criticality = client_criticality
        
        # Inject medical order DEVS generator (emits orders parametrized by criticality)
        self.add_component("medical_order_gen", MedicalOrderGenerator(client_criticality))

    def add_component(self, name, component):
        return 0
