"""PyMeasure driver for the Keysight P9375A vector network analyzer."""

from typing import Any

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range


class KeysightP9375A(Instrument):
    """Control the basic frequency sweep settings of a Keysight P9375A."""

    MIN_FREQUENCY_HZ = 300e3
    MAX_FREQUENCY_HZ = 9e9

    start_frequency = Instrument.control(
        ":SENS1:FREQ:START?",
        ":SENS1:FREQ:START %.12gHz",
        """Control the sweep start frequency in hertz.""",
        validator=strict_range,
        values=(MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ),
        cast=float,
    )

    stop_frequency = Instrument.control(
        ":SENS1:FREQ:STOP?",
        ":SENS1:FREQ:STOP %.12gHz",
        """Control the sweep stop frequency in hertz.""",
        validator=strict_range,
        values=(MIN_FREQUENCY_HZ, MAX_FREQUENCY_HZ),
        cast=float,
    )

    def __init__(
        self,
        adapter: Any,
        name: str = "Keysight P9375A",
        **kwargs: Any,
    ) -> None:
        """Initialize the analyzer using a PyMeasure adapter."""
        kwargs.setdefault("timeout", 5000)
        kwargs.setdefault("read_termination", "\n")
        kwargs.setdefault("write_termination", "\n")
        super().__init__(adapter, name, includeSCPI=False, **kwargs)

    @property
    def id(self) -> str:
        """Return the analyzer identification string."""
        return self.ask("*IDN?").strip()
