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
import time
# screen
pygame.init()
mixer.init()
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
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
# SquareGrid class
class SquareGrid:
    def __init__(self, x, y, width, height, square_size, padding):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.square_size = square_size
        self.padding = padding
        self.squares = []
    def create_squares(self):
        num_squares_x = (self.width - self.padding) // (self.square_size + self.padding)
        num_squares_y = (self.height - self.padding) // (self.square_size + self.padding)
        for i in range(num_squares_x):
            for j in range(num_squares_y):
                square_x = self.x + i * (self.square_size + self.padding) + self.padding
                square_y = self.y + j * (self.square_size + self.padding) + self.padding
                self.squares.append((square_x, square_y, self.square_size))
    def draw(self, screen):
        for square in self.squares:
            pygame.draw.rect(screen, DARK_GRAY, pygame.Rect(square[0], square[1], square[2], square[2]))
    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.create_squares()
# Helper class for draggable objects
class DraggableImageButton:
    def __init__(self, x, y, width, height, image_path, cell_size, window_width, window_height, square_grid, panel_x, panel_width):
        self.rect = pygame.Rect(x, y, width, height)
        self.image_original = pygame.image.load(image_path)
        self.image_original = pygame.transform.scale(self.image_original, (width, height))
        self.image = self.image_original.copy()
        self.clicked = False
        self.offset = (0, 0)
        self.cell_size = cell_size
        self.window_width = window_width
        self.window_height = window_height
        self.square_grid = square_grid
        self.panel_x = panel_x
        self.panel_width = panel_width
        self.snap_to_square_grid = True

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def update_size(self, square):
        if self.snap_to_square_grid and len(square) == 4 and square[2] == square[3]:
            self.image = pygame.transform.scale(self.image_original, (square[2], square[2]))

    def snap_to_grid(self):
        if self.rect.colliderect(pygame.Rect(self.panel_x, 0, self.panel_width, self.window_height)):
            self.snap_to_square_grid = True
            button_center = self.rect.center
            for square in self.square_grid.squares:
                square_rect = pygame.Rect(square[0], square[1], square[2], square[2])
                if square_rect.collidepoint(button_center):
                    self.rect.x = square[0]
                    self.rect.y = square[1]
                    self.update_size(square)
        else:
            self.rect.x = round(self.rect.x / self.cell_size) * self.cell_size
            self.rect.y = round(self.rect.y / self.cell_size) * self.cell_size
            self.image = self.image_original.copy()
            self.snap_to_square_grid = False
    
    def limit_position(self):
        self.rect.x = max(0, min(self.rect.x, self.window_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.window_height - self.rect.height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                self.offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
            self.snap_to_grid()
            self.limit_position()
        elif event.type == pygame.MOUSEMOTION:
            if self.clicked:
                self.rect.x = event.pos[0] - self.offset[0]
                self.rect.y = event.pos[1] - self.offset[1]
                self.limit_position()
                self.snap_to_grid()
# panel
class Panel:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hidePannel_origPos = (50,0)
        self.hidePannel = Button(self.hidePannel_origPos[0],self.hidePannel_origPos[1],50,50,"<-",DARK_GRAY,RED)
        self.home = SettingButton(0, screenHeight - 50, 50, 50, r"New folder\images\hut.png")
        self.settings = SettingButton(50, screenHeight -50, 50, 50, r"New folder\images\gear.png")
        self.buildSettings = SettingButton(0, screenHeight - 100, 50, 50, r"New folder\images\maintenance.png")
        self.show = SettingButton(50, screenHeight - 100, 50, 50, r'New folder\images\view.png')
        self.squareGrid = SquareGrid(0, 60, self.width, self.height - 160, 35, 10)
        self.squareGrid.create_squares()
        self.testButton = DraggableImageButton(screenWidth / 2, screenHeight / 2,50,50,r"New folder\images\gear.png",grid.cell_size,screenWidth, screenHeight, self.squareGrid, self.width,5)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if not(self.testButton.snap_to_square_grid):
            self.testButton.draw(screen)

        self.hidePannel.draw(screen)
        if self.hidePannel.x == self.hidePannel_origPos[0] and self.hidePannel.y == self.hidePannel_origPos[1]:
            self.home.draw(screen)
            self.settings.draw(screen)
            self.buildSettings.draw(screen)
            self.show.draw(screen)
            self.squareGrid.draw(screen)
            if self.testButton.snap_to_square_grid:
                self.testButton.draw(screen)
    
    def buttonHandle_event(self, event):
        global showSettings, can_build, show_grid
        if showSettings == False:
            self.home.handle_event(event)
            if self.home.clicked:
                self.home.update_image(r"New folder\images\home.png")
                self.home.reset()
            elif not(self.home.clicked):
                self.home.update_image(r"New folder\images\hut.png")
            self.settings.handle_event(event)
            if self.settings.clicked:
                showSettings = True
                self.settings.update_image(r"New folder\images\gear(1).png")
                self.settings.reset()
            elif not(self.settings.clicked):
                self.settings.update_image(r"New folder\images\gear.png")
            self.buildSettings.handle_event(event)
            if self.buildSettings.clicked:
                can_build = not(can_build)
                if can_build:
                    self.buildSettings.update_image(r"New folder\images\tools.png")
                else:
                    self.buildSettings.update_image(r"New folder\images\maintenance.png")
                self.buildSettings.reset()
            self.show.handle_event(event)
            if self.show.clicked:
                show_grid = not(show_grid)
                if show_grid:
                    self.show.update_image(r"New folder\images\hidden.png")
                else:
                    self.show.update_image(r"New folder\images\view.png")
                self.show.reset()

    def move_buttons(self):
        self.show.clicked = not(self.show.clicked)
        self.buildSettings.clicked = not(self.buildSettings.clicked)
        self.width, self.height = 100, screenHeight
        self.home.y, self.settings.y = screenHeight - 50, screenHeight - 50
        self.buildSettings.y, self.show.y = screenHeight - 100, screenHeight - 100

    def update(self):
        self.move_buttons()
        self.testButton.window_height, self.testButton.window_width = screenHeight, screenWidth

    def handle_event(self, event):
        self.hidePannel.handle_event(event)
        if self.hidePannel.x == self.hidePannel_origPos[0] and self.hidePannel.y == self.hidePannel_origPos[1]:
            self.buttonHandle_event(event)
        
        if self.hidePannel.clicked:
            if self.hidePannel.x == self.hidePannel_origPos[0] and self.hidePannel.y == self.hidePannel_origPos[1]:
                self.hidePannel.x, self.hidePannel.y = 0, 0
                self.hidePannel.text = "->"
                self.x, self.y = -self.width, 0
            else:
                self.hidePannel.x, self.hidePannel.y = self.hidePannel_origPos
                self.hidePannel.text = "<-"
                self.x, self.y = 0, 0
            self.hidePannel.reset()
        self.testButton.handle_event(event)
panel = Panel(0,0, 100, screenWidth, WHITE)
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

    def update(self):
        self.width, self.height = screenWidth, screenHeight
        self.close_button.x, self.close_button.y = self.x + self.width - 40, self.y

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
        elif event.type == pygame.VIDEORESIZE:
                screenWidth, screenHeight = event.size
        panel.handle_event(event)
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
        panel.draw(screen)
    else:
        # windows
        menuWindow.visible = True
        menuWindow.draw(screen)
    # update
    pygame.display.flip()
    pygame.display.update()
    clock.tick(frameRate)
