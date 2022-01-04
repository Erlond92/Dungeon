import pygame, random, os, sys


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
                pygame.draw.rect(surface, wcolor, (self.cell_size * j, self.cell_size * i,
                                                   self.cell_size, self.cell_size), 1 if self.board[i][j] == 0 else 0)

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
        if (x < self.cell_size * self.width and x > 0) and (y < self.cell_size * self.height and y > 0):
            i = x // self.cell_size
            j = y // self.cell_size
            return (i, j)
        else:
            return None


class Create_Players:

    def __init__(self):
        self.player = AnimatedSprite(load_image(f"hero_ani/{motion_vector}.png"), 4, 1, 64, 64)

    def render_player(self):
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

            if player_x > size * 80 - 80:
                player_x = size * 80 - 80
            elif player_x < 20:
                player_x = 20

            if player_y > size * 80 - 100:
                player_y = size * 80 - 100
            elif player_y < 20:
                player_y = 20

        screen.blit(self.player.update(), (player_x, player_y))
        last_motion_vector = motion_vector


class Create_Dungeon:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.list_room = ["start_room", "monster_room", "chest_room", "boss_room", "end_room"]
        self.create_list_floor_in_room()

    def create_list_floor_in_room(self):
        self.dict_floor_in_room = dict()
        for name_room in self.list_room:
            list_room = list()
            for i in range(self.height):
                a = list()
                for j in range(self.width):
                    if i == 0 and j == 0:
                        a.append("floor/floor_side_1.png")
                    elif i == 0 and j == self.width - 1:
                        a.append("floor/floor_side_2.png")
                    elif i == self.height - 1 and j == self.width - 1:
                        a.append("floor/floor_side_3.png")
                    elif i == self.height - 1 and j == 0:
                        a.append("floor/floor_side_4.png")
                    elif i == 0:
                        a.append("floor/floor_left.png")
                    elif j == self.width - 1:
                        a.append("floor/floor_bottom.png")
                    elif i == self.height - 1:
                        a.append("floor/floor_right.png")
                    elif j == 0:
                        a.append("floor/floor_top.png")
                    else:
                        a.append("floor/floor.png")
                list_room.append(a)
            self.dict_floor_in_room[name_room] = list_room.copy()

    def render_room(self, name_room):
        for i in range(len(self.dict_floor_in_room[name_room])):
            for j in range(len(self.dict_floor_in_room[name_room][i])):
                image = load_image(self.dict_floor_in_room[name_room][i][j])
                screen.blit(image, (i * 80, j * 80))


class Dungeon:

    def __init__(self):
        global motion, motion_vector, last_motion_vector, screen, all_sprites, player_room, player_x, player_y, size

        pygame.init()

        running = True
        motion = False
        clock = pygame.time.Clock()
        size = 10
        motion_vector = "down"
        last_motion_vector = "down"
        screen = pygame.display.set_mode((size * 80, size * 80))
        pygame.display.set_caption("Подземелье")
        all_sprites = pygame.sprite.Group()
        dungeon = Create_Dungeon(size, size)

        player_room = "start_room"
        player_x = 20
        player_y = 20

        player = Create_Players()

        while running:
            for event in pygame.event.get():
                dungeon.render_room("start_room")
                player.render_player()
                if event.type == pygame.QUIT:
                    running = False
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

                if event.type == pygame.KEYUP:
                    motion = False
            clock.tick(15)
            pygame.display.flip()
        pygame.quit()

    def menu(self):
        pass

    def start_game(self):
        self.player_coordinates = ["start_box", [5, 5]]
        self.dungeon = Create_Dungeon(11, 11)


if __name__ == '__main__':
    Dungeon()
