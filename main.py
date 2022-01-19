import pygame
import random
import os
import sys
import numpy as np
import sqlite3
from datetime import datetime
from win32api import GetSystemMetrics
from PIL import Image

db = sqlite3.connect("data/histori.db")
sql = db.cursor()

all_sprites = pygame.sprite.Group()
width_screen = GetSystemMetrics(0)
height_screen = GetSystemMetrics(1)
Door = pygame.sprite.Group()
atack_sprites = pygame.sprite.Group()
n_room = 0
render_position = "menu"
mob_list = ["black_wolf", "snake", "green_snake"]

with open("data/histori.txt", encoding="utf-8") as f:
    histori = str(f.read())


def resize_image(input_image_path, size):
    original_image = Image.open(input_image_path)
    original_image.resize(size).save(input_image_path)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Board:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.cell_size = 50

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surface, ):
        wcolor = pygame.Color("white")
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface, wcolor,
                                 (self.cell_size * j, self.cell_size * i,
                                  self.cell_size, self.cell_size),
                                 1 if self.board[i][j] == 0 else 0)

    def get_click(self, mouse_pos):
        cell_coords = self.get_cell(mouse_pos)
        if cell_coords is None:
            return

        self.on_click(cell_coords)

    def get_cell(self, mouse_pos):
        board_width = self.width * self.cell_size
        board_height = self.height * self.cell_size
        if mouse_pos[0] < board_width:
            if mouse_pos[1] < self.top + board_height:
                cell_coords_1 = mouse_pos[1] // self.cell_size, mouse_pos[0]
                cell_coords = cell_coords_1 // self.cell_size
                return cell_coords
        return None

    def on_click(self, cell_coords):
        x = cell_coords[0]
        y = cell_coords[1]
        if (x < self.cell_size * self.width and x > 0):
            if (y < self.cell_size * self.height and y > 0):
                i = x // self.cell_size
                j = y // self.cell_size
                return (i, j)
        else:
            return None


