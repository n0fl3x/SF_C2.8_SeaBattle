# Логика алгоритма ИИ для эффективного добивания многопалубных кораблей.

# Какие списки для логики добивания нам нужны:
# - Промахи
# - "Раненные" точки
# - Попытки добить (?)

# Изначально ИИ делает рандомные выстрелы.
# Если ИИ попадает в однопалубник, то потом тоже продолжает делать рандомные выстрелы.

# Если ИИ ранит корабль, то должен следующим выстрелом рандомно выбрать одну из 4 соседних клеток:
# точка попадания: wounded_dot = Dot(x, y)
# точки-соседи: next_to_wounded_dots = [Dot(x-1, y), Dot(x+1, y), Dot(x, y-1), Dot(x, y+1)]

#   |  1|  2|  3|  4|  5|  6|  7|  8|  9| 10|(Y)
#  1|   |   |   |   |   |   |   |   |   |   |
#  2|   |   |   |   |   |   |   |   |   |   |
#  3|   |   |   |   |   |   |   |   |   |   |
#  4|   |   |   |   | ? |   |   |   |   |   |
#  5|   |   |   | ? | X | ? |   |   |   |   |
#  6|   |   |   |   | ? |   |   |   |   |   |
#  7|   |   |   |   |   |   |   |   |   |   |
#  8|   |   |   |   |   |   |   |   |   |   |
#  9|   |   |   |   |   |   |   |   |   |   |
# 10|   |   |   |   |   |   |   |   |   |   |
# (X)

# Случайный выбор из этих 4 точек: try_to_fatality = random.choice(next_to_wounded_dots)
# Если промах, то продолжаем выбирать из оставшихся 3 точек:
# next_to_wounded_dots.remove(try_to_fatality)

#   |  1|  2|  3|  4|  5|  6|  7|  8|  9| 10|(Y)
#  1|   |   |   |   |   |   |   |   |   |   |
#  2|   |   |   |   |   |   |   |   |   |   |
#  3|   |   |   |   |   |   |   |   |   |   |
#  4|   |   |   |   | # | # |   |   |   |   |
#  5|   |   | ? | ? | X | Х | ? | ? |   |   |
#  6|   |   |   |   | # | # |   |   |   |   |
#  7|   |   |   |   |   |   |   |   |   |   |
#  8|   |   | # | # | # |   |   |   |   |   |
#  9|   | ? | Х | ? | Х | ? |   |   |   |   |
# 10|   |   | # | # | # |   |   |   |   |   |
# (X)

# Когда соседняя точка найдена и корабль убит (2-ухпалубник), то обнуляем список
# соседних клеток (перестаём к нему обращаться) - он теперь не нужен,
# пока не раним какой-нибудь следующий корабль.

# Если после очередного выстрела ранена ещё одна часть корабля (3 или 4 палубник),
# то мы сравниваем координаты этих двух раненых точек и находим ось, которая не изменилась,
# и фиксируем её как приоритетную для следующих попыток выстрела.
# В последствии меняем координату только по оставшейся оси каким-то приращением (dx/dy).

# Вообще если это кто-то действительно читает и проверяет, то могу сказать следующее:
# осознаю, что реализованная логика добивания кораблей неидеальна (мягко говоря).
# Но она работает, в отличие от некоторых очень сырых попыток, которые я видел в Слаке.
# + она создавалась не по шаблону, а путём моих собственных логических рассуждений.
# Это всяко лучше, чем ИИ, который ВСЕГДА делает рандомные выстрелы.
# В этой версии игры хотя бы периодически по-настоящему можно проиграть компьютеру.
