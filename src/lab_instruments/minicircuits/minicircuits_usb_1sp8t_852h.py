from __future__ import annotations

import hid


VID = 0x20CE
PID = 0x0022
PACKET_SIZE = 64


class MiniCircuitsSP8T:
    def __init__(self, serial_number: str | None = None) -> None:
        self.device = hid.device()

        if serial_number is None:
            self.device.open(VID, PID)
        else:
            self.device.open(VID, PID, serial_number)

        # Return immediately if no response is available.
        self.device.set_nonblocking(False)

    def close(self) -> None:
        self.device.close()

    def send_scpi(self, command: str) -> str:
        command_bytes = command.encode("ascii")

        # Byte 0 is the HID report ID.
        # Byte 1 is Mini-Circuits' SCPI command indicator.
        packet = bytearray(PACKET_SIZE + 1)
        packet[0] = 0x00
        packet[1] = 0x01

        if len(command_bytes) > PACKET_SIZE - 1:
            raise ValueError("SCPI command is too long")

        packet[2 : 2 + len(command_bytes)] = command_bytes

        bytes_written = self.device.write(packet)

        if bytes_written <= 0:
            raise RuntimeError("Failed to write to the switch")

        response = self.device.read(PACKET_SIZE, timeout_ms=1000)

        if not response:
            return ""

        response_bytes = bytes(response)

        # The first response byte is the Mini-Circuits response code.
        text = response_bytes[1:].split(b"\x00", 1)[0]

        return text.decode("ascii", errors="replace").strip()

    def set_port(self, port: int) -> None:
        if port not in range(1, 9):
            raise ValueError("Port must be from 1 through 8")

        response = self.send_scpi(f":SP8T:STATE:{port}")

        if response:
            print(f"Set response: {response}")

    def get_port(self) -> int:
        response = self.send_scpi(":SP8T:STATE?")

        try:
            return int(response)
        except ValueError as exc:
            raise RuntimeError(
                f"Unexpected switch response: {response!r}"
            ) from exc

    def __enter__(self) -> "MiniCircuitsSP8T":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


if __name__ == "__main__":
    with MiniCircuitsSP8T(serial_number="12605310007") as switch:
        switch.set_port(8)
        print(f"Selected port: J{switch.get_port()}")
