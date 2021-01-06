from __future__ import annotations

import pygame as pg
from pygame import freetype

from app.chip import Chip, ChipPin

from .utils import draw_circle, render_text
from .holders import PinLocation

freetype.init()


class ChipRenderer:

    chip_text_font = freetype.SysFont("Noto Sans Medium", 1)

    PIN_RADIUS = 7
    PIN_MARGIN = 2

    PIN_DIAMETER = 2 * PIN_RADIUS

    TOTAL_RADIUS = PIN_RADIUS + PIN_MARGIN
    TOTAL_DIAMETER = 2 * TOTAL_RADIUS

    PIN_COLOR = (0, 0, 0)
    PIN_HOVER_COLOR = (178, 178, 178)

    CHIP_BACKGROUND = (57, 122, 152)
    CHIP_HOVER_BORDER_COLOR = (71, 71, 71)

    FONT_COLOR = (226, 235, 240)
    FONT_SIZE = 14

    def __init__(self, chip: Chip, position: tuple = (0, 0)):
        # the chip this renderer is responsible for
        self.chip = chip
        # position of chip in world coordinates
        self.position = position

        # location (index and type) of pin currently under the mouse 
        self.hovered_pin_type = PinLocation.PL_NONE
        self.hovered_pin_index = -1

        # cached y-coordinates (relative to top left of chip) of chip's input and output pins
        self.input_pins_y = []
        self.output_pins_y = []

        for i in range(chip.InputPinCount):
            y = self.TOTAL_DIAMETER * i + self.TOTAL_RADIUS
            self.input_pins_y.append(y)

        for i in range(chip.OutputPinCount):
            y = self.TOTAL_DIAMETER * i + self.TOTAL_RADIUS
            self.output_pins_y.append(y)

        # rendered chip name (calculated one time only as name does not change )
        self.chip_name_surface = render_text(self.chip_text_font, chip.name, self.FONT_SIZE, self.FONT_COLOR)

        self.height = max(self.input_pins_y[-1], self.output_pins_y[-1]) + self.TOTAL_RADIUS + 1 # for some reason this 1 balances height
        self.width = 2 * self.PIN_RADIUS + 8 + self.chip_name_surface.get_width()

        # coordinates (relative to top left of chip) where chip's name will be rendered
        self.txt_x = self.PIN_RADIUS + 4
        self.txt_y = (self.height - self.chip_name_surface.get_height()) // 2

        # just centering things, nothing too fancy
        input_padding = (self.height - self.input_pins_y[-1] - self.TOTAL_RADIUS) // 2
        output_padding = (self.height - self.output_pins_y[-1] - self.TOTAL_RADIUS) // 2

        for i in range(chip.InputPinCount):
            self.input_pins_y[i] += input_padding

        for i in range(chip.OutputPinCount):
            self.output_pins_y[i] += output_padding

        self.bound_width = self.width + self.PIN_DIAMETER
        self.bound_height = self.height + self.PIN_DIAMETER

    def draw(self, surface):
        # draw the actual chip
        pg.draw.rect(surface, self.CHIP_BACKGROUND, pg.Rect(self.position[0], self.position[1], self.width, self.height))

        # draw input and output pins
        for i, y in enumerate(self.input_pins_y):
            if self.hovered_pin_type == PinLocation.PL_CHIP_IN and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            draw_circle(surface, self.position[0], self.position[1] + y, self.PIN_RADIUS, color)

        for i, y in enumerate(self.output_pins_y):
            if self.hovered_pin_type == PinLocation.PL_CHIP_OUT and self.hovered_pin_index == i:
                color = self.PIN_HOVER_COLOR
            else:
                color = self.PIN_COLOR
            draw_circle(surface, self.position[0] + self.width, self.position[1] + y, self.PIN_RADIUS, color)

        # render chip name
        surface.blit(self.chip_name_surface, (self.position[0] + self.txt_x, self.position[1] + self.txt_y))


    def get_pin_pos(self, pin_type, index):
        """"
            Returns the coordinates of pin identified by its type and index
        """
        if pin_type == PinLocation.PL_CHIP_IN:
            x = 0
            y = self.input_pins_y[index]
        else:
            x = self.width
            y = self.output_pins_y[index]

        return (self.position[0] + x, self.position[1] + y)        


    def update_hovered_pin(self, mouse_x, mouse_y):
        """
            Calculates (and updates) what pin is currently under the mouse
        """

        self.hovered_pin_index = -1
        self.hovered_pin_type = PinLocation.PL_NONE

        x = self.position[0]

        # Since precision is not that important and the size
        # of pins is relatively small, mouse coordinates are
        # only checked to be inside the square of side length
        # equal to the pin's diameter and centered at the pin
        # center as it is faster
        if mouse_x >= x - self.PIN_RADIUS and mouse_x <= x + self.PIN_RADIUS:
            for i, y in enumerate(self.input_pins_y):
                pin_y = self.position[1] + y 
                if mouse_y >= pin_y - self.PIN_RADIUS and mouse_y <= pin_y + self.PIN_RADIUS:
                    self.hovered_pin_type = PinLocation.PL_CHIP_IN
                    self.hovered_pin_index = i
                    return (self.hovered_pin_type, self.hovered_pin_index)
                    

        x = self.position[0] + self.width
        if mouse_x >= x - self.PIN_RADIUS and mouse_x <= x + self.PIN_RADIUS:
            for i, y in enumerate(self.output_pins_y):
                pin_y = self.position[1] + y
                if mouse_y >= pin_y - self.PIN_RADIUS and mouse_y <= pin_y + self.PIN_RADIUS:
                    self.hovered_pin_type = PinLocation.PL_CHIP_OUT
                    self.hovered_pin_index = i
                    return (self.hovered_pin_type, self.hovered_pin_index)

        return None


    def draw_chip_border(self, surface):
        """
            Draws a border around the chip to highlight it
        """
        left = self.position[0] - self.PIN_RADIUS
        top = self.position[1] - self.PIN_RADIUS

        pg.draw.rect(surface, self.CHIP_HOVER_BORDER_COLOR, pg.Rect(left, top, self.bound_width, self.bound_height))

    def check_collision(self, x, y):
        """
            Checks if given coordinates is inside the chip
        """
        # GOLD: I wasted 1 hour debugging because I accidently swapped the indices 0 and 1 below
        left = self.position[0] - self.PIN_RADIUS
        top = self.position[1] - self.PIN_RADIUS

        bottom = top + self.bound_height
        right = left + self.bound_width

        return x >= left and x <= right and y >= top and y <= bottom

    def move_to(self, x, y):
        self.position = (x, y)
