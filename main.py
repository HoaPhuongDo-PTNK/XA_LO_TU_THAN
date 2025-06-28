import pygame
import random
import math
import asyncio
import platform
import time
from maze_generator import MazeGenerator, Pathfinder

# Khởi tạo Pygame
pygame.init()
WIDTH, HEIGHT = 800, 800  # Fixed square dimensions
UI_HEIGHT = 80  # Height reserved for UI elements (reduced)
MAZE_START_Y = UI_HEIGHT
MAZE_HEIGHT = HEIGHT - UI_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner - Escape Game")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)  # For text visibility
ORANGE = (255, 165, 0)  # For text visibility
CYAN = (0, 255, 255)    # For text visibility
PURPLE = (128, 0, 128, 100)  # Semi-transparent purple for player trail
LIGHT_GREEN = (0, 255, 0, 80)  # Semi-transparent green for solution path
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
MODERN_BLUE = (41, 128, 185)
MODERN_GREEN = (39, 174, 96)
MODERN_RED = (231, 76, 60)
MODERN_ORANGE = (230, 126, 34)
MODERN_PURPLE = (142, 68, 173)
WIN_COLOR = (255, 0, 0)  # Red flag for winning

# Game states
MENU = 0
DIFFICULTY = 1
PLAYING = 2
GAME_OVER = 3
GAME_WON = 4
DEATH_ANIMATION = 5

# Khởi tạo maze generator
maze_generator = MazeGenerator(WIDTH, MAZE_HEIGHT, cell_size=20)
maze_generator.generate_maze()
maze_surface = maze_generator.create_surface()
pathfinder = Pathfinder(maze_generator)
solution_path = pathfinder.get_solution_path()

# Ensure we have at least start and goal positions
if not solution_path or len(solution_path) < 2:
    print("Warning: No initial solution path found, creating fallback path")
    start_x, start_y = maze_generator.get_start_position()
    goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2
    goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2
    solution_path = [(start_x, start_y), (goal_x, goal_y)]

# Adjust solution path for UI offset
solution_path = [(x, y + MAZE_START_Y) for x, y in solution_path]

# Game state
game_state = MENU
difficulty = 1  # Easy by default

# Animation state
animation_progress = 0
animation_speed = 0.8  # Much slower animation for better visibility
animation_wait_timer = 0  # Timer for waiting after animation completes
# Thông số game
PLAYER_SIZE = 20
ENEMY_SIZE = 15
PLAYER_SPEED = 3
# Enemy speed will be calculated based on difficulty
TRAIL_MAX_LENGTH = 50  # Maximum trail points

# Difficulty settings with different enemy speeds
DIFFICULTY_SETTINGS = {
    1: {"enemies": 1, "name": "Easy", "enemy_speed_multiplier": 1.15},    # 15% faster when tracking
    2: {"enemies": 2, "name": "Medium", "enemy_speed_multiplier": 1.20},  # 20% faster when tracking  
    3: {"enemies": 3, "name": "Hard", "enemy_speed_multiplier": 1.25}     # 25% faster when tracking
}

# Game timing
start_time = 0
end_time = 0
distance_traveled = 0

