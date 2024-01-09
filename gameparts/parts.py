# gameparts/parts.py
"""Модуль, содержащий классы проекта THE_SNAKE"""

from datetime import datetime
from random import choice, randint
from sys import exit

import pygame as pg
from pygame import gfxdraw

from gameparts import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    CENTER, UP, DOWN, LEFT, RIGHT, BOARD_BACKGROUND_COLOR,
    STEALTH_COLOR, TEXT_COLOR, SNAKE_COLOR, APPLE_COLOR, BOT_COLORS,
    SNACK_COLORS, SPEED_DELTA, EASY_START_SPEED, FONT, TURNS_BOT,
    MODES_SWITCH_RULES, easy, hard, MODES_DISPLAY,
    screen, surface, TURNS
)


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
        while self.position in busy_cells:
            self.position = (
                randint(0, (GRID_WIDTH - 1)) * GRID_SIZE,
                randint(0, (GRID_HEIGHT - 1)) * GRID_SIZE
            )

    def draw_cell(
            self, position, cell_color=None,
            width=0, border_radius=GRID_SIZE
    ):
        """Метод для отрисовки одной ячейки"""
        pg.draw.rect(
            surface,
            cell_color or self.body_color,
            pg.Rect(
                position,
                (GRID_SIZE, GRID_SIZE)
            ),
            width, border_radius
        )

    def erase_cell(self, position, cell_color=BOARD_BACKGROUND_COLOR):
        """Метод для стирания одной ячейки"""
        self.draw_cell(
            position, cell_color,
            border_radius=0
        )

    def draw(self):
        """Абстрактный метод для реализации в дочерних классах"""
        raise NotImplementedError
        """Абстрактный метод draw базового класса GameObject не знает,
        как отрисовывать объекты.
        """


class Apple(GameObject):
    """Класс для объектов, которые будет съедать змейка"""

    def __init__(self, color=APPLE_COLOR, busy_cells=None, power=1):
        """Инициализация яблока"""
        super().__init__(color)
        self.randomize_position(busy_cells)
        self.power = self.initial_power = power
        """Атрибуты для возможности отключать и включать яблоки"""
        self.initial_color = color

    def draw(self):
        """Отрисовка яблока"""
        self.draw_cell(self.position)
        self.display_power()

    def display_power(self):
        """Отображение силы яблока"""
        if self.power:
            surface.blit(
                FONT.render(
                    f'{self.power:+}',
                    True, BOARD_BACKGROUND_COLOR
                ),
                (
                    self.position[0] + GRID_SIZE / 5,
                    self.position[1] + GRID_SIZE / 4
                )
            )

    def toggle_snack(self):
        """Отключает и включает яблоки"""
        self.body_color = (STEALTH_COLOR if self.body_color != STEALTH_COLOR
                           else self.initial_color)
        self.power = 0 if self.power != 0 else self.initial_power


