import abc
import copy
import numpy as np
import random

from graph import export_pdf
from sklearn import tree

cell_empty = 0
cell_X = 1
cell_0 = 2
draw = 3

feature_names = ["side", "r1c1", "r1c2", "r1c3", "r2c1", "r2c2", "r2c3", "r3c1", "r3c2", "r3c3"]
target_names = ["r1c1", "r1c2", "r1c3", "r2c1", "r2c2", "r2c3", "r3c1", "r3c2", "r3c3"]


def print_field(field):
    output = ""
    for i in range(len(field)):
        row = field[i]
        for j in range(len(row)):
            symbol = "X" if field[i][j] == cell_X else "0" if field[i][j] == cell_0 else " "
            output += "|\t{}\t".format(symbol)
        output += "|\n"

    print(output)


def test_win(field):
    for i in range(len(field)):
        if done(field[i][0], field[i][1], field[i][2]):
            return field[i][0]
        if done(field[0][i], field[1][i], field[2][i]):
            return field[0][i]

    if done(field[0][0], field[1][1], field[2][2]):
        return field[1][1]
    if done(field[2][0], field[1][1], field[0][2]):
        return field[1][1]

    if not Player.random(Player, field):
        return draw

    return cell_empty


def done(item_1, item_2, item_3):
    return (item_1 == item_2 and
            item_2 == item_3 and
            item_1 != cell_empty)


class Player(object):
    def __init__(self, order):
        if order != cell_X and order != cell_0:
            raise Exception("Wrong player order: {}".format(order))
        self.order = order
        print("Player {} constructed".format(self.order))

    @abc.abstractmethod
    def make_move(self, field):
        return None

    def random(self, field):
        empty = []

        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                if row[j] == cell_empty:
                    empty.append([i, j])

        if len(empty) == 0:
            return None

        index = random.randint(0, len(empty) - 1)
        return empty[index]

    def random_from_list(self, field, points):
        if (not points or
            not field or
            len(points) < 1):
                return None

        for point in points:
            if field[point[0]][point[1]] == cell_empty:
                return point

        return None

    def random_corner(self, field):
        return self.random_from_list(field, [[0, 0], [0, 2], [2, 0], [2, 2]])

    def random_side(self, field):
        return self.random_from_list(field, [[0, 1], [1, 0], [1, 2], [2, 1]])

    def center(self, field):
        return self.random_from_list(field, [[1, 1]])

    def try_win(self, field, side=None):
        if side:
            player = side
        else:
            player = self.order

        if test_win(field) > 0:
            raise Exception("Game already won")

        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                if row[j] == cell_empty:
                    new_field = copy.deepcopy(field)
                    new_field[i][j] = player
                    if test_win(new_field):
                        return [i, j]
        return None


class Human(Player):

    def __init__(self, order):
        super(Human, self).__init__(order)
        print("Human player constructed")

    def make_move(self, field):
        print_field(field)

        x, y = input("Choose where to place {}: ".format("X" if self.order == cell_X else "0")).split()
        x = int(x)
        y = int(y)

        return [x, y]


class AI(Player):

    def __init__(self, order, data_x, data_y):
        super(AI, self).__init__(order)
        self.clf = tree.DecisionTreeClassifier()
        self.clf.fit(data_x, data_y)
        print("AI player constructed")

    def train(self, x, y):
        self.clf.fit(x, y)

    def make_move(self, field):
        sample = [self.order]
        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                sample.append(field[i][j])

        try:
            result = self.clf.predict(np.array(sample).reshape(1, -1))
        except DeprecationWarning:
            # just ignore it
            nothing = True

        x = result[0] // 3
        y = result[0] % 3
        if field[x][y] != cell_empty:
            return self.random(field)

        return [x, y]


