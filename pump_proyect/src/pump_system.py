from pypdevs.DEVS import CoupledDEVS
from src.models.gen_bag_end import EndBagGenerator
from src.models.controller_pump import PumpController
from src.models.gen_nurse import GeneratorNurseConfirmation
from src.models.gen_medical_order import MedicalOrderGenerator
from src.models.sensor_flow import SensorFlow
from src.models.actuator_pump import ActuatorPump
from src.models.alarm_module import AlarmModule
from src.models.logger import Logger


class PumpSystem(CoupledDEVS):
    def __init__(self, client_criticality: float, initial_states: dict = None):
        super().__init__("PumpSystem")

        self.client_criticality = client_criticality

        # Extract initial states parameters for each submodel, defaulting to empty dicts
        initial_states = initial_states or {}
        med_gen_init = initial_states.get("med_order", {})
        end_bag_init = initial_states.get("end_bag", {})
        controller_init = initial_states.get("controller", {})
        actuator_init = initial_states.get("actuator", {})
        sensor_init = initial_states.get("sensor", {})
        nurse_init = initial_states.get("nurse", {})
        alarm_init = initial_states.get("alarm", {})
        logger_init = initial_states.get("logger", {})

        self.medical_order_generator = self.addSubModel(
            MedicalOrderGenerator(client_criticality=client_criticality, **med_gen_init)
        )

        self.end_bag_generator = self.addSubModel(
            EndBagGenerator(**end_bag_init)
        )

        self.controller_pump = self.addSubModel(
            PumpController(**controller_init)
        )

        self.actuator_pump = self.addSubModel(
            ActuatorPump(**actuator_init)
        )

        self.sensor_flow = self.addSubModel(
            SensorFlow(**sensor_init)
        )

        self.nurse_confirmation_generator = self.addSubModel(
            GeneratorNurseConfirmation(**nurse_init)
        )

        self.alarm_module = self.addSubModel(
            AlarmModule(**alarm_init)
        )

        self.logger = self.addSubModel(
            Logger(**logger_init)
        )

        # Puerto de salida externo (EOC): M_alarmas → N
        self.out_alarm = self.addOutPort("out_alarm")

        # ── IC: M_gen → M_ctrl ──
        self.connectPorts(
            self.medical_order_generator.out_medical_order,
            self.controller_pump.in_medical_order
        )

        # ── IC: M_gen → M_bolsa ──
        self.connectPorts(
            self.medical_order_generator.out_medical_order,
            self.end_bag_generator.in_order
        )

        # ── IC: M_bolsa → M_ctrl ──
        self.connectPorts(
            self.end_bag_generator.out_end_bag,
            self.controller_pump.in_end_bag
        )

        # ── IC: M_ctrl → M_bomba (lazo de control) ──
        self.connectPorts(
            self.controller_pump.out_flow,
            self.actuator_pump.in_controller
        )

        # ── IC: M_bomba → M_sensor (lazo de control) ──
        self.connectPorts(
            self.actuator_pump.out_sensor_flow,
            self.sensor_flow.in_actuator
        )

        # ── IC: M_sensor → M_ctrl (lazo de control) ──
        self.connectPorts(
            self.sensor_flow.out_flow_measurement,
            self.controller_pump.in_sensor_flow
        )

        # ── IC: M_ctrl → M_alarmas ──
        self.connectPorts(
            self.controller_pump.out_alarm,
            self.alarm_module.in_alarm
        )

        # ── IC: M_alarmas → M_enf ──
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.nurse_confirmation_generator.in_alarm
        )

        # ── IC: M_enf → M_ctrl ──
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.controller_pump.in_nurse_confirmation
        )

        # ── IC: M_enf → M_alarmas (confirmation silences alarm) ──
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.alarm_module.in_nurse_confirmation
        )

        # ── IC: M_enf → M_logger (confirmacion del enfermero) ──
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.logger.in_nurse_confirmation
        )

        # ── IC: M_enf → M_bolsa (confirmacion reanuda la bolsa) ──
        self.connectPorts(
            self.nurse_confirmation_generator.out_confirmation,
            self.end_bag_generator.in_nurse_confirmation
        )

        # ── IC: M_ctrl → M_logger ──
        self.connectPorts(
            self.controller_pump.out_log,
            self.logger.in_state_control
        )

        # ── IC: M_alarmas → M_logger ──
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.logger.in_alarm_module
        )

        # ── EOC: M_alarmas → N ──
        self.connectPorts(
            self.alarm_module.out_alarm,
            self.out_alarm
        )

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
        return min(imm_children, key=lambda x: order.get(type(x), 99))
        