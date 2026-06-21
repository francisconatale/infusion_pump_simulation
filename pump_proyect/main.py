from pypdevs.simulator import Simulator

from src.pump_system import PumpSystem
from src.utils.initial_states_factory import InitialStatesFactory


def main():
    client_criticality = 0.95

    # Obtener el estado inicial para el escenario deseado desde la factory.
    # Escenarios disponibles: "default", "alarma_critica", "tolerancia_excedida"
    scenario_name = "default"
    initial_states = InitialStatesFactory.get_initial_state(scenario_name)

    model = PumpSystem(
        client_criticality=client_criticality,
        initial_states=initial_states
    )

    sim = Simulator(model)
    sim.setTerminationTime(100000)
    sim.simulate()

if __name__ == "__main__":
    main()
