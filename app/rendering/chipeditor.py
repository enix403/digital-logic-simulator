from __future__ import annotations

import pygame as pg
from pygame import gfxdraw

from app.builtinchips import AndGate, NotGate

from .holders import PinLocation as PinLoc, WireConnection
from .chiprenderer import ChipRenderer
# from .utils import draw_line


class ChipEditor:

    EDITOR_BACKGROUND = (50, 50, 50)
    # WIRE_COLOR_OFF = (36, 39, 46)
    WIRE_COLOR_OFF = (30, 35, 37)
    # WIRE_COLOR_ON = (236, 34, 56)
    WIRE_COLOR_ON = (246, 34, 56)

    STATE_IDLE = 0
    STATE_CHIP_MOVING = 1
    STATE_PLACING_WIRE = 2


    _VALID_CONNECTIONS = (
        (PinLoc.PL_SIG_IN, PinLoc.PL_CHIP_IN),
        (PinLoc.PL_CHIP_OUT, PinLoc.PL_CHIP_IN),
        (PinLoc.PL_CHIP_OUT, PinLoc.PL_SIG_OUT),
    )


    def __init__(self, width, height):
        self.surface = pg.surface.Surface((width, height))

        self.chip_renderers = []  # type: list[ChipRenderer]
        self.input_signals = []  # type: list[InputSignalPin]
        self.output_signals = []  # type: list[OutputSignalPin]

        self.wire_connections = [] # type: list[WireConnection]
        
        # self.temp()

        self.chip_renderers.append(ChipRenderer(AndGate(), (350, 420)))
        self.chip_renderers.append(ChipRenderer(NotGate(), (150, 150)))
        self.chip_renderers.append(ChipRenderer(NotGate(), (290, 90)))

        self.state = self.STATE_IDLE

        self.mouse_x = 0
        self.mouse_y = 0

        self.selected_chip_index = -1
        self.mouse_start_offset = (0, 0)
        self.mouse_start_position = (0, 0)

        self.src_pin_loc = PinLoc()
        self.dest_pin_loc = PinLoc()


    # def temp(self):
        # src = PinLoc(0, PinLoc.PL_CHIP_OUT, 0)
        # dest = PinLoc(1, PinLoc.PL_CHIP_IN, 0)
        # conn = WireConnection(src, dest)
        # self.wire_connections.append(conn)

    @property
    def RenderResult(self):
        return self.surface

    # def clear(self):
    #     self.chip_renderers = []
    #     self.input_signals = []
    #     self.output_signals = []
  
    def on_mouse_down(self):

        if self.state == self.STATE_IDLE:
            # if a source pin is currently being hovered, then select it and wait for the target pin
            if not self.src_pin_loc.is_empty():
                self.state = self.STATE_PLACING_WIRE
            else:
                self.select_hovered_chip()
                # if clicked on a hovered chip, select it and remember mouse position relative to chip
                # (to make dragging look a bit natural) and start the drag
                if self.selected_chip_index != -1:
                    self.state = self.STATE_CHIP_MOVING
                    self.mouse_start_offset = self.chip_renderers[self.selected_chip_index].position
                    self.mouse_start_position = (self.mouse_x, self.mouse_y)

        elif self.state == self.STATE_PLACING_WIRE:
            self.place_wire()
            self.state = self.STATE_IDLE


    def on_mouse_up(self):
        if self.state == self.STATE_CHIP_MOVING:
            self.state = self.STATE_IDLE

    def on_mouse_move(self, mouse_x, mouse_y):
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y



    def place_wire(self):
        if not self.src_pin_loc.is_empty() and not self.dest_pin_loc.is_empty():
            source_loc = self.src_pin_loc
            target_loc = self.dest_pin_loc

            valid = False
            swap = False

            # make sure the connection is valid and swap pin links if placed in reversed direction 
            if (source_loc.pin_type, target_loc.pin_type) in self._VALID_CONNECTIONS:
                valid = True
            elif (target_loc.pin_type, source_loc.pin_type) in self._VALID_CONNECTIONS:
                valid = True
                swap = True

            if valid:
                if swap:
                    source_loc, target_loc = target_loc, source_loc

                same_chip = source_loc.chip_index == target_loc.chip_index and source_loc.chip_index != -1
                if not same_chip:

                    source_pin = self.pin_from_loc(source_loc)
                    target_pin = self.pin_from_loc(target_loc)

                    # notify actual pins about connection
                    source_pin.connect_to(target_pin)

                    self.wire_connections.append(
                        WireConnection(source_loc.clone(), target_loc.clone())
                    )

        self.src_pin_loc.clear()
        self.dest_pin_loc.clear()


    def pin_from_loc(self, loc: PinLoc):
        """
        Returns the actual underlying pin given its location
        """
        if loc.pin_type == PinLoc.PL_CHIP_IN:
            return self.chip_renderers[loc.chip_index].chip.input_pins[loc.pin_index]

        if loc.pin_type == PinLoc.PL_CHIP_OUT:
            return self.chip_renderers[loc.chip_index].chip.output_pins[loc.pin_index]


    def connection_from_target_loc(self, target_loc):
        pass

    
    def select_hovered_chip(self):
        """
        'Activates' the pin that is currenly under the mouse
        """
        self.selected_chip_index = -1
        for i, renderer in enumerate(self.chip_renderers):
            if renderer.check_collision(self.mouse_x, self.mouse_y):
                self.selected_chip_index = i
                break

    def draw_wires(self):
        for conn in self.wire_connections:
            start = self.chip_renderers[conn.source.chip_index].get_pin_pos(conn.source.pin_type, conn.source.pin_index)
            end = self.chip_renderers[conn.dest.chip_index].get_pin_pos(conn.dest.pin_type, conn.dest.pin_index)
            pin = self.pin_from_loc(conn.source)
            # pin = self.pin_from_loc(conn.dest)

            # print(conn.source, conn.dest)

            # pg.draw.line(self.surface, self.WIRE_COLOR_OFF if pin.State == 0 else self.WIRE_COLOR_ON, start, end, width=3)
            pg.draw.aaline(self.surface, self.WIRE_COLOR_OFF if pin.State == 0 else self.WIRE_COLOR_ON, start, end)
            # gfxdraw.line(self.surface, start[0], start[1], end[0], end[1], self.WIRE_COLOR_OFF)
            # pg.draw.aaline(self.surface, self.WIRE_COLOR_OFF, start, end)


    def draw(self):
        self.surface.fill(self.EDITOR_BACKGROUND)

        self.draw_wires()

        if self.state == self.STATE_PLACING_WIRE:
            loc = self.src_pin_loc
            start = self.chip_renderers[loc.chip_index].get_pin_pos(loc.pin_type, loc.pin_index)
            pg.draw.line(self.surface, (0, 0, 0), start, (self.mouse_x, self.mouse_y), width=3)


        for i, renderer in enumerate(self.chip_renderers):
            if i == self.selected_chip_index:
                # skip the selected chip to later draw it on top
                continue

            renderer.draw(self.surface)

        # draw the selected chip on top
        if self.selected_chip_index != -1:
            renderer = self.chip_renderers[self.selected_chip_index]
            renderer.draw_chip_border(self.surface)
            renderer.draw(self.surface)


    def update(self):

        if self.state == self.STATE_CHIP_MOVING:
            selected_renderer = self.chip_renderers[self.selected_chip_index]

            relative_offset = (self.mouse_x - self.mouse_start_position[0], self.mouse_y - self.mouse_start_position[1])

            target_offset = (self.mouse_start_offset[0] + relative_offset[0], self.mouse_start_offset[1] + relative_offset[1])
            selected_renderer.move_to(target_offset[0], target_offset[1])
            # self.src_pin_loc.clear()
            # self.dest_pin_loc.clear()


        else:
            # This piece of code ONLY keeps track of what pin is currently under mouse
            if self.state == self.STATE_PLACING_WIRE:
                target_loc = self.dest_pin_loc
            else:
                target_loc = self.src_pin_loc

            target_loc.clear()

            for i, renderer in enumerate(self.chip_renderers):
                hovered_pin = renderer.update_hovered_pin(self.mouse_x, self.mouse_y)
                if hovered_pin is None:
                    continue

                pin_type, pin_index = hovered_pin

                target_loc.chip_index = i
                target_loc.pin_type = pin_type
                target_loc.pin_index = pin_index


        self.draw()


    # def package(self, name=None):
    #     ChipFactory = custom_chip_factory(self.input_signals, self.output_signals)
    #     self.clear()
    #     return ChipFactory
