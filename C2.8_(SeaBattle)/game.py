from random import randint as r_int
from random import choice as r_ch


class BoardException(Exception):
    """Класс для описания возможных исключений.
    Классом-родителем для этого класса является класс Exception (встроенный).
    Классы остальных исключений будут являться наследниками этого класса."""
    pass


class BoardOutException(BoardException):
    """Класс-наследник BoardException. Выбрасывает исключение при попытке
    сделать выстрел за пределы игрового поля."""

    def __str__(self) -> str:
        return " You're trying to shoot out of range of game field!"


class BoardUsedException(BoardException):
    """Класс-наследник BoardException. Выбрасывает исключение при попытке сделать
    выстрел в точку, в которую уже стреляли."""

    def __str__(self) -> str:
        return " This game field sector is already taken!"


class BoardWrongShipException(BoardException):
    """Класс-наследник BoardException, отвечающий за исключение
    при неверной расстановке кораблей на игровое поле."""
    pass


class Dot:
    """Класс для определения координат точки на игровом поле."""

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return (self.x == other.x) and (self.y == other.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class Ship:
    """Класс для описания свойств и методов кораблей."""

    def __init__(self, nose, length, orient) -> None:
        # точка нахождения носа корабля
        self.nose = nose
        # длина корабля (сколько палуб)
        self.length = length
        # ориентация корабля (0 - вертикальная / 1 - горизонтальная)
        self.orient = orient
        # количество "жизней" корабля (сколько ещё не подбитых палуб); по-умолчанию = длине корабля
        self.lives = length

    @property
    def dots(self) -> list:
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

    def shooted(self, shot) -> bool:
        """Метод проверки попадания в конкретный корабль.
        Сравнивает точку в которую выстрелили с точками корабля и возвращает True/False."""
        return shot in self.dots


class Board:
    """Класс для описания игрового поля."""

    def __init__(self, hid=False, size=10) -> None:
        # размер игрового поля
        self.size = size
        # этим мы определяем скрывать или показывать корабли на экране
        self.hid = hid
        # количество потопленных кораблей
        self.count = 0
        # шаблон строки
        self.field = [[" "] * size for _ in range(size)]
        # список "занятых" точек (куда уже делался выстрел)
        self.busy = []
        # список кораблей на игровом поле
        self.ships = []
        # список выстрелов, где оказались палубы кораблей
        self.hits = []

    def add_ship(self, ship) -> None:
        """Метод, выставляющий корабль на игровое поле.
        Если выставить корабль не получается, то выбрасывается исключение BoardWrongShipException."""
        for d in ship.dots:
            if self.out(d) or (d in self.busy):
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, paint=False) -> None:
        """Метод для определения ближайших соседних к любому кораблю точек."""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and (current not in self.busy):
                    if paint:  # принимает True если корабль полностью уничтожен
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)

    def __str__(self) -> str:
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

    def out(self, d) -> bool:
        """Метод проверки выхода координат точки за пределы игрового поля."""
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d) -> bool:
        """Метод для выстрела со всеми необходимыми проверками и возвратом boolean
        значения для понимания кто делает следующий ход:
        True - ход повторяется.
        False - ход переходит сопернику."""
        # точка за пределами игрового поля? - выбрасываем исключение
        if self.out(d):
            raise BoardOutException()
        # в точку уже стреляли? - аналогично
        if d in self.busy:
            raise BoardUsedException()
        # но если всё ок, то добавляем точку в список занятых точек
        self.busy.append(d)
        for ship in self.ships:
            # если попали палубу корабля
            if ship.shooted(d):
                # отнимаем жизнь
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                # добавляем точку в список подбитых точек
                self.hits.append(d)
                # если потопили корабль
                if ship.lives == 0:
                    # накручиваем счётчик
                    self.count += 1
                    # обводим контур
                    self.contour(ship, paint=True)
                    print(" Ship destroyed!")
                    # и обнуляем список подбитых точек, чтобы потом ИИ не тупил, когда будет пытаться
                    # добить следующий раненый корабль
                    self.hits.clear()
                    return True
                else:
                    print(" Ship hit.")
                    return True
        self.field[d.x][d.y] = "."
        print(" Miss.")
        return False

    def begin(self) -> None:
        """Метод обнуляющий список занятых клеток в начале игры."""
        self.busy = []

    def get_busy(self) -> list:
        """Метод возвращающий список занятых клеток."""
        return self.busy

    def get_hit(self) -> list:
        # возвращает список попаданий по палубам кораблей
        return self.hits

    def defeat(self) -> bool:
        """Метод определения проигрыша."""
        # счётчик потопленных кораблей = общему кол-ву кораблей на поле
        return self.count == len(self.ships)


