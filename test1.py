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

def draw_realistic_sign(sign):
    x, y = sign["x"], sign["y"]
    
    # Sign post shadow
    pygame.draw.line(win, (30, 30, 30), (x + 2, y + 42), (x + 2, y + 120), 8)
    
    # Sign post
    pygame.draw.line(win, (100, 100, 100), (x, y + 40), (x, y + 120), 6)
    
    # Sign shadow
    pygame.draw.circle(win, (30, 30, 30), (x + 3, y + 3), 42)
    
    # Sign background (white circle)
    pygame.draw.circle(win, WHITE, (x, y), 40)
    
    # Red border with gradient effect
    pygame.draw.circle(win, RED, (x, y), 40, 5)
    pygame.draw.circle(win, (200, 0, 0), (x, y), 35, 2)
    
    # Speed limit number with shadow
    limit_text = font.render(str(sign["limit"]), True, (50, 50, 50))
    shadow_rect = limit_text.get_rect(center=(x + 1, y - 3))
    win.blit(limit_text, shadow_rect)
    
    limit_text = font.render(str(sign["limit"]), True, BLACK)
    text_rect = limit_text.get_rect(center=(x, y - 5))
    win.blit(limit_text, text_rect)
    
    # "km/h" text
    small_font = pygame.font.SysFont("Arial", 16)
    kmh_text = small_font.render("km/h", True, BLACK)
    kmh_rect = kmh_text.get_rect(center=(x, y + 15))
    win.blit(kmh_text, kmh_rect)

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
    # Background with gradient effect
    for y in range(HEIGHT):
        gray_value = 169 - int(y * 0.1)
        color = (max(0, gray_value), max(0, gray_value), max(0, gray_value))
        pygame.draw.line(win, color, (0, y), (WIDTH, y))
    
    # Draw animated road
    draw_animated_road()
    
    # Draw realistic car
    draw_realistic_car()
    
    # Keyboard controls for car speed with smooth acceleration
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        car_speed += 0.5
    elif keys[pygame.K_DOWN]:
        car_speed -= 0.5
    else:
        # Natural deceleration
        if car_speed > 0:
            car_speed -= 0.1
    
    car_speed = max(0, min(car_speed, 120))
    
    # Generate traffic sign every 5 seconds
    if pygame.time.get_ticks() - last_sign_time > 5000:
        speed_limit = random.choice([40, 60, 80, 100])
        sign_x = random.randint(road_left + 50, road_right - 50)
        signs.append({"x": sign_x, "y": -60, "limit": speed_limit})
        last_sign_time = pygame.time.get_ticks()
    
    # Draw and move traffic signs with realistic physics
    for sign in signs[:]:
        sign["y"] += 3 + car_speed * 0.05  # Speed affects sign falling speed
        draw_realistic_sign(sign)
        
        if sign["y"] > HEIGHT:
            signs.remove(sign)
    
    # Display info with better styling
    speed_bg = pygame.Surface((250, 40))
    speed_bg.set_alpha(150)
    speed_bg.fill(BLACK)
    win.blit(speed_bg, (10, 10))
    
    speed_text = font.render(f"Car Speed: {int(car_speed)} km/h", True, WHITE)
    win.blit(speed_text, (20, 20))
    
    limit_bg = pygame.Surface((280, 40))
    limit_bg.set_alpha(150)
    limit_bg.fill(BLACK)
    win.blit(limit_bg, (10, 55))
    
    limit_text = font.render(f"Speed Limit: {speed_limit} km/h", True, WHITE)
    win.blit(limit_text, (20, 65))
    
    # Overspeed check with enhanced effects
    if car_speed > speed_limit:
        # Flashing warning with alpha effect
        flash_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
        warning_surface = pygame.Surface((WIDTH, 100))
        warning_surface.set_alpha(flash_alpha)
        warning_surface.fill(RED)
        win.blit(warning_surface, (0, HEIGHT // 2 - 50))
        
        warning = big_font.render("OVERSPEEDING!", True, WHITE)
        warning_rect = warning.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        win.blit(warning, warning_rect)
        
        # Create particles
        if random.random() < 0.3:
            overspeed_particles.extend(create_particle_effect(WIDTH // 2, HEIGHT // 2, RED))
        
        # Beep sound with cooldown
        if beep_cooldown <= 0:
            try:
                winsound.Beep(1000, 100)
                beep_cooldown = 30
            except:
                pass
    
    if beep_cooldown > 0:
        beep_cooldown -= 1
    
    # Update and draw particles
    update_particles(overspeed_particles)
    draw_particles(overspeed_particles)
    
    # Speed blur effect when going fast
    if car_speed > 80:
        blur_surface = pygame.Surface((WIDTH, HEIGHT))
        blur_surface.set_alpha(20)
        blur_surface.fill(WHITE)
        win.blit(blur_surface, (0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.update()
    clock.tick(60)  # Increased to 60 FPS for smoother animation

pygame.quit()