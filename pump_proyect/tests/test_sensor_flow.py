import pytest
from pypdevs.simulator import Simulator

from src.models.sensor_flow import SensorFlow

def test_output_ever_1_second_without_other_inputs():
    sensor = SensorFlow()
    
    sensor.extTransition({sensor.in_actuator: [123.456]})
    for i in range(10):
        sensor.outputFnc()
        sensor.intTransition()
        assert sensor.timeAdvance() == 1.0


def test_persistent_temp():
    sensor = SensorFlow()
    
    assert sensor.timeAdvance() == float("inf") or sensor.timeAdvance() == 1.0

    sensor.intTransition()
    assert sensor.state["sigma"] == 1.0

def test_last_input_is_output():
    sensor = SensorFlow()

    
    sensor.extTransition({sensor.in_actuator: [100.0]})

    sensor.extTransition({sensor.in_actuator: [150.0]})

    # internal state is the same as last input
    assert sensor.state["current_flow"] == 150.0

    
    output = sensor.outputFnc()
    assert output[sensor.out_flow_measurement][0] == 150.0

def test_presition_flow():
    sensor = SensorFlow()

    # Simular entrada de caudal exacto
    state = sensor.extTransition({sensor.in_actuator: [123.456]})

    assert state["current_flow"] == 123.456

    output = sensor.outputFnc()
    assert output[sensor.out_flow_measurement][0] == 123.456

def test_detects_changes():
    sensor = SensorFlow()

    # normal
    state = sensor.extTransition({sensor.in_actuator: [50]})
    
    assert state["current_flow"] == 50

    # medium
    state = sensor.extTransition({sensor.in_actuator: [120]})
    assert state["current_flow"] == 120

    # critical
    state = sensor.extTransition({sensor.in_actuator: [200]})
    assert state["current_flow"] == 200

