from datetime import datetime
from random import choice, randint
from sys import exit

import pygame as pg
from pygame import gfxdraw

from settings import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    CENTER, UP, DOWN, LEFT, RIGHT, BOARD_BACKGROUND_COLOR,
    TEXT_COLOR, SNAKE_COLOR, APPLE_COLOR, BOT_COLORS,
    SNACK_COLORS, SPEED_DELTA, EASY_START_SPEED, MAX_SPEED, TURNS, TURNS_BOT,
    MODES_SWITCH_RULES, EASY, HARD, MODES_DISPLAY
)


# Настройка игрового окна
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
GAME_FONT = pg.font.Font(None, 33)
clock = pg.time.Clock()


class GameObject:
    """Общий функционал для игровых объектов"""

    def __init__(self, color=None):
        """Инициализирует цвет и начальное положение"""
        self.body_color = color
        self.position = CENTER
        self.is_active = True

    def toggle_object(self):
        """Отключает и включает игровые объекты"""
        self.is_active = not self.is_active

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
        raise NotImplementedError(
            f'Абстрактный метод draw() базового класса {type(self)}'
            'не знает, как отрисовывать объекты.'
        )


class Apple(GameObject):
    """Класс для объектов, которые будет съедать змейка"""

    def __init__(self, color=APPLE_COLOR, busy_cells=None, power=1):
        """Инициализация яблока"""
        super().__init__(color)
        self.randomize_position(busy_cells)
        self.power = power

    def draw(self):
        """Отрисовка яблока"""
        self.draw_cell(self.position)
        self.display_power()

    def display_power(self):
        """Отображение силы яблока"""
        if self.is_active:
            surface.blit(
                GAME_FONT.render(
                    f'{self.power:+}',
                    True, BOARD_BACKGROUND_COLOR
                ),
                (
                    self.position[0] + GRID_SIZE / 5,
                    self.position[1] + GRID_SIZE / 4
                )
            )


