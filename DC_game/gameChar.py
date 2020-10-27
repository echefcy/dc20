import arcade
import random

DRAW_RADIUS = 2500

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Char(arcade.Sprite):
    # https://arcade.academy/examples/sprite_move_animation.html
    def __init__(self, game, x, y, image, **options):
        super().__init__()
        self.game = game
        self.texture = arcade.load_texture(image)
        # global coords
        self.x = x
        self.y = y

        self.scale = options.get("scale", 1)
        self.speed = options.get("speed", 0)
        self.tag = options.get("tag", None)

    def update(self):
        # convert to display coords
        self.center_x = self.x - self.game.screenX
        self.center_y = self.y - self.game.screenY

class Hero(Char):
    def __init__(self, game, x, y, image, **options):
        super().__init__(game, x, y, image, **options)
        self.maxHealth = options.get('health', 10 + self.game.level//2 - 5)
        self.health = self.maxHealth
        self.room = None
        for r in self.game.rooms:
            if r.left < self.x < r.right and r.bottom < self.y < r.top:
                self.room = r
        self.game.dynamicList.append(self)
        
    def takeDamage(self):
        if self.health > 0:
            self.health -= 1

    def heal(self, amount):
        self.health = min(self.maxHealth, self.health + amount)

    def __keyUpdate(self):
        for key in self.game.keys:
            if key == arcade.key.W:
                self.y += self.speed
            elif key == arcade.key.S:
                self.y -= self.speed
            elif key == arcade.key.A:
                self.x -= self.speed
            elif key == arcade.key.D:
                self.x += self.speed
        
        for rm in self.game.rooms:
            if distance(rm.x, rm.y, self.room.x, self.room.y) <= DRAW_RADIUS:
                self.game.drawCache.add(rm)
            if distance(rm.x, rm.y, self.room.x, self.room.y) > DRAW_RADIUS:
                self.game.drawCache.discard(rm)

        for r in self.game.drawCache:
            if r.left < self.x < r.right and r.bottom < self.y < r.top:
                self.room = r
        
        self.room.checkBounds(self)
        
        for wall in self.room.walls:
            wall.checkBounds(self)
        
    def update(self):
        self.__keyUpdate()
        hitList = arcade.check_for_collision_with_list(self, self.game.enemyProjectiles)
        for bullet in hitList:
            print("got hit")
            self.takeDamage()
            bullet.kill()
        if self.health == 0:
            self.game.gameOver = True
        # convert to display coords
        super().update()
