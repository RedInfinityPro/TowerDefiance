# pygame
import pygame
import pygame_widgets
import pygame.sprite
from pygame import mixer
from pygame.surfarray import make_surface
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
# ---------------
import numpy as np
import random, time, sys
from perlin_noise import PerlinNoise
from pathfinding.core.node import Node
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import time
# screen
pygame.init()
mixer.init()
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
pygame.display.flip()
all_sprites_list = pygame.sprite.Group()
# color
def RANDOM_COLOR():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GRAY = (128,128,128)
DARK_GRAY = (169,169,169)
LIME = (0,255,0)
# grid
class MainGrid:
    def __init__(self, cell_size=50):
        self.cell_size = cell_size
        self.cell_size = cell_size
        self.grid_offset = [0, 0]

    def draw(self, screen):
        start_x = int((-self.grid_offset[0] / self.cell_size) - 1)
        end_x = int((screen.get_width() - self.grid_offset[0]) / self.cell_size) + 1
        start_y = int((-self.grid_offset[1] / self.cell_size) - 1)
        end_y = int((screen.get_height() - self.grid_offset[1]) / self.cell_size) + 1
        # draw line
        for x in range(start_x, end_x):
            pygame.draw.line(screen, RED, (x * self.cell_size + self.grid_offset[0], 0),
                             (x * self.cell_size + self.grid_offset[0], screen.get_height()))
        for y in range(start_y, end_y):
            pygame.draw.line(screen, RED, (0, y * self.cell_size + self.grid_offset[1]),
                             (screen.get_width(), y * self.cell_size + self.grid_offset[1]))
grid = MainGrid(cell_size=50)
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
        self.build()

    def generate_ground(self):
        returnList = []
        freq = random.uniform(5, 30)
        amp = random.uniform(1, 15)
        octaves = random.randint(1, 6)
        seed = random.randint(1, 100)
        noise = PerlinNoise(octaves=octaves, seed=seed)
        water_threshold = random.triangular(0.0, 0.2, 0.5) # user 0.2 - 0.5 if you want realisum

        for i in range(self.width):
            for ii in range(self.height):
                cell_x = i / self.width
                cell_y = ii / self.height
                cell_height = noise([cell_x / freq, cell_y / freq]) * amp
                brightness = (cell_height + amp) / (2 * amp)
                brightness = max(0, min(1, brightness))
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

    def regenerate_map(self):
        self.segmentList = []
        self.ground_data = self.generate_ground()
        self.build()

    def build(self):
        for item in self.ground_data:
            cell_x, cell_y = item[0]
            cell_height = item[1]
            color = item[2]
            segment_width = self.screen_width // self.width
            segment_height = self.screen_height // self.height

            self.segment = Segment(cell_x * self.screen_width, cell_y * self.screen_height, segment_width, segment_height, LIME, color)
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
                self.regenerate_map()
                item.reset()
terrain_generator = Ground(screenWidth, screenHeight, 50)
# path
class Path:
    def __init__(self, width, height):
        self.matrixWidth = width
        self.matrixHeight = height
        self.matrix = []
        self.color = DARK_GRAY
        self.path_rects = []
        self.grid = None
        self.start = None
        self.end = None
        self.finder = None
        self.path = None
        self.path_coordinates = []
        self.colliders = []

    def buildMatrix(self):
        self.matrix = [[1] * self.matrixWidth for _ in range(self.matrixHeight)]

    def makePath(self):
        self.buildMatrix()
        self.grid = Grid(matrix=self.matrix)
        self.start = self.grid.node(random.randint(0, self.matrixWidth - 1), 0)
        end_y = 13
        while True:
            end_x = random.randint(0, self.matrixWidth - 1)
            if (end_x, end_y) != (self.start.x, self.start.y):
                self.end = self.grid.node(end_x, end_y)
                break

        self.finder = AStarFinder()
        self.path, self.runs = self.finder.find_path(self.start, self.end, self.grid)
        self.path_coordinates = [(node.x, node.y) for node in self.path]
        self.colliders = [pygame.Rect(x * 50, y * 50, 50, 50) for x, y in self.path_coordinates]

    def regeneratePath(self):
        self.makePath()

    def check_collision(self, player_rect):
        # Check collision with player_rect
        for collider in self.colliders:
            if collider.colliderect(player_rect):
                return True
        return False

    def draw(self, screen):
        for x, y in self.path_coordinates:
            pygame.draw.rect(screen, self.color, (x * 50, y * 50, 50, 50))
