from Container.imports_library import *
from MainMenu.menuFile import *
from MainMenu.pauseFile import *
from Information_Display.details import *
from Map.map import *

def on_resize(screen: pygame.Surface, main_menu, pause_menu) -> None:
    window_size = screen.get_size()
    new_w, new_h = window_size[0], window_size[1]
    main_menu.main_menu.resize(new_w, new_h)
    main_menu.load_menu.resize(new_w, new_h)
    pause_menu.pause_menu.resize(new_w, new_h)

def MoveCamera(cameraPos, speed):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        cameraPos[1] -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        cameraPos[1] += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        cameraPos[0] -= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        cameraPos[0] += speed

class Application:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower Defiance")
        self.screenWidth, self.screenHeight = 1280, 720
        self.clock = pygame.time.Clock()
        self.running = True
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
        self.background_surface = pygame.Surface((self.screenWidth, self.screenHeight)).convert()
        self.ui_manager = UIManager((self.screenWidth, self.screenHeight))
        # menu
        self.main_menu = MainMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.pause_menu = PauseMenu(screen=self.screen, width=self.screenWidth, height=self.screenHeight)
        self.main_menu.get_main_menu()
        self.pause_menu.get_pause_menu()
        # details
        self.details_panel = Details_Panel(ui_manager=self.ui_manager)
        self.ground = Ground(screen_size=self.screen.get_size(), cell_size=(10, 10), active_color=pygame.Color("lime"))
        self.weather = Weather()
        self.cameraPos = [0, 0]
        self.cameraSpeed = 10

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
                self.ui_manager.process_events(event)
                self.ground.handle_event(event)
            # menu
            if not self.main_menu.play or self.pause_menu.exit_to_main:
                self.main_menu.play = False
                self.pause_menu.reset_flags()
                self.main_menu.main_menu.update(events)
                self.main_menu.main_menu.draw(self.screen)
            elif self.main_menu.play and not self.pause_menu.resume_game:
                self.pause_menu.pause_menu.update(events)
                self.pause_menu.pause_menu.draw(self.screen)
            else:
                self.screen.blit(self.background_surface, (0, 0))
                # ground
                MoveCamera(cameraPos=self.cameraPos, speed=self.cameraSpeed)
                self.ground.draw(screen=self.screen)
                self.ground.move_camera(dx=self.cameraPos[0], dy=self.cameraPos[1])
                # weather
                self.weather.draw(screen=self.screen)
                # more
                self.ui_manager.draw_ui(self.screen)
            self.ui_manager.update(time_delta)
            self.details_panel.update(screen=self.screen)
            self.weather.update(elapsed_time=self.details_panel.elapsed_time)
            self.clock.tick(64)
            pygame.display.flip()
            pygame.display.update()
        pygame.quit()
        sys.exit()
    
if __name__ == "__main__":
    app = Application()
    app.run()