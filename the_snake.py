import pygame as pg

from gameparts import (  # noqa
    GameObject, Snake, Apple, Game, SCREEN_WIDTH,
    SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, BOARD_BACKGROUND_COLOR,
    UP, DOWN, LEFT, RIGHT, screen, surface, clock
)


def main():
    """Запуск игры"""
    pg.init()
    timer = 0
    game = Game()
    Game.screen_refresh()
    [bot.toggle_snake() for bot in game.bots]
    [snack.toggle_snack() for snack in game.snacks[1:]]
    while True:
        clock.tick(game.snake.speed)
        game.handle_user_events(game.snake, game.snacks[1:], game.bots)
        game.snake.show_info()
        game.move_snakes()
        game.handle_selfbite()
        [game.handle_eat_snack(snack) for snack in game.snacks]
        for bot in game.bots:
            game.handle_smash(bot)
            game.handle_bot_capture(bot)
            [game.handle_steal_snack(bot, snack) for snack in game.snacks]
        timer += 1
        if not timer % 140:
            game.handle_bot_turns(game.bots[0])
        if not timer % 200:
            game.handle_bot_turns(game.bots[1])
        if not timer % 2000:
            game.handle_captured_bot()
        screen.blit(surface, (0, 0))
        game.draw_objects()
        game.display_info()
        pg.display.update()


if __name__ == '__main__':
    main()
