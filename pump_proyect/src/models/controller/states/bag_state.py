from enum import Enum

class BagStatus(Enum):
    NORMAL_BAG = "normal_bag"
    END_BAG = "end_bag"
    EMPTY_BAG = "empty_bag"

class BagState:
    def __init__(self, status=BagStatus.NORMAL_BAG, time_to_empty_bag=float('inf')):
        self.status = status
        self.time_to_empty_bag = time_to_empty_bag
    def change_status(self, new_status):
        self.status = new_status

    def update_time_to_empty(self, time):
        self.time_to_empty_bag = time 
