import pygame_menu
from pygame.constants import K_SPACE, K_a, K_d
from pygame.mixer import *

class Menu(pygame_menu.Menu):
    def __init__(self):
        super(Menu, self).__init__(height=300, width=400, title='Settings', theme=pygame_menu.themes.THEME_BLUE)
        self.add.selector('Difficulty :',
                          [('Easy', 0), ('Normal', 1), ('Hard', 2)],
                          onchange=self.set_difficulty)

        self.play = self.add.button('Continue', self.start_game)

        self.add.range_slider("Volume",
                              default=80,
                              range_values=(0, 100),
                              increment=1,
                              value_format=lambda x: str(int(x)),
                              onchange=self.set_volume)

        self.key_inputs = {}
        self.key_inputs_pressed = {'LEFT': K_a , 'RIGHT': K_d, 'JUMP': K_SPACE}
        for i in [('LEFT', 'a'), ('RIGHT', 'd'), ('JUMP', 'space')]:
            direction = i[0]
            key = i[1]
            self.key_inputs[direction] = self.add.text_input(f"{direction}: ", default=f'key.{key}',
                                                             cursor_selection_enable=False,
                                                             copy_paste_enable=False,
                                                             onselect=self.input_selected,
                                                             onreturn=self.unselect,
                                                             onchange=self.change_control)
        self.add.button('Quit', self.quit)

        self._game_over = False
        self.show = False
        self.difficulty = 1
        self.volume_ = 5
        self.exit = False
        self.who_selected = ''

    def unselect(self, *args):
        self.key_inputs[self.who_selected].select(False)

    def start_game(self):
        self._game_over = False
        self.show = False
        self.play.set_title('Continue')
        self.disable()

    def quit(self):
        self.show = False
        self.disable()
        self.exit = True

    def set_difficulty(self, *args):
        self.difficulty = args[1]

    def set_volume(self, v):
        self.volume_ = int(v)
        music.set_volume(self.volume)

    def input_selected(self, *args):
        if args:
            if args[0]:
                self.who_selected = args[1].get_title()[:-2]

    def change_control(self, key):
        p = pygame.key.get_pressed()
        for i in range(len(p)):
            if p[i]:
                break

        if key[-1] == ' ':
            new_key = 'key.space'
        else:
            new_key = key[:4] + key[-1]
        self.key_inputs[self.who_selected].set_value(new_key)
        self.key_inputs_pressed[self.who_selected] = i

    def game_over(self):
        self._game_over = True
        self.play.set_title('Start new game')
        self.set_show()

    def is_game_over(self):
        return self._game_over

    @property
    def volume(self):
        return self.volume_ / 100

    @property
    def left_key(self):
        return self.key_inputs_pressed['LEFT']

    @property
    def right_key(self):
        return self.key_inputs_pressed['RIGHT']

    @property
    def jump_key(self):
        return self.key_inputs_pressed['JUMP']

    def set_show(self):
        self.show = True
        self.enable()


if __name__ == '__main__':
    import pygame
    import pygame_menu

    pygame.init()
    surface = pygame.display.set_mode((600, 400))
    menu = Menu()
    menu.mainloop(surface)
