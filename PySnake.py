#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import random
from collections import deque
from datetime import datetime
from tkinter import *

from pygame import *
import pygame

__version__ = '1.0'


class Move:
    """movement codes"""
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class GameOverType:
    """game over codes"""
    NULL = 0
    OUT_OF_PLACE = 1
    TOGGLE_SELF = 2


class Game:
    def __init__(self, width: int = 800, height: int = 600,
                 wall_mode: bool = True, difficulty: int = 1):
        self.wall_mode = wall_mode
        self.pause = False
        self.__restart = False
        self.game_over = GameOverType.NULL
        self._clock = datetime.now()
        self._internal_clock = pygame.time.Clock()

        # game difficulty
        self._tick = {
            1: .1,
            2: .05,
            3: .03
        }.get(difficulty)

        self.WIN_WIDTH = width
        self.WIN_HEIGHT = height
        self.DISPLAY = (self.WIN_WIDTH, self.WIN_HEIGHT)
        self.BACKGROUND_COLOR = "#000000"
        self.apple = False

        self.BLOCK_WIDTH = 16
        self.BLOCK_HEIGHT = 16
        self.SNAKE_COLOR = "#FF6262"
        self.APPLE_COLOR = "#8db600"

        # create level
        self.level_width = self.WIN_WIDTH // self.BLOCK_WIDTH
        self.level_height = self.WIN_HEIGHT // self.BLOCK_HEIGHT
        self.level = [
            [" " for _ in range(0, self.level_width + 1)]
            for _ in range(0, self.level_height)
        ]

        # install snake
        self.snake_path = deque()
        self.snake_len = 10
        self.move_direction = Move.RIGHT
        for point in range(self.snake_len):
            self.level[self.level_height // 2].pop(point)
            self.level[self.level_height // 2].insert(point, ".")
            self.snake_path.append((self.level_height // 2, point))

        self.main()

    def get_apple(self):
        """Generate `apple` on map

        :return:
        """

        def _():
            return random.randint(0, self.level_height - 1), \
                   random.randint(0, self.level_width - 1)

        y, x = _()
        while self.level[y][x] == ".":
            y, x = _()

        self.level[y][x] = 'x'
        self.apple = True

    def move(self):
        """Implements the movement of the snake relative to the current
        direction and time of the tick (difficulty).

        :return:
        """
        # if not enough time has passed...
        if (datetime.now() - self._clock).total_seconds() < self._tick:
            return

        self._clock = datetime.now()

        y, x = self.snake_path[-1]
        if self.move_direction == Move.UP:
            y -= 1
        elif self.move_direction == Move.RIGHT:
            x += 1
        elif self.move_direction == Move.DOWN:
            y += 1
        else:  # Move.LEFT
            x -= 1

        if (
                y not in range(self.level_height)
                or x not in range(self.level_width)
        ) and not self.wall_mode:
            self.game_over = GameOverType.OUT_OF_PLACE
        else:
            old_y, old_x = self.snake_path.popleft()
            self.level[old_y][old_x] = ''

            if self.wall_mode:
                # we implement an infinite-looped playing field
                if y not in range(self.level_height):
                    y = 0 if y >= self.level_height else self.level_height - 1
                elif x not in range(self.level_width):
                    x = 0 if x >= self.level_width else self.level_width - 1

            point = self.level[y][x]
            if point == "x":
                # if you ate an Apple, increase the length of the snake
                self.snake_len += 1
                self.snake_path.appendleft((old_y, old_x))
                self.level[old_y][old_x] = "."
                self.apple = False
            elif point == ".":
                # if you came across your body
                self.game_over = GameOverType.TOGGLE_SELF
            else:
                self.level[old_y][old_x] = " "

            self.level[y][x] = '.'
            self.snake_path.append((y, x))

    def render(self, screen):
        """Draw playing field with objects.

        :param screen: current screen
        :return:
        """
        x = y = 0
        for row in self.level:
            for col in row:
                if col in ["x", "."]:
                    pf = Surface((self.BLOCK_WIDTH, self.BLOCK_HEIGHT))
                    pf.fill(Color(
                        self.APPLE_COLOR if col == "x" else self.SNAKE_COLOR
                    ))
                    screen.blit(pf, (x, y))
                x += self.BLOCK_WIDTH
            y += self.BLOCK_HEIGHT
            x = 0

    def hud(self, screen, game_font):
        """Draw hud canvas.

        :param screen: current screen
        :param game_font: font file io
        :return:
        """
        if self.game_over != GameOverType.NULL:
            self.pause = True
            game_over_hud = game_font.render(
                "GAME OVER", True, (255, 0, 0)
            )
            msg1 = "You have touched the tail."
            msg2 = "You have gone beyond the limits of the playing field."
            message_hud = game_font.render(
                msg1 if self.game_over == GameOverType.TOGGLE_SELF else msg2,
                True, (255, 255, 255)
            )
            message_restart = game_font.render(
                "Press \"ENTER\" for a start new game.",
                True, (255, 255, 255)
            )
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", True, (255, 255, 255)
            )

            screen.blit(game_over_hud, (10, 10))
            screen.blit(message_hud, (10, 30))
            screen.blit(message_restart, (10, 50))
            screen.blit(points_hud, (10, 80))
        else:
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", True, (255, 255, 255)
            )
            screen.blit(points_hud, (5, 5))

    def main(self):
        """main game loop"""
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode(self.DISPLAY)
        pygame.display.set_caption("PSnake")
        pygame.display.set_icon(pygame.image.load("game.ico").convert_alpha())
        bg = Surface((self.WIN_WIDTH, self.WIN_HEIGHT))
        bg.fill(Color(self.BACKGROUND_COLOR))
        game_font = pygame.font.Font('game_font.ttf', 18)
        game_font.set_bold(True)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        raise SystemExit()
                    elif e.key in [pygame.K_UP, pygame.K_w]:
                        if self.move_direction != Move.DOWN:
                            self.move_direction = Move.UP
                    elif e.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.move_direction != Move.LEFT:
                            self.move_direction = Move.RIGHT
                    elif e.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.move_direction != Move.UP:
                            self.move_direction = Move.DOWN
                    elif e.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.move_direction != Move.RIGHT:
                            self.move_direction = Move.LEFT
                    elif e.key == pygame.K_PAUSE:
                        if not self.game_over:
                            self.pause = not self.pause
                    elif e.key == pygame.K_RETURN:
                        if self.pause \
                                and self.game_over != GameOverType.NULL:
                            pygame.quit()
                            self.__restart = True
                            break

            if self.__restart:
                break

            screen.blit(bg, (0, 0))
            if not self.apple:
                self.get_apple()
            if not self.pause:
                self.move()
            self.render(screen)
            self.hud(screen, game_font)
            # TODO: move to settings
            # fps = game_font.render(str(self._internal_clock.get_fps()),
            #                        False,
            #                        (255, 255, 255))
            # screen.blit(fps, (100, 0))

            pygame.display.update()

            self._internal_clock.tick(120)


class SettingsGUI:
    def __init__(self):
        self.result = False
        self.root = Tk()
        self.root.title('PySnake')
        self.root.iconbitmap('game.ico')

        Label(self.root, text="Resolution").grid(row=1, column=1)
        self.res_combo = StringVar(self.root)
        self.res_combo.set("800x600")
        res_option = OptionMenu(self.root, self.res_combo,
                                '800x600', '1024x768')
        res_option.grid(row=1, column=2)

        Label(self.root, text="Difficulty").grid(row=2, column=1)
        self.dif_list = ["Easy", "Normal", "Hard"]
        self.dif_combo = StringVar(self.root)
        self.dif_combo.set(self.dif_list[0])
        dif_option = OptionMenu(self.root, self.dif_combo, *self.dif_list,
                                command=self._dif_handler)
        dif_option.grid(row=2, column=2)

        Label(self.root, text="Wall mode").grid(row=3, column=1)
        self.var_check = BooleanVar()
        self.wm_option = Checkbutton(self.root, variable=self.var_check)
        self.wm_option.grid(row=3, column=2)

        btn = Button(self.root, text="Play", width=30, height=5, bg="green")
        btn.focus_set()
        btn.bind("<Button-1>", self.ok_close)
        self.root.bind("<Return>", self.ok_close)
        btn.grid(row=4, column=1, columnspan=2)

    def call(self):
        """Call the game settings window and wait for the "play" button
        or exit.

        :return: game settings dictionary
        """
        self.root.mainloop()

        if not self.result:
            exit()

        _res = self.res_combo.get().split('x')
        return dict(
            width=int(_res[0]),
            height=int(_res[1]),
            wall_mode=self.var_check.get(),
            difficulty=self.dif_list.index(self.dif_combo.get()) + 1
        )

    def ok_close(self, event):
        self.result = True
        self.root.destroy()

    def _dif_handler(self, value):
        if self.dif_list.index(value) > 1:
            self.wm_option.deselect()
            self.wm_option.config(state=DISABLED)
        else:
            self.wm_option.config(state=ACTIVE)


if __name__ == "__main__":
    """       _
          .__(.)< (MEOW)
    ~~~~~~~\___)~~~~~~~~
     ~  ~ ~   ~ ~    ~ 
    """
    config_window = SettingsGUI()
    game_args = config_window.call()
    while True:  # in case of game over, start game again
        Game(**game_args)
