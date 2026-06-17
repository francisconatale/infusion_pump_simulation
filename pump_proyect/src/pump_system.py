import src.utils.utils as Utils

class PumpSystem(CoupledDEVS):

    def __init__(self, client_criticality=1.0):
        super().__init__("PumpSystem")
        self.client_criticality = client_criticality
