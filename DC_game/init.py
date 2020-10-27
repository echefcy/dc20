from gameRoom import *
from gameWeap import *
import copy

WIDTH = 1000
HEIGHT = 700
TITLE = "hello"

class InfoHUD:
    def __init__(self, game):
        self.texture = None
        self.game = game
        self.width = WIDTH/4
        self.height = HEIGHT/6
        self.marginX = WIDTH/50
        self.marginY = HEIGHT/50
        self.healthTopMargin = self.height/7
        self.healthLRMargin = self.width/10
        self.healthWidth = (self.game.hero.health/self.game.hero.maxHealth)*(self.width - self.healthLRMargin*2)
        self.maxHealthWidth = (self.width - self.healthLRMargin*2)
        self.healthHeight = self.height/5
        self.healthBottomMargin = self.healthTopMargin
        self.text = f"LV{(self.game.level-5)//2 + 1}  SIZE: {self.game.level}"
    
    def draw(self):
        if self.texture == None:
            arcade.draw_lrtb_rectangle_filled(self.marginX, self.marginX + self.width, HEIGHT - self.marginY, HEIGHT - self.marginY - self.height, arcade.color.MINT)
        else:
            arcade.draw_lrwh_rectangle_textured(self.marginX, HEIGHT - self.marginY - self.height, self.width, self.height, self.texture)
        left = self.marginX + self.healthLRMargin
        top = HEIGHT - self.marginY - self.healthTopMargin
        arcade.draw_lrtb_rectangle_outline(left, left + self.maxHealthWidth, top, top - self.healthHeight, arcade.color.RED, 5)
        arcade.draw_lrtb_rectangle_filled(left, left + self.healthWidth, top, top - self.healthHeight, arcade.color.RED)
        arcade.draw_text(self.text, left, top - self.healthHeight - self.healthBottomMargin, arcade.color.BLACK, 26,
            font_name="Times", anchor_y="top")

    def update(self):
        self.healthTopMargin = self.height/7
        self.healthLRMargin = self.width/10
        self.healthWidth = (self.game.hero.health/self.game.hero.maxHealth)*(self.width - self.healthLRMargin*2)
        self.maxHealthWidth = (self.width - self.healthLRMargin*2)
        self.healthHeight = self.height/5

