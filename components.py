import pygame
import sys
import random
import colorsys

class Grid:
    def __init__(self, width, height, cell_size):
        self.rows = height // cell_size
        self.cols = width // cell_size
        self.cell_size = cell_size
        self.cells = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def draw(self, screen, default_color):
        for row in range(self.rows):
            for col in range(self.cols):
                particle = self.cells[row][col]
                color = default_color if self.cells[row][col] is None else particle.color
                pygame.draw.rect(screen, color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

    def add(self, row, col, type):
        if 0 <= row < self.rows and 0 <= col < self.cols and self.cells[row][col] == None:
            self.cells[row][col] = type()

    def erase(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col] = None

    def is_empty(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col] is None
        
    def set_cell(self, row, col, particle):
        if not(0 <= row < self.rows and 0 <= col < self.cols):
            return
        self.cells[row][col] = particle

    def get_cells(self, row, col):
        return self.cells[row][col] if (0 <= row < self.rows and 0 <= col < self.cols) else None


class Simulation:
    def __init__(self, width, height, cell_size):
        self.grid = Grid(width, height, cell_size)
        self.particle_type = SandParticle
        self.action = "create"
        self.cell_size = cell_size
        self.brush = 2

    def draw(self, screen, default_color = (150, 150, 150)):
        self.grid.draw(screen, default_color)
        self.cursor(screen)

    def add_particle(self, row, col, type):
        self.grid.add(row, col, type)
    
    def erase_particle(self, row, col):
        self.grid.erase(row, col)

    def update(self):
        for row in range(self.grid.rows, -1, -1):
            for col in range(self.grid.cols):
                particle = self.grid.get_cells(row, col)
                if particle is not None:
                    new_pos = particle.update(self.grid, row, col)
                    if new_pos != (row, col):
                        self.grid.set_cell(new_pos[0], new_pos[1], particle)
                        self.grid.erase(row, col)

    def reset(self):
        self.grid.cells = [[None for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.handle_keys(event)
        self.handle_mouse()

    def handle_keys(self, event):
        if event.key == pygame.K_SPACE:
            self.reset()
        elif event.key == pygame.K_s:
            self.particle_type = SandParticle
            self.brush = 2
        elif event.key == pygame.K_w:
            self.particle_type = Water
            self.brush = 2
        elif event.key == pygame.K_r:
            self.particle_type = Rock
            self.brush = 3
        elif event.key == pygame.K_c:
            self.action = "create"
        elif event.key == pygame.K_e:
            self.action = "erase"

    def handle_mouse(self):
        clicks = pygame.mouse.get_pressed()
        if clicks[0]:
            x, y = pygame.mouse.get_pos()
            row = y // self.cell_size
            col = x // self.cell_size
            self.brush_size(row, col)

    def brush_size(self, row, col):
        for r in range(self.brush):
            for c in range(self.brush):
                current_row = r + row
                current_col = c + col

                if self.action == "create":
                    self.add_particle(current_row, current_col, self.particle_type)
                elif self.action == "erase":
                    self.erase_particle(current_row, current_col)

    def cursor(self, screen):
        x, y = pygame.mouse.get_pos()
        row = y // self.cell_size
        col = x // self.cell_size

        br_size = self.brush * self.cell_size
        color = (0, 0, 0) 
        if self.action == "erase":
            color = (255, 255, 255)
        else:
            if self.particle_type == SandParticle:
                color = (180, 140, 60)
            elif self.particle_type == Water:
                color = (93, 151, 231)
            elif self.particle_type == Rock:
                color = (135, 135, 135)

        pygame.draw.rect(screen, color, (x, y, br_size, br_size))        


class Particle:
    def __init__(self):
        self.color = (255, 255, 255)

    def update(self, grid, row, col):
        return row, col


class SandParticle(Particle):
    def __init__(self):
        self.color = self.random_color()

    def random_color(self):
        hue = random.uniform(0.1, 0.12)
        saturation = random.uniform(0.5, 0.7)
        value = random.uniform(0.6, 0.9)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return int(r * 255), int(g * 255), int(b * 255)
    
    def update(self, grid, row, col):
        if grid.is_empty(row+1, col): 
            return row + 1, col 
        else: 
            offsets = [-1, 1]
            random.shuffle(offsets)
            for offset in offsets:
                new_col = col + offset
                if grid.is_empty(row+1, new_col):
                    return row+1, new_col
        return row, col
    
class Water(Particle):
    def __init__(self):
        colors = [(65, 107, 223),(93, 151, 231),(62, 164, 240),(0, 112, 255)]
        self.color = random.choice(colors)
    
    def update(self, grid, row, col):
        if grid.is_empty(row + 1, col): 
            return row + 1, col 
        else: 
            offsets = [-1, 1]
            random.shuffle(offsets)
            for offset in offsets:
                new_col = col + offset
                if grid.is_empty(row + 1, new_col):
                    return row + 1, new_col
            for offset in offsets:
                new_col = col + offset
                if grid.is_empty(row, new_col):
                    return row, new_col
        return row, col
    
class Rock(Particle):
    def __init__(self):
        colors = [(128, 128, 128),(146, 141, 133),(135, 135, 135)]
        self.color = random.choice(colors)
