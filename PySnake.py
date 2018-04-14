#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import random
from collections import deque
from datetime import datetime

import pygame
from PyQt5.QtWidgets import *
from pygame import *

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
    def __init__(self, width=800, height=600, wall_mode=True, difficulty=1):
        self.wall_mode = wall_mode
        self.pause = False
        self.__restart = False
        self.game_over = GameOverType.NULL
        self._clock = datetime.now()

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

        self.level[y].pop(x)
        self.level[y].insert(x, "x")
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
            self.level[old_y].pop(old_x)

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
                self.level[old_y].insert(old_x, ".")
                self.apple = False
            elif point == ".":
                # if you came across your body
                self.game_over = GameOverType.TOGGLE_SELF
            else:
                self.level[old_y].insert(old_x, " ")

            self.level[y].pop(x)
            self.level[y].insert(x, ".")
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
                "GAME OVER", False, (255, 0, 0)
            )
            msg1 = "You have touched the tail."
            msg2 = "You have gone beyond the limits of the playing field."
            message_hud = game_font.render(
                msg1 if self.game_over == GameOverType.TOGGLE_SELF else msg2,
                False, (255, 255, 255)
            )
            message_restart = game_font.render(
                "Press \"ENTER\" for a start new game.",
                False, (255, 255, 255)
            )
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", False, (255, 255, 255)
            )

            screen.blit(game_over_hud, (10, 10))
            screen.blit(message_hud, (10, 30))
            screen.blit(message_restart, (10, 50))
            screen.blit(points_hud, (10, 80))
        else:
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", False, (255, 255, 255)
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

            pygame.display.update()


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.__ok = False
        self.res_label = QLabel("Resolution", self)
        self.res_combo = QComboBox(self)
        self.res_combo.addItems(["800x600", "1024x768"])
        self.dif_label = QLabel("Difficulty", self)
        self.dif_combo = QComboBox(self)
        self.dif_combo.addItems(["Easy", "Normal", "Hard"])
        self.wm_label = QLabel("Wall mode", self)
        self.wm_check = QCheckBox(self)
        self.button = QPushButton("Play", self)
        self.init_ui()

    def init_ui(self):
        self.res_combo.move(65, 10)
        self.res_label.move(10, 13)
        self.dif_combo.move(65, 40)
        self.dif_combo.currentIndexChanged.connect(
            self._difficulty_handler
        )
        self.dif_label.move(10, 43)
        self.wm_check.move(65, 70)
        self.wm_label.move(10, 70)
        self.button.resize(60, 60)
        self.button.move(170, 20)
        self.button.clicked.connect(self.ok_close)
        self.button.setFocus()
        self.setGeometry(300, 300, 250, 100)
        self.setWindowTitle('PSnake - Conf')
        self.show()

    def ok_close(self):
        self.__ok = True
        self.close()

    def _difficulty_handler(self, difficulty):
        if difficulty == 2:
            self.wm_check.setChecked(False)
            self.wm_check.setDisabled(True)
        else:
            self.wm_check.setDisabled(False)

    def get_params(self):
        res = self.res_combo.currentText()
        w_mode = self.wm_check.isChecked()
        return {
            "ok": self.__ok, "res": res.split("x"), "wall_mode": w_mode,
            "difficulty": self.dif_combo.currentIndex()
        }


if __name__ == "__main__":
    import sys
    """       _
          .__(.)< (MEOW)
    ~~~~~~~\___)~~~~~~~~
     ~  ~ ~   ~ ~    ~ 
    """

    app = QApplication(sys.argv)
    ex = Widget()
    app.exec_()
    args = ex.get_params()
    if args['ok']:
        while True:
            Game(
                width=int(args['res'][0]),
                height=int(args['res'][1]),
                wall_mode=args['wall_mode'],
                difficulty=int(args['difficulty']) + 1
            )
