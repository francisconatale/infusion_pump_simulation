from pypdevs.DEVS import CoupledDEVS

class PumpSystem(CoupledDEVS):
    def __init__(self, client_criticality):
        super().__init__("PumpSystem")

        self.client_criticality = client_criticality

        self.end_bag_generator = self.addSubModel(
            EndBagGenerator()
        )
    
        self.controller_pump = self.addSubModel(
            ControllerPump()
        )

        self.nurse_confirmation_generator = self.addSubModel(
            NurseConfirmationGenerator()
        )

        self.sensor_flow = self.addSubModel(SensorFlow())

        self.medical_order_generator = self.addSubModel(
            MedicalOrderGenerator(client_criticality)
        )

        self.connectPorts(
            self.medical_order_generator.out_medical_order,
            self.controller_pump.in_medical_order
        )

        self.connectPorts(self.end_bag_generator.out_end_bag,
                            self.controller_pump.in_end_bag)

        self.connectPorts(self.sensor_flow.out_flow_measurement,
                            self.controller_pump.in_sensor_flow)

        self.connectPorts(self.nurse_confirmation_generator.out_confirmation,
                            self.controller_pump.in_nurse_confirmation)

        #   self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        