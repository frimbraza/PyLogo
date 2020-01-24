
# This file is the simulation engine. The engine consists of two loops. The top loop runs when the model is not
# running. It's in that loop where the user clicks, setup, go, exit, etc.
# The model loop runs the model. Once around that loop for each model tick.

from PyLogo.core.gui import SimpleGUI

import pygame as pg
from pygame.time import Clock


class SimEngine:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=11, bounce=True, fps=None):

        # Constants for the main loop in start() below.
        self.CTRL_D = 'D:68'
        self.CTRL_d = 'd:68'
        self.ESCAPE = 'Escape:27'
        self.FPS = 'FPS'
        self.NORMAL = 'normal'
        self.Q = 'Q'
        self.q = 'q'

        self.clock = Clock()
        self.fps = 60
        self.idle_fps = 10

        self.world = None

        self.simple_gui = SimpleGUI(model_gui_elements, caption=caption, patch_size=patch_size, bounce=bounce, fps=fps)
        self.window = self.simple_gui.window
        self.graph_point = None


    def draw_world(self):
        # Fill the screen with the background color, draw the world, and update the display.
        self.simple_gui.fill_screen()
        self.world.draw()
        pg.display.update()

    def model_loop(self):
        while True:
            (event, values) = self.window.read(timeout=10)

            if event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            fps = values.get('fps', None)
            if fps:
                self.fps = int(fps)

            if event == 'GoStop':
                # Disable the GO_ONCE button
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                break

            if self.world.done():
                self.window['GoStop'].update(disabled=True)
                break

            # TICKS are our local counter for the number of times we have gone around this loop.
            self.world.increment_ticks()
            self.world.save_values_and_step(event, values)
            self.draw_world()
            # The next line limits how fast the simulation runs. It is not a counter.
            self.clock.tick(self.fps)

        return self.NORMAL

    def top_loop(self, world_class, patch_class, turtle_class):
        self.world = world_class(patch_class, turtle_class)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        # Give event a value so that the while loop can look at it the first time through.
        event = None
        while event not in [self.ESCAPE, self.q, self.Q,
                            self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)

            if event in (None, self.simple_gui.EXIT):
                self.window.close()
                break

            if event == self.simple_gui.GRAPH:
                self.world.mouse_click(values['-GRAPH-'])
                self.draw_world()

            if event == self.simple_gui.SETUP:
                # fps = values.get('fps', None)
                # if fps:
                #     self.fps = fps
                self.window[self.simple_gui.GOSTOP].update(disabled=False)
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                self.world.reset_all()
                self.world.save_values_and_setup(event, values)
                self.draw_world()

            if event == self.simple_gui.GO_ONCE:
                self.world.increment_ticks()
                self.world.save_values_and_step(event, values)
                self.draw_world()

            if event == self.simple_gui.GOSTOP:
                self.window[self.simple_gui.GOSTOP].update(text='stop', button_color=('white', 'red'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=True)
                self.window[self.simple_gui.SETUP].update(disabled=True)
                returned_value = self.model_loop()
                self.window['GoStop'].update(text='go', button_color=('white', 'green'))
                self.window[self.simple_gui.SETUP].update(disabled=False)
                self.world.final_thoughts()
                if returned_value == self.simple_gui.EXIT:
                    self.window.close()
                    break

            self.clock.tick(self.idle_fps)
