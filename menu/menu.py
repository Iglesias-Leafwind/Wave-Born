import pygame_menu


class Menu(pygame_menu.Menu):
    def __init__(self):
        super(Menu, self).__init__(height=300, width=400, title='Settings', theme=pygame_menu.themes.THEME_BLUE)
        self.add.selector('Difficulty :',
                          [('Easy', 0), ('Normal', 1), ('Hard', 2)],
                          onchange=self.set_difficulty)

        self.add.button('Play', self.start_the_game)
        self.add.button('Quit', self.quit)

        self.add.range_slider("Volume",
                              default=5,
                              range_values=(0, 10),
                              increment=1,
                              value_format=lambda x: str(int(x)),
                              onchange=self.set_volume)
        self.show = False
        self.difficulty = 1
        self.volume = 5

    def start_the_game(self):
        self.quit()

    def quit(self):
        self.show = False
        self.disable()

    def set_difficulty(self, *args):
        self.difficulty = args[1]

    def set_volume(self, v):
        self.volume = int(v)

    def set_show(self):
        self.show = True
        self.enable()