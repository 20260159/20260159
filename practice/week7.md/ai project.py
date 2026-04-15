import pygame
import random
import sys
import os

# --- 1. 초기화 및 상수 설정 ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
except:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Shooter - High Score & Game Over")
clock = pygame.time.Clock()
FPS = 60

FRAME_W, FRAME_H = 80, 75
DISPLAY_SCALE = 0.8
FRAME_DELAY = 100

WHITE, GRAY, BLUE = (255, 255, 255), (20, 20, 40), (50, 150, 255)
RED, YELLOW, ORANGE = (220, 50, 50), (240, 220, 0), (255, 165, 0)
HS_FILE = "high_score.txt"

# --- 2. 자원 로드 및 유틸리티 ---
def load_assets():
    shoot_sound = None
    try:
        if os.path.exists("./assets/sounds/boom.mp3"):
            shoot_sound = pygame.mixer.Sound("./assets/sounds/boom.mp3")
            shoot_sound.set_volume(0.5)
        pygame.mixer.music.load("./assets/sounds/bgm.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except: pass

    sprite_path = "./assets/sprites/jet.png"
    if os.path.exists(sprite_path):
        sheet = pygame.image.load(sprite_path).convert_alpha()
    else:
        sheet = pygame.Surface((FRAME_W * 5, FRAME_H * 5))
        sheet.fill((255, 0, 255))
    return shoot_sound, sheet

shoot_sound, player_sheet = load_assets()

def get_frames(row):
    frames = []
    for col in range(5):
        rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
        img = player_sheet.subsurface(rect)
        img = pygame.transform.scale(img, (int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)))
        frames.append(img)
    return frames

plane1, plane2, plane3, boss_frames = get_frames(0), get_frames(1), get_frames(2), get_frames(4)

# [최고 기록 관리 함수]
def load_high_score():
    if os.path.exists(HS_FILE):
        with open(HS_FILE, "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_high_score(score):
    with open(HS_FILE, "w") as f:
        f.write(str(score))

def get_font(size):
    try: return pygame.font.SysFont("malgungothic", size)
    except: return pygame.font.SysFont(None, size)

FONT_36, FONT_72 = get_font(36), get_font(72)

def draw_text_center(text, font, color, y_offset):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

# --- 3. 메뉴 함수 (정지 & 게임오버) ---
def pause_menu():
    pygame.mixer.music.pause()
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
                if event.key == pygame.K_ESCAPE: pygame.mixer.music.unpause(); return "RESUME"
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_q: pygame.quit(); sys.exit()
        clock.tick(10)

def game_over_menu(current_score):
    high_score = load_high_score()
    is_new = current_score > high_score
    if is_new: save_high_score(current_score); high_score = current_score

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 0, 0)) # 붉은 톤의 배경
    screen.blit(overlay, (0, 0))
    
    draw_text_center("GAME OVER", FONT_72, RED, -100)
    draw_text_center(f"Your Score: {current_score}", FONT_36, WHITE, -20)
    draw_text_center(f"{'NEW ' if is_new else ''}BEST SCORE: {high_score}", FONT_36, YELLOW if is_new else WHITE, 30)
    draw_text_center("Press R to Restart | Q to Quit", FONT_36, WHITE, 110)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_q: pygame.quit(); sys.exit()
        clock.tick(10)

# --- 4. 메인 게임 루프 ---
LEVELS = [
    {"speed": 1.5, "spawn": 60, "label": "Lv.1", "delay": 3000, "elite": 0.0},
    {"speed": 2.2, "spawn": 50, "label": "Lv.2", "delay": 3000, "elite": 0.1},
    {"speed": 2.8, "spawn": 40, "label": "Lv.3", "delay": 3000, "elite": 0.2},
    {"speed": 3.5, "spawn": 30, "label": "Lv.4", "delay": 2000, "elite": 0.3},
    {"speed": 4.2, "spawn": 25, "label": "Lv.5", "delay": 2000, "elite": 0.4},
    {"speed": 5.0, "spawn": 20, "label": "Lv.6 - MAX", "delay": 1500, "elite": 0.6},
]
THRESHOLDS = [50, 120, 200, 300, 500]

