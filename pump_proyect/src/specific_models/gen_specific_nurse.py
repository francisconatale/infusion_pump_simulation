from math import inf as infinity

from src.models.gen_nurse import GeneratorNurseConfirmation
from src.models.gen_bag_end import BagState


class SpecificNurseConfirmation(
    GeneratorNurseConfirmation):

    def __init__(self, confirmation_time):
        super().__init__()
        self.confirmation_time = confirmation_time

    def time_advance(self):
        return self.confirmation_time