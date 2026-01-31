import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BLUE = (65, 105, 225)
DARK_BLUE = (25, 25, 112)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
SNOW_WHITE = (240, 248, 255)
ICE_BLUE = (176, 224, 230)
LIGHT_GRAY = (211, 211, 211)
VILLAGE_GREEN = (107, 142, 35)
SKY_BLUE = (135, 206, 235)

class LaneType(Enum):
    SAFE = 0
    ROAD = 1
    RIVER = 2
    TRAIN = 3
    DANGER = 4

class Character(Enum):
    CHICKEN = 0
    ANDROID = 1
    BRITISH_GUARD = 2
    SNOWMAN = 3

class Environment(Enum):
    CITY = 0
    VILLAGE = 1
    SNOW = 2
    TECH = 3

class GameObject:
    def __init__(self, x, y, width, height, speed=0, direction=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = direction
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self):
        self.x += self.speed * self.direction
        # Wrap around screen
        if self.direction > 0 and self.x > SCREEN_WIDTH:
            self.x = -self.width
        elif self.direction < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

class Car(GameObject):
    def __init__(self, x, y, speed, direction, color, car_type="car"):
        super().__init__(x, y, GRID_SIZE * 2, GRID_SIZE - 10, speed, direction)
        self.color = color
        self.car_type = car_type
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        if -100 < y_pos < SCREEN_HEIGHT + 100:
            if self.car_type == "car":
                # Car body
                pygame.draw.rect(screen, self.color, 
                               (int(self.x), y_pos, self.width, self.height))
                # Windows
                pygame.draw.rect(screen, SKY_BLUE, 
                               (int(self.x) + 10, y_pos + 5, self.width - 50, self.height - 15))
                # Headlights
                light_x = int(self.x) + self.width - 5 if self.direction > 0 else int(self.x) + 5
                pygame.draw.circle(screen, YELLOW, (light_x, y_pos + self.height // 2), 3)
            elif self.car_type == "bus":
                # Bus body
                pygame.draw.rect(screen, self.color, 
                               (int(self.x), y_pos, self.width, self.height))
                # Windows
                for i in range(3):
                    pygame.draw.rect(screen, SKY_BLUE, 
                                   (int(self.x) + 10 + i * 20, y_pos + 5, 15, self.height - 15))

class Log(GameObject):
    def __init__(self, x, y, width, speed, direction):
        super().__init__(x, y, width, GRID_SIZE - 10, speed, direction)
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        if -100 < y_pos < SCREEN_HEIGHT + 100:
            # Log body
            pygame.draw.rect(screen, BROWN, 
                           (int(self.x), y_pos, self.width, self.height))
            # Log rings
            for i in range(0, self.width, 20):
                pygame.draw.circle(screen, (101, 67, 33), 
                                 (int(self.x) + i + 10, y_pos + self.height // 2), 8)

class Train(GameObject):
    def __init__(self, x, y, speed, direction):
        super().__init__(x, y, GRID_SIZE * 6, GRID_SIZE - 5, speed, direction)
        self.warning_time = 120  # 2 seconds warning
        self.active = False
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        if -300 < y_pos < SCREEN_HEIGHT + 100 and self.active:
            # Train engine
            pygame.draw.rect(screen, RED, 
                           (int(self.x), y_pos, self.width, self.height))
            # Train windows
            for i in range(5):
                pygame.draw.rect(screen, YELLOW, 
                               (int(self.x) + 10 + i * 40, y_pos + 5, 30, self.height - 15))
            # Front light
            if self.direction > 0:
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x) + self.width - 10, y_pos + self.height // 2), 8)
            else:
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x) + 10, y_pos + self.height // 2), 8)

class Enemy(GameObject):
    def __init__(self, x, y, speed, direction, enemy_type="robot"):
        super().__init__(x, y, GRID_SIZE - 5, GRID_SIZE - 5, speed, direction)
        self.enemy_type = enemy_type
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        if -100 < y_pos < SCREEN_HEIGHT + 100:
            if self.enemy_type == "robot":
                # Robot body
                pygame.draw.rect(screen, GRAY, 
                               (int(self.x), y_pos + 10, self.width, self.height - 10))
                # Robot head
                pygame.draw.rect(screen, DARK_GRAY, 
                               (int(self.x) + 5, y_pos, self.width - 10, 15))
                # Robot eyes
                pygame.draw.circle(screen, RED, 
                                 (int(self.x) + 10, y_pos + 7), 3)
                pygame.draw.circle(screen, RED, 
                                 (int(self.x) + self.width - 10, y_pos + 7), 3)
            elif self.enemy_type == "alien":
                # Alien body
                pygame.draw.ellipse(screen, GREEN, 
                                  (int(self.x), y_pos + 10, self.width, self.height - 10))
                # Alien head
                pygame.draw.ellipse(screen, DARK_GREEN, 
                                  (int(self.x) + 5, y_pos, self.width - 10, 20))
                # Alien eyes
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x) + 10, y_pos + 8), 4)
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.x) + self.width - 10, y_pos + 8), 4)

