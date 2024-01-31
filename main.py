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
# Map Manager
class MapManager:
    def __init__(self):
        self.main_map = None
        self.smaller_maps = {}

    def save_main_map(self, map_data):
        self.main_map = map_data

    def load_main_map(self):
        return self.main_map

    def save_smaller_map(self, key, map_data):
        self.smaller_maps[key] = map_data

    def load_smaller_map(self, key):
        if key in self.smaller_maps:
            return self.smaller_maps[key]
        else:
            print(f"Smaller map with key '{key}' not found.")
            return None

    def generate_and_save_main_map(self, screen_width, screen_height, cell_size):
        new_main_map = Ground(screen_width, screen_height, cell_size).ground_data
        self.save_main_map(new_main_map)

    def generate_and_save_smaller_map(self, key, screen_width, screen_height, cell_size):
        new_smaller_map = Ground(screen_width, screen_height, cell_size).ground_data
        self.save_smaller_map(key, new_smaller_map)
map_manager = MapManager()
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

    def get_ground_data(self):
        return self.ground_data

    def recreate_saved_map(self, saved_map):
        self.segmentList = []
        self.ground_data = saved_map
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
        self.color = GRAY
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
# wrap text
class WrapText:
    def __init__(self, text, font_size, color, position, max_width):
        self.text = text
        self.font_size = font_size
        self.max_width = max_width
        self.font = pygame.font.Font(None, self.font_size)
        self.lines = self.update()
        self.color = color
        self.position = position

    def update(self):
        words = self.text.split()
        lines = []
        current_line = []
        for word in words:
            # Check if adding the next word exceeds the max width
            if self.font.size(' '.join(current_line + [word]))[0] <= self.max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))
        return lines

    def render(self, screen):
        for i, line in enumerate(self.lines):
            text_surface = self.font.render(line, True, self.color)
            screen.blit(text_surface, (self.position[0], self.position[1] + i * self.font.get_linesize()))
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
        self.textColor = BLACK
        self.font_size = min(self.width // len(self.text) + 10, self.height)
        self.font = pygame.font.Font(None, self.font_size)
        self.clicked = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 2)
        text_surface = self.font.render(self.text, True, self.textColor)
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
    def __init__(self, width, height, position=(0, 0), background_image_path=None):
        self.width = width
        self.height = height
        self.x, self.y = position[0], position[1]
        self.visible = True
        self.showTutorial = False
        self.showSettings = False
        self.title = "Menu"
        self.background_image = pygame.image.load(background_image_path) if background_image_path else None
        vertical_center = screenHeight // 2
        padding = 10
        self.backButton = Button(screenWidth // 2 - 125, 50, 100, 100, "Back", BLACK, WHITE)
        self.titleText = Text(self.title, 100, WHITE, ((screenWidth / 2) - (len(self.title) * 24),36))
        self.play_button = Button(screenWidth // 2 - 100, vertical_center - 160 - padding, 200, 100, "Play", BLACK, WHITE)
        self.options_button = Button(screenWidth // 2 - 100, vertical_center - 50, 200, 100, "Options", BLACK, WHITE)
        self.tutorial_button = Button(screenWidth // 2 - 100, vertical_center + 60 + padding, 200, 100, "Tutorial", BLACK, WHITE)
        self.quit_button = Button(screenWidth // 2 - 100, vertical_center + 170 + 2 * padding, 200, 100, "Quit", BLACK, WHITE)
        self.backButton.textColor = WHITE
        self.play_button.textColor = WHITE
        self.options_button.textColor = WHITE
        self.tutorial_button.textColor = WHITE
        self.quit_button.textColor = WHITE
        self.tutorial()
        self.settings()

    def tutorial(self):
        text = "This is a sample text that we want to wrap within a box to prevent it from leaving the square."
        self.tutorial_text = WrapText(text,20,WHITE,((screenWidth / 2) - 125,200),(self.width) - 432.9)
        
    def settings(self):
        self.sound = Text("Music", 36, BLACK, (230, 200))
        self.sound_slider = Slider(screen, 230, 240, 200, 10, min=0, max=100, step=1, initial=100)
        self.sound_output = TextBox(screen, 440, 210, 50, 50, fontSize=25)
        self.sound_output.disable()
        self.sound_effects = Text("Sound Effects", 36, BLACK, (230, 300))
        self.sound_effects_slider = Slider(screen, 230, 340, 200, 10, min=0, max=100, step=1, initial=100)
        self.sound_effects_output = TextBox(screen, 440, 310, 50, 50, fontSize=25)
        self.sound_effects_output.disable()
        self.frame_rate = Text("Frame Rate", 36, BLACK, (230, 400))
        self.frame_rate_slider = Slider(screen, 230, 450, 128, 10, min=1, max=64, step=1, initial=64)
        self.frame_rate_output = TextBox(screen, 440, 413, 50, 50, fontSize=25)
        self.frame_rate_output.disable()
        self.brightness_text = Text("Brightness", 36, BLACK, (230, 500))
        self.brightness_slider = Slider(screen, 230, 550, 200, 10, min=0, max=1.0, step=0.1, initial=1.0)
        self.brightness_output = TextBox(screen, 440, 513, 50, 50, fontSize=25)
        self.brightness_output.disable()

    def draw(self, screen):
        global Background_volume, soundEffect_volume, frameRate, brightness
        if self.visible:
            if self.background_image:
                image_rect = self.background_image.get_rect()
                image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
                image_rect = image_rect.inflate(((self.width) - 400 - image_rect.width, (self.height) - 40 - image_rect.height))
                screen.blit(pygame.transform.scale(self.background_image, (image_rect.width, image_rect.height)), image_rect.topleft)

            if not(self.showTutorial or self.showSettings):
                self.titleText.render(screen)
                self.play_button.draw(screen)
                self.options_button.draw(screen)
                self.tutorial_button.draw(screen)
                self.quit_button.draw(screen)
            else:
                self.backButton.draw(screen)
                if (self.showTutorial):
                    self.tutorial_text.render(screen)
                else:
                    # sliders
                    self.sound.render(screen)
                    self.sound_effects.render(screen)
                    self.frame_rate.render(screen)
                    self.sound_slider.draw()
                    self.sound_output.draw()
                    self.sound_output.setText(self.sound_slider.getValue())
                    Background_volume = self.sound_slider.getValue()
                    self.sound_effects_slider.draw()
                    self.sound_effects_output.draw()
                    self.sound_effects_output.setText(self.sound_effects_slider.getValue())
                    soundEffect_volume = self.sound_effects_slider.getValue()
                    self.frame_rate_slider.draw()
                    self.frame_rate_output.draw()
                    self.frame_rate_output.setText(self.frame_rate_slider.getValue())
                    frameRate = self.frame_rate_slider.getValue()
                    self.brightness_text.render(screen)
                    self.brightness_slider.draw()
                    self.brightness_output.draw()
                    self.brightness_output.setText(round(self.brightness_slider.getValue(),2))
                    brightness = round(self.brightness_slider.getValue(),2)

    def handle_event(self, event):
        global running, HomeScreen
        if self.visible:
            pygame_widgets.update(event)
            if not(self.showTutorial or self.showSettings):
                button_list = [self.backButton, self.play_button, self.options_button, self.tutorial_button, self.quit_button]
                for button in button_list:
                    button.textColor = BLACK if button.color == button.active_color else WHITE

                self.play_button.handle_event(event)
                self.options_button.handle_event(event)
                self.tutorial_button.handle_event(event)
                self.quit_button.handle_event(event)

                if self.play_button.clicked:
                    HomeScreen = False
                    self.play_button.reset()

                if self.options_button.clicked:
                    self.showSettings = True
                    self.options_button.reset()

                if self.tutorial_button.clicked:
                    self.showTutorial = True
                    self.tutorial_button.reset()

                if self.quit_button.clicked:
                    running = False
                    sys.exit()
            else:
                self.backButton.handle_event(event)
                if self.backButton.clicked:
                    if self.showTutorial:
                        self.showTutorial = False
                    else:
                        self.showSettings = False
                    self.backButton.reset()
menuWindow = Main_Menu(screenHeight, screenWidth, (0, 0),r'New folder\images\images.png')
# brightness
def adjust_brightness(surface, brightness):
    overlay = pygame.Surface((screenWidth, screenHeight))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(255 - int(brightness * 255))
    surface.blit(overlay, (0, 0))

# map details
paths = []
def AddPath():
    for _ in range(random.randint(1,3)):
        path = Path(screenWidth // 50, screenHeight // 50)
        path.makePath()
        paths.append(path)

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

ememie_timer = 0
def TransitionMaps():
    global ememie_timer, ememies_list, paths
    ememie_timer += 1
    if ememie_timer % 500 == 0:
        ememies_list = pygame.sprite.Group()
        terrain_generator.regenerate_map()
        paths = []
        AddPath()

randomMap_times = 0
def RendomizeMap():
    global randomMap_times
    if randomMap_times == 0:
        for x in range(random.randint(1,100)):
            terrain_generator.regenerate_map()
            randomMap_times += 1
# loop
running = True
brightness = 1.0
frameRate = 64
Background_volume = 1.0
soundEffect_volume = 1.0
HomeScreen = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not(HomeScreen):
                    HomeScreen = True
        menuWindow.handle_event(event)
        if not(HomeScreen):
            terrain_generator.handle_event(event)
    screen.fill(WHITE)
    # map
    terrain_generator.draw(screen)

    if HomeScreen:
        TransitionMaps()
        if len(paths) <= 0:
            AddPath()
        # path
        for path in paths:
            path.draw(screen)
        # ememies
        spawn_enemies(100)
        if len(ememies_list):
            ememies_list.draw(screen)
            for ememie in ememies_list:
                ememie.move()
    else:
        ememies_list = pygame.sprite.Group()
        paths = []
        RendomizeMap()
        path.color = DARK_GRAY
        loaded_main_map = map_manager.load_main_map()
        if loaded_main_map:
            pass
        else:
            map_manager.generate_and_save_main_map(screenWidth, screenHeight, 50)
    # windows
    if HomeScreen:
        menuWindow.draw(screen)
    # update
    adjust_brightness(screen, brightness)
    pygame.display.flip()
    pygame.display.update()
    clock.tick(frameRate)
