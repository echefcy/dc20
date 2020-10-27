# https://arcade.academy/arcade.html
from gameWeap import *

# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
def cross2d(v, w):
    return v[0]*w[1] - v[1]*w[0]
def addVec(v, w):
    return (v[0] + w[0], v[1] + w[1])
def subVec(v, w):
    return (v[0] - w[0], v[1] - w[1])
def checkCrossing(x1, y1, x2, y2, xa, ya, xb, yb):
    q = (x1, y1)
    s = (x2 - x1, y2 - y1)
    p = (xa, ya)
    r = (xb - xa, yb - xa)
    if cross2d(r, s) == 0:
        return False
    t = cross2d(subVec(q, p), s)/cross2d(r, s)
    u = cross2d(subVec(q, p), r)/cross2d(r, s)
    return True if 0 <= t <= 1 and 0 <= u <= 1 else False

class Wall:
    # will most likely be used in Room's subclasses
    def __init__(self, room, width, height, startX=0, startY=0, image=None):
        self.room = room
        # global coords
        self.left = startX
        self.right = startX + width
        self.top = startY + height
        self.bottom = startY
        self.texture = image

        self.x = startX + width/2
        self.y = startY + height/2
    
    def draw(self):
        # convert to display coords
        l = self.left - self.room.game.screenX
        r = self.right - self.room.game.screenX
        t = self.top - self.room.game.screenY
        b = self.bottom - self.room.game.screenY
        if self.texture == None:
            arcade.draw_lrtb_rectangle_filled(l, r, t, b, arcade.color.BLACK)
        else:
            arcade.draw_lrwh_rectangle_textured(l, b, r - l, t - b, self.texture)
    
    def checkBounds(self, entity):
        if isinstance(entity, Char):
            # checks: the sum of both circumradii >= the distance between the centers of entity and wall
            # basically sets up a detection radius
            # if (distance(entity.x - entity.width/2, entity.y - entity.height/2, entity.x + entity.width/2, entity.y + entity.height/2)/2
            #     + distance(self.left, self.bottom, self.right, self.top)/2 >= distance(entity.x, entity.y, self.x, self.y)):
            if (distance(self.left, self.bottom, self.right, self.top)/2 + (self.right - self.left)/2 >= distance(entity.x, entity.y, self.x, self.y)):
                if (checkCrossing(self.right, self.bottom, self.right, self.top,
                    self.x, self.y, entity.x, entity.y) and entity.x - entity.width/2 <= self.right): # approaching from right
                    entity.x += entity.speed
                if (checkCrossing(self.left, self.top, self.right, self.top, 
                    self.x, self.y, entity.x, entity.y) and entity.y - entity.height/2 <= self.top): # approaching from the top
                    entity.y += entity.speed
                if (checkCrossing(self.left, self.bottom, self.left, self.top,
                    self.x, self.y, entity.x, entity.y) and entity.x + entity.width/2 >= self.left): # approaching from the left
                    entity.x -= entity.speed
                if (checkCrossing(self.left, self.bottom, self.right, self.bottom,
                    self.x, self.y, entity.x, entity.y) and entity.y + entity.height/2 >= self.bottom): # approaching from the bottom
                    entity.y -= entity.speed

        elif isinstance(entity, Projectile):
            if (self.left - entity.width/2 < entity.x < self.right + entity.width/2
                and self.bottom - entity.height/2 < entity.y < self.top + entity.height/2):
                entity.kill()
            
class Portal(arcade.Sprite):
    def __init__(self, room):
        super().__init__()
        self.room = room
        self.texture = arcade.load_texture("portal.png")
        self.x = (self.room.right - self.room.left)/2 + self.room.left
        self.y = (self.room.top - self.room.bottom)/2 + self.room.bottom
        self.scale = 0.05
        self.room.game.dynamicList.append(self)

    def update(self):
        self.center_x = self.x - self.room.game.screenX
        self.center_y = self.y - self.room.game.screenY
        if arcade.check_for_collision(self, self.room.game.hero):
            print("advanced to the next level")
            self.room.game.nextLevel = True
    
class Heal(arcade.Sprite):
    def __init__(self, room):
        super().__init__()
        # green ring: https://www.pngguru.com/free-transparent-background-png-clipart-evier
        # black ring: https://www.pngkey.com/png/full/171-1711785_circle-png-black-ring.png
        self.room = room
        self.used = False
        self.texture = arcade.load_texture("green_ring.png")
        self.x = (self.room.right - self.room.left)/2 + self.room.left
        self.y = (self.room.top - self.room.bottom)/2 + self.room.bottom
        self.scale = 0.3
        self.room.game.dynamicList.append(self)

    def update(self):
        self.center_x = self.x - self.room.game.screenX
        self.center_y = self.y - self.room.game.screenY
        if arcade.check_for_collision(self, self.room.game.hero) and not self.used:
            self.room.game.hero.heal(random.randint(2,6))
            print("healed")
            self.texture = arcade.load_texture("black_ring.png")
            self.used = True
