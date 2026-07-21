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
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MarconiInstruments2041(Instrument):
    """ Represents the Marconi 2041 signal generator
    and provides a high-level interface for interacting
    with the instrument.
    """

    # inherit SCPImixins

    def __init__(self, adapter, name="Marconi Instruments 2041", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=True,
            send_end=True,
            **kwargs,
        )

    is_enabled = Instrument.control(
        "RFLV?",
        "RFLV:%s",
        """Control whether the RF output is enabled.""",
        validator=strict_discrete_set,
        values={False: 'OFF', True: 'ON'},
        set_process=lambda x: 'ON' if x else 'OFF',
        get_process=lambda x: "ON" in x,  # ':RFLV:UNITS DBM;VALUE -26.7;INC 0.1;OFF\n'
       )

    # Marconi operation manual refers to this as Carrier Frequency but 
    # center_frequency was used to conform w/ property names of other
    # signal generators.
    center_frequency = Instrument.control(
        "CFRQ?",
        "CFRQ:VALUE %dHz",
        """Control the carrier frequency in Hz.""",
        validator=strict_range,
        values=[10e3, 2.7e9],
        get_process=lambda f: float(f.split(' ')[1].split(';')[0]),  # ':CFRQ:VALUE 52000000.0;INC 1000.0\n'
       )

    power = Instrument.control(
        "RFLV?",
        "RFLV:UNITS DBM;VALUE %f; INC 0.1",
        """Control the RF output power in dBm""",
        validator=strict_range,
        values=[-144,10],
        get_process=lambda p: float(p.split(';')[1].split(' ')[1]),  # ':RFLV:UNITS DBM;VALUE -26.7;INC 0.1;OFF\n'
        )
    
    # disable modulation
    # signal generator mode (noise1, noise2, normal)