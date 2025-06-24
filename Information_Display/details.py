from Container.imports_library import *
from Information_Display.elements import*

class Details_Panel:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.details_panel = UIPanel(relative_rect=pygame.Rect((10, 10), (128, 85)), manager=self.ui_manager, starting_height=1)
        # day tracker
        self.month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.month, self.day, self.year = 0, 1, 2001
        self.speed_num = 1
        self.last_update_time = time.time()
        self.elapsed_time = 0
        self.day_length = 60
        self.pause = False
        self.change_day = True
        # resources
        self.money = 0
        self.energy = 0
        self.water = 0
        self.food = 0
        self.storage = 0
        # Max values for progress bars
        self.max_energy = 100
        self.max_water = 100
        self.max_food = 100
        self.max_storage = 100
        self._build()
    
    def _build(self):
        self.money_button = UIButton(relative_rect=pygame.Rect((8, 8), (100, 18)), manager=self.ui_manager, container=self.details_panel, text="Money: $0.00")
        self.date_label = UILabel(relative_rect=pygame.Rect((120, 8), (100, 18)), manager=self.ui_manager, container=self.details_panel, text="Jan 1, 2001")
        self.pause_button = UIButton(relative_rect=pygame.Rect((8, 30), (50, 22)), manager=self.ui_manager, container=self.details_panel, text="Pause", command=self._pause)
        self.speed_button = UIButton(relative_rect=pygame.Rect((62, 30), (70, 22)), manager=self.ui_manager, container=self.details_panel, text="Speed 1x", command=self._speed)
        # resource
        self.resource_panel = UIPanel(relative_rect=pygame.Rect((250, 0), (80, 85)), manager=self.ui_manager, container=self.details_panel)
        self.energy_label = UILabel(relative_rect=pygame.Rect((0, 0), (80, 18)), manager=self.ui_manager, container=self.resource_panel, text="Energy:")
        self.energy_bar = UIProgressBar(relative_rect=pygame.Rect((80, 0), (200, 18)), manager=self.ui_manager, container=self.resource_panel)
        self.water_label = UILabel(relative_rect=pygame.Rect((0, 18), (80, 18)), manager=self.ui_manager, container=self.resource_panel, text="Water:")
        self.water_bar = UIProgressBar(relative_rect=pygame.Rect((80, 18), (200, 18)), manager=self.ui_manager, container=self.resource_panel)
        self.food_label = UILabel(relative_rect=pygame.Rect((0, 36), (80, 18)), manager=self.ui_manager, container=self.resource_panel, text="Food:")
        self.food_bar = UIProgressBar(relative_rect=pygame.Rect((80, 36), (200, 18)), manager=self.ui_manager, container=self.resource_panel)
        self.storage_label = UILabel(relative_rect=pygame.Rect((0, 54), (80, 18)), manager=self.ui_manager, container=self.resource_panel, text="Storage:")
        self.storage_bar = UIProgressBar(relative_rect=pygame.Rect((80, 54), (200, 18)), manager=self.ui_manager, container=self.resource_panel)

    def _pause(self):
        self.pause = not(self.pause)
        if self.pause:
            self.pause_button.set_text("Play")
        else:
            self.pause_button.set_text("Pause")

    def _speed(self):
        if self.speed_num < 3:
            self.speed_num += 1
        else:
            self.speed_num = 1

    def update(self, screen: pygame.display):
        screenScale = screen.get_size()
        self.details_panel.set_dimensions((screenScale[0] - 20, 85))
        self.resource_panel.set_dimensions((screenScale[0] - 250, 85))
        # time
        current_time = time.time()
        delta = current_time - self.last_update_time
        self.last_update_time = current_time
        if not self.pause:
            self.elapsed_time += delta * (self.speed_num)
            if self.elapsed_time >= self.day_length:
                self.elapsed_time = 0
                self.day += 1
                if self.day > self.days_in_month[self.month]:
                    self.day = 1
                    self.month += 1
                    if self.month > 11:
                        self.month = 0
                        self.year += 1
        # format
        self.formatMoney = Format_Number(self.money)
        self.money_button.set_text(f"${self.formatMoney}")
        self.speed_button.set_text("Speed {speed}".format(speed=self.speed_num))
        self.date_label.set_text("{Month}: {Day}/{Year}".format(Month=self.month_list[self.month], Day=self.day, Year=self.year))

        if self.pause:
            pygame.draw.rect(screen, pygame.Color('red'), pygame.Rect(0, 0, screen.get_size()[0], screen.get_size()[1]), 4)