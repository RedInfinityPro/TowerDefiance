from Container.imports_library import *

class WeatherParticle:
    def __init__(self, x: float, y: float, screen_width: float, screen_height: float):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = True
    
    def update(self, dt: float):
        pass
    
    def draw(self, screen: pygame.Surface):
        pass
    
    def reset_position(self):
        self.x = random.randint(0, self.screen_width)
        self.y = -10

class RainDrop(WeatherParticle):
    def __init__(self, x: float, y: float, screen_width: float, screen_height: float):
        super().__init__(x, y, screen_width, screen_height)
        self.speed = random.uniform(300, 500)  # pixels per second
        self.wind_offset = random.uniform(-2, 2)
        self.length = random.uniform(8, 15)
        
    def update(self, dt: float):
        if not self.active:
            return
        self.y += self.speed * dt
        self.x += self.wind_offset * dt * 10
        # Reset if off screen
        if self.y > self.screen_height + 20:
            self.reset_position()
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        start_pos = (int(self.x), int(self.y))
        end_pos = (int(self.x + self.wind_offset), int(self.y + self.length))
        pygame.draw.line(screen, (100, 150, 220), start_pos, end_pos, 2)

class SnowFlake(WeatherParticle):
    def __init__(self, x: float, y: float, screen_width: float, screen_height: float):
        super().__init__(x, y, screen_width, screen_height)
        self.speed = random.uniform(50, 150)  # pixels per second
        self.wind_offset = random.uniform(-1, 1)
        self.size = random.uniform(2, 5)
        self.sway_speed = random.uniform(0.5, 2.0)
        self.sway_amount = random.uniform(10, 30)
        self.time_offset = random.uniform(0, 6.28)  # 2π
        
    def update(self, dt: float):
        if not self.active:
            return
        self.y += self.speed * dt
        # Add swaying motion
        sway_x = math.sin(time.time() * self.sway_speed + self.time_offset) * self.sway_amount * dt
        self.x += sway_x + self.wind_offset * dt * 20
        # Reset if off screen
        if self.y > self.screen_height + 20:
            self.reset_position()
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        pygame.draw.circle(screen, (200, 225, 255), (int(self.x), int(self.y)), int(self.size))

class BlizzardFlake(WeatherParticle):
    def __init__(self, x: float, y: float, screen_width: float, screen_height: float):
        super().__init__(x, y, screen_width, screen_height)
        self.speed = random.uniform(200, 400)  # pixels per second
        self.wind_offset = random.uniform(-5, 5)
        self.size = random.uniform(1, 3)
        self.horizontal_speed = random.uniform(-100, 100)
        
    def update(self, dt: float):
        if not self.active:
            return
        self.y += self.speed * dt
        self.x += (self.horizontal_speed + self.wind_offset * 50) * dt
        # Wrap around screen horizontally
        if self.x < -10:
            self.x = self.screen_width + 10
        elif self.x > self.screen_width + 10:
            self.x = -10
        # Reset if off screen vertically
        if self.y > self.screen_height + 20:
            self.reset_position()
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        pygame.draw.circle(screen, (220, 240, 255), (int(self.x), int(self.y)), int(self.size))

class FogParticle(WeatherParticle):
    def __init__(self, x: float, y: float, screen_width: float, screen_height: float):
        super().__init__(x, y, screen_width, screen_height)
        self.speed = random.uniform(10, 30)  # pixels per second
        self.size = random.uniform(10, 20)
        self.alpha = random.randint(20, 80)
        self.drift_x = random.uniform(-20, 20)
        self.drift_y = random.uniform(-10, 10)
        
    def update(self, dt: float):
        if not self.active:
            return
        self.x += self.drift_x * dt
        self.y += self.drift_y * dt
        # Wrap around screen
        if self.x < -self.size:
            self.x = self.screen_width + self.size
        elif self.x > self.screen_width + self.size:
            self.x = -self.size
        if self.y < -self.size:
            self.y = self.screen_height + self.size
        elif self.y > self.screen_height + self.size:
            self.y = -self.size
    
    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        # Create a surface with per-pixel alpha for fog effect
        fog_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(fog_surface, (200, 200, 240, self.alpha), (int(self.size), int(self.size)), int(self.size))
        screen.blit(fog_surface, (int(self.x - self.size), int(self.y - self.size)))

