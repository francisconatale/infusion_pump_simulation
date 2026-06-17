from src.utils.medical_order_factory.service_duration_distribution import ServiceDurationDistribution
from src.utils.medical_order_factory.ml_generator import MLGenerator


class MedicalOrderFactory:
	"""Factory for medical orders that combines two DEVS generators.
	
	Uses ServiceDurationDistribution (hours interval) and MLGenerator (flow rate)
	to build complete medical orders parametrized by client criticality.
	
	Usage:
	  order_factory = MedicalOrderFactory(client_critical=0.7)
	  hours, ml = order_factory.next_order()  # returns (interval hours, flow ml/h)
	"""

	def __init__(self, client_critical):
		self.service_duration = ServiceDurationDistribution(client_critical)
		self.ml_generator = MLGenerator(client_critical)

	def next_order(self):
		"""Generate next medical order: returns (hours_until_next, flow_ml_h)."""
		hours = self.service_duration.next_interval_hours()
		ml = self.ml_generator.next_interval_hours()
		return (hours, ml)


