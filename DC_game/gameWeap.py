from gameChar import *
import math

class Weap(arcade.Sprite):
    def __init__(self, char, image, scale=1):
        super().__init__()
        self.char = char
        self.offset = 35
        self.scale = scale
        self.angle = 0
        self.texture = arcade.load_texture(image)

    def target(self, x, y):
        charX = self.char.x
        charY = self.char.y
        rectifiedX = x - charX
        rectifiedY = y - charY
        if rectifiedY >= 0:
            if rectifiedX > 0: # first quadrant
                self.angle = math.degrees(math.atan(rectifiedY/rectifiedX))
            elif rectifiedX < 0: # second quadrant
                self.angle = 180 + math.degrees(math.atan(rectifiedY/rectifiedX))
        elif rectifiedY < 0:
            if rectifiedX > 0: # fourth quadrant
                self.angle = math.degrees(math.atan(rectifiedY/rectifiedX))
            elif rectifiedX < 0: # third quadrant
                self.angle = -180 + math.degrees(math.atan(rectifiedY/rectifiedX))

    def manualAim(self):
        worldMouseX = self.char.game.mouseX + self.char.game.screenX
        worldMouseY = self.char.game.mouseY + self.char.game.screenY
        self.target(worldMouseX, worldMouseY)
        
    def update(self):
        self.manualAim()
        rad = math.radians(self.angle)
        self.x = self.char.x + self.offset*math.cos(rad)
        self.y = self.char.y + self.offset*math.sin(rad)
        self.center_x = self.x - self.char.game.screenX
        self.center_y = self.y - self.char.game.screenY

class Pistol(Weap):
    def __init__(self, char, image="Pistol.png", scale=0.15):
        super().__init__(char, image, scale)
        # visuals/config
        self.lastFired = 0
        # greater = slower
        self.projectileOffset = 10

        # weapon specs
        # larger = slower rate of fire
        self.reload = 0.5
        self.projectileSpeed = 20
        self.inacc = 5
        self.bullet = "Silver_Bullet.png"
        self.bulletSize = 1.5

        self.char.game.dynamicList.append(self)

    def shoot(self):
        # https://gamepedia.cursecdn.com/terraria_gamepedia/0/0f/Silver_Bullet.png?version=84ea53023beac9efbaec57a9ad602847
        self.char.game.heroProjectiles.append(Projectile(self, self.bullet, self.bulletSize, self.projectileSpeed))
        self.lastFired = self.char.game.timer

    def update(self):
        super().update()
        if self.char.game.mouseDown and self.char.game.timer - self.lastFired >= self.reload:
            self.shoot()

