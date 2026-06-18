from pypdevs.DEVS import AtomicDEVS
from src.utils.medical_order_factory.factory_medical_order import MedicalOrderFactory


class MedicalOrderGenerator(AtomicDEVS):
	"""DEVS Generator for medical orders.
	
	Emits medical orders (hours, ml) tuples at regular intervals determined
	by the MedicalOrderFactory parametrized by client criticality.
	
	Ports:
	  - out_order: output port emitting (hours_interval, flow_ml_h) tuples
	
	Usage:
	  gen = MedicalOrderGenerator(client_criticality=k)
	  # In DEVS simulation, will emit orders on 'out_order' port
	"""

	def __init__(self, client_criticality=1.0):
		super().__init__("MedicalOrderGenerator")

		self.out_order = self.addOutPort("out_order")

		self.factory = MedicalOrderFactory(client_criticality)

		self.current_order = self.factory.next_order()
		self.hours_interval, self.ml_flow = self.current_order

		self.state = {
			"order": self.current_order,
			"hours": self.hours_interval,
			"ml": self.ml_flow
		}
		
	def intTransition(self):
		"""Internal transition: generate next order."""
		self.current_order = self.factory.next_order()
		self.hours_interval, self.ml_flow = self.current_order

		self.state = {
        	"order": self.current_order,
        	"hours": self.hours_interval,
        	"ml": self.ml_flow
    	}
		return self.state
	
	def outputFnc(self):
		"""Output: emit the current order tuple."""
		print("OUTPUT:", self.state)
		return {
            self.out_order: self.state["order"]
        }
	
	def timeAdvance(self):
		"""Time advance: hours until next order."""
		return self.hours_interval
	
