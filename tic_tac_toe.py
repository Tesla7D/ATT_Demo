import abc
import copy

cell_empty = 0
cell_X = 1
cell_0 = 2
draw = 3

feature_names = ["side", "field"]
target_names = ["Move"]

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
        for i in range(len(field)):
            row = field[i]
            for j in range(len(row)):
                if row[j] == cell_empty:
                    return [i, j]

        return None

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
    def make_move(self, field):
        print_field(field)

        x, y = input("Choose where to place {}: ".format("X" if self.order == cell_X else "0")).split()
        x = int(x)
        y = int(y)

        return [x, y]


class Algorithm(Player):

    def __init__(self, order):
        super(Algorithm, self).__init__(order)
        print("Algorithm player constructed")

    def make_move(self, field):
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

                return self.random_side()
            elif stage == 2:
                chance = self.try_win(field)
                if chance:
                    return chance

                enemy_chance = self.try_win(field, cell_X)
                if enemy_chance:
                    return enemy_chance

                return self.random(field)

        return self.random(field)

def play_game(player_x, player_o):
    field = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
            ]

    result = 0
    stage = 0
    while result == 0:
        if stage % 2 == 0:
            move = player_x.make_move(field)
            if field[move[0]][move[1]] != cell_empty:
                return cell_0

            field[move[0]][move[1]] = cell_X
        else:
            move = player_o.make_move(field)
            if field[move[0]][move[1]] != cell_empty:
                return cell_X

            field[move[0]][move[1]] = cell_0

        stage += 1
        result = test_win(field)

    return result

algo = Algorithm(cell_X)
algo2 = Algorithm(cell_0)
human = Human(cell_0)
field = [
        [1, 1, 2],
        [2, 1, 0],
        [0, 1, 2]
        ]

print(play_game(algo, human))

# print(human.make_move(field))