# ememies
ememies_list = pygame.sprite.Group()
class Enemies(pygame.sprite.Sprite):
    def __init__(self,x,y,radius, path_coordinates):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = RANDOM_COLOR()
        self.path_coordinates = path_coordinates
        self.index = 0
        self.origionalSpeed = random.uniform(1,2)
        self.speed_factor = 1
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        for x, y in self.path_coordinates:
            x, y = self.path_coordinates[self.index]
            x *= (52)
            y *= (50)
            if self.rect.x > x:
                self.rect.x -= int(1 * self.speed_factor)
            elif self.rect.x < x:
                self.rect.x += int(1 * self.speed_factor)

            if self.rect.y > y:
                self.rect.y -= int(1 * self.speed_factor)
            elif self.rect.y < y:
                self.rect.y += int(1 * self.speed_factor)

            threshold = 1
            if abs(self.rect.x - x) <= threshold and abs(self.rect.y - y) <= threshold:
                self.index += 1
                if self.index >= len(self.path_coordinates):
                    self.index = 0
                    ememies_list.remove(self)
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
# button
class Button:
    def __init__(self, x, y, width, height, text, active_color, inactive_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.font_size = min(self.width // len(self.text) + 10, self.height)
        self.font = pygame.font.Font(None, self.font_size)
        self.clicked = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)
    
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
# settings Buttons
class SettingButton:
    def __init__(self, x, y, width, height, image_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image_path = image_path
        self.load_image()
        self.clicked = False

    def load_image(self):
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_image(self, new_image_path):
        self.image_path = new_image_path
        self.load_image()

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.clicked = True

    def reset(self):
        self.clicked = False
# start menu
class Main_Menu():
    def __init__(self, width, height, position=(0, 0)):
        self.width = width
        self.height = height
        self.x, self.y = position[0], position[1]
        self.visible = True
        self.title = "Menu"
        self.titleText = Text(self.title, 100, BLACK, ((screenWidth / 2) - (len(self.title) * 25),36))
        self.play = Button()
    
    def draw(self, screen):
        if self.visible:
            self.titleText.render(screen)
menuWindow = Main_Menu(screenHeight, screenWidth, (0, 0))
# map details
paths = []
def AddPath():
    for _ in range(random.randint(1,3)):
        path = Path(screenWidth // 50, screenHeight // 50)
        path.makePath()
        paths.append(path)
AddPath()

enemies_timer = 0
def spawn_enemies(amount):
    global enemies_timer
    enemies_timer += 1
    spawn_interval = 100
    if enemies_timer % spawn_interval == 0:
        for i in range(random.randint(0, amount)):
            path_index = random.randint(0, len(paths) - 1)
            path = paths[path_index]
            start_x, start_y = path.path_coordinates[0]
            ememy = Enemies(start_x * 50, start_y * 50 - (i * random.randint(10, 50)), 10, path.path_coordinates)
            ememies_list.add(ememy)

time = 0
def TransitionMaps():
    global time, ememies_list, paths
    time += 1
    if time % 500 == 0:
        ememies_list = pygame.sprite.Group()
        terrain_generator.regenerate_map()
        paths = []
        AddPath()

# loop
running = True
frameRate = 64
Background_volume = 1.0
soundEffect_volume = 1.0
HomeScreen = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
    screen.fill(WHITE)
    # map
    terrain_generator.draw(screen)
    for path in paths:
        path.draw(screen)

    if HomeScreen:
        TransitionMaps()
        spawn_enemies(100)
        ememies_list.draw(screen)
        for ememie in ememies_list:
            ememie.move()
    # windows
    menuWindow.draw(screen)
    # update
    pygame.display.flip()
    pygame.display.update()
    clock.tick(64)
