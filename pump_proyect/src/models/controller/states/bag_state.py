from enum import Enum

class BagStatus(Enum):
    NORMAL_BAG = "normal_bag"
    END_BAG = "end_bag"
    EMPTY_BAG = "empty_bag"
    AWAIT_STOP_BAG = "await_stop_bag"

class BagState:
    def __init__(self, status=BagStatus.NORMAL_BAG, time_to_empty_bag=float('inf')):
        self.status = status
        self.time_to_empty_bag = time_to_empty_bag

    def change_status(self, new_status):
        self.status = new_status

    def update_time(time):
        self.time_to_empty_bag = time_to_empty_bag + time
    
    def get_time_to_empty(self):
        return self.time_to_empty_bag
        
    def get_snapshot(self):
        return deepcopy(self.status)
    
    def get_status(self):
        return self.status  

    def awaiting_stop_bag(self):
        return self.status == BagStatus.AWAIT_STOP_BAG
