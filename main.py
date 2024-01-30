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
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
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
            pygame.draw.line(screen, BLACK, (x * self.cell_size + self.grid_offset[0], 0),
                             (x * self.cell_size + self.grid_offset[0], screen.get_height()))
        for y in range(start_y, end_y):
            pygame.draw.line(screen, BLACK, (0, y * self.cell_size + self.grid_offset[1]),
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

    def generate_ground(self):
        returnList = []
        freq = random.uniform(5, 30)
        amp = random.uniform(1, 15)
        octaves = random.randint(1, 6)
        seed = random.randint(1, 100)
        noise = PerlinNoise(octaves=octaves, seed=seed)
        water_threshold = random.uniform(0.0, 0.1) # user 0.2 - 0.5 if you want realisum

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

    def regenerate_map(self):
        self.segmentList = []
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
                self.regenerate_map()
                item.reset()
terrain_generator = Ground(screenWidth, screenHeight, 50)
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
home = SettingButton(0, screenHeight - 50, 50, 50, r"New folder\images\hut.png")
settings = SettingButton(50, screenHeight -50, 50, 50, r"New folder\images\gear.png")
buildSettings = SettingButton(0, screenHeight - 100, 50, 50, r"New folder\images\maintenance.png")
show = SettingButton(50, screenHeight - 100, 50, 50, r'New folder\images\view.png')
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
#menu
class MenuWindow:
    def __init__(self, width, height, position=(0, 0)):
        self.width = width
        self.height = height
        self.x, self.y = position[0], position[1]
        self.visible = True
        self.close_button = Button(self.x + self.width - 40, self.y, 40,40,"X",RED,DARK_GRAY)
        self.title = "Menu"
        self.background_color = WHITE
        self.titleText = Text(self.title, 36, BLACK, ((screenWidth / 2) - (len(self.title) * 10),36))
        self.showSettings = True
        self.showFixBug = False
        self.showSaveQuit = False
        # buttons
        self.settings = Button(self.x + 10, self.y + 100,100,50,"Settings",DARK_GRAY,BLUE)
        self.fixBug = Button(self.x + 120, self.y + 100,108,50,"Report Bug",DARK_GRAY,BLUE)
        self.saveQuit = Button(self.x + 237, self.y + 100,150,50,"Save and Quit",DARK_GRAY,BLUE)
        # Sliders
        self.sound = Text("Music", 36, BLACK, (10, 160))
        self.sound_slider = Slider(screen, 10, 200, 200, 10, min=0, max=100, step=1, initial=100)
        self.sound_output = TextBox(screen, 220, 180, 50, 50, fontSize=25)
        self.sound_output.disable()

        self.sound_effects = Text("Sound Effects", 36, BLACK, (10, 260))
        self.sound_effects_slider = Slider(screen, 10, 300, 200, 10, min=0, max=100, step=1, initial=100)
        self.sound_effects_output = TextBox(screen, 220, 270, 50, 50, fontSize=25)
        self.sound_effects_output.disable()

        self.frame_rate = Text("Frame Rate", 36, BLACK, (10, 360))
        self.frame_rate_slider = Slider(screen, 10, 400, 128, 10, min=1, max=64, step=1, initial=64)
        self.frame_rate_output = TextBox(screen, 148, 370, 50, 50, fontSize=25)
        self.frame_rate_output.disable()

    def draw(self, screen):
        global frameRate,Background_volume,soundEffect_volume
        if self.visible:
            pygame.draw.rect(screen, self.background_color, (self.x - 2, self.y - 2, self.width + 4, self.height + 4))
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height), 2)
            self.close_button.draw(screen)
            self.titleText.render(screen)
            # buttons
            self.settings.draw(screen)
            self.fixBug.draw(screen)
            self.saveQuit.draw(screen)
            
            if showSettings:
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
            else:
                self.sound_output.enable()
                self.sound_effects_output.enable()
                self.frame_rate_output.enable()

    def handle_event(self, event):
        global showSettings
        if self.visible:
            if self.showSettings:
                self.close_button.handle_event(event)
                self.settings.handle_event(event)
                self.fixBug.handle_event(event)
                self.saveQuit.handle_event(event)
            
            if self.settings.clicked:
                self.showSettings = True
                self.showFixBug = False
                self.showSaveQuit = False
                self.settings.reset()

            if self.fixBug.clicked:
                self.showSettings = False
                self.showFixBug = True
                self.showSaveQuit = False
                self.fixBug.reset()

            if self.saveQuit.clicked:
                self.showSettings = False
                self.showFixBug = False
                self.showSaveQuit = True
                self.saveQuit.reset()

            if self.close_button.clicked:
                showSettings = False
                self.visible = False
                self.close_button.reset()
        pygame_widgets.update(event)
menuWindow = MenuWindow(screenHeight, screenWidth, (0, 0))
# loop
frameRate = 64
Background_volume = 1.0
soundEffect_volume = 1.0
show_grid = False
can_build = False
showSettings = False
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
        # settings events
        if showSettings == False:
            home.handle_event(event)
            if home.clicked:
                home.update_image(r"New folder\images\home.png")
                home.reset()
            elif not(home.clicked):
                home.update_image(r"New folder\images\hut.png")
            settings.handle_event(event)
            if settings.clicked:
                showSettings = True
                settings.update_image(r"New folder\images\gear(1).png")
                settings.reset()
            elif not(home.clicked):
                settings.update_image(r"New folder\images\gear.png")
            buildSettings.handle_event(event)
            if buildSettings.clicked:
                can_build = not(can_build)
                if can_build:
                    buildSettings.update_image(r"New folder\images\tools.png")
                else:
                    buildSettings.update_image(r"New folder\images\maintenance.png")
                buildSettings.reset()
            show.handle_event(event)
            if show.clicked:
                show_grid = not(show_grid)
                if show_grid:
                    show.update_image(r"New folder\images\hidden.png")
                else:
                    show.update_image(r"New folder\images\view.png")
                show.reset()
        # windows events
        menuWindow.handle_event(event)
        # map events
        # terrain_generator.handle_event(event)
    screen.fill(WHITE)
    # map
    if showFull_map:
        terrain_generator.draw(screen)
    # grid
    if show_grid:
        grid.draw(screen)
    # menu buttons
    if showSettings == False:
        home.draw(screen)
        settings.draw(screen)
        buildSettings.draw(screen)
        show.draw(screen)
    else:
        # windows
        menuWindow.visible = True
        menuWindow.draw(screen)
    # update
    pygame.display.flip()
    pygame.display.update()
    clock.tick(frameRate)
