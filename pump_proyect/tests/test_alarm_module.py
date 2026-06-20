# tests/test_alarm_module.py
import pytest
from math import inf as infinity

from src.models.alarm_module import (
    AlarmModule,
    AlarmStatus,
    ModuleAlarmStatus,
)

# --- ALARMS ONLY INPUT ---

def test_initial_state():
    alarm = AlarmModule()

    assert alarm.state["alarm_state"] == AlarmStatus.NO_ALARM
    assert alarm.state["hours"] == infinity
    assert alarm.timeAdvance() == infinity

@pytest.mark.parametrize(
    "alarm_status",
    [   
        AlarmStatus.LOW_ALARM,
        AlarmStatus.MEDIUM_ALARM
    ]
)

def test_low_or_medium_alarm_flow(alarm_status):
    alarm = AlarmModule()

    alarm.extTransition({
        alarm.in_alarm: [alarm_status]
    })

    assert alarm.state["alarm_state"] == alarm_status
    assert alarm.timeAdvance() == 0.0

    assert alarm.outputFnc() == {
        alarm.out_alarm:  [alarm_status]
    }

    alarm.intTransition()

    assert alarm.state["alarm_state"] == AlarmStatus.NO_ALARM
    assert alarm.state["hours"] == infinity


def test_correct_transition_to_long_wait():
    alarm = AlarmModule()

    alarm.extTransition({
        alarm.in_alarm: [AlarmStatus.CRITICAL_ALARM]
    })

    # First output
    assert alarm.outputFnc() == {
        alarm.out_alarm: [AlarmStatus.CRITICAL_ALARM]
    }

    # CRITICAL -> LONG_WAIT
    alarm.intTransition()

    assert alarm.state["alarm_state"] == ModuleAlarmStatus.LONG_WAIT
    assert alarm.timeAdvance() == 30.0

    # LONG_WAIT doesnt output anything
    assert alarm.outputFnc() == {}


def test_correct_transition_to_repeat_critical():
    alarm = AlarmModule()

    ## set long wait
    alarm.state = {
        "alarm_state": ModuleAlarmStatus.LONG_WAIT,
        "hours": 30.0
    }

    # LONG_WAIT -> REPEAT_CRITICAL
    alarm.intTransition()

    assert alarm.state["alarm_state"] == ModuleAlarmStatus.REPEAT_CRITICAL
    assert alarm.timeAdvance() == 0.0
    # Second ouput
    assert alarm.outputFnc() == {
        alarm.out_alarm: [AlarmStatus.CRITICAL_ALARM]
    }


def test_correct_transition_to_short_wait():
    alarm = AlarmModule()

    ## set short wait
    alarm.state = {
        "alarm_state": ModuleAlarmStatus.SHORT_WAIT,
        "hours": 10.0
    }

    
    for i in range(10):
        # SHORT_WAIT doesn't output anything
        assert alarm.outputFnc() == {}

        # SHORT_WAIT -> REPEAT_CRITICAL
        alarm.intTransition()
        
        assert alarm.state["alarm_state"] == ModuleAlarmStatus.REPEAT_CRITICAL
        assert alarm.timeAdvance() == 0.0

        # Third output
        assert alarm.outputFnc() == {
            alarm.out_alarm: [AlarmStatus.CRITICAL_ALARM]
        }

        # REPEAT_CRITICAL -> SHORT_WAIT
        alarm.intTransition()

        assert alarm.state["alarm_state"] == ModuleAlarmStatus.SHORT_WAIT
        assert alarm.timeAdvance() == 10.0

    ## and so on until nurse confirmation

def test_from_long_wait_to_short_wait():
    alarm = AlarmModule()

    ## set long wait
    alarm.state = {
        "alarm_state": ModuleAlarmStatus.LONG_WAIT,
        "hours": 30.0
    }

    ## Long wait -> repeat
    alarm.intTransition()

    ## Repeat -> Short wait
    alarm.intTransition()

    assert alarm.state["alarm_state"] == ModuleAlarmStatus.SHORT_WAIT
    assert alarm.timeAdvance() == 10.0


# --- NURSE CONFIRMATION INPUT ---


@pytest.mark.parametrize(
    "alarm_status",
    [   
        AlarmStatus.LOW_ALARM,
        AlarmStatus.MEDIUM_ALARM,
        AlarmStatus.CRITICAL_ALARM
    ]
)

def test_nurse_confirmation_ignored(alarm_status):
    alarm = AlarmModule()

    alarm.state["alarm_state"] = alarm_status

    hours_before = alarm.state["hours"]

    alarm.extTransition({
        alarm.in_nurse_confirmation: [True]
    })

    assert alarm.state["alarm_state"] == alarm_status
    assert alarm.state["hours"] <= hours_before

@pytest.mark.parametrize(
    "module_status",
    [   
        ModuleAlarmStatus.LONG_WAIT,
        ModuleAlarmStatus.SHORT_WAIT,
        ModuleAlarmStatus.REPEAT_CRITICAL,
    ]
)
def test_nurse_confirmation_resets_any_alarm_state(module_status):
    alarm = AlarmModule()

    alarm.state = {
        "alarm_state": module_status,
        "hours": 10.0
    }

    alarm.extTransition({
        alarm.in_nurse_confirmation: [True]
    })

    assert alarm.state["alarm_state"] == AlarmStatus.NO_ALARM
    assert alarm.state["hours"] == infinity



    