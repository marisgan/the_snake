from random import choice
from sys import exit

import pygame as pg

from gameparts import (  # noqa
    GameObject, Snake, Apple, Game, TURNS, MODES, TIMER, SCREEN_WIDTH,
    SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, BOARD_BACKGROUND_COLOR,
    UP, DOWN, LEFT, RIGHT, screen, surface, clock, TURNS_BOT
)


def handle_user_events(snake, snacks, bots):
    """Общая обработка действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            handle_quit()
        if event.type == pg.KEYDOWN:
            handle_keys(event.key, snake, snacks, bots)


def handle_keys(event_key, snake, snacks, bots):
    """Обработка нажатия клавиш"""
    if event_key == pg.K_ESCAPE:
        handle_quit()
    if event_key in [turn[1] for turn in TURNS]:
        snake.update_direction(
            TURNS.get((snake.direction, event_key))
        )
    if event_key in [mode[1] for mode in MODES]:
        snake.toggle_speed(
            MODES.get((snake.speed_mode, event_key))
        )
        Game.screen_refresh()
    if event_key == pg.K_3:
        [snack.toggle_snack() for snack in snacks]
        Game.screen_refresh()
    if event_key == pg.K_4:
        [bot.toggle_snake() for bot in bots]
        Game.screen_refresh()


def handle_quit():
    """Выход из программы"""
    pg.quit()
    exit()


def main():
    """Запуск игры"""
    pg.init()
    global TIMER
    game = Game()
    Game.screen_refresh()
    [bot.toggle_snake() for bot in game.bots]
    [snack.toggle_snack() for snack in game.snacks[1:]]
    game.eat_elephant()
    while True:
        clock.tick(game.snake.speed)
        handle_user_events(game.snake, game.snacks[1:], game.bots)
        game.snake.show_info()
        game.move_snakes()
        game.handle_selfbite()
        TIMER += 1
        if not TIMER % 140:
            game.bots[0].update_direction(
                choice(TURNS_BOT.get(game.bots[0].direction))
            )
        if not TIMER % 200:
            game.bots[1].update_direction(
                choice(TURNS_BOT.get(game.bots[1].direction))
            )
        [game.handle_eat_snack(snack) for snack in game.snacks]
        for bot in game.bots:
            game.handle_smash(bot)
            game.handle_bot_capture(bot)
            [game.handle_steal_snack(bot, snack) for snack in game.snacks]
        screen.blit(surface, (0, 0))
        game.draw_objects()
        game.display_info()
        pg.display.update()


if __name__ == '__main__':
    main()
