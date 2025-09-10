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

# Horn control
no_horn_zone = False
horn_warning_time = 0
horn_violation_particles = []

clock = pygame.time.Clock()
running = True


# === Helper functions ===
def draw_animated_road():
    global lane_line_offset, road_animation_offset
    pygame.draw.rect(win, DARK_GRAY, (road_left, 0, road_right - road_left, HEIGHT))
    pygame.draw.line(win, WHITE, (road_left, 0), (road_left, HEIGHT), 3)
    pygame.draw.line(win, WHITE, (road_right, 0), (road_right, HEIGHT), 3)

    lane_line_offset += car_speed * 0.3
    if lane_line_offset > 80:
        lane_line_offset = 0

    center_x = WIDTH // 2
    for y in range(-40, HEIGHT + 40, 80):
        line_y = y + lane_line_offset
        pygame.draw.rect(win, WHITE, (center_x - 2, line_y, 4, 40))


def draw_car():
    pygame.draw.rect(win, BLUE, (car_x, car_y, car_width, car_height))
    pygame.draw.rect(win, (0, 0, 150), (car_x, car_y, car_width, car_height), 3)


def draw_speed_sign(sign):
    x, y, limit = sign["x"], sign["y"], sign["limit"]
    pygame.draw.circle(win, WHITE, (x, y), 40)
    pygame.draw.circle(win, RED, (x, y), 40, 5)
    text = font.render(str(limit), True, BLACK)
    win.blit(text, text.get_rect(center=(x, y)))


def draw_no_horn_sign(sign):
    x, y = sign["x"], sign["y"]
    pygame.draw.circle(win, WHITE, (x, y), 40)
    pygame.draw.circle(win, RED, (x, y), 40, 5)
    # Speaker icon (simple)
    pygame.draw.rect(win, BLACK, (x - 15, y - 10, 10, 20))  # speaker box
    pygame.draw.polygon(win, BLACK, [(x - 5, y - 10), (x + 5, y - 20), (x + 5, y + 20), (x - 5, y + 10)])
    # Cross mark
    pygame.draw.line(win, RED, (x - 20, y - 20), (x + 20, y + 20), 4)
    pygame.draw.line(win, RED, (x - 20, y + 20), (x + 20, y - 20), 4)


# === Main loop ===
while running:
    win.fill(GRAY)
    draw_animated_road()
    draw_car()

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

    # Generate random sign every 5s
    if pygame.time.get_ticks() - last_sign_time > 5000:
        if random.choice([True, False]):
            # Speed sign
            limit = random.choice([40, 60, 80, 100])
            signs.append({"type": "speed", "x": WIDTH - 150, "y": -60, "limit": limit})
        else:
            # No horn sign
            signs.append({"type": "no_horn", "x": WIDTH - 200, "y": -60})
        last_sign_time = pygame.time.get_ticks()

    # Move and draw signs
    no_horn_zone = False
    for sign in signs[:]:
        sign["y"] += 3
        if sign["type"] == "speed":
            draw_speed_sign(sign)
            speed_limit = sign["limit"]
        elif sign["type"] == "no_horn":
            draw_no_horn_sign(sign)
            no_horn_zone = True

        if sign["y"] > HEIGHT:
            signs.remove(sign)

    # Display info
    speed_text = font.render(f"Car Speed: {int(car_speed)} km/h", True, BLACK)
    win.blit(speed_text, (20, 20))
    limit_text = font.render(f"Speed Limit: {speed_limit} km/h", True, BLACK)
    win.blit(limit_text, (20, 60))
    if no_horn_zone:
        horn_text = font.render("NO HORN ZONE", True, RED)
        win.blit(horn_text, (20, 100))

    # Overspeed check
    if car_speed > speed_limit:
        warning = big_font.render("OVERSPEEDING!", True, RED)
        win.blit(warning, (WIDTH // 2 - warning.get_width() // 2, HEIGHT // 2))
        if beep_cooldown <= 0:
            winsound.Beep(1000, 200)
            beep_cooldown = 30
    if beep_cooldown > 0:
        beep_cooldown -= 1

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            if no_horn_zone:
                # Warning horn
                winsound.Beep(400, 200)
                horn_warning_time = 60
            else:
                winsound.Beep(1500, 200)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
