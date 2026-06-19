from pypdevs.simulator import Simulator

from src.pump_system import PumpSystem
from src.utils.random_utils import RandomGenerator
from src.constants import CLIENT_CRITICALITY


def main():
    client_criticality = 0.95
    model = PumpSystem(client_criticality=client_criticality)

    sim = Simulator(model)
    sim.setTerminationTime(100000)
    sim.simulate()

if __name__ == "__main__":
    main()
