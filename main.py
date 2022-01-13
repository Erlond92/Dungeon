import pygame
import random
import os
import sys
import time
import numpy as np
from win32api import GetSystemMetrics
from PIL import Image

floor = pygame.sprite.Group()
wall = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
width_screen = GetSystemMetrics(0)
height_screen = GetSystemMetrics(1)
n_room = 0


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
        super().__init__(mob, 4, 1, 64, 64)
        self.name_mob = name_mob
        mob_x_in_board = random.randrange(3, size[0] - 2)
        self.rect.x = left + mob_x_in_board * 80
        mob_y_in_board = random.randrange(3, size[1] - 2)
        self.rect.y = top + mob_y_in_board * 80
        self.speed = 5
        self.add(mobs)
        self.motion_vector = "down"
        self.last_motion_vector = "down"
        self.atack = 10

    def update(self):
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
            super().__init__(image, 4, 1, 80 ,80)

        self.last_motion_vector = self.motion_vector


class Create_Mob:

    def __init__(self, name_mob, n, size_room):
        for _ in range(n):
            Mob(name_mob, size_room)


class Create_Player(AnimatedSprite):

    def __init__(self):
        image = load_image(f"hero_ani/{motion_vector}.png")
        self.rect = pygame.Rect((width_screen // 2, height_screen // 2,
                                      80, 80))
        super().__init__(image, 4, 1, 80, 80)
        self.mask = pygame.mask.from_surface(self.image)
        self.add(all_sprites)

        self.speed = 10
        self.health = 100
        self.atack = 10

    def update(self):
        global last_motion_vector, coordinates

        coordinates = [self.rect.x, self.rect.y]

        if last_motion_vector != motion_vector:
            image = load_image(f"hero_ani/{motion_vector}.png")
            super().__init__(image, 4, 1, 80 ,80)
            if motion_vector == "up":
                self.rect = self.rect.move((0, -self.speed))
            elif motion_vector == "down":
                self.rect = self.rect.move((0, self.speed))
            elif motion_vector == "right":
                self.rect = self.rect.move((self.speed, 0))
            elif motion_vector == "left":
                self.rect = self.rect.move((-self.speed, 0))

        if motion and not pygame.sprite.spritecollideany(self, wall):
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            if motion_vector == "up":
                self.rect = self.rect.move((0, -self.speed))
            elif motion_vector == "down":
                self.rect = self.rect.move((0, self.speed))
            elif motion_vector == "right":
                self.rect = self.rect.move((self.speed, 0))
            elif motion_vector == "left":
                self.rect = self.rect.move((-self.speed, 0))

        if pygame.sprite.spritecollideany(self, mobs):
            pos = (self.rect.x, self.rect.y)
            mob = pygame.sprite.spritecollide(self, mobs, dokill=False)
            self.health -= mob[0].atack

        last_motion_vector = motion_vector

    def draw(self):
        screen.blit(self.image, self.rect)


class Room(pygame.sprite.Sprite):

    def __init__(self, group, filename, coordinates):
        super().__init__(group)
        self.image = load_image(filename)
        self.rect = pygame.Rect((coordinates[0], coordinates[1], 80, 80))
        self.add(all_sprites)

    def update(self):
        pass


