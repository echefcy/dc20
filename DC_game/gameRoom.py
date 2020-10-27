from gameRoomElems import *
import copy

ROOM_WIDTH = 1024
ROOM_HEIGHT = 1024

# assuming that the rectangle is lying flat (longer side down)
HALL_LENGTH = 3*ROOM_WIDTH/4
HALL_HEIGHT = ROOM_HEIGHT/2

WALL_SIZE = 64

# NOTE: Room class will probably contain objects from gameRoomElems

class Room:
    def __init__(self, game, width, height, startX=0, startY=0, **options):
        self.game = game
        # global coords
        self.left = startX
        self.right = startX + width
        self.top = startY + height
        self.bottom = startY
        self.x = startX + width/2
        self.y = startY + height/2

        self.texture = None if "image" not in options else arcade.load_texture(options["image"])
        self.tag = options.get("tag", None)

        # ex. "n0.5 s200" 
        openingRaw = options.get("opening", None)
        self.opening = dict()
        self.updateGates(openingRaw)
        self.beenClosed = False

        self.wallMap = options.get("wallMap", [])
        self.walls = []
        for row in range(len(self.wallMap) - 1, -1, -1):
            for col in range(len(self.wallMap[0])):
                if self.wallMap[row][col] == 1:
                    self.walls.append(Wall(self, WALL_SIZE, WALL_SIZE, self.left + col*WALL_SIZE, self.bottom + (len(self.wallMap) - row - 1)*WALL_SIZE))

    def addGate(self, openingRaw):
        if openingRaw[0] == "n" or openingRaw[0] == "s":
            # left and right (X-value) bounds for if the opening is north or south
            middle = self.left + (self.right - self.left)/2
            openingSize = float(openingRaw[1:])
            if openingSize > 1:
                openingSmallBound = middle - openingSize/2
                openingLargeBound = middle + openingSize/2
            else:
                openingSmallBound = middle - openingSize*(self.right - self.left)/2
                openingLargeBound = middle + openingSize*(self.right - self.left)/2
        elif openingRaw[0] == "w" or openingRaw[0] == "e":
            # top and bottom (Y-value) bounds for if the opening is west or east
            middle = self.bottom + (self.top - self.bottom)/2
            openingSize = float(openingRaw[1:])
            if openingSize > 1:
                openingSmallBound = middle - openingSize/2
                openingLargeBound = middle + openingSize/2
            else:
                openingSmallBound = middle - openingSize*(self.top - self.bottom)/2
                openingLargeBound = middle + openingSize*(self.top - self.bottom)/2
        self.opening[openingRaw[0]] = (openingSmallBound, openingLargeBound)

    def updateGates(self, openingRaw):
        if openingRaw == None:
            for gate in "nsew":
                self.opening[gate] = (float("inf"), -float("inf"))
            return

        for gate in "nsew":
                self.opening[gate] = (float("inf"), -float("inf"))

        for gate in openingRaw.split(" "):
            self.addGate(gate)
            
        for gate in "nsew":
            self.opening[gate] = self.opening.get(gate, (float("inf"), -float("inf")))

    def closeGates(self):
        if not self.beenClosed:
            self.gates = copy.deepcopy(self.opening)
            self.updateGates(None)
            self.beenClosed = True
    
    def openGates(self):
        if self.beenClosed:
            self.opening = self.gates

    def charBounds(self, entity):
        if isinstance(entity, Char):
            if entity.x > self.right and not (self.opening['e'][0] < entity.y < self.opening['e'][1]):
                entity.x = self.right
            if entity.x < self.left and not (self.opening['w'][0] < entity.y < self.opening['w'][1]):
                entity.x = self.left
            if entity.y > self.top and not (self.opening['n'][0] < entity.x < self.opening['n'][1]):
                entity.y = self.top
            if entity.y < self.bottom and not (self.opening['s'][0] < entity.x < self.opening['s'][1]):
                entity.y = self.bottom

    def projectileBounds(self, entity):
        if isinstance(entity, Projectile):
            # https://arcade.academy/examples/sprite_collect_coins.html#sprite-collect-coins
            if entity.x > self.right:
                entity.kill()
            elif entity.x < self.left:
                entity.kill()
            elif entity.y > self.top:
                entity.kill()
            elif entity.y < self.bottom:
                entity.kill()

    def checkBounds(self, entity):
        self.charBounds(entity)
        self.projectileBounds(entity)
    
    def draw(self, handlerColor=arcade.color.BLACK):
        # convert to display coords
        l = self.left - self.game.screenX
        r = self.right - self.game.screenX
        t = self.top - self.game.screenY
        b = self.bottom - self.game.screenY
        if self.texture == None:
            arcade.draw_lrtb_rectangle_filled(l, r, t, b, arcade.color.MAGIC_MINT)
            arcade.draw_lrtb_rectangle_outline(l, r, t, b, handlerColor, 10)
        else:
            arcade.draw_lrwh_rectangle_textured(l, b, r - l, t - b, self.texture)
        
        for wall in self.walls:
            wall.draw()
    
    def __repr__(self):
        return f"<{self.tag}:({self.left}, {self.bottom})>"

