import pygame
import random, sys, time
from perlin_noise import PerlinNoise
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
current_time = time.time()
random.seed(current_time)

# ground
class Segment:
    def __init__(self, x, y, width, height, active_color, inactive_color):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.clicked = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.color = self.active_color
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True
        else:
            self.color = self.inactive_color

# map
class Ground:
    def __init__(self, screen_width, screen_height, cell_size, active_color):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.width = screen_width // self.cell_size[0]
        self.height = screen_height // self.cell_size[1]
        self.active_color = active_color
        self.freq = random.uniform(5, 30)
        self.amp = random.uniform(1, 15)
        self.octaves = random.randint(1, 6)
        self.seed = random.randint(0, sys.maxsize)
        self.water_threshold = random.uniform(0.0, 0.6)
        self.biome_type_list = round(random.uniform(0.3, 0.7))
        self.segmentList = []
        self.ground_data = self.generate_ground()
        self.build()

    def generate_ground(self):
        noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        detail_noise = PerlinNoise(octaves=self.octaves * 2, seed=self.seed // 2)
        ground_data = []

        for x in range(self.width):
            for y in range(self.height):
                cell_x = x * self.cell_size[0]
                cell_y = y * self.cell_size[1]
                base_height = noise([cell_x / self.freq, cell_y / self.freq])
                detail_height = detail_noise([cell_x / self.freq, cell_y / self.freq]) * 0.1
                cell_height = (base_height + detail_height) * self.amp

                brightness = (cell_height + self.amp) / (2 * self.amp)
                brightness = max(0, min(1, brightness))
                # adjust color base on height
                if cell_height < self.water_threshold:
                    biome_type = "water"
                else:
                    biome_type = self.get_biome_type(self.biome_type_list)

                color = self.get_biome_color(biome_type, brightness)
                ground_data.append([(cell_x, cell_y), cell_height, color])

        return ground_data
    
    def get_biome_type(self, height):
        if height < 0.3:
            return 'swamp'
        elif height < 0.4:
            return 'forest'
        elif height < 0.5:
            return 'grassland'
        elif height < 0.6:
            return 'desert'
        elif height < 0.7:
            return 'mountain'
        else:
            return 'snow'
    
    def get_biome_color(self, biome_type, brightness):
        if biome_type == 'water':
            color_value = int(brightness * 100)
            return (0, 0, max(0, min(255, color_value)))
        elif biome_type == 'grassland':
            color_value = int(brightness * 100) + random.randint(-10, 10)
            return (0, max(0, min(255, color_value)), 0)
        elif biome_type == 'mountain':
            color_value = int(brightness * 100) + random.randint(-10, 10)
            return (max(0, min(255, color_value)), max(0, min(255, color_value) - 50), max(0, min(255, color_value) - 100))
        elif biome_type == 'desert':
            base_color = (max(200, min(255, brightness * 255)), max(150, min(255, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'snow':
            base_color = (255, 255, 255)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'forest':
            base_color = (0, max(50, min(150, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
        elif biome_type == 'swamp':
            base_color = (max(0, min(100, brightness * 255)), max(100, min(200, brightness * 255)), 0)
            color_variation = random.randint(-10, 10)
            return tuple(max(0, min(255, c + color_variation)) for c in base_color)
    
    def build(self):
        for item in self.ground_data:
            cell_x, cell_y = item[0]
            color = item[2]
            segment_width = self.screen_width // self.width
            segment_height = self.screen_height // self.height

            self.segment = Segment(cell_x, cell_y, segment_width, segment_height, self.active_color, color)
            self.segmentList.append(self.segment)
    
    def draw(self, screen):
        for item in self.segmentList:
            item.draw(screen)

    def handle_event(self, event):
        for item in self.segmentList:
            item.handle_event(event)

# path
class Path:
    def __init__(self, width, height, bodyColor, edgeColor, cell_size):
        self.matrixWidth = width // cell_size
        self.matrixHeight = height // cell_size
        self.martix = []
        self.bodyColor = bodyColor
        self.edgeColor = edgeColor
        self.cell_size = cell_size
        self.path_rects = []
        self.grid = None
        self.start = None
        self.end = None
        self.path = None
        self.path_coordinates = []
        self.colliders = []

    def build_matrix(self):
        self.matrix = [[1] * self.matrixWidth for _ in range(self.matrixHeight)]
    
    def make_path(self):
        self.build_matrix()
        self.grid = Grid(matrix=self.matrix)

        # pick an edge
        start_edge = random.choice(['top','bottom','left','right'])
        if start_edge == 'top':
            self.start = self.grid.node(random.randint(0, self.matrixWidth - 1), 0)
        elif start_edge == 'bottom':
            self.start = self.grid.node(random.randint(0, self.matrixWidth - 1), self.matrixHeight - 1)
        elif start_edge == 'left':
            self.start = self.grid.node(0, random.randint(0, self.matrixHeight - 1))
        elif start_edge == 'right':
            self.start = self.grid.node(self.matrixWidth - 1, random.randint(0, self.matrixHeight - 1))
        
        # Determine the opposite edge for the end node
        if start_edge == 'top':
            self.end = self.grid.node(random.randint(0, self.matrixWidth - 1), self.matrixHeight - 1)
        elif start_edge == 'bottom':
            self.end = self.grid.node(random.randint(0, self.matrixWidth - 1), 0)
        elif start_edge == 'left':
            self.end = self.grid.node(self.matrixWidth - 1, random.randint(0, self.matrixHeight - 1))
        elif start_edge == 'right':
            self.end = self.grid.node(0, random.randint(0, self.matrixHeight - 1))
        
        self.finder = AStarFinder()
        self.path, self.runs = self.finder.find_path(self.start, self.end, self.grid)
        self.path_coordinates = [(node.x, node.y) for node in self.path]
        self.colliders = [pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size) for x, y in self.path_coordinates]

    def regenerate_path(self):
        self.make_path()
    
    def check_collision(self, obj_rect):
        for collider in self.colliders:
            if collider.colliderect(obj_rect):
                return True
        return False
    
    def draw(self, screen):
        for x, y in self.path_coordinates:
            pygame.draw.rect(screen, self.bodyColor, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
            pygame.draw.rect(screen, self.edgeColor, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size), 2)