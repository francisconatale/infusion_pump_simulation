from pypdevs.DEVS import AtomicDEVS
from src.utils.random_utils import hours_to_seconds
from src.utils.random_utils import RandomGenerator
from math import inf as infinity

class Logger(AtomicDEVS):
    def __init__(self):
        super().__init__("Logger")
        self.in_state_control = self.addInPort("in_state_control")
        
        # Write events in real time to a CSV file
        self.log_file = open("resultados.csv", "w")
        self.state = {
            "list_of_events": [],
            "accumulated_time": 0.0}

    def extTransition(self, inputs):
        e = self.elapsed

        self.state["accumulated_time"] += e
        
        new_event = inputs[self.in_state_control] if self.in_state_control in inputs else None
        
        self.state["list_of_events"].append((self.state["accumulated_time"], new_event))

        if self.in_state_control in inputs:
            data = inputs[self.in_state_control]
            
            self.log_file.write(f"{self.state['accumulated_time']}, {data}\n")
            
        return self.state

    def timeAdvance(self):
        """Time advance: always wait for next external event."""
        return infinity 
    
    
