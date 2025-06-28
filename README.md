# 🏃‍♂️ Pygame Maze Game

A modern, feature-rich maze game built with Pygame featuring procedural maze generation, intelligent enemy AI with A* pathfinding, visual trails, and smooth animations.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)

## 🎮 Features

### Core Gameplay
- **Procedural Maze Generation**: Each game generates a unique, challenging maze with multiple paths and dead ends
- **Always Solvable**: Mazes are guaranteed to have a solution path but include many wrong routes and dead ends
- **Visual Feedback**: Player and enemy trails with smooth fading effects
- **Solution Path**: Animated green path shows the solution when you lose (only on death)
- **Performance Tracking**: Real-time timer and distance counter

### 🤖 Smart Enemy AI
- **Dynamic Behavior**: Enemies alternate between goal-seeking movement and intelligent player tracking
- **A* Pathfinding**: When tracking, enemies use A* algorithm to navigate the maze efficiently
- **Tracking Cycles**: Every 6 seconds, enemies track the player for 6 seconds (indicated by orange color)
- **Adaptive Speed**: Enemy speed varies by difficulty - Easy: 15% faster, Medium: 20% faster, Hard: 25% faster when tracking
- **Goal-Seeking Movement**: When not tracking, enemies move toward the goal at 85% of player speed
- **Smart Spawning**: Enemies spawn at the player's starting position with a brief delay
- **Anti-Blocking**: Enemies are designed to never permanently block the exit
- **Memory System**: Enemies remember recent moves to avoid getting stuck in loops

### 🎨 Modern UI/UX
- **Gradient Backgrounds**: Beautiful color gradients for visual appeal
- **Rounded Elements**: Modern card-style UI with rounded corners
- **Non-Intrusive HUD**: Game information displayed without blocking gameplay
- **Overlay System**: Game over and victory screens appear above the maze
- **Responsive Design**: UI adapts to different maze sizes

### ✨ Visual Effects
- **Smooth Animations**: All movements and effects are fluid and polished
- **Trail Effects**: Purple player trail and red enemy trails with fade-out
- **Death Animation**: Solution path animates smoothly when the player loses
- **Color Coding**: 
  - Blue: Player
  - Red: Enemies (goal-seeking mode)
  - Orange: Enemies (tracking/hunting mode)
  - Purple: Player trail
  - Green: Solution path (death only)
  - Yellow: Goal

## 🎯 Controls

- **Arrow Keys** or **WASD**: Move the player
- **R**: Restart the game with a new maze
- **ESC**: Quit the game

## 🚀 Installation

1. **Install Python 3.7+**
2. **Install Pygame**:
   ```bash
   pip install pygame
   ```
   Or install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the Game

```bash
python main.py
```

## 🎮 Game Mechanics

### Objective
Navigate from the blue starting position to the yellow goal while avoiding red enemies.

### Enemy Behavior
- **Goal-Seeking Phase (Red)**: Enemies move toward the goal at 85% of player speed, creating constant pressure
- **Tracking Phase (Orange)**: Every 6 seconds, enemies actively hunt the player for 6 seconds
- **Pathfinding**: Enemies use intelligent A* pathfinding to navigate around walls
- **Difficulty-Based Speed**: 
  - Easy: 15% faster than player when tracking
  - Medium: 20% faster than player when tracking  
  - Hard: 25% faster than player when tracking
- **Timing**: After tracking ends, enemies always wait a full 6 seconds before tracking again

### Scoring
- **Time**: How long you survived or took to complete the maze
- **Distance**: Total distance traveled (measured in grid cells)
- **Difficulty**: Based on maze size and enemy count

## ⚙️ Technical Details

### Maze Generation
- Uses a recursive backtracking algorithm with additional complexity layers
- Creates multiple branching paths, dead ends, and wrong routes to challenge players
- Strategically places dead end branches off main paths for maximum confusion
- Guarantees a solution path exists from start to goal
- Optimized for challenging but fair gameplay with multiple route choices

### Pathfinding
- **Player Movement**: Direct grid-based movement with collision detection
- **Enemy AI**: A* algorithm for optimal pathfinding through the maze
- **Solution Display**: Dijkstra's algorithm finds the shortest path for the solution visualization

