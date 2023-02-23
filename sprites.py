import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


def findMin(niz):
    for i in range(len(niz) - 1):
        for j in range(i, len(niz)):
            t1 = niz[i].cost()
            t2 = niz[j].cost()
            if t1 > t2:
                t = niz[i]
                niz[i] = niz[j]
                niz[j] = t
    return niz


class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col

        while True:
            if row != goal[0] or col != goal[1]:
                niz = []
                if row - 1 >= 0 and not (game_map[row - 1][col] in path):
                    gm1 = game_map[row - 1][col]
                    niz.append(gm1)
                if col + 1 < len(game_map[0]) and not (game_map[row][col + 1] in path):
                    gm2 = game_map[row][col + 1]
                    niz.append(gm2)
                if row + 1 < len(game_map) and not (game_map[row + 1][col] in path):
                    gm3 = game_map[row + 1][col]
                    niz.append(gm3)
                if col - 1 >= 0 and not (game_map[row][col - 1] in path):
                    gm4 = game_map[row][col - 1]
                    niz.append(gm4)

                niz = findMin(niz)

                row = niz[0].position()[0]
                col = niz[0].position()[1]
            else:
                break
            path.append(game_map[row][col])
        return path


def sortJocke(niz):
    for i in range(len(niz) - 1):
        for j in range(i, len(niz)):
            t1 = niz[i][1]
            t2 = niz[j][1]
            if t1 > t2:
                t = niz[i]
                niz[i] = niz[j]
                niz[j] = t
    return niz


def zbir_suseda(game_map, row, col):
    sum = 0
    br_suseda = 0
    if row - 1 >= 0:
        br_suseda += 1
        sum += game_map[row - 1][col].cost()
    if col + 1 < len(game_map[0]):
        br_suseda += 1
        sum += game_map[row][col + 1].cost()
    if row + 1 < len(game_map):
        br_suseda += 1
        sum += game_map[row + 1][col].cost()
    if col - 1 >= 0:
        br_suseda += 1
        sum += game_map[row][col - 1].cost()
    return float(sum)/br_suseda


class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        queue = [game_map[self.row][self.col]]

        mat_tile = [[0 for col in range(len(game_map[0]))] for row in range(len(game_map))]
        mat_tile[self.row][self.col] = -1
        while len(queue) != 0:
            tile = queue.pop(0)
            row = tile.row
            col = tile.col

            if row == goal[0] and col == goal[1]:
                break

            niz = []
            if row - 1 >= 0 and mat_tile[row-1][col] == 0:
                gm1 = game_map[row - 1][col]
                niz.append((gm1, zbir_suseda(game_map, gm1.position()[0], gm1.position()[1])))
            if col + 1 < len(game_map[0]) and mat_tile[row][col + 1] == 0:
                gm2 = game_map[row][col + 1]
                niz.append((gm2, zbir_suseda(game_map, gm2.position()[0], gm2.position()[1])))
            if row + 1 < len(game_map) and mat_tile[row + 1][col] == 0:
                gm3 = game_map[row + 1][col]
                niz.append((gm3, zbir_suseda(game_map,gm3.position()[0], gm3.position()[1])))
            if col - 1 >= 0 and mat_tile[row][col - 1] == 0:
                gm4 = game_map[row][col - 1]
                niz.append((gm4, zbir_suseda(game_map,gm4.position()[0], gm4.position()[1])))

            niz = sortJocke(niz)
            for i in range(len(niz)):
                pair = niz[i]
                child_tile = pair[0]
                mat_tile[child_tile.position()[0]][child_tile.position()[1]] = tile
                queue.append(child_tile)

        path = [game_map[row][col]]
        while mat_tile[row][col] != -1:
            path.append(mat_tile[row][col])
            old_row = row
            row = mat_tile[row][col].position()[0]
            col = mat_tile[old_row][col].position()[1]
        path.reverse()
        return path


def pathCost(path):
    cost = 0
    for i in range(len(path) - 1):
        cost += path[i].cost()
    return cost


class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        queue = [[game_map[self.row][self.col]]]

        while len(queue) != 0:
            path = queue.pop(0)
            tile = path[-1]
            row = tile.row
            col = tile.col

            if row == goal[0] and col == goal[1]:
                return path

            if row - 1 >= 0 and not game_map[row - 1][col] in path:
                newPath = path.copy()
                newPath.append(game_map[row - 1][col])
                queue.append(newPath)
            if col + 1 < len(game_map[0]) and not game_map[row][col + 1] in path:
                newPath = path.copy()
                newPath.append(game_map[row][col + 1])
                queue.append(newPath)
            if row + 1 < len(game_map) and not game_map[row + 1][col] in path:
                newPath = path.copy()
                newPath.append(game_map[row + 1][col])
                queue.append(newPath)
            if col - 1 >= 0 and not game_map[row][col - 1] == 0 in path:
                newPath = path.copy()
                newPath.append(game_map[row][col - 1])
                queue.append(newPath)

            queue.sort(key=len)
            queue.sort(key=pathCost)


def heuristic(path, goal, game_map):
    cost = 0
    for i in range(len(path) - 1):
        cost += path[i].cost()
    distance = abs(path[-1].position()[0] - goal[0]) + abs(path[-1].position()[1] - goal[1])
    return cost + float(distance) / (len(game_map) + len(game_map[0]))


class Bole(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        queue = [[game_map[self.row][self.col]]]
        i = 0
        while len(queue) != 0:
            i += 1
            path = queue.pop(0)
            tile = path[-1]
            row = tile.row
            col = tile.col

            if row == goal[0] and col == goal[1]:
                return path

            if row - 1 >= 0 and not game_map[row - 1][col] in path:
                newPath = path.copy()
                newPath.append(game_map[row - 1][col])
                queue.append(newPath)
            if col + 1 < len(game_map[0]) and not game_map[row][col + 1] in path:
                newPath = path.copy()
                newPath.append(game_map[row][col + 1])
                queue.append(newPath)
            if row + 1 < len(game_map) and not game_map[row + 1][col] in path:
                newPath = path.copy()
                newPath.append(game_map[row + 1][col])
                queue.append(newPath)
            if col - 1 >= 0 and not game_map[row][col - 1] == 0 in path:
                newPath = path.copy()
                newPath.append(game_map[row][col - 1])
                queue.append(newPath)

            queue.sort(key=lambda x: heuristic(x, goal, game_map))


class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def compare(self, o) -> bool:
        return self.row == o.row and self.col == o.col

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
