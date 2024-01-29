import pygame.sprite
import pygame
import random, time, sys
import pygame_widgets
from pygame_widgets.slider import Slider
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import numpy as np
from perlin_noise import PerlinNoise
from pygame.surfarray import make_surface
# screen
pygame.init()
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
pygame.display.flip()
all_sprites_list = pygame.sprite.Group()
# color
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GRAY = (128,128,128)
DARK_GRAY = (169,169,169)
LIME = (0,255,0)
# ground Segment
class Segment:
    def __init__(self, x, y, width, height, active_color, inactive_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.clicked = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.color = self.active_color
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True
                    self.color = self.active_color
        else:
            self.color = self.inactive_color

    def reset(self):
        self.clicked = False
        self.color = self.inactive_color
# ground
class Ground:
    def __init__(self, screen_width, screen_height, cell_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // cell_size
        self.height = screen_height // cell_size
        self.segmentList = []
        self.ground_data = self.generate_ground()
        self.Build()

    def generate_ground(self, clicked_x=None, clicked_y=None):
        returnList = []
        freq = random.uniform(5, 30)
        amp = random.uniform(1, 15)
        octaves = random.randint(1, 6)
        seed = random.randint(1, 100)
        noise = PerlinNoise(octaves=octaves, seed=seed)
        water_threshold = random.uniform(0.2, 0.5)

        for i in range(self.width):
            for ii in range(self.height):
                cell_x = i / self.width
                cell_y = ii / self.height
                cell_height = noise([cell_x / freq, cell_y / freq]) * amp
                brightness = (cell_height + amp) / (2 * amp)
                # Adjust color based on height and add some randomness
                color_value = int(brightness * 255) + random.randint(-10, 10)
                color_value = max(0, min(255, color_value))
                if cell_height < water_threshold:
                    color = (0, 0, color_value)
                else:
                    # Variation in color based on height
                    color = (color_value, color_value - 50, color_value - 100)
                returnList.append([(cell_x, cell_y), cell_height, color])
        return returnList

    def regenerate_map(self, clicked_segment = None):
        self.segmentList = []
        if clicked_segment != None:
            clicked_x = clicked_segment.x // self.screen_width
            clicked_y = clicked_segment.y // self.screen_height
        self.ground_data = self.generate_ground()
        self.Build()

    def Build(self):
        for item in self.ground_data:
            cell_x, cell_y = item[0]
            cell_height = item[1]
            color = item[2]
            self.segment = Segment(cell_x * self.screen_width,cell_y * self.screen_height,50,50,LIME,color)
            self.segmentList.append(self.segment)

    def draw(self,screen):
        for item in self.segmentList:
            item.draw(screen)
    
    def handle_event(self, event):
        global showFull_map
        for item in self.segmentList:
            item.handle_event(event)
            if item.clicked:
                showFull_map = False
                self.regenerate_map(item)
                item.reset()
terrain_generator = Ground(screenWidth, screenHeight, 50)
# loop
showFull_map = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                terrain_generator.regenerate_map()
        terrain_generator.handle_event(event)
    screen.fill(WHITE)
    if showFull_map:
        terrain_generator.draw(screen)
    pygame.display.flip()
    pygame.display.update()
    clock.tick(64)
