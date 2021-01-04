from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.chip import Chip


class Pin:
    def __init__(self):
        self._state = 0

    @property
    def State(self):
        return self._state

    def recv_signal(self, signal):
        self._state = signal


class SignalEmitter(Pin):
    def __init__(self):
        super().__init__()

        self.children = []  # type: list[Pin]

    def broadcast_signal(self, signal):
        for child in self.children:
            child.recv_signal(signal)

    def connect_to(self, target: Pin):
        self.children.append(target)
        target.recv_signal(self._state)

    
    def disconnect_from(self, target: Pin):
        self.children.remove(target)
        target.recv_signal(0)


class ChipPin(SignalEmitter):
    """
        Base class for all pins that are either ON or OFF
    """

    class PinType:
        INPUT = 1
        OUTPUT = 2

    def __init__(self):
        super().__init__()

        self.chip = None  # type: Chip
        self.index = -1
        self.pin_type = 0

    def set_chip(self, chip: Chip):
        self.chip = chip

    def recv_signal(self, signal):

        # Don't do anything if nothing changed
        if self._state == signal:
            return

        self._state = signal
        if self.pin_type == self.PinType.INPUT:
            self.chip.process_output()
        else:
            self.broadcast_signal(signal)


class InputSignalPin(SignalEmitter):
    def __init__(self):
        super().__init__()
        self.index = -1

    def recv_signal(self, signal):
        self._state = signal
        self.broadcast_signal(signal)


class OutputSignalPin(Pin):
    def __init__(self):
        self.index = -1

