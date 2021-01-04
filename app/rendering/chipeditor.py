from __future__ import annotations

import pygame as pg

from app.builtinchips import AndGate, NotGate

from .holders import PinLocation, WireConnection
from .chiprenderer import ChipRenderer

class ChipEditor:

    EDITOR_BACKGROUND = (50, 50, 50)

    STATE_IDLE = 0
    STATE_CHIP_MOVING = 1
    STATE_PLACING_WIRE = 2

    def __init__(self, width, height):
        self.surface = pg.surface.Surface((width, height))

        self.chip_renderers = []  # type: list[ChipRenderer]
        self.input_signals = []  # type: list[InputSignalPin]
        self.output_signals = []  # type: list[OutputSignalPin]

        self.wire_connections = [] # type: list[WireConnection]
        
        self.temp()

        self.chip_renderers.append(ChipRenderer(AndGate(), (350, 420)))
        self.chip_renderers.append(ChipRenderer(NotGate(), (150, 150)))

        self.state = self.STATE_PLACING_WIRE

        self.mouse_x = 0
        self.mouse_y = 0

        self.selected_chip_index = -1
        self.mouse_start_offset = (0, 0)
        self.mouse_start_position = (0, 0)

        self.src_pin_loc = PinLocation(1, PinLocation.PIN_LOC_CHIP_OUT, 0)
        self.dest_pin_loc = PinLocation()


    def temp(self):
        src = PinLocation(0, PinLocation.PIN_LOC_CHIP_OUT, 0)
        dest = PinLocation(1, PinLocation.PIN_LOC_CHIP_IN, 0)
        conn = WireConnection(src, dest)
        self.wire_connections.append(conn)



    @property
    def RenderResult(self):
        return self.surface

    # def clear(self):
    #     self.chip_renderers = []
    #     self.input_signals = []
    #     self.output_signals = []
  
    def on_mouse_down(self):
        self.select_hovered_chip()
        if self.selected_chip_index != -1:
            self.state = self.STATE_CHIP_MOVING
            self.mouse_start_offset = self.chip_renderers[self.selected_chip_index].position
            self.mouse_start_position = (self.mouse_x, self.mouse_y)

    def on_mouse_up(self):
        self.state = self.STATE_IDLE
        # self.selected_chip_index = -1

    def on_mouse_move(self, mouse_x, mouse_y):
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def select_hovered_chip(self):
        self.selected_chip_index = -1
        for i, renderer in enumerate(self.chip_renderers):
            if renderer.check_collision(self.mouse_x, self.mouse_y):
                self.selected_chip_index = i
                break


    def draw_wires(self):
        conn = self.wire_connections[0]
        start = self.chip_renderers[conn.source.chip_index].get_pin_pos(conn.source.pin_type, conn.source.pin_index)
        end = self.chip_renderers[conn.dest.chip_index].get_pin_pos(conn.dest.pin_type, conn.dest.pin_index)
        # gfxdraw.line(self.surface, start[0], start[1], end[0], end[1], ChipRenderer.WIRE_COLOR_ON)
        # pg.draw.line(self.surface, ChipRenderer.WIRE_COLOR_ON, start, end)
        pg.draw.aaline(self.surface, ChipRenderer.WIRE_COLOR_ON, start, end)


    def draw(self):
        self.surface.fill(self.EDITOR_BACKGROUND)

        self.draw_wires()

        if self.state == self.STATE_PLACING_WIRE:
            loc = self.src_pin_loc
            start = self.chip_renderers[loc.chip_index].get_pin_pos(loc.pin_type, loc.pin_index)
            pg.draw.aaline(self.surface, ChipRenderer.WIRE_COLOR_OFF, start, (self.mouse_x, self.mouse_y))

        for i, renderer in enumerate(self.chip_renderers):
            if i == self.selected_chip_index:
                # skip the selected chip to later draw it on top
                continue

            renderer.update_hovered_pin(self.mouse_x, self.mouse_y)
            renderer.draw(self.surface)

        # draw the selected chip on top
        if self.selected_chip_index != -1:
            renderer = self.chip_renderers[self.selected_chip_index]
            renderer.draw_chip_border(self.surface)
            renderer.update_hovered_pin(self.mouse_x, self.mouse_y)
            renderer.draw(self.surface)


    def update(self):

        if self.state == self.STATE_CHIP_MOVING:
            selected_renderer = self.chip_renderers[self.selected_chip_index]

            relative_offset = (self.mouse_x - self.mouse_start_position[0], self.mouse_y - self.mouse_start_position[1])

            target_offset = (self.mouse_start_offset[0] + relative_offset[0], self.mouse_start_offset[1] + relative_offset[1])
            selected_renderer.move_to(target_offset[0], target_offset[1])

        self.draw()


    # def package(self, name=None):
    #     ChipFactory = custom_chip_factory(self.input_signals, self.output_signals)
    #     self.clear()
    #     return ChipFactory
