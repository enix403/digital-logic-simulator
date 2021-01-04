from __future__ import annotations

class PinLocation:

    PIN_LOC_NONE = 0 
    PIN_LOC_CHIP_IN = 1
    PIN_LOC_CHIP_OUT = 2
    PIN_LOC_SIG_IN = 3
    PIN_LOC_SIG_OUT = 4

    chip_index: int
    pin_type: int
    pin_index: int

    def __init__(self, chip_index: int = -1, ptype: int = PIN_LOC_NONE, pindex: int = -1):
        self.chip_index = chip_index
        self.pin_type = ptype
        self.pin_index = pindex

    def clone(self):
        return PinLocation(self.chip_index, self.pin_type, self.pin_index)
   

class WireConnection:
    def __init__(self, source: PinLocation, dest: PinLocation):
        self.source = source
        self.dest = dest
