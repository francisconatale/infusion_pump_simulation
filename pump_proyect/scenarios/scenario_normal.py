from src.pump_system import PumpSystem


def build_model():
    return PumpSystem(
        client_criticality=0.95
    )