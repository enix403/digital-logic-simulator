from __future__ import annotations
import contextlib

with contextlib.redirect_stdout(None):
    import pygame as pg
from pygame import freetype
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE,
    MOUSEBUTTONDOWN,
    MOUSEMOTION,
    MOUSEBUTTONUP
)


from app.rendering.chipeditor import ChipEditor

class Application:

    WINDOW_WIDTH = 1024
    WINDOW_HEIGTH = 576

    FPS_MAX = 60

    def __init__(self):

        pg.init()
         
        self.running = False
        self.clock = None
        self.main_window = None

        self.chip_editor = None

    def start(self):
        pg.display.set_caption('Digital Logic Simulation')
        self.main_window = pg.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGTH))
        self.clock = pg.time.Clock()

        self.chip_editor = ChipEditor(self.WINDOW_WIDTH, self.WINDOW_HEIGTH)

        self.running = True
        while self.running:
            self.clear()
            self.poll_events()
            self.update()

        pg.quit()

    def clear(self):
        self.main_window.fill((255, 255, 255))

    def poll_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.running = False
                return

            elif event.type == MOUSEMOTION:
                self.chip_editor.on_mouse_move(*pg.mouse.get_pos())
            
            elif event.type == MOUSEBUTTONDOWN:
                self.chip_editor.on_mouse_down()
                # if event.button == 3:
                #     callback_event = MouseDownEvent(MouseButton.Right, mouse_pos[0], mouse_pos[1])
                # elif event.button == 1:
                #     callback_event = MouseDownEvent(MouseButton.Left, mouse_pos[0], mouse_pos[1])
                # elif event.button == 4:
                #     callback_event = MouseScrollEvent(MouseScrollDirection.Up)
                # elif event.button == 5:
                #     callback_event = MouseScrollEvent(MouseScrollDirection.Down)

            elif event.type == MOUSEBUTTONUP:
                self.chip_editor.on_mouse_up()
                # if event.button == 3:
                    # callback_event = MouseReleaseEvent(MouseButton.Right, mouse_pos[0], mouse_pos[1])
                # elif event.button == 1:
                    # callback_event = MouseReleaseEvent(MouseButton.Left, mouse_pos[0], mouse_pos[1])

    def update(self):
        self.clock.tick(self.FPS_MAX)
    
        self.chip_editor.update()
        self.main_window.blit(self.chip_editor.RenderResult, (0, 0))

        pg.display.update()


        

# appl = Application()
# appl.start()