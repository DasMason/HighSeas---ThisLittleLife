import pygame
from pygame.locals import *
from pygame.math import Vector2
import random
import math
from collections import defaultdict

pygame.font.init()
menuFont = pygame.font.SysFont("arial", 24)
buttonFont = pygame.font.SysFont("arial", 20)

# Screen
screensize = 800
screen = pygame.display.set_mode((screensize, screensize))
pygame.display.set_caption("ThisLittleLife")

class Slider:
    def __init__(self, x, y, name, minval, maxval, initialval, w, h):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.name = name
        self.minval = minval
        self.maxval = maxval
        self.val = initialval
        self.handleRect = pygame.Rect(0, 0, 20, h)
        self.handleRect.center = (x, y)
        self.handleRect.centerx = x + (initialval - minval) / (maxval - minval) * w
        self.dragging = False
        self.nameText = menuFont.render(name, False, (0, 0, 0))
        self.valText = menuFont.render(f"{initialval:.3f}", False, (0, 0, 0))

    def draw(self, mscreen):
        mscreen.blit(self.nameText, self.nameText.get_rect(center=(self.x, self.y - 30)))
        pygame.draw.rect(mscreen, (200, 200, 200), self.rect)
        pygame.draw.rect(mscreen, (100, 100, 255), self.handleRect)
        self.valText = menuFont.render(f"{self.val:.3f}", True, (0, 0, 0))
        mscreen.blit(self.valText, (self.rect.right + 10, self.rect.centery - 10))

    def handledrag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handleRect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handleRect.centerx = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.val = self.minval + (self.handleRect.centerx - self.rect.left) / self.rect.width * (self.maxval - self.minval)
            self.val = min(max(self.val, self.minval), self.maxval)
            print(f"Slider {self.name} value: {self.val}")

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 200, 0)
        self.hover_color = (0, 255, 0)
        self.text = text
        self.action = action
        self.textSurf = buttonFont.render(text, True, (255, 255, 255))
        self.textRect = self.textSurf.get_rect(center=self.rect.center)
        self.hovered = False

    def draw(self, mscreen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(mscreen, color, self.rect)
        mscreen.blit(self.textSurf, self.textRect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                print(f"Button {self.text} clicked")
                self.action()

n = 1000
dt = 0.015
frictionHLF = 0.010
rMax = 0.25
m = 6
grid_size = 10
menuopen = True

def makeRandomMatrix():
    return [[random.random() * 15 - 7.5 for _ in range(m)] for _ in range(m)]

matrix = makeRandomMatrix()
frictionFactor = math.pow(0.5, dt / frictionHLF)

color_set = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (0, 255, 255), (255, 0, 255)
]

def initialize_particles(n):
    positions, velocities, colors = [], [], []
    for i in range(n):
        colors.append(color_set[i % m])
        positions.append(Vector2(random.random(), random.random()))
        velocities.append(Vector2(0, 0))
    return positions, velocities, colors

def get_grid_position(position):
    return int(position.x * grid_size), int(position.y * grid_size)

def force(r, a):
    beta = 0.3
    if r < beta:
        return r / beta - 1
    elif beta < r < 1:
        return a * (1 - abs(2 * r - 1 - beta) / (1 - beta))
    return 0

def update_particles(positions, velocities, colors):
    grid = defaultdict(list)
    new_velocities = []

    for i, pos in enumerate(positions):
        grid_pos = get_grid_position(pos)
        grid[grid_pos].append(i)

    for i, pos in enumerate(positions):
        total_force = Vector2(0, 0)
        grid_pos = get_grid_position(pos)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_pos = (grid_pos[0] + dx, grid_pos[1] + dy)
                for j in grid.get(neighbor_pos, []):
                    if j == i:
                        continue
                    r = positions[j] - positions[i]
                    dist = r.length()
                    if 0 < dist < rMax:
                        f = force(dist / rMax, matrix[color_set.index(colors[j])][color_set.index(colors[i])])
                        total_force += r.normalize() * f

        new_velocity = velocities[i] * frictionFactor + total_force * dt * rMax * 4
        new_velocities.append(new_velocity)

    for i in range(n):
        velocities[i] = new_velocities[i]
        positions[i] += velocities[i] * dt
        positions[i].x %= 1
        positions[i].y %= 1

    return positions, velocities

def start_program():
    global menuopen
    menuopen = False
    print("Starting the game...")

def menu():
    global n, dt, menuopen
    particle_slider = Slider(400, 250, "Particle Amount", 500, 2500, n, 200, 20)
    dt_slider = Slider(400, 300, "Delta Time", 0.005, 0.05, dt, 200, 20)
    start_button = Button(350, 400, 100, 50, "Start", start_program)

    run = True
    while run and menuopen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            particle_slider.handledrag(event)
            dt_slider.handledrag(event)
            start_button.handle_event(event)

        screen.fill((255, 255, 255))
        particle_slider.draw(screen)
        dt_slider.draw(screen)
        start_button.draw(screen)
        pygame.display.flip()

    n = int(particle_slider.val)
    dt = dt_slider.val
    print(f"Slider values set to: Particles = {n}, Delta Time = {dt}")

def main():
    global n, dt
    clock = pygame.time.Clock()

    positions, velocities, colors = initialize_particles(n)
    print(f"Particles initialized: {n}")

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill((0, 0, 0))
        positions, velocities = update_particles(positions, velocities, colors)
        for i in range(n):
            pos = (int(positions[i].x * screensize), int(positions[i].y * screensize))
            pygame.draw.circle(screen, colors[i], pos, 2)

        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

pygame.init()

while menuopen:
    print("Running the menu...")
    menu()

if not menuopen:
    print("Running the main program...")
    screen.fill((0, 0, 0))
    pygame.display.flip()
    main()

pygame.quit()
