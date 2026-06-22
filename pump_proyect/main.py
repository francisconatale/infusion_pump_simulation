import os
from pypdevs.simulator import Simulator

from src.pump_system import PumpSystem
from src.scenarios.initial_states_factory import InitialStatesFactory


class Scenario:
    def __init__(self, name: str, initial_state_name: str, duration: float, client_criticality: float):
        self.name = name
        self.initial_state_name = initial_state_name
        self.duration = duration
        self.client_criticality = client_criticality


def run_scenario(scenario: Scenario):
    print(f"\n{'='*50}")
    print(f"Iniciando escenario: {scenario.name}")
    print(f"Duracion: {scenario.duration} | Criticidad: {scenario.client_criticality}")
    print(f"{'='*50}")

    initial_states = InitialStatesFactory.get_initial_state(scenario.initial_state_name)
    
    # Creamos el directorio para este escenario
    output_dir = f"resultados/{scenario.name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Asignamos el log dentro de esa carpeta
    initial_states["logger"]["log_filename"] = f"{output_dir}/resultados.csv"

    model = PumpSystem(
        client_criticality=scenario.client_criticality,
        initial_states=initial_states
    )

    sim = Simulator(model)
    sim.setTerminationTime(scenario.duration)
    sim.simulate()
    
    print(f"Escenario '{scenario.name}' finalizado.\n")


def main():
    scenarios = [
        Scenario(
            name="flujo_normal_corto",
            initial_state_name="default",
            duration=1000,
            client_criticality=0.95
        ),
        Scenario(
            name="paciente_critico_alarma",
            initial_state_name="alarma_critica",
            duration=500,
            client_criticality=0.99
        ),
        Scenario(
            name="falla_tolerancia",
            initial_state_name="tolerancia_excedida",
            duration=2000,
            client_criticality=0.80
        ),
        Scenario(
            name="flujo_normal_10_horas",
            initial_state_name="default",
            duration=36000,
            client_criticality=0.95
        ),

        Scenario(
            name="orden_medica_cero",
            initial_state_name="orden_medica_cero",
            duration=1000,
            client_criticality=0.95
        ),
        
        Scenario(
            name="orden_medica_cambio",
            initial_state_name="orden_medica_cambio",
            duration=1000,
            client_criticality=0.95
        ),

        Scenario(
            name="fin_bolsa_por_60_segundos",
            initial_state_name="fin_bolsa_por_60_segundos",
            duration=500,
            client_criticality=0.95
        ),

        Scenario(
            name="fin_bolsa_menos_de_60_segundos",
            initial_state_name="fin_bolsa_menos_de_60_segundos",
            duration=500,
            client_criticality=0.95
        ),
        Scenario(
            name= "alarma_critica_no_confirmada_por_mas_30_segundos",
            initial_state_name="alarma_critica_no_confirmada_por_mas_30_segundos",
            duration = 500,
            client_criticality=0.95),
            
        Scenario(
            name="desvio_leve_corregido",
            initial_state_name="desvio_leve_corregido",
            duration=1000,
            client_criticality=0.95
        ),

        Scenario(
            name="desvio_mayor_alarma",
            initial_state_name="desvio_mayor_alarma",
            duration=1000,
            client_criticality=0.95
        )
    ]

    for scenario in scenarios:
        run_scenario(scenario)


if __name__ == "__main__":
    main()

