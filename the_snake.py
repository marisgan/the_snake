from datetime import datetime
import pygame as pg
from random import choice, randint
import sys


pg.init()
"""Инициализация модуля PyGame"""

"""Размеры экрана и сетки"""
GRID_SIZE = 40
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
Новые направления движения змейки, в зависимости
от старого направления при нажатии клавиши-стрелки.
"""
NEW_DIR = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}

ARROW_KEYS = [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]

"""Цвета фона, сетки, объектов в формате RGB"""
BOARD_BACKGROUND_COLOR = (13, 13, 13)
GRID_COLOR = (35, 35, 35)
APPLE_COLOR = (200, 0, 30)
BONUS_APPLE_COLOR = (230, 0, 200)
SNAKE_COLOR = (100, 210, 40)
SNAKE_COLOR2 = (40, 0, 190)
POISON_COLOR1 = (30, 30, 30)
POISON_COLOR2 = (55, 55, 55)
POISON_COLOR3 = (75, 75, 75)

"""Настройка игрового окна"""
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

"""Контроль времени и скорости"""
clock = pg.time.Clock()
SPEED_MIN = 5
SPEED_MAX = 30
now = datetime.now()
now_str = datetime.strftime(now, '%d-%m-%Y, %H:%M:%S')


class GameObject:
    """Общий функционал для игровых объектов"""

    def __init__(self, color=None, busy_cells=None):
        """Инициализирует цвет и положение объекта"""
        self.body_color = color
        self.position = CENTER

    def randomize_position(self, busy_cells=None):
        """Задает координаты объектам в свободных ячейках"""
        if not busy_cells:
            self.position = CENTER
        else:
            while True:
                x_position = (randint(0, GRID_WIDTH - 1)) * GRID_SIZE
                y_position = (randint(0, GRID_HEIGHT - 1)) * GRID_SIZE
                if (x_position, y_position) not in busy_cells:
                    self.position = (x_position, y_position)
                    break

    def draw_cell(self, coords, cell_color=None):
        """Отрисовка одной ячейки"""
        cell_rect = pg.Rect(coords[0], coords[1], GRID_SIZE, GRID_SIZE)
        if not cell_color:
            pg.draw.rect(screen, self.body_color, cell_rect)
        else:
            pg.draw.rect(screen, cell_color, cell_rect)

    def draw(self):
        """Отрисовка игрового объекта"""
        self.draw_cell(self.position)


class Apple(GameObject):
    """Класс для объектов, которые будет съедать змейка"""

    def __init__(self, busy_cells=None, color=APPLE_COLOR, power=1):
        """
        Инициализация яблока по цвету, размещение
        на незанятых ячейках. Сила яблока изменяет длину
        и скорость змеи на значение power.
        """
        self.randomize_position(busy_cells)
        super().__init__(color)
        self.power = power
        """Атрибуты для возможности отключать и включать яблоки"""
        self.initial_color = color
        self.initial_power = power

    def add_health(self, game_object):
        """
        Яблоко изменяет длину и скорость змеи на значение power.
        На старте, когда длина змеи 1 ячейка, можно только прибавлять силу.
        Отрицательное power действовать не будет.
        """
        if len(game_object.positions) <= self.power:
            game_object.length += self.power
            game_object.speed += self.power
        """
        Когда длина змеи 2 или 3 ячейки, отрицательное power
        независимо от значения всегда действует как -1.
        """
        if 2 <= len(game_object.positions) <= 3 and self.power < 0:
            game_object.length -= 1
            game_object.positions.pop()
            if SPEED_MIN + 1 <= game_object.speed <= SPEED_MAX:
                game_object.speed -= 1
        """
        Когда длина змеи 4 и более ячейки, power действует в полную силу.
        """
        if len(game_object.positions) > abs(self.power):
            game_object.length += self.power
            if SPEED_MIN <= game_object.speed < (SPEED_MAX - abs(self.power)):
                game_object.speed += self.power
            if self.power < 0:
                for _ in range(abs(self.power)):
                    game_object.positions.pop()

    # @TODO: нужно оптимизировать
    def toggle(self):
        """
        Спрятать и обнулить все серые яблоки при нажатие на клавишу 0
        и вернуть обратно при повторном нажатии
        """
        if self.body_color != BOARD_BACKGROUND_COLOR:
            self.change_color(BOARD_BACKGROUND_COLOR)
        else:
            self.change_color(self.initial_color)
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

    def __init__(self, color=SNAKE_COLOR, busy_cells=None):
        """
        Инициализация змеи. Методом reset получаем данные для старта,
        задаем стартовое направление вправо и первый результат для вывода инфо.
        """
        super().__init__(color, busy_cells)
        self.reset()
        self.direction = RIGHT
        self.results = [1]

    def reset(self):
        """
        Сброс в начальную позицию.
        Плюс новое случайное направление движения.
        """
        self.length = 1
        self.randomize_position()
        self.positions = [self.position]
        self.speed = SPEED_MIN
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

    def draw(self):
        """Отрисовка змеи"""
        for pos in self.positions:
            self.draw_cell(pos)

    def show_info(self):
        """f-строка с текущим счетом игры и др.инфо."""
        return f'Змейка. \
Длина: {len(self.positions)}. \
Рекорд: {max(self.results)}. \
Скорость: {self.speed - SPEED_MIN + 1}. \
Быстрее: Q, медл.: W, без яда: 0, выход: ESC'

    def update_direction(self, new_dir):
        """Метод обновляет направление после нажатия на стрелку"""
        if new_dir:
            self.direction = new_dir

    def get_head_position(self):
        """Метод возвращает текущие координаты головы"""
        return self.positions[0]

    def move(self):
        """
        Метод, создающий движение змейки.
        Вычисляем новое положение головы.
        """
        x, y = self.get_head_position()
        new_head_position = (
            (x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        """Проверяем новую позицю на столкновение головы с телом."""
        if new_head_position in self.positions[5:]:
            """
            Если змейка укусила себя, игра заканчивается.
            Финальный счет сохраняется в файле и игра перезапускается.
            """
            with open('results.txt', 'a', encoding='utf-8') as f:
                f.write(f'Дата, время: {now_str}. \
    Длина змейки: {(len(self.positions) - 1)}\n')
            self.results.append(len(self.positions))
            self.reset()
        """
        Если проверки пройдены и все в порядке,
        новую позицию головы вставляем в начало тела змейки.
        """
        self.positions.insert(0, new_head_position)
        """
        Проверяем длину змейки, чтобы узнать, съедено ли яблоко,
        и нужно ли удалить последнюю ячейку.
        """
        if len(self.positions) > self.length:
            self.positions.pop()


class AutoSnake(Snake):
    """
    Автоматическая змея, от которой нужно уворачиваться.
    Если главная змея прикоснется к автозмее головой, игра заканчивается.
    """

    def __init__(self, busy_cells, color=SNAKE_COLOR2, length=2):
        super().__init__(color, busy_cells)
        self.reset()
        self.randomize_position(busy_cells)
        self.length = length


def handle_keys(snake, poison1, poison2, poison3):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            match event.key:
                case pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                case event.key if event.key in ARROW_KEYS:
                    new_dir = NEW_DIR.get((snake.direction, event.key))
                    snake.update_direction(new_dir)
                case pg.K_q:
                    if snake.speed > SPEED_MIN:
                        snake.speed -= 1
                case pg.K_w:
                    if snake.speed < SPEED_MAX:
                        snake.speed += 1
                case pg.K_0:
                    poison1.toggle()
                    poison2.toggle()
                    poison3.toggle()


def draw_grid():
    """Отрисовка разметки на фоне"""
    for col in range(GRID_WIDTH):
        if col % 2:
            grid_rect = pg.Rect(
                col * GRID_SIZE,
                0,
                GRID_SIZE,
                SCREEN_HEIGHT
            )
            pg.draw.rect(screen, GRID_COLOR, grid_rect, 1)
    for row in range(GRID_HEIGHT):
        if not row % 2:
            grid_rect = pg.Rect(
                0,
                row * GRID_SIZE,
                SCREEN_WIDTH,
                GRID_SIZE
            )
            pg.draw.rect(screen, GRID_COLOR, grid_rect, 1)


def main():
    """Запуск игры. Создаем экземпляры классов игровых объектов."""
    snake = Snake()
    apple = Apple(busy_cells=[*snake.positions])
    auto_snake = AutoSnake(busy_cells=(*snake.positions, apple.position))
    cells_examp = (
        *snake.positions,
        apple.position,
        *auto_snake.positions
    )
    bonus_apple = Apple(
        color=BONUS_APPLE_COLOR,
        busy_cells=cells_examp,
        power=2
    )
    poison1 = Apple(color=POISON_COLOR1, busy_cells=cells_examp, power=-1)
    poison2 = Apple(color=POISON_COLOR2, busy_cells=cells_examp, power=-2)
    poison3 = Apple(color=POISON_COLOR3, busy_cells=cells_examp, power=-3)

    snacks = [apple, bonus_apple, poison1, poison2, poison3]
    timer = 0

    while True:
        """Бесконечный цикл, в котором проходят процессы игры."""
        clock.tick(snake.speed)
        pg.display.set_caption(snake.show_info())
        handle_keys(snake, poison1, poison2, poison3)
        snake.move()
        auto_snake.move()
        """
        Проверка: съедено ли яблоко или отрава. Или столкновение
        с синей змеёй. Если да, запускаем метод изменения длины
        и скорости змеи, и яблоко возникает в новом месте.
        """
        if snake.get_head_position() in auto_snake.positions:
            with open('results.txt', 'a', encoding='utf-8') as f:
                f.write(f'Дата, время: {now_str}.\
    Длина змейки: {len(snake.positions)}\n')
            snake.results.append(len(snake.positions))
            snake.reset()

        for snack in snacks:
            if snake.get_head_position() == snack.position:
                snack.add_health(snake)
                snack.randomize_position(
                    (*snake.positions, *[snack.position for snack in snacks])
                )
            if auto_snake.positions[0] == snack.position:
                snack.randomize_position(
                    (*snake.positions, *[snack.position for snack in snacks])
                )

        """Таймер для ресета бонусного яблока, отравы и второй змеи"""
        timer += 1
        if timer > 15:
            timer = 0
            auto_snake.update_direction(choice([UP, DOWN, LEFT, RIGHT]))
            for snack in snacks[1:]:
                snack.randomize_position(
                    (*snake.positions, *[snack.position for snack in snacks])
                )

        """Отрисовка объектов"""
        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_grid()
        snake.draw()
        auto_snake.draw()
        for snack in snacks:
            snack.draw()

        """Обновление экрана."""
        pg.display.update()


if __name__ == '__main__':
    main()
