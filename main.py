import pygame
import random, sys, math, time
import pygame_menu
from pygame_menu import themes
# ---
import Menu, Map, GameSprites

pygame.init()
current_time = time.time()
random.seed(current_time)
# Seting up the display
screenWidth, screenHeight = 700, 700
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
pygame.display.set_caption("Tower Defince")
clock = pygame.time.Clock()
cell_size = 50

# color
def random_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128),
    "DARK_GRAY": (169, 169, 169),
    "GRAY": (128,128,128),
    "GOLD": (255,215,0)
}

# menu
# Function checked if the window is resized.
def on_resize() -> None:
    window_size = screen.get_size()
    new_w, new_h = window_size[0], window_size[1]
    menu.main_menu.resize(new_w, new_h)
    menu.loadGame_screen.resize(new_w, new_h)
    menu.settings_screen.resize(new_w, new_h)

menu = Menu.MainMenu(screen, screenWidth, screenHeight)
on_resize()

# sprites
enemies_timer = 0
spawn_interval = random.randint(100, 900)
def spawn_enemies(amount):
    global enemies_timer, spawn_interval
    enemies_timer += 1
    if enemies_timer % spawn_interval == 0:
        for i in range(random.randint(0, amount)):
            path_index = random.randint(0, len(list_paths) - 1)
            path = list_paths[path_index]
            ememy = GameSprites.Enemies(50, path.path_coordinates, random_color())
            GameSprites.enemies_list.add(ememy)

# ground
ground = Map.Ground(screenWidth, screenWidth, (cell_size,cell_size), colors['GREEN'])
list_paths = []
def add_paths(amount):
    for _ in range(random.randint(1, amount)):
        path = Map.Path(screenWidth, screenWidth, colors['DARK_GRAY'], colors['GRAY'], cell_size)
        path.make_path()
        list_paths.append(path)
add_paths(random.randint(1,3))

# player info
current_goods = 0
current_health, current_gold = 100, 100
max_health = 100
# panel
BUTTON_SIZE = (cell_size, cell_size)
panel = Menu.Panel(screen, screenWidth // 4, screenHeight, colors['WHITE'])

# Initialize game variables
building_clone_list = []
clones_list = []

# restart
def restart():
    global ground, list_paths, current_health, current_gold, clones_list
    global spawn_interval, building_clone_list

    GameSprites.enemies_list.empty()
    GameSprites.upgrade_list.empty()
    ground = Map.Ground(screenWidth, screenWidth, (cell_size, cell_size), colors['GREEN'])
    list_paths = []
    add_paths(random.randint(1,3))
    
    current_health, current_gold = 100, 100
    spawn_interval = random.randint(100, 900)
    clones_list = []
    building_clone_list = []

# main
restart_game = False
def main():
    global screen, current_health, current_gold, max_health, restart_game
    dragging_button = None
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                on_resize()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu.play = not(menu.play)
            # player button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for x, building_type in enumerate(panel.building_type_list):
                    if building_type.is_clicked(event.pos):
                        new_building = GameSprites.Building(event.pos[0],event.pos[1], BUTTON_SIZE[0], BUTTON_SIZE[1], building_type.image_path, cell_size, building_type.upgrade_image_path)
                        building_clone_list.append(new_building)
                        dragging_button = new_building
                        dragging_button.start_drag()

                for x, player_type in enumerate(panel.player_types_list):
                    if player_type.is_clicked(event.pos):
                        new_button = GameSprites.PlayerButton(event.pos[0],event.pos[1], BUTTON_SIZE[0], BUTTON_SIZE[1], player_type.image_path, cell_size)
                        clones_list.append(new_button)
                        dragging_button = new_button
                        dragging_button.start_drag()
            # stop dragging
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_button:
                    dragging_button.stop_drag()
                    dragging_button = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_button:
                    dragging_button.update_position(event.pos)
            # map
            if menu.play: 
                ground.handle_event(event) 
            # panel
            panel.handle_event(event)         
        screen.fill(colors["WHITE"])
        if not menu.play:
            menu.main_menu.update(events)
            menu.main_menu.draw(screen)
        # game
        if menu.play:
            # ground
            ground.draw(screen)
            for path in list_paths:
                path.draw(screen)

            # enemies
            spawn_enemies(100)
            GameSprites.enemies_list.update()
            GameSprites.enemies_list.draw(screen)
            for enemie in GameSprites.enemies_list:
                current_health = enemie.move(current_health)
            
            panel.create_panel()
            
            # buildings
            for building in building_clone_list:
                building.draw(screen)
                building.update()
                GameSprites.upgrade_list.update()
                GameSprites.upgrade_list.draw(screen)
            # clones 
            for button in clones_list:
                button.draw(screen)
                button.update_bullets()
                # bullets
                for bullet in button.bullets:
                    for enemy in GameSprites.enemies_list:
                        if bullet.colliderect(enemy):
                            if enemy.armor > 0:
                                enemy.armor -= 1
                            if enemy.armor <= 0:
                                enemy.health -= 1
                            if enemy.health <= 0:
                                GameSprites.enemies_list.remove(enemy)
                                button.bullets.remove(bullet)
                                current_gold += 0.02
                                break
            # circle
            for player in clones_list:
                circle_rect = pygame.Rect(player.rect.centerx - 50, player.rect.centery - 50, 200, 200)
                for sprite in GameSprites.enemies_list:
                    if circle_rect.colliderect(sprite):
                        player.rotate_to_face(sprite.rect.center, current_gold)
                        current_gold = player.shoot(current_gold)
                        break
            
            # exit
            if current_health <= 0:
                menu.play = False
                restart()
        # This is to update the scene
        clock.tick(64)
        pygame.display.flip()
        pygame.display.update()

# loop
if __name__ == "__main__":
    main()