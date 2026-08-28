"""Device tests for a physically connected Fluke 8846A."""

import os
from collections.abc import Iterator

import pytest
from pymeasure.adapters import PrologixAdapter, VISAAdapter

from lab_instruments.fluke import Fluke8846A


@pytest.fixture(scope="module")
def meter() -> Iterator[Fluke8846A]:
    """Connect to the meter configured through environment variables."""
    resource = os.getenv("FLUKE_8846A_RESOURCE")
    if not resource:
        pytest.skip("Set FLUKE_8846A_RESOURCE to run Fluke 8846A device tests")

    gpib_address = os.getenv("FLUKE_8846A_GPIB_ADDRESS")
    if gpib_address is None:
        adapter = VISAAdapter(resource)
    else:
        adapter = PrologixAdapter(resource, address=int(gpib_address))

    instrument = Fluke8846A(adapter)
    try:
        yield instrument
    finally:
        instrument.shutdown()


@pytest.mark.device
def test_identification(meter: Fluke8846A) -> None:
    """Identify the connected meter as a Fluke 8846A."""
    identification = meter.id.upper()
    assert "FLUKE" in identification
    assert "8846A" in identification


@pytest.mark.device
def test_direct_resistance_measurement(meter: Fluke8846A) -> None:
    """Take one direct two-wire resistance measurement."""
    assert isinstance(meter.resistance, float)
