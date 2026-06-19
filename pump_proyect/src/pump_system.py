from pypdevs.DEVS import CoupledDEVS
from src.models.gen_bag_end import EndBagGenerator
from src.models.controller_pump import PumpController
from src.models.gen_nurse import GeneratorNurseConfirmation
from src.models.gen_medical_order import MedicalOrderGenerator
from src.models.sensor_flow import SensorFlow
from src.models.alarm_module import AlarmModule
from src.models.logger import Logger

class PumpSystem(CoupledDEVS):
    def __init__(self, client_criticality):
        super().__init__("PumpSystem")

        self.client_criticality = client_criticality

        self.end_bag_generator = self.addSubModel(
            EndBagGenerator()
        )
    
        self.controller_pump = self.addSubModel(
            PumpController()
        )

        self.nurse_confirmation_generator = self.addSubModel(
            GeneratorNurseConfirmation()
        )

        self.sensor_flow = self.addSubModel(SensorFlow())

        self.medical_order_generator = self.addSubModel(
            MedicalOrderGenerator(client_criticality)
        )

        self.logger = self.addSubModel(
            Logger()
        )

        self.alarm_module = self.addSubModel(
            AlarmModule()
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

        self.connectPorts(self.controller_pump.out_log,
                            self.logger.in_state_control)

        self.connectPorts(self.controller_pump.out_alarm,
                            self.alarm_module.in_alarm)

        #   self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        