def main_game():
    high_score = load_high_score()
    p_w, p_h = int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)
    player = pygame.Rect(WIDTH//2-p_w//2, HEIGHT-p_h-20, p_w, p_h)
    
    bullets, enemies, e_bullets = [], [], []
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)] for _ in range(50)]
    score, lives, shoot_cd, spawn_timer, invincible = 0, 3.0, 0, 0, 0
    level_idx = 0
    boss_active, boss_done = False, False
    boss_hp, boss_invincible_timer, boss_hurt, boss_shoot_cd = 10, 0, 0, 0
    boss_rect = pygame.Rect(WIDTH//2 - 100, -200, 200, 150)
    boss_move_dir = 1

    while True:
        now = pygame.time.get_ticks()
        if boss_done: level_idx = 5
        else: level_idx = min(sum(1 for t in THRESHOLDS if score >= t), 4)
        cfg = LEVELS[level_idx]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause_menu() == "RESTART": return "RESTART"

        if score >= 500 and not boss_active and not boss_done:
            boss_active, boss_invincible_timer = True, 30
            # 보스전 시작 시 일반 적 스폰만 멈춤 (기존 적은 유지)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 6
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 6
        if keys[pygame.K_UP] and player.top > 0: player.y -= 6
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT: player.y += 6
        
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            bullets.append(pygame.Rect(player.centerx-4, player.top, 8, 20))
            shoot_cd = 15
            if shoot_sound: shoot_sound.play()
        if shoot_cd > 0: shoot_cd -= 1

        # 행동 로직
        if boss_active:
            if boss_invincible_timer > 0: boss_invincible_timer -= 1
            if boss_rect.y < 60: boss_rect.y += 2
            else:
                boss_rect.x += 3 * boss_move_dir
                if boss_rect.right >= WIDTH or boss_rect.left <= 0: boss_move_dir *= -1
            boss_shoot_cd += 1
            if boss_shoot_cd >= 40:
                boss_shoot_cd = 0
                e_bullets.append(pygame.Rect(boss_rect.centerx - 40, boss_rect.bottom, 10, 20))
                e_bullets.append(pygame.Rect(boss_rect.centerx + 30, boss_rect.bottom, 10, 20))
        
        # 보스전이 아닐 때만 적 스폰
        if not boss_active:
            spawn_timer += 1
            if spawn_timer >= cfg["spawn"]:
                spawn_timer = 0
                is_elite = random.random() < cfg["elite"]
                enemies.append({
                    "rect": pygame.Rect(random.randint(0, WIDTH-p_w), -p_h, p_w, p_h),
                    "spawn_time": now, "shot": False, "speed": cfg["speed"],
                    "type": "elite" if is_elite else "normal",
                    "hp": 2 if is_elite else 1, "hurt": 0,
                    "anim_frames": plane3 if is_elite else plane2
                })

        # 업데이트
        for b in bullets: b.y -= 12
        bullets = [b for b in bullets if b.bottom > 0]
        for eb in e_bullets: eb.y += 8
        e_bullets = [eb for eb in e_bullets if eb.top < HEIGHT]

        for en in enemies:
            en["rect"].y += en["speed"]
            if en["hurt"] > 0: en["hurt"] -= 1
            if not en["shot"] and (now - en["spawn_time"] >= cfg["delay"]):
                e_bullets.append(pygame.Rect(en["rect"].centerx-3, en["rect"].bottom, 6, 15))
                en["shot"] = True
        enemies = [en for en in enemies if en["rect"].top < HEIGHT]

        # 충돌 판정
        for b in bullets[:]:
            if boss_active and b.colliderect(boss_rect):
                if b in bullets: bullets.remove(b)
                if boss_invincible_timer <= 0:
                    boss_hp -= 1; boss_hurt = 5
                    if boss_hp <= 0: score += 500; boss_active, boss_done = False, True
                continue
            for en in enemies[:]:
                if b.colliderect(en["rect"]):
                    if b in bullets: bullets.remove(b)
                    en["hp"] -= 1; en["hurt"] = 5
                    if en["hp"] <= 0:
                        score += 30 if en["type"] == "elite" else 10
                        enemies.remove(en)
                    break

        # 플레이어 피격
        if invincible > 0: invincible -= 1
        else:
            hit = any(player.colliderect(en["rect"]) for en in enemies)
            if not hit and boss_active: hit = player.colliderect(boss_rect)
            if not hit:
                for eb in e_bullets[:]:
                    if player.colliderect(eb): hit = True; e_bullets.remove(eb); break
            if hit:
                lives -= 0.5; invincible = 90
                # [수정] 생명력 소진 시 게임오버 메뉴 호출
                if lives <= 0: 
                    if game_over_menu(score) == "RESTART": return "RESTART"

        # 그리기
        screen.fill(GRAY)
        for s in stars:
            s[1] += 1
            if s[1] > HEIGHT: s[1] = 0; s[0] = random.randint(0, WIDTH)
            pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

        current_frame_idx = (now // FRAME_DELAY) % 5
        for b in bullets: pygame.draw.rect(screen, YELLOW, b)
        for eb in e_bullets: pygame.draw.rect(screen, ORANGE, eb)

        if boss_active:
            b_img = boss_frames[current_frame_idx].copy()
            b_img = pygame.transform.scale(b_img, (boss_rect.width, boss_rect.height))
            b_img = pygame.transform.rotate(b_img, 180)
            if boss_invincible_timer > 0 and (now // 100) % 2 == 0: b_img.set_alpha(100)
            if boss_hurt > 0:
                b_img.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                boss_hurt -= 1
            screen.blit(b_img, boss_rect)
            pygame.draw.rect(screen, RED, (WIDTH//2-100, 30, boss_hp*20, 10))

        for en in enemies:
            img = en["anim_frames"][current_frame_idx].copy()
            if en["hurt"] > 0: img.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
            img = pygame.transform.rotate(img, 180); screen.blit(img, en["rect"])
        
        if (invincible // 10) % 2 == 0: screen.blit(plane1[current_frame_idx], player)

        # UI 출력 (현재 점수, 최고 기록, 레벨, 생명력)
        screen.blit(FONT_36.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(FONT_36.render(f"Best: {max(score, high_score)}", True, BLUE), (10, 50))
        label_text = "BOSS STAGE" if boss_active else cfg["label"]
        screen.blit(FONT_36.render(label_text, True, YELLOW), (WIDTH//2-60, 10))
        h_txt = "♥" * int(lives) + ("♡" if lives % 1 >= 0.5 else "")
        screen.blit(FONT_36.render(f"Lives: {h_txt}", True, RED), (WIDTH-240, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    while True:
        if main_game() == "RESTART": continue
        else: break