class Create_Dungeon:

    def __init__(self, name_room):
        self.width = width_screen // 80
        self.height = height_screen // 80
        self.top = width_screen % 80 // 2
        self.left = height_screen % 80 // 2
        self.dict_room = {"start_room": (8, 8), "chest_room": (8, 8),
                          "monster_room": (self.width - 1, self.height - 1),
                          "boss_room": (self.width - 1, self.height - 1)}
        self.create_room(name_room)

    def create_room(self, name_room):
        s = self.dict_room[name_room]
        for i in range(s[0]):
            for j in range(s[1]):
                x = width_screen - self.left
                x -= (self.width - s[0]) * 40 + (s[0] - i) * 80
                y = height_screen - self.top
                y -= (self.height - s[1]) * 40 + (s[1] - j) * 80
                if i == 0 and j == 0:
                    Room(wall, "wall/wall_side_1.png", (x, y))
                elif i == 0 and j == s[1] - 1:
                    Room(wall, "wall/wall_side_2.png", (x, y))
                elif i == s[0] - 1 and j == s[1] - 1:
                    Room(wall, "wall/wall_side_3.png", (x, y))
                elif i == s[0] - 1 and j == 0:
                    Room(wall, "wall/wall_side_4.png", (x, y))
                elif i == 0:
                    Room(wall, "wall/wall_left.png", (x, y))
                elif j == s[1] - 1:
                    Room(wall, "wall/wall_bottom.png", (x, y))
                elif i == s[0] - 1:
                    Room(wall, "wall/wall_right.png", (x, y))
                elif j == 0:
                    Room(wall, "wall/wall_top.png", (x, y))
                elif i == 1 and j == 1:
                    Room(floor, "floor/floor_side_1.png", (x, y))
                elif i == 1 and j == s[1] - 2:
                    Room(floor, "floor/floor_side_2.png", (x, y))
                elif i == s[0] - 2 and j == s[1] - 2:
                    Room(floor, "floor/floor_side_3.png", (x, y))
                elif i == s[0] - 2 and j == 1:
                    Room(floor, "floor/floor_side_4.png", (x, y))
                elif i == 1:
                    Room(floor, "floor/floor_side_left.png", (x, y))
                elif j == s[1] - 2:
                    Room(floor, "floor/floor_side_bottom.png", (x, y))
                elif i == s[0] - 2:
                    Room(floor, "floor/floor_side_right.png", (x, y))
                elif j == 1:
                    Room(floor, "floor/floor_side_top.png", (x, y))
                else:
                    Room(floor, "floor/floor.png", (x, y))


class Menu:

    def __init__(self, size):
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

        self.setting = font.render("Setting", 40, (150, 111, 95))
        setting_rect = (size[0] // 2, size[1] // 2 + size[1] // 6)
        self.setting_rect = self.setting.get_rect(center=setting_rect)

        self.quit = font.render("Quit Game", 40, (150, 111, 95))
        self.quit_rect = self.quit.get_rect(center=(size[0] // 2,
                                                    size[1] - size[1] // 6))

    def render(self):
        screen.blit(self.wallpaper, (0, 0))
        screen.blit(self.start, self.start_rect)
        screen.blit(self.setting, self.setting_rect)
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
        elif self.setting_rect.collidepoint(pos):
            return "setting"
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


class Dungeon:

    def __init__(self):
        global screen, render_position

        pygame.init()
        screen = pygame.display.set_mode((width_screen, height_screen),
                                         pygame.FULLSCREEN)
        pygame.display.set_caption("Подземелье")
        render_position = "game"
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
                break
        pygame.quit()

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
                        running = False
                        self.running = False
            if render_position != "menu":
                running = False
            self.clock.tick(10)
            pygame.display.flip()

    def game(self):
        global motion_vector, last_motion_vector, motion

        motion_vector = "down"
        last_motion_vector = "down"
        motion = False
        running = True
        player = Create_Player()
        room_list = ["start_room", "monster_room", "chest_room", "boos_room"]
        dict_room = {"start_room": (8, 8), "chest_room": (8, 8),
                     "monster_room": (width_screen // 80 - 1, height_screen // 80 - 1),
                     "boss_room": (width_screen // 80 - 1, height_screen // 80 - 1)}

        self.font = pygame.font.Font("data/acrade.ttf", height_screen // 20)

        for name_room in room_list[1:]:
            name_room = "monster_room"
            Create_Dungeon(name_room)
            if name_room == "monster_room":
                Create_Mob("black_wolf", 1, dict_room[name_room])
            player.update()
            while running:
                self.health_text = self.font.render(f"HP: {player.health}/100",
                                                    40, (0, 0, 0))
                self.health_rect = self.health_text.get_rect()
                screen.fill((81, 64, 71))
                all_sprites.draw(screen)
                screen.blit(self.health_text, self.health_rect)
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
                            running = False
                            self.running = False
                    if event.type == pygame.KEYUP:
                        motion = False
                if render_position != "game":
                    running = False
                if player.health > 0:
                    player.draw()
                    player.update()
                mobs.update()
                self.clock.tick(10)
                pygame.display.flip()


if __name__ == '__main__':
    Dungeon()
