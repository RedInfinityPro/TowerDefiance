import pygame.sprite
import pygame
import random, time, sys
import pygame_widgets
from pygame_widgets.slider import Slider
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import numpy as np
from perlin_noise import PerlinNoise
# screen
pygame.init()
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
pygame.display.flip()
all_sprites_list = pygame.sprite.Group()
# colors
def RANDOM_COLOR():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GRAY = (128,128,128)
DARK_GRAY = (169,169,169)
LIGHT_BLUE = (173,216,230)
CRIMSON = (220,20,60)
FIRE_BRICK = (178,34,34)
# ground
class Ground:
    def __init__(self, screen_width, screen_height, cell_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // cell_size
        self.height = screen_height // cell_size
        self.ground_data = self.ground()
    
    def ground(self):
        returnList = []
        freq = random.uniform(10, 30)
        amp = random.uniform(2, 10)
        octaves = random.randint(1, 4)
        seed = random.randint(1, 100)
        noise = PerlinNoise(octaves=octaves, seed=seed)
        for i in range(self.width):
            for ii in range(self.height):
                cell_x = i / self.width
                cell_y = ii / self.height
                cell_height = noise([cell_x / freq, cell_y / freq]) * amp
                brightness = (cell_height + amp) / (2 * amp)  # Value between 0 and 1
                color_value = int(brightness * 255)
                color = (color_value, color_value, color_value)
                returnList.append([(cell_x, cell_y), cell_height, color])
        return returnList
    
    def draw(self, screen):
        for item in self.ground_data:
            cell_x, cell_y = item[0]
            cell_height = item[1]
            color = item[2]
            pygame.draw.rect(screen, color, (cell_x * self.screen_width, cell_y * self.screen_height, self.cell_size, self.cell_size))

terrain_generator = Ground(screenWidth, screenHeight, 50)
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
            pygame.draw.line(screen, BLACK, (x * self.cell_size + self.grid_offset[0], 0),
                             (x * self.cell_size + self.grid_offset[0], screen.get_height()))
        for y in range(start_y, end_y):
            pygame.draw.line(screen, BLACK, (0, y * self.cell_size + self.grid_offset[1]),
                             (screen.get_width(), y * self.cell_size + self.grid_offset[1]))
grid = MainGrid(cell_size=50)
# ememies
ememies_list = pygame.sprite.Group()
class Ememies(pygame.sprite.Sprite):
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
# build Road
class Path:
    def __init__(self, width, height):
        self.matrixWidth = width
        self.matrixHeight = height
        self.matrix = []
        self.color = DARK_GRAY

    def buildMatrix(self):
        for i in range(self.matrixHeight):
            row = [1] * self.matrixWidth
            self.matrix.append(row)
    
    def makePath(self):
        self.buildMatrix()
        self.grid = Grid(matrix=self.matrix)
        self.start = self.grid.node(random.randint(0,self.matrixWidth - 1), 0)
        self.end = self.grid.node(random.randint(0,self.matrixWidth - 1),13)
        self.finder = AStarFinder()
        self.path, self.runs = self.finder.find_path(self.start, self.end, self.grid)
        self.path_coordinates = [(node.x, node.y) for node in self.path]
    
    def draw(self, screen):
        for x, y in self.path_coordinates:
            pygame.draw.rect(screen, self.color, (x * 50, y * 50, 50, 50))
path = Path(screenWidth // 50, screenHeight // 50)
path.makePath()
# button
class Button:
    def __init__(self, x, y, width, height, text, active_color, inactive_color, image_path=None):
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

        if image_path is not None:
            self.image_path = image_path
            self.load_image()
        else:
            self.image = None
    
    def load_image(self):
        if self.image_path is not None:
            self.image = pygame.image.load(self.image_path)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x, self.y))
        else:
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

    def update_image(self, new_image_path):
        self.image_path = new_image_path
        self.load_image()
freeSpots = []
for item in range(12):
    builSpot = Button(0,0,50,50,"X",FIRE_BRICK,CRIMSON)
    freeSpots.append(builSpot)
