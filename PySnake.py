#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import argparse
import platform
import random
import time as t
from collections import deque
from datetime import datetime
from itertools import repeat
from tkinter import *

try:
    import pygame
    from pygame import *
except ImportError:
    raise SystemExit("Please install PyGame==1.9.3 with PIP.")

__version__ = '1.1'
RED_COLOR = "#FF6262"
GREEN_COLOR = "#8db600"
BLACK_COLOR = "#000000"
TICKS = {
    1: .08,
    2: .05,
    3: .03
}


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
    def __init__(self, context, width: int = 800, height: int = 600,
                 wall_mode: bool = True, max_apples: int = 1,
                 difficulty: int = 1):
        self.options = context
        self.wall_mode = wall_mode
        self.pause = False
        self.max_apples = max_apples
        self.__restart = False
        self.game_over = GameOverType.NULL
        self._clock = datetime.now()
        self._internal_clock = pygame.time.Clock()
        self.timer = 0
        self._timer = 0
        self.ptimer = 0
        self._ptimer = 0

        # game difficulty
        self._tick = TICKS.get(difficulty)

        self.WIN_WIDTH = width
        self.WIN_HEIGHT = height
        self.DISPLAY = (self.WIN_WIDTH, self.WIN_HEIGHT)
        self.BACKGROUND_COLOR = BLACK_COLOR
        self.apples_counter = 0

        self.BLOCK_WIDTH = 16
        self.BLOCK_HEIGHT = 16
        self.SNAKE_COLOR = RED_COLOR if difficulty < 3 else GREEN_COLOR
        self.APPLE_COLOR = GREEN_COLOR if difficulty < 3 else RED_COLOR

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
        self._tmp_move = Move.RIGHT
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
        while self.level[y][x] in [".", "x"]:
            y, x = _()

        self.level[y][x] = 'x'
        self.apples_counter += 1

    @property
    def is_tick(self):
        return (datetime.now() - self._clock).total_seconds() > self._tick

    def move(self):
        """Implements the movement of the snake relative to the current
        direction and time of the tick (difficulty).

        :return:
        """
        # if not enough time has passed...
        if not self.is_tick:
            return
        self.move_direction = self._tmp_move

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
                self.apples_counter -= 1
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
        if self.options.fps:
            fps_hud = game_font.render(
                f"{int(self._internal_clock.get_fps())}",
                True, (150, 150, 150)
            )
            fps_rect = fps_hud.get_rect()
            screen.blit(fps_hud, (self.WIN_WIDTH - fps_rect.right - 2, 0))

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
            timer_hud = game_font.render(
                f"Time: {t.strftime('%M:%S', t.gmtime(self.timer))}",
                True, (255, 255, 255)
            )

            screen.blit(game_over_hud, (10, 10))
            screen.blit(message_hud, (10, 30))
            screen.blit(message_restart, (10, 50))
            screen.blit(points_hud, (10, 80))
            screen.blit(timer_hud, (10, 100))
        else:
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", True,
                (150, 150, 150) if self.pause else (255, 255, 255)
            )
            screen.blit(points_hud, (5, 0))

            timer_hud = game_font.render(
                t.strftime('%M:%S', t.gmtime(self.timer)),
                True, (150, 150, 150) if self.pause else (255, 255, 255)
            )
            screen.blit(timer_hud, (5, 20))

            if self.pause:
                pause_hud = game_font.render(
                    f"PAUSE", True, (255, 255, 255)
                )
                pause_rect = pause_hud.get_rect()
                screen.blit(pause_hud, (
                    self.WIN_WIDTH / 2 - pause_rect.centerx,
                    self.WIN_HEIGHT / 2 - pause_rect.centery
                ))

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
        self._timer = t.time()

        while True:
            # #1 we need this to avoid turning two times in one tick (this can
            # happen if user will press two buttons rapidly)
            move = self._tmp_move

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.__restart = True
                        break
                    elif e.key in [pygame.K_UP, pygame.K_w]:
                        if self.move_direction != Move.DOWN:
                            move = Move.UP
                    elif e.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.move_direction != Move.LEFT:
                            move = Move.RIGHT
                    elif e.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.move_direction != Move.UP:
                            move = Move.DOWN
                    elif e.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.move_direction != Move.RIGHT:
                            move = Move.LEFT
                    elif e.key in [pygame.K_PAUSE, pygame.K_SPACE]:
                        if not self.game_over:
                            self._change_pause()
                    elif e.key == pygame.K_RETURN:
                        if self.pause \
                                and self.game_over != GameOverType.NULL:
                            self.__restart = True
                            break
                        elif self.pause:
                            self._change_pause()

            self._tmp_move = move

            if self.__restart:
                break

            screen.blit(bg, (0, 0))
            if self.apples_counter < self.max_apples:
                repeat(self.get_apple(), self.max_apples - self.apples_counter)
            if not self.pause:
                self.timer = t.time() - self._timer - self.ptimer
                self.move()
            self.render(screen)
            self.hud(screen, game_font)
            pygame.display.update()
            self._internal_clock.tick(120)

        pygame.quit()

    def _change_pause(self):
        self.pause = not self.pause
        if self.pause:
            self._ptimer = t.time()
        else:
            self.ptimer += t.time() - self._ptimer


class SettingsGUI:
    def __init__(self):
        self.result = False
        self.root = Tk()
        self.root.title('PySnake')

        # TODO: Undefined behavior on Linux
        if platform.system() != "Linux":
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

        Label(self.root, text="Apples count").grid(row=3, column=1)
        self.ap_count_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.ap_count_combo = StringVar(self.root)
        self.ap_count_combo.set(self.ap_count_list[0])
        ap_count_option = OptionMenu(self.root, self.ap_count_combo,
                                     *self.ap_count_list)
        ap_count_option.grid(row=3, column=2)

        Label(self.root, text="Wall mode").grid(row=4, column=1)
        self.var_check = BooleanVar()
        self.wm_option = Checkbutton(self.root, variable=self.var_check)
        self.wm_option.grid(row=4, column=2)

        btn = Button(self.root, text="Play", width=30, height=5, bg="green")
        btn.focus_set()
        btn.bind("<Button-1>", self.ok_close)
        self.root.bind("<Return>", self.ok_close)
        btn.grid(row=5, column=1, columnspan=2)

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
            max_apples=self.ap_count_list.index(self.ap_count_combo.get()) + 1,
            difficulty=self.dif_list.index(self.dif_combo.get()) + 1
        )

    def ok_close(self, _):
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
    parser = argparse.ArgumentParser(description="Hi")
    parser.add_argument('-f', '--fps', dest='fps', action='store_true',
                        help='Display FPS')
    context = parser.parse_args()

    while True:  # in case of game over, start game again
        config_window = SettingsGUI()
        game_args = config_window.call()
        Game(context, **game_args)