class Snake(GameObject):
    """Класс змеи"""

    def __init__(self, color=SNAKE_COLOR, busy_cells=None, length=1):
        """Инициализация змеи. Методом reset получаем данные для старта."""
        super().__init__(color)
        self.initial_length = length * GRID_SIZE
        self.initial_color = color
        self.speed_mode = EASY_START_SPEED
        self.mode_display = easy
        self.best_result = {easy: 1, hard: 1}
        self.next_direction = None
        self.bot_capture_amount = 0
        self.captured_bot = None
        self.reset()

    def toggle_snake(self):
        """Метод для включения и отключения змеи"""
        self.body_color = (STEALTH_COLOR if self.body_color != STEALTH_COLOR
                           else self.initial_color)
        self.eye_color = (STEALTH_COLOR if self.eye_color != STEALTH_COLOR
                          else BOARD_BACKGROUND_COLOR)

    def reset(self, busy_cells=None):
        """Сброс в начальную позицию"""
        self.length = self.initial_length
        self.randomize_position(busy_cells)
        self.positions = [self.position]
        self.speed = self.speed_mode
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None
        self.eye_color = BOARD_BACKGROUND_COLOR

    def switch_speed_mode(self, switch_status):
        """Метод для переключения между режимами скорости easy и hard.
        Если пришел статус None - значит пользователь нажал на кнопку
        режима, который на данный момент уже включен.
        """
        if switch_status:
            self.speed_mode = switch_status
            self.mode_display = MODES_DISPLAY[switch_status]
            self.handle_records()
            self.save_result()
            self.reset()

    def draw(self):
        """Отрисовка змеи"""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.erase_cell(
                self.last,
                cell_color=(STEALTH_COLOR if self.body_color == STEALTH_COLOR
                            else BOARD_BACKGROUND_COLOR)
            )
        """Отрисовка глаза с использованием anti-aliasing"""
        gfxdraw.aacircle(
            screen,
            self.get_head_position()[0] + GRID_SIZE // 2,
            self.get_head_position()[1] + GRID_SIZE // 2,
            GRID_SIZE // 6,
            self.eye_color
        )
        gfxdraw.filled_circle(
            screen,
            self.get_head_position()[0] + GRID_SIZE // 2,
            self.get_head_position()[1] + GRID_SIZE // 2,
            GRID_SIZE // 6,
            self.eye_color
        )

    def update_direction(self, new_direction):
        """Метод обновляет направление после нажатия на стрелку"""
        self.next_direction = new_direction

    def get_head_position(self):
        """Метод возвращает текущее положение головы"""
        return self.positions[0]

    def move(self):
        """
        Метод создает движение змеи, добавляя новое положение головы
        в начало списка и удаляя последний элемент, если длина не увеличилась.
        """
        self.positions.insert(0, self.get_new_head_position())
        if len(self.positions) // GRID_SIZE + 1 > self.length // GRID_SIZE:
            self.last = self.positions.pop()

    def get_new_head_position(self):
        """Метод вычисляет новое положение головы
        в зависимости от того, был поворот или нет
        """
        x, y = self.get_head_position()
        if self.next_direction:
            """Если был поворот, то длина шага на повороте: GRID_SIZE // 4"""
            new_head_position = (
                (
                    x + self.next_direction[0] * (GRID_SIZE // 4)
                ) % (SCREEN_WIDTH - GRID_SIZE // 2),
                (
                    y + self.next_direction[1] * (GRID_SIZE // 4)
                ) % (SCREEN_HEIGHT - GRID_SIZE // 2)
            )
            self.direction = self.next_direction
            self.next_direction = None
        else:
            """Если поворота не было"""
            new_head_position = (
                (x + self.direction[0]) % SCREEN_WIDTH,
                (y + self.direction[1]) % SCREEN_HEIGHT
            )
        return new_head_position

    def get_best_result(self):
        """Метод возвращает рекорд для текущего режима игры"""
        return self.best_result[self.mode_display]

    def handle_records(self):
        """Проверка результата игры на рекорд и обновление рекорда"""
        if self.length // GRID_SIZE > self.get_best_result():
            self.best_result[
                self.mode_display
            ] = self.length // GRID_SIZE

    def show_info(self):
        """Вывод информации в шапку окна"""
        pg.display.set_caption(
            f'Изгиб питона. Вы на {self.mode_display}. '
            f'Длина: {self.length // GRID_SIZE} '
            f'(рекорд: {self.get_best_result()}) '
            f'Скорость: {(self.speed - EASY_START_SPEED) // SPEED_DELTA + 1} |'
            f' ESC - выход | 1 - изи | 2 - хард | 3 - экстраз | 4 - боты'
        )

    def save_result(self):
        """Сохраняет результат в файле"""
        if len(self.positions) // GRID_SIZE > 3:
            now = datetime.strftime(datetime.now(), '%d-%m-%Y, %H:%M:%S')
            with open('results.txt', 'a', encoding='utf-8') as f:
                f.write(
                    f'Дата, время: {now}. '
                    f'Длина змейки: {self.length // GRID_SIZE}. '
                    f'Скорость: {self.speed}. '
                    f'Режим: {self.mode_display}\n'
                )

    def speed_affect(self, power):
        """Метод для изменения скорости"""
        if power > 0:
            if not (self.length // GRID_SIZE) % 3:
                self.speed += SPEED_DELTA
        else:
            self.speed -= SPEED_DELTA
            """Чтобы скорость не снижалась ниже минимума текущего режима"""
            if self.speed < self.speed_mode:
                self.speed = self.speed_mode

    def length_affect(self, power):
        """Метод для изменения длины змеи"""
        if power >= 0:
            self.length += power * GRID_SIZE
        else:
            if 1 <= len(self.positions) // GRID_SIZE < (abs(power) + 1):
                self.length -= GRID_SIZE
                self.erase_snake_parts(GRID_SIZE)
            if len(self.positions) // GRID_SIZE > abs(power):
                self.length += power * GRID_SIZE
                self.erase_snake_parts(abs(power) * GRID_SIZE)

    def erase_snake_parts(self, cell_num):
        """Метод для стирания нескольких блоков из хвоста змеи
        (после съедения яблок с отрицательной силой)
        """
        for _ in range(cell_num):
            cell_off = self.positions.pop()
            self.erase_cell(cell_off)


class Game:
    """
    Класс игры, в котором создаются игровые объеты, запускается
    движение, отрисовка и логика взаимодействия
    """

    def __init__(self):
        """Инициализация игровых объектов"""
        self.snake = Snake()
        hold_cells = [*self.snake.positions]
        self.apple = Apple(busy_cells=hold_cells)
        hold_cells.append(self.apple.position)
        """Инициализация ботов"""
        self.bots = []
        for i in range(2, 4):
            color = BOT_COLORS[i - 2]
            length = i - 1
            self.bot = Snake(
                color=color,
                busy_cells=hold_cells,
                length=length
            )
            self.bots.append(self.bot)
            hold_cells.append(self.bot.positions)
        """Инициализация яблок разных видов"""
        self.snacks = [self.apple]
        for i in range(-3, 4):
            color = SNACK_COLORS[i]
            power = i
            self.snack = Apple(
                color=color,
                busy_cells=hold_cells,
                power=power
            )
            self.snacks.append(self.snack)
            hold_cells.append(self.snack.position)

    def handle_eat_snack(self, snack):
        """Если змейка съедает неспрятанное яблоко, то сила яблока
        меняет ее длину и скорость, а яблоко перемещается.
        """
        if (
            snack.body_color != STEALTH_COLOR
            and self.is_collision(
                self.snake.get_head_position(),
                snack.position
            )
        ):
            self.snake.length_affect(snack.power)
            self.snake.speed_affect(snack.power)
            snack.erase_cell(snack.position)
            snack.randomize_position(
                (
                    *self.snake.positions,
                    *[pos for bot in self.bots for pos in bot.positions],
                    *[snack.position for snack in self.snacks]
                )
            )

    def handle_selfbite(self):
        """Обработка ситуации самоукуса"""
        if self.snake.get_head_position() in self.snake.positions[
            GRID_SIZE * 3:
        ]:
            self.handle_game_over()

    def handle_steal_snack(self, bot, snack):
        """Если неспрятанный змеебот крадёт неспрятанное яблоко,
        то сила яблока меняет его длину, а яблоко перемещается.
        """
        if (
            bot.body_color != STEALTH_COLOR
            and snack.body_color != STEALTH_COLOR
            and self.is_collision(
                bot.get_head_position(),
                snack.position
            )
        ):
            bot.length_affect(snack.power)
            snack.erase_cell(snack.position)
            snack.randomize_position(
                (
                    *self.snake.positions,
                    *[pos for bot in self.bots for pos in bot.positions],
                    *[snack.position for snack in self.snacks]
                )
            )

    def handle_smash(self, bot):
        """Если змей врезается головой в неспрятанного бота,
        то игра заканчивается. Однако, когда змей маленький
        (на старте - только голова), то ему ничего не угрожает.
        Это нужно для спец.тактики: ждать пока боты подрастут
        сами собой, чтобы сразу захватить длинного бота
        и получить его ячейки без роста скорости.
        Также и наоборот: пока бот маленький (одна голова) - в него
        нельзя врезаться, чтобы не было лишнего хаоса при ресете.
        """
        for pos in bot.positions:
            if (
                bot.body_color != STEALTH_COLOR
                and self.snake.length > GRID_SIZE
                and bot.length > GRID_SIZE
                and self.is_collision(
                    self.snake.get_head_position(),
                    pos, threshold=GRID_SIZE / 2
                )
            ):
                self.handle_game_over()
                [bot.reset(
                    (
                        *self.snake.positions,
                        *[snack.position for snack in self.snacks]
                    )
                ) for bot in self.bots]

    def handle_bot_capture(self, bot):
        """Захват змеебота, т.е. если змеебот врезается в змейку"""
        if (
            bot.body_color != STEALTH_COLOR
            and bot.get_head_position() in self.snake.positions[GRID_SIZE:]
        ):
            self.snake.length_affect(bot.length // GRID_SIZE)
            self.snake.speed_affect(power=1)
            self.snake.bot_capture_amount += 1
            [bot.erase_cell(pos) for pos in bot.positions[GRID_SIZE:]]
            bot.reset(
                (
                    *self.snake.positions,
                    *[pos for bot in self.bots for pos in bot.positions],
                    *[snack.position for snack in self.snacks]
                )
            )
            if not self.snake.captured_bot:
                bot.toggle_snake()
                self.snake.captured_bot = bot

    def handle_captured_bot(self):
        """Возвращает к жизни захваченного бота"""
        if self.snake.captured_bot:
            self.snake.captured_bot.toggle_snake()
            self.snake.captured_bot = None

    def handle_game_over(self):
        """Обработка окончания игры"""
        self.snake.save_result()
        self.snake.handle_records()
        self.snake.reset()
        self.screen_refresh()
        self.handle_captured_bot()

    def display_info(self):
        """Отображение дополнительной информации на экране"""
        if self.snake.bot_capture_amount > 0:
            screen.blit(
                FONT.render(
                    f'Пошла охота на змееботов! '
                    f'Вы захватили: {self.snake.bot_capture_amount} шт.',
                    True, TEXT_COLOR
                ),
                (GRID_SIZE // 3, GRID_SIZE // 4))

    def draw_objects(self):
        """Отрисовка всех объектов"""
        [snack.draw() for snack in self.snacks]
        [bot.draw() for bot in self.bots]
        self.snake.draw()

    def move_snakes(self):
        """Движение всех змеев"""
        [bot.move() for bot in self.bots]
        self.snake.move()

    def handle_bot_turns(self, bot):
        """Создает случайные повороты при движении бота"""
        bot.update_direction(choice(TURNS_BOT.get(bot.direction)))

    def handle_user_events(self, snake, snacks, bots):
        """Общая обработка действий пользователя"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.handle_quit()
            if event.type == pg.KEYDOWN:
                self.handle_keys(event.key, snake, snacks, bots)

    def handle_keys(self, key, snake, snacks, bots):
        """Обработка нажатия клавиш"""
        if key == pg.K_ESCAPE:
            self.handle_quit()
        if key in [key for _, key in TURNS]:
            snake.update_direction(
                TURNS.get((snake.direction, key))
            )
        if key in [key for _, key in MODES_SWITCH_RULES]:
            snake.switch_speed_mode(
                MODES_SWITCH_RULES.get((snake.speed_mode, key))
            )
            self.screen_refresh()
        if key == pg.K_3:
            [snack.toggle_snack() for snack in snacks]
            self.screen_refresh()
        if key == pg.K_4:
            self.handle_captured_bot()
            [bot.toggle_snake() for bot in bots]
            self.screen_refresh()

    @staticmethod
    def screen_refresh():
        """Перезаливка экрана на слое surface"""
        surface.fill(BOARD_BACKGROUND_COLOR)

    @staticmethod
    def is_collision(position1, position2, threshold=GRID_SIZE):
        """Метод проверяет, есть ли столкновение"""
        x1, y1 = position1
        x2, y2 = position2
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return distance < threshold

    @staticmethod
    def handle_quit():
        """Выход из программы"""
        pg.quit()
        exit()
