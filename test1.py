import pygame
import random
import winsound
import math

# Initialize pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Sign Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

# Car setup
car_width, car_height = 60, 100
car_x, car_y = WIDTH // 2 - car_width // 2, HEIGHT - 150
car_speed = 0

# Animation variables
lane_line_offset = 0
road_animation_offset = 0

# Traffic signs
speed_limit = 60
signs = []
last_sign_time = 0
beep_cooldown = 0

# Road boundaries
road_left = WIDTH // 3
road_right = 2 * WIDTH // 3

# Horn system
no_horn_zone = False
horn_warning_time = 0
horn_violation_particles = []

clock = pygame.time.Clock()
running = True

def draw_animated_road():
    global lane_line_offset, road_animation_offset
    
    # Main road surface
    pygame.draw.rect(win, DARK_GRAY, (road_left, 0, road_right - road_left, HEIGHT))
    
    # Road shoulders
    pygame.draw.rect(win, (70, 70, 70), (road_left - 20, 0, 20, HEIGHT))
    pygame.draw.rect(win, (70, 70, 70), (road_right, 0, 20, HEIGHT))
    
    # Side road markings
    pygame.draw.rect(win, WHITE, (road_left - 3, 0, 3, HEIGHT))
    pygame.draw.rect(win, WHITE, (road_right, 0, 3, HEIGHT))
    
    # Animated center lane lines
    lane_line_offset += car_speed * 0.3
    if lane_line_offset > 80:
        lane_line_offset = 0
    
    center_x = WIDTH // 2
    for y in range(-40, HEIGHT + 40, 80):
        line_y = y + lane_line_offset
        pygame.draw.rect(win, WHITE, (center_x - 2, line_y, 4, 40))
    
    # Road texture lines (subtle)
    road_animation_offset += car_speed * 0.1
    if road_animation_offset > 10:
        road_animation_offset = 0
    
    for y in range(-5, HEIGHT + 5, 10):
        texture_y = y + road_animation_offset
        pygame.draw.line(win, (60, 60, 60), 
                        (road_left + 10, texture_y), 
                        (road_right - 10, texture_y), 1)

def draw_realistic_car():
    # Car shadow
    shadow_offset = 3
    pygame.draw.rect(win, (30, 30, 30), 
                    (car_x + shadow_offset, car_y + shadow_offset, 
                     car_width, car_height))
    
    # Main car body
    pygame.draw.rect(win, BLUE, (car_x, car_y, car_width, car_height))
    
    # Car outline
    pygame.draw.rect(win, (0, 0, 150), (car_x, car_y, car_width, car_height), 2)
    
    # Windshield
    pygame.draw.rect(win, (100, 150, 255), 
                    (car_x + 8, car_y + 10, car_width - 16, 25))
    
    # Rear window
    pygame.draw.rect(win, (100, 150, 255), 
                    (car_x + 8, car_y + car_height - 20, car_width - 16, 15))
    
    # Headlights (animated based on speed)
    brightness = min(255, 100 + car_speed * 2)
    headlight_color = (brightness, brightness, 0)
    pygame.draw.circle(win, headlight_color, 
                      (car_x + 15, car_y + car_height - 8), 6)
    pygame.draw.circle(win, headlight_color, 
                      (car_x + car_width - 15, car_y + car_height - 8), 6)
    
    # Tail lights
    pygame.draw.circle(win, RED, (car_x + 15, car_y + 8), 4)
    pygame.draw.circle(win, RED, (car_x + car_width - 15, car_y + 8), 4)
    
    # Side mirrors
    pygame.draw.rect(win, (0, 0, 100), (car_x - 5, car_y + 30, 8, 10))
    pygame.draw.rect(win, (0, 0, 100), (car_x + car_width - 3, car_y + 30, 8, 10))

def create_particle_effect(x, y, color):
    particles = []
    for _ in range(5):
        particles.append({
            'x': x + random.randint(-10, 10),
            'y': y + random.randint(-5, 5),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-3, -1),
            'life': 20,
            'color': color
        })
    return particles

def update_particles(particles):
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particles.remove(particle)

def draw_particles(particles):
    for particle in particles:
        alpha = particle['life'] * 12
        if alpha > 0:
            s = pygame.Surface((4, 4))
            s.set_alpha(alpha)
            s.fill(particle['color'])
            win.blit(s, (particle['x'], particle['y']))

# Particle systems
overspeed_particles = []

while running:
    # Background gradient
    for y in range(HEIGHT):
        gray_value = 169 - int(y * 0.1)
        color = (max(0, gray_value), max(0, gray_value), max(0, gray_value))
        pygame.draw.line(win, color, (0, y), (WIDTH, y))
    
    # Draw road and car
    draw_animated_road()
    draw_realistic_car()
    
    # Car speed control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        car_speed += 0.5
    elif keys[pygame.K_DOWN]:
        car_speed -= 0.5
    else:
        if car_speed > 0:
            car_speed -= 0.1
    
    car_speed = max(0, min(car_speed, 120))
    
    # Info HUD
    speed_text = font.render(f"Car Speed: {int(car_speed)} km/h", True, WHITE)
    win.blit(speed_text, (20, 20))
    limit_text = font.render(f"Speed Limit: {speed_limit} km/h", True, WHITE)
    win.blit(limit_text, (20, 60))
    
    # Overspeed check
    if car_speed > speed_limit:
        warning = big_font.render("OVERSPEEDING!", True, RED)
        win.blit(warning, (WIDTH//2 - 150, HEIGHT//2 - 50))
    
    # Update particles
    update_particles(overspeed_particles)
    draw_particles(overspeed_particles)
    update_particles(horn_violation_particles)
    draw_particles(horn_violation_particles)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Horn
                if no_horn_zone:
                    if horn_warning_time <= 0:
                        horn_warning_time = 120
                        horn_violation_particles.extend(create_particle_effect(WIDTH // 2, HEIGHT // 3, YELLOW))
                        try:
                            winsound.Beep(1500, 200)
                        except:
                            pass
                else:
                    try:
                        winsound.Beep(400, 200)
                    except:
                        pass
    
    if horn_warning_time > 0:
        horn_warning_time -= 1
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
