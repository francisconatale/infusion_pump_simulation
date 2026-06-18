import src.utils.utils as Utils
from src.models.gen_medical_order_devs import MedicalOrderGenerator
from src.models.gen_bag_end import EndBagGenerator
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS


class PumpSystem(CoupledDEVS):

    def __init__(self, client_criticality=1.0):
        super().__init__("PumpSystem")
        self.client_criticality = client_criticality
        
        self.medical_order_gen = self.addSubModel(
            MedicalOrderGenerator(client_criticality)
        )

        self.bag_end_gen = self.addSubModel(
            EndBagGenerator()
        )

        self.connectPorts(
            self.medical_order_gen.out_order,
            self.bag_end_gen.in_order
        )
