from maze_generator import MazeGenerator
import pygame
pygame.init()

# Test the new maze generation
maze = MazeGenerator(800, 720, 20)
maze.generate_maze()
print('Maze generated successfully!')
print(f'Start position: {maze.start_pos}')
print(f'Goal position: {maze.goal_pos}')

# Quick connectivity test
visited = [[False for _ in range(maze.maze_width)] for _ in range(maze.maze_height)]
def flood_fill(x, y):
    if (x < 0 or x >= maze.maze_width or y < 0 or y >= maze.maze_height or visited[y][x] or maze.maze[y][x]):
        return 0
    visited[y][x] = True
    count = 1
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        count += flood_fill(x + dx, y + dy)
    return count

reachable_cells = flood_fill(maze.start_pos[0], maze.start_pos[1])
print(f'Reachable cells from start: {reachable_cells}')
print(f'Goal reachable: {visited[maze.goal_pos[1]][maze.goal_pos[0]]}')