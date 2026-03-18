import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Move Circle")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
running = True

x = 400
y = 300
speed = 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 이동
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    # ✅ Shift 키로 FPS 변경
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        fps = 200
    else:
        fps = 60

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (x, y), 50)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()