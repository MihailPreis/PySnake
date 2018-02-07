#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from time import sleep
from collections import deque

import pygame
from pygame import *


class Move:
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class GameOverType:
    NULL = 0
    OUT_OF_PLACE = 1
    TOGGLE_SELF = 2


class Game:
    def __init__(self, width=800, height=600):
        self.tick_time = 1
        self.different = 1  # TODO: finish him
        self.wall_mode = True  # TODO: finish him
        self.pause = False
        self.game_over = GameOverType.NULL

        self.WIN_WIDTH = width
        self.WIN_HEIGHT = height
        self.DISPLAY = (self.WIN_WIDTH, self.WIN_HEIGHT)
        self.BACKGROUND_COLOR = "#000000"
        self.apple = False

        self.BLOCK_WIDTH = 16  # / difficulty
        self.BLOCK_HEIGHT = 16  # / difficulty
        self.SNAKE_COLOR = "#FF6262"
        self.APPLE_COLOR = "#8db600"

        # create level
        self.level_width = self.WIN_WIDTH // self.BLOCK_WIDTH
        self.level_height = self.WIN_HEIGHT // self.BLOCK_HEIGHT
        self.level = [
            [" " for _ in range(0, self.level_width)]
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
        y, x = self.snake_path[-1]
        if self.move_direction == Move.UP:
            y -= 1
        elif self.move_direction == Move.RIGHT:
            x += 1
        elif self.move_direction == Move.DOWN:
            y += 1
        else:  # Move.LEFT
            x -= 1

        if y not in range(self.level_height) \
                or x not in range(self.level_width - 1):
            self.game_over = GameOverType.OUT_OF_PLACE
        else:
            old_y, old_x = self.snake_path.popleft()
            self.level[old_y].pop(old_x)

            point = self.level[y][x]
            if point == "x":
                self.snake_len += 1
                self.snake_path.appendleft((old_y, old_x))
                self.level[old_y].insert(old_x, ".")
                self.apple = False
            elif point == ".":
                self.game_over = GameOverType.TOGGLE_SELF
            else:
                self.level[old_y].insert(old_x, " ")

            self.level[y].pop(x)
            self.level[y].insert(x, ".")
            self.snake_path.append((y, x))

    def render(self, screen):
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
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", False, (255, 255, 255)
            )

            screen.blit(game_over_hud, (10, 10))
            screen.blit(message_hud, (10, 30))
            screen.blit(points_hud, (10, 60))
        else:
            points_hud = game_font.render(
                f"Point: {self.snake_len - 10}", False, (255, 255, 255)
            )
            screen.blit(points_hud, (5, 5))

    def main(self):
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode(self.DISPLAY)
        pygame.display.set_caption("PSnake")
        bg = Surface((self.WIN_WIDTH, self.WIN_HEIGHT))
        bg.fill(Color(self.BACKGROUND_COLOR))
        game_font = pygame.font.Font('game_font.ttf', 18)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit("QUIT")
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        raise SystemExit("QUIT")
                    elif e.key in [pygame.K_UP, pygame.K_w]:
                        if self.move_direction != Move.DOWN:
                            self.move_direction = Move.UP
                            print("UP")
                    elif e.key in [pygame.K_RIGHT, pygame.K_d]:
                        if self.move_direction != Move.LEFT:
                            self.move_direction = Move.RIGHT
                            print("RIGHT")
                    elif e.key in [pygame.K_DOWN, pygame.K_s]:
                        if self.move_direction != Move.UP:
                            self.move_direction = Move.DOWN
                            print("DOWN")
                    elif e.key in [pygame.K_LEFT, pygame.K_a]:
                        if self.move_direction != Move.RIGHT:
                            self.move_direction = Move.LEFT
                            print("LEFT")
                    elif e.key == pygame.K_PAUSE:
                        if not self.game_over:
                            self.pause = not self.pause
                            print(f"PAUSE {self.pause}")

            screen.blit(bg, (0, 0))
            if not self.apple:
                self.get_apple()
            self.hud(screen, game_font)
            if not self.pause:
                self.move()
            self.render(screen)

            pygame.display.update()
            sleep(.05)


if __name__ == "__main__":
    Game()
