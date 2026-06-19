from pypdevs.DEVS import AtomicDEVS
from math import inf as infinity

class Logger(AtomicDEVS):
    def __init__(self):
        super().__init__("Logger")
        self.in_state_control = self.addInPort("in_state_control")

        self.log_file = open("resultados.csv", "w", encoding="utf-8")
        self.state = {
            "accumulated_time": 0.0,
            "last_event_count": 0
        }

    def extTransition(self, inputs) -> dict:
        e = self.elapsed
        self.state["accumulated_time"] += e

        if self.in_state_control in inputs:
            data = inputs[self.in_state_control]
            self.state["last_event_count"] += 1
            self.log_file.write(f"{self.state['accumulated_time']}, {data}\n")
            self.log_file.flush()

        return self.state

    def intTransition(self) -> dict:
        return self.state

    def timeAdvance(self) -> float:
        return infinity

    def __del__(self):
        if hasattr(self, "log_file") and self.log_file:
            self.log_file.close()

    
    
