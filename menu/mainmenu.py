from collections import Counter

import pygame_menu
from pygame.constants import K_SPACE, K_a, K_d
from pygame.mixer import *
import pygame


class MainMenu(pygame_menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__(height=300, width=400, title='Main menu', theme=pygame_menu.themes.THEME_BLUE)
        self.add.selector('Difficulty :',
                          [('Easy', 0), ('Normal', 1), ('Hard', 2)],
                          onchange=self.set_difficulty)
        self.play = self.add.button('Start Game', self.start_game)

        self.settings = self.add.button('Settings', self.show_setting_menu)

        self.add.range_slider("Volume",
                              default=80,
                              range_values=(0, 100),
                              increment=1,
                              value_format=lambda x: str(int(x)),
                              onchange=self.set_volume)

        self.add.button('Quit', self.quit)

        self._game_over = False
        self.during_game = False
        self.show = False
        self.difficulty = 1
        self.volume_ = 5
        self.exit = False
        self.config_menu = ConfigMenu()
        self.pause_menu = PauseMenu()

    def start_game(self):
        self._game_over = False
        self.during_game = True
        self.play.hide()
        self.show = False
        self.disable()

    def show_setting_menu(self):
        self.config_menu.enable()
        self.config_menu.mainloop(self.surface)

    def mainloop(self, surface):
        self.surface = surface
        super(MainMenu, self).mainloop(surface)

    def quit(self):
        self.show = False
        self.disable()
        self.exit = True

    def set_difficulty(self, *args):
        self.difficulty = args[1]

    def set_volume(self, v):
        self.volume_ = int(v)
        music.set_volume(self.volume)

    def game_over(self):
        self._game_over = True
        self.during_game = False
        self.play.show()
        self.set_show()

    def is_game_over(self):
        return self._game_over

    @property
    def volume(self):
        return self.volume_ / 100

    @property
    def left_key(self):
        return self.config_menu.left_key

    @property
    def right_key(self):
        return self.config_menu.right_key

    @property
    def jump_key(self):
        return self.config_menu.jump_key

    def set_show(self):
        if self.during_game:
            self.pause_menu.enable()
            self.pause_menu.mainloop(self.surface)

        if self.pause_menu.resume_game:
            self.disable()
        else:
            self.show = True
            self.enable()


class ConfigMenu(pygame_menu.Menu):
    def __init__(self):
        super(ConfigMenu, self).__init__(height=300, width=400, title='Settings', theme=pygame_menu.themes.THEME_BLUE)
        self.back = self.add.button('To Main Menu', self.go_back)
        self.key_inputs = {}
        self.key_old_values = {}
        self.key_inputs_pressed = {'LEFT': K_a, 'RIGHT': K_d, 'JUMP': K_SPACE}
        for i in [('LEFT', 'a'), ('RIGHT', 'd'), ('JUMP', 'space')]:
            direction = i[0]
            key = f'key.{i[1]}'
            self.key_inputs[direction] = self.add.text_input(f"{direction}: ", default=key,
                                                             cursor_selection_enable=False,
                                                             copy_paste_enable=False,
                                                             onselect=self.input_selected,
                                                             onreturn=self.unselect,
                                                             onchange=self.change_control)
            self.key_old_values[direction] = i[1]
        self.who_selected = ''

    def go_back(self):
        self.disable()

    def change_control(self, key):
        p = pygame.key.get_pressed()
        for i in range(len(p)):
            if p[i]:
                break
        to_be_delete = list('key.' + self.key_old_values[self.who_selected])
        if i == 32:
            new_key = 'space'
        else:
            new_key = ''
            for k in key:
                if k in to_be_delete:
                    to_be_delete.remove(k)
                else:
                    new_key += k

        self.key_inputs_pressed[self.who_selected] = i
        self.key_inputs[self.who_selected].set_value(f'key.{new_key}')
        self.key_old_values[self.who_selected] = new_key

    def unselect(self, *args):
        self.key_inputs[self.who_selected].select(False)

    def input_selected(self, *args):
        if args:
            if args[0]:
                self.who_selected = args[1].get_title()[:-2]

    @property
    def left_key(self):
        return self.key_inputs_pressed['LEFT']

    @property
    def right_key(self):
        return self.key_inputs_pressed['RIGHT']

    @property
    def jump_key(self):
        return self.key_inputs_pressed['JUMP']


class PauseMenu(pygame_menu.Menu):
    def __init__(self):
        super(PauseMenu, self).__init__(height=300, width=400, title='Pasue Menu', theme=pygame_menu.themes.THEME_BLUE)
        self.back = self.add.button('To Main Menu', self.go_back)
        self._resume = self.add.button('Resume', self.resume)
        self.resume_game = False

    def go_back(self):
        self.resume_game = False
        self.disable()

    def resume(self):
        self.resume_game = True
        self.disable()


if __name__ == '__main__':
    import pygame
    import pygame_menu

    pygame.init()
    surface = pygame.display.set_mode((600, 400))
    menu = MainMenu()
    menu.mainloop(surface)