class Algorithm(Player):

    def __init__(self, order, accuracy):
        self.accuracy = accuracy
        self.o_position1 = -1
        self.o_position2 = -1
        super(Algorithm, self).__init__(order)
        print("Algorithm player constructed")

    def make_move(self, field):
        dice = random.randint(0, 99)
        if dice > self.accuracy:
            return self.random(field)

        x_loc = []
        o_loc = []
        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                if row[j] == cell_X:
                    x_loc.append([i, j])
                elif row[j] == cell_0:
                    o_loc.append([i, j])

        if self.order == cell_X:
            stage = len(x_loc)
            if stage == 0:
                return self.random_corner(field)
            elif stage == 1:
                self.o_position1 = o_loc[0]

                if (self.o_position1 == [1, 0] or
                    self.o_position1 == [1, 1] or
                    self.o_position1 == [2, 0]):
                    return [0, 1]
                elif (self.o_position1 == [0, 1] or
                      self.o_position1 == [0, 2]):
                    return [1, 0]
                elif (self.o_position1 == [2, 1] or
                      self.o_position1 == [2, 2]):
                    return [0, 2]

                return [1, 1]
            elif stage == 2:
                chance = self.try_win(field)
                if chance:
                    return chance

                enemy_chance = self.try_win(field, cell_0)
                if enemy_chance:
                    return enemy_chance

                for o in o_loc:
                    if o != self.o_position1:
                        self.o_position2 = o
                        break

                if (self.o_position1 == [2, 2] and
                    self.o_position2 == [0, 1]):
                    return [2, 0]

                if field[1][1] == cell_empty:
                    return [1, 1]

                return self.random(field)
            elif stage == 3:
                chance = self.try_win(field)
                if chance:
                    return chance

                enemy_chance = self.try_win(field, cell_0)
                if enemy_chance:
                    return enemy_chance

                return self.random(field)
        else:
            stage = len(o_loc)
            if stage == 0:
                if field[1][1] == cell_empty:
                    return [1, 1]

                return self.random_corner(field)
            elif stage == 1:
                enemy_chance = self.try_win(field, cell_X)
                if enemy_chance:
                    return enemy_chance

                side_count = 0
                for x in x_loc:
                    if x[0] == 1 or x[1] == 1:
                        side_count += 1

                if side_count > 1:
                    return self.random_corner(field)

                return self.random_side(field)
            elif stage == 2:
                chance = self.try_win(field)
                if chance:
                    return chance

                enemy_chance = self.try_win(field, cell_X)
                if enemy_chance:
                    return enemy_chance

                return self.random(field)

        return self.random(field)


def play_game(player_1, player_2):
    if player_1.order == player_2.order:
        raise Exception("Players have same side")

    if player_1.order == cell_empty or player_2.order == cell_empty:
        raise Exception("One of the players has no side")

    if player_1.order == cell_X:
        player_x = player_1
        player_o = player_2
    else:
        player_x = player_2
        player_o = player_1

    field = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
            ]

    x_moves = []
    o_moves = []

    result = 0
    stage = 0
    while result == 0:
        local_field = copy.deepcopy(field)

        if stage % 2 == 0:
            move = player_x.make_move(field)
            print("Player X does " + str(move))
            if field[move[0]][move[1]] != cell_empty:
                return cell_0, x_moves, o_moves

            x_moves.append([local_field, move])
            field[move[0]][move[1]] = cell_X
        else:
            move = player_o.make_move(field)
            print("Player 0 does " + str(move))
            if field[move[0]][move[1]] != cell_empty:
                return cell_X, x_moves, o_moves

            o_moves.append([local_field, move])
            field[move[0]][move[1]] = cell_0

        stage += 1
        result = test_win(field)

    return result, x_moves, o_moves

algo = Algorithm(cell_X, 100)
algo2 = Algorithm(cell_0, 100)
field = [
        [1, 1, 2],
        [2, 1, 0],
        [0, 1, 2]
        ]

res, x_moves, o_moves = play_game(algo, algo2)


def dummy_data():
    data = []

    sample = [cell_0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    sample_2 = [cell_X, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(9):
        data.append([sample, i])
        data.append([sample_2, i])

    return data


def add_moves_to_data(data, moves, side):
    for move in moves:
        field = move[0]
        sample = [side]
        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                sample.append(field[i][j])

        target = move[1][0] * 3 + move[1][1]
        data.append([sample, target])


def column(matrix, i):
    return [row[i] for row in matrix]

data = []
add_moves_to_data(data, o_moves, cell_0)
add_moves_to_data(data, x_moves, cell_X)
add_moves_to_data(data, o_moves, cell_0)

dummy = dummy_data()
data_array = np.array(data)
ai = AI(cell_X, column(dummy, 0), column(dummy, 1))

# export_pdf(ai.clf, feature_names, target_names, "X_0.pdf")

human = Human(cell_0)
# print(play_game(human, ai))

ai.train(column(data_array, 0), column(data_array, 1))
ai.order = cell_0
human.order = cell_X
# print(play_game(human, ai))

ai_win = algo_win = draw_c = 0
test_ai = AI(cell_X, column(dummy, 0), column(dummy, 1))
test_algo = Algorithm(cell_0, 100)
data = []
for i in range(1000):
    result, ai_moves, algo_moves = play_game(test_ai, test_algo)

    if result == draw:
        draw_c += 1
        if test_ai.order == cell_0:
            add_moves_to_data(data, ai_moves, cell_0)
    else:
        if test_ai.order == result:
            ai_win += 1
            add_moves_to_data(data, ai_moves, result)
        else:
            algo_win += 1
            add_moves_to_data(data, algo_moves, result)

    data_array = np.array(data)
    test_ai.train(column(data_array, 0), column(data_array, 1))

    if test_ai.order == cell_X:
        test_ai.order = cell_0
    else:
        test_ai.order = cell_X

    if test_algo.order == cell_X:
        test_algo.order = cell_0
    else:
        test_algo.order = cell_X

print("AI wins: {}; Algorithm wins {}; Draws {}".format(ai_win, algo_win, draw_c))
export_pdf(test_ai.clf, feature_names, target_names, "X_0.pdf")

test_ai.order = cell_0
human.order = cell_X
print(play_game(human, test_ai))
