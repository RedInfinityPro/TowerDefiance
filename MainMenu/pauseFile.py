from Container.imports_library import *
from MainMenu.baseFile import *

class PauseMenu(BaseMenu):
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        super().__init__(screen, width, height)
        self.resume_game = True
        self.exit_to_main = False
        self._create_menus()
    
    def _create_menus(self):
        # Pause menu
        self.pause_menu = pygame_menu.Menu('Game Paused', self.width, self.height, theme=pygame_menu.themes.THEME_DARK)
        # Add pause menu buttons
        self.pause_menu.add.button('Play Game', self._resume)
        self.pause_menu.add.button('Settings', self._show_settings)
        self.pause_menu.add.button('Save Game', self._save_game)
        self.pause_menu.add.button('Main Menu', self._return_to_main)
        # Create settings menu
        self.settings_menu = self.create_settings_menu()
    
    def _resume(self):
        self.resume_game = True
    
    def _save_game(self):
        print("Game saved!")
    
    def _return_to_main(self):
        self.exit_to_main = True
        self.resume_game = True
    
    def _show_settings(self):
        self.pause_menu._open(self.settings_menu)
    
    def _get_pause_menu(self):
        return self.pause_menu
    
    def _reset_flags(self):
        self.resume_game = False
        self.exit_to_main = False
        self.quit_game = False