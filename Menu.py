import pygame
import pygame_menu
from pygame_menu import themes
import textwrap
import random
# --
import GameSprites, UI

# main menu
class MainMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.play = False
        self.create_main_menu()
    
    def create_main_menu(self):
        self.main_menu = pygame_menu.Menu('Welcome', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.loadGame_screen = pygame_menu.Menu('Load Game', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.settings_screen = pygame_menu.Menu('Settings', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.tutorial_screen = pygame_menu.Menu('Tutorial', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.main_menu.add.button('Play', self.Play)
        self.main_menu.add.button('Load Game', self.load_game)
        self.main_menu.add.button('Tutorial', self.tutorial)
        self.main_menu.add.button('Settings', self.settings)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)
    
    def load_game(self):
        self.loadGame_screen.clear()
        saved_games = [
            "Load Game",
            "Load Game",
            "Load Game"
        ]
        for index, save in enumerate(saved_games):
            self.loadGame_screen.add.button(save, lambda index=index: self.load_game(index))
        self.loadGame_screen.add.button('Return to Main Menu', pygame_menu.events.BACK)
        self.main_menu._open(self.loadGame_screen)

    def settings(self):
        self.music_volume = self.settings_screen.add.range_slider('Music Volume', default=50, range_values=(0, 100), increment=1)
        self.settings_screen.add.range_slider('Sound Effects', default=50, range_values=(0, 100), increment=1)
        self.settings_screen.add.range_slider('Frame Rate', default=60, range_values=(30, 120), increment=1)
        self.settings_screen.add.range_slider('Brightness', default=100, range_values=(0, 100), increment=1)
        self.settings_screen.add.button('Return to Main Menu', pygame_menu.events.BACK)
        self.main_menu._open(self.settings_screen)
    
    def tutorial(self):
        self.tutorial_screen.clear()
        # gmae
        self.tutorial_screen.add.label('Game:')
        frequency_long_text = (
            "In the gmae you are persented with 3 diffrent colors: Red, Green, and Blue.",
            "Each one has a select cost per tower and a sepret cost pre bullet. However,",
            "For each kill, you will earn $0.01.",
            "Red Tower: 32.50 - 42.00 | Bullets: 0.10 - 0.45",
            "Blue Tower: 43.00 - 52.50 | Bullets: 0.46 - 0.81",
            "Green Tower: 53.00 - 62.50 | Bullets: 0.82 - 1.16"
        )
        wrapped_frequency_text = self.wrap_text(frequency_long_text, 40)
        for line in wrapped_frequency_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

        # Frequency
        self.tutorial_screen.add.label('Frequency:')
        frequency_long_text = (
            "In the context of Perlin noise, frequency refers to how often the noise "
            "function repeats. A higher frequency will result in more 'features' or "
            "details in the generated noise pattern. Increasing the frequency can "
            "create a more complex and detailed appearance."
        )
        wrapped_frequency_text = self.wrap_text(frequency_long_text, 40)
        for line in wrapped_frequency_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

        # Amplitude
        self.tutorial_screen.add.label('Amplitude:')
        amplitude_long_text = (
            "Amplitude in Perlin noise determines the height or intensity of the "
            "generated noise. Higher amplitude results in more pronounced features, "
            "creating more significant variations in the terrain or texture."
        )
        wrapped_amplitude_text = self.wrap_text(amplitude_long_text, 40)
        for line in wrapped_amplitude_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

        # Octaves
        self.tutorial_screen.add.label('Octaves:')
        octaves_long_text = (
            "Octaves are used to add multiple layers of Perlin noise to create "
            "a more realistic and complex result. Each octave introduces noise "
            "at a different frequency and amplitude. Combining multiple octaves "
            "allows for the creation of more natural-looking terrain or textures."
        )
        wrapped_octaves_text = self.wrap_text(octaves_long_text, 40)
        for line in wrapped_octaves_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

        # Perlin Noise
        self.tutorial_screen.add.label('Perlin Noise:')
        perlin_noise_long_text = (
            "Perlin noise is a gradient noise function used in procedural generation. "
            "It produces continuous, smooth random variations and is commonly used "
            "in computer graphics to create natural textures, terrain, and other "
            "visual effects."
        )
        wrapped_perlin_noise_text = self.wrap_text(perlin_noise_long_text, 40)
        for line in wrapped_perlin_noise_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')
        
        self.main_menu._open(self.tutorial_screen)

    def wrap_text(self, text, max_chars_per_line):
        return textwrap.wrap(text, width=max_chars_per_line)
    
    def quitMenu(self):
        self.main_menu.disable()

    def Play(self):
        self.play = True


# bars
class Bars:
    def __init__(self, screen, width, height, color, text, image_path):
        self.screen = screen
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.image_path = image_path
        # font
        self.icon_size = 40
        self.size_font()
        self.text_color = (0, 0, 0)

    def size_font(self):
        # font
        max_font_size = 36
        font = pygame.font.Font(None, max_font_size)
        while font.size(self.text)[0] > self.width - self.icon_size - 20:
            max_font_size -= 1
            font = pygame.font.Font(None, max_font_size)
        self.font = font

    def create_menu(self):
        bar_rect = pygame.Rect(0, self.height - 50, self.width, 50)
        pygame.draw.rect(self.screen, self.color, bar_rect)
        # Draw the icon
        icon = pygame.image.load(self.image_path)
        icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
        self.screen.blit(icon, (10, self.height - 50 + (50 - self.icon_size) // 2))
        # Render and center the text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.width // 2 + (self.icon_size / 2), self.height - 25))
        self.screen.blit(text_surface, text_rect)
    
    def update_text(self, new_text):
        self.text = new_text
        self.size_font()

# panel
class Panel:
    def __init__(self, screen, width, height, color):
        self.screen = screen
        self.width = width
        self.height = height
        self.color = color
        self.x = 0
        self.show = True
        self.expand_button = UI.Button(self.width - 60, 10, 50, 50, "->", (255,0,0), (105,105,105))
        # Define constants
        BUTTON_SIZE = (50, 50)
        tower_cost_ranges = [(32.50, 42.00), (43.00, 52.50), (53.00, 62.50)]
        bullet_cost_ranges = [(0.10, 0.45), (0.46, 0.81), (0.82, 1.16)]
        building_cost = [(125.00, 134.20), (135.20, 144.4), (145.4, 154.9)]
        # Generate costs
        tower_costs = [round(random.uniform(*r), 2) for r in tower_cost_ranges]
        bullet_costs = [round(random.uniform(*r), 2) for r in bullet_cost_ranges]
        building_costs = [round(random.uniform(*r), 2) for r in building_cost]

        # Create buttons
        button_data = [
            ('Cannon.png', bullet_costs[0], 1, None),
            ('Cannon2.png', bullet_costs[0], 2, None),
            ('MG.png', bullet_costs[1], 1, None),
            ('MG2.png', bullet_costs[1], 2, None),
            ('MG3.png', bullet_costs[1], 4, None),
            ('Missile_Launcher.png', bullet_costs[2], 1, None),
            ('Missile_Launcher2.png', bullet_costs[2], 2, None),
            ('Missile_Launcher3.png', bullet_costs[2], 4, None),
            ('factory.png', building_costs[0], 1, r"Assets\PNG\Bullet_Cannon.png"),
            ('mine.png', building_costs[1], 1, r"Assets\Icons\dollar.png"),
            ('warehouse.png', building_costs[2], 1, r"Assets\Icons\box.png")
        ]

        self.player_types_list = []
        self.building_type_list = []

        # Grid settings
        cols = 2
        spacing = 10
        start_x = 25
        start_y = 80

        for i, (image, bullet_cost, multiplier, product) in enumerate(button_data):
            row = i // cols
            col = i % cols
            x = start_x + col * (BUTTON_SIZE[0] + spacing)
            y = start_y + row * (BUTTON_SIZE[1] + spacing)
            if i < 8:
                button = GameSprites.PlayerButton(x, y, *BUTTON_SIZE, f'Assets/PNG/{image}', 50)
                button.cost_per_bullet = bullet_cost * multiplier
                self.player_types_list.append(button)
            else:
                button = GameSprites.Building(x, y, *BUTTON_SIZE, f'Assets\Icons\{image}', 50, product)
                self.building_type_list.append(button)
        
    def create_panel(self):
        if self.show:
            panel_rect = pygame.Rect(0, self.x, self.width, self.height)
            pygame.draw.rect(self.screen, self.color, panel_rect)
            for button in self.player_types_list + self.building_type_list:
                button.draw(self.screen)
        self.expand_button.draw(self.screen)

    def handle_event(self, event):
        self.expand_button.handle_event(event)
        if self.expand_button.clicked:
            self.show = not(self.show)
            self.expand_button.reset()
        if self.show:
            self.expand_button.x = self.width - 60
            self.expand_button.text = "<-"
        else:
            self.expand_button.x = 0
            self.expand_button.text = "->"