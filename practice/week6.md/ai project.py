import pygame
import random
import sys
import os

# --- 1. 초기화 및 상수 설정 ---
pygame.init()
pygame.mixer.init()  # 사운드 시스템 초기화
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Balance Update")
clock = pygame.time.Clock()
FPS = 60

# 설정값 (스프라이트 관련)
FRAME_W, FRAME_H = 80, 75
DISPLAY_SCALE = 0.8
FRAME_DELAY = 100

# 색상
WHITE, GRAY, BLUE = (255, 255, 255), (20, 20, 40), (50, 150, 255)
RED, YELLOW, ORANGE = (220, 50, 50), (240, 220, 0), (255, 165, 0)

# --- 2. 자원 로드 (사운드 & 스프라이트) ---

# [사운드 로드]
try:
    shoot_sound = pygame.mixer.Sound("./assets/sounds/boom.mp3")
    shoot_sound.set_volume(0.5)
except:
    print("사운드 파일을 로드할 수 없습니다.")
    shoot_sound = None

# [스프라이트 로드]
sprite_path = "C:/Users/com/Desktop/week6/assets/sprites/jet.png"
try:
    player_sheet = pygame.image.load(sprite_path).convert_alpha()
except:
    player_sheet = pygame.Surface((FRAME_W * 5, FRAME_H * 5))
    player_sheet.fill((255, 0, 255))

def get_frames(row):
    frames = []
    for col in range(5):
        rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
        img = player_sheet.subsurface(rect)
        img = pygame.transform.scale(img, (int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)))
        frames.append(img)
    return frames

plane1 = get_frames(0)  # 내 캐릭터
plane2 = get_frames(1)  # 일반 적
plane3 = get_frames(2)  # 엘리트 적

# --- 3. 기타 자원 및 메뉴 함수 ---
def get_font(size):
    try: return pygame.font.SysFont("malgungothic", size)
    except: return pygame.font.SysFont(None, size)

FONT_36 = get_font(36)
FONT_72 = get_font(72)
HS_FILE = "high_score.txt"

def load_high_score():
    if os.path.exists(HS_FILE):
        with open(HS_FILE, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_high_score(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))

LEVELS = [
    {"speed": 1.5, "spawn": 60, "label": "Lv.1", "delay": 3000, "elite": 0.0},
    {"speed": 2.2, "spawn": 50, "label": "Lv.2", "delay": 3000, "elite": 0.1},
    {"speed": 2.8, "spawn": 40, "label": "Lv.3", "delay": 3000, "elite": 0.2},
    {"speed": 3.5, "spawn": 30, "label": "Lv.4", "delay": 2000, "elite": 0.3},
    {"speed": 4.2, "spawn": 25, "label": "Lv.5", "delay": 2000, "elite": 0.4},
]
THRESHOLDS = [50, 120, 200, 300]

def draw_text_center(text, font, color, y_offset):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

def pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text_center("PAUSED", FONT_72, YELLOW, -50)
    draw_text_center("ESC: Resume | R: Restart | Q: Quit", FONT_36, WHITE, 50)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "RESUME"
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_q: pygame.quit(); sys.exit()
        clock.tick(10)

def game_over_menu(current_score):
    high_score = load_high_score()
    is_new = current_score > high_score
    if is_new: save_high_score(current_score); high_score = current_score
    screen.fill((10, 10, 30))
    draw_text_center("GAME OVER", FONT_72, RED, -100)
    draw_text_center(f"Your Score: {current_score}", FONT_36, WHITE, -20)
    draw_text_center(f"{'NEW ' if is_new else ''}BEST SCORE: {high_score}", FONT_36, YELLOW if is_new else WHITE, 30)
    draw_text_center("R: Restart | Q: Quit", FONT_36, WHITE, 110)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_q: pygame.quit(); sys.exit()
        clock.tick(10)