class SafeRoom(Room):
    def __init__(self, game, startX=0, startY=0, **options):
        super().__init__(game, ROOM_WIDTH, ROOM_HEIGHT, startX, startY, **options)

class Hall(Room):
    def __init__(self, game, startX, startY, direction, **options):
        if direction == "h" or direction == "horizontal" or direction == "lr":
            super().__init__(game, HALL_LENGTH, HALL_HEIGHT, startX, startY, opening="w1 e1", **options)
        elif direction == "v" or direction == "vertical" or direction == "ud":
            super().__init__(game, HALL_HEIGHT, HALL_LENGTH, startX, startY, opening="n1 s1", **options)
        else:
            super().__init__(game, HALL_LENGTH, HALL_HEIGHT, startX, startY, **options)

class PortalRoom(Room):
    def __init__(self, game, startX=0, startY=0, **options):
        super().__init__(game, ROOM_WIDTH, ROOM_HEIGHT, startX, startY, **options)
        self.portal = Portal(self)

    def draw(self):
        super().draw(arcade.color.BLUE)

class HealRoom(Room):
    def __init__(self, game, startX=0, startY=0, **options):
        super().__init__(game, ROOM_WIDTH, ROOM_HEIGHT, startX, startY, **options)
        self.heal = Heal(self)
    
    def draw(self):
        super().draw(arcade.color.MINT)

