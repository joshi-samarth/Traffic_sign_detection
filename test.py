import pygame
import random
import winsound

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

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

# Car setup
car_width, car_height = 60, 100
car_x, car_y = WIDTH // 2 - car_width // 2, HEIGHT - 150
car_speed = 0

# Traffic signs
speed_limit = 60
signs = []
last_sign_time = 0

clock = pygame.time.Clock()
running = True

while running:
    win.fill(GRAY)

    # Draw road
    pygame.draw.rect(win, (50, 50, 50), (WIDTH // 3, 0, WIDTH // 3, HEIGHT))
    pygame.draw.line(win, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)

    # Draw car
    pygame.draw.rect(win, BLUE, (car_x, car_y, car_width, car_height))

    # Keyboard controls for car speed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        car_speed += 1
    if keys[pygame.K_DOWN]:
        car_speed -= 1
    car_speed = max(0, min(car_speed, 120))

    # Generate traffic sign every 5 seconds
    if pygame.time.get_ticks() - last_sign_time > 5000:
        speed_limit = random.choice([40, 60, 80, 100])
        signs.append({"x": WIDTH - 150, "y": -60, "limit": speed_limit})
        last_sign_time = pygame.time.get_ticks()

    # Draw and move traffic signs
    for sign in signs[:]:
        sign["y"] += 5
        pygame.draw.circle(win, WHITE, (sign["x"], sign["y"]), 40)
        pygame.draw.circle(win, RED, (sign["x"], sign["y"]), 40, 5)
        limit_text = font.render(str(sign["limit"]), True, BLACK)
        text_rect = limit_text.get_rect(center=(sign["x"], sign["y"]))
        win.blit(limit_text, text_rect)

        if sign["y"] > HEIGHT:
            signs.remove(sign)

    # Display info
    speed_text = font.render(f"Car Speed: {car_speed} km/h", True, BLACK)
    win.blit(speed_text, (20, 20))
    limit_text = font.render(f"Speed Limit: {speed_limit} km/h", True, BLACK)
    win.blit(limit_text, (20, 60))

    # Overspeed check
    if car_speed > speed_limit:
        warning = big_font.render("OVERSPEEDING!", True, RED)
        win.blit(warning, (WIDTH // 2 - warning.get_width() // 2, HEIGHT // 2))
        winsound.Beep(1000, 200)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(30)

pygame.quit()
