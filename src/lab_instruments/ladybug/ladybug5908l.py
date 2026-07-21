#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LadyBug5908L(SCPIMixin, Instrument):
    """Represents the LadyBug 5908L power meter
    and provides a high-level interface for interacting
    with the instrument.
    """

    # inherit SCPImixins

    def __init__(self, adapter, name="LadyBug 5908L", **kwargs):
        super().__init__(
            adapter,
            name,
            # includeSCPI=True,
            send_end=True,
            **kwargs,
        )

    resolution = Instrument.control(
        "CONF?",
        "CONF DEF, %d",
        """
        Control the resolution of the power measurement (float).
        """,
        get_process=lambda x: x[1],
    )

    # trigger_source

    continuous_triggering_enabled = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %d",
        """
        Controls continuous triggering (bool).
        """,
        map_values=True,
        values={True: 1, False: 0},
    )

    averaging_enabled = Instrument.control(
        "AVER:STAT?",
        "AVER:STAT %s",
        """
        Controls averaging (bool).
        """,
        map_values=True,
        values={True: 1, False: 0},
    )

    # auto_averaging

    averaging_counts = Instrument.control(
        "AVER:COUN?",
        "AVER:COUN %d",
        """
        Controls the number of average counts made (int).
        """,
    )

    frequency = Instrument.control(
        "FREQ?",
        "FREQ %d",
        """
        Controls the frequency in Hz that power meter measures (float).
        """,
    )

    # read power MEAS? but READ? is better and FETCH? is fastest
    power = Instrument.measurement(
        "FETCH?",
        """
        Get the power measurement in Hz (float).
        """,
    )

    # set offset from e4418b need to check if this works
    offset_gain = Instrument.control(
        "SENS:CORR:GAIN2?",
        "SENS:CORR:GAIN2 %f",
        """
        Control the offset added (in dB) from the power sensor measurement
        to account for cable and other losses to the power meter. (float)
        """,
        cast=float,
        validator=strict_range,
        values=[-100, 100],
    )

    # need to check if this works
    offset_gain_enabled = Instrument.control(
        "SENS:CORR:GAIN2:STAT?",
        "SENS:CORR:GAIN2:STAT %d",
        """
        Control whether the offset is enabled. (bool)
        """,
        cast=bool,
    )
