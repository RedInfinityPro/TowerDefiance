import pygame
import pygame_widgets
import pygame.sprite
from pygame import mixer
from pygame.surfarray import make_surface
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.dropdown import Dropdown
import pygame_textinput
# ---------------
import random, time, sys, math
from perlin_noise import PerlinNoise
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
# hand made files
import PerlinMapGenerator
# screen
pygame.init()
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Tower Defince")
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
        self.highlighted = False

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

    def handle_highlight(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted = self.rect.collidepoint(mouse_pos)

    def reset(self):
        self.clicked = False
        self.highlighted = False
# map images
class GroundImage:
    def __init__(self, screen_width, screen_height, cell_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // cell_size
        self.height = screen_height // cell_size
        self.pick = random.randint(0, 1)
        self.biome_type_list = ['grassland', 'mountain', 'desert', 'snow', 'forest', 'swamp']
        self.biome_type = random.choice(self.biome_type_list)
        self.origionalType = self.biome_type
        self.ground_data = self.generate_ground()

    def get_biome_color(self, biome_type, brightness):
        if biome_type == 'water':
            color_value = int(brightness * 100) + random.randint(-10, 10)
            return (0, 0, max(0, min(255, color_value)))
        elif biome_type == 'grassland':
            color_value = int(brightness * 100) + random.randint(-10, 10)
            return (0, max(0, min(255, color_value)), 0)
        elif biome_type == 'mountain':
            color_value = int(brightness * 100) + random.randint(-10, 10)
            return (max(0, min(255, color_value)), max(0, min(255, color_value) - 50), max(0, min(255, color_value) - 100))
        elif biome_type == 'desert':
            base_color = (max(200, min(255, brightness * 255)), max(150, min(255, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'snow':
            base_color = (255, 255, 255)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'forest':
            base_color = (0, max(50, min(150, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'swamp':
            base_color = (max(0, min(100, brightness * 255)), max(100, min(200, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)

    def generate_ground(self):
        returnList = []
        freq = random.uniform(5, 30)
        amp = random.uniform(1, 15)
        octaves = random.randint(1, 6)
        seed = random.randint(1, sys.maxsize)
        noise = PerlinNoise(octaves=octaves, seed=seed)
        water_threshold = water_threshold = random.triangular(0.0, 0.2, 0.5) # Use 0.2 - 0.5 for realism

        for i in range(self.width):
            for ii in range(self.height):
                cell_x = i / self.width
                cell_y = ii / self.height
                cell_height = noise([cell_x / freq, cell_y / freq]) * amp
                brightness = (cell_height + amp) / (2 * amp)
                brightness = max(0, min(1, brightness))
                # Adjust color based on height and add some randomness
                if self.pick == 1:
                    if cell_height < water_threshold:
                        biome_type = "water"
                        color = self.get_biome_color(biome_type, brightness)
                    else:
                        biome_type = self.origionalType
                        color = self.get_biome_color(biome_type, brightness)
                    returnList.append([(cell_x, cell_y), cell_height, color])
                else:
                    color_value = int(brightness * 255) + random.randint(-10, 10)
                    color_value = max(0, min(255, color_value))
                    if cell_height < water_threshold:
                        color = (0, 0, color_value)
                    else:
                        color = (color_value, color_value - 50, color_value - 100)
                    returnList.append([(cell_x, cell_y), cell_height, color])
        return returnList
    
    def regenerate_map(self):
        self.pick = random.randint(0, 1)
        self.biome_type_list = ['grassland', 'mountain', 'desert', 'snow', 'forest', 'swamp']
        self.biome_type = random.choice(self.biome_type_list)
        self.ground_data = self.generate_ground()

    def generate_map_surface(self):
        map_surface = pygame.Surface((self.screen_width, self.screen_height))
        for item in self.ground_data:
            cell_x, cell_y = item[0]
            color = item[2]
            pygame.draw.rect(map_surface, color, (cell_x * self.screen_width, cell_y * self.screen_height, self.cell_size, self.cell_size))
        return map_surface
image_ground = GroundImage(screenWidth,screenHeight, 50)
map_surface = image_ground.generate_map_surface()
# map menu
class Map_Menu():
    def __init__(self, width, height, position=(0, 0), background_image_path=None):
        self.width = width
        self.height = height
        self.x, self.y = position[0], position[1]
        self.visible = True
        self.title = "Menu"
        self.character_limit = 9
        self.background_image = pygame.image.load(background_image_path) if background_image_path else None
        self.backButton = Button(screenWidth // 2 - 125, 50, 110, 50, "Back", GREEN, WHITE)
        self.backButton.textColor = GREEN
        self.pickBiomes = Dropdown(screen, 350, 50, 100, 50, name="Biomes",choices = ['grassland','mountain','desert','snow','forest','swamp'])
        self.regenerate_map = Button(screenWidth // 2 - 125, 110, 110, 50, "Regenerate", GREEN, WHITE)
        self.regenerate_map.textColor = GREEN
        self.submitButton = Button(screenWidth // 2 - 125, 600, self.width - 450, 50, "Submit", GREEN, WHITE)
        self.submitButton.textColor = GREEN
        self.sliders()

    def sliders(self):
        self.seed = Text("Seed", 36, GREEN, (350, 110))
        self.seed_textbox = pygame_textinput.TextInputVisualizer(font_color=WHITE,cursor_color=WHITE)
        self.freq = Text("Frequency", 36, GREEN, (230, 200))
        self.freq_slider = Slider(screen, 230, 240, 200, 10, min=5.0, max=30.0, step=0.1, initial=0.5)
        self.freq_slider.handleColour, self.freq_slider.colour = WHITE, GRAY
        self.freq_output = TextBox(screen, 440, 210, 50, 50, fontSize=20)
        self.freq_output.disable()
        self.amp = Text("Amplitude", 36, GREEN, (230, 300))
        self.amp_slider = Slider(screen, 230, 340, 200, 10, min=1.0, max=15.0, step=0.1, initial=15.0)
        self.amp_slider.handleColour, self.amp_slider.colour = WHITE, GRAY
        self.amp_output = TextBox(screen, 440, 310, 50, 50, fontSize=20)
        self.amp_output.disable()
        self.octaves = Text("Octaves", 36, GREEN, (230, 400))
        self.octaves_slider = Slider(screen, 230, 450, 200, 10, min=1, max=6, step=1, initial=6)
        self.octaves_slider.handleColour, self.octaves_slider.colour = WHITE, GRAY
        self.octaves_output = TextBox(screen, 440, 413, 50, 50, fontSize=25)
        self.octaves_output.disable()
        self.water = Text("Water Threshold", 36, GREEN, (230, 500))
        self.water_slider = Slider(screen, 230, 550, 200, 10, min=0.0, max=0.5, step=0.1, initial=0.5)
        self.water_slider.handleColour, self.water_slider.colour = WHITE, GRAY
        self.water_output = TextBox(screen, 440, 513, 50, 50, fontSize=25)
        self.water_output.disable()

    def draw_sliders(self, screen):
        global terrain_generator
        self.seed.render(screen)
        if len(self.seed_textbox.value) < self.character_limit:
            filtered_input = ''.join(c for c in self.seed_textbox.value if c.isdigit())
            self.seed_textbox.value = filtered_input
        else:
            self.seed_textbox.value = self.seed_textbox.value[:self.character_limit]
        if len(self.seed_textbox.value) > 0: 
            terrain_generator.seed = int(self.seed_textbox.value) 
        else: 
            terrain_generator.seed = random.randint(0,sys.maxsize)
        screen.blit(self.seed_textbox.surface, (350,150))

        self.freq.render(screen)
        self.freq_slider.draw()
        self.freq_output.draw()
        self.freq_output.setText(round(self.freq_slider.getValue(),2))
        terrain_generator.freq = self.freq_slider.getValue()

        self.amp.render(screen)
        self.amp_slider.draw()
        self.amp_output.draw()
        self.amp_output.setText(round(self.amp_slider.getValue(),2))
        terrain_generator.amp = self.amp_slider.getValue()

        self.octaves.render(screen)
        self.octaves_slider.draw()
        self.octaves_output.draw()
        self.octaves_output.setText(self.octaves_slider.getValue())
        terrain_generator.octaves = self.octaves_slider.getValue()

        self.water.render(screen)
        self.water_slider.draw()
        self.water_output.draw()
        self.water_output.setText(round(self.water_slider.getValue(),2))
        terrain_generator.water_threshold = self.water_slider.getValue()

        self.pickBiomes.draw()
        terrain_generator.biome_type = self.pickBiomes.getSelected

    def draw(self, screen):
        if self.visible:
            if self.background_image:
                image_rect = self.background_image.get_rect()
                image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
                image_rect = image_rect.inflate(((self.width) - 400 - image_rect.width, (self.height) - 40 - image_rect.height))
                screen.blit(pygame.transform.scale(self.background_image, (image_rect.width, image_rect.height)), image_rect.topleft)
            else:
                pygame.draw.rect(screen, DARK_GRAY, ((self.x + self.width // 2) - 150, (self.y + self.height // 2) - 330, self.width - 400, self.height - 40), 2)  # Draw a white square outline
        self.backButton.draw(screen)
        self.regenerate_map.draw(screen)
        self.draw_sliders(screen)
        self.submitButton.draw(screen)

    def handle_event(self, event):
        global show_MainMenu, terrain_generator, show_MapMenu
        if self.visible:
            pygame_widgets.update(event)
            button_list = [self.backButton, self.submitButton, self.regenerate_map]
            for button in button_list:
                button.textColor = GREEN if button.color == button.active_color else WHITE
            self.seed_textbox.update(events)
            self.backButton.handle_event(event)
            if self.backButton.clicked:
                show_MainMenu = True
                self.backButton.reset()
                self.seed_textbox.value = ""
            self.submitButton.handle_event(event)
            if self.submitButton.clicked:
                self.submitButton.reset()
            self.regenerate_map.handle_event(event)
            if self.regenerate_map.clicked:
                terrain_generator.regenerate_map(biome_type = self.pickBiomes.getSelected())
                self.regenerate_map.reset()
                time.sleep(0.2)
            self.submitButton.handle_event(event)
            if self.submitButton.clicked:
                show_MapMenu = False
                self.submitButton.reset()
mapWindow = Map_Menu(screenHeight, screenWidth, (0, 0))
# start menu
class Start_Menu():
    def __init__(self, width, height, position=(0, 0), background_image_path=None):
        self.width = width
        self.height = height
        self.x, self.y = position[0], position[1]
        self.visible = True
        self.showTutorial = False
        self.showSettings = False
        self.showLoadScreen = False
        self.title = "Menu"
        self.background_image = pygame.image.load(background_image_path) if background_image_path else None
        vertical_center = screenHeight // 2
        padding = 20
        button_height = 80
        self.titleText = Text(self.title, 100, WHITE, ((screenWidth / 2) - (len(self.title) * 24),36))
        self.backButton = Button(screenWidth // 2 - 125, 50, 100, 100, "Back", BLACK, WHITE)
        self.button_positions = [vertical_center - 2 * (button_height + padding), vertical_center - 1 * (button_height + padding), vertical_center, vertical_center + 1 * (button_height + padding), vertical_center + 2 * (button_height + padding)]

        self.play_button = Button(screenWidth // 2 - 100, self.button_positions[0], 200, button_height, "Play", (0, 0, 0), (255, 255, 255))
        self.loadGame_button = Button(screenWidth // 2 - 100, self.button_positions[1], 200, button_height, "Load Game", (0, 0, 0), (255, 255, 255)) 
        self.options_button = Button(screenWidth // 2 - 100, self.button_positions[2], 200, button_height, "Options", (0, 0, 0), (255, 255, 255))
        self.tutorial_button = Button(screenWidth // 2 - 100, self.button_positions[3], 200, button_height, "Tutorial", (0, 0, 0), (255, 255, 255))
        self.quit_button = Button(screenWidth // 2 - 100, self.button_positions[4], 200, button_height, "Quit", (0, 0, 0), (255, 255, 255))
        self.backButton.textColor = WHITE
        self.play_button.textColor = WHITE
        self.loadGame_button.textColor = WHITE
        self.options_button.textColor = WHITE
        self.tutorial_button.textColor = WHITE
        self.quit_button.textColor = WHITE
        self.tutorial()
        self.settings()
        self.loadScreen()

    def get_text(self):
        self.file = open(r"New folder\tutorial_text.text", "r")
        self.content = self.file.read()
        return self.content

    def tutorial(self):
        text = self.get_text()
        self.tutorial_text = WrapText(text,20,WHITE,((screenWidth / 2) - 130,220),(self.width) - 427)
        
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

    def loadScreen(self):
        self.loadSlots_list = []
        for x in range(5):
            self.loadSlots = SettingButton(screenWidth / 2 - 147, (100) * x + 170, 300, 100, r"New folder\images\plus.png")
            self.loadSlots_list.append(self.loadSlots)
    
    def draw(self, screen):
        global Background_volume, soundEffect_volume, frameRate, brightness
        if self.visible:
            if self.background_image:
                image_rect = self.background_image.get_rect()
                image_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
                image_rect = image_rect.inflate(((self.width) - 400 - image_rect.width, (self.height) - 40 - image_rect.height))
                screen.blit(pygame.transform.scale(self.background_image, (image_rect.width, image_rect.height)), image_rect.topleft)

            if not(self.showTutorial or self.showSettings or self.showLoadScreen):
                self.titleText.render(screen)
                self.play_button.draw(screen)
                self.loadGame_button.draw(screen)
                self.options_button.draw(screen)
                self.tutorial_button.draw(screen)
                self.quit_button.draw(screen)
            elif (self.showTutorial):
                self.tutorial_text.render(screen)
                self.backButton.draw(screen)
            elif (self.showSettings):
                self.backButton.draw(screen)
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
            elif (self.showLoadScreen):
                self.backButton.draw(screen)
                for loadSlots in self.loadSlots_list:
                    loadSlots.draw(screen)

    def handle_event(self, event):
        global running, show_MainMenu, show_MapMenu
        if self.visible:
            pygame_widgets.update(event)
            if not(self.showTutorial or self.showSettings or self.showLoadScreen):
                button_list = [self.backButton, self.play_button, self.loadGame_button, self.options_button, self.tutorial_button, self.quit_button]
                for button in button_list:
                    button.textColor = BLACK if button.color == button.active_color else WHITE

                self.play_button.handle_event(event)
                self.loadGame_button.handle_event(event)
                self.options_button.handle_event(event)
                self.tutorial_button.handle_event(event)
                self.quit_button.handle_event(event)

                if self.play_button.clicked:
                    show_MainMenu = False
                    show_MapMenu = True
                    self.play_button.reset()

                if self.loadGame_button.clicked:
                    self.showLoadScreen = True
                    self.loadGame_button.reset()

                if self.options_button.clicked:
                    self.showSettings = True
                    self.options_button.reset()

                if self.tutorial_button.clicked:
                    self.showTutorial = True
                    self.tutorial_button.reset()
                    self.file.close()

                if self.quit_button.clicked:
                    self.quit_button.reset()
                    running = False
                    sys.exit()
            else:
                if self.showTutorial:
                    self.backButton.handle_event(event)
                    if self.backButton.clicked:
                        self.showTutorial = False
                        self.backButton.reset()
                elif self.showSettings:
                    self.backButton.handle_event(event)
                    if self.backButton.clicked:
                        self.showSettings = False
                        self.backButton.reset()
                elif self.showLoadScreen:
                    self.backButton.handle_event(event)
                    for loadSlots in self.loadSlots_list:
                        loadSlots.handle_event(event)
                        loadSlots.handle_highlight(event)
                    if self.backButton.clicked:
                        self.showLoadScreen = False
                        self.backButton.reset()
menuWindow = Start_Menu(screenHeight, screenWidth, (0, 0),r'New folder\images\images.png')
# path
class Path:
    def __init__(self, width, height):
        self.matrixWidth = width
        self.matrixHeight = height
        self.matrix = []
        self.color = DARK_GRAY
        self.outlineColor = GRAY
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
            pygame.draw.rect(screen, self.outlineColor, (x * 50, y * 50, 50, 50),2)
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
# brightness
def adjust_brightness(surface, brightness):
    overlay = pygame.Surface((screenWidth, screenHeight))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(255 - int(brightness * 255))
    surface.blit(overlay, (0, 0))
# add paths to scene
paths = []
def AddPath():
    for _ in range(random.randint(1,3)):
        path = Path(screenWidth // 50, screenHeight // 50)
        path.makePath()
        paths.append(path)
# enemies
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
# menu
AnimationTimer = 0
def MenuAnimation():
    global AnimationTimer, map_surface, paths, ememies_list
    AnimationTimer += 1
    if (AnimationTimer % 500) == 0:
        image_ground.regenerate_map()
        map_surface = image_ground.generate_map_surface()
        paths = []
        ememies_list = pygame.sprite.Group()
# random map
randomMap_times = 0
terrain_generator = PerlinMapGenerator.Ground(screenWidth,screenHeight,50)
def RendomizeMap():
    global randomMap_times
    if randomMap_times == 0:
        for x in range(random.randint(1,100)):
            terrain_generator.regenerate_map()
        randomMap_times += 1
# loop
brightness = 1.0
frameRate = 64
Background_volume = 1.0
soundEffect_volume = 1.0
show_MainMenu = True
show_MapMenu = False
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                show_MainMenu = True
                show_MapMenu = False
        if show_MainMenu:
            menuWindow.handle_event(event)
        if not(show_MapMenu) and not(show_MainMenu):
            terrain_generator.handle_event(event)
    mapWindow.handle_event(event)
    screen.fill(WHITE)
    if show_MainMenu:
        randomMap_times = 0
        MenuAnimation()
        screen.blit(map_surface, (0, 0))
        # path
        if len(paths) <= 0:
            AddPath()
        for path in paths:
            path.draw(screen)
        # ememies
        spawn_enemies(100)
        if len(ememies_list):
            ememies_list.draw(screen)
            for ememie in ememies_list:
                ememie.move()
        menuWindow.draw(screen)
    else:
        RendomizeMap()
        terrain_generator.draw(screen)
        if show_MapMenu:
            mapWindow.draw(screen)
    # update
    adjust_brightness(screen, brightness)
    pygame.display.flip()
    pygame.display.update()
    clock.tick(frameRate)
