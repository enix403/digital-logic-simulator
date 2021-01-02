from __future__ import annotations

class Pin:
    """
        Base class that does nothing but store a state of 0 or 1
    """

    def __init__(self):
        self._state = 0

    @property
    def State(self):
        return self._state



class SignalReceiver(Pin):
    """
        Base class for all pins that can fetch their state from multiple pins

        (For example some sort of "input pins" can fetch state from multiple wires)
    """

    def __init__(self):
        super().__init__()
        self.sources = [] # type: list[SignalEmitter]
        self.last_state = 0
    
    def refresh_signal(self):
        # the state of this pin is 1 if any of the sources has a state on 1, and 0 otherwise.
        # Analogous to the fact that a wire carries current if at least one of the wires
        # connecting it has current flowing through it
        signal = 0
        for source in self.sources:
            if source.State == 1:
                signal = 1
                break
        self.last_state = self._state
        self._state = signal


class SignalEmitter(Pin):
    """
    Base class for all pins that can send their state to multiple pins.

    (For example an output pin of a component can be further connected to multiple pins)
    """
    def __init__(self):
        super().__init__()
        self.listeners = [] # type: list[SignalReceiver]

    def broadcast_signal(self, signal):
        if self._state != signal:
            self._state = signal
            for listener in self.listeners:
                listener.refresh_signal()


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
        for i, pin in enumerate(self.input_pins): # type: int, ChipPin
            pin.index = i
        for i, pin in enumerate(self.output_pins): # type: int, ChipPin
            pin.index = i

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


class AndGate(Chip):
    def __init__(self):
        super().__init__()
        self.input_pins.append(ChipInputPin(self))
        self.input_pins.append(ChipInputPin(self))

        self.output_pins.append(SignalEmitter())
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        inp_2 = self.input_pins[1].State
        result_pin: SignalEmitter = self.output_pins[0]
        result_pin.broadcast_signal(1 if inp_1 == 1 and inp_2 == 1 else 0)

    
class OrGate(Chip):
    def __init__(self):
        super().__init__()
        self.input_pins.append(ChipInputPin(self))
        self.input_pins.append(ChipInputPin(self))

        self.output_pins.append(SignalEmitter())
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        inp_2 = self.input_pins[1].State
        result_pin: SignalEmitter = self.output_pins[0]
        result_pin.broadcast_signal(0 if inp_1 == 0 and inp_2 == 0 else 1)

    

class NotGate(Chip):
    def __init__(self):
        super().__init__()
        self.input_pins.append(ChipInputPin(self))
        self.output_pins.append(SignalEmitter())
        
        self.initialize_pins()

    def process_output(self):
        inp_1 = self.input_pins[0].State
        result_pin: SignalEmitter = self.output_pins[0]
        result_pin.broadcast_signal(1 if inp_1 == 0 else 0)

def connect(emitter: SignalEmitter, listener: SignalReceiver):
    emitter.listeners.append(listener)
    listener.sources.append(emitter)
    listener.refresh_signal()

def disconnect(emitter: SignalEmitter, listener: SignalReceiver):
    emitter.listeners.remove(listener)
    listener.sources.remove(emitter)
    listener.refresh_signal()


class CustomChip(Chip):

    def __init__(self, input_signals: list[SignalEmitter], output_signals: list[SignalReceiver]):

        """
        Class used to bundle a set of components connected together into a single chip

        It takes a set (kinda Linked list) of input signals and output signals and wraps
        them in a layer in Chip Input Pins and Output Pins

        Input (and output) signals are the SignalEmitters that carry input (and output)
        from the user taken from the "editor"


        For example if the input is:

            input signals -> component 1 -> compoent 2 -> ... -> output signals

        then resulting chip will be like

            chip's input pins -> input signals -> ... components ... -> output signals -> chip's output pins  
        """
        
        super().__init__()

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

    
def custom_chip_factory(input_signals: list[SignalEmitter], output_signals: list[SignalReceiver]):
    def _f():
        return CustomChip(input_signals, output_signals)

    return _f


def create_nand_gate():
    and_gate = AndGate()
    not_gate = NotGate()

    signal_1 = SignalEmitter()
    signal_2 = SignalEmitter()
    output_signal = SignalReceiver()

    connect(signal_1, and_gate.input_pins[0])
    connect(signal_2, and_gate.input_pins[1])

    connect(and_gate.output_pins[0], not_gate.input_pins[0])
    connect(not_gate.output_pins[0], output_signal)

    return custom_chip_factory([signal_1, signal_2], [output_signal])
    # return

NandGate = create_nand_gate()


class ChipRenderer:
    def __init__(self, chip: Chip, position: tuple):
        self.chip = chip
        self.position = position


class ChipEditor:
    def __init__(self):
        pass

class LogicWorkspace:
    pass


class Application:
    def __init__(self):

        gate1 = NandGate()
        gate2 = NandGate()

        gate1.input_pins[0].force_update_signal(1)
        gate2.input_pins[0].force_update_signal(1)

        print(gate1.output_pins[0].State)
        print(gate2.output_pins[0].State)

        print()

        gate1.input_pins[1].force_update_signal(1)

        print(gate1.output_pins[0].State)
        print(gate2.output_pins[0].State)
        

        print()

        gate1.process_output()
        gate2.process_output()

        print(gate1.output_pins[0].State)
        print(gate2.output_pins[0].State)
        
        

    def test(self, p1, p2):
        # self.signal_1.broadcast_signal(p1)
        # self.signal_2.broadcast_signal(p2)
        # res = self.output_signal.State
        
        # print(f"{p1} AND {p2} = {res}")
        pass

    def start(self):
        self.test(0, 0)
        self.test(0, 1)
        self.test(1, 0)
        self.test(1, 1)
        

# appl = Application()
# appl.start()