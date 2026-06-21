from math import inf

from pypdevs.DEVS import CoupledDEVS

from src.models.gen_bag_end import EndBagGenerator
from src.models.controller_pump import PumpController
from src.models.gen_nurse import GeneratorNurseConfirmation
from src.models.gen_medical_order import MedicalOrderGenerator
from src.models.sensor_flow import SensorFlow
from src.models.actuator_pump import ActuatorPump
from src.models.alarm_module import AlarmModule
from src.models.logger import Logger

from src.specific_models.gen_specific_medical_order import (
    ScenarioMedicalOrderGenerator
)
from src.specific_models.specific_actuator_pump import (
    ScenarioDeviationPump
)
from src.specific_models.gen_specific_end_bag import (
    SpecificBagGenerator
)
from src.specific_models.gen_specific_nurse import (
    SpecificNurseConfirmation
)


class PumpSystem(CoupledDEVS):

    def __init__(self, client_criticality, scenario="normal"):
        super().__init__("PumpSystem")

        self.client_criticality = client_criticality

        self._create_scenario_models(scenario)
        self._create_core_models()
        self._create_connections()

    # ------------------------------------------------------------------
    # SCENARIOS
    # ------------------------------------------------------------------

    def _create_scenario_models(self, scenario):

        # Defaults
        medical_order = MedicalOrderGenerator(self.client_criticality)
        actuator = ActuatorPump()
        end_bag = EndBagGenerator()
        nurse = GeneratorNurseConfirmation()

        if scenario == "order_change":
            medical_order = ScenarioMedicalOrderGenerator([
                (0, 50),
                (100, 80)
            ])

        elif scenario == "stop_order":
            medical_order = ScenarioMedicalOrderGenerator([
                (0, 50),
                (100, 0)
            ])

        elif scenario == "mild_deviation":
            actuator = ScenarioDeviationPump(
                deviation_factor=0.92,
                duration=20
            )

        elif scenario == "critical_deviation":
            actuator = ScenarioDeviationPump(
                deviation_factor=0.70,
                duration=inf
            )

            nurse = SpecificNurseConfirmation(
                confirmation_time=60
            )

        elif scenario == "end_bag":
            end_bag = SpecificBagGenerator(
                end_bag_time=100
            )

            nurse = SpecificNurseConfirmation(
                confirmation_time=5
            )

        elif scenario == "no_confirmation":
            nurse = SpecificNurseConfirmation(
                confirmation_time=inf
            )

        self.medical_order_generator = self.addSubModel(
            medical_order
        )

        self.actuator_pump = self.addSubModel(
            actuator
        )

        self.end_bag_generator = self.addSubModel(
            end_bag
        )

        self.nurse_confirmation_generator = self.addSubModel(
            nurse
        )

    # ------------------------------------------------------------------
    # COMMON MODELS
    # ------------------------------------------------------------------

    def _create_core_models(self):

        self.controller_pump = self.addSubModel(
            PumpController()
        )

        self.sensor_flow = self.addSubModel(
            SensorFlow()
        )

        self.alarm_module = self.addSubModel(
            AlarmModule()
        )

        self.logger = self.addSubModel(
            Logger()
        )

        self.out_alarm = self.addOutPort(
            "out_alarm"
        )

    # ------------------------------------------------------------------
    # CONNECTIONS
    # ------------------------------------------------------------------

    def _create_connections(self):

        # Medical order -> controller
        self.connectPorts(
            self.medical_order_generator.out_medical_order,
            self.controller_pump.in_medical_order
        )

        # Medical order -> bag generator
        self.connectPorts(
            self.medical_order_generator.out_medical_order,
            self.end_bag_generator.in_order
        )

        # End bag -> controller
        self.connectPorts(
            self.end_bag_generator.out_end_bag,
            self.controller_pump.in_end_bag
        )

        # Controller -> actuator
        self.connectPorts(
            self.controller_pump.out_flow,
            self.actuator_pump.in_controller
        )

        # Actuator -> sensor
        self.connectPorts(
            self.actuator_pump.out_sensor_flow,
            self.sensor_flow.in_actuator
        )

        # Sensor -> controller
        self.connectPorts(
            self.sensor_flow.out_flow_measurement,
            self.controller_pump.in_sensor_flow
        )

        # Controller -> alarm module
        self.connectPorts(
            self.controller_pump.out_alarm,
            self.alarm_module.in_alarm
        )

        # Alarm -> nurse
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.nurse_confirmation_generator.in_alarm
        )

        # Nurse -> controller
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.controller_pump.in_nurse_confirmation
        )

        # Nurse -> alarm module
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.alarm_module.in_nurse_confirmation
        )

        # Nurse -> logger
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.logger.in_nurse_confirmation
        )

        # Controller -> logger
        self.connectPorts(
            self.controller_pump.out_log,
            self.logger.in_state_control
        )

        # Alarm -> logger
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.logger.in_alarm_module
        )

        # External output
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.out_alarm
        )

    # ------------------------------------------------------------------
    # SELECT
    # ------------------------------------------------------------------

    def select(self, imm_children):

        order = {
            MedicalOrderGenerator: 0,
            PumpController: 1,
            ActuatorPump: 2,
            SensorFlow: 3,
            EndBagGenerator: 4,
            GeneratorNurseConfirmation: 5,
            AlarmModule: 6,
            Logger: 7,
        }

        return min(
            imm_children,
            key=lambda x: order.get(type(x), 99)
        )