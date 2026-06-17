from src.utils.random_utils import RandomGenerator
from pypdevs.DEVS import AtomicDEVS

class ParametrizedDistribution(AtomicDEVS):
	"""
	Parametrized discrete distribution for time between medical orders.

	Each implementer must provide their discrete tables: `values`, `pc`, and `pe`.

	Constructor:
		ParametrizedDistribution(client_critical, values, pc, pe)

	- `client_critical`: float in [0,1]
	- `values`: list of discrete values (e.g. [2,4,6,8,12])
	- `pc`: list of probabilities for the critical case (same length as `values`)
	- `pe`: list of probabilities for the stable case (same length as `values`)
	"""

	def __init__(self, client_critical, values, pc, pe):
		# require implementer-provided tables
		if values is None or pc is None or pe is None:
			raise ValueError("ParametrizedDistribution requires values, pc and pe tables")
		if not (len(values) == len(pc) == len(pe)):
			raise ValueError("values, pc and pe must have the same length")

		self.client_critical = client_critical
		self.values = list(values)
		self.pc = list(pc)
		self.pe = list(pe)

	def next_interval_hours(self):
		"""Return the next interval T in hours according to the parametric criticality and provided tables."""
		return RandomGenerator.sample_mixture(self.client_critical, self.values, self.pc, self.pe)

	def get_interval_probabilities(self):
		"""Return (values, probabilities) mixed according to criticality.

		Useful for mapping these probabilities to service/attention times
		using external rules.
		"""
		probs = RandomGenerator.mixture_probabilities(self.client_critical, self.pc, self.pe)
		return list(self.values), probs