class BadPistol(Pistol):
    def __init__(self, char):
        super().__init__(char)
        self.reload = max(0, 4 - self.char.game.level/7) if self.char.phase == 1 else max(0, (4 - self.char.game.level/7)*(12/self.char.game.level))
        self.projectileSpeed = random.randint(4 + self.char.game.level//2 - 5, 4 + self.char.game.level//2)
        self.inacc = 30 - self.char.game.level*2 + 10 if 30 - self.char.game.level*2 + 10 > 0 else 0
        self.bullet = "Meteor_Shot.png"
        self.aimX = 0
        self.aimY = 0
        self.shooting = False

    def shoot(self):
        # https://gamepedia.cursecdn.com/terraria_gamepedia/0/0f/Silver_Bullet.png?version=84ea53023beac9efbaec57a9ad602847
        self.char.game.enemyProjectiles.append(Projectile(self, self.bullet, self.bulletSize, self.projectileSpeed))
        self.lastFired = self.char.game.timer

    def aim(self, x, y):
        self.aimX = x
        self.aimY = y

    def update(self):
        self.reload = max(0, 4 - self.char.game.level/7) if self.char.phase == 1 else max(0, (4 - self.char.game.level/7)*3)
        self.target(self.aimX, self.aimY)
        if self.shooting and self.char.game.timer - self.lastFired >= self.reload:
            self.shoot()
        rad = math.radians(self.angle)
        self.x = self.char.x + self.offset*math.cos(rad)
        self.y = self.char.y + self.offset*math.sin(rad)
        self.center_x = self.x - self.char.game.screenX
        self.center_y = self.y - self.char.game.screenY

class Projectile(arcade.Sprite):
    def __init__(self, weap, image, scale=1, speed=0):
        super().__init__()
        self.weap = weap
        self.texture = arcade.load_texture(image)
        self.scale = scale
        self.speed = speed
        self.rad = math.radians(self.weap.angle + (random.choice([-1,1])*random.random())*(self.weap.inacc/2))
        self.x = self.weap.char.x + (self.weap.offset + self.weap.projectileOffset)*math.cos(self.rad)
        self.y = self.weap.char.y + (self.weap.offset + self.weap.projectileOffset)*math.sin(self.rad)
        self.room = None

    def update(self):
        self.x += self.speed*math.cos(self.rad)
        self.y += self.speed*math.sin(self.rad)
        self.center_x = self.x - self.weap.char.game.screenX
        self.center_y = self.y - self.weap.char.game.screenY
        self.weap.char.room.checkBounds(self)

        for wall in self.weap.char.room.walls:
            wall.checkBounds(self)

class Enemy(Char):
    def __init__(self, room, game, x, y, image="Goblin_Scout.png", **options):
        super().__init__(game, x, y, image, **options)
        self.speed = max(1, random.random()+0.5)*(self.game.level//2)/1.5
        self.texture = arcade.load_texture(image)
        # self.direction = self.getDir()
        self.direction = (0, 0)
        self.time = 0.5
        self.phase = random.choices([0, 1], weights=(min(20, self.game.level+5), max(5, 18-self.game.level+5)))[0]
        self.room = room
        self.weap = None
        self.maxHealth = 2 + (self.game.level - 5)//4
        self.health = self.maxHealth
    
    def equip(self, weap):
        self.weap = weap
        self.room.weaponsList.append(self.weap)

    def getDir(self):
        dirs = [(-1,-1), (-1,0), (-1,1),
                (0,-1), (0,1),
                (1,-1), (1,0), (1,1)]
        d = random.choice(dirs)
        return d

    def getDir2(self):
        x = int((self.game.hero.x - self.x)/abs(self.game.hero.x - self.x)) if self.game.hero.x - self.x != 0 else 0
        y = int((self.game.hero.y - self.y)/abs(self.game.hero.y - self.y)) if self.game.hero.y - self.y != 0 else 0
        d = (x, y)
        return d

    def wander(self):
        if self.weap != None:
            self.weap.aim(self.game.hero.x, self.game.hero.y)
            self.weap.shooting = True
        if abs(self.game.timer - self.time) <= 0.1:
            if self.game.level < 7:
                self.direction = self.getDir()
            elif self.game.level < 9:
                self.direction = random.choice([self.getDir(), self.getDir(), self.getDir2()])
            elif self.game.level < 11:
                self.direction = random.choice([self.getDir(), self.getDir2()])
            elif self.game.level < float("inf"):
                self.direction = random.choice([self.getDir2()])
            self.time = self.game.timer + 0.5
        else:
            self.x += self.speed*self.direction[0]
            self.y += self.speed*self.direction[1]

    def attack(self):
        if self.weap != None:
            self.weap.aim(self.game.hero.x, self.game.hero.y)
            self.weap.shooting = True

    def simpleAI(self):
        # choosing subroutine
        if (self.game.timer) % 2 <= 0.01:
            self.phase = random.choices([0, 1], weights=(min(20, self.game.level+5), max(5, 18-self.game.level+5)))[0]
        if self.phase == 0:
            self.wander()
        elif self.phase == 1:
            self.time = self.game.timer
            self.attack()
    
    def takeDamage(self):
        if self.health > 0:
            self.health -= 1

    def update(self):
        self.room.checkBounds(self)
        if self.room == self.game.hero.room:
            self.simpleAI()
        else:
            self.weap.aim(self.x + 5, self.y)
            self.weap.shooting = False
        
        if self.health == 0:
            self.game.killCount += 1
            self.weap.kill()
            self.kill()

        for wall in self.room.walls:
            wall.checkBounds(self)

        super().update()
