from typing import Dict, Any
from src.models.actuator_pump import ActuatorStatus
from src.models.alarm_module import AlarmStatus
from src.models.controller_pump import FlowState, BagState as ControllerBagState
from src.models.gen_bag_end import BagState as GeneratorBagState
from src.models.gen_nurse import NurseState
from math import inf as infinity


class InitialStatesFactory:
    @staticmethod
    def _get_base_states() -> Dict[str, Any]:
        return {
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

    @staticmethod
    def get_initial_state(scenario: str = "default") -> Dict[str, Any]:
        """
        Returns a dictionary containing the initial states for each DEVS model component
        for a specific scenario.
        """
        states = InitialStatesFactory._get_base_states()
        scenario_lower = scenario.lower()

        scenario_modifiers = {
            "default": InitialStatesFactory._apply_default,
            "alarma_critica": InitialStatesFactory._apply_alarma_critica,
            "tolerancia_excedida": InitialStatesFactory._apply_tolerancia_excedida,
            "orden_medica_cero": InitialStatesFactory._apply_orden_medica_cero,
            "orden_medica_cambio": InitialStatesFactory._apply_orden_medica_cambio,
            "fin_bolsa_por_60_segundos": InitialStatesFactory._apply_fin_bolsa_por_60_segundos,
            "fin_bolsa_menos_de_60_segundos": InitialStatesFactory._apply_fin_bolsa_menos_de_60_segundos,
        }

        modifier = scenario_modifiers.get(scenario_lower)
        if not modifier:
            valid_scenarios = "', '".join(scenario_modifiers.keys())
            raise ValueError(
                f"Escenario desconocido: '{scenario}'. "
                f"Los escenarios válidos son: '{valid_scenarios}'."
            )

        modifier(states)
        return states

    @staticmethod
    def _apply_default(states: Dict[str, Any]) -> None:
        pass

    @staticmethod
    def _apply_alarma_critica(states: Dict[str, Any]) -> None:
        states["alarm"]["initial_alarm_state"] = AlarmStatus.CRITICAL_ALARM
        states["alarm"]["initial_hours"] = 0.0
        states["actuator"]["initial_status"] = ActuatorStatus.IDLE
        states["controller"]["initial_flow_state"] = (FlowState.CRITICAL_FLOW, 5.0)

    @staticmethod
    def _apply_tolerancia_excedida(states: Dict[str, Any]) -> None:
        states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 4.0)
        states["controller"]["initial_last_sensor_medition"] = 100.0
        states["controller"]["initial_medical_order"] = 120.0

    @staticmethod
    def _apply_orden_medica_cero(states: Dict[str, Any]) -> None:
        states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
        states["controller"]["initial_last_sensor_medition"] = 120.0
        states["controller"]["initial_medical_order"] = 120.0
        states["actuator"]["initial_currentCaudal"] = 120.0
        states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
        states["sensor"]["initial_current_flow"] = 120.0
        states["med_order"]["initial_sigma"] = 0.0
        states["med_order"]["initial_order"] = (2, 0.0)

    @staticmethod
    def _apply_orden_medica_cambio(states: Dict[str, Any]) -> None:
        states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
        states["controller"]["initial_last_sensor_medition"] = 120.0
        states["controller"]["initial_medical_order"] = 120.0
        states["actuator"]["initial_currentCaudal"] = 120.0
        states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
        states["sensor"]["initial_current_flow"] = 120.0
        states["med_order"]["initial_sigma"] = 78.0
        states["med_order"]["initial_order"] = (2, 80.0)

    @staticmethod
    def _apply_fin_bolsa_por_60_segundos(states: Dict[str, Any]) -> None:
        states["controller"]["initial_flow_state"] = (FlowState.NORMAL_FLOW, 0.0)
        states["controller"]["initial_last_sensor_medition"] = 120.0
        states["controller"]["initial_medical_order"] = 120.0
        states["actuator"]["initial_currentCaudal"] = 120.0
        states["actuator"]["initial_status"] = ActuatorStatus.RUNNING
        states["sensor"]["initial_current_flow"] = 120.0
        states["end_bag"]["initial_phase"] = GeneratorBagState.PROGRAMMED
        states["end_bag"]["initial_hours"] = 0.0
        states["nurse"]["initial_phase"] = NurseState.IDLE
        states["nurse"]["initial_sigma"] = 100.0  # more than 60 seconds

    @staticmethod
    def _apply_fin_bolsa_menos_de_60_segundos(states: Dict[str, Any]) -> None:
        states["nurse"]["initial_phase"] = NurseState.IDLE
        states["nurse"]["initial_sigma"] = 10.0  # less than 60 seconds
