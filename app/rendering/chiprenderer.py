from __future__ import annotations

import pygame as pg
from pygame import freetype

from app.chip import Chip, ChipPin
from .utils import draw_circle, render_text

freetype.init()


class ChipRenderer:

    chip_text_font = freetype.SysFont("Noto Sans Medium", 1)

    pin_radius = 7
    pin_margin = 2

    pin_diameter = 2 * pin_radius

    total_radius = pin_radius + pin_margin
    total_diameter = 2 * total_radius

    PIN_COLOR = (0, 0, 0)
    PIN_HOVER_COLOR = (178, 178, 178)

    WIRE_COLOR_OFF = (36, 39, 46)
    WIRE_COLOR_ON = (236, 34, 56)

    CHIP_BACKGROUND = (57, 122, 152)
    CHIP_HOVER_BORDER_COLOR = (71, 71, 71)

    FONT_COLOR = (226, 235, 240)
    FONT_SIZE = 14

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
            if self.hovered_pin_type == ChipPin.PinType.INPUT and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            draw_circle(surface, self.position[0], self.position[1] + y, self.pin_radius, color)

        for i, y in enumerate(self.output_pins_y):
            if self.hovered_pin_type == ChipPin.PinType.OUTPUT and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            draw_circle(surface, self.position[0] + self.width, self.position[1] + y, self.pin_radius, color)

        surface.blit(self.chip_name_surface, (self.position[0] + self.txt_x, self.position[1] + self.txt_y))


    def get_pin_pos(self, pin_type, index):
        if pin_type == ChipPin.PinType.INPUT:
            x = 0
            y = self.input_pins_y[index]
        else:
            x = self.width
            y = self.output_pins_y[index]

        return (self.position[0] + x, self.position[1] + y)        


    def update_hovered_pin(self, mouse_x, mouse_y):
        self.hovered_pin_index = -1
        self.hovered_pin_type = 0

        x = self.position[0]

        if mouse_x >= x - self.pin_radius and mouse_x <= x + self.pin_radius:
            for i, y in enumerate(self.input_pins_y):
                pin_y = self.position[1] + y 
                if mouse_y >= pin_y - self.pin_radius and mouse_y <= pin_y + self.pin_radius:
                    self.hovered_pin_type = ChipPin.PinType.INPUT
                    self.hovered_pin_index = i
                    return (self.hovered_pin_type, self.hovered_pin_index)
                    

        x = self.position[0] + self.width
        if mouse_x >= x - self.pin_radius and mouse_x <= x + self.pin_radius:
            for i, y in enumerate(self.output_pins_y):
                pin_y = self.position[1] + y 
                if mouse_y >= pin_y - self.pin_radius and mouse_y <= pin_y + self.pin_radius:
                    self.hovered_pin_type = ChipPin.PinType.OUTPUT
                    self.hovered_pin_index = i
                    return (self.hovered_pin_type, self.hovered_pin_index)



        return None


    def draw_chip_border(self, surface):
        left = self.position[0] - self.pin_radius
        top = self.position[1] - self.pin_radius

        pg.draw.rect(surface, self.CHIP_HOVER_BORDER_COLOR, pg.Rect(left, top, self.bound_width, self.bound_height))

    def check_collision(self, x, y):
        # GOLD: I wasted 1 hour debugging because I accidently swapped the indices 0 and 1 below
        left = self.position[0] - self.pin_radius
        top = self.position[1] - self.pin_radius

        bottom = top + self.bound_height
        right = left + self.bound_width

        return x >= left and x <= right and y >= top and y <= bottom

    def move_to(self, x, y):
        self.position = (x, y)
