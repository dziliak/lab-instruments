"""PyMeasure driver for the Fluke 8846A digital multimeter."""

from __future__ import annotations

from typing import Any

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

_BOOLEAN_VALUES = {True: 1, False: 0}
_NPLC_VALUES = (0.02, 0.2, 1, 10, 100)
_APERTURE_VALUES = (0.01, 0.1, 1.0)
_BANDWIDTH_VALUES = (3, 20, 200)

_FUNCTION_VALUES = {
    "capacitance": '"CAP"',
    "continuity": '"CONT"',
    "current_ac": '"CURR:AC"',
    "current_dc": '"CURR:DC"',
    "diode": '"DIOD"',
    "frequency": '"FREQ"',
    "period": '"PER"',
    "resistance": '"RES"',
    "resistance_4w": '"FRES"',
    "temperature_2w": '"TEMP:RTD"',
    "temperature_4w": '"TEMP:FRTD"',
    "voltage_ac": '"VOLT:AC"',
    "voltage_dc": '"VOLT:DC"',
    "voltage_ratio": '"VOLT:DC:RAT"',
}

_TRIGGER_SOURCE_VALUES = {
    "bus": "BUS",
    "external": "EXT",
    "immediate": "IMM",
}

_TEMPERATURE_UNIT_VALUES = {
    "celsius": "C",
    "fahrenheit": "F",
    "kelvin": "K",
}

_RTD_TYPE_VALUES = {
    "pt100_385": "PT100_385",
    "pt100_392": "PT100_392",
    "custom": "CUST1",
}

_TERMINAL_VALUES = {
    "front": "FRON",
    "rear": "REAR",
}


def _normalize_function_reply(value: Any) -> str:
    """Normalize a function query reply to the driver's mapped SCPI value."""
    text = str(value).strip().strip("\"'").upper()
    aliases = {
        "CAP": "CAP",
        "CAPACITANCE": "CAP",
        "CONT": "CONT",
        "CONTINUITY": "CONT",
        "CURR:AC": "CURR:AC",
        "CURRENT:AC": "CURR:AC",
        "CURR:DC": "CURR:DC",
        "CURRENT:DC": "CURR:DC",
        "DIOD": "DIOD",
        "DIODE": "DIOD",
        "FREQ": "FREQ",
        "FREQUENCY": "FREQ",
        "PER": "PER",
        "PERIOD": "PER",
        "RES": "RES",
        "RESISTANCE": "RES",
        "FRES": "FRES",
        "FRESISTANCE": "FRES",
        "TEMP:RTD": "TEMP:RTD",
        "TEMPERATURE:RTD": "TEMP:RTD",
        "TEMP:FRTD": "TEMP:FRTD",
        "TEMPERATURE:FRTD": "TEMP:FRTD",
        "VOLT:AC": "VOLT:AC",
        "VOLTAGE:AC": "VOLT:AC",
        "VOLT:DC": "VOLT:DC",
        "VOLTAGE:DC": "VOLT:DC",
        "VOLT:DC:RAT": "VOLT:DC:RAT",
        "VOLT:DC:RATIO": "VOLT:DC:RAT",
        "VOLTAGE:DC:RATIO": "VOLT:DC:RAT",
    }
    try:
        return f'"{aliases[text]}"'
    except KeyError as exc:
        raise ValueError(f"Unknown Fluke 8846A function reply: {value!r}") from exc


def _normalize_trigger_source(value: Any) -> str:
    """Normalize a trigger source reply to BUS, EXT, or IMM."""
    text = str(value).strip().upper()
    return {
        "BUS": "BUS",
        "EXT": "EXT",
        "EXTERNAL": "EXT",
        "IMM": "IMM",
        "IMMEDIATE": "IMM",
    }.get(text, text)


def _normalize_temperature_unit(value: Any) -> str:
    """Normalize a temperature unit reply to C, F, or K."""
    text = str(value).strip().upper()
    return {
        "C": "C",
        "CEL": "C",
        "CELSIUS": "C",
        "F": "F",
        "FAR": "F",
        "FAHRENHEIT": "F",
        "K": "K",
        "KEL": "K",
        "KELVIN": "K",
    }.get(text, text)


