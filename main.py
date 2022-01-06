import pygame
import random
import os
import sys
import numpy as np
from win32api import GetSystemMetrics
from PIL import Image


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
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if motion:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        return self.frames[self.cur_frame]


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
                cell_coords = mouse_pos[1] // self.cell_size, \
                              mouse_pos[0] // self.cell_size
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


class Mob(pygame.sprite.Sprite):

    def __init__(self, name_mob, size, mob_group):
        super().__init__(mob_group)
        self.name_mob = name_mob
        self.mob = AnimatedSprite(load_image(f"mob/{name_mob}/down.png"), 4, 1, 64, 64)
        self.mob_x_in_board = random.randrange(1, size)
        self.mob_y_in_board = random.randrange(1, size)
        self.speed = 5

    def render(self):
        self.motion()
        screen.blit(self.mob.update(), (self.mob_x_in_board, self.mob_y_in_board))

    def motion(self):
        try:
            a = np.arctan((player_x - self.mob_x_in_board) /
                          (player_y - self.mob_y_in_board))
        except ZeroDivisionError:
            a = np.arctan(0)
        self.mob_x_in_board += int(np.sin(a) * self.speed)
        self.mob_y_in_board += int(np.cos(a) * self.speed)

        if self.mob_x_in_board > S * 80 - 80:
            self.mob_x_in_board = S * 80 - 80
        elif self.mob_x_in_board < 20:
            self.mob_x_in_board = 20

        if self.mob_y_in_board > S * 80 - 100:
            self.mob_y_in_board = S * 80 - 100
        elif self.mob_y_in_board < 20:
            self.mob_y_in_board = 20


class Create_Mob:

    def __init__(self, name_mob, n, size_room, group):
        group = pygame.sprite.Group()
        for _ in range(n):
            Mob(name_mob, size_room, group)
        group.draw(screen)
        group.render()



class Create_Players:

    def __init__(self):
        self.player = AnimatedSprite(load_image(f"hero_ani/{motion_vector}.png"), 4, 1, 64, 64)

    def render(self):
        global last_motion_vector, player_y, player_x

        if last_motion_vector != motion_vector:
            self.player = AnimatedSprite(load_image(f"hero_ani/{motion_vector}.png"), 4, 1, 64, 64)

        speed = 10
        run_speed = 20

        if motion:
            if motion_vector == "up":
                player_y -= speed
            elif motion_vector == "down":
                player_y += speed
            elif motion_vector == "right":
                player_x += speed
            elif motion_vector == "left":
                player_x -= speed

            if player_x > S * 80 - 80:
                player_x = S * 80 - 80
            elif player_x < 20:
                player_x = 20

            if player_y > S * 80 - 100:
                player_y = S * 80 - 100
            elif player_y < 20:
                player_y = 20

        screen.blit(self.player.update(), (player_x, player_y))
        last_motion_vector = motion_vector


class Create_Dungeon(Board):

    def __init__(self):
        self.dict_room = {"start_room": 4, "monster_room": 10,
                          "chest_room": 4, "boss_room": 10}
        self.create_list_floor_in_room()

    def create_list_floor_in_room(self):
        self.dict_floor_in_room = dict()
        for name_room in self.dict_room.keys():
            list_room = list()
            s = self.dict_room[name_room]
            for i in range(s):
                a = list()
                for j in range(s):
                    if i == 0 and j == 0:
                        a.append("floor/floor_side_1.png")
                    elif i == 0 and j == s- 1:
                        a.append("floor/floor_side_2.png")
                    elif i == s - 1 and j == s - 1:
                        a.append("floor/floor_side_3.png")
                    elif i == s - 1 and j == 0:
                        a.append("floor/floor_side_4.png")
                    elif i == 0:
                        a.append("floor/floor_side_left.png")
                    elif j == s - 1:
                        a.append("floor/floor_side_bottom.png")
                    elif i == s - 1:
                        a.append("floor/floor_side_right.png")
                    elif j == 0:
                        a.append("floor/floor_side_top.png")
                    elif i == 1 and j == 1:
                        a.append("floor/floor_1.png")
                    elif i == 1 and j == s - 2:
                        a.append("floor/floor_2.png")
                    elif i == s - 2 and j == s - 2:
                        a.append("floor/floor_3.png")
                    elif i == s - 2 and j == 1:
                        a.append("floor/floor_4.png")
                    elif i == 1:
                        a.append("floor/floor_left.png")
                    elif j == s - 2:
                        a.append("floor/floor_bottom.png")
                    elif i == s - 2:
                        a.append("floor/floor_right.png")
                    elif j == 1:
                        a.append("floor/floor_top.png")
                    else:
                        a.append("floor/floor.png")
                list_room.append(a)
            self.dict_floor_in_room[name_room] = list_room.copy()

    def render(self, name_room):
        global S
        S = self.dict_room[name_room]
        for i in range(S):
            for j in range(S):
                image = load_image(self.dict_floor_in_room[name_room][i][j])
                screen.blit(image, (i * 80, j * 80))


class Menu:

    def __init__(self, size):
        resize_image("data/start_menu.jpeg", size)
        self.wallpaper = load_image("start_menu.jpeg")

        name_font = pygame.font.Font("data/acrade.ttf", size[1] // 4)
        self.name = name_font.render("Dungeon", 40, (150, 111, 95))
        self.name_rect = self.name.get_rect(center=(size[0] // 2, size[1] // 3))

        font = pygame.font.Font("data/acrade.ttf", size[1] // 6)
        self.start = font.render("Start Game", 40, (150, 111, 95))
        self.start_rect = self.start.get_rect(center=(size[0] // 2, size[1] // 2))

        self.setting = font.render("Setting", 40, (150, 111, 95))
        self.setting_rect = self.setting.get_rect(center=(size[0] // 2,
                                                size[1] // 2 + size[1] // 6))

        self.quit = font.render("Quit Game", 40, (150, 111, 95))
        self.quit_rect = self.quit.get_rect(center=(size[0] // 2,
                                                    size[1] - size[1] // 6))

    def render(self):
        screen.blit(self.wallpaper, (0 , 0))
        screen.blit(self.start, self.start_rect)
        screen.blit(self.setting, self.setting_rect)
        screen.blit(self.name, self.name_rect)
        screen.blit(self.quit, self.quit_rect)

    def get_click(self, mouse_pos):
        pos = self.get_cell(mouse_pos)
        if pos == None:
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
            return None

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
        global screen, all_sprites, render_position, width_screen, height_screen

        pygame.init()

        width_screen = GetSystemMetrics(0)
        height_screen = GetSystemMetrics(1)
        screen = pygame.display.set_mode((width_screen, height_screen),
                                         pygame.FULLSCREEN)
        pygame.display.set_caption("Подземелье")
        all_sprites = pygame.sprite.Group()
        render_position = "menu"
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
        global player_x, player_y, motion_vector, last_motion_vector, motion

        motion_vector = "down"
        last_motion_vector = "down"
        motion = False
        player_x = 80
        player_y = 80
        running = True

        self.dungeon = Create_Dungeon()
        self.player = Create_Players()

        while running:
            screen.fill((150, 111, 95))
            self.dungeon.render("boss_room")
            self.player.render()
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
            self.clock.tick(10)
            pygame.display.flip()


if __name__ == '__main__':
    Dungeon()
