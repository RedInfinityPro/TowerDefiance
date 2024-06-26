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

class Text:
    def __init__(self, text, font_size, color, position, bg_color=None):
        self.text = text
        self.font_size = font_size
        self.color = color
        self.position = position
        self.bg_color = bg_color
        self.font = pygame.font.Font(None, self.font_size)  # You can specify a font file or use None for default font
        self.rendered_text = None
        self.text_rect = None

    def update(self, new_text):
        self.text = new_text
        self.rendered_text = None  # Clear the rendered text to update it
        self.text_rect = None

    def render(self, screen):
        if self.rendered_text is None or self.text_rect is None:
            self.rendered_text = self.font.render(self.text, True, self.color)
            self.text_rect = self.rendered_text.get_rect(topleft=self.position)
        
        if self.bg_color:
            # Calculate the background rectangle size
            bg_rect = pygame.Rect(
                self.text_rect.x - self.text_rect.width // 2,
                self.text_rect.y - self.text_rect.height // 2,
                self.text_rect.width * 2,
                self.text_rect.height * 2
            )
            pygame.draw.rect(screen, self.bg_color, bg_rect)
        
        screen.blit(self.rendered_text, self.position)

# image button
class ImageButton:
    def __init__(self, x, y, width, height, image_path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.origional_Image = image_path 
        self.image_path = image_path
        self.load_image()
        self.clicked = False
        self.highlighted = False

    def load_image(self):
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_image(self, new_image_path):
        self.image_path = new_image_path
        self.load_image()

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def handle_event(self, event, new_image_path):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.clicked = not(self.clicked)
        self.handle_highlight(new_image_path)

    def handle_highlight(self, new_image_path):
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted = self.rect.collidepoint(mouse_pos)
        if self.highlighted:
            self.update_image(new_image_path)
        else:
            self.update_image(self.origional_Image)

    def reset(self):
        self.highlighted = False