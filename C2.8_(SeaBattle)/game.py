from random import randint as r_int


class Dot:
    """Класс для определения координат точки на игровом поле."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    """Класс для описания возможных исключений.
    Классом-родителем для этого класса является класс Exception (встроенный).
    Классы остальных исключений будут являться наследниками этого класса."""
    pass


class BoardOutException(BoardException):
    """Класс-наследник BoardException, который выбрасывает исключение при попытке
    сделать выстрел за пределы игрового поля."""
    def __str__(self):
        return " You're trying to shoot out of range of game field!"


class BoardUsedException(BoardException):
    """Класс-наследник BoardException. Выбрасывает исключение при попытке сделать
    выстрел в точку, в которую уже стреляли."""
    def __str__(self):
        return " You have already shoot at this sector!"


class BoardWrongShipException(BoardException):
    """Класс-наследник BoardException, отвечающий за исключение
    при неверной расстановке кораблей на игровое поле."""
    pass


class Ship:
    """Класс для описания свойств и методов кораблей."""
    def __init__(self, nose, length, orient):
        self.nose = nose  # точка нахождения носа корабля
        self.length = length  # длина корабля (сколько палуб)
        self.orient = orient  # ориентация корабля (0 - вертикальная / 1 - горизонтальная)
        self.lives = length  # количество "жизней" корабля (сколько ещё не подбитых палуб),
                             # по-умолчанию = длине корабля

    @property
    def dots(self):
        """Метод-свойство, возвращающий список всех точек одного корабля."""
        ship_dots = []
        for i in range(self.length):
            current_x = self.nose.x
            current_y = self.nose.y
            if self.orient == 0:
                current_x += i
            if self.orient == 1:
                current_y += i
            ship_dots.append(Dot(current_x, current_y))
        return ship_dots

    def shooten(self, shot):
        """Метод проверки попадания в конкретный корабль."""
        return shot in self.dots


class Board:
    """Класс для описания игрового поля."""
    def __init__(self, hid=False, size=10):
        self.size = size  # размер игрового поля
        self.hid = hid  # этим мы определяем скрывать или показывать корабли на экране
        self.count = 0  # количество потопленных кораблей
        self.field = [[" "] * size for _ in range(size)]  # шаблон строки
        self.busy = []  # список "занятых" точек (где стоят корабли, или куда уже делался выстрел)
        self.ships = []  # список кораблей на игровом поле

    def add_ship(self, ship):
        """Метод, выставляющий корабль на игровое поле.
        Если выставить корабль не получается, то выбрасывается исключение BoardWrongShipException."""
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, paint=False):
        """Метод для определения ближайших соседних к любому кораблю точек."""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and current not in self.busy:
                    if paint:
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)

    def __str__(self):
        """Метод для построчного вывода нашего поля на основе шаблона строки + косметические доработки."""
        line = ""
        line += "  |  1|  2|  3|  4|  5|  6|  7|  8|  9| 10|(Y)"
        for i, j in enumerate(self.field):
            if i < 9:
                line += f"\n {i + 1}| " + " | ".join(j) + " |"
            else:
                line += f"\n{i + 1}| " + " | ".join(j) + " |"
        line += "\n(X)"

        if self.hid:
            line = line.replace("■", " ")  # тут мы реализуем условие скрытия кораблей нашего оппонента
        return line

    def out(self, d):
        """Метод проверки выхода координат точки за пределы игрового поля."""
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
        # т.е.: НЕ(координаты x и y находятся внутри поля)

    def shot(self, d):
        """Метод для выстрела со всеми необходимыми проверками и возвратом булевого
        значения для понимания кто делает следующий ход."""
        # если точка в пределах игрового поля
        if self.out(d):
            raise BoardOutException()
        # и точка не занята
        if d in self.busy:
            raise BoardUsedException()
        # то добавляем точку в список занятых точек
        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, paint=True)
                    print(" Ship destroyed!")
                    return True
                else:
                    print(" Ship hitted!")
                    return True

        self.field[d.x][d.y] = "."
        print(" Miss!")
        return False

    def begin(self):
        """Метод обнуляющий список занятых клеток в начале игры (мы ж ещё никуда не стреляли)."""
        self.busy = []

    def defeat(self):
        """Метод определения проигрыша."""
        return self.count == len(self.ships)  # счётчик потопленных кораблей =
                                              # = общему кол-ву кораблей на поле


class Player:
    """Класс-родитель для описания свойств и методов игрока."""
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        """Метод, который просит у игрока координаты точки, в которую тот будет стрелять."""
        raise NotImplementedError()

    def move(self):
        """Метод для совершения хода."""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    """Класс-наследник от Player. Наш ИИ."""
    def ask(self):
        """Метод, генерирующий координаты точки для ИИ."""
        dot = Dot(r_int(0, 9), r_int(0, 9))
        print(f" Computer's turn: {dot.x + 1} {dot.y + 1}")
        return dot


class User(Player):
    """Класс-наследник от Player. Наш игрок."""
    def ask(self):
        """Метод, запрашивающий ввод координат точки у игрока."""
        while True:
            cords = input(" Your turn: ").split()
            if len(cords) != 2:
                print(" Enter 2 coordinates!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Enter numbers!")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    """Класс для описания самой игры: генерация игровых полей, приветствие, цикл для совершения ходов и т.д."""
    def __init__(self, size=10):
        self.size = size
        self.lengths = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True
        self.ai = AI(comp, player)
        self.us = User(player, comp)

    @staticmethod
    def greet():
        """Косметический метод для приветствия и описания формата ввода данных."""
        print("-" * 35)
        print("  Welcome to The Sea Battle game!  ")
        print("-" * 35)
        print("       Format of data input: ")
        print("             X(space)Y  ")

    def try_board(self):
        """Метод для попытки автоматической расстановки кораблей на игровом поле."""
        board = Board(size=self.size)
        attempts = 0
        for _ in self.lengths:
            while True:
                attempts += 1
                if attempts > 5000:
                    return None
                ship = Ship(Dot(r_int(0, self.size), r_int(0, self.size)), _, r_int(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        """Метод, возвращающий готовое к игре поле, если его получилось создать."""
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self):
        """Метод для вывода игровых полей на экран."""
        print("-" * 35)
        print(" Your board:")
        print(self.us.board)
        print("-" * 35)
        print(" Computer's board:")
        print(self.ai.board)
        print("-" * 35)

    def loop(self):
        """Метод для поочерёдного совершения ходов и проверки на проигрыш + остановки игры."""
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print(" Your turn!")
                repeat = self.us.move()
            else:
                print(" Computer's turn!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print(" You won!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print(" Computer won!")
                break
            num += 1

    def start(self):
        """Метод для запуска игры."""
        self.greet()
        self.loop()


if __name__ == "__main__":
    # Вызываем метод start класса Game для начала игры.
    Game().start()