class Weather:
    def __init__(self):
        self.time = 0  # Represents in-game time (0-24 hours)
        self.day_length = 60  # Seconds for a full day
        self.weather_types = ["clear", "overcast", "snowstorm", "fog", "rain", "snow"]
        self.current_weather = random.choice(self.weather_types)
        self.weather_timer = time.time() + random.uniform(0.1, 24)  # Next weather change
        # Particle systems
        self.rain_particles = []
        self.snow_particles = []
        self.blizzard_particles = []
        self.fog_particles = []
        # Pause state
        self.is_paused = False
        self.update_weather_values()
        
    def set_pause_state(self, paused: bool):
        self.is_paused = paused
        # When pausing, freeze all particles
        for particle_list in [self.rain_particles, self.snow_particles, self.blizzard_particles, self.fog_particles]:
            for particle in particle_list:
                particle.active = not paused

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

    def _initialize_particles(self, screen_width: float, screen_height: float):
        """Initialize particle systems based on current weather"""
        # Clear existing particles
        self.rain_particles.clear()
        self.snow_particles.clear()
        self.blizzard_particles.clear()
        self.fog_particles.clear()
        if self.current_weather == "rain":
            for _ in range(80):
                x = random.randint(0, screen_width)
                y = random.randint(-screen_height, 0)
                self.rain_particles.append(RainDrop(x, y, screen_width, screen_height))
        elif self.current_weather == "snow":
            for _ in range(70):
                x = random.randint(0, screen_width)
                y = random.randint(-screen_height, 0)
                self.snow_particles.append(SnowFlake(x, y, screen_width, screen_height))
        elif self.current_weather == "snowstorm":
            for _ in range(100):
                x = random.randint(0, screen_width)
                y = random.randint(-screen_height, 0)
                self.blizzard_particles.append(BlizzardFlake(x, y, screen_width, screen_height))
        elif self.current_weather == "fog":
            for _ in range(30):
                x = random.randint(0, screen_width)
                y = random.randint(0, screen_height)
                self.fog_particles.append(FogParticle(x, y, screen_width, screen_height))

    def draw(self, screen: pygame.Surface, dt: float):
        screen_width, screen_height = screen.get_size()
        # Initialize particles if needed (when weather changes or screen size changes)
        if (self.current_weather in ["rain", "snow", "snowstorm", "fog"] and 
            not any([self.rain_particles, self.snow_particles, self.blizzard_particles, self.fog_particles])):
            self._initialize_particles(screen_width, screen_height)
        # Apply lighting
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self._get_lighting())
        screen.blit(overlay, (0, 0))
        # Update and draw particles only if not paused
        if not self.is_paused:
            # Update particles
            for particle in self.rain_particles:
                particle.update(dt)
            for particle in self.snow_particles:
                particle.update(dt)
            for particle in self.blizzard_particles:
                particle.update(dt)
            for particle in self.fog_particles:
                particle.update(dt)
        # Draw particles (always draw, even when paused)
        for particle in self.rain_particles:
            particle.draw(screen)
        for particle in self.snow_particles:
            particle.draw(screen)
        for particle in self.blizzard_particles:
            particle.draw(screen)
        # Draw fog overlay first, then particles
        if self.current_weather == "fog":
            fog_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fog_overlay.fill((180, 180, 220, 120))
            screen.blit(fog_overlay, (0, 0))
        for particle in self.fog_particles:
            particle.draw(screen)

    def update(self, elapsed_time: float, dt: float):
        self.time = elapsed_time or (time.time() % self.day_length) / self.day_length * 24
        # Only change weather if not paused
        if not self.is_paused and time.time() > self.weather_timer:
            old_weather = self.current_weather
            self.current_weather = random.choice(self.weather_types)
            self.update_weather_values()
            self.weather_timer = time.time() + random.uniform(0.1, 24)
            # If weather changed, clear particles to force reinitialize
            if old_weather != self.current_weather:
                self.rain_particles.clear()
                self.snow_particles.clear()
                self.blizzard_particles.clear()
                self.fog_particles.clear()