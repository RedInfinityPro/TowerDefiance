import pygame
import random, sys, time
from perlin_noise import PerlinNoise
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
current_time = time.time()
random.seed(current_time)
# ground
class Segment:
    def __init__(self, position, scale, active_color, inactive_color):
        self.x, self.y = position
        self.width, self.height = scale
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.origional_color = self.color
        self.clicked = False
        # day/night
        self.time = 0
        self.day_length = 60
        self.daytime, self.Dawn, self.night = 50, 100, 150
        self.amounttime = 5
    
    def draw(self, screen, camera_offset):
        screen_x, screen_y = self.x - camera_offset[0], self.y - camera_offset[1]
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))

    def handle_event(self, event, camera_offset):
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_x, adjusted_mouse_y = mouse_pos[0] + camera_offset[0], mouse_pos[1] + camera_offset[1]
        
        if (self.x < adjusted_mouse_x < self.x + self.width and 
            self.y < adjusted_mouse_y < self.y + self.height):
            self.color = self.active_color
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.clicked = True
        else:
            self.color = self.inactive_color

# map
class Ground:
    def __init__(self, screen_size, cell_size, active_color):
        self.screen_width, self.screen_height = screen_size
        self.cell_size = cell_size
        self.active_color = active_color
        # Noise parameters
        self.freq = random.uniform(5, 30)
        self.amp = random.uniform(1, 15)
        self.octaves = random.randint(1, 6)
        self.seed = random.randint(0, sys.maxsize)
        self.water_threshold = random.uniform(0.0, 0.6)
        self.biome_type_list = random.randint(0, 5)
        # Chunk management
        self.chunk_size = 16
        self.chunks = {}
        self.visible_chunks = {}
        # Camera position (center of the view)
        self.camera_x = 0
        self.camera_y = 0
        # Initialize noise generators
        self.noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        self.detail_noise = PerlinNoise(octaves=self.octaves * 2, seed=self.seed // 2)
        self.water_noise = PerlinNoise(octaves=2, seed=self.seed // 3)
        self.river_noise = PerlinNoise(octaves=1, seed=self.seed // 5)
        # Water generation parameters
        self.ocean_level = random.uniform(-0.7, -0.5)  # Lower values mean more ocean
        self.lake_threshold = random.uniform(0.7, 0.9)  # Higher values mean fewer lakes
        self.river_density = random.uniform(0.01, 0.03)  # Controls how many rivers appear
        self.river_width = random.uniform(0.01, 0.03) 

    def move_camera(self, dx, dy):
        """Move the camera by the given delta values"""
        self.camera_x += dx
        self.camera_y += dy
        self.update_visible_chunks()
    
    def set_camera_position(self, x, y):
        """Set the camera to an absolute position"""
        self.camera_x = x
        self.camera_y = y
        self.update_visible_chunks()

    def update_screen_size(self, new_screen_size):
        """Update the ground when screen size changes"""
        old_width, old_height = self.screen_width, self.screen_height
        self.screen_width, self.screen_height = new_screen_size
        
        # Calculate how the view changes based on the new screen size
        width_ratio = self.screen_width / old_width
        height_ratio = self.screen_height / old_height
        
        # Calculate how many more chunks need to be visible
        # This helps prevent sudden pop-in of new terrain when resizing
        width_change = (self.screen_width - old_width) // (self.chunk_size * self.cell_size[0])
        height_change = (self.screen_height - old_height) // (self.chunk_size * self.cell_size[1])
        
        # Log the screen size change
        #print(f"Screen size updated: {old_width}x{old_height} -> {self.screen_width}x{self.screen_height}")
        #print(f"Chunk visibility adjustment: width {width_change}, height {height_change}")
        
        # Update visible chunks based on new screen dimensions
        self.update_visible_chunks()
        
        # Return the ratios in case the camera position needs to be adjusted externally
        return width_ratio, height_ratio

    def get_chunk_key(self, chunk_x, chunk_y):
        """Generate a unique key for each chunk based on its coordinates"""
        return f"{chunk_x}:{chunk_y}"
    
    def get_visible_chunk_coordinates(self):
        """Calculate which chunks should be visible based on camera position"""
        # Calculate the range of chunks that should be visible
        chunk_width_in_pixels = self.chunk_size * self.cell_size[0]
        chunk_height_in_pixels = self.chunk_size * self.cell_size[1]
        
        # Extra chunks for smooth scrolling (render one more chunk in each direction)
        extra_chunks = 2
        
        # Calculate chunk coordinates for the camera's view area
        start_chunk_x = (self.camera_x - self.screen_width // 2) // chunk_width_in_pixels - extra_chunks
        start_chunk_y = (self.camera_y - self.screen_height // 2) // chunk_height_in_pixels - extra_chunks
        
        end_chunk_x = (self.camera_x + self.screen_width // 2) // chunk_width_in_pixels + extra_chunks
        end_chunk_y = (self.camera_y + self.screen_height // 2) // chunk_height_in_pixels + extra_chunks
        
        return [(x, y) for x in range(int(start_chunk_x), int(end_chunk_x) + 1) 
                        for y in range(int(start_chunk_y), int(end_chunk_y) + 1)]
    
    def update_visible_chunks(self):
        """Update which chunks are currently visible and generate new ones as needed"""
        visible_chunk_coords = self.get_visible_chunk_coordinates()
        
        # Clear the current visible chunks
        self.visible_chunks = {}
        
        for chunk_x, chunk_y in visible_chunk_coords:
            chunk_key = self.get_chunk_key(chunk_x, chunk_y)
            
            # Generate chunk if it doesn't exist yet
            if chunk_key not in self.chunks:
                self.chunks[chunk_key] = self.generate_chunk(chunk_x, chunk_y)
            
            # Add to visible chunks
            self.visible_chunks[chunk_key] = self.chunks[chunk_key]
        
        # Optional: Remove chunks that are far from view to save memory
        # This could be implemented with a distance threshold or a maximum cache size
    
    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a new chunk at the given coordinates"""
        chunk_segments = []
        
        # Calculate absolute pixel position of chunk's top-left corner
        chunk_pixel_x = chunk_x * self.chunk_size * self.cell_size[0]
        chunk_pixel_y = chunk_y * self.chunk_size * self.cell_size[1]
        
        for x in range(self.chunk_size):
            for y in range(self.chunk_size):
                # Calculate absolute cell position
                cell_x = chunk_pixel_x + x * self.cell_size[0]
                cell_y = chunk_pixel_y + y * self.cell_size[1]
                
                # Generate height value using noise
                base_height = self.noise([cell_x / self.freq, cell_y / self.freq])
                detail_height = self.detail_noise([cell_x / self.freq, cell_y / self.freq]) * 0.1
                cell_height = (base_height + detail_height) * self.amp
                
                # Calculate water features using separate noise maps
                water_value = self.water_noise([cell_x / (self.freq * 3), cell_y / (self.freq * 3)])
                river_value = self.river_noise([cell_x / (self.freq * 10), cell_y / (self.freq * 10)])
                
                # Calculate color based on height
                brightness = (cell_height + self.amp) / (2 * self.amp)
                brightness = max(0, min(1, brightness))
                
                # Determine biome type with improved water features
                biome_type = self.determine_biome_with_water(cell_height, water_value, river_value, cell_x, cell_y)
                
                color = self.get_biome_color(biome_type, brightness)
                
                # Create segment
                segment = Segment(
                    (cell_x, cell_y), 
                    (self.cell_size[0], self.cell_size[1]), 
                    self.active_color, color
                )
                chunk_segments.append(segment)
        
        return chunk_segments
    
    def determine_biome_with_water(self, height, water_value, river_value, x, y):
        """Determine the biome type with improved water feature generation"""
        # Ocean generation - large bodies of water at low elevations
        if height < self.ocean_level:
            return 'ocean'
        
        # Lake generation - smaller bodies of water that form in depressions
        if water_value > self.lake_threshold and height < 0:
            return 'lake'
        
        # River generation - flowing water that follows noise patterns
        river_noise_mod = abs(river_value) % 1.0
        if river_noise_mod < self.river_density and self.is_river_path(x, y, river_value):
            return 'river'
        
        # Regular biome determination for land
        return self.get_biome_type(self.biome_type_list)
    
    def is_river_path(self, x, y, river_value):
        """Determine if this location should be part of a river"""
        # Calculate flow direction based on the gradient of the river noise
        gradient_x = self.river_noise([x / (self.freq * 10) + 0.01, y / (self.freq * 10)]) - river_value
        gradient_y = self.river_noise([x / (self.freq * 10), y / (self.freq * 10) + 0.01]) - river_value
        
        # Normalize the gradient
        length = max(0.001, (gradient_x**2 + gradient_y**2)**0.5)
        gradient_x /= length
        gradient_y /= length
        
        # Project the position onto the flow direction
        projection = (x * gradient_x + y * gradient_y) / (self.freq * 10)
        
        # Create a sine wave along the flow direction to make a winding river
        winding = math.sin(projection * 50) * self.river_width
        
        # Check if point is within the river width
        return abs(winding) < self.river_width
    
    def get_biome_color(self, biome_type, brightness):
        if biome_type == 'ocean':
            depth_factor = max(0.2, min(0.9, brightness * 1.5))
            return (0, 0, int(120 + 135 * depth_factor))
        elif biome_type == 'lake':
            depth_factor = max(0.4, min(1.0, brightness * 1.3))
            return (0, int(70 * depth_factor), int(180 * depth_factor))
        elif biome_type == 'river':
            depth_factor = max(0.5, min(1.0, brightness * 1.2))
            return (0, int(100 * depth_factor), int(200 * depth_factor))
        elif biome_type == 'water':  # Legacy water type
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
    
    def get_biome_type(self, height):
        if height < 1:
            return 'swamp'
        elif height < 2:
            return 'forest'
        elif height < 3:
            return 'grassland'
        elif height < 4:
            return 'desert'
        elif height < 5:
            return 'mountain'
        else:
            return 'snow'
    
    def draw(self, screen):
        """Draw all visible chunks"""
        # Calculate camera offset for drawing
        camera_offset_x = self.camera_x - self.screen_width // 2
        camera_offset_y = self.camera_y - self.screen_height // 2
        
        # Draw each segment in each visible chunk
        for chunk_segments in self.visible_chunks.values():
            for segment in chunk_segments:
                segment.draw(screen, (camera_offset_x, camera_offset_y))
    
    def handle_event(self, event):
        """Handle events for all visible segments"""
        camera_offset_x = self.camera_x - self.screen_width // 2
        camera_offset_y = self.camera_y - self.screen_height // 2
        
        for chunk_segments in self.visible_chunks.values():
            for segment in chunk_segments:
                segment.handle_event(event, (camera_offset_x, camera_offset_y))\

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
