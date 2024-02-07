import pygame
import sys
import random
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
# bar
class Bar:
    def __init__(self, x,y, width, height, color, outline_path, icon_path, max_value,current_value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.outline_path = outline_path
        self.icon_path = icon_path
        self.max_value = max_value
        self.current_value = current_value
        self.load_image()
        self.image = pygame.Surface((self.width, self.height))
        self.font = pygame.font.Font(None, 24)

    def load_image(self):
        self.image1 = pygame.image.load(self.outline_path)
        self.image1 = pygame.transform.scale(self.image1, (self.width, self.height))
        self.rect1 = self.image1.get_rect(topleft=(self.x + (self.width/5), self.y))
        self.image2 = pygame.image.load(self.icon_path)
        self.image2 = pygame.transform.scale(self.image2, (self.width / 2, self.height))
        self.rect2 = self.image2.get_rect(topleft=(self.x, self.y))
    
    def draw(self, screen):
        inner_width = (self.width - 2 * (self.width // 20)) * (self.current_value / self.max_value)
        pygame.draw.rect(screen, self.color, (self.x + (self.width // 4), self.y + 10, inner_width, self.height - 19))
        screen.blit(self.image1, self.rect1.topleft)
        screen.blit(self.image2, self.rect2.topleft)
        # Render text
        text_surface = self.font.render(f'{self.current_value}/{self.max_value}', True, (255, 255, 255))  # Change color as needed
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height + 10))
        screen.blit(text_surface, text_rect)
        
    def update(self, subtract):
        if self.current_value > 0:
            self.current_value -= subtract
            if self.current_value < 0:
                self.current_value = 0
# load slots button
class LoadSlotButton:
    def __init__(self, screen, x, y, width, height, color, text, seed_number, hover_color):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.seed_number = seed_number
        self.textColor = BLACK
        self.is_hovered = False

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        button_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(self.screen, button_color, self.rect)
        font = pygame.font.Font(None, 30)
        text_surface = font.render(self.text, True, self.textColor)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def is_clicked(self, mouse_pos):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        return self.rect.collidepoint(mouse_pos) and mouse_click[0] == 1
# pop up
class Popup:
    def __init__(self, screen, message, x, y, width, height, background_color, text_color, duration_ms=6000):
        self.screen = screen
        self.message = message
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_color = background_color
        self.text_color = text_color
        self.duration_ms = duration_ms

        self.font = pygame.font.Font(None, 36)
        self.start_time = pygame.time.get_ticks()

    def draw(self):
        pygame.draw.rect(self.screen, self.background_color, (self.x, self.y, self.width, self.height))
        text_surface = self.font.render(self.message, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        self.screen.blit(text_surface, text_rect)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration_ms:
            return True  # Signal that the popup should be removed
        return False

    def reset(self):
        self.start_time = pygame.time.get_ticks()