settings = Button(screenWidth - 50, screenHeight - 50, 50, 50,"Settings",WHITE,WHITE,"gear.png")
eye = Button(screenWidth - 50,screenHeight - 100,50,50,"Show",WHITE,WHITE,image_path = "hidden.png")
buildSettings = Button(screenWidth - 50, screenHeight - 150, 50, 50,"Tools",WHITE,WHITE,"maintenance.png")
# Drag Button
class DragButton:
    def __init__(self, x, y, width, height, active_color, inactive_color, cell_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_dragging = False
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.cell_size = cell_size
        self.placed = True
        self.upgrade = False
        self.upgrade_timer_max = random.randint(1000,9000)
        self.upgrade_timer = 0
        self.upgrade_animation_speed = 2
        self.upgrade_animation_range = 20
        self.upgrade_offset = 0
        self.upgrade_direction = 1
        self.showUpgrade = Button(self.x + 15, self.y - self.width, 25, 25, "Upgrade", WHITE,WHITE,"arrow-up.png")

    def countDown(self):
        if not(self.upgrade) and self.placed:
            if self.upgrade_timer < self.upgrade_timer_max:
                self.upgrade_timer += 1
                self.upgrade = False
            else:
                self.upgrade_timer = 0
                self.upgrade = True
        if not(self.placed):
            self.upgrade_timer = 0
            self.upgrade = False

    def update_upgrade_animation(self):
        if self.upgrade:
            self.upgrade_offset += self.upgrade_direction * self.upgrade_animation_speed
            if abs(self.upgrade_offset) >= self.upgrade_animation_range:
                self.upgrade_direction *= -1 

    def draw(self, screen):
        self.countDown()
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.upgrade:
            self.update_upgrade_animation()
            self.showUpgrade.y = self.y - self.width + self.upgrade_offset
            self.showUpgrade.draw(screen)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        screen_width, screen_height = pygame.display.get_surface().get_size()

        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.color = self.active_color
            if event.type == pygame.MOUSEBUTTONDOWN and not(self.placed):
                self.is_dragging = True
                self.offset_x = mouse_pos[0] - self.x
                self.offset_y = mouse_pos[1] - self.y
        elif event.type == pygame.MOUSEBUTTONUP and self.is_dragging and not(self.placed):
            self.reset()
        elif event.type == pygame.MOUSEMOTION and self.is_dragging and not(self.placed):
            new_x = (mouse_pos[0] - self.offset_x + grid.grid_offset[0]) // self.cell_size * self.cell_size
            new_y = (mouse_pos[1] - self.offset_y + grid.grid_offset[1]) // self.cell_size * self.cell_size
            # Check if the new position is within the screen boundaries
            if 0 <= new_x <= screen_width - self.width and 0 <= new_y <= screen_height - self.height:
                self.x = new_x
                self.y = new_y
        else:
            self.reset()
        # upgrade
        if event.type == pygame.MOUSEBUTTONDOWN and self.upgrade:
            self.upgrade = False
        
        if self.upgrade:
            self.showUpgrade.handle_event(event)
            if self.showUpgrade.clicked:
                self.upgrade = False

    def snap_to_grid(self):
        self.x = round((self.x - grid.grid_offset[0]) / self.cell_size) * self.cell_size + grid.grid_offset[0]
        self.y = round((self.y - grid.grid_offset[1]) / self.cell_size) * self.cell_size + grid.grid_offset[1]
        self.showUpgrade.x, self.showUpgrade.y = self.x + 15, self.y

    def reset(self):
        self.is_dragging = False
        self.color = self.inactive_color
        self.snap_to_grid()
building = DragButton(300,300,50,50,BLUE,LIGHT_BLUE,grid.cell_size)
# spon timer
timer = 0
def Spon(amount):
    global timer
    timer += 1
    spawn_interval = 100
    x,y = path.path_coordinates[0]
    if (timer % spawn_interval == 0):
        for i in range(random.randint(0,amount)):
            ememie = Ememies(x * 50,y * 50 - (i * random.randint(10,50)),10,path.path_coordinates)
            ememies_list.add(ememie)

# loop
showSettings = False
can_build = False
show_grid = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        building.handle_event(event)
        if event.type == pygame.MOUSEBUTTONUP:
            building.reset()
        # build spot
        for freeSpot in freeSpots:
            freeSpot.handle_event(event)
            if freeSpot.clicked:
                freeSpot.reset()
        # eye
        eye.handle_event(event)
        if eye.clicked:
            show_grid = not(show_grid)
            if show_grid:
                eye.update_image("hidden.png")
            else:
                eye.update_image("view.png")
            eye.reset()
        # build
        buildSettings.handle_event(event)
        if buildSettings.clicked:
            can_build = not(can_build)
            if can_build:
                buildSettings.update_image("tools.png")
            else:
                buildSettings.update_image("maintenance.png")
            building.placed = True
            buildSettings.reset()
        # settings
        settings.handle_event(event)
        if settings.clicked:
            showSettings = not(showSettings)
            if showSettings:
                settings.update_image("gear(1).png")
            else:
                settings.update_image("gear.png")
                for ememie in ememies_list:
                    ememie.speed_factor = ememie.origionalSpeed
            settings.reset()
    # screen
    screen.fill(WHITE)
    terrain_generator.draw(screen)
    path.draw(screen)
    building.draw(screen)
    #ememies
    if showSettings == False:
        Spon(100)
        for ememie in ememies_list:
            ememie.speed_factor = ememie.origionalSpeed
    else:
        for ememie in ememies_list:
            ememie.speed_factor = 0
    ememies_list.draw(screen)
    for ememie in ememies_list:
        ememie.move()
    # can build
    if can_build:
        building.placed = False
        # free spots
        for freeSpot in freeSpots:
            freeSpot.draw(screen)

        for i in range(3):
            freeSpots[i].x = building.x - 50
            freeSpots[i].y = building.y - 50 + (i * 50)

        for i in range(3, 6):
            freeSpots[i].x = building.x + 50
            freeSpots[i].y = building.y - 50 + ((i - 3) * 50)

        for i in range(6, 9):
            freeSpots[i].x = building.x - 50 + (i - 6) * 50
            freeSpots[i].y = building.y + 50
        
        for i in range(9, 12):
            freeSpots[i].x = building.x - 50 + (i - 9) * 50
            freeSpots[i].y = building.y - 50
    # update
    if show_grid:
        grid.draw(screen)
    eye.draw(screen)
    buildSettings.draw(screen)
    settings.draw(screen)
    pygame.display.update()
    clock.tick(64)