class Player:
    """Класс-родитель для описания свойств и методов игрока."""

    def __init__(self, board, enemy) -> None:
        super().__init__()
        self.board = board
        self.enemy = enemy
        self.tries = []

    def ask(self) -> None:
        """Метод, запрашивающий у игрока координаты точки, в которую тот будет стрелять."""
        raise NotImplementedError()

    def move(self) -> bool:
        """Метод для совершения хода."""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as fail:
                print(fail)


class AI(Player, Board):
    """Класс-наследник от Player и Board (т.к. взаимодействует
    со списком раненых точек) - наш ИИ."""

    def ask(self) -> Dot:
        """Метод, генерирующий координаты точки выстрела для ИИ
        и логику добивания многопалубных кораблей."""
        # берём список раненых точек
        hits = Board.get_hit(self.enemy)
        # берём список занятых точек
        busy = Board.get_busy(self.enemy)
        # если он пустой, то стреляем случайным образом
        if not hits:
            while True:
                rand_dot = Dot(r_int(0, 9), r_int(0, 9))
                # делаем некоторые проверки, чтобы не повторяться в выстрелах
                if (rand_dot not in busy) and not self.out(rand_dot)\
                        and (rand_dot not in self.tries) and (rand_dot not in hits):
                    print(f" Computer's turn: {rand_dot.x + 1} {rand_dot.y + 1}")
                    return rand_dot
                else:
                    continue
        # если в списке раненых точек 1 точка
        elif len(hits) == 1:
            # достаём её
            last_hit = hits[-1]
            # определяем 4 соседей в которые теперь точно есть смысл стрелять
            maybe_dots = [Dot(last_hit.x - 1, last_hit.y),
                          Dot(last_hit.x, last_hit.y + 1),
                          Dot(last_hit.x + 1, last_hit.y),
                          Dot(last_hit.x, last_hit.y - 1)]
            # теперь, пока в списке соседей есть хоть одна точка
            while maybe_dots:
                # выбираем случайную из них
                maybe_hit = r_ch(maybe_dots)
                # сразу убираем её из списка соседей
                maybe_dots.remove(maybe_hit)
                # проверки на то, что эта выбранная точка:
                # не в списке промахов,
                # в пределах поля,
                # не в списке точек по которым уже пытались добить корабль
                # и не списке уже раненых палуб
                if (maybe_hit not in busy) and not self.out(maybe_hit)\
                        and (maybe_hit not in self.tries) and (maybe_hit not in hits):
                    # добавляем эту точку в список попыток добить
                    self.tries.append(maybe_hit)
                    print(f" Computer's turn: {maybe_hit.x + 1} {maybe_hit.y + 1}")
                    # и возвращаем эту точку как координату для очередного хода
                    return maybe_hit
                # а если какое-то условие не выполняется, то пробуем снова
                else:
                    continue
        # тут у меня уже нет сил писать блок комментариев, но суть в том, что если
        # у нас уже 2 подбитых точки, то сравниваются их координаты и находится общая.
        # общая координата уже не меняется, т.к. ориентация корабля стала понятной,
        # а другая координата меняется с приращением +1/-1 и +2/-2 от каждой из этих двух точек.
        # не очень эффективно, но в этом диапазоне 100 % всегда будет весь корабль,
        # даже если это 4-ёхпалубник
        else:
            if hits[1].x == hits[0].x:
                last_hit = hits[1]
                pre_last_hit = hits[0]
                maybe_dots = [Dot(last_hit.x, last_hit.y - 1),
                              Dot(last_hit.x, last_hit.y + 1),
                              Dot(pre_last_hit.x, pre_last_hit.y - 1),
                              Dot(pre_last_hit.x, pre_last_hit.y + 1),
                              Dot(last_hit.x, last_hit.y - 2),
                              Dot(last_hit.x, last_hit.y + 2),
                              Dot(pre_last_hit.x, pre_last_hit.y - 2),
                              Dot(pre_last_hit.x, pre_last_hit.y + 2)]
                while True:
                    maybe_hit = r_ch(maybe_dots)
                    maybe_dots.remove(maybe_hit)
                    if (maybe_hit not in busy) and not self.out(maybe_hit)\
                            and (maybe_hit not in self.tries) and (maybe_hit not in hits):
                        self.tries.append(maybe_hit)
                        print(f" Computer's turn: {maybe_hit.x + 1} {maybe_hit.y + 1}")
                        return maybe_hit
                    else:
                        continue
            elif hits[1].y == hits[0].y:
                last_hit = hits[1]
                pre_last_hit = hits[0]
                maybe_dots = [Dot(last_hit.x - 1, last_hit.y),
                              Dot(last_hit.x + 1, last_hit.y),
                              Dot(pre_last_hit.x - 1, pre_last_hit.y),
                              Dot(pre_last_hit.x + 1, pre_last_hit.y),
                              Dot(last_hit.x - 2, last_hit.y),
                              Dot(last_hit.x + 2, last_hit.y),
                              Dot(pre_last_hit.x - 2, pre_last_hit.y),
                              Dot(pre_last_hit.x + 2, pre_last_hit.y)]
                while True:
                    maybe_hit = r_ch(maybe_dots)
                    maybe_dots.remove(maybe_hit)
                    if (maybe_hit not in busy) and not self.out(maybe_hit)\
                            and (maybe_hit not in self.tries) and (maybe_hit not in hits):
                        self.tries.append(maybe_hit)
                        print(f" Computer's turn: {maybe_hit.x + 1} {maybe_hit.y + 1}")
                        return maybe_hit
                    else:
                        continue


