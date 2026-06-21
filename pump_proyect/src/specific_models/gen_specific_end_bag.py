from math import inf as infinity

from src.models.gen_bag_end import EndBagGenerator
from src.models.gen_bag_end import BagState


class SpecificBagGenerator(EndBagGenerator):

    def __init__(self, end_bag_time=100):
        super().__init__()

        self.name = "SpecificBagGenerator"
        self.end_bag_time = end_bag_time

    def time_bag(self) -> float:
        """
        Tiempo fijo para testing.

        Ejemplo:
            end_bag_time = 100

        => el evento end_bag ocurrirá exactamente
           a los 100 segundos desde que comienza
           una infusión activa.
        """
        return self.end_bag_time