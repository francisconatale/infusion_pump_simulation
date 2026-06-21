from src.models.actuator_pump import ActuatorStatus
from src.models.alarm_module import AlarmStatus
from src.models.controller_pump import FlowState, BagState as ControllerBagState
from src.models.gen_bag_end import BagState as GeneratorBagState
from src.models.gen_nurse import NurseState
from math import inf as infinity


class InitialStatesFactory:
    @staticmethod
    def get_initial_state(scenario: str = "default") -> dict:
        """
        Returns a dictionary containing the initial states for each DEVS model component
        for a specific scenario.
        """
        # 1. Default (Standard) initial states
        states = {
            "actuator": {
                "initial_currentCaudal": 0.0,
                "initial_status": ActuatorStatus.IDLE,
                "initial_sigma": infinity
            },
            "alarm": {
                "initial_alarm_state": AlarmStatus.NO_ALARM,
                "initial_hours": infinity
            },
            "controller": {
                "initial_flow_state": (FlowState.NORMAL_FLOW, 0.0),
                "initial_bag_state": (ControllerBagState.NORMAL_BAG, infinity),
                "initial_last_sensor_medition": 0.0,
                "initial_medical_order": 0.0,
                "initial_tolerance_exceedance_start_time": 0.0,
                "initial_actions": None
            },
            "end_bag": {
                "initial_phase": GeneratorBagState.INACTIVE,
                "initial_hours": infinity
            },
            "med_order": {
                "initial_sigma": 0.0,
                "initial_order": None
            },
            "nurse": {
                "initial_sigma": infinity,
                "initial_phase": NurseState.IDLE
            },
            "sensor": {
                "initial_current_flow": 0.0,
                "initial_sigma": infinity
            },
            "logger": {
                "initial_accumulated_time": 0.0,
                "log_filename": "resultados.csv",
                "initial_last_data": None
            }
        }

        # Apply scenario modifications
        scenario_lower = scenario.lower()
        if scenario_lower == "default":
            pass

        elif scenario_lower == "alarma_critica":
            states["alarm"]["initial_alarm_state"] = AlarmStatus.CRITICAL_ALARM
            states["alarm"]["initial_hours"] = 0.0
            states["actuator"]["initial_status"] = ActuatorStatus.IDLE
            states["controller"]["initial_flow_state"] = (FlowState.CRITICAL_FLOW, 5.0)

        elif scenario_lower == "tolerancia_excedida":
            states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 4.0)
            states["controller"]["initial_last_sensor_medition"] = 100.0
            states["controller"]["initial_medical_order"] = 120.0

        elif scenario_lower == "orden_medica_cero":
            states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
            states["controller"]["initial_last_sensor_medition"] = 120.0
            states["controller"]["initial_medical_order"] = 120.0
            states["actuator"]["initial_currentCaudal"] = 120.0
            states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
            states["sensor"]["initial_current_flow"] = 120.0
            states["med_order"]["initial_sigma"] = 0.0
            states["med_order"]["initial_order"] = (2, 0)
            states["med_order"]["initial_hours"] = 2.0
            states["med_order"]["initial_ml"] = 0.0
        
        elif scenario_lower == "fin_bolsa_por_60_segundos":
            states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
            states["controller"]["initial_last_sensor_medition"] = 120.0
            states["controller"]["initial_medical_order"] = 120.0
            states["actuator"]["initial_currentCaudal"] = 120.0
            states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
            states["sensor"]["initial_current_flow"] = 120.0
            states["end_bag"]["initial_phase"] = GeneratorBagState.PROGRAMMED
            states["end_bag"]["initial_hours"] = 0.0
            states["nurse"]["initial_phase"] = NurseState.IDLE
            states["nurse"]["initial_sigma"] = 100.0 # more than 60 seconds

        elif scenario_lower == "fin_bolsa_menos_de_60_segundos":
            states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
            states["controller"]["initial_last_sensor_medition"] = 120.0
            states["controller"]["initial_medical_order"] = 120.0
            states["actuator"]["initial_currentCaudal"] = 120.0
            states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
            states["sensor"]["initial_current_flow"] = 120.0
            states["end_bag"]["initial_phase"] = GeneratorBagState.PROGRAMMED
            states["end_bag"]["initial_hours"] = 0.0
            states["nurse"]["initial_phase"] = NurseState.IDLE
            states["nurse"]["initial_sigma"] = 10.0 # less than 60 seconds

        else:
            raise ValueError(
                f"Escenario desconocido: '{scenario}'. "
                "Los escenarios válidos son: 'default', 'alarma_critica', 'tolerancia_excedida'."
            )

        return states
