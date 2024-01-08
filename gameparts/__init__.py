# gameparts/__init__.py
"""Пакет модулей проекта THE_SNAKE"""

from .constants import (  # noqa
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    CENTER, UP, DOWN, LEFT, RIGHT, TURNS, TURNS_BOT, BOARD_BACKGROUND_COLOR,
    STEALTH_COLOR, TEXT_COLOR, SNAKE_COLOR, APPLE_COLOR, BOT_COLORS,
    SNACK_COLORS, TIMER, SPEED_DELTA, EASY_START_SPEED,
    HARD_START_SPEED, MODES, MODES_DISPLAY, screen, surface, clock
)
from .parts import (GameObject, Snake, Apple, Game)  # noqa
