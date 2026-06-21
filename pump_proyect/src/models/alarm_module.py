from enum import Enum
from pypdevs.DEVS import AtomicDEVS
from math import inf as infinity

class AlarmStatus(Enum):
    NO_ALARM = "no_alarm"
    LOW_ALARM = "low_alarm"
    MEDIUM_ALARM = "medium_alarm"
    CRITICAL_ALARM = "critical_alarm"
    SHORT_WAIT = "short_wait"
    LONG_WAIT = "long_wait"
    REPEAT_CRITICAL = "repeat_critical"    

class AlarmModule(AtomicDEVS):
    def __init__(self):
        super().__init__("AlarmModule")

        self.in_alarm = self.addInPort("in_alarm")
        self.in_nurse_confirmation = self.addInPort("in_nurse_confirmation")

        self.out_alarm = self.addOutPort("out_alarm")

        self.state = {
            "alarm_state": AlarmStatus.NO_ALARM,
            "hours": infinity
        }

    def extTransition(self, inputs) -> dict:
        e = self.elapsed

        if self.in_alarm in inputs:
            alarm = inputs[self.in_alarm][0]
            status = alarm.get_status() if hasattr(alarm, "get_status") else alarm

            if status == AlarmStatus.CRITICAL_ALARM:
                self.state["alarm_state"] = AlarmStatus.CRITICAL_ALARM
                self.state["hours"] = 0.0
                return self.state
            elif status in (
                AlarmStatus.LOW_ALARM,
                AlarmStatus.MEDIUM_ALARM
            ):
                self.state["alarm_state"] = status
                self.state["hours"] = 0.0

                return self.state

        elif self.in_nurse_confirmation in inputs:
            if  self.state["alarm_state"] in ( AlarmStatus.LONG_WAIT, AlarmStatus.SHORT_WAIT, AlarmStatus.REPEAT_CRITICAL):
                self.state["alarm_state"] = AlarmStatus.NO_ALARM
                self.state["hours"] = infinity

                return self.state
        
        self.state["hours"] = max(0.0, self.state["hours"] - e)

        return self.state
        

 
    def intTransition(self) -> dict:
        current_state = self.state["alarm_state"]

        if current_state in (
            AlarmStatus.LOW_ALARM,
            AlarmStatus.MEDIUM_ALARM
        ):
            self.state["alarm_state"] = AlarmStatus.NO_ALARM,
            self.state["hours"] = infinity

        elif current_state == AlarmStatus.CRITICAL_ALARM:
            self.state["alarm_state"] = AlarmStatus.LONG_WAIT,
            self.state["hours"] = 30.0

        elif current_state == AlarmStatus.LONG_WAIT:
            self.state["alarm_state"] = AlarmStatus.REPEAT_CRITICAL,
            self.state["hours"] = 0.0001

        elif current_state == AlarmStatus.REPEAT_CRITICAL:
            self.state["alarm_state"] = AlarmStatus.SHORT_WAIT,
            self.state["hours"] = 10.0

        elif current_state == AlarmStatus.SHORT_WAIT:
            self.state["alarm_state"] = AlarmStatus.REPEAT_CRITICAL,
            self.state["hours"] = 0.0001

        return self.state


    def outputFnc(self) -> dict:
        if self.state["alarm_state"] in (
            AlarmStatus.CRITICAL_ALARM,
            AlarmStatus.REPEAT_CRITICAL
        ):
            return {
                self.out_alarm: [AlarmStatus.CRITICAL_ALARM]
            }

        elif self.state["alarm_state"] in (
            AlarmStatus.LOW_ALARM,
            AlarmStatus.MEDIUM_ALARM
        ):
            return {
                self.out_alarm: [self.state["alarm_state"]]
            }

        return {}

    def timeAdvance(self) -> float:
        return self.state["hours"]