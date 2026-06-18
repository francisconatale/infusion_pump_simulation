from pypdevs.DEVS import CoupledDEVS

class PumpSystem(CoupledDEVS):
    def __init__(self, client_criticality):
        super().__init__("PumpSystem")

        self.client_criticality = client_criticality

        self.controller_pump = self.addSubModel(
            ControllerPump()
        )

        self.medical_order_gen = self.addSubModel(
            MedicalOrderGenerator(client_criticality)
        )

        self.connectPorts(
            self.medical_order_gen.out_order,
            self.controller_pump.in_medical_order
        )