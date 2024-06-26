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
        # Game
        self.tutorial_screen.add.label('Game:')
        game_long_text = (
            "Panel: This panel features a selection of three distinct tower options,",
            "each with varying costs ranging from $32.50 to $62.50. Each tower also",
            "incurs different bullet costs, ranging from $0.10 to $1.16. Additionally,",
            "the panel offers three different buildings and a hidden image. The buildings",
            "are priced between $125.00 and $154.90 each. Upgrading costs $25 per level,",
            "with production rates set at intervals of 900 units and 1800 units for upgrades.",
            "The hidden button hide the bars that shows the amount of storage, Gold, Helath",
            "you have currently."
        )
        wrapped_game_text = self.wrap_text(" ".join(game_long_text), 40)
        for line in wrapped_game_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

        # cost
        self.tutorial_screen.add.label('Cost:')
        cost_long_text = (
            "Red Tower (Cannon): Bullet Cost $0.10 - $0.45, Tower Cost $32.50 - $42.00, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2.",
            "Green Tower (MG): Bullet Cost $0.46 - $0.81, Tower Cost $43.00 - $52.50, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2",
            "Blue Tower (Missile Launcher): Bullet Cost $0.82 - $1.16, Tower Cost $53.00 - $62.50, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2",
            "Factory: Cost: $125.00 - $134.20, Upgrade Cost $25 per level, Production Rate: 900 - 1800",
            "Mine: Cost $135.20 - $144.40, Upgrade Cost $25 per level, Production Rate: 900 - 1800",
            "Warehouse: Cost $145.40 - $154.90, Upgrade Cost $25 per level, Production Rate: 900 - 1800"
        )
        wrapped_cost_text = self.wrap_text(" ".join(cost_long_text), 40)
        for line in wrapped_cost_text:
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
        def quit_menu(self):
            self.main_menu.disable()

    def Play(self):
        self.play = True

# pause menu
class PauseMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.play = True
        self.restart_game = False
        self.exit_game_varible = False
        self.create_main_menu()
    
    def create_main_menu(self):
        self.pause_menu_screen = pygame_menu.Menu('Pause Menu', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.options_screen = pygame_menu.Menu('Options', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.pause_menu_screen.add.button('Resume', self.resume)
        self.pause_menu_screen.add.button('Restart', self.restart)
        self.pause_menu_screen.add.button('Options', self.options)
        self.pause_menu_screen.add.button('Exit', self.exit_game)
    
    def resume(self):
        self.play = True
    
    def restart(self):
        self.restart_game = True
        self.play = True
    
    def options(self):
        self.music_volume = self.options_screen.add.range_slider('Music Volume', default=50, range_values=(0, 100), increment=1)
        self.options_screen.add.range_slider('Sound Effects', default=50, range_values=(0, 100), increment=1)
        self.options_screen.add.range_slider('Frame Rate', default=60, range_values=(30, 120), increment=1)
        self.options_screen.add.range_slider('Brightness', default=100, range_values=(0, 100), increment=1)
        self.options_screen.add.button('Return to Main Menu', pygame_menu.events.BACK)
        self.pause_menu_screen._open(self.options_screen)
    
    def exit_game(self):
        self.exit_game_varible = True
        self.play = True

    def quit_menu(self):
        self.pause_menu_screen.disable()
# bars
class Bars:
    def __init__(self, screen, width, y, x, color, text, image_path):
        self.screen = screen
        self.width = width
        self.y = y
        self.x = x
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

    def create_bar(self):
        bar_rect = pygame.Rect(self.x, self.y - 50, self.width, 50)
        pygame.draw.rect(self.screen, self.color, bar_rect)
        # Draw the icon
        icon = pygame.image.load(self.image_path)
        icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
        self.screen.blit(icon, (self.x, self.y - 50 + (50 - self.icon_size) // 2))
        # Render and center the text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2 + (self.icon_size / 2), self.y - 25))
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
        self.show_bars = True
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
        self.image_buttons_list = []

        # Grid settings
        cols = 2
        spacing = 10
        start_x = 25
        start_y = 80

        for i, data in enumerate(button_data):
            row = i // cols
            col = i % cols
            x = start_x + col * (BUTTON_SIZE[0] + spacing)
            y = start_y + row * (BUTTON_SIZE[1] + spacing)
            if len(data) == 4:
                image, cost, multiplier, product = data
                if i < 8:
                    button = GameSprites.PlayerButton(x, y, *BUTTON_SIZE, f'Assets/PNG/{image}', 50)
                    button.cost_per_bullet = cost * multiplier
                    self.player_types_list.append(button)
                else:
                    button = GameSprites.Building(x, y, *BUTTON_SIZE, f'Assets\Icons\{image}', 50, product)
                    self.building_type_list.append(button)
        
        image_button_text = UI.ImageButton(90, 380, 50, 50, r"Assets/Icons/extra/eye.png")
        self.image_buttons_list.append(image_button_text)

    def create_panel(self):
        if self.show:
            panel_rect = pygame.Rect(0, self.x, self.width, self.height)
            pygame.draw.rect(self.screen, self.color, panel_rect)
            for button in self.player_types_list:
                button.draw(self.screen)
            for button in self.building_type_list:
                button.draw(self.screen)
            for button in self.image_buttons_list:
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
        # image button
        for image_button in self.image_buttons_list:
            image_button.handle_event(event, r"Assets\Icons\extra\hidden.png")
            if image_button.clicked:
                image_button.update_image("Assets\Icons\extra\hidden.png")
            self.show_bars = not(image_button.clicked)
            image_button.reset()