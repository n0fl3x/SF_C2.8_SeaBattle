from random import randint as rndt


class Dot:
    """Класс для определения координат точки на игровом поле."""

    # У любой точки 2 координаты - x и y.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Переопределяем стандартный метод __eq__, чтобы было удобнее сравнивать точки между собой и определять
    # находится ли координаты той или иной точки в каком-либо списке координат с помощью оператора in.
    # До переопределения сравнивали id, а теперь сами значения координат.
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Переопределяем стандартный метод __str__, чтобы удобнее выводить координаты точки в читаемом виде
    # через функцию print: (x, y).
    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    """Класс для описания возможных исключений.
    Классом-родителем для этого класса является класс Exception (встроенный).
    Классы остальных исключений будут являться наследниками этого класса."""
    pass


class BoardOutException(BoardException):
    """Класс-наследник BoardException, который отвечает за попытку сделать выстрел за пределы
    игрового поля."""
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы игрового поля!"


class BoardUsedException(BoardException):
    """Класс-наследник BoardException, который отвечает за попытку сделать выстрел точку,
    в которую уже производился выстрел."""
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    """Класс-наследник BoardException, который задаётся НЕ для вывода пользователю,
    а для исключения при неверной расстановке кораблей на игровое поле."""
    pass


class Ship:
    """Класс для описания свойств и методов кораблей."""
    def __init__(self, bow, length, orient):
        self.bow = bow  # точка нахождения носа корабля
        self.length = length  # длина корабля (сколько палуб)
        self.orient = orient  # ориентация корабля (вертикальная/горизонтальная)
        self.lives = length  # количество "жизней" корабля (сколько ещё не подбитых палуб) = длине корабля

    @property
    def dots(self):
        """Метод, возвращающий список всех точек корабля."""
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.orient == 0:
                cur_x += i
            elif self.orient == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    """Класс для описания игровой доски."""
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

    def contour(self, ship, verb=False):
        """Метод для определения ближайших соседних к любому кораблю точек."""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

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
        """Метод для выстрела со всеми необходимыми проверками."""
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
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(rndt(0, 9), rndt(0, 9))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=10):
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, player)
        self.us = User(player, comp)

    def try_board(self):
        lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for _ in lens:
            while True:
                attempts += 1
                if attempts > 5000:
                    return None
                ship = Ship(Dot(rndt(0, self.size), rndt(0, self.size)), _, rndt(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем Вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
