import pygame
from random import choice, randint


pygame.init()
"""Инициализация модуля PyGame."""

"""Константы для размеров."""
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

"""Направления движения."""
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

"""Цвета фона, сетки, объектов, текста в формате RGB."""
BOARD_BACKGROUND_COLOR = (13, 13, 13)
GRID_COLOR = (30, 30, 30)
APPLE_BG_COLOR = (230, 0, 60)
SNAKE_BG_COLOR = (20, 200, 50)
BAD_SNACK_COLOR = (60, 60, 60)
TEXT_COLOR = (255, 255, 255)

"""Настройка игрового окна."""
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')

"""Создаем объекты и объявлем константы
для контроля скорости течения игры"""
clock = pygame.time.Clock()
SPEED = 60  # frames per second
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 140)  # milliseconds

"""Переменная для управления настройками шрифта при выводе текста на экран"""
game_font = pygame.font.Font(None, 27)


class GameObject:
    """Родительский класс, содержащий общий функционал для игровых объектов."""

    def __init__(self, bg_color=None, fg_color=None):
        """Инициализирует цвет и положение объекта."""
        self.body_color = bg_color
        self.figure_color = fg_color
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

    def draw(self, surface):
        """Заготовка для методов отрисовки дочерних классов"""
        pass


class Apple(GameObject):
    """Класс для объектов, которые будет съедать змейка"""

    def __init__(self, bg_color=APPLE_BG_COLOR, fg_color=GRID_COLOR):
        """Инициализирует объект по цвету и задает случайное положение"""
        super().__init__(bg_color, fg_color)
        self.position = self.randomize_position(busy=None)

    def randomize_position(self, busy):
        """
        Метод формирует новые рандомные координаты для положения на экране
        таким образом, чтобы объекты не наслаивались друг на друга.
        В параметр можно передать координаты текущих объектов на экране или
        обозначить этот параметр как None.
        """
        while True:
            x_position = (randint(0, GRID_WIDTH - 1)) * GRID_SIZE
            y_position = (randint(0, GRID_HEIGHT - 1)) * GRID_SIZE
            if not busy:
                return x_position, y_position
            else:
                if (x_position, y_position) not in busy:
                    return x_position, y_position

    def draw(self, surface):
        """Метод для отрисовки объектов, которые будет съедать змейка"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, self.figure_color, rect, 1)


class Snake(GameObject):
    """Класс змеи, содержащий необходимые для игры атрибуты и методы"""

    def __init__(self,
                 bg_color=SNAKE_BG_COLOR,
                 fg_color=BOARD_BACKGROUND_COLOR
                 ):
        """
        При инициализации змейки задается цвет, стартовая длина,
        позиция в центре экрана (наследуется от родительского класса),
        стартовое направление движения, а также задаются атрибуты для
        дальнейшего просчета направления и закрашивания последней ячейки.
        """
        super().__init__(bg_color, fg_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw_score(self):
        """Метод для вывода текущего счета игры на экран."""
        score_text = f'Длина змейки: {(len(self.positions) - 1)}'
        score_surface = game_font.render(score_text, False, TEXT_COLOR)
        score_x = GRID_SIZE * 2.1
        score_y = GRID_SIZE // 2
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        screen.blit(score_surface, score_rect)

    def reset(self):
        """
        Метод для сброса змейки при проигрыше в начальную позицию.
        Переопределяет направление движения на новое случайное.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, DOWN, UP, LEFT])
        screen.fill(BOARD_BACKGROUND_COLOR)

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Метод, создающий движение змейки.
        Сначала получаем текущие координаты головы.
        """
        head_x, head_y = self.get_head_position()
        """Добавляем новое направление к координатам головы."""
        head_x = head_x + self.direction[0] * GRID_SIZE
        head_y = head_y + self.direction[1] * GRID_SIZE
        """Проверяем выход за границы экрана."""
        if not 0 <= head_x < SCREEN_WIDTH:
            head_x = abs(abs(head_x) - SCREEN_WIDTH)
        if not 0 <= head_y < SCREEN_HEIGHT:
            head_y = abs(abs(head_y) - SCREEN_HEIGHT)
        """Назначаем новую позицию головы."""
        new_head_position = (head_x, head_y)
        """Проверяем новую позицю на столкновение головы с телом."""
        if new_head_position in self.positions[2:]:
            """
            Если змейка укусила себя, игра заканчивается.
            Финальный счет сохраняется в файле и игра перезапускается.
            """
            with open('results.txt', 'a', encoding='utf-8') as f:
                f.write(f'Длина змейки: {(len(self.positions) - 1)}\n')
            self.reset()
        """
        Если проверки пройдены и все в порядке,
        новую позицию головы вставляем в начало тела змейки.
        """
        self.positions.insert(0, new_head_position)
        """Проверяем длину змейки, чтобы узнать, съедено ли яблоко,
        и нужно ли стирать последнюю ячейку."""
        if len(self.positions) - 1 > self.length:
            self.last = self.positions.pop()

    def get_head_position(self):
        """Метод возвращает текущие координаты головы."""
        return self.positions[0]

    def draw(self, surface):
        """Метод для отрисовки змейки и стирания хвоста."""
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, rect, 1)

        """Отрисовка головы змейки."""
        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, head_rect, 1)

        """Затирание последнего сегмента"""
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == SCREEN_UPDATE:
            """
            Запускаем движение змеи (которое происходит 1 раз в 140 мс,
            что задано в начале программы через SCREEN_UPDATE).
            Это позволяет сохранять желаемую скорость игры примерно одинаковой
            на разных компьютерах независимо от их мощности.
            """
            game_object.move()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def draw_grid():
    """Функция для отрисовки разметки на фоне."""
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            grid_rect = pygame.Rect(
                col * GRID_SIZE,
                row * GRID_SIZE,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
            pygame.draw.rect(screen, GRID_COLOR, grid_rect, 1)


def main():
    """Запуск игры. Создаем экзэмпляры классов игровых объектов."""
    apple = Apple()
    bad_snack = Apple(BAD_SNACK_COLOR, GRID_COLOR)
    snake = Snake()
    snack_timer = 0

    while True:
        """Бесконечный цикл, в котором проходят процессы игры."""
        clock.tick(SPEED)
        """
        При SPEED равным 60, игровой цикл будет исполняться со скоростью
        60 раз в секунду, (т.е. игровое окно будет транслировать 60 FPS).
        Запускается функция обработки нажатия клавиш.
        """
        handle_keys(snake)
        snake.update_direction()
        """
        Проверка: съедено ли яблоко. Если съедено, счет игры
        увеличивается на 1 очко, и яблоко возникает в новом месте.
        """
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.position = apple.randomize_position(
                (*snake.positions, apple.position, bad_snack.position)
            )
        """
        Проверка: если съедена плохая закуска, длина змеи
        уменьшается на 1 ячейку и счет игры уменьшается на 1 очко,
        и закуска появляется в новом месте.
        """
        if snake.get_head_position() == bad_snack.position:
            bad_snack.position = bad_snack.randomize_position(
                (*snake.positions, apple.position, bad_snack.position)
            )
            if len(snake.positions) > 2:
                snake.length -= 1
                snake.positions.pop()
        """
        Таймер для ресета плохой закуски, которая меняет положение
        примерно 1 раз в 500 мс.
        """
        snack_timer += 1
        if snack_timer >= 500:
            snack_timer = 0
            bad_snack.position = bad_snack.randomize_position(
                (*snake.positions, apple.position, bad_snack.position)
            )
        """Заливка экрана."""
        screen.fill(BOARD_BACKGROUND_COLOR)
        """Отрисовка объектов."""
        apple.draw(screen)
        bad_snack.draw(screen)
        snake.draw(screen)
        draw_grid()
        snake.draw_score()
        """Обновление экрана."""
        pygame.display.update()


if __name__ == '__main__':
    main()
