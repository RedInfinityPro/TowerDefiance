from Container.imports_library import *

# weather
class Weather:
    def __init__(self):
        self.time = 0  # Represents in-game time (0-24 hours)
        self.day_length = 60  # Seconds for a full day
        self.weather_types = ["clear", "overcast", "snowstorm", "fog", "rain", "snow"]
        self.current_weather = random.choice(self.weather_types)
        self.weather_timer = time.time() + random.randint(10, 30)  # Next weather change
        self.update_weather_values()

    def update_weather_values(self):
        base_temp = 75
        variation = 1.5
        self.current_temperature = round(random.uniform(base_temp - variation, base_temp + variation), 2)
        # Wind speeds
        self.wind_speed = round(random.uniform(5, 30), 2)
        self.wind_direction = random.choice(["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"])
        # Special effects for different weather types
        if self.current_weather == "rain":
            self.visibility = round(random.uniform(5, 20), 1)
        elif self.current_weather == "snow":
            self.visibility = round(random.uniform(2, 10), 1)
        elif self.current_weather == "snowstorm":
            self.visibility = round(random.uniform(1, 5), 1)
        elif self.current_weather == "fog":
            self.visibility = round(random.uniform(3, 8), 1)
        else:
            self.precipitation_type = "none"
            self.visibility = round(random.uniform(20, 100), 1)

    def _get_lighting(self):
        if 6 <= self.time < 18:  # Daytime
            return (255, 255, 255, 50)  # Light overlay
        elif 18 <= self.time < 21 or 3 <= self.time < 6:  # Dawn/Dusk
            return (50, 50, 100, 100)  # Dark blue tint
        else:  # Night
            return (0, 0, 25, 150)  # Dark overlay

    def draw(self, screen: pygame.Surface):
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self._get_lighting())  # Apply lighting
        screen.blit(overlay, (0, 0))

        if self.current_weather == "snowstorm":
            for _ in range(100):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (220, 240, 255), (x, y), random.uniform(0.1, 0.3))
        elif self.current_weather == "rain":
            for _ in range(80):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.line(screen, (100, 150, 220), (x, y), (x + random.uniform(-2, 2), y + 10), 2)
        elif self.current_weather == "snow":
            for _ in range(70):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (200, 225, 255), (x, y), random.uniform(0.2, 0.4))
        elif self.current_weather == "fog":
            fog_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fog_overlay.fill((180, 180, 220, 120))
            screen.blit(fog_overlay, (0, 0))
            # Add swirling fog particles
            for _ in range(30):
                x, y = random.randint(0, screen.get_width()), random.randint(0, screen.get_height())
                pygame.draw.circle(screen, (200, 200, 240, 60), (x, y), random.uniform(0.10, 0.30))

    def update(self, elapsed_time: float):
        self.time = elapsed_time or (time.time() % self.day_length) / self.day_length * 24
        if self.time > self.weather_timer:
            self.current_weather = random.choice(self.weather_types)
            self.update_weather_values()  # Refresh weather data
            self.weather_timer = self.time + random.randint(15, 45)
    
class Segment:
    def __init__(self, position: Tuple[float, float], scale: Tuple[float, float], biome_type: str, active_color: pygame.Color, inactive_color: pygame.Color):
        self.x, self.y = position
        self.width, self.height = scale
        self.biome_type = biome_type
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.original_color = self.color
        self.clicked = False

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        screen_x, screen_y = self.x - camera_offset[0], self.y - camera_offset[1]
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))

    def handle_event(self, event: Any, camera_offset: Tuple[float, float]):
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_x = mouse_pos[0] + camera_offset[0]
        adjusted_mouse_y = mouse_pos[1] + camera_offset[1]
        in_bounds = self.x < adjusted_mouse_x < self.x + self.width and self.y < adjusted_mouse_y < self.y + self.height
        self.color = self.active_color if in_bounds else self.inactive_color
        if in_bounds and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.clicked = True

