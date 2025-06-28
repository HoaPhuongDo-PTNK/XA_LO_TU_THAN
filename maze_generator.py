import pygame
import random
from collections import deque
import math

class MazeGenerator:
    def __init__(self, width, height, cell_size=20):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.maze_width = width // cell_size
        self.maze_height = height // cell_size
        
        # Ensure odd dimensions for proper maze generation
        if self.maze_width % 2 == 0:
            self.maze_width -= 1
        if self.maze_height % 2 == 0:
            self.maze_height -= 1
        
        # Colors
        self.BLACK = (0, 0, 0)  # Walls
        self.WHITE = (255, 255, 255)  # Paths
        self.RED = (255, 0, 0)  # Goal/Flag
        self.GREEN = (0, 255, 0)  # Start position
        
        # Create maze grid (True = wall, False = path)
        self.maze = [[True for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        self.start_pos = (1, 1)
        self.goal_pos = (self.maze_width - 2, self.maze_height - 2)
        
    def generate_maze(self):
        """Generate maze using Recursive Backtracking algorithm for proper maze structure"""
        # Initialize all cells as walls
        self.maze = [[True for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        
        # Start recursive backtracking from (1,1)
        self._recursive_backtrack(1, 1)
        
        # Ensure start and goal positions are clear
        self.maze[self.start_pos[1]][self.start_pos[0]] = False
        self.maze[self.goal_pos[1]][self.goal_pos[0]] = False
        
        # Add some strategic complexity to prevent trivial solutions
        self._prevent_trivial_solutions()
        
        # Ensure connectivity
        self._ensure_connectivity()
    
    def _recursive_backtrack(self, start_x, start_y):
        """Recursive backtracking maze generation algorithm"""
        # Stack for backtracking
        stack = [(start_x, start_y)]
        
        # Mark starting cell as path
        self.maze[start_y][start_x] = False
        
        # Directions: right, down, left, up (dx, dy)
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Find unvisited neighbors (2 cells away to maintain wall structure)
            neighbors = []
            for dx, dy in directions:
                next_x, next_y = current_x + dx, current_y + dy
                
                # Check if neighbor is within bounds and is a wall (unvisited)
                if (1 <= next_x < self.maze_width - 1 and 
                    1 <= next_y < self.maze_height - 1 and 
                    self.maze[next_y][next_x]):
                    neighbors.append((next_x, next_y, dx, dy))
            
            if neighbors:
                # Choose random neighbor
                next_x, next_y, dx, dy = random.choice(neighbors)
                
                # Remove wall between current and next cell
                wall_x = current_x + dx // 2
                wall_y = current_y + dy // 2
                self.maze[wall_y][wall_x] = False
                
                # Mark next cell as visited (path)
                self.maze[next_y][next_x] = False
                
                # Add to stack for further exploration
                stack.append((next_x, next_y))
            else:
                # No unvisited neighbors, backtrack
                stack.pop()
    
    def _prevent_trivial_solutions(self):
        """Add strategic walls to prevent trivial direct paths to goal"""
        # Find current path length to goal
        current_path_length = self._get_path_length()
        
        # Calculate minimum desired path length (should be at least 1.5x Manhattan distance)
        manhattan_dist = abs(self.goal_pos[0] - self.start_pos[0]) + abs(self.goal_pos[1] - self.start_pos[1])
        min_desired_length = int(manhattan_dist * 1.5)
        
        # If current path is too short, try to add strategic blocks
        if current_path_length > 0 and current_path_length < min_desired_length:
            self._add_strategic_blocks()
    
    def _get_path_length(self):
        """Get the length of the shortest path from start to goal"""
        # Simple BFS to find shortest path length
        from collections import deque
        
        queue = deque([(self.start_pos[0], self.start_pos[1], 0)])
        visited = set()
        visited.add(self.start_pos)
        
        while queue:
            x, y, dist = queue.popleft()
            
            if (x, y) == self.goal_pos:
                return dist
            
            # Check 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                
                if (0 <= next_x < self.maze_width and 
                    0 <= next_y < self.maze_height and
                    not self.maze[next_y][next_x] and
                    (next_x, next_y) not in visited):
                    
                    visited.add((next_x, next_y))
                    queue.append((next_x, next_y, dist + 1))
        
        return 0  # No path found
    
    def _add_strategic_blocks(self):
        """Add walls to create a more complex path"""
        # Get current path
        path = self._get_current_path()
        if not path or len(path) < 4:
            return
        
        # Try to block some middle segments of the path
        blocks_added = 0
        max_blocks = 3
        
        # Skip start and end portions, try to block middle parts
        middle_start = len(path) // 4
        middle_end = 3 * len(path) // 4
        
        for i in range(middle_start, middle_end, 2):
            if blocks_added >= max_blocks:
                break
                
            x, y = path[i]
            
            # Find adjacent cells that we could potentially block
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                block_x, block_y = x + dx, y + dy
                
                if (1 <= block_x < self.maze_width - 1 and 
                    1 <= block_y < self.maze_height - 1 and
                    not self.maze[block_y][block_x] and
                    (block_x, block_y) != self.start_pos and
                    (block_x, block_y) != self.goal_pos):
                    
                    # Try blocking this cell
                    self.maze[block_y][block_x] = True
                    
                    # Check if goal is still reachable
                    if self._get_path_length() > 0:
                        blocks_added += 1
                        break  # Successfully added a block
                    else:
                        # Restore if it breaks connectivity
                        self.maze[block_y][block_x] = False
    
    def _get_current_path(self):
        """Get the current shortest path from start to goal"""
        from collections import deque
        
        queue = deque([(self.start_pos[0], self.start_pos[1], [(self.start_pos[0], self.start_pos[1])])])
        visited = set()
        visited.add(self.start_pos)
        
        while queue:
            x, y, path = queue.popleft()
            
            if (x, y) == self.goal_pos:
                return path
            
            # Check 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                
                if (0 <= next_x < self.maze_width and 
                    0 <= next_y < self.maze_height and
                    not self.maze[next_y][next_x] and
                    (next_x, next_y) not in visited):
                    
                    visited.add((next_x, next_y))
                    new_path = path + [(next_x, next_y)]
                    queue.append((next_x, next_y, new_path))
        
        return []  # No path found
    
    def _ensure_connectivity(self):
        """Ensure start and goal are connected"""
        if self._get_path_length() == 0:
            # Create a simple connection
            self._create_direct_path()
    
    def _create_direct_path(self):
        """Create a direct path from start to goal as fallback"""
        current_x, current_y = self.start_pos
        goal_x, goal_y = self.goal_pos
        
        # Create L-shaped path: horizontal then vertical
        # Horizontal movement
        while current_x != goal_x:
            self.maze[current_y][current_x] = False
            if current_x < goal_x:
                current_x += 1
            else:
                current_x -= 1
        
        # Vertical movement
        while current_y != goal_y:
            self.maze[current_y][current_x] = False
            if current_y < goal_y:
                current_y += 1
            else:
                current_y -= 1
        
        # Ensure goal is reachable
        self.maze[goal_y][goal_x] = False
    
    def create_surface(self):
        """Create a pygame surface with the maze"""
        surface = pygame.Surface((self.width, self.height))
        surface.fill(self.WHITE)
        
        # Draw walls
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.maze[y][x]:  # Wall
                    pygame.draw.rect(surface, self.BLACK, 
                                   (x * self.cell_size, y * self.cell_size, 
                                    self.cell_size, self.cell_size))
        
        # Draw goal (red flag)
        goal_x = self.goal_pos[0] * self.cell_size
        goal_y = self.goal_pos[1] * self.cell_size
        pygame.draw.rect(surface, self.RED, 
                        (goal_x, goal_y, self.cell_size, self.cell_size))
        
        return surface
    
    def get_start_position(self):
        """Get starting position in pixel coordinates"""
        return (self.start_pos[0] * self.cell_size + self.cell_size // 2,
                self.start_pos[1] * self.cell_size + self.cell_size // 2)
    
    def is_wall(self, x, y):
        """Check if position is a wall"""
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        if 0 <= grid_x < self.maze_width and 0 <= grid_y < self.maze_height:
            return self.maze[grid_y][grid_x]
        return True  # Outside bounds = wall
    
    def is_goal(self, x, y):
        """Check if position is the goal"""
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        return (grid_x, grid_y) == self.goal_pos

class Pathfinder:
    def __init__(self, maze_generator):
        self.maze = maze_generator
        
    def find_path(self, start_x, start_y, target_x, target_y):
        """Find path using A* algorithm"""
        start_grid = (int(start_x // self.maze.cell_size), int(start_y // self.maze.cell_size))
        target_grid = (int(target_x // self.maze.cell_size), int(target_y // self.maze.cell_size))
        
        # A* algorithm
        open_set = [(0, start_grid)]
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self.heuristic(start_grid, target_grid)}
        
        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            open_set = [item for item in open_set if item[1] != current]
            
            if current == target_grid:
                # Reconstruct path - include start position
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Skip if out of bounds or wall
                if (neighbor[0] < 0 or neighbor[0] >= self.maze.maze_width or
                    neighbor[1] < 0 or neighbor[1] >= self.maze.maze_height or
                    self.maze.maze[neighbor[1]][neighbor[0]]):
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, target_grid)
                    
                    if (f_score[neighbor], neighbor) not in open_set:
                        open_set.append((f_score[neighbor], neighbor))
        
        return []  # No path found
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_solution_path(self):
        """Get the correct solution path from start to goal"""
        start_x, start_y = self.maze.get_start_position()
        goal_x = self.maze.goal_pos[0] * self.maze.cell_size + self.maze.cell_size // 2
        goal_y = self.maze.goal_pos[1] * self.maze.cell_size + self.maze.cell_size // 2
        
        path = self.find_path(start_x, start_y, goal_x, goal_y)
        
        # Convert grid coordinates to pixel coordinates
        pixel_path = []
        for grid_x, grid_y in path:
            pixel_x = grid_x * self.maze.cell_size + self.maze.cell_size // 2
            pixel_y = grid_y * self.maze.cell_size + self.maze.cell_size // 2
            pixel_path.append((pixel_x, pixel_y))
        
        return pixel_path
    
    def get_direction_to_target(self, start_x, start_y, target_x, target_y):
        """Get direction vector towards target using pathfinding"""
        path = self.find_path(start_x, start_y, target_x, target_y)
        if len(path) > 0:
            next_grid = path[0]
            next_x = next_grid[0] * self.maze.cell_size + self.maze.cell_size // 2
            next_y = next_grid[1] * self.maze.cell_size + self.maze.cell_size // 2
            
            # Calculate direction
            dx = next_x - start_x
            dy = next_y - start_y
            
            # Normalize
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                return dx / distance, dy / distance
        
        return 0, 0
