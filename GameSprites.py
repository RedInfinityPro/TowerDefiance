import pygame
import pygame.sprite
import random, sys, math, time

# enemies
enemies_list = pygame.sprite.Group()
class Enemies(pygame.sprite.Sprite):
    def __init__(self, cell_size, path_coordinates, color):
        pygame.sprite.Sprite.__init__(self)
        self.cell_size = cell_size
        self.path_coordinates = path_coordinates
        self.index = 0
        self.x, self.y = path_coordinates[self.index]
        self.color = color
        self.identify = self.DNA()

        # Make the enemy size relative to the cell size
        radius = self.cell_size // 3
        self.image = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(self.x * self.cell_size + radius, self.y * self.cell_size + radius))
    
    def normalize(self, value, old_min=1, old_max=255, new_min=1, new_max=100):
        normalized_value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        return normalized_value
    
    def scale_random_number(self, num, old_min=1, old_max=100, new_min=1.1, new_max=1.9):
        # Scale the number from the old range to the new range
        scaled_value = ((num - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        return scaled_value

    def DNA(self):
        self.health = self.normalize(self.color[0])
        self.origional_health = self.health
        self.armor = self.normalize(self.color[1])
        self.speed = self.scale_random_number(self.normalize(self.color[2]))

    def move(self, current_health):
        if self.index < len(self.path_coordinates):
            target_x, target_y = self.path_coordinates[self.index]
            target_x = target_x * self.cell_size + (self.cell_size // 2) + self.cell_size / 5
            target_y = target_y * self.cell_size + (self.cell_size // 2) + self.cell_size / 5

            if self.rect.centerx > target_x:
                self.rect.centerx -= int(1 * self.speed)
            elif self.rect.centerx < target_x:
                self.rect.centerx += int(1 * self.speed)

            if self.rect.centery > target_y:
                self.rect.centery -= int(1 * self.speed)
            elif self.rect.centery < target_y:
                self.rect.centery += int(1 * self.speed)

            threshold = 1
            if abs(self.rect.centerx - target_x) <= threshold and abs(self.rect.centery - target_y) <= threshold:
                self.index += 1
                if self.index >= len(self.path_coordinates):
                    enemies_list.remove(self)
                    self.kill()
                    current_health -= 1
        return current_health

# bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, image):
        super().__init__()
        self.image = pygame.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center=(x,y))
        self.angle = angle
        self.speed = 10
        self.time = 0
    
    def update(self):
        rad_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(rad_angle)
        self.rect.y += self.speed * math.sin(rad_angle)
        self.time += 1

    def colliderect(self, sprite):
        return self.rect.colliderect(sprite.rect)

# player buttons
class PlayerButton:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.original_image = self.image
        self.dragging = False
        self.placed = False
        self.angle = 0
        self.bullet_image = pygame.transform.scale(pygame.image.load(r"Assets\PNG\Bullet_Cannon.png"), (10, 10))
        self.bullets = pygame.sprite.Group()
        self.cost_per_bullet = 0.10
        self.tower_cost = 32.50
    
    def draw(self, screen):
        if self.dragging or self.placed:
            pygame.draw.circle(screen, (0,0,0), self.rect.center, 100, 2)
        screen.blit(self.image, self.rect.topleft)
        self.bullets.draw(screen)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def start_drag(self, ):
        self.dragging = True

    def stop_drag(self):
        self.dragging = False
        self.placed = True

    def update_position(self, pos):
        if not self.placed:
            if self.dragging:
                self.rect.topleft = pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2
                
    def rotate_to_face(self, target_pos, current_gold):
        if self.placed:
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            self.angle = math.degrees(math.atan2(dy, dx)) + 90

            # Rotate the original image and update the rect
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.shoot(current_gold)
    
    def shoot(self, current_gold):
        if self.placed and current_gold >= self.cost_per_bullet:
            current_gold -= self.cost_per_bullet
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle - 90, self.bullet_image)
            self.bullets.add(bullet)
        return current_gold
    
    def update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets:
            if bullet.time >= 10:
                self.bullets.remove(bullet)
