from pypdevs.DEVS import AtomicDEVS
class SensorFlow(AtomicDEVS):
    def __init__(self):
        super().__init__("SensorFlow")

        self.out_flow_measurement = self.addOutPort("out_flow_measurement")
