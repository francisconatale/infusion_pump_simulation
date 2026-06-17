from src.utils.medical_order_factory.parametrized_distribution import ParametrizedDistribution


class MLGenerator(ParametrizedDistribution):
    """
    Generator for infusion flow rate (caudal) in ml/h.

    This class implements `ParametrizedDistribution` using the discrete table
    defined in the project specification (Table 2).

    Values and tables are:
      values = [0, 50, 100, 150, 200]  (ml/h)
      pc = [0.00, 0.10, 0.20, 0.40, 0.30]  (critical patient)
      pe = [0.30, 0.35, 0.20, 0.10, 0.05]  (stable patient)

    Usage:
        g = MLGenerator(client_critical=0.7)
        flow = g.next_interval_hours()  # returns flow rate in ml/h
    """

    def __init__(self, client_critical):
        values = [0, 50, 100, 150, 200]
        pc = [0.00, 0.10, 0.20, 0.40, 0.30]
        pe = [0.30, 0.35, 0.20, 0.10, 0.05]
        super().__init__(client_critical, values, pc, pe)
