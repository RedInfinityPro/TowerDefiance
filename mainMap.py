import pygame
import sys

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
