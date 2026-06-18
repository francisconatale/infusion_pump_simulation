from enum import Enum
from flow_state import FlowState, FlowStatus
from bag_state import BagState, FlowStatus

class PumpController(AtomicDEVS):

    def __init__(self, max_tolerance_exceedance_seconds=5):
        super().__init__("PumpController")
        self.max_tolerance_exceedance_seconds = max_tolerance_exceedance_seconds

        self.margin_tolerance =  0.1
        self.in_medical_order = self.addInPort("in_medical_order")
        self.in_end_bag = self.addInPort("in_end_bag")
        self.in_sensor_flow = self.addInPort("in_sensor_flow")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")
        self.out_adjust_flow = self.addOutPort("out_adjust_flow")
        self.out_turn_off_bomb = self.addOutPort("out_turn_off_bomb")
        self.out_alarm = self.addOutPort("out_alarm")
        self.out_log = self.addOutPort("out_log")
        self.state = {FlowState: FlowState(NORMAL_STATUS), BagState: BagState(NORMAL_BAG, float('inf')), "exceeded_tolerance_count": 0, last_sensor_medition: 0, objetive: 0, actions: []}

    def tolerance_exceeded(self, last_sensor_medition, objetive):
        return (abs(last_sensor_medition - objetive)) / objetive > self.margin_tolerance
    
    def intTransition(self):
        



    