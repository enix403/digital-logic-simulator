from __future__ import annotations

class PinLocation:

    PL_NONE = 0 
    PL_CHIP_IN = 1
    PL_CHIP_OUT = 2
    PL_SIG_IN = 3
    PL_SIG_OUT = 4

    chip_index: int
    pin_type: int
    pin_index: int

    def __init__(self, chip_index: int = -1, ptype: int = PL_NONE, pindex: int = -1):
        self.chip_index = chip_index
        self.pin_type = ptype
        self.pin_index = pindex

    def clone(self):
        return PinLocation(self.chip_index, self.pin_type, self.pin_index)

    def clear(self):
        self.chip_index = -1
        self.pin_type = self.PL_NONE
        self.pin_index = -1

    def is_empty(self):
        return self.pin_type == self.PL_NONE

    def __eq__(self, other: PinLocation):
        if not isinstance(other, PinLocation):
            return False
            
        return self.chip_index == other.chip_index and \
                self.pin_type == other.pin_type and \
                self.pin_index == other.pin_type


    def __repr__(self):
        return f"PinLocation < chip_index={self.chip_index}, pin_type={self.pin_type}, pin_index={self.pin_index} >"
   

class WireConnection:
    def __init__(self, source: PinLocation, dest: PinLocation):
        self.source = source
        self.dest = dest