class Lane:
    def __init__(self, y, lane_type, environment):
        self.y = y
        self.lane_type = lane_type
        self.environment = environment
        self.objects = []
        self.warning_timer = 0
        self.train_cooldown = 0
        
        if lane_type == LaneType.ROAD:
            self._spawn_cars()
        elif lane_type == LaneType.RIVER:
            self._spawn_logs()
        elif lane_type == LaneType.TRAIN:
            self._setup_train()
        elif lane_type == LaneType.DANGER:
            self._spawn_enemies()
    
    def _spawn_cars(self):
        num_cars = random.randint(2, 4)
        speed = random.uniform(1.5, 3.5)
        direction = random.choice([-1, 1])
        
        colors = [RED, BLUE, YELLOW, ORANGE, PURPLE]
        
        # Calculate positions to avoid overlaps
        positions = []
        min_gap = GRID_SIZE * 3  # Minimum gap between cars
        
        for i in range(num_cars):
            car_type = "bus" if random.random() < 0.2 else "car"
            car_width = GRID_SIZE * 3 if car_type == "bus" else GRID_SIZE * 2
            
            # Find a valid position
            max_attempts = 20
            for attempt in range(max_attempts):
                # Try to place car
                if i == 0:
                    # First car - random position
                    x = random.randint(0, SCREEN_WIDTH - car_width)
                else:
                    # Subsequent cars - find space
                    x = random.randint(0, SCREEN_WIDTH - car_width)
                
                # Check if this position overlaps with existing cars
                valid = True
                for existing_x, existing_width in positions:
                    if abs(x - existing_x) < (car_width + existing_width) / 2 + min_gap:
                        valid = False
                        break
                
                if valid:
                    break
            
            # Only add if we found a valid position
            if valid or i == 0:
                positions.append((x, car_width))
                color = random.choice(colors)
                
                if car_type == "bus":
                    car = Car(x, self.y, speed * 0.7, direction, color, car_type)
                    car.width = GRID_SIZE * 3
                else:
                    car = Car(x, self.y, speed, direction, color, car_type)
                
                self.objects.append(car)
    
    def _spawn_logs(self):
        num_logs = random.randint(2, 4)
        speed = random.uniform(0.8, 2.0)
        direction = random.choice([-1, 1])
        
        # Calculate positions to avoid overlaps
        positions = []
        min_gap = GRID_SIZE  # Minimum gap between logs
        
        for i in range(num_logs):
            width = random.randint(GRID_SIZE * 2, GRID_SIZE * 4)
            
            # Find a valid position
            max_attempts = 20
            valid = False
            
            for attempt in range(max_attempts):
                if i == 0:
                    # First log - random position
                    x = random.randint(0, SCREEN_WIDTH - width)
                else:
                    # Subsequent logs - find space
                    x = random.randint(0, SCREEN_WIDTH - width)
                
                # Check if this position overlaps with existing logs
                valid = True
                for existing_x, existing_width in positions:
                    if abs(x - existing_x) < (width + existing_width) / 2 + min_gap:
                        valid = False
                        break
                
                if valid:
                    break
            
            # Only add if we found a valid position
            if valid or i == 0:
                positions.append((x, width))
                log = Log(x, self.y, width, speed, direction)
                self.objects.append(log)
    
    def _setup_train(self):
        # Train starts off-screen
        direction = random.choice([-1, 1])
        x = -GRID_SIZE * 6 if direction > 0 else SCREEN_WIDTH
        train = Train(x, self.y, 8, direction)
        self.objects.append(train)
        self.train_cooldown = random.randint(180, 360)  # 3-6 seconds
    
    def _spawn_enemies(self):
        num_enemies = random.randint(3, 5)
        speed = random.uniform(1.0, 2.5)
        direction = random.choice([-1, 1])
        
        enemy_type = "alien" if self.environment == Environment.TECH else "robot"
        enemy_width = GRID_SIZE - 5
        
        # Calculate positions to avoid overlaps
        positions = []
        min_gap = GRID_SIZE * 1.5  # Minimum gap between enemies
        
        for i in range(num_enemies):
            # Find a valid position
            max_attempts = 20
            valid = False
            
            for attempt in range(max_attempts):
                if i == 0:
                    # First enemy - random position
                    x = random.randint(0, SCREEN_WIDTH - enemy_width)
                else:
                    # Subsequent enemies - find space
                    x = random.randint(0, SCREEN_WIDTH - enemy_width)
                
                # Check if this position overlaps with existing enemies
                valid = True
                for existing_x in positions:
                    if abs(x - existing_x) < enemy_width + min_gap:
                        valid = False
                        break
                
                if valid:
                    break
            
            # Only add if we found a valid position
            if valid or i == 0:
                positions.append(x)
                enemy = Enemy(x, self.y, speed, direction, enemy_type)
                self.objects.append(enemy)
    
    def update(self):
        for obj in self.objects:
            if isinstance(obj, Train):
                if self.train_cooldown > 0:
                    self.train_cooldown -= 1
                    obj.active = False
                    # Reset train position
                    if obj.direction > 0:
                        obj.x = -obj.width
                    else:
                        obj.x = SCREEN_WIDTH
                elif self.train_cooldown == 0:
                    obj.active = True
                    obj.update()
                    # Check if train has passed
                    if (obj.direction > 0 and obj.x > SCREEN_WIDTH + 100) or \
                       (obj.direction < 0 and obj.x < -obj.width - 100):
                        self.train_cooldown = random.randint(180, 360)
            else:
                obj.update()
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        
        # Draw lane background
        if -100 < y_pos < SCREEN_HEIGHT + 100:
            if self.lane_type == LaneType.SAFE:
                if self.environment == Environment.SNOW:
                    color = (230, 240, 255)  # Light ice blue instead of white
                    pattern_color = (180, 200, 220)  # Darker ice blue for pattern
                elif self.environment == Environment.VILLAGE:
                    color = VILLAGE_GREEN
                    pattern_color = DARK_GREEN
                elif self.environment == Environment.TECH:
                    color = LIGHT_GRAY
                    pattern_color = GRAY
                else:
                    color = GREEN
                    pattern_color = DARK_GREEN
                pygame.draw.rect(screen, color, (0, y_pos, SCREEN_WIDTH, GRID_SIZE))
                # Add pattern (grass or snow texture)
                for i in range(0, SCREEN_WIDTH, 20):
                    pygame.draw.circle(screen, pattern_color, (i, y_pos + 10), 3)
            elif self.lane_type == LaneType.ROAD:
                pygame.draw.rect(screen, DARK_GRAY, (0, y_pos, SCREEN_WIDTH, GRID_SIZE))
                # Road lines
                for i in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.rect(screen, YELLOW, (i, y_pos + GRID_SIZE // 2 - 2, 20, 4))
            elif self.lane_type == LaneType.RIVER:
                if self.environment == Environment.SNOW:
                    color = ICE_BLUE
                else:
                    color = BLUE
                pygame.draw.rect(screen, color, (0, y_pos, SCREEN_WIDTH, GRID_SIZE))
                # Water waves
                for i in range(0, SCREEN_WIDTH, 30):
                    pygame.draw.arc(screen, DARK_BLUE, 
                                  (i, y_pos + 10, 20, 20), 0, 3.14, 2)
            elif self.lane_type == LaneType.TRAIN:
                pygame.draw.rect(screen, DARK_GRAY, (0, y_pos, SCREEN_WIDTH, GRID_SIZE))
                # Train tracks
                pygame.draw.rect(screen, BROWN, (0, y_pos + 10, SCREEN_WIDTH, 5))
                pygame.draw.rect(screen, BROWN, (0, y_pos + 25, SCREEN_WIDTH, 5))
                # Warning if train is coming
                if self.train_cooldown < 60 and self.train_cooldown > 0:
                    if (self.train_cooldown // 10) % 2 == 0:
                        pygame.draw.circle(screen, RED, (20, y_pos + 20), 8)
                        pygame.draw.circle(screen, RED, (SCREEN_WIDTH - 20, y_pos + 20), 8)
            elif self.lane_type == LaneType.DANGER:
                pygame.draw.rect(screen, PURPLE, (0, y_pos, SCREEN_WIDTH, GRID_SIZE))
                # Danger pattern
                for i in range(0, SCREEN_WIDTH, 40):
                    points = [(i, y_pos), (i + 20, y_pos + 20), (i, y_pos + 40)]
                    pygame.draw.polygon(screen, (255, 0, 255), points, 2)
        
        # Draw objects
        for obj in self.objects:
            obj.draw(screen, camera_y)

class Player:
    def __init__(self, character, environment):
        self.character = character
        self.environment = environment
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.start_y = self.y
        self.width = GRID_SIZE - 10
        self.height = GRID_SIZE - 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_log = None
        self.hop_animation = 0
        self.hop_direction = None
        self.target_x = self.x
        self.target_y = self.y
        self.is_hopping = False
    
    def move(self, dx, dy):
        if not self.is_hopping:
            self.target_x = self.x + dx * GRID_SIZE
            self.target_y = self.y + dy * GRID_SIZE
            self.hop_direction = (dx, dy)
            self.is_hopping = True
            self.hop_animation = 10
    
    def update(self):
        if self.is_hopping and self.hop_animation > 0:
            # Smooth hopping animation
            progress = (10 - self.hop_animation) / 10
            self.x = self.x + (self.target_x - self.x) * 0.3
            self.y = self.y + (self.target_y - self.y) * 0.3
            self.hop_animation -= 1
            
            if self.hop_animation == 0:
                self.x = self.target_x
                self.y = self.target_y
                self.is_hopping = False
        
        # Update rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
            self.target_x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.target_x = SCREEN_WIDTH - self.width
        
        # Move with log if on one
        if self.on_log:
            self.x += self.on_log.speed * self.on_log.direction
            self.target_x = self.x
    
    def draw(self, screen, camera_y):
        y_pos = int(self.y - camera_y)
        hop_offset = -abs(self.hop_animation * 2) if self.is_hopping else 0
        
        if self.character == Character.CHICKEN:
            # Chicken body
            pygame.draw.ellipse(screen, WHITE, 
                              (int(self.x), y_pos + 10 + hop_offset, self.width, self.height - 10))
            # Chicken head
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x) + self.width // 2, y_pos + 8 + hop_offset), 8)
            # Beak
            points = [(int(self.x) + self.width // 2, y_pos + 8 + hop_offset),
                     (int(self.x) + self.width // 2 + 8, y_pos + 10 + hop_offset),
                     (int(self.x) + self.width // 2, y_pos + 12 + hop_offset)]
            pygame.draw.polygon(screen, ORANGE, points)
            # Eyes
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x) + self.width // 2 - 3, y_pos + 6 + hop_offset), 2)
        
        elif self.character == Character.ANDROID:
            # Android body
            pygame.draw.rect(screen, (164, 198, 57), 
                           (int(self.x), y_pos + 12 + hop_offset, self.width, self.height - 12))
            # Android head
            pygame.draw.circle(screen, (164, 198, 57), 
                             (int(self.x) + self.width // 2, y_pos + 10 + hop_offset), 10)
            # Antennae
            pygame.draw.line(screen, (164, 198, 57), 
                           (int(self.x) + self.width // 2 - 5, y_pos + 3 + hop_offset),
                           (int(self.x) + self.width // 2 - 8, y_pos + hop_offset), 3)
            pygame.draw.line(screen, (164, 198, 57), 
                           (int(self.x) + self.width // 2 + 5, y_pos + 3 + hop_offset),
                           (int(self.x) + self.width // 2 + 8, y_pos + hop_offset), 3)
            pygame.draw.circle(screen, (164, 198, 57), 
                             (int(self.x) + self.width // 2 - 8, y_pos + hop_offset), 2)
            pygame.draw.circle(screen, (164, 198, 57), 
                             (int(self.x) + self.width // 2 + 8, y_pos + hop_offset), 2)
            # Eyes
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x) + self.width // 2 - 4, y_pos + 10 + hop_offset), 3)
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x) + self.width // 2 + 4, y_pos + 10 + hop_offset), 3)
        
        elif self.character == Character.BRITISH_GUARD:
            # Guard body (red uniform)
            pygame.draw.rect(screen, RED, 
                           (int(self.x), y_pos + 15 + hop_offset, self.width, self.height - 15))
            # Guard head (beige)
            pygame.draw.circle(screen, (255, 228, 196), 
                             (int(self.x) + self.width // 2, y_pos + 12 + hop_offset), 8)
            # Hat (black bearskin)
            pygame.draw.rect(screen, BLACK, 
                           (int(self.x) + 5, y_pos + hop_offset, self.width - 10, 10))
            # Eyes
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x) + self.width // 2 - 3, y_pos + 12 + hop_offset), 2)
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x) + self.width // 2 + 3, y_pos + 12 + hop_offset), 2)
        
        elif self.character == Character.SNOWMAN:
            # Snowman bottom
            pygame.draw.circle(screen, SNOW_WHITE, 
                             (int(self.x) + self.width // 2, y_pos + 25 + hop_offset), 12)
            # Snowman middle
            pygame.draw.circle(screen, SNOW_WHITE, 
                             (int(self.x) + self.width // 2, y_pos + 15 + hop_offset), 9)
            # Snowman head
            pygame.draw.circle(screen, SNOW_WHITE, 
                             (int(self.x) + self.width // 2, y_pos + 7 + hop_offset), 7)
            # Eyes
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x) + self.width // 2 - 3, y_pos + 6 + hop_offset), 2)
            pygame.draw.circle(screen, BLACK, 
                             (int(self.x) + self.width // 2 + 3, y_pos + 6 + hop_offset), 2)
            # Carrot nose
            points = [(int(self.x) + self.width // 2, y_pos + 8 + hop_offset),
                     (int(self.x) + self.width // 2 + 8, y_pos + 9 + hop_offset),
                     (int(self.x) + self.width // 2, y_pos + 10 + hop_offset)]
            pygame.draw.polygon(screen, ORANGE, points)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Crossy Road - Python Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.character = Character.CHICKEN
        self.environment = Environment.CITY
        self.player = None
        self.lanes = []
        self.camera_y = 0
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.in_menu = True
        self.selected_character = 0
        
        self.init_game()
    
    def init_game(self):
        self.player = Player(self.character, self.environment)
        self.lanes = []
        self.score = 0
        self.game_over = False
        
        # Set camera to follow player from the start
        self.camera_y = self.player.y - SCREEN_HEIGHT * 0.65
        
        # Create starting safe zone (large)
        for i in range(5):
            lane = Lane(SCREEN_HEIGHT - 100 - i * GRID_SIZE, LaneType.SAFE, self.environment)
            self.lanes.append(lane)
        
        # Generate initial lanes
        for i in range(30):
            self.generate_lane()
    
    def generate_lane(self):
        if len(self.lanes) == 0:
            y = 0
        else:
            y = self.lanes[-1].y - GRID_SIZE
        
        # Determine lane type based on environment
        if len(self.lanes) % 5 == 0:  # Safe zone every 5 lanes
            lane_type = LaneType.SAFE
        else:
            if self.environment == Environment.CITY:
                lane_type = random.choices(
                    [LaneType.ROAD, LaneType.TRAIN, LaneType.SAFE],
                    weights=[60, 10, 30]
                )[0]
            elif self.environment == Environment.VILLAGE:
                lane_type = random.choices(
                    [LaneType.ROAD, LaneType.RIVER, LaneType.SAFE],
                    weights=[40, 40, 20]
                )[0]
            elif self.environment == Environment.SNOW:
                lane_type = random.choices(
                    [LaneType.RIVER, LaneType.SAFE, LaneType.DANGER],
                    weights=[50, 30, 20]
                )[0]
            else:  # TECH
                lane_type = random.choices(
                    [LaneType.ROAD, LaneType.DANGER, LaneType.SAFE],
                    weights=[40, 40, 20]
                )[0]
        
        lane = Lane(y, lane_type, self.environment)
        self.lanes.append(lane)
    
    def check_collisions(self):
        player_rect = self.player.rect
        current_lane = None
        
        # Find current lane
        for lane in self.lanes:
            if abs(lane.y - self.player.y) < GRID_SIZE // 2:
                current_lane = lane
                break
        
        if not current_lane:
            return False
        
        # Check if on river/water
        if current_lane.lane_type == LaneType.RIVER:
            self.player.on_log = None
            for obj in current_lane.objects:
                if isinstance(obj, Log) and player_rect.colliderect(obj.rect):
                    self.player.on_log = obj
                    break
            
            # If not on a log, game over
            if not self.player.on_log:
                return True
        else:
            self.player.on_log = None
        
        # Check collision with obstacles
        for obj in current_lane.objects:
            if isinstance(obj, (Car, Train, Enemy)):
                if isinstance(obj, Train) and not obj.active:
                    continue
                if player_rect.colliderect(obj.rect):
                    return True
        
        return False
    
    def update_camera(self):
        # Camera smoothly follows player, keeping them in view
        # Target: keep player in the lower third of the screen for better forward visibility
        target_camera = self.player.y - SCREEN_HEIGHT * 0.65
        
        # Smooth camera movement
        if abs(target_camera - self.camera_y) > 1:
            self.camera_y += (target_camera - self.camera_y) * 0.1
        else:
            self.camera_y = target_camera
        
        # Update score based on progress (only when moving forward/up)
        new_score = int((self.player.start_y - self.player.y) // GRID_SIZE)
        if new_score > self.score:
            self.score = new_score
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.player.is_hopping:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.move(0, -1)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.move(0, 1)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move(-1, 0)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move(1, 0)
    
    def draw_menu(self):
        self.screen.fill(SKY_BLUE)
        
        # Title
        title = self.font.render("CROSSY ROAD", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Character selection
        characters = [
            ("CHICKEN", Character.CHICKEN, Environment.CITY),
            ("ANDROID ROBOT", Character.ANDROID, Environment.TECH),
            ("BRITISH GUARD", Character.BRITISH_GUARD, Environment.VILLAGE),
            ("SNOWMAN", Character.SNOWMAN, Environment.SNOW)
        ]
        
        instruction = self.small_font.render("Select Character (Arrow Keys + SPACE)", True, BLACK)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 120))
        
        for i, (name, char, env) in enumerate(characters):
            y = 180 + i * 80
            color = YELLOW if i == self.selected_character else WHITE
            
            # Draw selection box
            pygame.draw.rect(self.screen, color, 
                           (SCREEN_WIDTH // 2 - 150, y, 300, 60), 0 if i == self.selected_character else 2)
            
            # Draw character name
            text = self.small_font.render(name, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y + 20))
        
        # Instructions
        inst_text = self.small_font.render("WASD or Arrow Keys to Move | ESC to Menu", True, BLACK)
        self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 520))
    
    def draw_game(self):
        # Background
        if self.environment == Environment.SNOW:
            self.screen.fill((200, 220, 240))  # Light winter sky blue
        elif self.environment == Environment.VILLAGE:
            self.screen.fill(VILLAGE_GREEN)
        elif self.environment == Environment.TECH:
            self.screen.fill(DARK_GRAY)
        else:
            self.screen.fill(SKY_BLUE)
        
        # Draw lanes
        for lane in self.lanes:
            lane.draw(self.screen, self.camera_y)
        
        # Draw player
        self.player.draw(self.screen, self.camera_y)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(high_score_text, (10, 50))
        
        # Draw game over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            self.screen.blit(final_score, 
                           (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
            
            restart_text = self.small_font.render("Press SPACE to play again | ESC for menu", True, WHITE)
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.in_menu:
                        if event.key == pygame.K_UP:
                            self.selected_character = (self.selected_character - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            self.selected_character = (self.selected_character + 1) % 4
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            characters = [
                                (Character.CHICKEN, Environment.CITY),
                                (Character.ANDROID, Environment.TECH),
                                (Character.BRITISH_GUARD, Environment.VILLAGE),
                                (Character.SNOWMAN, Environment.SNOW)
                            ]
                            self.character, self.environment = characters[self.selected_character]
                            self.in_menu = False
                            self.init_game()
                    
                    elif self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.init_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.in_menu = True
                    
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.in_menu = True
            
            if self.in_menu:
                self.draw_menu()
            
            elif not self.game_over:
                # Handle input
                self.handle_input()
                
                # Update
                self.player.update()
                
                for lane in self.lanes:
                    lane.update()
                
                # Check collisions
                if self.check_collisions():
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                
                # Update camera
                self.update_camera()
                
                # Generate new lanes ahead of player
                # Keep generating lanes as long as we need more ahead of the camera
                while len(self.lanes) < 50 or self.lanes[-1].y > self.camera_y - SCREEN_HEIGHT * 2:
                    self.generate_lane()
                
                # Remove old lanes that are far behind the camera
                self.lanes = [lane for lane in self.lanes if lane.y > self.camera_y - SCREEN_HEIGHT * 2]
                
                # Draw
                self.draw_game()
            
            else:
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
