from pypdevs.simulator import Simulator

from src.pump_system import PumpSystem
from src.utils.random_utils import RandomGenerator
from src.constants import CLIENT_CRITICALITY


def main():
    client_criticality = RandomGenerator.get_uniform(0,1) # 1 = critical, 0 = stable, 0 < x < 0.5 = low risk, 0.5 < x < 1 = high risk
    model = PumpSystem(client_criticality=client_criticality)

    sim = Simulator(model)
    sim.setVerbose(None)
    sim.simulate()

if __name__ == "__main__":
    main()