def _normalize_rtd_type(value: Any) -> str:
    """Normalize an RTD type query reply to its set-command value."""
    text = str(value).strip().upper()
    return {
        "385": "PT100_385",
        "PT100_385": "PT100_385",
        "392": "PT100_392",
        "PT100_392": "PT100_392",
        "CUST1": "CUST1",
        "CUSTOM": "CUST1",
    }.get(text, text)


def _normalize_terminal(value: Any) -> str:
    """Normalize a terminal query reply to FRON or REAR."""
    text = str(value).strip().upper()
    return "FRON" if text == "FRONT" else text


def _unquote_scpi_string(reply: str) -> str:
    """Remove matching SCPI string delimiters and unescape doubled quotes."""
    text = reply.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        quote = text[0]
        return text[1:-1].replace(quote * 2, quote)
    return text


def _validate_display_text(value: Any, _: Any) -> str:
    """Validate and quote text for the 12-character front-panel display."""
    text = str(value)
    if len(text) > 12:
        raise ValueError("Fluke 8846A display text is limited to 12 characters")
    return f'"{text.replace(chr(34), chr(34) * 2)}"'


class Fluke8846A(SCPIMixin, Instrument):
    """Control a Fluke 8846A through any compatible PyMeasure adapter."""

    function = Instrument.control(
        "FUNC?",
        "FUNC %s",
        """Control the primary measurement function (string).""",
        validator=strict_discrete_set,
        values=_FUNCTION_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_function_reply,
        check_get_errors=True,
        check_set_errors=True,
    )

    voltage_dc = Instrument.measurement(
        "MEAS:VOLT:DC?",
        """Measure DC voltage in volts.""",
        check_get_errors=True,
    )
    voltage_ac = Instrument.measurement(
        "MEAS:VOLT:AC?",
        """Measure AC voltage in volts.""",
        check_get_errors=True,
    )
    voltage_ratio = Instrument.measurement(
        "MEAS:VOLT:DC:RAT?",
        """Measure the DC input-to-reference voltage ratio.""",
        check_get_errors=True,
    )
    current_dc = Instrument.measurement(
        "MEAS:CURR:DC?",
        """Measure DC current in amperes.""",
        check_get_errors=True,
    )
    current_ac = Instrument.measurement(
        "MEAS:CURR:AC?",
        """Measure AC current in amperes.""",
        check_get_errors=True,
    )
    resistance = Instrument.measurement(
        "MEAS:RES?",
        """Measure two-wire resistance in ohms.""",
        check_get_errors=True,
    )
    resistance_4w = Instrument.measurement(
        "MEAS:FRES?",
        """Measure four-wire resistance in ohms.""",
        check_get_errors=True,
    )
    frequency = Instrument.measurement(
        "MEAS:FREQ?",
        """Measure frequency in hertz.""",
        check_get_errors=True,
    )
    period = Instrument.measurement(
        "MEAS:PER?",
        """Measure period in seconds.""",
        check_get_errors=True,
    )
    capacitance = Instrument.measurement(
        "MEAS:CAP?",
        """Measure capacitance in farads.""",
        check_get_errors=True,
    )
    temperature_2w = Instrument.measurement(
        "MEAS:TEMP:RTD?",
        """Measure temperature using a two-wire RTD.""",
        check_get_errors=True,
    )
    temperature_4w = Instrument.measurement(
        "MEAS:TEMP:FRTD?",
        """Measure temperature using a four-wire RTD.""",
        check_get_errors=True,
    )
    diode = Instrument.measurement(
        "MEAS:DIOD?",
        """Measure the diode forward voltage in volts.""",
        check_get_errors=True,
    )
    continuity = Instrument.measurement(
        "MEAS:CONT?",
        """Measure continuity resistance in ohms.""",
        check_get_errors=True,
    )

    reading = Instrument.measurement(
        "READ?",
        """Measure using the current configuration and get one or more readings.""",
        check_get_errors=True,
    )
    last_reading = Instrument.measurement(
        "FETC3?",
        """Get the most recent primary-display reading.""",
        check_get_errors=True,
    )
    stored_reading_count = Instrument.measurement(
        "DATA:POIN?",
        """Get the number of readings stored in internal memory.""",
        get_process=int,
        check_get_errors=True,
    )

    voltage_dc_range = Instrument.control(
        "VOLT:DC:RANG?",
        "VOLT:DC:RANG %.12g",
        """Control the DC voltage range in volts (float strictly from 0 to 1000).""",
        validator=strict_range,
        values=(0.0, 1000.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_dc_autorange = Instrument.control(
        "VOLT:DC:RANG:AUTO?",
        "VOLT:DC:RANG:AUTO %d",
        """Control whether DC voltage autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_ac_range = Instrument.control(
        "VOLT:AC:RANG?",
        "VOLT:AC:RANG %.12g",
        """Control the AC voltage range in volts (float strictly from 0 to 750).""",
        validator=strict_range,
        values=(0.0, 750.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_ac_autorange = Instrument.control(
        "VOLT:AC:RANG:AUTO?",
        "VOLT:AC:RANG:AUTO %d",
        """Control whether AC voltage autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_dc_range = Instrument.control(
        "CURR:DC:RANG?",
        "CURR:DC:RANG %.12g",
        """Control the DC current range in amperes (float strictly from 0 to 10).""",
        validator=strict_range,
        values=(0.0, 10.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    current_dc_autorange = Instrument.control(
        "CURR:DC:RANG:AUTO?",
        "CURR:DC:RANG:AUTO %d",
        """Control whether DC current autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_ac_range = Instrument.control(
        "CURR:AC:RANG?",
        "CURR:AC:RANG %.12g",
        """Control the AC current range in amperes (float strictly from 0 to 10).""",
        validator=strict_range,
        values=(0.0, 10.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    current_ac_autorange = Instrument.control(
        "CURR:AC:RANG:AUTO?",
        "CURR:AC:RANG:AUTO %d",
        """Control whether AC current autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_range = Instrument.control(
        "RES:RANG?",
        "RES:RANG %.12g",
        """Control the two-wire resistance range in ohms.""",
        validator=strict_range,
        values=(0.0, 1e9),
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_autorange = Instrument.control(
        "RES:RANG:AUTO?",
        "RES:RANG:AUTO %d",
        """Control whether two-wire resistance autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_4w_range = Instrument.control(
        "FRES:RANG?",
        "FRES:RANG %.12g",
        """Control the four-wire resistance range in ohms.""",
        validator=strict_range,
        values=(0.0, 1e9),
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_4w_autorange = Instrument.control(
        "FRES:RANG:AUTO?",
        "FRES:RANG:AUTO %d",
        """Control whether four-wire resistance autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    capacitance_range = Instrument.control(
        "CAP:RANG?",
        "CAP:RANG %.12g",
        """Control the capacitance range in farads.""",
        validator=strict_range,
        values=(0.0, 0.1),
        check_get_errors=True,
        check_set_errors=True,
    )
    capacitance_autorange = Instrument.control(
        "CAP:RANG:AUTO?",
        "CAP:RANG:AUTO %d",
        """Control whether capacitance autoranging is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )

    voltage_dc_nplc = Instrument.control(
        "VOLT:DC:NPLC?",
        "VOLT:DC:NPLC %.12g",
        """Control DC voltage integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_dc_nplc = Instrument.control(
        "CURR:DC:NPLC?",
        "CURR:DC:NPLC %.12g",
        """Control DC current integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_nplc = Instrument.control(
        "RES:NPLC?",
        "RES:NPLC %.12g",
        """Control two-wire resistance integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    resistance_4w_nplc = Instrument.control(
        "FRES:NPLC?",
        "FRES:NPLC %.12g",
        """Control four-wire resistance integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_2w_nplc = Instrument.control(
        "TEMP:RTD:NPLC?",
        "TEMP:RTD:NPLC %.12g",
        """Control two-wire RTD integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_4w_nplc = Instrument.control(
        "TEMP:FRTD:NPLC?",
        "TEMP:FRTD:NPLC %.12g",
        """Control four-wire RTD integration time in power-line cycles.""",
        validator=strict_discrete_set,
        values=_NPLC_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )

    frequency_aperture = Instrument.control(
        "FREQ:APER?",
        "FREQ:APER %.12g",
        """Control the frequency gate time in seconds.""",
        validator=strict_discrete_set,
        values=_APERTURE_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    period_aperture = Instrument.control(
        "PER:APER?",
        "PER:APER %.12g",
        """Control the period gate time in seconds.""",
        validator=strict_discrete_set,
        values=_APERTURE_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_ac_bandwidth = Instrument.control(
        "VOLT:AC:BAND?",
        "VOLT:AC:BAND %d",
        """Control the AC voltage filter bandwidth in hertz.""",
        validator=strict_discrete_set,
        values=_BANDWIDTH_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    current_ac_bandwidth = Instrument.control(
        "CURR:AC:BAND?",
        "CURR:AC:BAND %d",
        """Control the AC current filter bandwidth in hertz.""",
        validator=strict_discrete_set,
        values=_BANDWIDTH_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )
    detector_bandwidth = Instrument.control(
        "DET:BAND?",
        "DET:BAND %d",
        """Control the common AC detector bandwidth in hertz.""",
        validator=strict_discrete_set,
        values=_BANDWIDTH_VALUES,
        check_get_errors=True,
        check_set_errors=True,
    )

    temperature_unit = Instrument.control(
        "UNIT:TEMP?",
        "UNIT:TEMP %s",
        """Control the temperature unit (celsius, fahrenheit, or kelvin).""",
        validator=strict_discrete_set,
        values=_TEMPERATURE_UNIT_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_temperature_unit,
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_2w_rtd_type = Instrument.control(
        "TEMP:RTD:TYP?",
        "TEMP:RTD:TYP %s",
        """Control the two-wire RTD type.""",
        validator=strict_discrete_set,
        values=_RTD_TYPE_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_rtd_type,
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_4w_rtd_type = Instrument.control(
        "TEMP:FRTD:TYP?",
        "TEMP:FRTD:TYP %s",
        """Control the four-wire RTD type.""",
        validator=strict_discrete_set,
        values=_RTD_TYPE_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_rtd_type,
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_2w_r0 = Instrument.control(
        "TEMP:RTD:R0?",
        "TEMP:RTD:R0 %.12g",
        """Control the two-wire RTD resistance at 0 degrees Celsius in ohms.""",
        validator=strict_range,
        values=(0.0, 1010.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_4w_r0 = Instrument.control(
        "TEMP:FRTD:R0?",
        "TEMP:FRTD:R0 %.12g",
        """Control the four-wire RTD resistance at 0 degrees Celsius in ohms.""",
        validator=strict_range,
        values=(0.0, 1010.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_2w_alpha = Instrument.control(
        "TEMP:RTD:ALPH?",
        "TEMP:RTD:ALPH %.8g",
        """Control the two-wire RTD alpha coefficient.""",
        validator=strict_range,
        values=(0.00374, 0.00393),
        check_get_errors=True,
        check_set_errors=True,
    )
    temperature_4w_alpha = Instrument.control(
        "TEMP:FRTD:ALPH?",
        "TEMP:FRTD:ALPH %.8g",
        """Control the four-wire RTD alpha coefficient.""",
        validator=strict_range,
        values=(0.00374, 0.00393),
        check_get_errors=True,
        check_set_errors=True,
    )

    analog_filter_enabled = Instrument.control(
        "FILT?",
        "FILT %d",
        """Control whether the analog DC filter is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    digital_filter_enabled = Instrument.control(
        "FILT:DIG?",
        "FILT:DIG %d",
        """Control whether the digital DC averaging filter is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    autozero_enabled = Instrument.control(
        "ZERO:AUTO?",
        "ZERO:AUTO %d",
        """Control whether automatic zero measurements are enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    voltage_dc_high_impedance_enabled = Instrument.control(
        "VOLT:DC:IMP:AUTO?",
        "VOLT:DC:IMP:AUTO %d",
        """Control automatic high input impedance for low DC voltage ranges.""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?",
        "TRIG:SOUR %s",
        """Control the trigger source (bus, external, or immediate).""",
        validator=strict_discrete_set,
        values=_TRIGGER_SOURCE_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_trigger_source,
        check_get_errors=True,
        check_set_errors=True,
    )
    trigger_delay = Instrument.control(
        "TRIG:DEL?",
        "TRIG:DEL %.12g",
        """Control the trigger delay in seconds (float strictly from 0 to 3600).""",
        validator=strict_range,
        values=(0.0, 3600.0),
        check_get_errors=True,
        check_set_errors=True,
    )
    trigger_delay_auto = Instrument.control(
        "TRIG:DEL:AUTO?",
        "TRIG:DEL:AUTO %d",
        """Control whether automatic trigger delay is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    sample_count = Instrument.control(
        "SAMP:COUN?",
        "SAMP:COUN %d",
        """Control measurements per trigger (int strictly from 1 to 50000).""",
        validator=strict_range,
        values=(1, 50000),
        get_process=int,
        check_get_errors=True,
        check_set_errors=True,
    )
    trigger_count = Instrument.control(
        "TRIG:COUN?",
        "TRIG:COUN %d",
        """Control accepted triggers (int strictly from 1 to 50000).""",
        validator=strict_range,
        values=(1, 50000),
        get_process=int,
        check_get_errors=True,
        check_set_errors=True,
    )

    terminal = Instrument.measurement(
        "ROUT:TERM?",
        """Get the selected input terminals (front or rear).""",
        values=_TERMINAL_VALUES,
        map_values=True,
        cast=str,
        get_process=_normalize_terminal,
        check_get_errors=True,
    )
    display_enabled = Instrument.control(
        "DISP?",
        "DISP %d",
        """Control whether the front-panel display is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    display_text = Instrument.control(
        "DISP:TEXT?",
        "DISP:TEXT %s",
        """Control the front-panel message (string of at most 12 characters).""",
        validator=_validate_display_text,
        cast=str,
        maxsplit=0,
        preprocess_reply=_unquote_scpi_string,
        check_get_errors=True,
        check_set_errors=True,
    )
    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?",
        "SYST:BEEP:STAT %d",
        """Control whether the continuity and limit beeper is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )
    error_beeper_enabled = Instrument.control(
        "SYST:ERR:BEEP?",
        "SYST:ERR:BEEP %d",
        """Control whether the error beeper is enabled (bool).""",
        validator=strict_discrete_set,
        values=_BOOLEAN_VALUES,
        map_values=True,
        check_get_errors=True,
        check_set_errors=True,
    )

    def __init__(
        self,
        adapter: Any,
        name: str = "Fluke 8846A",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("timeout", 10000)
        kwargs.setdefault("read_termination", "\n")
        kwargs.setdefault("write_termination", "\n")
        super().__init__(adapter, name, **kwargs)

    def check_get_errors(self) -> list:
        """Read and return all errors after querying a property."""
        return self.check_errors()

    def check_set_errors(self) -> list:
        """Read and return all errors after setting a property."""
        return self.check_errors()

    def initiate(self) -> None:
        """Place the meter in the wait-for-trigger state."""
        self.write("INIT")
        self.check_errors()

    def trigger(self) -> None:
        """Send a bus trigger to a meter waiting with the BUS trigger source."""
        self.write("*TRG")
        self.check_errors()

    def fetch(self) -> list[float]:
        """Get all readings currently stored for the primary display."""
        readings = [float(value) for value in self.values("FETC?")]
        self.check_errors()
        return readings

    def set_infinite_trigger_count(self) -> None:
        """Configure the meter to accept triggers continuously."""
        self.write("TRIG:COUN INF")
        self.check_errors()

    def autozero_once(self) -> None:
        """Initiate one automatic zero measurement."""
        self.write("ZERO:AUTO ONCE")
        self.check_errors()

    def beep(self) -> None:
        """Sound the meter beeper once."""
        self.write("SYST:BEEP")
        self.check_errors()

    def clear_display_text(self) -> None:
        """Clear the custom front-panel display message."""
        self.write("DISP:TEXT:CLE")
        self.check_errors()

    def remote(self) -> None:
        """Place an RS-232 or Ethernet connection into remote mode."""
        self.write("SYST:REM")
        self.check_errors()

    def remote_lockout(self) -> None:
        """Place an RS-232 or Ethernet connection into remote lockout mode."""
        self.write("SYST:RWL")
        self.check_errors()

    def local(self) -> None:
        """Return an RS-232 or Ethernet connection to local control."""
        self.write("SYST:LOC")
        self.check_errors()
