from src.utils.medical_order_factory.parametrized_distribution import ParametrizedDistribution


class ServiceDurationDistribution(ParametrizedDistribution):
    """
    Default distribution for service/attention durations (in hours).

    This class implements `ParametrizedDistribution` and provides a sensible
    default table. Implementers can subclass or instantiate with custom tables.

    Usage:
        d = ServiceDurationDistribution(client_critical=0.7)
        t = d.next_interval_hours()  # returns duration in hours
    """

    def __init__(self, client_critical):
        values = [2, 4, 6, 8, 12]
        pc = [0.50, 0.30, 0.15, 0.05, 0.00]
        pe = [0.00, 0.05, 0.15, 0.40, 0.40]
        super().__init__(client_critical, values, pc, pe)
