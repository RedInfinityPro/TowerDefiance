import pygame

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
        self.textColor = (0, 0, 0)
        self.origional_textColor = self.textColor
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
                    self.textColor = self.active_color
                    self.color = self.active_color
        else:
            self.color = self.inactive_color
            self.textColor = self.origional_textColor

    def reset(self):
        self.clicked = False
        self.color = self.inactive_color
        self.textColor = self.origional_textColor