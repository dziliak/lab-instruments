# lab-instruments

Private instrument drivers and hardware helpers for laboratory automation. The
PyMeasure drivers in this repository provide higher-level Python interfaces to
selected RF signal generators and power meters. The project is primarily for
local use and experimentation; it is not intended to be a complete replacement
for the upstream PyMeasure instrument collection.

## Supported hardware

| Manufacturer | Model | Interface | Implementation |
| --- | --- | --- | --- |
| Agilent | E4418B power meter | PyMeasure adapter | `AgilentE4418B` |
| Keysight | P9375A vector network analyzer | PyMeasure adapter | `KeysightP9375A` |
| Fluke | 8846A digital multimeter | PyMeasure adapter | `Fluke8846A` |
| LadyBug | 5908L power meter | PyMeasure adapter | `LadyBug5908L` |
| Marconi Instruments | 2041 signal generator | PyMeasure adapter | `MarconiInstruments2041` |
| Rigol | DSG815 RF signal generator | PyMeasure adapter | `RigolDSG815` |
| Mini-Circuits | USB 1-SP8T-852H switch | USB HID | `MiniCircuitsSP8T` |

The Keysight P9375A driver supports sweep configuration, averaging, triggering,
output power, and Touchstone SnP export in addition to sweep start and stop
frequency.

Driver coverage varies by instrument. The available interfaces include common
operations such as frequency, output power, output state, power measurements,
averaging, resolution, offsets, calibration, and preset/zero operations. Refer
to the driver source and the instrument documentation for the exact supported
commands and ranges.

## Installation

This project requires Python 3.11 or newer. Install it with `uv`:

```bash
uv sync
```

The package depends on [PyMeasure](https://pymeasure.readthedocs.io/) and
`hidapi` for the Mini-Circuits USB switch. These dependencies are installed by
the project configuration.

For development, install the tools declared in the `dev` dependency group
(using `uv`):

```bash
uv sync --dev
```

To use this library and test from Jupyter, run the following:

```bash
uv run --group notebook python -m ipykernel install \
    --user \
    --name lab-instruments \
    --display-name "Python (lab-instruments)"
```

## Usage

PyMeasure drivers accept any compatible PyMeasure adapter, such as a VISA
adapter. For example, the Rigol driver can be used over VISA as follows:

```python
from pymeasure.adapters import VISAAdapter

from lab_instruments.rigol.rigol_dsg815 import RigolDSG815


adapter = VISAAdapter("TCPIP0::192.0.2.10::INSTR")
generator = RigolDSG815(adapter)
generator.frequency = 100e6
generator.power_dbm = -10
generator.enable_output()

try:
    print(generator.id)
finally:
    generator.shutdown()
```

The Mini-Circuits switch uses a direct USB HID connection rather than a
PyMeasure adapter:

```python
from lab_instruments.minicircuits.minicircuits_usb_1sp8t_852h import (
    MiniCircuitsSP8T,
)


with MiniCircuitsSP8T() as switch:
    switch.set_port(8)
    print(switch.get_port())
```

Use the device's serial number when more than one compatible switch is
connected. Hardware access requires the appropriate VISA backend, USB
permissions, and a connected instrument.

## Development

Run the test suite with:

```bash
uv run pytest
```

Run linting and formatting checks with:

```bash
uv run ruff check
uv run ruff format --check
```

Tests that require physical equipment should use the `device` marker and may
be skipped unless the required hardware is available.

## Hardware setup

VISA-based drivers require a VISA backend, such as NI-VISA or pyvisa-py, and a
connected instrument. Pass the instrument's VISA resource string to
`VISAAdapter`, for example:

```python
from pymeasure.adapters import VISAAdapter

adapter = VISAAdapter("TCPIP0::192.0.2.10::INSTR")
```

The Mini-Circuits switch requires a compatible USB connection and appropriate
USB permissions. Device tests are skipped unless the required hardware and
resource configuration are available.

## Project layout

```text
src/lab_instruments/
├── agilent/        Agilent E4418B power meter driver
├── ladybug/        LadyBug 5908L power meter driver
├── marconi/        Marconi 2041 signal generator driver
├── minicircuits/   Mini-Circuits USB HID switch helper
├── keysight/       Keysight P9375A vector network analyzer driver
└── rigol/          Rigol DSG815 signal generator driver
```

## License

See [LICENSE](LICENSE).
