import shutil

from pypdevs.simulator import Simulator
from src.pump_system import PumpSystem

SCENARIOS = ["normal",
    "order_change",
    "stop_order"]
    
def run():
    for scenario in SCENARIOS:
        model = PumpSystem(0.95, scenario)

        sim = Simulator(model)
        sim.setTerminationTime(10000)
        sim.simulate()

        shutil.move(
            "resultados.csv",
            f"docs/{scenario}.csv"
        )

if __name__ == "__main__":
    run()