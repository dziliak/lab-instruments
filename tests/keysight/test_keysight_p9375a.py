import pytest
from pymeasure.test import expected_protocol

from lab_instruments.keysight import KeysightP9375A


def test_frequency_range_protocol():
    with expected_protocol(
        KeysightP9375A,
        [
            (":SENS1:FREQ:START 1000000Hz", None),
            (":SENS1:FREQ:STOP 9000000000Hz", None),
            (":SENS1:FREQ:START?", "1000000"),
            (":SENS1:FREQ:STOP?", "9000000000"),
        ],
    ) as analyzer:
        analyzer.start_frequency = 1e6
        analyzer.stop_frequency = 9e9
        assert analyzer.start_frequency == 1e6
        assert analyzer.stop_frequency == 9e9


@pytest.mark.parametrize("property_name", ["start_frequency", "stop_frequency"])
def test_frequency_range_validation(property_name):
    with expected_protocol(KeysightP9375A, []) as analyzer, pytest.raises(ValueError):
        setattr(analyzer, property_name, 299999)
