from __future__ import annotations
import math

import pygame as pg
from pygame import gfxdraw
from pygame import freetype

freetype.init()

from app.chip import Chip, custom_chip_factory
from app.builtinchips import AndGate, NotGate


# pg.surface.Surface((self.app.MainWindow.width, self.app.MainWindow.height), pg.SRCALPHA, 64)

def _draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def render_text(font, text, size, fgcolor, bgcolor=(0, 0, 0, 0)) -> pg.Surface:
    txt_surface, _ = font.render(text, fgcolor, bgcolor, freetype.STYLE_DEFAULT, 0, size)
    return txt_surface


class ChipRenderer:

    chip_text_font = freetype.SysFont("Noto Sans Medium", 1)

    pin_radius = 7
    pin_margin = 2

    pin_diameter = 2 * pin_radius

    total_radius = pin_radius + pin_margin
    total_diameter = 2 * total_radius

    PIN_COLOR = (0, 0, 0)
    PIN_HOVER_COLOR = (178, 178, 178)

    WIRE_COLOR_OFF = (0, 0, 0)
    WIRE_COLOR_ON = (236, 34, 56)

    CHIP_BACKGROUND = (57, 122, 152)
    CHIP_HOVER_BORDER_COLOR = (71, 71, 71)

    FONT_COLOR = (226, 235, 240)
    FONT_SIZE = 14

    PIN_TYPE_INPUT = 1
    PIN_TYPE_OUTPUT = 2

    def __init__(self, chip: Chip, position: tuple = (0, 0)):
        self.chip = chip
        # self.chip.input_pins[0].force_update_signal(1)
        self.position = position

        self.hovered_pin_index = -1
        self.hovered_pin_type = 0

        self.input_pins_y = []
        self.output_pins_y = []

        for i in range(chip.InputPinCount):
            y = self.total_diameter * i + self.total_radius
            self.input_pins_y.append(y)

        for i in range(chip.OutputPinCount):
            y = self.total_diameter * i + self.total_radius
            self.output_pins_y.append(y)

        self.chip_name_surface = render_text(self.chip_text_font, chip.name, self.FONT_SIZE, self.FONT_COLOR)
        self.height = max(self.input_pins_y[-1], self.output_pins_y[-1]) + self.total_radius + 1 # to balance shit
        self.width = 2 * self.pin_radius + 8 + self.chip_name_surface.get_width()
        self.txt_x = self.pin_radius + 4
        self.txt_y = (self.height - self.chip_name_surface.get_height()) // 2

        # just centering things, nothing to fancy

        input_padding = (self.height - self.input_pins_y[-1] - self.total_radius) // 2
        output_padding = (self.height - self.output_pins_y[-1] - self.total_radius) // 2

        for i in range(chip.InputPinCount):
            self.input_pins_y[i] += input_padding

        for i in range(chip.OutputPinCount):
            self.output_pins_y[i] += output_padding

        self.bound_width = self.width + self.pin_diameter
        self.bound_height = self.height + self.pin_diameter

    def draw(self, surface):
        pg.draw.rect(surface, self.CHIP_BACKGROUND, pg.Rect(self.position[0], self.position[1], self.width, self.height))

        for i, y in enumerate(self.input_pins_y):
            if self.hovered_pin_type == self.PIN_TYPE_INPUT and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            _draw_circle(surface, self.position[0], self.position[1] + y, self.pin_radius, color)

        for i, y in enumerate(self.output_pins_y):
            if self.hovered_pin_type == self.PIN_TYPE_OUTPUT and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            _draw_circle(surface, self.position[0] + self.width, self.position[1] + y, self.pin_radius, color)

        surface.blit(self.chip_name_surface, (self.position[0] + self.txt_x, self.position[1] + self.txt_y))

    def update_hovered_pin(self, mouse_x, mouse_y):
        self.hovered_pin_index = -1
        self.hovered_pin_type = 0

        x = self.position[0]

        if mouse_x >= x - self.pin_radius and mouse_x <= x + self.pin_radius:
            for i, y in enumerate(self.input_pins_y):
                pin_y = self.position[1] + y 
                if mouse_y >= pin_y - self.pin_radius and mouse_y <= pin_y + self.pin_radius:
                    self.hovered_pin_index = i
                    self.hovered_pin_type = self.PIN_TYPE_INPUT
                    return
                    

        x = self.position[0] + self.width
        if mouse_x >= x - self.pin_radius and mouse_x <= x + self.pin_radius:
            for i, y in enumerate(self.output_pins_y):
                pin_y = self.position[1] + y 
                if mouse_y >= pin_y - self.pin_radius and mouse_y <= pin_y + self.pin_radius:
                    self.hovered_pin_index = i
                    self.hovered_pin_type = self.PIN_TYPE_OUTPUT
                    return


    def draw_border(self, surface):
        left = self.position[0] - self.pin_radius
        top = self.position[1] - self.pin_radius

        pg.draw.rect(surface, self.CHIP_HOVER_BORDER_COLOR, pg.Rect(left, top, self.bound_width, self.bound_height))

    def check_collision(self, x, y):
        # i wasted 1 hour debugging because i accidently swapped the indices 0 and 1 below
        left = self.position[0] - self.pin_radius
        top = self.position[1] - self.pin_radius

        bottom = top + self.bound_height
        right = left + self.bound_width

        return x >= left and x <= right and y >= top and y <= bottom

    def move_to(self, x, y):
        self.position = (x, y)


