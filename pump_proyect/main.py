from pypdevs.simulator import Simulator

from src.pump_system import PumpSystem


def main():
    model = PumpSystem()

    sim = Simulator(model)

    sim.setVerbose(None)

    sim.simulate()


if __name__ == "__main__":
    main()
