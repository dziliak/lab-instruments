"""Protocol tests for the Fluke 8846A driver."""

import pytest
from pymeasure.test import expected_protocol

from lab_instruments.fluke import Fluke8846A

_NO_ERROR = '+0,"No error"'


def test_top_level_export() -> None:
    """Export the driver from the package root."""
    from lab_instruments import Fluke8846A as ExportedFluke8846A

    assert ExportedFluke8846A is Fluke8846A


def test_measure_resistance() -> None:
    """Issue a direct two-wire resistance measurement."""
    protocol = [
        ("MEAS:RES?", "1.23456789E+03"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.resistance == pytest.approx(1234.56789)


def test_read_returns_multiple_samples() -> None:
    """Return a list when READ? produces multiple samples."""
    protocol = [
        ("READ?", "1.0,2.0,3.0"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.reading == [1.0, 2.0, 3.0]


def test_set_and_get_function() -> None:
    """Map friendly function names to quoted SCPI values."""
    protocol = [
        ('FUNC "RES"', None),
        ("SYST:ERR?", _NO_ERROR),
        ("FUNC?", '"VOLTage:DC"'),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        meter.function = "resistance"
        assert meter.function == "voltage_dc"


def test_function_rejects_unknown_value() -> None:
    """Reject unsupported function names before writing to the meter."""
    with expected_protocol(Fluke8846A, []) as meter, pytest.raises(ValueError):
        meter.function = "inductance"


def test_set_resistance_nplc() -> None:
    """Set a supported resistance integration time."""
    protocol = [
        ("RES:NPLC 10", None),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        meter.resistance_nplc = 10


def test_nplc_rejects_unsupported_value() -> None:
    """Reject NPLC values not supported by the meter."""
    with expected_protocol(Fluke8846A, []) as meter, pytest.raises(ValueError):
        meter.resistance_nplc = 5


def test_sample_count_parses_scientific_notation() -> None:
    """Convert a scientific-notation sample count to an integer."""
    protocol = [
        ("SAMP:COUN?", "+2.50000000E+01"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.sample_count == 25


def test_trigger_source_mapping() -> None:
    """Map long and abbreviated trigger source values."""
    protocol = [
        ("TRIG:SOUR EXT", None),
        ("SYST:ERR?", _NO_ERROR),
        ("TRIG:SOUR?", "IMMediate"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        meter.trigger_source = "external"
        assert meter.trigger_source == "immediate"


def test_rtd_type_mapping() -> None:
    """Normalize the abbreviated RTD type returned by the meter."""
    protocol = [
        ("TEMP:RTD:TYP?", "385"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.temperature_2w_rtd_type == "pt100_385"


def test_display_text_quotes_and_unquotes_strings() -> None:
    """Escape embedded quotes and preserve commas in display text."""
    protocol = [
        ('DISP:TEXT "A""B"', None),
        ("SYST:ERR?", _NO_ERROR),
        ("DISP:TEXT?", '"A,B"'),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        meter.display_text = 'A"B'
        assert meter.display_text == "A,B"


def test_display_text_rejects_more_than_twelve_characters() -> None:
    """Reject overlength display messages before writing to the meter."""
    with expected_protocol(Fluke8846A, []) as meter, pytest.raises(ValueError):
        meter.display_text = "thirteen chars"


def test_terminal_mapping() -> None:
    """Map the abbreviated front-terminal response."""
    protocol = [
        ("ROUT:TERM?", "FRON"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.terminal == "front"


def test_fetch_returns_all_stored_readings() -> None:
    """Fetch buffered primary-display readings."""
    protocol = [
        ("FETC?", "1.25,2.5,3.75"),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        assert meter.fetch() == [1.25, 2.5, 3.75]


def test_initiate_and_infinite_trigger_commands() -> None:
    """Issue acquisition commands and check the error queue."""
    protocol = [
        ("INIT", None),
        ("SYST:ERR?", _NO_ERROR),
        ("TRIG:COUN INF", None),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        meter.initiate()
        meter.set_infinite_trigger_count()


def test_check_errors_drains_the_error_queue() -> None:
    """Return all queued errors until the meter reports no error."""
    protocol = [
        ("SYST:ERR?", '-222,"Data out of range"'),
        ("SYST:ERR?", _NO_ERROR),
    ]
    with expected_protocol(Fluke8846A, protocol) as meter:
        errors = meter.check_errors()

    assert len(errors) == 1
    assert int(errors[0][0]) == -222
    assert "Data out of range" in errors[0][1]