class User(Player):
    """Класс-наследник от Player - наш игрок."""

    def ask(self) -> Dot:
        """Метод, запрашивающий ввод координат точки выстрела у игрока."""
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

    def __init__(self, size=10) -> None:
        self.size = size
        self.lengths = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True
        self.ai = AI(comp, player)
        self.us = User(player, comp)

    @staticmethod
    def greet() -> None:
        """Косметический метод для приветствия и описания формата ввода данных."""
        print("-" * 35)
        print("  Welcome to The Sea Battle game!  ")
        print("-" * 35)
        print("       Format of data input: ")
        print("             X(space)Y  ")

    def try_board(self) -> Board or None:
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

    def random_board(self) -> Board:
        """Метод, возвращающий готовое к игре поле, если его получилось создать."""
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self) -> None:
        """Метод для вывода игровых полей на экран."""
        print("-" * 35)
        print(" Your board:")
        print(self.us.board)
        print("-" * 35)
        print(" Computer's board:")
        print(self.ai.board)
        print("-" * 35)

    def loop(self) -> None:
        """Метод для поочерёдного совершения ходов и проверки на проигрыш + остановки игры."""
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print(" Your turn.")
                repeat = self.us.move()
            else:
                print(" Computer's turn.")
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

    def start(self) -> None:
        """Метод для запуска игры."""
        self.greet()
        self.loop()


if __name__ == "__main__":
    Game().start()