class Ground:
    def __init__(self, screen_size: pygame.Surface, cell_size: Tuple[float, float], active_color: pygame.Color):
        self.screen_width, self.screen_height = screen_size
        self.cell_size = cell_size
        self.active_color = active_color
        self.chunk_size = 32
        self.camera_x = 0
        self.camera_y = 0
        self.chunks = {}
        self.visible_chunks = {}
        # Terrain generation parameters
        self.continent_scale = random.uniform(1, 1000)   # Large scale for continent shapes
        self.elevation_scale = random.uniform(1, 1000)   # Medium scale for elevation
        self.detail_scale = 50.0                         # Fine detail scale
        self.temperature_scale = random.uniform(1, 1000)  # Temperature variation scale
        self.humidity_scale = random.uniform(1, 1000)     # Humidity variation scale
        self.seed = random.randint(0, sys.maxsize)
        # Multiple noise layers for realistic terrain
        self.continent_noise = PerlinNoise(octaves=3, seed=self.seed)        # Large landmasses
        self.elevation_noise = PerlinNoise(octaves=6, seed=self.seed // 2)   # Elevation details
        self.temperature_noise = PerlinNoise(octaves=4, seed=self.seed // 3) # Temperature zones
        self.humidity_noise = PerlinNoise(octaves=4, seed=self.seed // 4)    # Rainfall patterns
        self.river_noise = PerlinNoise(octaves=2, seed=self.seed // 5)       # River systems
        # Biome thresholds - adjusted for coherent landmasses
        self.sea_level = 0.0          # Base sea level
        self.continental_threshold = -0.1  # Minimum height for land
        self.mountain_threshold = 0.4      # Height for mountains
        self.hill_threshold = 0.2          # Height for hills
        # Water feature parameters
        self.lake_threshold = 0.7
        self.river_density = 0.008    # Reduced for more realistic rivers
        self.river_width = 0.015
        # Climate zones
        self.arctic_temp = -0.4
        self.temperate_temp = 0.2
        self.tropical_temp = 0.5
        self.arid_humidity = -0.2
        self.moderate_humidity = 0.2
        self.wet_humidity = 0.5

    def _get_chunk_key(self, x: float, y: float): 
        return f"{x}:{y}"

    def update_visible_chunks(self):
        extra = 1
        chunk_px = self.chunk_size * self.cell_size[0]
        start_x = (self.camera_x - self.screen_width // 2) // chunk_px - extra
        start_y = (self.camera_y - self.screen_height // 2) // chunk_px - extra
        end_x = (self.camera_x + self.screen_width // 2) // chunk_px + extra
        end_y = (self.camera_y + self.screen_height // 2) // chunk_px + extra
        self.visible_chunks.clear()
        for cx in range(int(start_x), int(end_x)+1):
            for cy in range(int(start_y), int(end_y)+1):
                key = self._get_chunk_key(cx, cy)
                if key not in self.chunks:
                    self.chunks[key] = self._generate_chunk(cx, cy)
                self.visible_chunks[key] = self.chunks[key]

    def _generate_chunk(self, cx: float, cy: float):
        chunk_segments = []
        chunk_start_x = cx * self.chunk_size * self.cell_size[0]
        chunk_start_y = cy * self.chunk_size * self.cell_size[1]
        for x in range(self.chunk_size):
            for y in range(self.chunk_size):
                px = chunk_start_x + x * self.cell_size[0]
                py = chunk_start_y + y * self.cell_size[1]
                # Get terrain data for this position
                terrain_data = self._get_terrain_data(px, py)
                # Determine biome based on comprehensive terrain analysis
                biome = self._determine_biome_comprehensive(terrain_data, px, py)
                # Calculate brightness based on elevation and biome
                brightness = self._calculate_brightness(terrain_data, biome)
                # Get biome color with coherent shading
                color = self._get_biome_color(biome, brightness, terrain_data)
                segment = Segment((px, py), self.cell_size, biome, self.active_color, color)
                chunk_segments.append(segment)
        return chunk_segments

    def _get_terrain_data(self, x: float, y: float):
        # Normalize coordinates for different scales
        continent_coords = [x / self.continent_scale, y / self.continent_scale]
        elevation_coords = [x / self.elevation_scale, y / self.elevation_scale]
        temperature_coords = [x / self.temperature_scale, y / self.temperature_scale]
        humidity_coords = [x / self.humidity_scale, y / self.humidity_scale]
        # Generate base terrain values
        continent_shape = self.continent_noise(continent_coords)
        base_elevation = self.elevation_noise(elevation_coords)
        # Combine continent shape with elevation for realistic landmasses
        # Continental shelf effect - land tends to be higher than ocean floor
        if continent_shape > self.continental_threshold:
            # On land - elevation is modified by continental shape
            final_elevation = base_elevation * 0.7 + continent_shape * 0.3
            # Boost land elevation to keep it above sea level
            final_elevation = max(0.05, final_elevation + 0.1)
        else:
            # In ocean - deeper based on distance from continental shelf
            ocean_depth = (self.continental_threshold - continent_shape) * 0.5
            final_elevation = base_elevation * 0.3 - ocean_depth
        # Temperature influenced by latitude (y-coordinate) and elevation
        base_temperature = self.temperature_noise(temperature_coords)
        latitude_effect = math.sin(y / 2000.0) * 0.4  # Simulate latitude temperature variation
        elevation_cooling = max(0, final_elevation - 0.2) * -0.8  # Higher = colder
        final_temperature = base_temperature + latitude_effect + elevation_cooling
        # Humidity patterns
        base_humidity = self.humidity_noise(humidity_coords)
        # Coastal areas tend to be more humid
        coastal_effect = 0
        if continent_shape > self.continental_threshold - 0.1:  # Near coastline
            coastal_effect = 0.2
        final_humidity = base_humidity + coastal_effect
        
        return {
            'continent_shape': continent_shape,
            'elevation': final_elevation,
            'temperature': final_temperature,
            'humidity': final_humidity,
            'is_land': continent_shape > self.continental_threshold
        }

    def _determine_biome_comprehensive(self, terrain_data: Any, x: float, y: float):
        """Determine biome using comprehensive terrain analysis"""
        elevation = terrain_data['elevation']
        temperature = terrain_data['temperature']
        humidity = terrain_data['humidity']
        is_land = terrain_data['is_land']
        # Water biomes first
        if not is_land:
            if elevation < -0.3:
                return 'deep_ocean'
            elif elevation < -0.1:
                return 'ocean'
            else:
                return 'shallow_water'
        # Check for freshwater features on land
        water_biome = self._check_freshwater_features(x, y, elevation, humidity)
        if water_biome:
            return water_biome
        # Land biomes based on temperature and humidity
        if temperature < self.arctic_temp:
            # Arctic climates
            if elevation > self.mountain_threshold:
                return 'glacier'
            elif humidity > self.moderate_humidity:
                return 'tundra_wet'
            else:
                return 'tundra_dry'
        elif temperature < self.temperate_temp:
            # Cold temperate climates
            if elevation > self.mountain_threshold:
                return 'alpine'
            elif elevation > self.hill_threshold:
                if humidity > self.wet_humidity:
                    return 'montane_forest'
                else:
                    return 'rocky_hills'
            elif humidity > self.wet_humidity:
                return 'boreal_forest'
            elif humidity > self.moderate_humidity:
                return 'mixed_forest'
            else:
                return 'cold_grassland'
        elif temperature < self.tropical_temp:
            # Temperate climates
            if elevation > self.mountain_threshold:
                return 'mountain_peak'
            elif elevation > self.hill_threshold:
                if humidity > self.moderate_humidity:
                    return 'temperate_forest'
                else:
                    return 'scrubland'
            elif humidity > self.wet_humidity:
                return 'deciduous_forest'
            elif humidity > self.moderate_humidity:
                return 'grassland'
            elif humidity > self.arid_humidity:
                return 'prairie'
            else:
                return 'semi_desert'
        
        else:
            # Tropical/hot climates
            if elevation > self.mountain_threshold:
                return 'tropical_mountain'
            elif humidity > self.wet_humidity:
                return 'tropical_rainforest'
            elif humidity > self.moderate_humidity:
                return 'tropical_forest'
            elif humidity > self.arid_humidity:
                return 'savanna'
            else:
                return 'hot_desert'

    def _check_freshwater_features(self, x: float, y: float, elevation: float, humidity: float):
        """Check for lakes and rivers"""
        # Lakes in depressions with sufficient humidity
        if elevation < 0.15 and humidity > self.lake_threshold:
            return 'lake'
        # Rivers using improved flow-based generation
        river_value = self.river_noise([x / (self.elevation_scale * 2), y / (self.elevation_scale * 2)])
        if abs(river_value % 1.0) < self.river_density and self._is_river_path(x, y, river_value):
            return 'river'
        # Wetlands in low-lying humid areas
        if elevation < 0.1 and humidity > 0.4:
            return 'wetlands'
        return None

    def _is_river_path(self, x: float, y: float, river_value: float):
        """Enhanced river path detection"""
        scale = self.elevation_scale * 2
        dx = self.river_noise([x / scale + 1, y / scale]) - river_value
        dy = self.river_noise([x / scale, y / scale + 1]) - river_value
        length = max(0.001, (dx**2 + dy**2)**0.5)
        flow_x, flow_y = dx / length, dy / length
        # Create more natural winding
        flow_distance = (x * flow_x + y * flow_y) / scale
        winding = math.sin(flow_distance * 20) * self.river_width * 0.8
        base_width = self.river_width * (0.5 + 0.5 * abs(river_value))
        return abs(winding) < base_width

    def _calculate_brightness(self, terrain_data: Any, biome: str):
        elevation = terrain_data['elevation']
        # Base brightness from elevation
        if biome in ['deep_ocean', 'ocean', 'shallow_water']:
            # Water gets darker with depth
            brightness = max(0.3, min(0.8, 0.6 + elevation * 0.4))
        else:
            # Land brightness varies with elevation
            brightness = max(0.4, min(1.0, 0.5 + elevation * 0.5))
        # Biome-specific brightness adjustments
        if 'desert' in biome:
            brightness = min(1.0, brightness * 1.2)  # Deserts are brighter
        elif 'forest' in biome:
            brightness *= 0.8  # Forests are darker
        elif 'mountain' in biome or 'alpine' in biome:
            brightness = min(1.0, brightness * 1.1)  # Mountains catch more light
        return brightness

    def _get_biome_color(self, biome: str, brightness: float, terrain_data: Any):
        # Reduced random variation for more coherent look
        def vary_color(base_color, variation=5):
            return tuple(max(0, min(255, int(c * brightness + random.randint(-variation, variation)))) for c in base_color)
        # Water biomes
        if biome == 'deep_ocean':
            return vary_color((0, 20, 80))
        elif biome == 'ocean':
            return vary_color((0, 40, 120))
        elif biome == 'shallow_water':
            return vary_color((20, 80, 160))
        elif biome == 'lake':
            return vary_color((10, 60, 140))
        elif biome == 'river':
            return vary_color((30, 100, 180))
        elif biome == 'wetlands':
            return vary_color((40, 80, 60))
        # Arctic biomes
        elif biome == 'glacier':
            return vary_color((240, 250, 255))
        elif biome == 'tundra_wet':
            return vary_color((100, 120, 100))
        elif biome == 'tundra_dry':
            return vary_color((140, 140, 120))
        # Cold temperate biomes
        elif biome == 'alpine':
            return vary_color((160, 160, 140))
        elif biome == 'boreal_forest':
            return vary_color((40, 80, 40))
        elif biome == 'mixed_forest':
            return vary_color((60, 100, 50))
        elif biome == 'montane_forest':
            return vary_color((50, 90, 45))
        elif biome == 'cold_grassland':
            return vary_color((80, 140, 60))
        elif biome == 'rocky_hills':
            return vary_color((120, 110, 90))
        # Temperate biomes
        elif biome == 'mountain_peak':
            return vary_color((140, 130, 110))
        elif biome == 'temperate_forest':
            return vary_color((50, 120, 40))
        elif biome == 'deciduous_forest':
            return vary_color((70, 130, 50))
        elif biome == 'grassland':
            return vary_color((60, 160, 40))
        elif biome == 'prairie':
            return vary_color((100, 180, 60))
        elif biome == 'scrubland':
            return vary_color((120, 140, 80))
        elif biome == 'semi_desert':
            return vary_color((180, 160, 100))
        # Tropical biomes
        elif biome == 'tropical_mountain':
            return vary_color((100, 120, 80))
        elif biome == 'tropical_rainforest':
            return vary_color((20, 80, 20))
        elif biome == 'tropical_forest':
            return vary_color((40, 100, 30))
        elif biome == 'savanna':
            return vary_color((140, 180, 80))
        elif biome == 'hot_desert':
            return vary_color((220, 200, 120))
        # Default fallback
        else:
            return vary_color((100, 100, 100))

    def draw(self, screen: pygame.Surface):
        offset = (self.camera_x - self.screen_width // 2, self.camera_y - self.screen_height // 2)
        for chunk in self.visible_chunks.values():
            for segment in chunk:
                segment.draw(screen, offset)

    def handle_event(self, event: Any):
        offset = (self.camera_x - self.screen_width // 2, self.camera_y - self.screen_height // 2)
        for chunk in self.visible_chunks.values():
            for segment in chunk:
                segment.handle_event(event, offset)

    def move_camera(self, dx: float, dy: float):
        self.camera_x = dx
        self.camera_y = dy
        self.update_visible_chunks()