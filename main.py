from Container.imports_library import *
from MainMenu.menuFile import *
from MainMenu.pauseFile import *
from Information_Display.details import *
from Map.map import *
from Map.weather import *

# loop
def on_resize(screen: pygame.Surface, main_menu: Any, pause_menu: Any) -> None:
    window_size = screen.get_size()
    new_w, new_h = window_size[0], window_size[1]
    main_menu.main_menu.resize(new_w, new_h)
    main_menu.load_menu.resize(new_w, new_h)
    pause_menu.pause_menu.resize(new_w, new_h)

class PlayerCamera:
    def __init__(self, cameraPos: Tuple[float, float], cameraSpeed: float):
        self.cameraPos = cameraPos
        self.cameraSpeed = cameraSpeed
    
    def move_update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.cameraPos[1] -= self.cameraSpeed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.cameraPos[1] += self.cameraSpeed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.cameraPos[0] -= self.cameraSpeed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.cameraPos[0] += self.cameraSpeed

class Application:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower Defiance")
        self.screenWidth, self.screenHeight = 1280, 720
        self.clock = pygame.time.Clock()
        self.running = True
        self.main_map = True
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
        self.background_surface = pygame.Surface((self.screenWidth, self.screenHeight)).convert()
        self.ui_manager = UIManager((self.screenWidth, self.screenHeight), theme_path="Assets\design.json")
        # menu
        self.main_menu = MainMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.pause_menu = PauseMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.main_menu._get_main_menu()
        self.pause_menu._get_pause_menu()
        # game objects
        self.playerCamera = PlayerCamera(cameraPos=[0, 0], cameraSpeed=10)
        self.ground = Ground(screen_size=self.screen.get_size(), cell_size=(10, 10), active_color=pygame.Color("lime"))
        self.weather = Weather()
        self.gameOptions = GameOptions(ui_manager=self.ui_manager)
        self.details_panel = Details_Panel(ui_manager=self.ui_manager)
        
    def run(self):
        while self.running:
            time_delta = self.clock.tick(64) / 1000.0
            # Get input
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screenWidth, self.screenHeight = event.w, event.h
                    self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
                    self.background_surface = pygame.transform.scale(self.background_surface, (self.screenWidth, self.screenHeight))
                    on_resize(screen=self.screen, main_menu=self.main_menu, pause_menu=self.pause_menu)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.main_menu.play:
                            self.pause_menu.resume_game = not(self.pause_menu.resume_game)
                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.gameOptions.build_dropDownMenu:
                        self.selected_option = event.text
            self.ui_manager.update(time_delta)
            # handle event 
            if self.main_menu.play and self.pause_menu.resume_game:
                self.ui_manager.process_events(event)
                self.ground.handle_event(event=event)
            # menu
            if not self.main_menu.play or self.pause_menu.exit_to_main:
                self.main_menu.play = False
                self.pause_menu._reset_flags()
                self.main_menu.main_menu.update(events=events)
                self.main_menu.main_menu.draw(surface=self.screen)
            elif self.main_menu.play and not self.pause_menu.resume_game:
                self.pause_menu.pause_menu.update(events=events)
                self.pause_menu.pause_menu.draw(surface=self.screen)
            # play
            if self.main_menu.play and self.pause_menu.resume_game:
                self.screen.blit(self.background_surface, (0, 0))
                self.playerCamera.move_update()
                self.ground.draw(screen=self.screen)
                self.weather.draw(screen=self.screen, dt=time_delta)
                self.ui_manager.draw_ui(self.screen)
                # updates
                self.ground.move_camera(dx=self.playerCamera.cameraPos[0], dy=self.playerCamera.cameraPos[1])
                self.weather.update(elapsed_time=self.details_panel.elapsed_time, dt=time_delta)
                self.weather.set_pause_state(paused=self.details_panel.pause)
                self.gameOptions.update(screen=self.screen)
                self.details_panel.update(screen=self.screen, dt=time_delta)
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()
        pygame.quit()
        sys.exit()
    
if __name__ == "__main__":
    app = Application()
    app.run()