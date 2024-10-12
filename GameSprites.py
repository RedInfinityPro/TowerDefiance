import pygame
import pygame.sprite
import random, sys, math, time
# -- handmade
import UI
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
    
    def scale_random_number(self, num, old_min=1, old_max=100, new_min=1.1, new_max=2.9):
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
class PlayerButton(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path, grid_size):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.original_image = self.image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.grid_size = grid_size
        self.dragging = False
        self.placed = False
        self.angle = 0
        self.bullet_image = pygame.transform.scale(pygame.image.load(r"Assets\PNG\Bullet_Cannon.png"), (10, 10))
        self.bullets = pygame.sprite.Group()
        self.cost_per_bullet = 0.10
        self.tower_cost = 32.50
        self.circle_radius = 100
        self.screen = None
        self.tool_tip = UI.Text(f"Tower ${self.tower_cost}, Bullet ${self.cost_per_bullet}", 23, (255, 255, 255), (self.rect.x, self.rect.y), (0, 0, 0))

    def draw(self, screen):
        self.screen = screen
        if self.dragging or self.placed:
            pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.circle_radius, 2)
        screen.blit(self.image, self.rect.topleft)
        self.bullets.draw(screen)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def start_drag(self):
        self.dragging = True

    def stop_drag(self):
        self.dragging = False
        self.placed = True
        # Snap to grid
        self.rect.topleft = (
            round(self.rect.left / self.grid_size) * self.grid_size,
            round(self.rect.top / self.grid_size) * self.grid_size
        )

    def update_position(self, pos):
        if not self.placed:
            if self.dragging:
                self.rect.topleft = pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2
                # Snap to grid for visual feedback while dragging
                self.rect.topleft = (
                    round(self.rect.left / self.grid_size) * self.grid_size,
                    round(self.rect.top / self.grid_size) * self.grid_size
                )

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
        if self.placed:
            if current_gold >= self.cost_per_bullet:
                current_gold -= self.cost_per_bullet
                bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle - 90, self.bullet_image)
                self.bullets.add(bullet)
        return current_gold

    def update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets:
            if bullet.time >= (self.circle_radius) / 10:
                self.bullets.remove(bullet)
    
    def colliderect(self, sprite):
        return self.rect.colliderect(sprite.rect)

    def handle_highlight(self):
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted = self.rect.collidepoint(mouse_pos)
        # f"Upgrade_cost ${self.upgrade_cost}, {self.building_cost}"
        if self.highlighted:
            self.tool_tip.update(f"Tower ${self.tower_cost}, Bullet ${self.cost_per_bullet}")
            self.tool_tip.render(self.screen)

# building
upgrade_list = pygame.sprite.Group()
product_list = pygame.sprite.Group()
class UpgradeIcon(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))
        self.start_y = y
        self.direction = 1

    def update(self):
        self.rect.y += self.direction
        if self.rect.y >= self.start_y + 10 or self.rect.y <= self.start_y - 10:
            self.direction *= -1
        
class Building(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path, grid_size, product_image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image_path = image_path
        self.grid_size = grid_size
        self.dragging = False
        self.placed = False
        self.level = 1
        self.timer = 0
        self.can_upgrade = False
        self.upgrade_icon = None
        self.product_icon = None
        self.upgrade_cost = 25
        self.building_cost = 125.00
        self.upgrade_image_path = r"Assets\Icons\up-arrow.png"
        self.product_image_path = product_image_path
        self.screen = None
        self.tool_tip = UI.Text(f"Upgrade ${self.upgrade_cost}, Building ${self.building_cost}", 23, (255, 255, 255), (self.rect.x, self.rect.y), (0, 0, 0))

    def draw(self, screen):
        self.screen = screen
        screen.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def start_drag(self):
        self.dragging = True

    def stop_drag(self):
        self.dragging = False
        self.placed = True
        self.snap_to_grid()

    def snap_to_grid(self):
        self.rect.topleft = (
            round(self.rect.left / self.grid_size) * self.grid_size,
            round(self.rect.top / self.grid_size) * self.grid_size
        )

    def update_position(self, pos):
        if not self.placed and self.dragging:
            self.rect.topleft = pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2
            self.snap_to_grid()

    def update(self):
        if self.can_upgrade:
            self.timer += 1
            # Produce product
            if self.timer % 900 == 0:
                if not self.product_icon:
                    self.product_icon = UpgradeIcon(self.rect.centerx, self.rect.centery - 50, 25, 25, self.product_image_path)
                    product_list.add(self.product_icon)
            # Upgrade
            if self.timer % 1800 == 0:
                if not self.upgrade_icon:
                    self.upgrade_icon = UpgradeIcon(self.rect.centerx, self.rect.centery - 50, 25, 25, self.upgrade_image_path)
                    upgrade_list.add(self.upgrade_icon)

    def handle_event(self, event, current_gold, current_goods):
        if self.can_upgrade:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    if self.upgrade_icon:
                        current_gold = self.upgrade(current_gold)
                    if self.product_icon:
                        current_goods = self.collect_product(current_goods)
        return current_gold, current_goods

    def handle_highlight(self):
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted = self.rect.collidepoint(mouse_pos)
        # f"Upgrade_cost ${self.upgrade_cost}, {self.building_cost}"
        if self.highlighted:
            self.tool_tip.update(f"Upgrade ${self.upgrade_cost}, Building ${self.building_cost}")
            self.tool_tip.render(self.screen)

    def upgrade(self, current_gold):
        if self.upgrade_icon:
            cost = self.upgrade_cost * self.level
            if current_gold >= cost:
                self.level += 1
                current_gold -= cost
                upgrade_list.remove(self.upgrade_icon)
                self.upgrade_icon = None
        return current_gold

    def collect_product(self, current_goods):
        if self.product_icon:
            current_goods += 5  # Adjust the amount collected as needed
            product_list.remove(self.product_icon)
            self.product_icon = None
        return current_goods