class ChipEditor:

    EDITOR_BACKGROUND = (50, 50, 50)

    STATE_IDLE = 0
    STATE_CHIP_MOVING = 1

    def __init__(self, width, height):
        self.chip_renderers = []  # type: list[ChipRenderer]
        self.input_signals = []  # type: list[SignalEmitter]
        self.output_signals = []  # type: list[SignalReceiver]

        self.surface = pg.surface.Surface((width, height))
        self.chip_renderers.append(ChipRenderer(AndGate(), (350, 420)))
        self.chip_renderers.append(ChipRenderer(NotGate(), (150, 150)))

        self.state = self.STATE_IDLE

        self.mouse_x = 0
        self.mouse_y = 0

        self.selected_chip_index = -1
        self.mouse_start_offset = (0, 0)
        self.mouse_start_position = (0, 0)

    @property
    def RenderResult(self):
        return self.surface

    def clear(self):
        self.chip_renderers = []
        self.input_signals = []
        self.output_signals = []

    def select_hovered_chip(self):
        self.selected_chip_index = -1
        for i, renderer in enumerate(self.chip_renderers):
            if renderer.check_collision(self.mouse_x, self.mouse_y):
                self.selected_chip_index = i
                break

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

    def update(self):

        if self.state == self.STATE_CHIP_MOVING:
            selected_renderer = self.chip_renderers[self.selected_chip_index]

            relative_offset = (self.mouse_x - self.mouse_start_position[0], self.mouse_y - self.mouse_start_position[1])

            target_offset = (self.mouse_start_offset[0] + relative_offset[0], self.mouse_start_offset[1] + relative_offset[1])
            selected_renderer.move_to(target_offset[0], target_offset[1])

        self.draw()

    def draw(self):
        self.surface.fill(self.EDITOR_BACKGROUND)

        for i, renderer in enumerate(self.chip_renderers):
            if i == self.selected_chip_index:
                # skip the selected chip to later draw it on top
                continue

            renderer.update_hovered_pin(self.mouse_x, self.mouse_y)
            renderer.draw(self.surface)

        # draw the selected chip on top
        if self.selected_chip_index != -1:
            renderer = self.chip_renderers[self.selected_chip_index]
            renderer.draw_border(self.surface)
            renderer.update_hovered_pin(self.mouse_x, self.mouse_y)
            renderer.draw(self.surface)


    # def package(self, name=None):
    #     ChipFactory = custom_chip_factory(self.input_signals, self.output_signals)
    #     self.clear()
    #     return ChipFactory
