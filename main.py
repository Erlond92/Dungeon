import pygame

 
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 30
        self.board_list = list()
        for i in range(self.height):
            l = list()
            for j in range(self.width):
                l.append(0)
            self.board_list.append(l)

 
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
 
    def render(self, surface,):
        wcolor = pygame.Color("white")
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface, wcolor, (self.left + self.cell_size * j, self.top + self.cell_size * i,
                                                   self.cell_size, self.cell_size), 1 if self.board[i][j] == 0 else 0)
        
 
    def get_click(self, mouse_pos):
        cell_coords = self.get_cell(mouse_pos)
        if cell_coords is None:
            return
 
        self.on_click(cell_coords)
 
    def get_cell(self, mouse_pos):
        board_width = self.width * self.cell_size
        board_height = self.height * self.cell_size
        if self.left < mouse_pos[0] < self.left + board_width:
            if self.top < mouse_pos[1] < self.top + board_height:
                cell_coords = (mouse_pos[1] - self.left) // self.cell_size,\
                              (mouse_pos[0] - self.top) // self.cell_size
                return cell_coords
        return None
 
    def on_click(self, cell_coords):
        x = cell_coords[0] - self.left
        y = cell_coords[1] - self.top
        if (x < self.cell_size * self.width and x > 0) and (y < self.cell_size * self.height and y > 0):
            i = x // self.cell_size
            j = y // self.cell_size
            return (i, j)
        else:
            return None

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Подземелье")
    board = Board(10, 10)
    board.set_view(50, 50, 55)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                print(board.on_click(event.pos))
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()
    pygame.quit()