### Performance
- Efficient rendering with minimal CPU usage
- Smooth 60 FPS gameplay
- Optimized collision detection and pathfinding

## 🛠️ Customization

The game can be easily modified by adjusting constants in `main.py`:

```python
# Maze dimensions
MAZE_WIDTH = 25
MAZE_HEIGHT = 20

# Enemy settings
NUM_ENEMIES = 3
ENEMY_TRACKING_DURATION = 360  # 6 seconds at 60 FPS
ENEMY_CHANCE_INTERVAL = 360    # 6 seconds at 60 FPS
DIFFICULTY_SETTINGS = {
    1: {"enemies": 1, "enemy_speed_multiplier": 1.15},  # Easy: 15% faster
    2: {"enemies": 2, "enemy_speed_multiplier": 1.20},  # Medium: 20% faster
    3: {"enemies": 3, "enemy_speed_multiplier": 1.25}   # Hard: 25% faster
}

# Visual settings
CELL_SIZE = 25
TRAIL_FADE_SPEED = 5
SOLUTION_ANIMATION_SPEED = 3
```

## 📁 Files

- **`main.py`**: Main game logic, rendering, and game loop
- **`maze_generator.py`**: Maze generation and pathfinding algorithms
- **`requirements.txt`**: Python package dependencies
- **`test_game.py`**: Test script for maze generation and pathfinding

## 📦 Dependencies

- **Pygame**: For graphics, input handling, and game loop
- **Random**: For procedural generation and enemy AI
- **Heapq**: For A* pathfinding implementation
- **Collections**: For deque data structures in pathfinding

## 🔍 Features in Detail

### Trail System
- **Player Trail**: Purple squares that fade out over time, showing your path
- **Enemy Trails**: Red squares that mark enemy movement paths
- **Smooth Fading**: All trails use alpha blending for smooth visual effects

### Solution Path Animation
- **Trigger**: Only appears when the player dies (touches an enemy)
- **Animation**: Green path animates from start to goal
- **Timing**: 1-second delay after animation completes before showing game over screen
- **Algorithm**: Uses Dijkstra's algorithm to find the optimal solution

### Enemy AI States
1. **Goal-Seeking (Red)**: Enemies move toward the goal at 85% player speed, always creating pressure
2. **Tracking (Orange)**: Active pursuit of player using A* pathfinding at difficulty-based speeds
3. **Cooldown**: 6-second wait between tracking phases

### UI Elements
- **Real-time Stats**: Timer and distance in the top-left corner
- **Game Over Screen**: Shows final stats and restart option
- **Victory Screen**: Celebrates successful maze completion
- **Modern Styling**: Gradient backgrounds and rounded UI elements

## 🎯 Strategy Tips

- **Watch the Colors**: Red enemies are seeking the goal, orange enemies are actively hunting you
- **Use Dead Ends**: The maze now has many dead ends - use them to confuse enemies but don't get trapped
- **Route Planning**: Multiple paths exist - explore to find the best route while avoiding enemies
- **Use the Walls**: Break line of sight to confuse enemy pathfinding
- **Trail Awareness**: Your purple trail helps you avoid going in circles
- **Timing**: Learn the enemy tracking cycle (6 seconds goal-seeking, 6 seconds tracking)
- **Difficulty Awareness**: Higher difficulties have faster enemies when tracking
- **Solution Path**: When you die, watch the green animation to learn the optimal route

## 🐛 Bug Fixes Implemented

- ✅ Fixed enemy getting stuck in corners or loops
- ✅ Fixed enemy tracking timer not resetting properly after tracking ends
- ✅ Fixed solution path visibility during gameplay
- ✅ Fixed collision detection accuracy for all entities
- ✅ Fixed UI elements overlapping with maze rendering
- ✅ Fixed enemy spawning and initial positioning
- ✅ Fixed animation timing and smoothness

## 🚀 Performance Optimizations

- Efficient maze generation algorithm
- Optimized A* pathfinding with early termination
- Smart rendering with minimal redraw operations
- Trail system with alpha blending optimization
- Memory-efficient enemy AI with path caching

This maze game combines classic gameplay with modern features, creating an engaging and polished gaming experience that's both challenging and visually appealing. The intelligent enemy AI, smooth animations, and modern UI make it a standout implementation of the classic maze genre.
