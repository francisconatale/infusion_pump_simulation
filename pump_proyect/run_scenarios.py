import shutil

from pypdevs.simulator import Simulator

from scenarios.scenario_normal import build_model as normal
from scenarios.scenario_order_change import build_model as order_change
from scenarios.scenario_stop_order import build_model as stop_order

SCENARIOS = {
    "normal": normal,
    "order_change": order_change,
    "stop_order": stop_order,
}

def run():
    for scenario_name, builder in SCENARIOS.items():
        model = builder()

        sim = Simulator(model)
        sim.setTerminationTime(1000)
        sim.simulate()

        shutil.move(
            "resultados.csv",
            f"docs/{scenario_name}.csv"
        )

if __name__ == "__main__":
    run()