# --- 4. 메인 게임 루프 ---
def main_game():
    p_w, p_h = int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)
    player = pygame.Rect(WIDTH//2-p_w//2, HEIGHT-p_h-20, p_w, p_h)
    
    bullets, enemies, e_bullets = [], [], []
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)] for _ in range(50)]
    score, lives, shoot_cd, spawn_timer, invincible = 0, 3.0, 0, 0, 0
    level_idx = 0

    while True:
        now = pygame.time.get_ticks()
        cfg = LEVELS[level_idx]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if pause_menu() == "RESTART": return "RESTART"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 6
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 6
        if keys[pygame.K_UP] and player.top > 0: player.y -= 6
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT: player.y += 6
        
        # 공격 및 사운드
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            bullets.append(pygame.Rect(player.centerx-4, player.top, 8, 20))
            shoot_cd = 15
            if shoot_sound:
                shoot_sound.play()
                
        if shoot_cd > 0: shoot_cd -= 1

        # 적 스폰
        spawn_timer += 1
        if spawn_timer >= cfg["spawn"]:
            spawn_timer = 0
            is_elite = random.random() < cfg["elite"]
            enemies.append({
                "rect": pygame.Rect(random.randint(0, WIDTH-p_w), -p_h, p_w, p_h),
                "spawn_time": now,
                "shot": False,
                "type": "elite" if is_elite else "normal",
                "hp": 2 if is_elite else 1, # [수정] 엘리트 적 체력을 3에서 2로 변경
                "hurt": 0,
                "anim_frames": plane3 if is_elite else plane2
            })

        # 이동 및 충돌 판정 (기존 로직 동일)
        for b in bullets: b.y -= 10
        bullets = [b for b in bullets if b.bottom > 0]
        for eb in e_bullets: eb.y += 7
        e_bullets = [eb for eb in e_bullets if eb.top < HEIGHT]

        for en in enemies:
            en["rect"].y += cfg["speed"]
            if en["hurt"] > 0: en["hurt"] -= 1
            if not en["shot"] and (now - en["spawn_time"] >= cfg["delay"]):
                e_bullets.append(pygame.Rect(en["rect"].centerx-3, en["rect"].bottom, 6, 15))
                en["shot"] = True
        enemies = [en for en in enemies if en["rect"].top < HEIGHT]

        for b in bullets[:]:
            hit_eb = False
            for eb in e_bullets[:]:
                if b.colliderect(eb):
                    if b in bullets: bullets.remove(b)
                    if eb in e_bullets: e_bullets.remove(eb)
                    hit_eb = True; break
            if hit_eb: continue

            for en in enemies[:]:
                if b.colliderect(en["rect"]):
                    if b in bullets: bullets.remove(b)
                    en["hp"] -= 1
                    en["hurt"] = 5
                    if en["hp"] <= 0:
                        score += 30 if en["type"] == "elite" else 10
                        enemies.remove(en)
                    break

        if invincible > 0: invincible -= 1
        else:
            hit = any(player.colliderect(en["rect"]) for en in enemies)
            if not hit:
                for eb in e_bullets[:]:
                    if player.colliderect(eb): hit = True; e_bullets.remove(eb); break
            if hit:
                lives -= 0.5
                invincible = 90
                if lives <= 0:
                    if game_over_menu(score) == "RESTART": return "RESTART"

        level_idx = min(sum(1 for t in THRESHOLDS if score >= t), len(LEVELS)-1)

        # 그리기
        screen.fill(GRAY)
        for s in stars:
            s[1] += 1
            if s[1] > HEIGHT: s[1] = 0; s[0] = random.randint(0, WIDTH)
            pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

        current_frame_idx = (now // FRAME_DELAY) % 5
        for b in bullets: pygame.draw.rect(screen, YELLOW, b)
        for eb in e_bullets: pygame.draw.rect(screen, ORANGE, eb)

        for en in enemies:
            img = en["anim_frames"][current_frame_idx].copy()
            if en["hurt"] > 0:
                img.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
            img = pygame.transform.rotate(img, 180)
            screen.blit(img, en["rect"])
        
        if (invincible // 10) % 2 == 0:
            screen.blit(plane1[current_frame_idx], player)

        screen.blit(FONT_36.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(FONT_36.render(LEVELS[level_idx]["label"], True, YELLOW), (WIDTH//2-25, 10))
        h_txt = "♥" * int(lives) + ("♡" if lives % 1 >= 0.5 else "")
        screen.blit(FONT_36.render(f"Lives: {h_txt}", True, RED), (WIDTH-240, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    while True:
        if main_game() == "RESTART": continue
        else: break