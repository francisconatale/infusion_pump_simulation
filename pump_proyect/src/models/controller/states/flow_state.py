from enum import Enum

class FlowStatus(Enum):
    NORMAL_STATUS = "normal_flow"
    MEDIUM_STATUS = "medium_flow"
    CRITICAL_STATUS = "critical_flow"

class FlowState:
    def __init__(self, status=FlowStatus.NORMAL_STATUS):
        self.status = status

    def change_status(self, new_status):
        self.status = new_status