from __future__ import annotations
from typing import Callable

from app.pins import SignalReceiver, SignalEmitter

class ChipInputPin(SignalReceiver):
    # the chip this pin belongs to
    chip: Chip

    # index of the pin with respect to its parent chip
    index: int = -1

    def __init__(self, chip: Chip):
        super().__init__()
        self.chip = chip

    def refresh_signal(self):
        super().refresh_signal()

        # this check below is crucial because ouput from a component
        # can be connected to its input, so when the the output
        # is calculated, it calls refresh_signal of all SignalReceivers it is
        # connected to, including this input which will forward it to
        # the chip, which will forward it again to the output and this recursive
        # loop keeps going on, so ask the chip to calculate output only when its
        # inputs change, which prevents recursion and as a bonus prevents unnecessary
        # calculations
        if self.last_state != self._state:
            self.chip.process_output()

    # temporary function used for debugging
    def force_update_signal(self, signal):
        if signal != self._state:
            self.last_state = self._state
            self._state = signal
            self.chip.process_output()


class Chip:

    """Base class for all chips"""

    name = "Untitled"


    @property
    def InputPinCount(self):
        return self._len_input_pins

    @property
    def OutputPinCount(self):
        return self._len_output_pins

    def __init__(self):
        self.input_pins = [] # type: list[ChipInputPin]
        self.output_pins = [] # type: list[SignalEmitter]

         # they are used quite often and they do not change once set, so cache them
        self._len_input_pins = -1
        self._len_output_pins = -1

    def initialize_pins(self):
        # for i, pin in enumerate(self.input_pins): # type: int, ChipPin
        #     pin.index = i
        # for i, pin in enumerate(self.output_pins): # type: int, ChipPin
        #     pin.index = i

        self._len_input_pins = len(self.input_pins)
        self._len_output_pins = len(self.output_pins)

        # calculate the initial output when all the pins have a value 0.
        # This is required because, for example, without it, a NOT Gate will have
        # an initial output of 0 (the default state of output pins)
        # when it should be having a value of 1
        self.process_output()
            
    def process_output(self):
        """
        Reads the values from input pins, calculates the output and sends the output
        to the output pins
        """
        # meant to be implemented by child classes




class CustomChip(Chip):

    def __init__(self, name: str, input_signals: list[SignalEmitter], output_signals: list[SignalReceiver]):

        """
        Class used to bundle a set of components connected together into a single chip

        It takes a set (kinda Linked list) of input signals and output signals and wraps
        them in a layer in Chip Input Pins and Output Pins

        Input (and output) signals are the SignalEmitters that carry input (and output)
        from the user taken from the chip editor


        For example if the input is:

            input signals -> component 1 -> compoent 2 -> ... -> output signals

        then resulting chip will be like

            chip's input pins -> input signals -> ... components ... -> output signals -> chip's output pins  
        """
        
        super().__init__()
        self.name = name

        self.input_signals = input_signals
        self.output_signals = output_signals

        for _ in range(len(input_signals)):
            self.input_pins.append(ChipInputPin(self))

        for _ in range(len(output_signals)):
            self.output_pins.append(SignalEmitter())

        self.initialize_pins()


    def process_output(self):
        # forwars signals from input pins to the first layer of input signals
        for i in range(self.InputPinCount):
            self.input_signals[i].broadcast_signal(self.input_pins[i].State)

        # forwars signals from output signal layer (2nd last layer) to output pins
        for i in range(self.OutputPinCount):
            self.output_pins[i].broadcast_signal(self.output_signals[i].State)

    
def custom_chip_factory(name, input_signals: list[SignalEmitter], output_signals: list[SignalReceiver]):
    def _f():
        return CustomChip(name, input_signals, output_signals)

    return _f