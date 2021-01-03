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



def connect(emitter: SignalEmitter, listener: SignalReceiver):
    emitter.listeners.append(listener)
    listener.sources.append(emitter)
    listener.refresh_signal()

def disconnect(emitter: SignalEmitter, listener: SignalReceiver):
    emitter.listeners.remove(listener)
    listener.sources.remove(emitter)
    listener.refresh_signal()