class GameView(arcade.View):
    # https://arcade.academy/examples/view_instructions_and_game_over.html
    def __init__(self, level, kc, buffs):
        super().__init__()
        self.killCount = kc
        self.level = level
        self.buffs = buffs
        self.setup()

    def setup(self):
        # self.background = arcade.load_texture("Bliss.png")
        arcade.set_background_color(arcade.color.DARK_IMPERIAL_BLUE)
        self.gameOver = False
        self.nextLevel = False
        self.dynamicList = arcade.SpriteList()
        self.enemyProjectiles = arcade.SpriteList()
        self.heroProjectiles = arcade.SpriteList()

        for bullet in self.enemyProjectiles:
            bullet.kill()
        for bullet in self.heroProjectiles:
            bullet.kill()

        self.rooms = []
        self.floor = genMap(self.level)
        self.mapToRooms()
        format2dList(self.floor)
        print()

        self.keys = set()
        self.mouseX = 100
        self.mouseY = 100
        self.timer = 0
        self.mouseDown = False

        # https://vignette.wikia.nocookie.net/soul-knight/images/6/6b/Knight.png/revision/latest?cb=20190519083100
        self.hero = Hero(self, 500, 350, "Knight.png", scale=0.35, speed=15)
        # https://vignette.wikia.nocookie.net/soul-knight/images/a/a2/Sprite_BadPistol.png/revision/latest?cb=20181217093123
        self.weap = Pistol(self.hero)
        self.buff(self.buffs)

        self.screenX = self.hero.x - WIDTH/2
        self.screenY = self.hero.y - HEIGHT/2
        self.HUD = InfoHUD(self)

        self.drawCache = set()

    def buff(self, buffList):
        for b in buffList:
            if b == "improved reload":
                self.weap.reload /= 1.3
            elif b == "greatly improved reload\nbut more inaccurate":
                self.weap.reload /= 2
                self.weap.inacc *= 2.2
            elif b == "increased bullet size":
                self.weap.bulletSize *= 1.2
            elif b == "increased bullet speed":
                self.weap.projectileSpeed *= 1.4
            elif b == "greatly increased bullet speed\nbut smaller bullets":
                self.weap.bulletSize /= 1.5
                self.weap.projectileSpeed *= 2
            elif b == "greatly improved reload\nbut smaller bullets":
                self.weap.reload *= 2
                self.weap.bulletSize /= 1.5
            elif b == "improved hero speed":
                self.hero.speed *= 1.65
            elif b == "improved hero health":
                self.hero.maxHealth += 4
                self.hero.health += 4

    def mapToRooms(self):
        # make a copy of the original map
        floorMap = copy.deepcopy(self.floor)

        # initial safe room (in the bottom left corner)
        rm = SafeRoom(self)
        floorMap[self.level - 1][0] = rm
        self.rooms.append(rm)

        rm = PortalRoom(self, (self.level - 1)*(ROOM_WIDTH + HALL_LENGTH), (self.level - 1)*(ROOM_HEIGHT + HALL_LENGTH))
        floorMap[0][self.level - 1] = rm
        self.rooms.append(rm)

        for row in range(self.level - 1, -1, -1):
            for col in range(self.level):
                if floorMap[row][col] == 1:
                    rm = getRoom(self.level)(self, col*(ROOM_WIDTH + HALL_LENGTH), (self.level - row - 1)*(ROOM_HEIGHT + HALL_LENGTH), tag=f"{row}, {col}")
                    floorMap[row][col] = rm
                    self.rooms.append(rm)

        # horizontal connections
        for row in range(self.level - 1, -1, -1):
            for col in range(self.level - 1):
                left = floorMap[row][col]
                right = floorMap[row][col+1]
                if isinstance(left, Room) and isinstance(right, Room):
                    self.rooms.append(Hall(self, (ROOM_WIDTH + HALL_LENGTH)*col+(ROOM_WIDTH),
                        (ROOM_HEIGHT + HALL_LENGTH)*(self.level - row - 1) + (ROOM_HEIGHT/2 - HALL_HEIGHT/2), "h"))
                    left.addGate(f'e{HALL_HEIGHT}')
                    right.addGate(f'w{HALL_HEIGHT}')
        # vertical connections
        for col in range(self.level):
            for row in range(self.level - 1, 0, -1):
                top = floorMap[row - 1][col]
                bottom = floorMap[row][col]
                if isinstance(top, Room) and isinstance(bottom, Room):
                    self.rooms.append(Hall(self, (ROOM_WIDTH + HALL_LENGTH)*col + (ROOM_WIDTH/2 - HALL_HEIGHT/2), 
                        (ROOM_HEIGHT + HALL_LENGTH)*(self.level - row - 1)+(ROOM_HEIGHT), "v"))
                    top.addGate(f's{HALL_HEIGHT}')
                    bottom.addGate(f'n{HALL_HEIGHT}')
                    
    def on_draw(self):
        arcade.start_render()
        # arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        for room in self.drawCache:
            if isinstance(room, Hall):
                room.draw()
        for room in self.drawCache:
            if not isinstance(room, Hall):
                room.draw()

        self.dynamicList.draw()
        self.enemyProjectiles.draw()
        self.heroProjectiles.draw()

        self.HUD.draw()

    def on_key_press(self, key, modifiers):
        self.keys.add(key)
    
    def on_key_release(self, key, modifiers):
        self.keys.discard(key)

    def on_update(self, delta_time):
        self.timer += delta_time
        self.screenX = self.hero.x - WIDTH/2
        self.screenY = self.hero.y - HEIGHT/2
        for room in self.drawCache:
            if isinstance(room, EnemyRoom):
                room.update()

        self.dynamicList.update()
        self.enemyProjectiles.update()
        self.heroProjectiles.update()

        self.HUD.update()
        if self.gameOver:
            gameOverView = GameOverView((self.level-5)//2 + 1, self.killCount)
            self.window.show_view(gameOverView)
        elif self.nextLevel:
            transitionView = TransitionView(self.level, self.killCount, self.buffs)
            self.window.show_view(transitionView)

    # https://arcade.academy/examples/move_mouse.html
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseX = x
        self.mouseY = y
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouseDown = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouseDown = False

class TextButton:
    def __init__(self, app, text, cx, cy, width, height, color, txtColor):
        self.app = app
        self.text = text
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.color = color
        self.txtColor = txtColor
    
    def clicking(self):
        if (self.cx - self.width/2 < self.app.mouseX < self.cx + self.width/2
            and self.cy - self.height/2 < self.app.mouseY < self.cy + self.height/2) and self.app.mouseDown:
            return True
        return False

    def draw(self):
        arcade.draw_rectangle_filled(self.cx, self.cy, self.width, self.height, self.color)
        arcade.draw_text(self.text, self.cx, self.cy, self.txtColor, self.height/6, font_name="Times", bold=True, anchor_x="center", anchor_y="center")

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.playGame = TextButton(self, "Play", WIDTH/4, HEIGHT/4, WIDTH/5, HEIGHT/5, arcade.color.BLACK, arcade.color.WHITE)
        self.instructions = TextButton(self, "Instructions", 3*WIDTH/4, HEIGHT/4, WIDTH/5, HEIGHT/5, arcade.color.BLACK, arcade.color.WHITE)
        self.mouseX = 0
        self.mouseY = 0
        self.mouseDown = False
    
    def on_show(self):
        arcade.set_background_color(arcade.color.MINT)
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("The Maze", WIDTH/2, 3*HEIGHT/4, arcade.color.WHITE, 40, font_name="Times", bold=True, anchor_x="center", anchor_y="center")
        self.playGame.draw()
        self.instructions.draw()
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseX = x
        self.mouseY = y
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouseDown = True
    
    def on_update(self, delta_time):
        if self.playGame.clicking():
            self.playGame.color = arcade.color.WHITE
            self.playGame.txtColor = arcade.color.BLACK
            gameView = GameView(5, 0, [])
            self.window.show_view(gameView)
        if self.instructions.clicking():
            self.playGame.color = arcade.color.WHITE
            self.playGame.txtColor = arcade.color.BLACK
            instructionView = InstructionView()
            self.window.show_view(instructionView)

class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
    
    def on_show(self):
        arcade.set_background_color(arcade.color.MINT)

    def on_draw(self):
        arcade.start_render()
        instructions = """\
            Instructions:

            - go through as many mazes as possible!
            - find the portal (blue) room on the top right of the map to advance
            - green rings heal you
            - fight enemies
            - get buffs for solving a maze
            - gets increasingly difficult
            - press anywhere to go back"""
        arcade.draw_text(instructions, WIDTH/2, HEIGHT/2, arcade.color.WHITE, 20, font_name="Times", bold=True, anchor_x="center", anchor_y="center")
    
    def on_mouse_press(self, x, y, button, modifiers):
        titleView = TitleView()
        self.window.show_view(titleView)

class TransitionView(arcade.View):
    def __init__(self, level, kC, buffs):
        super().__init__()
        self.level = level
        self.killCount = kC
        self.buffs = buffs
        self.mouseX = 0
        possibleBuffs = ["improved reload", "greatly improved reload\nbut more inaccurate", "increased bullet size",
            "increased bullet speed", "greatly increased bullet speed\nbut smaller bullets",
            "greatly improved reload\nbut smaller bullets", "improved hero speed", "improved hero health"]
        self.buffChoices = [random.choice(possibleBuffs)] 
        possibleBuffs.remove(self.buffChoices[-1])
        self.buffChoices.append(random.choice(possibleBuffs))
        possibleBuffs.remove(self.buffChoices[-1])
        self.buffChoices.append(random.choice(possibleBuffs))
    
    def on_show(self):
        arcade.set_background_color(arcade.color.MINT)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(self.buffChoices[0], 
            WIDTH/6, HEIGHT/2, arcade.color.WHITE, 18, font_name="Times", anchor_x="center", anchor_y="center")
        arcade.draw_text(self.buffChoices[1], 
            WIDTH/2, HEIGHT/2, arcade.color.WHITE, 18, font_name="Times", anchor_x="center", anchor_y="center")
        arcade.draw_text(self.buffChoices[2], 
            5*WIDTH/6, HEIGHT/2, arcade.color.WHITE, 18, font_name="Times", anchor_x="center", anchor_y="center")

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseX = x

    def on_mouse_press(self, x, y, button, modifiers):
        newBuffs = copy.deepcopy(self.buffs)
        if button == arcade.MOUSE_BUTTON_LEFT:
            newBuffs.append(self.buffChoices[int(self.mouseX//(WIDTH/3))])
            gameView = GameView(self.level + 2, self.killCount, newBuffs)
            self.window.show_view(gameView)

class GameOverView(arcade.View):
    def __init__(self, maxLevel, enemiesKilled):
        super().__init__()
        self.maxLevel = maxLevel
        self.enemiesKilled = enemiesKilled

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(f"           Game Over\nPress anywhere to restart", WIDTH/2, HEIGHT/2 + HEIGHT/8, arcade.color.WHITE, 24, font_name="Times", bold=True, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Max level reached:{self.maxLevel}\nEnemies killed: {self.enemiesKilled}", 
            WIDTH/2, HEIGHT/2 - HEIGHT/8, arcade.color.WHITE, 18, font_name="Times", anchor_x="center", anchor_y="center")
    
    def on_mouse_press(self, x, y, button, modifiers):
        gameView = GameView(5, 0, [])
        self.window.show_view(gameView)

def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    titleView = TitleView()
    window.show_view(titleView)
    arcade.run()

if __name__ == "__main__":
    main()