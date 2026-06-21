from src.pump_system import PumpSystem

def build_model():
    return PumpSystem(
        client_criticality=0.95,

        medical_order_generator_kwargs={
            "active": False,
            "orders": [
                (0, 50),
                (100, 0)
            ]
        }
    )