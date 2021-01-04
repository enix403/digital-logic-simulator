from __future__ import annotations

from app.chip import Chip
from app.pins import ChipPin


class AndGate(Chip):
    
    name = "AND"

    def __init__(self):
        super().__init__()
        self._add_pin(ChipPin.PinType.INPUT)
        self._add_pin(ChipPin.PinType.INPUT)

        self._add_pin(ChipPin.PinType.OUTPUT)
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        inp_2 = self.input_pins[1].State
        result_pin: ChipPin = self.output_pins[0]
        result_pin.recv_signal(1 if inp_1 == 1 and inp_2 == 1 else 0)

    
class OrGate(Chip):

    name = "OR"

    def __init__(self):
        super().__init__()
        self._add_pin(ChipPin.PinType.INPUT)
        self._add_pin(ChipPin.PinType.INPUT)

        self._add_pin(ChipPin.PinType.OUTPUT)
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        inp_2 = self.input_pins[1].State
        result_pin: ChipPin = self.output_pins[0]
        result_pin.recv_signal(0 if inp_1 == 0 and inp_2 == 0 else 1)

    

class NotGate(Chip):

    name = "NOT"

    def __init__(self):
        super().__init__()
        self._add_pin(ChipPin.PinType.INPUT)
        self._add_pin(ChipPin.PinType.OUTPUT)
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        result_pin: ChipPin = self.output_pins[0]
        result_pin.recv_signal(1 if inp_1 == 0 else 0)

