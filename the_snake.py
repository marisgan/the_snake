from random import choice, randint
from sys import exit

from datetime import datetime
import pygame as pg

pg.init()
"""Инициализация модуля PyGame"""

"""Размеры экрана и сетки"""
GRID_SIZE = 60
GRID_WIDTH = 16
GRID_HEIGHT = 12
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

"""Координаты направлений движения змейки"""
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

"""
Новые направления движения для змейки, в зависимости
от старого направления при нажатии клавиши-стрелки.
"""
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
"""Новые направления движения для змеебота"""
TURNS_BOT = {
    LEFT: (LEFT, UP, DOWN),
    RIGHT: (RIGHT, UP, DOWN),
    UP: (UP, LEFT, RIGHT),
    DOWN: (DOWN, LEFT, RIGHT)
}


"""Цвета фона, сетки, объектов в формате RGB"""
BOARD_BACKGROUND_COLOR = (13, 13, 13)
GRID_COLOR = (35, 35, 35)
APPLE_COLOR = (180, 0, 30)
BONUS_APPLE_COLOR = (240, 0, 180)
SNAKE_COLOR = (100, 210, 40)
SNAKE_COLOR2 = (40, 0, 190)
POISON_COLORS = [
    (35, 35, 35),
    (60, 60, 60),
    (85, 85, 85)
]

"""Настройка игрового окна"""
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

"""Контроль времени и скорости"""
clock = pg.time.Clock()
SPEED_MIN = 6
SPEED_MAX = 30


class GameObject:
    """Общий функционал для игровых объектов"""

    def __init__(self, color=None):
        """Инициализирует цвет и начальное положение"""
        self.body_color = color
        self.position = CENTER

    def randomize_position(self, busy_cells=None):
        """Метод меняет позицию объекта на случайную из возможных"""
        if not busy_cells:
            self.position = CENTER
            return
        while True:
            position = (
                (randint(0, GRID_WIDTH - 1)) * GRID_SIZE,
                (randint(0, GRID_HEIGHT - 1)) * GRID_SIZE
            )
            if position not in busy_cells:
                self.position = position
                break

    def draw_cell(self, position, old_position=None, cell_color=None):
        """Отрисовка одной ячейки"""
        if not cell_color:
            cell_color = self.body_color
        pg.draw.rect(
            screen,
            cell_color,
            pg.Rect(*position, GRID_SIZE, GRID_SIZE)
        )
        if old_position:
            pg.draw.rect(
                screen,
                BOARD_BACKGROUND_COLOR,
                pg.Rect(*old_position, GRID_SIZE, GRID_SIZE)
            )
            pg.draw.rect(
                screen,
                GRID_COLOR,
                pg.Rect(*old_position, GRID_SIZE, GRID_SIZE),
                1
            )

    def draw(self):
        """Общий метод для отрисовки объектов"""
        pass

    def is_collision(self, snake_object):
        """Проверка на столкновение"""
        return self.get_head_position() in snake_object.positions

    def is_eaten(self, apple_object):
        """Проверка на съедение"""
        return self.get_head_position() == apple_object.position


class Apple(GameObject):
    """Класс для объектов, которые будет съедать змейка"""

    def __init__(self, busy_cells=None, color=APPLE_COLOR, power=1):
        """
        Инициализация яблока. Сила яблока изменяет длину
        и скорость змеи на значение power.
        """
        super().__init__(color)
        self.randomize_position(busy_cells)
        self.power = power
        """Атрибуты для возможности отключать и включать яблоки"""
        self.initial_color = color
        self.initial_power = power

    def draw(self):
        """Отрисовка яблока"""
        self.draw_cell(self.position)

    def toggle_color(self):
        """Спрятать все серые яблоки при нажатие на 0"""
        if self.body_color != BOARD_BACKGROUND_COLOR:
            self.change_color(BOARD_BACKGROUND_COLOR)
        else:
            self.change_color(self.initial_color)

    def toggle_power(self):
        """Обнулить силу отрицательных яблок при нажатии на 0"""
        if not self.power:
            self.change_power(0)
        else:
            self.change_power(self.initial_power)

    def change_color(self, new_color):
        """Чтобы прятать серые яблоки при нажатии на 0"""
        self.body_color = new_color

    def change_power(self, new_power):
        """Чтобы обнулять силу при нажатии на 0"""
        self.power = new_power


