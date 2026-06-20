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


def test_low_alarm_flow():
    alarm = AlarmModule()

    alarm.extTransition({
        alarm.in_alarm: [AlarmStatus.LOW_ALARM]
    })

    assert alarm.state["alarm_state"] == AlarmStatus.LOW_ALARM
    assert alarm.timeAdvance() == 0.0

    assert alarm.outputFnc() == {
        alarm.out_alarm: [AlarmStatus.LOW_ALARM]
    }

    alarm.intTransition()

    assert alarm.state["alarm_state"] == AlarmStatus.NO_ALARM
    assert alarm.state["hours"] == infinity


def test_medium_alarm_flow():
    alarm = AlarmModule()

    alarm.extTransition({
        alarm.in_alarm: [AlarmStatus.MEDIUM_ALARM]
    })

    assert alarm.state["alarm_state"] == AlarmStatus.MEDIUM_ALARM
    assert alarm.timeAdvance() == 0.0

    assert alarm.outputFnc() == {
        alarm.out_alarm: [AlarmStatus.MEDIUM_ALARM]
    }

    alarm.intTransition()

    assert alarm.state["alarm_state"] == AlarmStatus.NO_ALARM
    assert alarm.state["hours"] == infinity


def test_critical_alarm_cycle():
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

    # LONG_WAIT -> REPEAT_CRITICAL
    alarm.intTransition()

    assert alarm.state["alarm_state"] == ModuleAlarmStatus.REPEAT_CRITICAL
    assert alarm.timeAdvance() == 0.0

    # Second ouput
    assert alarm.outputFnc() == {
        alarm.out_alarm: [AlarmStatus.CRITICAL_ALARM]
    }

    # REPEAT_CRITICAL -> SHORT_WAIT
    alarm.intTransition()

    assert alarm.state["alarm_state"] == ModuleAlarmStatus.SHORT_WAIT
    assert alarm.timeAdvance() == 10.0

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

    ## and so on until nurse confirmation

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



    