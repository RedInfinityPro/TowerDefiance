import pygame.sprite
import pygame
import random, time, sys
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame import mixer
import numpy as np
import noise
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
mixer.init()
pygame.init()
# pygame screen
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
pygame.display.set_caption("The Red Map")
# colors
TextColor = (0, 0, 0)
BLACK = (0,0,0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0,0,255)
WHITE = (255, 255, 255)
# background
clock = pygame.time.Clock()
background_colour = WHITE
screen.fill(background_colour)
pygame.display.flip()
# text
class Text:
    def __init__(self, text, font_size, color, position):
        self.text = text
        self.font_size = font_size
        self.color = color
        self.position = position
        self.font = pygame.font.Font(None, self.font_size)  # You can specify a font file or use None for default font
        self.rendered_text = None
    def update(self, new_text):
        self.text = new_text
        self.rendered_text = None  # Clear the rendered text to update it
    def render(self, screen):
        if self.rendered_text is None:
            self.rendered_text = self.font.render(self.text, True, self.color)
        screen.blit(self.rendered_text, self.position)
# map
map = pygame.sprite.Group()
class MapSegment(pygame.sprite.Sprite):
    def __init__(self, x, y, size, value):
        super().__init__()
        self.value = value
        self.default_color = self.calculate_color()
        self.hover_color = (0, 0, 0)
        self.image = pygame.Surface(size)
        self.image.fill(self.default_color)
        self.size = size
        self.rect = self.image.get_rect(topleft=(x, y))
    def calculate_color(self):
        brightness = int(255 * (1 - abs(self.value)))
        return pygame.Color(0, brightness, 0)
    def set_value(self, value):
        self.value = value
        self.image.fill(self.calculate_color())
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.image.fill(self.hover_color if self.rect.collidepoint(event.pos) else self.default_color)
# create map
class MapGenerator:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.matrix = []
        self.path_coordinates = []
    def randomize_values(self):
        self.octaves = random.randint(4, 6)
        self.persistence = random.uniform(0.3, 0.7)
        self.lacunarity = random.uniform(1.5, 2.5)
        self.scale = random.uniform(50, 200)
        self.zoom = random.uniform(0.5, 2.0)
    def generate_perlin_noise_map(self):
        world = np.zeros((self.map_height, self.map_width))
        for y in range(self.map_height):
            for x in range(self.map_width):
                x_coord = x / (self.scale * self.zoom)
                y_coord = y / (self.scale * self.zoom)
                perlin_value = noise.pnoise2(x_coord, y_coord, octaves=self.octaves, 
                                            persistence=self.persistence, lacunarity=self.lacunarity,
                                            repeatx=1024, repeaty=1024, base=0)
                world[y][x] = perlin_value
        world = 2 * (world - np.min(world)) / np.ptp(world) - 1
        return world
    def create_map(self, position):
        self.randomize_values()
        perlin_noise_map = self.generate_perlin_noise_map()
        for y in range(self.map_height):
            perlin_row = []
            for x in range(self.map_width):
                perlin_value = perlin_noise_map[y][x]
                map_segment = MapSegment(position[0] + (x * 10), position[1] + (y * 10), (10, 10), perlin_value)
                map.add(map_segment)
                all_sprites_list.add(map_segment)
                if perlin_value < 0:
                    perlin_row.append(0)
                else:
                    perlin_row.append(1)
            self.matrix.append(perlin_row)
    def create_path(self):
        try:
            grid = Grid(matrix=self.matrix)
            while True:
                start_x, start_y = random.randint(0, self.map_width - 1), random.randint(0, self.map_height - 1)
                end_x, end_y = random.randint(0, self.map_width - 1), random.randint(0, self.map_height - 1)
                start = grid.node(start_x, start_y)
                endpoint = grid.node(end_x, end_y)
                if [start != endpoint and self.matrix[start_x][start_y] != 0 and self.matrix[end_x][end_y] != 0]:
                    break
            finder = AStarFinder()
            path, runs = finder.find_path(start, endpoint, grid)
            self.path_coordinates.append([(node.x, node.y) for node in path])

            for node in path:
                x, y = node
                self.matrix[y][x] = 0
        except Exception as e:
            print(e)
# create path
def create_path(self, blue_path_coordinates):
    try:
        grid = Grid(matrix=self.matrix)
        while True:
            start_x, start_y = random.randint(0, self.map_width - 1), random.randint(0, self.map_height - 1)
            end_x, end_y = random.randint(0, self.map_width - 1), random.randint(0, self.map_height - 1)
            start = grid.node(start_x, start_y)
            endpoint = grid.node(end_x, end_y)
            if [start != endpoint and self.matrix[start_x][start_y] != 0 and self.matrix[end_x][end_y] != 0]:
                finder = AStarFinder()
                path, runs = finder.find_path(start, endpoint, grid)
                # Check for overlap with blue path
                overlap = False
                for node in path:
                    if (node.x, node.y) in blue_path_coordinates:
                        overlap = True
                        break
                if not overlap:
                    self.path_coordinates.append([(node.x, node.y) for node in path])
                    for node in path:
                        x, y = node
                        self.matrix[y][x] = 0
                    break
    except Exception as e:
        print(e)
all_sprites_list = pygame.sprite.Group()
# rivers
map_width, map_height = 75, 75
map_generator = MapGenerator(map_width, map_height)
map_generator.create_map((0, 0))
for _ in range(10):
    map_generator.create_path()
# path
additional_path_coordinates = []
for _ in range(10):
    map_generator.create_path()
    additional_path_coordinates.append(map_generator.path_coordinates[-1])
# loop
running = True
game_paused = False
# settings
frameRate = 64
Background_volume = 1.0
soundEffect_volume = 1.0
# game loop
def GameLoop():
    global running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            # map
            for mapSegment in map:
                mapSegment.handle_event(event)
                mapSegment.update()
        screen.fill(WHITE)
        for mapSegment in map:
            screen.blit(mapSegment.image, mapSegment.rect.topleft)
        # draw river
        for path_coords in map_generator.path_coordinates:
            try:
                for y, x in path_coords:
                    if 0 <= x < len(map_generator.matrix[0]) and 0 <= y < len(map_generator.matrix):
                        pygame.draw.rect(screen, BLUE, (x * 10, y * 10, 10, 10))
            except:
                pass
        # draw path
        for path_coords in additional_path_coordinates:
            try:
                for y, x in path_coords:
                    if 0 <= x < len(map_generator.matrix[0]) and 0 <= y < len(map_generator.matrix):
                        pygame.draw.rect(screen, RED, (x * 10, y * 10, 10, 10))
            except:
                pass
        # update
        pygame.display.update()
        clock.tick(frameRate)
GameLoop()
