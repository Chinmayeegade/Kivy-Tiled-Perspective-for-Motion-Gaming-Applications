import math

import kivy
from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.vertex_instructions import Quad, Triangle, Rectangle
from kivy.graphics.vertex_instructions import Ellipse
import random
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint


class FinalGame(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    vertical_lines = []
    v_lines_num = 6
    v_lines_spacing = 0.5
    horizontal_lines = []
    h_lines_num = 10
    h_lines_spacing = 0.15
    current_offset_y = 0
    speed_y = 0.5
    current_offset_x = 0
    current_y_loop = 0
    speed_x = 3
    current_speed_x = 0
    num_tiles = 300
    tiles = []
    tiles_coordinates = []

    score = NumericProperty(0)

    def __init__(self,**kwargs):
        super(FinalGame,self).__init__(**kwargs)
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tiles()

        self.generate_tiles_coordinates()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0/60.0)
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)

        self._keyboard = None

    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        else:
            return False
    def init_tiles(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(0, self.num_tiles):
                self.tiles.append(Quad())
    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))
    def generate_tiles_coordinates(self):
        last_y = 0
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1] + 1
        for i in range(len(self.tiles_coordinates), self.num_tiles):
            r = random.randint(-(int(self.v_lines_num/2)-1),(int(self.v_lines_num/2)-1))
            self.tiles_coordinates.append((r, last_y))
            last_y += 1
            #self.v_lines_num += 2
    def init_vertical_line(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(0,self.v_lines_num):
                self.vertical_lines.append(Line())
    def get_line_x_from_index(self, index):
        start_index = -int(self.v_lines_num/2)
        central_line_x = self.perspective_point_x
        spacing = self.v_lines_spacing * self.width
        offset = index - 0.5
        line_x = int(central_line_x + offset * spacing + self.current_offset_x)
        return line_x
    def get_line_y_from_index(self, index):
        spacing_y = self.h_lines_spacing * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y
    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y
    def update_tiles(self):
        for i in range(0, self.num_tiles):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1,y1,x2,y2,x3,y3,x4,y4]

    def update_vertical_lines(self):
        start_index = -int(self.v_lines_num/2)+1
        for i in range(start_index,start_index+self.v_lines_num):
            line_x = self.get_line_x_from_index(i)
            x1,y1 = self.transform(line_x,0)
            x2,y2 = self.transform(line_x,self.height)
            self.vertical_lines[i].points=[x1,y1,x2,y2 ]
    def init_horizontal_line(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(0,self.h_lines_num):
                self.horizontal_lines.append(Line())
    def update_horizontal_lines(self):
        start_index = -int(self.v_lines_num / 2) + 1
        end_index = start_index + self.v_lines_num - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0,self.h_lines_num):
            line_y = self.get_line_y_from_index(i)
            x1,y1 = self.transform(xmin, line_y)
            x2,y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points=[x1,y1,x2,y2 ]
    def transform(self,x,y):
        #return self.transform_2D(x,y)
        return self.transform_perspective(x,y)
    def transform_2D(self,x,y):
        return int(x),int(y)
    def transform_perspective(self,x,y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y
        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y/self.perspective_point_y
        factor_y = pow(factor_y, 2)
        tr_x = self.perspective_point_x + diff_x*factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.current_speed_x = self.speed_x
        elif keycode[1] == 'right':
            self.current_speed_x = -self.speed_x
        return True
    def _on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True
    def on_touch_down(self, touch):
        if touch.x < self.width/2:
            self.current_speed_x = self.speed_x
        else:
            self.current_speed_x = -self.speed_x
    def on_touch_up(self, touch):
        self.current_speed_x = 0


    def update(self, dt):
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        time_factor = dt*60
        speed = self.speed_y*self.height/100
        self.current_offset_y += speed*time_factor
        spacing_y = self.h_lines_spacing*self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_tiles_coordinates()
        speed2 = self.current_speed_x*self.width/100
        self.current_offset_x += speed2*time_factor



class FinalApp(App):
    def build(self):
        game = FinalGame()

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    FinalApp().run()

# References: FreeCodeCamp