# Hàm kiểm tra va chạm với maze
def check_collision(x, y):
    """Check collision with maze walls and goal - improved precision"""
    # Ensure coordinates are within maze bounds
    if x < 0 or y < 0:
        return "wall"
    
    grid_x = int(x // maze_generator.cell_size)
    grid_y = int(y // maze_generator.cell_size)
    
    # Check bounds
    if grid_x >= maze_generator.maze_width or grid_y >= maze_generator.maze_height:
        return "wall"
    
    if maze_generator.maze[grid_y][grid_x]:
        return "wall"
    elif (grid_x, grid_y) == maze_generator.goal_pos:
        return "goal"
    return None

def check_goal_collision(player_rect):
    """Check if player rectangle overlaps with goal"""
    goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size
    goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size
    goal_rect = pygame.Rect(goal_x, goal_y, maze_generator.cell_size, maze_generator.cell_size)
    return player_rect.colliderect(goal_rect)

# Lớp người chơi
class Player:
    def __init__(self):
        start_x, start_y = maze_generator.get_start_position()
        self.x = start_x
        self.y = start_y + MAZE_START_Y  # Adjust for UI offset
        self.rect = pygame.Rect(self.x - PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.trail = []  # Store player trail positions
        self.last_position = (self.x, self.y)

    def move(self, keys):
        global distance_traveled
        old_x, old_y = self.x, self.y
        collision_result = None
        moved = False
        
        # Check movement with collision detection
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x = self.x - PLAYER_SPEED
            if not check_collision(new_x, self.y - MAZE_START_Y):
                self.x = new_x
                moved = True
            
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x = self.x + PLAYER_SPEED
            if not check_collision(new_x, self.y - MAZE_START_Y):
                self.x = new_x
                moved = True
            
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y = self.y - PLAYER_SPEED
            if not check_collision(self.x, new_y - MAZE_START_Y):
                self.y = new_y
                moved = True
            
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y = self.y + PLAYER_SPEED
            if not check_collision(self.x, new_y - MAZE_START_Y):
                self.y = new_y
                moved = True
        
        # Add to trail and calculate distance if player moved
        if moved:
            self.trail.append((old_x, old_y))
            if len(self.trail) > TRAIL_MAX_LENGTH:
                self.trail.pop(0)  # Remove oldest trail point
            
            # Calculate distance traveled
            distance_traveled += math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
            
        self.rect = pygame.Rect(self.x - PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        
        # Check goal collision with rectangle overlap (adjust for maze offset)
        goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size
        goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + MAZE_START_Y
        goal_rect = pygame.Rect(goal_x, goal_y, maze_generator.cell_size, maze_generator.cell_size)
        if self.rect.colliderect(goal_rect):
            collision_result = "goal"
            
        return collision_result

    def draw(self):
        # Draw trail first (behind player)
        self.draw_trail()
        # Draw player
        pygame.draw.rect(screen, BLUE, self.rect)
    
    def draw_trail(self):
        # Create a surface for transparency
        if len(self.trail) > 1:
            trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i, (x, y) in enumerate(self.trail):
                # Make trail fade out (more transparent for older points)
                alpha = int(100 * (i + 1) / len(self.trail))
                color = (*PURPLE[:3], alpha)
                pygame.draw.circle(trail_surface, color, (int(x), int(y)), 3)
            screen.blit(trail_surface, (0, 0))

# Lớp kẻ thù với random roaming và tracking AI
class Enemy:
    def __init__(self, difficulty_level=1):
        # Spawn at player's starting position
        start_x, start_y = maze_generator.get_start_position()
        self.x = start_x
        self.y = start_y + MAZE_START_Y  # Adjust for UI offset
        self.rect = pygame.Rect(self.x - ENEMY_SIZE // 2, self.y - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.direction_change_timer = 0
        self.safe_zone_timer = 0  # Timer to ensure player has safe passage
        
        # Speed calculation based on difficulty
        self.difficulty = difficulty_level
        self.base_speed = PLAYER_SPEED * 0.15  # Much slower when roaming (0.15x player speed)
        self.tracking_speed = PLAYER_SPEED * DIFFICULTY_SETTINGS[difficulty_level]["enemy_speed_multiplier"]
        
        # AI tracking behavior - updated timings
        self.ai_timer = 0
        self.tracking_timer = 0
        self.is_tracking = False
        self.tracking_chance_timer = 0
        self.spawn_timer = 0  # Timer for spawning delay
        self.is_spawned = False  # Whether enemy has spawned yet
        
        # Pathfinding and movement memory
        self.visited_positions = []  # Track visited positions to avoid backtracking
        self.stuck_counter = 0  # Count how long we've been stuck
        self.last_position = (self.x, self.y)
        self.path_to_player = []  # Current path to player
        self.path_to_goal = []   # Current path to goal (for roaming)
        self.path_update_timer = 0  # Timer to update path periodically
    
    def get_current_speed(self):
        """Get current movement speed based on tracking state"""
        return self.tracking_speed if self.is_tracking else self.base_speed

    def move(self, player_x, player_y):
        # Handle spawn delay - enemies spawn after 3 seconds
        if not self.is_spawned:
            self.spawn_timer += 1
            if self.spawn_timer >= 180:  # 3 seconds at 60 FPS
                self.is_spawned = True
            return  # Don't move until spawned
        
        # AI behavior: track player for 6 seconds every 6 seconds
        self.tracking_chance_timer += 1
        if self.tracking_chance_timer >= 360:  # 6 seconds at 60 FPS
            self.tracking_chance_timer = 0
            self.is_tracking = True
            self.tracking_timer = 360  # 6 seconds at 60 FPS
            self.path_to_player = []  # Reset path when starting to track
            self.path_to_goal = []    # Clear goal path when starting to track
        
        if self.is_tracking:
            self.tracking_timer -= 1
            if self.tracking_timer <= 0:
                self.is_tracking = False
                self.path_to_player = []  # Clear path when stopping tracking
                self.path_to_goal = []    # Clear goal path when stopping tracking
                self.tracking_chance_timer = 0  # Reset to wait full 6 seconds before tracking again
            
            # Update path to player periodically or if we don't have one
            self.path_update_timer += 1
            if self.path_update_timer >= 30 or not self.path_to_player:  # Update every 0.5 seconds
                self.path_update_timer = 0
                # Get path from current position to player
                try:
                    # Convert pixel coordinates to grid coordinates for pathfinding
                    current_grid_x = int(self.x // maze_generator.cell_size)
                    current_grid_y = int((self.y - MAZE_START_Y) // maze_generator.cell_size)
                    player_grid_x = int(player_x // maze_generator.cell_size)
                    player_grid_y = int((player_y - MAZE_START_Y) // maze_generator.cell_size)
                    
                    # Ensure coordinates are within bounds
                    current_grid_x = max(0, min(maze_generator.maze_width - 1, current_grid_x))
                    current_grid_y = max(0, min(maze_generator.maze_height - 1, current_grid_y))
                    player_grid_x = max(0, min(maze_generator.maze_width - 1, player_grid_x))
                    player_grid_y = max(0, min(maze_generator.maze_height - 1, player_grid_y))
                    
                    path_result = pathfinder.find_path(
                        current_grid_x * maze_generator.cell_size + maze_generator.cell_size // 2,
                        current_grid_y * maze_generator.cell_size + maze_generator.cell_size // 2,
                        player_grid_x * maze_generator.cell_size + maze_generator.cell_size // 2,
                        player_grid_y * maze_generator.cell_size + maze_generator.cell_size // 2
                    )
                    if path_result and len(path_result) > 1:
                        # Convert path to pixel coordinates, skip current position
                        self.path_to_player = [
                            (pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2,
                             pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2 + MAZE_START_Y)
                            for pos in path_result[1:]  # Skip current position
                        ]
                    else:
                        self.path_to_player = []
                except Exception as e:
                    self.path_to_player = []
            
            # Follow the path if we have one
            if self.path_to_player:
                target_x, target_y = self.path_to_player[0]
                
                # Calculate direction to next waypoint
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 15:  # Close enough to waypoint, move to next one
                    self.path_to_player.pop(0)
                    if self.path_to_player:
                        target_x, target_y = self.path_to_player[0]
                        dx = target_x - self.x
                        dy = target_y - self.y
                
                # Normalize direction
                if distance > 0:
                    self.direction_x = dx / distance
                    self.direction_y = dy / distance
                else:
                    self.direction_x = 0
                    self.direction_y = 0
            else:
                # No path found, use simple movement toward player but avoid walls
                dx = player_x - self.x
                dy = player_y - self.y
                
                # Try different movement directions if direct path is blocked
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
                best_direction = None
                best_distance = float('inf')
                
                for dir_x, dir_y in directions:
                    test_x = self.x + dir_x * self.get_current_speed() * 2
                    test_y = self.y + dir_y * self.get_current_speed() * 2
                    
                    if not check_collision(test_x, test_y - MAZE_START_Y):
                        # Calculate distance to player from this direction
                        dist = math.sqrt((test_x - player_x)**2 + (test_y - player_y)**2)
                        if dist < best_distance:
                            best_distance = dist
                            best_direction = (dir_x, dir_y)
                
                if best_direction:
                    self.direction_x, self.direction_y = best_direction
                else:
                    # All directions blocked, try random movement
                    self.direction_x = random.choice([-1, 0, 1])
                    self.direction_y = random.choice([-1, 0, 1])
        else:
            # Use A* pathfinding for roaming toward goal (like tracking but toward goal)
            goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2
            goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2
            
            # Update path to goal periodically or if we don't have one
            self.path_update_timer += 1
            if self.path_update_timer >= 45 or not hasattr(self, 'path_to_goal') or not self.path_to_goal:  # Update every 0.75 seconds for roaming
                self.path_update_timer = 0
                
                try:
                    # Get path from current position to goal using A* pathfinding
                    current_grid_x = int(self.x // maze_generator.cell_size)
                    current_grid_y = int((self.y - MAZE_START_Y) // maze_generator.cell_size)
                    goal_grid_x = maze_generator.goal_pos[0]
                    goal_grid_y = maze_generator.goal_pos[1]
                    
                    # Ensure coordinates are within bounds
                    current_grid_x = max(0, min(maze_generator.maze_width - 1, current_grid_x))
                    current_grid_y = max(0, min(maze_generator.maze_height - 1, current_grid_y))
                    
                    path_result = pathfinder.find_path(
                        current_grid_x * maze_generator.cell_size + maze_generator.cell_size // 2,
                        current_grid_y * maze_generator.cell_size + maze_generator.cell_size // 2,
                        goal_x,
                        goal_y
                    )
                    
                    if path_result and len(path_result) > 1:
                        # Convert path to pixel coordinates, skip current position
                        self.path_to_goal = [
                            (pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2,
                             pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2 + MAZE_START_Y)
                            for pos in path_result[1:]  # Skip current position
                        ]
                    else:
                        self.path_to_goal = []
                except Exception as e:
                    self.path_to_goal = []
            
            # Follow the path to goal if we have one
            if hasattr(self, 'path_to_goal') and self.path_to_goal:
                target_x, target_y = self.path_to_goal[0]
                
                # Calculate direction to next waypoint
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 15:  # Close enough to waypoint, move to next one
                    self.path_to_goal.pop(0)
                    if self.path_to_goal:
                        target_x, target_y = self.path_to_goal[0]
                        dx = target_x - self.x
                        dy = target_y - self.y
                
                # Normalize direction
                if distance > 0:
                    self.direction_x = dx / distance
                    self.direction_y = dy / distance
                else:
                    self.direction_x = 0
                    self.direction_y = 0
            else:
                # Fallback to old method if A* pathfinding fails
                # Calculate direction toward goal
                dx = goal_x - self.x
                dy = (goal_y + MAZE_START_Y) - self.y
                distance = math.sqrt(dx*dx + dy*dy) if dx != 0 or dy != 0 else 1
                
                # Try to move toward goal, but if blocked, find alternative path
                target_dir_x = dx / distance
                target_dir_y = dy / distance
                
                # Test if direct movement toward goal is possible
                test_x = self.x + target_dir_x * self.get_current_speed()
                test_y = self.y + target_dir_y * self.get_current_speed()
                
                if not check_collision(test_x, test_y - MAZE_START_Y):
                    # Direct path to goal is clear
                    self.direction_x = target_dir_x
                    self.direction_y = target_dir_y
                else:
                    # Direct path blocked, try alternative directions that get closer to goal
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
                    best_direction = None
                    best_distance = float('inf')
                    
                    for dir_x, dir_y in directions:
                        test_x = self.x + dir_x * self.get_current_speed()
                        test_y = self.y + dir_y * self.get_current_speed()
                        
                        if not check_collision(test_x, test_y - MAZE_START_Y):
                            # Calculate distance to goal from this direction
                            dist_to_goal = math.sqrt((test_x - goal_x)**2 + ((test_y - MAZE_START_Y) - goal_y)**2)
                            if dist_to_goal < best_distance:
                                best_distance = dist_to_goal
                                best_direction = (dir_x, dir_y)
                    
                    if best_direction:
                        self.direction_x, self.direction_y = best_direction
                    else:
                        # All directions blocked, try random movement
                        self.direction_x = random.choice([-0.5, 0, 0.5])
                        self.direction_y = random.choice([-0.5, 0, 0.5])
        
        # Track visited positions to avoid backtracking
        current_grid_pos = (int(self.x // 20), int(self.y // 20))
        if current_grid_pos != self.last_position:
            self.visited_positions.append(current_grid_pos)
            if len(self.visited_positions) > 10:  # Keep only recent positions
                self.visited_positions.pop(0)
            self.last_position = current_grid_pos
        
        # Move in current direction with collision checking
        current_speed = self.get_current_speed()
        new_x = self.x + self.direction_x * current_speed
        new_y = self.y + self.direction_y * current_speed
        
        # Keep enemies within screen bounds
        new_x = max(ENEMY_SIZE, min(WIDTH - ENEMY_SIZE, new_x))
        new_y = max(MAZE_START_Y + ENEMY_SIZE, min(HEIGHT - ENEMY_SIZE, new_y))
        
        # Check collisions with more sophisticated movement
        can_move_x = not check_collision(new_x, self.y - MAZE_START_Y)
        can_move_y = not check_collision(self.x, new_y - MAZE_START_Y)
        can_move_both = not check_collision(new_x, new_y - MAZE_START_Y)
        
        # Check if new position would be backtracking (only if not tracking player)
        new_grid_pos = (int(new_x // 20), int(new_y // 20))
        is_backtracking = new_grid_pos in self.visited_positions[-5:] if not self.is_tracking else False
        
        moved = False
        
        # Try to move with improved collision handling
        if can_move_both and not is_backtracking:
            # Best case: can move diagonally
            self.x = new_x
            self.y = new_y
            moved = True
        elif can_move_x and not is_backtracking:
            # Can move horizontally
            self.x = new_x
            moved = True
        elif can_move_y and not is_backtracking:
            # Can move vertically
            self.y = new_y
            moved = True
        elif can_move_both:  # Allow backtracking if necessary
            self.x = new_x
            self.y = new_y
            moved = True
        elif can_move_x:
            self.x = new_x
            moved = True
        elif can_move_y:
            self.y = new_y
            moved = True
        
        # Enhanced stuck detection and recovery
        if not moved:
            self.stuck_counter += 1
            
            # If stuck for too long, try more aggressive recovery
            if self.stuck_counter > 20:  # Reduced from 30 to 20
                self.stuck_counter = 0
                self.visited_positions = []  # Clear memory to allow any movement
                
                # Try multiple escape directions with increasing distance
                escape_attempts = [
                    # First try adjacent cells
                    [(1, 0), (-1, 0), (0, 1), (0, -1)],
                    # Then try diagonal movements
                    [(1, 1), (-1, -1), (1, -1), (-1, 1)],
                    # Finally try larger steps
                    [(2, 0), (-2, 0), (0, 2), (0, -2)]
                ]
                
                escaped = False
                for attempt_set in escape_attempts:
                    if escaped:
                        break
                    random.shuffle(attempt_set)
                    
                    for dir_x, dir_y in attempt_set:
                        test_x = self.x + dir_x * self.get_current_speed()
                        test_y = self.y + dir_y * self.get_current_speed()
                        test_x = max(ENEMY_SIZE, min(WIDTH - ENEMY_SIZE, test_x))
                        test_y = max(MAZE_START_Y + ENEMY_SIZE, min(HEIGHT - ENEMY_SIZE, test_y))
                        
                        if not check_collision(test_x, test_y - MAZE_START_Y):
                            self.x = test_x
                            self.y = test_y
                            self.direction_x = dir_x / abs(dir_x) if dir_x != 0 else 0
                            self.direction_y = dir_y / abs(dir_y) if dir_y != 0 else 0
                            escaped = True
                            break
                
                # If still stuck, teleport to a nearby open area
                if not escaped:
                    self._emergency_relocate()
        else:
            self.stuck_counter = 0  # Reset stuck counter if we moved
        
        # Don't stay near the goal for too long (ensures player can reach it)
        goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size
        goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + MAZE_START_Y
        distance_to_goal = math.sqrt((self.x - goal_x)**2 + (self.y - goal_y)**2)
        
        if distance_to_goal < 60:  # If too close to goal
            self.safe_zone_timer += 1
            if self.safe_zone_timer > 120:  # After 2 seconds, move away
                self.direction_x = 1 if self.x < goal_x else -1
                self.direction_y = 1 if self.y < goal_y else -1
                self.safe_zone_timer = 0
                self.is_tracking = False  # Stop tracking when moving away from goal
                self.path_to_goal = []    # Clear goal path when forced to move away
                self.path_to_player = []  # Clear player path when forced to move away
        else:
            self.safe_zone_timer = 0
            
        # Final position validation - ensure enemy stays within valid bounds
        self.x = max(ENEMY_SIZE, min(WIDTH - ENEMY_SIZE, self.x))
        self.y = max(MAZE_START_Y + ENEMY_SIZE, min(HEIGHT - ENEMY_SIZE, self.y))
        
        self.rect = pygame.Rect(self.x - ENEMY_SIZE // 2, self.y - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)
    
    def _emergency_relocate(self):
        """Emergency relocation when enemy is completely stuck"""
        # Try to find a nearby open area
        for radius in range(40, 100, 20):  # Search in expanding circles
            for _ in range(20):  # Try 20 random positions at each radius
                angle = random.random() * 2 * math.pi
                test_x = self.x + radius * math.cos(angle)
                test_y = self.y + radius * math.sin(angle)
                
                # Keep within bounds
                test_x = max(ENEMY_SIZE, min(WIDTH - ENEMY_SIZE, test_x))
                test_y = max(MAZE_START_Y + ENEMY_SIZE, min(HEIGHT - ENEMY_SIZE, test_y))
                
                if not check_collision(test_x, test_y - MAZE_START_Y):
                    self.x = test_x
                    self.y = test_y
                    self.visited_positions = []  # Clear history
                    self.stuck_counter = 0
                    return
        
        # If still can't find a spot, move towards player starting position
        start_x, start_y = maze_generator.get_start_position()
        self.x = start_x
        self.y = start_y + MAZE_START_Y

    def draw(self):
        # Only draw if spawned
        if self.is_spawned:
            # Draw enemy with different color when tracking
            color = ORANGE if self.is_tracking else RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ENEMY_SIZE // 2)

# Hàm reset game
def reset_game():
    global player, enemies, running, game_won, game_lost, maze_generator, maze_surface, pathfinder, solution_path, start_time, distance_traveled, end_time, animation_progress
    
    # Generate new maze
    maze_generator = MazeGenerator(WIDTH, MAZE_HEIGHT, cell_size=20)
    maze_generator.generate_maze()
    maze_surface = maze_generator.create_surface()
    pathfinder = Pathfinder(maze_generator)
    solution_path = pathfinder.get_solution_path()
    
    # Ensure we have at least start and goal positions
    if not solution_path or len(solution_path) < 2:
        print("Warning: No solution path found, creating fallback path")
        start_x, start_y = maze_generator.get_start_position()
        goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2
        goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2
        solution_path = [(start_x, start_y), (goal_x, goal_y)]
    
    # Adjust solution path for UI offset - do this properly
    solution_path = [(x, y + MAZE_START_Y) for x, y in solution_path]
    
    player = Player()
    
    # Spawn enemies based on difficulty with delay
    enemies = []
    num_enemies = DIFFICULTY_SETTINGS[difficulty]["enemies"]
    for i in range(num_enemies):
        enemy = Enemy(difficulty)  # Pass difficulty level to enemy
        # Set spawn delay - each enemy spawns 3 seconds after the previous one
        enemy.spawn_timer = -(i * 180)  # Negative timer for delay
        enemies.append(enemy)
    
    running = True
    game_won = False
    game_lost = False
    start_time = time.time()
    end_time = 0
    distance_traveled = 0
    animation_progress = 0
    animation_wait_timer = 0

# Khởi tạo đối tượng
player = Player()
enemies = []
running = True
game_won = False
game_lost = False
clock = pygame.time.Clock()

def draw_modern_button(text, x, y, width, height, color, text_color, selected=False):
    """Draw a modern button with rounded corners and shadow"""
    # Shadow
    shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
    pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=10)
    
    # Button
    button_color = tuple(min(255, c + 30) for c in color) if selected else color
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    
    # Border
    border_color = WHITE if selected else LIGHT_GRAY
    pygame.draw.rect(screen, border_color, button_rect, width=2, border_radius=10)
    
    # Text
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, text_color)
    text_x = x + (width - text_surface.get_width()) // 2
    text_y = y + (height - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))

def draw_menu():
    """Draw the main menu"""
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(MODERN_BLUE[0] * (1 - color_ratio) + MODERN_PURPLE[0] * color_ratio)
        g = int(MODERN_BLUE[1] * (1 - color_ratio) + MODERN_PURPLE[1] * color_ratio)
        b = int(MODERN_BLUE[2] * (1 - color_ratio) + MODERN_PURPLE[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Title with shadow
    font_title = pygame.font.Font(None, 96)
    title_text = "MAZE RUNNER"
    
    # Shadow
    shadow_surface = font_title.render(title_text, True, BLACK)
    screen.blit(shadow_surface, (WIDTH//2 - shadow_surface.get_width()//2 + 3, 103))
    
    # Main title
    title_surface = font_title.render(title_text, True, WHITE)
    screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 100))
    
    # Subtitle
    font_sub = pygame.font.Font(None, 48)
    sub_text = font_sub.render("Escape the Maze!", True, LIGHT_GRAY)
    screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, 180))
    
    # Modern card for instructions
    card_rect = pygame.Rect(100, 250, WIDTH - 200, 300)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=15)
    pygame.draw.rect(screen, LIGHT_GRAY, card_rect, width=2, border_radius=15)
    
    # Instructions
    font_inst = pygame.font.Font(None, 32)
    instructions = [
        "Use WASD or Arrow Keys to move",
        "Reach the RED FLAG to win!",
        "Avoid the red enemies",
        "Follow the green solution path"
    ]
    
    for i, instruction in enumerate(instructions):
        inst_text = font_inst.render(instruction, True, DARK_GRAY)
        screen.blit(inst_text, (120, 280 + i * 50))
    
    # Start button
    draw_modern_button("PRESS SPACE TO START", WIDTH//2 - 150, 600, 300, 60, MODERN_GREEN, WHITE)

def draw_difficulty_menu():
    """Draw the difficulty selection menu"""
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(MODERN_GREEN[0] * (1 - color_ratio) + MODERN_BLUE[0] * color_ratio)
        g = int(MODERN_GREEN[1] * (1 - color_ratio) + MODERN_BLUE[1] * color_ratio)
        b = int(MODERN_GREEN[2] * (1 - color_ratio) + MODERN_BLUE[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Title
    font_title = pygame.font.Font(None, 84)
    title_text = font_title.render("SELECT DIFFICULTY", True, WHITE)
    # Shadow
    shadow_surface = font_title.render("SELECT DIFFICULTY", True, BLACK)
    screen.blit(shadow_surface, (WIDTH//2 - shadow_surface.get_width()//2 + 2, 102))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    # Difficulty cards
    card_width = 200
    card_height = 120
    start_x = (WIDTH - (card_width * 3 + 40)) // 2
    
    for diff_level, settings in DIFFICULTY_SETTINGS.items():
        x = start_x + (diff_level - 1) * (card_width + 20)
        y = 300
        
        selected = diff_level == difficulty
        card_color = MODERN_ORANGE if selected else WHITE
        text_color = WHITE if selected else DARK_GRAY
        
        # Card
        card_rect = pygame.Rect(x, y, card_width, card_height)
        if selected:
            # Glow effect
            glow_rect = pygame.Rect(x - 5, y - 5, card_width + 10, card_height + 10)
            pygame.draw.rect(screen, MODERN_ORANGE, glow_rect, border_radius=20)
        
        pygame.draw.rect(screen, card_color, card_rect, border_radius=15)
        pygame.draw.rect(screen, MODERN_ORANGE if selected else LIGHT_GRAY, card_rect, width=3, border_radius=15)
        
        # Difficulty info
        font_num = pygame.font.Font(None, 72)
        font_name = pygame.font.Font(None, 36)
        font_enemies = pygame.font.Font(None, 28)
        
        num_text = font_num.render(str(diff_level), True, text_color)
        name_text = font_name.render(settings['name'], True, text_color)
        enemies_text = font_enemies.render(f"{settings['enemies']} enemies", True, text_color)
        
        screen.blit(num_text, (x + (card_width - num_text.get_width()) // 2, y + 10))
        screen.blit(name_text, (x + (card_width - name_text.get_width()) // 2, y + 60))
        screen.blit(enemies_text, (x + (card_width - enemies_text.get_width()) // 2, y + 90))
    
    # Instructions
    font_inst = pygame.font.Font(None, 36)
    inst_text = font_inst.render("Press 1, 2, or 3 to select", True, WHITE)
    screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, 500))
    
    # Start button
    draw_modern_button("PRESS ENTER TO START", WIDTH//2 - 150, 600, 300, 60, MODERN_GREEN, WHITE)

def draw_solution_path():
    """Draw the green solution path like user trail"""
    if solution_path and len(solution_path) > 0:
        # Create a surface for transparency
        path_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, (x, y) in enumerate(solution_path):
            # Semi-transparent green circles for solution path
            pygame.draw.circle(path_surface, (0, 200, 0, 120), (int(x), int(y)), 4)
        screen.blit(path_surface, (0, 0))

def draw_animated_solution_path(progress):
    """Draw animated solution path for death animation - smooth trail like player trail with fading"""
    if solution_path and len(solution_path) > 1:
        # Calculate how many points to show based on progress
        total_points = len(solution_path)
        points_to_show = int(progress * total_points)
        
        if points_to_show >= 2:
            # Create a surface for the animated trail
            trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            
            # Draw smooth trail connecting points (like player trail)
            trail_points = solution_path[:points_to_show]
            for i in range(len(trail_points) - 1):
                start_pos = trail_points[i]
                end_pos = trail_points[i + 1]
                
                # Calculate fade effect (newer segments are more opaque)
                segment_alpha = int(255 * (i + 1) / len(trail_points))
                segment_alpha = min(200, segment_alpha)  # Cap at 200 for visibility
                
                # Bright green line for the animated solution path with fading
                pygame.draw.line(trail_surface, (0, 255, 0, segment_alpha), start_pos, end_pos, 6)
            
            # Draw circles at each point for visibility with fading
            for i, point in enumerate(trail_points):
                # Calculate alpha for each point (fade out older points)
                point_alpha = int(255 * (i + 1) / len(trail_points))
                point_alpha = min(255, point_alpha)
                pygame.draw.circle(trail_surface, (0, 255, 0, point_alpha), (int(point[0]), int(point[1])), 3)
            
            screen.blit(trail_surface, (0, 0))
    else:
        # Fallback: create a simple path from start to goal
        start_x, start_y = maze_generator.get_start_position()
        goal_x = maze_generator.goal_pos[0] * maze_generator.cell_size + maze_generator.cell_size // 2
        goal_y = maze_generator.goal_pos[1] * maze_generator.cell_size + maze_generator.cell_size // 2
        
        # Adjust for UI offset
        start_y += MAZE_START_Y
        goal_y += MAZE_START_Y
        
        # Draw a simple line animation from start to goal
        trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        end_x = start_x + (goal_x - start_x) * progress
        end_y = start_y + (goal_y - start_y) * progress
        pygame.draw.line(trail_surface, (0, 255, 0, 200), (start_x, start_y), (int(end_x), int(end_y)), 6)
        screen.blit(trail_surface, (0, 0))

def draw_game_over():
    """Draw modern game over screen"""
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(MODERN_RED[0] * (1 - color_ratio) + BLACK[0] * color_ratio)
        g = int(MODERN_RED[1] * (1 - color_ratio) + BLACK[1] * color_ratio)
        b = int(MODERN_RED[2] * (1 - color_ratio) + BLACK[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Modern card for game over content
    card_rect = pygame.Rect(100, 100, WIDTH - 200, HEIGHT - 200)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=20)
    pygame.draw.rect(screen, MODERN_RED, card_rect, width=4, border_radius=20)
    
    # Game Over text with shadow
    font_title = pygame.font.Font(None, 84)
    title_text = "GAME OVER"
    
    # Shadow
    shadow_surface = font_title.render(title_text, True, DARK_GRAY)
    screen.blit(shadow_surface, (WIDTH//2 - shadow_surface.get_width()//2 + 3, 153))
    
    # Main title
    game_over_text = font_title.render(title_text, True, MODERN_RED)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 150))
    
    # Stats section
    font_stats = pygame.font.Font(None, 36)
    elapsed_time = end_time - start_time if end_time > 0 else time.time() - start_time
    stats = [
        f"Time: {elapsed_time:.1f} seconds",
        f"Distance: {distance_traveled:.0f} pixels",
        f"Difficulty: {DIFFICULTY_SETTINGS[difficulty]['name']}"
    ]
    
    for i, stat in enumerate(stats):
        stat_text = font_stats.render(stat, True, DARK_GRAY)
        screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, 250 + i * 50))
    
    # Modern restart buttons
    draw_modern_button("RESTART (R)", WIDTH//2 - 200, 450, 180, 50, MODERN_GREEN, WHITE)
    draw_modern_button("MENU (ESC)", WIDTH//2 + 20, 450, 180, 50, MODERN_BLUE, WHITE)

def draw_game_won():
    """Draw modern game won screen"""
    # Gradient background
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(MODERN_GREEN[0] * (1 - color_ratio) + MODERN_BLUE[0] * color_ratio)
        g = int(MODERN_GREEN[1] * (1 - color_ratio) + MODERN_BLUE[1] * color_ratio)
        b = int(MODERN_GREEN[2] * (1 - color_ratio) + MODERN_BLUE[2] * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Modern card for victory content
    card_rect = pygame.Rect(100, 100, WIDTH - 200, HEIGHT - 200)
    pygame.draw.rect(screen, WHITE, card_rect, border_radius=20)
    pygame.draw.rect(screen, MODERN_GREEN, card_rect, width=4, border_radius=20)
    
    # Victory text with shadow
    font_title = pygame.font.Font(None, 84)
    title_text = "VICTORY!"
    
    # Shadow
    shadow_surface = font_title.render(title_text, True, DARK_GRAY)
    screen.blit(shadow_surface, (WIDTH//2 - shadow_surface.get_width()//2 + 3, 153))
    
    # Main title
    victory_text = font_title.render(title_text, True, MODERN_GREEN)
    screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, 150))
    
    # Congratulations message
    font_congrats = pygame.font.Font(None, 42)
    congrats_text = font_congrats.render("Congratulations! You escaped!", True, MODERN_PURPLE)
    screen.blit(congrats_text, (WIDTH//2 - congrats_text.get_width()//2, 210))
    
    # Stats section
    font_stats = pygame.font.Font(None, 36)
    elapsed_time = end_time - start_time if end_time > 0 else time.time() - start_time
    stats = [
        f"Time: {elapsed_time:.1f} seconds",
        f"Distance: {distance_traveled:.0f} pixels",
        f"Difficulty: {DIFFICULTY_SETTINGS[difficulty]['name']}"
    ]
    
    for i, stat in enumerate(stats):
        stat_text = font_stats.render(stat, True, DARK_GRAY)
        screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, 280 + i * 40))
    
    # Modern restart buttons
    draw_modern_button("PLAY AGAIN (R)", WIDTH//2 - 200, 450, 180, 50, MODERN_GREEN, WHITE)
    draw_modern_button("MENU (ESC)", WIDTH//2 + 20, 450, 180, 50, MODERN_BLUE, WHITE)

def setup():
    global running, game_won, game_lost
    running = True
    game_won = False
    game_lost = False

async def update_loop():
    global running, game_won, game_lost, game_state, difficulty, end_time
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key == pygame.K_SPACE:
                        game_state = DIFFICULTY
                elif game_state == DIFFICULTY:
                    if event.key == pygame.K_1:
                        difficulty = 1
                    elif event.key == pygame.K_2:
                        difficulty = 2
                    elif event.key == pygame.K_3:
                        difficulty = 3
                    elif event.key == pygame.K_RETURN:
                        game_state = PLAYING
                        reset_game()
                elif game_state == PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        game_state = MENU
                elif game_state in [GAME_OVER, GAME_WON]:
                    if event.key == pygame.K_r:
                        game_state = PLAYING
                        reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        game_state = MENU
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == PLAYING:
                # Click to remove enemy (optional feature) - only spawned enemies
                mouse_pos = pygame.mouse.get_pos()
                for enemy in enemies[:]:
                    if enemy.is_spawned and enemy.rect.collidepoint(mouse_pos):
                        enemies.remove(enemy)

        # Game logic
        if game_state == PLAYING and not game_won and not game_lost:
            # Player movement
            keys = pygame.key.get_pressed()
            collision_result = player.move(keys)
            
            # Check if player reached the goal (red flag)
            if collision_result == "goal":
                game_won = True
                game_state = GAME_WON
                end_time = time.time()  # Stop timer

            # Move enemies
            for enemy in enemies[:]:
                enemy.move(player.x, player.y)
                
                # Check collision with player only if enemy is spawned
                if enemy.is_spawned and enemy.rect.colliderect(player.rect):
                    game_lost = True
                    game_state = DEATH_ANIMATION
                    end_time = time.time()  # Stop timer
                    animation_progress = 0  # Reset animation
                    animation_wait_timer = 0  # Reset wait timer
        
        elif game_state == DEATH_ANIMATION:
            # Update death animation
            animation_progress += animation_speed / 100.0
            if animation_progress >= 1.0:
                # Animation complete, wait 1 second before showing game over
                animation_wait_timer += 1
                if animation_wait_timer >= 60:  # 1 second at 60 FPS
                    game_state = GAME_OVER

        # Drawing
        if game_state == MENU:
            draw_menu()
        elif game_state == DIFFICULTY:
            draw_difficulty_menu()
        elif game_state == PLAYING:
            screen.fill(WHITE)
            screen.blit(maze_surface, (0, MAZE_START_Y))
            
            # Don't draw solution path during normal gameplay
            # draw_solution_path()  # Commented out - only show on death
            
            player.draw()
            
            for enemy in enemies:
                enemy.draw()
                
            # Draw UI with better colors - more compact layout
            font = pygame.font.Font(None, 24)
            elapsed_time = time.time() - start_time
            
            # Create text with background for better visibility
            def draw_text_with_bg(text, color, bg_color, x, y):
                text_surface = font.render(text, True, color)
                bg_surface = pygame.Surface((text_surface.get_width() + 8, text_surface.get_height() + 2))
                bg_surface.fill(bg_color)
                bg_surface.set_alpha(180)
                screen.blit(bg_surface, (x - 4, y - 1))
                screen.blit(text_surface, (x, y))
            
            # First row
            draw_text_with_bg(f"Time: {elapsed_time:.1f}s", YELLOW, BLACK, 10, 10)
            draw_text_with_bg(f"Distance: {distance_traveled:.0f}", CYAN, BLACK, 150, 10)
            draw_text_with_bg(f"Enemies: {len([e for e in enemies if e.is_spawned])}", ORANGE, BLACK, 320, 10)
            
            # Second row
            draw_text_with_bg("Purple: Trail | Green: Solution | Orange: Hunting | Red: Goal-seeking", WHITE, DARK_GRAY, 10, 35)
            draw_text_with_bg("ESC: Menu", LIGHT_GRAY, BLACK, 580, 35)
        
        elif game_state == DEATH_ANIMATION:
            screen.fill(WHITE)
            screen.blit(maze_surface, (0, MAZE_START_Y))
            
            # Draw animated solution path
            draw_animated_solution_path(animation_progress)
            
            player.draw()
            
            for enemy in enemies:
                enemy.draw()
            
            # Draw death message
            font_death = pygame.font.Font(None, 48)
            death_text = font_death.render("Following the solution path...", True, BLACK)
            death_bg = pygame.Surface((death_text.get_width() + 20, death_text.get_height() + 10))
            death_bg.fill(WHITE)
            death_bg.set_alpha(200)
            screen.blit(death_bg, (WIDTH//2 - death_text.get_width()//2 - 10, 50))
            screen.blit(death_text, (WIDTH//2 - death_text.get_width()//2, 55))
            
        elif game_state == GAME_OVER:
            draw_game_over()
        elif game_state == GAME_WON:
            draw_game_won()
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(update_loop())
else:
    if __name__ == "__main__":
        print("Starting Maze Runner Game...")
        print("Controls: WASD or Arrow Keys to move")
        print("Goal: Reach the RED FLAG to win!")
        print("Avoid the red enemies!")
        asyncio.run(update_loop())