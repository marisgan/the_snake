# constants.py
"""Модуль, содержащий константы и переменные проекта THE_SNAKE"""

import pygame as pg

# Размеры экрана и сетки
GRID_SIZE = 40
GRID_WIDTH = 22
GRID_HEIGHT = 16
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
# Координаты направлений движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
# Правила для поворотов змейки при нажатии на стрелки
TURNS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}
# Правила поворотов для змеебота
TURNS_BOT = {
    LEFT: (LEFT, UP, DOWN),
    RIGHT: (RIGHT, UP, DOWN),
    UP: (UP, LEFT, RIGHT),
    DOWN: (DOWN, LEFT, RIGHT)
}
# Цвета в формате RGB
BOARD_BACKGROUND_COLOR = (27, 27, 30)
STEALTH_COLOR = (0, 0, 0, 0)
TEXT_COLOR = (240, 240, 240)
SNAKE_COLOR = (240, 190, 40)
APPLE_COLOR = (240, 30, 90)
BOT_COLORS = [
    (50, 100, 200),
    (10, 50, 200)
]
SNACK_COLORS = [
    (150, 0, 200),
    (240, 0, 180),
    (220, 100, 0),
    (30, 200, 100),
    (100, 100, 100),
    (80, 80, 80),
    (60, 60, 60)
]
# Контроль скорости
SPEED_DELTA = 20
EASY_START_SPEED = 200
HARD_START_SPEED = EASY_START_SPEED * 2
clock = pg.time.Clock()
TIMER = 0
# Правила переключения режимов скорости
MODES = {
    (EASY_START_SPEED, pg.K_2): HARD_START_SPEED,
    (HARD_START_SPEED, pg.K_1): EASY_START_SPEED
}
MODES_DISPLAY = {
    EASY_START_SPEED: 'ИЗИ',
    HARD_START_SPEED: 'ХАРД'
}
# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
