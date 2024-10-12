import pygame
import pygame_menu
from pygame_menu import themes
import textwrap
import random
# -- handmade
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
        self.credits_screen = pygame_menu.Menu('Credits', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.main_menu.add.button('Play', self.Play)
        self.main_menu.add.button('Load Game', self.load_game)
        self.main_menu.add.button('Tutorial', self.tutorial)
        self.main_menu.add.button('Settings', self.settings)
        self.main_menu.add.button('Credits', self.credits)
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
        self.settings_screen.clear()
        self.music_volume = self.settings_screen.add.range_slider('Music Volume', default=50, range_values=(0, 100), increment=1)
        self.settings_screen.add.range_slider('Sound Effects', default=50, range_values=(0, 100), increment=1)
        self.settings_screen.add.range_slider('Frame Rate', default=60, range_values=(30, 120), increment=1)
        self.settings_screen.add.range_slider('Brightness', default=100, range_values=(0, 100), increment=1)
        self.settings_screen.add.button('Return to Main Menu', pygame_menu.events.BACK)
        self.main_menu._open(self.settings_screen)
    
    def tutorial(self):
        self.tutorial_screen.clear()
        # general info
        self.tutorial_screen.add.label('general:')
        general_long_text = {
            "Bullet types:", 
            "Red tip: specialize in removing the enemies health.",
            "lazer: specialize in damaging the enemies armor.",
            "Missle: specialize in damaging the enemies armor and health",
            "Building driscription:",
            "The factory: Provides an alternative method to acquire essential resources like bullets. The factory offers a choice between two fixed types of bullets (Type 1 or Type 2, Type 3), which cannot be changed once selected.",
            "The mine: Offers an additional income source, generating coins independently of enemy encounters.",
            "The warehouse: Normally, towers expend money each time they fire due to depleted ammunition stocks, necessitating frequent purchases from external suppliers. However, with sufficient storage capacity, towers can draw from stored reserves, reducing the need for continuous expenditure. Essentially, investing $125.00 to $134.20 in a factory and an additional $145.40 to $154.90 in a warehouse, totaling a maximum of $289.10 (excluding upgrades), ensures ongoing bullet supply without further expenditure after this initial investment.",
        }
        wrapped_general_text = self.wrap_text(" ".join(general_long_text), 40)
        for line in wrapped_general_text:
            self.tutorial_screen.add.label(line)
        self.tutorial_screen.add.label('')

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
            "Red Tower (Cannon): Bullet Cost $0.10 - $0.45, Tower Cost $32.50 - $42.00, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2",
            "Green Tower (MG): Bullet Cost $0.50 - $0.85, Tower Cost $43.00 - $52.50, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2",
            "Blue Tower (Missile Launcher): Bullet Cost $0.90 - $1.30, Tower Cost $53.00 - $62.50, Upgrade Cost $25 per level, Bullet Upgrade Cost: current cost * 2",
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

    def credits(self):
        self.credits_screen.clear()
        # credits
        long_text = {
            "Ware, G. (n.d.). Box free icon. Retrieved from https://www.flaticon.com/free-icon/box_685388?term=box&page=1&position=2&origin=search&related_id=685388.",
            "sonnycandra. (n.d.). Hidden free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/hidden_10812267?term=eye&page=1&position=16&origin=search&related_id=10812267.",
            "Phai, N. (n.d.). Warehouse free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/warehouse_2897808?term=warehouse&page=1&position=52&origin=search&related_id=2897808.",
            "Nido. (2020). tower-defence-basic-towers. opengameart.org. Retrieved from https://opengameart.org/content/tower-defence-basic-towers.",
            "NajmunNahar. (n.d.). Dollar free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/dollar_9382189?term=dollar&page=1&position=18&origin=search&related_id=9382189.",
            "Kroffle. (n.d.). Heart free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/heart_9484251?term=heart&page=1&position=9&origin=search&related_id=9484251.",
            "justicon. (n.d.). Money Bag free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/money-bag_2460475?term=money&page=1&position=73&origin=search&related_id=2460475.",
            "hqrloveq. (n.d.). Up Arrow free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/up-arrow_5610930?term=up+arrow&page=1&position=5&origin=search&related_id=5610930.",
            "Freepik. (n.d.-b). Mine free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/mine_4492671?term=mine&page=1&position=8&origin=search&related_id=4492671.",
            "Freepik. (n.d.-a). Factory free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/factory_3256216?term=factory&page=1&position=2&origin=search&related_id=3256216.",
            "Cresnar, G. (n.d.). Eye free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/eye_159604?term=eye&page=1&position=1&origin=search&related_id=159604.",
            "Smashicons. (n.d.). Logout free icon. flaticon.com. Retrieved from https://www.flaticon.com/free-icon/logout_660350?term=exit&related_id=660350."
        }
        wrapped_credits_text = self.wrap_text(" ".join(long_text), 40)
        for line in wrapped_credits_text:
            self.credits_screen.add.label(line)
        self.credits_screen.add.label('')

        self.main_menu._open(self.credits_screen)

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
        self.options_screen.clear()
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
        self.pause = False
        self.expand_button = UI.Button(self.width - 60, 10, 50, 50, "->", (255,0,0), (105,105,105))
        # Define constants
        BUTTON_SIZE = (50, 50)
        # Define cost ranges
        tower_cost_ranges = {
            'Cannon': (32.50, 42.00),
            'Cannon2': (32.50, 42.00),
            'Cannon3': (32.50, 42.00),
            'MG': (43.00, 52.50),
            'MG2': (43.00, 52.50),
            'MG3': (43.00, 52.50),
            'Missile_Launcher': (53.00, 62.50),
            'Missile_Launcher2': (53.00, 62.50),
            'Missile_Launcher3': (53.00, 62.50),
        }

        bullet_cost_ranges = {
            'Cannon': (0.10, 0.45),
            'Cannon2': (0.10, 0.45),
            'Cannon3': (0.10, 0.45),
            'MG': (0.46, 0.81),
            'MG2': (0.46, 0.81),
            'MG3': (0.46, 0.81),
            'Missile_Launcher': (0.82, 1.16),
            'Missile_Launcher2': (0.82, 1.16),
            'Missile_Launcher3': (0.82, 1.16),
        }

        building_cost_ranges = {
            'Factory': (125.00, 134.20),
            'Mine': (135.20, 144.4),
            'Warehouse': (145.4, 154.9),
        }

        # Generate random costs
        tower_costs = {tower: round(random.uniform(*tower_cost_ranges[tower]), 2) for tower in tower_cost_ranges}
        bullet_costs = {tower: round(random.uniform(*bullet_cost_ranges[tower]), 2) for tower in bullet_cost_ranges}
        building_costs = {building: round(random.uniform(*building_cost_ranges[building]), 2) for building in building_cost_ranges}

        # Create button data with dynamic costs
        button_data = [
            ('Cannon.png', tower_costs['Cannon'], bullet_costs['Cannon'], 1, None),
            ('Cannon2.png', tower_costs['Cannon2'], bullet_costs['Cannon2'], 2, None),
            ('Cannon3.png', tower_costs['Cannon3'], bullet_costs['Cannon3'], 4, None),
            ('MG.png', tower_costs['MG'], bullet_costs['MG'], 1, None),
            ('MG2.png', tower_costs['MG2'], bullet_costs['MG2'], 2, None),
            ('MG3.png', tower_costs['MG3'], bullet_costs['MG3'], 4, None),
            ('Missile_Launcher.png', tower_costs['Missile_Launcher'], bullet_costs['Missile_Launcher'], 1, None),
            ('Missile_Launcher2.png', tower_costs['Missile_Launcher2'], bullet_costs['Missile_Launcher2'], 2, None),
            ('Missile_Launcher3.png', tower_costs['Missile_Launcher3'], bullet_costs['Missile_Launcher3'], 4, None),
            ('factory.png', None, building_costs['Factory'], 1, r"Assets\PNG\Bullet_Cannon.png"),
            ('mine.png', None, building_costs['Mine'], 2, r"Assets\Icons\dollar.png"),
            ('warehouse.png', None, building_costs['Warehouse'], 4, r"Assets\Icons\box.png")
        ]

        # Initialize lists
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

            image, tower_cost, bullet_cost, multiplier, product = data
            if i < 9:
                button = GameSprites.PlayerButton(x, y, *BUTTON_SIZE, f'Assets/PNG/{image}', 50)
                button.cost_per_bullet = bullet_cost * multiplier
                button.tower_cost = tower_cost
                self.player_types_list.append(button)
            else:
                button = GameSprites.Building(x, y, *BUTTON_SIZE, f'Assets\Icons\{image}', 50, product)
                button.building_cost = bullet_cost
                self.building_type_list.append(button)
        
        image_button_eye = UI.ImageButton(85, 438, 50, 50, r"Assets/Icons/extra/eye.png")
        image_button_door = UI.ImageButton(25, 438, 50, 50, r"Assets\Icons/extra/logout.png")
        self.image_buttons_list.append(image_button_eye)
        self.image_buttons_list.append(image_button_door)

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

        for image_button in self.image_buttons_list:
            if image_button == self.image_buttons_list[0]:
                image_button.handle_event(event, r"Assets\Icons\extra\hidden.png")
                if image_button.clicked:
                    image_button.update_image(r"Assets\Icons\extra\hidden.png")
                self.show_bars = not(image_button.clicked)
                image_button.reset()
            else:
                image_button.handle_event(event, r"Assets\Icons\extra\logout(1).png")
                if image_button.clicked:
                    image_button.update_image(r"Assets\Icons\extra\logout.png")
                self.pause = image_button.clicked
                image_button.reset()