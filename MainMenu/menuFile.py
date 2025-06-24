from Container.imports_library import *
from MainMenu.baseFile import *

class MainMenu(BaseMenu):
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        super().__init__(screen, width, height)
        self.play = False
        self.selected_save_slot = None
        self._create_menus()
    
    def _create_menus(self):
        # Main menu
        self.main_menu = pygame_menu.Menu('Tower Defiance', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        self.load_menu = pygame_menu.Menu('Load Game', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add main menu buttons
        self.main_menu.add.button('Play Game', self._start_game)
        self.main_menu.add.button('Load Game', self._show_load_menu)
        self.main_menu.add.button('Settings', self._show_settings)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)
        # Create sub-menus
        self.load_menu = self._create_load_menu()
        self.settings_menu = self.create_settings_menu()
    
    def _create_load_menu(self):
        self.load_menu.clear()
        for i in range(1, 11):
            self.load_menu.add.button(f'Save Slot {i}', lambda slot=i: self._load_game(slot))
        self.load_menu.add.button('Return to Main Menu', pygame_menu.events.BACK)
        return self.load_menu
    
    def _start_game(self):
        self.play = True
    
    def _load_game(self, slot_number: int):
        self.selected_save_slot = slot_number
        self.play = True
        print(f"Loading game from slot {slot_number}")
    
    def _show_load_menu(self):
        self.main_menu._open(self.load_menu)
    
    def _show_settings(self):
        self.main_menu._open(self.settings_menu)
    
    def _get_main_menu(self):
        return self.main_menu