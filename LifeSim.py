import pygame
from pygame.locals import *
from pygame.math import Vector2
import random, math, itertools, colorsys

# Screen
screensize = 800
screen = pygame.display.set_mode((screensize, screensize))
pygame.display.set_caption("ThisLittleLife")

n = 1250  # Increased particle count to 1250
dt = 0.015  # Slightly increased dt for slower update frequency
frictionHLF = 0.015
rMax = 0.25  # Adjusted interaction range
m = 6

def makeRandomMatrix():
    rows = []
    for i in range(m):
        row = []
        for j in range(m):
            row.append(random.random() * 15 - 7.5)
        rows.append(row)
    return rows

matrix = makeRandomMatrix()
frictionFactor = math.pow(0.5, dt / frictionHLF)

colors = []
positions = []
velocities = []

# Define a set of 6 distinct colors
color_set = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255)   # Magenta
]

for i in range(n):
    colors.append(color_set[i % m])  # Assign colors from the color set
    positions.append(Vector2(random.random(), random.random()))
    velocities.append(Vector2(0, 0))

# Grid-based spatial partitioning
grid_size = 10  # Smaller grid size for better performance
grid = {}

def get_grid_position(position):
    return (int(position.x * grid_size), int(position.y * grid_size))

def force(r, a):
    beta = 0.3
    if r < beta:
        return r / beta - 1
    elif beta < r and r < 1:
        return a * (1 - abs(2 * r - 1 - beta) / (1 - beta))
    else:
        return 0

def updateParticles():
    global positions, velocities, grid
    new_velocities = []
    grid = {}

    for i in range(n):
        grid_pos = get_grid_position(positions[i])
        if grid_pos not in grid:
            grid[grid_pos] = []
        grid[grid_pos].append(i)

    for i in range(n):
        total_force = Vector2(0, 0)
        grid_pos = get_grid_position(positions[i])

        for dx in [-1, 0, 1]:  # Fewer neighboring cells to check
            for dy in [-1, 0, 1]:
                neighbor_pos = (grid_pos[0] + dx, grid_pos[1] + dy)
                if neighbor_pos in grid:
                    for j in grid[neighbor_pos]:
                        if j == i:
                            continue
                        r = positions[j] - positions[i]
                        dist = r.length()
                        if dist > 0 and dist < rMax:
                            f = force(dist / rMax, matrix[color_set.index(colors[j])][color_set.index(colors[i])])
                            total_force += r.normalize() * f
        total_force *= rMax * 4  # Adjusted force intensity
        new_velocity = velocities[i] * frictionFactor + total_force * dt
        new_velocities.append(new_velocity)
    
    for i in range(n):
        velocities[i] = new_velocities[i]
        positions[i] += velocities[i] * dt
        # Wrap around edges manually
        positions[i].x = positions[i].x % 1
        positions[i].y = positions[i].y % 1

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill((0, 0, 0))
        updateParticles()
        for i in range(n):
            # Convert to screen coordinates
            pos = (int(positions[i].x * screensize), int(positions[i].y * screensize))
            pygame.draw.circle(screen, colors[i], pos, 2)  # Draw with a consistent size
        pygame.display.flip()
        clock.tick(45)  # Slightly reduced frame rate for smoother visuals

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()