class Mob(AnimatedSprite):

    def __init__(self, name_mob, size):
        left = width_screen % 80
        top = height_screen % 80
        self.rect = pygame.Rect((left, top, 64, 64))
        mob = load_image(f"mob/{name_mob}/down.png")
        super().__init__(mob, 8, 1, 64, 64)
        self.name_mob = name_mob
        mob_x_in_board = random.randrange(3, size[0] - 2)
        self.rect.x = left + mob_x_in_board * 80
        mob_y_in_board = random.randrange(3, size[1] - 2)
        self.rect.y = top + mob_y_in_board * 80
        self.add(mobs)
        self.motion_vector = "down"
        self.last_motion_vector = "down"
        self.font = pygame.font.Font("data/acrade.ttf", height_screen // 50)

        self.max_hp = 100
        self.hp = 100
        self.atack = 10
        self.speed = 5

        Mob_list.append(self)

    def update(self):
        if self.hp > 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            x = coordinates[0] - self.rect.x
            y = coordinates[1] - self.rect.y
            dist = np.sqrt(x * x + y * y)
            if dist > 0:
                x /= dist
                y /= dist
            move_dist = min(self.speed, dist)
            self.rect = self.rect.move((move_dist * x, move_dist * y))

            self.hp_text = self.font.render(str(self.hp), 40, (0, 0, 0))
            self.hp_rect = self.hp_text.get_rect(center=(self.rect.x + 40, self.rect.y))

            screen.blit(self.hp_text, self.hp_rect)

            if y < 0 and x < y:
                self.motion_vector = "up"
            elif y > 0 and x < y:
                self.motion_vector = "down"
            elif x < 0 and x > y:
                self.motion_vector = "left"
            elif x > 0 and x > y:
                self.motion_vector = "right"
            if self.last_motion_vector != self.motion_vector:
                image = load_image(f"mob/{self.name_mob}/{self.motion_vector}.png")
                super().__init__(image, 8, 1, 80, 80)

            self.last_motion_vector = self.motion_vector
            screen.blit(self.image, self.rect)


class Create_Mob:

    def __init__(self, n, size_room):
        for _ in range(n):
            Mob(random.choice(mob_list), size_room)


class Atack_Player(AnimatedSprite):

    def __init__(self, pos, name_atack):
        self.speed = 10
        x = pos[0] - int(coordinates[0])
        y = pos[1] - int(coordinates[1])
        dist = np.sqrt(x * x + y * y)
        if dist > 0:
            x /= dist
            y /= dist
        move_dist = min(self.speed, dist)
        self.move = (move_dist * x, move_dist * y)
        if abs(x) > abs(y):
            if x > 0:
                v = "right"
            else:
                v = "left"
        else:
            if y > 0:
                v = "down"
            else:
                v = "top"
        image = load_image(f"atack/{name_atack}_{v}.png")
        self.rect = pygame.Rect((coordinates[0], coordinates[1], 64, 64))
        if name_atack == "Energy_Ball":
            super().__init__(image, 9, 1, 32, 32)
            self.atack = 10
            self.mp = 10
        elif name_atack == "Fire_Ball":
            super().__init__(image, 45, 1, 64, 64)
            self.atack = 50
            self.mp = 25
        self.mask = pygame.mask.from_surface(self.image)
        self.add(atack_sprites)

    def update(self):
        self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.rect = self.rect.move(self.move)
        screen.blit(self.image, self.rect)
        if pygame.sprite.spritecollideany(self, mobs):
            for mob in pygame.sprite.spritecollide(self, mobs, False):
                if mob.hp > 0:
                    mob.hp -= self.atack
                    self.kill()
                    del self
                    break


class Create_Player(AnimatedSprite):

    def __init__(self):
        global check

        image = load_image(f"hero_ani/{motion_vector}.png")
        self.rect = pygame.Rect((width_screen // 2, height_screen // 2, 80, 80))
        super().__init__(image, 4, 1, 80, 80)
        self.mask = pygame.mask.from_surface(self.image)
        self.max_hp = 100
        self.max_mp = 100
        self.speed = 10
        self.hp = 100
        self.mp = 100
        self.atack = 10
        self.font = pygame.font.Font("data/acrade.ttf", height_screen // 20)

    def update(self):
        global last_motion_vector, coordinates

        coordinates = [self.rect.x, self.rect.y]

        if last_motion_vector != motion_vector:
            image = load_image(f"hero_ani/{motion_vector}.png")
            super().__init__(image, 4, 1, 80, 80)
            if motion_vector == "up":
                self.rect = self.rect.move((0, -self.speed))
            elif motion_vector == "down":
                self.rect = self.rect.move((0, self.speed))
            elif motion_vector == "right":
                self.rect = self.rect.move((self.speed, 0))
            elif motion_vector == "left":
                self.rect = self.rect.move((-self.speed, 0))

        if motion and not pygame.sprite.spritecollideany(self, self.wall):
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            if motion_vector == "up":
                self.rect = self.move_image((0, -self.speed))
            elif motion_vector == "down":
                self.rect = self.move_image((0, self.speed))
            elif motion_vector == "right":
                self.rect = self.move_image((self.speed, 0))
            elif motion_vector == "left":
                self.rect = self.move_image((-self.speed, 0))

        if pygame.sprite.spritecollideany(self, mobs):
            pos = (self.rect.x, self.rect.y)
            collide_mob = pygame.sprite.spritecollide(self, mobs, dokill=False)
            for mob in collide_mob:
                if mob.hp > 0:
                    c.check -= mob.atack
                    self.hp -= mob.atack

        self.hp_text = self.font.render(f"HP: {self.max_hp} / {self.hp}", 40, (0, 0, 0))
        self.hp_rect = self.hp_text.get_rect()

        self.mp_text = self.font.render(f"MP: {self.max_mp} / {self.mp}", 40, (0, 0, 0))
        self.mp_rect = pygame.Rect((0, self.hp_rect.y + self.hp_rect.h, self.hp_rect.w, self.hp_rect.h))

        last_motion_vector = motion_vector

    def move_image(self, move):
        self.move = pygame.sprite.Sprite(pygame.sprite.Group())
        self.move.kill()
        self.move.image = self.image
        self.move.rect = self.rect.move(move)
        if not pygame.sprite.spritecollideany(self.move, self.wall):
            return self.move.rect
        else:
            return self.rect

    def draw(self, w):
        self.wall = w
        self.update()
        screen.blit(self.hp_text, self.hp_rect)
        screen.blit(self.mp_text, self.mp_rect)
        screen.blit(self.image, self.rect)


class Room(pygame.sprite.Sprite):

    def __init__(self, group, filename, coordinates):
        self.image = load_image(filename)
        self.rect = pygame.Rect((coordinates[0], coordinates[1], 80, 80))

    def update(self):
        pass


class Create_Door(AnimatedSprite):

    def __init__(self):
        image = load_image("door_ani.png")
        self.rect = pygame.Rect((width_screen // 2, height_screen // 2, 64, 64))
        super().__init__(image, 14, 1, 64, 64)
        self.rect = self.image.get_rect(center=(width_screen // 2, height_screen // 2))
        self.kill()
        self.add(Door)

    def update(self):
        if self.cur_frame < 13:
            self.cur_frame += 1
            self.image = self.frames[self.cur_frame]
        else:
            self.image = load_image("door.png")

    def draw(self):
        self.update()
        screen.blit(self.image, self.rect)


class Create_Dungeon:

    def __init__(self):
        self.width = width_screen // 80
        self.height = height_screen // 80
        self.top = width_screen % 80 // 2
        self.left = height_screen % 80 // 2
        self.dict_room = dict()
        self.dict_size = {"start_room": (8, 8), "end_room": (8, 8),
                          "monster_room": (width_screen // 80 - 1, height_screen // 80 - 1),
                          "boss_room": (width_screen // 80 - 1, height_screen // 80 - 1)}
        self.create_room()

    def create_room(self):
        room_list = ["start_room", "monster_room", "boss_room", "end_room"]
        for name_room in room_list:
            s = self.dict_size[name_room]
            self.dict_room[name_room] = dict()
            self.dict_room[name_room]["wall"] = pygame.sprite.Group()
            self.dict_room[name_room]["floor"] = pygame.sprite.Group()
            for i in range(s[0]):
                for j in range(s[1]):
                    sprite = pygame.sprite.Sprite()
                    x = width_screen - self.left
                    x -= (self.width - s[0]) * 40 + (s[0] - i) * 80
                    y = height_screen - self.top
                    y -= (self.height - s[1]) * 40 + (s[1] - j) * 80
                    if i == 0 and j == 0:
                        image = "wall/wall_side_1.png"
                    elif i == 0 and j == s[1] - 1:
                        image = "wall/wall_side_2.png"
                    elif i == s[0] - 1 and j == s[1] - 1:
                        image = "wall/wall_side_3.png"
                    elif i == s[0] - 1 and j == 0:
                        image = "wall/wall_side_4.png"
                    elif i == 0:
                        image = "wall/wall_left.png"
                    elif j == s[1] - 1:
                        image = "wall/wall_bottom.png"
                    elif i == s[0] - 1:
                        image = "wall/wall_right.png"
                    elif j == 0:
                        image = "wall/wall_top.png"
                    elif i == 1 and j == 1:
                        image = "floor/floor_side_1.png"
                    elif i == 1 and j == s[1] - 2:
                        image = "floor/floor_side_2.png"
                    elif i == s[0] - 2 and j == s[1] - 2:
                        image = "floor/floor_side_3.png"
                    elif i == s[0] - 2 and j == 1:
                        image = "floor/floor_side_4.png"
                    elif i == 1:
                        image = "floor/floor_side_left.png"
                    elif j == s[1] - 2:
                        image = "floor/floor_side_bottom.png"
                    elif i == s[0] - 2:
                        image = "floor/floor_side_right.png"
                    elif j == 1:
                        image = "floor/floor_side_top.png"
                    else:
                        image = "floor/floor.png"
                    sprite.image = load_image(image)
                    sprite.rect = pygame.Rect((x, y, 80, 80))
                    if "wall" in image:
                        sprite.add(self.dict_room[name_room]["wall"])
                    else:
                        sprite.add(self.dict_room[name_room]["floor"])


class Menu:

    def __init__(self, size):
        global check

        check = 0

        resize_image("data/start_menu.jpeg", size)
        self.wallpaper = load_image("start_menu.jpeg")

        name_font = pygame.font.Font("data/acrade.ttf", size[1] // 4)
        self.name = name_font.render("Dungeon", 40, (150, 111, 95))
        self.name_rect = self.name.get_rect(center=(size[0] // 2,
                                                    size[1] // 3))

        font = pygame.font.Font("data/acrade.ttf", size[1] // 6)
        self.start = font.render("Start Game", 40, (150, 111, 95))
        self.start_rect = self.start.get_rect(center=(size[0] // 2,
                                                      size[1] // 2))

        # self.setting = font.render("Setting", 40, (150, 111, 95))
        # setting_rect = (size[0] // 2, size[1] // 2 + size[1] // 6)
        # self.setting_rect = self.setting.get_rect(center=setting_rect)

        self.quit = font.render("Quit Game", 40, (150, 111, 95))
        self.quit_rect = self.quit.get_rect(center=(size[0] // 2, size[1] // 2 + size[1] // 6))

    def render(self):
        screen.blit(self.wallpaper, (0, 0))
        screen.blit(self.start, self.start_rect)
        # screen.blit(self.setting, self.setting_rect)
        screen.blit(self.name, self.name_rect)
        screen.blit(self.quit, self.quit_rect)

    def get_click(self, mouse_pos):
        pos = self.get_cell(mouse_pos)
        if pos == "None":
            pass
        else:
            self.on_click(pos)

    def get_cell(self, pos):
        if self.start_rect.collidepoint(pos):
            return "game"
        # elif self.setting_rect.collidepoint(pos):
        #     return "setting"
        elif self.quit_rect.collidepoint(pos):
            return "quit"
        else:
            return "None"

    def on_click(self, text):
        global render_position
        if text == "game":
            render_position = text
        elif text == "setting":
            render_position = text
        elif text == "quit":
            render_position = text


class Histori:

    def __init__(self):
        self.font = pygame.font.Font("data/histori.otf", height_screen // 20)
        self.n = 1
        self.space = self.font.size(" ")[0]
        self.text_dict = dict()
        self.clock = pygame.time.Clock()
        self.full = True

    def update(self):
        self.text = ""
        self.t = self.font.render(self.text, 40, (255, 255, 255))
        self.rect = self.t.get_rect(center=(width_screen // 2, height_screen // 2))
        for word in histori.split(" "):
            if self.rect.w + self.space * 2 + self.font.render(word, 40, "white").get_rect().w >= width_screen:
                self.text_dict[self.t] = self.rect
                for key in self.text_dict.keys():
                    self.text_dict[key] = self.text_dict[key].move((0, -1 * (self.rect.h + 10)))
                self.text = ""
            for i in range(len(word)):
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == 27:
                            quit()
                screen.fill((0, 0, 0))
                self.text += word[i]
                self.t = self.font.render(self.text, True, (255, 255, 255))
                self.rect = self.t.get_rect(center=(width_screen // 2, height_screen // 2))
                if self.full:
                    if self.text_dict.keys():
                        for item in self.text_dict.items():
                            screen.blit(item[0], item[1])
                        screen.blit(self.t, self.rect)
                    else:
                        screen.blit(self.t, self.rect)
                    pygame.display.flip()
                    self.clock.tick(10)
            self.text += " "
        for item in self.text_dict.items():
            screen.blit(item[0], item[1])
        screen.blit(self.t, self.rect)
        pygame.display.flip()

    def draw(self):
        self.full = False


class Check:

    def __init__(self):
        self.check = 0
        self.font = pygame.font.Font("data/histori.otf", height_screen // 20)
        self.n = 255
        self.run = True

    def update(self):
        self.text = self.font.render(f"Счёт: {self.check}", 40, (self.n, self.n, self.n))
        self.rect = self.text.get_rect(center=(width_screen // 2, height_screen // 2))
        screen.blit(self.text, self.rect)
        if self.n == 255:
            self.run = False
        elif self.n == 0:
            self.run = True
        if self.run:
            self.n += 1
        else:
            self.n -= 1


class Dungeon:

    def __init__(self):
        global screen, render_position

        pygame.init()
        screen = pygame.display.set_mode((width_screen, height_screen), pygame.FULLSCREEN)
        pygame.display.set_caption("Подземелье")
        self.running = True
        self.clock = pygame.time.Clock()

        while self.running:
            if render_position == "menu":
                screen.fill((0, 0, 0))
                pygame.display.flip()
                self.start_menu()
            elif render_position == "game":
                screen.fill((0, 0, 0))
                pygame.display.flip()
                self.game()
            elif render_position == "quit":
                pygame.quit()
                exit()

    def start_menu(self):
        running = True
        self.menu = Menu((width_screen, height_screen))

        while running:
            self.menu.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu.get_click(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == 27:
                        pygame.quit()
                        exit()
            if render_position != "menu":
                self.__init__()
            self.clock.tick(10)
            pygame.display.flip()

    def game(self):
        global motion_vector, last_motion_vector, motion, render_postion, mobs, Mob_list, c

        h = Histori()
        h.update()

        c = Check()
        Mob_list = []
        motion_vector = "down"
        last_motion_vector = "down"
        motion = False
        mobs = pygame.sprite.Group()
        player = Create_Player()
        dungeon = Create_Dungeon()
        Create_Mob(7, dungeon.dict_size["monster_room"])
        room_list = ["start_room", "monster_room", "monster_room"]
        for name_room in room_list:
            door = Create_Door()
            wall = dungeon.dict_room[name_room]["wall"].copy()
            floor = dungeon.dict_room[name_room]["floor"].copy()
            running = True
            while running:
                if player.mp + 2 < player.max_mp:
                    player.mp += 2
                else:
                    player.mp = player.max_mp
                screen.fill((81, 64, 71))
                wall.draw(screen)
                floor.draw(screen)
                if player.hp > 0:
                    player.draw(wall)
                else:
                    self.start_menu()
                if name_room != "monster_room" or all(i.hp <= 0 for i in mobs.sprites()):
                    door.draw()
                    atack_sprites.empty()
                else:
                    if name_room == "monster_room":
                        for mob in Mob_list:
                            if mob.hp > 0:
                                mob.update()
                        c.check += mob.max_hp * (len(Mob_list) -  len(list(filter(lambda x: x.hp > 0, Mob_list))))
                        Mob_list = list(filter(lambda x: x.hp > 0, Mob_list))
                for sprite in atack_sprites:
                    if pygame.sprite.spritecollideany(sprite, wall):
                        sprite.kill()
                        del sprite
                atack_sprites.update()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        motion = True
                        if event.key == 119:
                            motion_vector = "up"
                        elif event.key == 115:
                            motion_vector = "down"
                        elif event.key == 97:
                            motion_vector = "left"
                        elif event.key == 100:
                            motion_vector = "right"
                        elif event.key == 27:
                            pygame.quit()
                            exit()
                    if event.type == pygame.KEYUP:
                        motion = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and player.mp >= 15:
                            Atack_Player(event.pos, "Energy_Ball")
                            player.mp -= 15
                        elif event.button == 3 and player.mp >= 45:
                            Atack_Player(event.pos, "Fire_Ball")
                            player.mp -= 45
                if pygame.sprite.spritecollideany(player, Door) and door.cur_frame > 12:
                    break
                if render_position != "game":
                    self.__init__()
                self.clock.tick(12)
            for i in dungeon.dict_room[name_room]["wall"]:
                i.kill()
                del i
            dungeon.dict_room[name_room]["wall"] = pygame.sprite.Group()
            for i in dungeon.dict_room[name_room]["floor"]:
                i.kill()
                del i
            dungeon.dict_room[name_room]["floor"] = pygame.sprite.Group()
        c.check += 10 * int(player.hp)
        self.end()

    def end(self):
        global render_postion
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            screen.fill((0, 0, 0))
            c.update()
            pygame.display.flip()
            self.clock.tick(100)
        screen.fill((0, 0, 0))
        pygame.display.flip()

        time = "".join(str(datetime.now()).split(","))
        sql.execute(f"INSERT INTO Histori VALUES ('{time}', '{c.check}')")
        db.commit()
        render_postion = "menu"
        self.start_menu()


if __name__ == '__main__':
    Dungeon()
