"""PyMeasure driver for the Rigol DSG815 RF signal generator."""

import re
from typing import Any

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def _parse_frequency_hz(value: Any) -> float:
    """Convert a DSG800 frequency reply such as '1.500GHz' to hertz."""
    text = str(value).strip().replace(" ", "")
    match = re.fullmatch(rf"({_NUMBER})([kKmMgG]?[hH][zZ])?", text)

    if match is None:
        raise ValueError(f"Could not parse DSG815 frequency reply: {value!r}")

    magnitude = float(match.group(1))
    unit = (match.group(2) or "Hz").lower()

    multiplier = {
        "hz": 1.0,
        "khz": 1e3,
        "mhz": 1e6,
        "ghz": 1e9,
    }[unit]

    return magnitude * multiplier


def _parse_power_dbm(value: Any) -> float:
    """Convert a DSG800 level reply to dBm, accepting an optional suffix."""
    text = str(value).strip().replace(" ", "")
    match = re.fullmatch(rf"({_NUMBER})(?:[dD][bB][mM])?", text)

    if match is None:
        raise ValueError(f"Could not parse DSG815 power reply: {value!r}")

    return float(match.group(1))


class RigolDSG815(Instrument):
    """Control a Rigol DSG815 through any PyMeasure/PyVISA transport."""

    MIN_FREQUENCY_HZ = 9e3
    MAX_FREQUENCY_HZ = 1.5e9

    MIN_POWER_DBM = -110.0
    MAX_POWER_DBM = 20.0

    frequency = Instrument.control(
        ":FREQ?",
        ":FREQ %.12gHz",
        """Control the RF carrier frequency in hertz.""",
        validator=strict_range,
        values=(MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ),
        # DSG815 replies contain units, for example "1.500GHz".
        cast=str,
        get_process=_parse_frequency_hz,
    )

    power_dbm = Instrument.control(
        ":LEV?",
        ":LEV %.6gdBm",
        """Control the RF output level in dBm.""",
        validator=strict_range,
        values=(MIN_POWER_DBM, MAX_POWER_DBM),
        cast=str,
        get_process=_parse_power_dbm,
    )

    output_enabled = Instrument.control(
        ":OUTP?",
        ":OUTP %d",
        """Control whether the RF output is enabled.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def __init__(
        self,
        adapter: Any,
        name: str = "Rigol DSG815",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("timeout", 5000)
        kwargs.setdefault("read_termination", "\n")
        kwargs.setdefault("write_termination", "\n")

        # The DSG815 supports selected SCPI commands, but its documented
        # factory reset is not the generic *RST used by SCPIMixin.
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs,
        )

    @property
    def id(self) -> str:
        """Return the identification string from *IDN?."""
        return self.ask("*IDN?").strip()

    @property
    def power(self) -> float:
        """Alias for power_dbm."""
        return self.power_dbm

    @power.setter
    def power(self, value: float) -> None:
        self.power_dbm = value

    def enable_output(self) -> None:
        """Enable the RF output."""
        self.output_enabled = True

    def disable_output(self) -> None:
        """Disable the RF output."""
        self.output_enabled = False

    def factory_reset(self) -> None:
        """Restore the DSG815 factory preset."""
        self.write(":SYST:PRES:TYPE FAC")
        self.write(":SYST:PRES")

    def reset(self) -> None:
        """Alias for factory_reset."""
        self.factory_reset()

    def shutdown(self) -> None:
        """Disable RF output and mark the instrument as shut down."""
        try:
            self.disable_output()
        finally:
            super().shutdown()