class Snake(GameObject):
    """Класс змеи"""

    def __init__(self, color=SNAKE_COLOR, length=1, busy_cells=None):
        """Инициализация змеи. Методом reset получаем данные для старта."""
        super().__init__(color)
        self.initial_length = length
        self.reset()
        self.best_result = 1

    def reset(self, busy_cells=None):
        """Сброс в начальную позицию"""
        self.length = self.initial_length
        self.randomize_position(busy_cells)
        self.positions = [self.position]
        self.speed = SPEED_MIN
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None
        screen_refresh()

    def draw(self):
        """Отрисовка змеи"""
        self.draw_cell(self.get_head_position(), self.last)

    def show_info(self):
        """Инфо для вывода в шапку окна"""
        info = [
            f'Змейка. Длина: {len(self.positions)}. '
            f'Рекорд: {self.best_result}. '
            f'Скорость: {self.speed - SPEED_MIN + 1}. '
            'Быстрее: Q, медл.: W, без яда: 0, выход: ESC'
        ]
        return ' '.join(info)

    def update_direction(self, new_dir):
        """Метод обновляет направление после нажатия на стрелку"""
        self.direction = new_dir

    def get_head_position(self):
        """Метод возвращает текущие координаты головы"""
        return self.positions[0]

    def move(self):
        """Метод, создающий движение змейки"""
        x, y = self.get_head_position()
        new_head_position = (
            (x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        """Проверка на самоукус"""
        if self.get_head_position() in self.positions[5:]:
            self.save_result()
            if len(self.positions) > self.best_result:
                self.best_result = len(self.positions)
            self.reset()

    def save_result(self):
        """Сохранить результат в файле"""
        with open('results.txt', 'a', encoding='utf-8') as f:
            f.write(
                f'Дата, время: {
                    datetime.strftime(datetime.now(), '%d-%m-%Y, %H:%M:%S')
                }. '
                f'Длина змейки: {len(self.positions)}\n'
            )

    def health_affect(self, snack):
        """
        Яблоки влияют на длину и скорость змеи:
        красные - увеличивают, серые - уменьшают.
        """
        if len(self.positions) <= snack.power:
            self.length += snack.power
            self.speed += snack.power // 2
        """
        Когда длина змеи 2 или 3 ячейки, отрицательное power
        независимо от значения всегда действует как -1.
        """
        if 2 <= len(self.positions) <= 3 and snack.power < 0:
            self.length -= 1
            self.last = self.positions.pop()
            screen_refresh()
            if SPEED_MIN + 1 <= self.speed <= SPEED_MAX:
                self.speed -= 1
        """
        Когда длина змеи 4 и более ячейки, power действует в полную силу.
        """
        if len(self.positions) > abs(snack.power):
            self.length += snack.power
            if SPEED_MIN <= self.speed < (SPEED_MAX - snack.power):
                self.speed += snack.power // 2
            if snack.power < 0:
                for _ in range(abs(snack.power)):
                    self.last = self.positions.pop()
                screen_refresh()


def handle_keys(snake, snacks):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            handle_quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                handle_quit()
            if event.key == pg.K_q:
                handle_speed_change(snake, -1)
            elif event.key == pg.K_w:
                handle_speed_change(snake, 1)
            elif event.key == pg.K_0:
                for snack in snacks:
                    snack.toggle_color()
                    snack.toggle_power()
            snake.update_direction(
                TURNS.get(
                    (snake.direction, event.key), snake.direction
                )
            )


def handle_quit():
    """Выход из программы"""
    pg.quit()
    exit()


def handle_speed_change(snake, delta):
    """Изменение скорости"""
    new_speed = snake.speed + delta
    if SPEED_MIN <= new_speed <= SPEED_MAX:
        snake.speed = new_speed


def draw_grid():
    """Отрисовка разметки на фоне"""
    for col in range(0, GRID_WIDTH, 2):
        pg.draw.rect(
            screen,
            GRID_COLOR,
            pg.Rect(col * GRID_SIZE, 0, GRID_SIZE, SCREEN_HEIGHT),
            1
        )
    for row in range(0, GRID_HEIGHT, 2):
        pg.draw.rect(
            screen,
            GRID_COLOR,
            pg.Rect(0, row * GRID_SIZE, SCREEN_WIDTH, GRID_SIZE),
            1
        )


def screen_refresh():
    """Перезаливка экрана при ресете змейки"""
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_grid()


class MainGame:
    """Класс игры. Создаем игровые объекты"""

    def __init__(self):
        self.snake = Snake()
        self.apple = Apple(busy_cells=self.snake.positions)
        self.snake_bot = Snake(
            color=SNAKE_COLOR2,
            length=2,
            busy_cells=(*self.snake.positions, self.apple.position)
        )
        """Занятые ячейки на поле"""
        self.hold_cells = [
            *self.snake.positions,
            self.apple.position,
            *self.snake_bot.positions
        ]
        self.bonus_apple = Apple(
            color=BONUS_APPLE_COLOR,
            busy_cells=self.hold_cells,
            power=2
        )
        self.hold_cells.append(self.bonus_apple.position)
        self.snacks = [self.apple, self.bonus_apple]
        for i in range(1, 4):
            color = POISON_COLORS[i - 1]
            power = - i
            self.poison = Apple(
                color=color,
                busy_cells=self.hold_cells,
                power=power
            )
            self.snacks.append(self.poison)
            self.hold_cells.append(self.poison.position)

    def move_objects(self):
        """Движение объектов"""
        self.snake.move()
        self.snake_bot.move()

    def draw_objects(self):
        """Отрисовка на экране"""
        self.snake_bot.draw()
        self.snake.draw()
        for snack in self.snacks:
            snack.draw()


def main():
    """Запуск игры"""
    game = MainGame()
    timer = 0
    while True:
        game.move_objects()
        """Цикл игры"""
        clock.tick(game.snake.speed)
        pg.display.set_caption(game.snake.show_info())
        handle_keys(game.snake, game.snacks[2:])
        """Таймер для поворотов змеебота и ресета яблок"""
        timer += 1
        if not timer % 3:
            game.snake_bot.update_direction(
                choice(TURNS_BOT.get(game.snake_bot.direction))
            )
        elif not timer % 50:
            for snack in game.snacks[1:]:
                snack.randomize_position(
                    (*game.snake.positions,
                     *[snack.position for snack in game.snacks])
                )
                screen_refresh()
        """Проверка на столкновение со змееботом"""
        if game.snake.is_collision(game.snake_bot):
            if len(game.snake.positions) > game.snake.best_result:
                game.snake.best_result = len(game.snake.positions)
            game.snake.save_result()
            game.snake.reset()
        if game.snake_bot.is_collision(game.snake):
            game.snake.health_affect(game.apple)
            game.snake_bot.reset(
                (
                    *game.snake.positions,
                    *game.snake_bot.positions,
                    *[snack.position for snack in game.snacks]
                )
            )
        """Проверка, что съела змейка"""
        for snack in game.snacks:
            if game.snake.is_eaten(snack):
                game.snake.health_affect(snack)
                snack.randomize_position(
                    (
                        *game.snake.positions,
                        *game.snake_bot.positions,
                        *[snack.position for snack in game.snacks]
                    )
                )
        game.draw_objects()
        pg.display.update()


if __name__ == '__main__':
    main()