def XPattern(size=10):
    mapSizeRow = ROOM_HEIGHT//WALL_SIZE
    mapSizeCol = ROOM_WIDTH//WALL_SIZE
    ret = [[0 for i in range(mapSizeCol)] for j in range(mapSizeRow)]
    for row in range((mapSizeRow-size)//2, (mapSizeRow-size)//2+size):
        for col in range((mapSizeCol-size)//2, (mapSizeCol-size)//2+size):
            if row - col == 0:
                ret[row][col] = 1
            elif row + col == mapSizeRow - 1:
                ret[row][col] = 1
    return ret

def slashPattern(size=10):
    mapSize = ROOM_WIDTH//WALL_SIZE
    ret = [[0 for i in range(mapSize)] for j in range(mapSize)]
    for row in range((mapSize-size)//2, (mapSize-size)//2+size):
        for col in range((mapSize-size)//2, (mapSize-size)//2+size):
            if row + col == mapSize - 1:
                ret[row][col] = 1
    return ret

def unSlashPattern(size=5):
    mapSize = ROOM_WIDTH//WALL_SIZE
    ret = [[0 for i in range(ROOM_WIDTH//WALL_SIZE)] for j in range(ROOM_WIDTH//WALL_SIZE)]

    for row in range(ROOM_WIDTH//WALL_SIZE - size, ROOM_WIDTH//WALL_SIZE): # bottom left
        for col in range(size):
            if row + col == ROOM_WIDTH//WALL_SIZE - 1:
                ret[row][col] = 1
    
    for row in range(size): # top right
        for col in range(ROOM_WIDTH//WALL_SIZE - size, ROOM_WIDTH//WALL_SIZE):
            if row + col == ROOM_WIDTH//WALL_SIZE - 1:
                ret[row][col] = 1

    return ret

def noPattern():
    return []

class EnemyRoom(Room):
    def __init__(self, game, startX, startY, **options):
        wallPattern = random.choice([XPattern, unSlashPattern, slashPattern, noPattern, noPattern, noPattern])
        size = random.randint(5, 10) if wallPattern != unSlashPattern else random.randint(3, 7)
        super().__init__(game, ROOM_WIDTH, ROOM_HEIGHT, startX, startY, wallMap=wallPattern(), **options)
        enemyCount = random.randint(options.get("minEnemyCount", 3), options.get("maxEnemyCount", 12))
        self.enemies = [Enemy(self, game, random.randint(50, 950) + startX, 
            random.randint(50, 950) + startY, "Goblin_Scout.png", scale=1.2) for i in range(enemyCount)]

        self.enemyList = arcade.SpriteList()
        self.weaponsList = arcade.SpriteList()
        for enemi in self.enemies:
            enemi.equip(BadPistol(enemi))
            self.enemyList.append(enemi)
    
    def isCleared(self):
        return True if len(self.enemyList) <= 0 else False

    def draw(self):
        super().draw(arcade.color.RED)
        self.enemyList.draw()
        self.weaponsList.draw()

    def update(self):
        self.enemyList.update()
        self.weaponsList.update()
        if self.game.hero.room == self:
            self.closeGates()
            for enemy in self.enemyList:
                hitList = arcade.check_for_collision_with_list(enemy, self.game.heroProjectiles)
                for bullet in hitList:
                    enemy.takeDamage()
                    bullet.kill()
            if self.isCleared():
                self.openGates()
    
    def checkBounds(self, entity):
        if isinstance(entity, Char):
            if entity.x + entity.width/2 >= self.right and not (self.opening['e'][0] < entity.y < self.opening['e'][1]):
                entity.x -= entity.speed
            if entity.x - entity.width/2 <= self.left and not (self.opening['w'][0] < entity.y < self.opening['w'][1]):
                entity.x += entity.speed
            if entity.y + entity.height/2 >= self.top and not (self.opening['n'][0] < entity.x < self.opening['n'][1]):
                entity.y -= entity.speed
            if entity.y - entity.height/2 <= self.bottom and not (self.opening['s'][0] < entity.x < self.opening['s'][1]):
                entity.y += entity.speed
        self.projectileBounds(entity)

def format2dList(lst):
    for row in lst:
        print(row)

# https://en.wikipedia.org/wiki/Maze_generation_algorithm
# https://stackoverflow.com/questions/29739751/implementing-a-randomly-generated-maze-using-prims-algorithm
def getFrontier(chart, row, col):
    dirs = [(0, 2), (2, 0), (-2, 0), (0, -2)]
    frontier = []
    for d in dirs:
        drow, dcol = d
        newRow = row + d[0]
        newCol = col + d[1]
        if 0 <= newRow < len(chart) and 0 <= newCol < len(chart) and chart[newRow][newCol] == 0:
            frontier.append((newRow, newCol))
    return frontier

def getNeighbor(chart, row, col):
    dirs = [(0, 2), (2, 0), (-2, 0), (0, -2)]
    neighbors = []
    for d in dirs:
        drow, dcol = d
        newRow = row + d[0]
        newCol = col + d[1]
        if 0 <= newRow < len(chart) and 0 <= newCol < len(chart) and chart[newRow][newCol] != 0:
            neighbors.append((newRow, newCol))
    return neighbors

def prims(chart, startRow, startCol):
    chart[startRow][startCol] = 1
    frontier = set(getFrontier(chart, startRow, startCol))
    while len(frontier) != 0:
        frtRow, frtCol = random.sample(frontier, 1)[0]
        frontier.discard((frtRow, frtCol))
        nbrRow, nbrCol = random.choice(getNeighbor(chart, frtRow, frtCol))
        drow = (frtRow - nbrRow)//abs(frtRow - nbrRow) if frtRow != nbrRow else 0
        dcol = (frtCol - nbrCol)//abs(frtCol - nbrCol) if frtCol != nbrCol else 0
        chart[nbrRow + drow][nbrCol + dcol] = 1
        chart[frtRow][frtCol] = 1
        for front in getFrontier(chart, frtRow, frtCol):
            frontier.add(front)

def getRoom(level):
    return random.choices([SafeRoom, EnemyRoom, HealRoom], 
        weights=(max(5, 12 - level//2), 2*min(20, level//2), level//4))[0]

def genMap(size):
    # odd integers
    chart = [[0 for col in range(size)] for row in range(size)]
    prims(chart, size-1, 0)
    return chart