class Snake(GameObject):
    """Класс змеи"""

    def __init__(self, color=SNAKE_COLOR, busy_cells=None, length=1):
        """Инициализация змеи. Методом reset получаем данные для старта."""
        super().__init__(color)
        self.initial_length = length * GRID_SIZE
        self.speed_mode = EASY_START_SPEED
        self.new_speed_mode = None
        self.mode_display = EASY
        self.best_result = {EASY: 1, HARD: 1}
        self.next_direction = None
        self.reset()

    def reset(self, busy_cells=None):
        """Сброс в начальную позицию"""
        self.length = self.initial_length
        self.randomize_position(busy_cells)
        self.positions = [self.position]
        self.speed = self.speed_mode
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def draw(self):
        """Отрисовка змеи"""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.erase_cell(
                self.last,
                cell_color=BOARD_BACKGROUND_COLOR
            )
        """Отрисовка глаза с использованием anti-aliasing"""
        gfxdraw.aacircle(
            surface,
            self.get_head_position()[0] + GRID_SIZE // 2,
            self.get_head_position()[1] + GRID_SIZE // 2,
            GRID_SIZE // 6,
            BOARD_BACKGROUND_COLOR
        )
        gfxdraw.filled_circle(
            surface,
            self.get_head_position()[0] + GRID_SIZE // 2,
            self.get_head_position()[1] + GRID_SIZE // 2,
            GRID_SIZE // 6,
            BOARD_BACKGROUND_COLOR
        )

    def update_direction(self, new_direction):
        """Метод обновляет направление после нажатия на стрелку"""
        self.next_direction = new_direction

    def update_speed_mode(self, new_speed_mode):
        """Метод обновляет поле для фиксации нажатия
        на клавиши 1 и 2, сменяющие режим
        """
        self.new_speed_mode = new_speed_mode

    def handle_speed_mode_change(self):
        """Обработка ситуации смены режимов изи и хард"""
        if self.new_speed_mode:
            self.handle_records()
            self.save_result()
            self.speed_mode = self.new_speed_mode
            self.mode_display = MODES_DISPLAY[self.new_speed_mode]
            self.new_speed_mode = None
            self.reset()
            Game.screen_refresh()

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
        """Метод для изменения скорости после съедения яблок"""
        if power >= 0:
            if not (self.length // GRID_SIZE) % 3:
                self.speed = min(self.speed + SPEED_DELTA, MAX_SPEED)
            return
        self.speed = max(self.speed - SPEED_DELTA, self.speed_mode)

    def length_affect(self, power):
        """Метод для изменения длины змеи после съедения яблок"""
        self.length = max(self.length + power * GRID_SIZE, GRID_SIZE)
        if power < 0:
            self.erase_snake_parts(abs(power) * GRID_SIZE)

    def erase_snake_parts(self, cell_num):
        """Метод для стирания нескольких блоков из хвоста змеи
        (после съедения яблок с отрицательной силой)
        """
        cell_num = min(cell_num, len(self.positions) - GRID_SIZE)
        for _ in range(cell_num):
            self.erase_cell(self.positions.pop())


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
        self.bot_capture_amount = 0
        self.captured_bot = None
        self.timer = 0
        """Инициализация ботов"""
        self.bots = []
        for num in range(2, 4):
            color = BOT_COLORS[num - 2]
            length = num - 1
            bot = Snake(
                color=color,
                busy_cells=hold_cells,
                length=length
            )
            self.bots.append(bot)
            hold_cells.extend(bot.positions)
        """Инициализация яблок разных видов"""
        self.snacks = [self.apple]
        for num in range(-3, 4):
            color = SNACK_COLORS[num]
            power = num
            snack = Apple(
                color=color,
                busy_cells=hold_cells,
                power=power
            )
            self.snacks.append(snack)
            hold_cells.append(snack.position)

    def handle_eat_snack(self, snack):
        """Если змейка съедает неспрятанное яблоко, то сила яблока
        меняет ее длину и скорость, а яблоко перемещается.
        """
        if (
            snack.is_active
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
            bot.is_active
            and snack.is_active
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
                bot.is_active
                and self.snake.length > GRID_SIZE
                and bot.length > GRID_SIZE
                and self.is_collision(
                    self.snake.get_head_position(),
                    pos, threshold=GRID_SIZE / 2
                )
            ):
                self.handle_game_over()

    def handle_bot_capture(self, bot):
        """Захват змеебота, т.е. если змеебот врезается в змейку"""
        if (
            bot.is_active
            and bot.get_head_position() in self.snake.positions[GRID_SIZE:]
        ):
            self.snake.length_affect(bot.length // GRID_SIZE)
            self.snake.speed_affect(power=1)
            self.bot_capture_amount += 1
            [bot.erase_cell(pos) for pos in bot.positions[GRID_SIZE:]]
            bot.reset(
                (
                    *self.snake.positions,
                    *[pos for bot in self.bots for pos in bot.positions],
                    *[snack.position for snack in self.snacks]
                )
            )
            """Чтобы снизить хаос, временно выключаем захваченного бота"""
            if not self.captured_bot:
                bot.toggle_object()
                self.captured_bot = bot

    @classmethod
    def handle_captured_bot(cls, self):
        """Возвращает к жизни захваченного бота"""
        if self.captured_bot:
            self.captured_bot.toggle_object()
            self.captured_bot = None

    def handle_game_over(self):
        """Обработка окончания игры"""
        Game.handle_captured_bot(self)
        self.snake.save_result()
        self.snake.handle_records()
        self.snake.reset()
        self.screen_refresh()

    def display_info(self):
        """Отображение дополнительной информации на экране"""
        if self.bot_capture_amount > 0:
            screen.blit(
                GAME_FONT.render(
                    f'Пошла охота на змееботов! '
                    f'Вы захватили: {self.bot_capture_amount} шт.',
                    True, TEXT_COLOR
                ),
                (GRID_SIZE // 3, GRID_SIZE // 4))

    def handle_objects_activity(self):
        """Отрисовывает и двигает объекты в зависимости
        от их статуса активности
        """
        for snack in self.snacks:
            if snack.is_active:
                snack.draw()
        for bot in self.bots:
            if bot.is_active:
                bot.draw()
                bot.move()
                self.make_bots_turns()

    def make_bots_turns(self):
        """Поворачивает ботов по таймеру"""
        if not self.timer % 140:
            self.handle_bot_turns(self.bots[0])
        if not self.timer % 200:
            self.handle_bot_turns(self.bots[1])

    def handle_bot_turns(self, bot):
        """Создает случайные повороты при движении бота"""
        bot.update_direction(choice(TURNS_BOT.get(bot.direction)))

    @classmethod
    def handle_user_events(cls, game, snake, snacks, bots):
        """Общая обработка действий пользователя"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                Game.handle_quit()
            if event.type == pg.KEYDOWN:
                Game.handle_key_down(event.key, game, snake, snacks, bots)

    @classmethod
    def handle_key_down(cls, key, game, snake, snacks, bots):
        """Обработка нажатия клавиш"""
        if key == pg.K_ESCAPE:
            Game.handle_quit()
        if (
            key == pg.K_UP or key == pg.K_DOWN
            or key == pg.K_LEFT or key == pg.K_RIGHT
        ):
            snake.update_direction(
                TURNS.get((snake.direction, key))
            )
        if key == pg.K_1 or key == pg.K_2:
            snake.update_speed_mode(
                MODES_SWITCH_RULES.get(
                    (snake.speed_mode, key))
            )
            Game.screen_refresh()
        if key == pg.K_3:
            for snack in snacks:
                snack.toggle_object()
            Game.screen_refresh()
        if key == pg.K_4:
            """Перед выключением ботов - нужно обнулить статус
            захваченного бота для корректной работы этой опции
            """
            Game.handle_captured_bot(game)
            for bot in bots:
                bot.toggle_object()
            Game.screen_refresh()

    @staticmethod
    def screen_refresh():
        """Перезаливка экрана на слое surface"""
        surface.fill(BOARD_BACKGROUND_COLOR)

    @staticmethod
    def is_collision(position1, position2, threshold=GRID_SIZE):
        """Метод проверяет, есть ли столкновение"""
        x1, y1 = position1
        x2, y2 = position2
        distance = (x2 - x1) ** 2 + (y2 - y1) ** 2
        return distance < threshold ** 2

    @staticmethod
    def handle_quit():
        """Выход из программы"""
        pg.quit()
        exit()


def handle_keys(game, snake, snacks, bots):
    """Функция для запуска обработки действий пользователя"""
    Game.handle_user_events(game, snake, snacks, bots)


def main():
    """Запуск игры"""
    game = Game()
    Game.screen_refresh()
    for bot in game.bots:
        bot.toggle_object()
    for snack in game.snacks[1:]:
        snack.toggle_object()
    while True:
        clock.tick(game.snake.speed)
        game.timer += 1
        handle_keys(game, game.snake, game.snacks[1:], game.bots)
        game.snake.show_info()
        game.snake.handle_speed_mode_change()
        game.snake.move()
        game.handle_selfbite()
        game.handle_objects_activity()
        for snack in game.snacks:
            game.handle_eat_snack(snack)
        for bot in game.bots:
            game.handle_smash(bot)
            game.handle_bot_capture(bot)
            for snack in game.snacks:
                game.handle_steal_snack(bot, snack)
        if not game.timer % 2000:
            Game.handle_captured_bot(game)
        screen.blit(surface, (0, 0))
        game.snake.draw()
        game.display_info()
        pg.display.update()


if __name__ == '__main__':
    main()
