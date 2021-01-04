from __future__ import annotations

import pathlib
import sys
root = pathlib.Path('.').parent.resolve().absolute()
sys.path.append(str(root))

# from typing import Callable
from app.pins import ChipPin, InputSignalPin, OutputSignalPin

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
        self.input_pins = [] # type: list[ChipPin]
        self.output_pins = [] # type: list[ChipPin]

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


    def _add_pin(self, pin_type):
        pin = ChipPin()
        pin.pin_type = pin_type
        if pin_type == ChipPin.PinType.INPUT:
            self.input_pins.append(pin)
        else:
            self.output_pins.append(pin)

        pin.set_chip(self)
        return pin
        
            
    def process_output(self):
        """
        Reads the values from input pins, calculates the output and sends the output
        to the output pins
        """
        # meant to be implemented by child classes


class CustomChip(Chip):

    def __init__(self, name: str, input_signals: list[InputSignalPin], output_signals: list[OutputSignalPin]):

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
            self._add_pin(ChipPin.PinType.INPUT)

        for _ in range(len(output_signals)):
            self._add_pin(ChipPin.PinType.OUTPUT)

        self.initialize_pins()


    def process_output(self):
        # forwars signals from input pins to the first layer of input signals
        for i in range(self.InputPinCount):
            self.input_signals[i].recv_signal(self.input_pins[i].State)

        # forwars signals from output signal layer (2nd last layer) to output pins
        for i in range(self.OutputPinCount):
            self.output_pins[i].recv_signal(self.output_signals[i].State)

    
def custom_chip_factory(name, input_signals: list[InputSignalPin], output_signals: list[OutputSignalPin]):
    def _f():
        return CustomChip(name, input_signals, output_signals)

    return _f


# def test(s1: InputSignalPin, s2: InputSignalPin, s3: OutputSignalPin, p1, p2):
#     s1.recv_signal(p1)
#     s2.recv_signal(p2)

#     res = s3.State
    
#     print(f"{p1} OP {p2} = {res}")

# def test(gate: Chip, p1, p2):
#     gate.input_pins[0].recv_signal(p1)
#     gate.input_pins[1].recv_signal(p2)

#     res = gate.output_pins[0].State
    
#     print(f"{p1} {gate.name} {p2} = {res}")


# s1 = InputSignalPin()
# s2 = InputSignalPin()
# s3 = OutputSignalPin()

# gate = AndGate()
# no = NotGate()

# s1.connect_to(gate.input_pins[0])
# s2.connect_to(gate.input_pins[1])

# gate.output_pins[0].connect_to(no.input_pins[0])
# no.output_pins[0].connect_to(s3)

# NandGate = custom_chip_factory('NAND', [s1, s2], [s3])

# g = NandGate()


# test(g, 0, 0)
# test(g, 0, 1)
# test(g, 1, 0)
# test(g, 1, 1)