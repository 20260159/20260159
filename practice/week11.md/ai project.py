import pygame
import random
import sys
import os
def resource_path(relative_path):

    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)
# --- 1. 초기화 및 상수 설정 ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
except:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Shooter - Top View Clouds (Custom Player)")
clock = pygame.time.Clock()
FPS = 60

FRAME_W, FRAME_H = 80, 75
DISPLAY_SCALE = 0.8
FRAME_DELAY = 100

WHITE, GRAY, BLUE = (255, 255, 255), (20, 20, 40), (50, 150, 255)
RED, YELLOW, ORANGE = (220, 50, 50), (240, 220, 0), (255, 165, 0)
HS_FILE = "high_score.txt"

SKY_BLUE = (100, 170, 240)
CLOUD_WHITE = (255, 255, 255, 180)

# --- 2. 자원 로드 및 유틸리티 ---
def load_assets():
    shoot_sound = None
    try:
        if os.path.exists(resource_path("./assets/sounds/boom.mp3")):
            shoot_sound = pygame.mixer.Sound(resource_path("./assets/sounds/boom.mp3"))
            shoot_sound.set_volume(0.5)
        pygame.mixer.music.load(resource_path("./assets/sounds/bgm.mp3"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except: pass

    # 적과 보스를 위한 기존 jet.png 로드
    sprite_path = (resource_path("./assets/sprites/jet.png"))
    if os.path.exists(sprite_path):
        enemy_sheet = pygame.image.load(sprite_path).convert_alpha()
    else:
        enemy_sheet = pygame.Surface((FRAME_W * 5, FRAME_H * 5))
        enemy_sheet.fill((255, 0, 255))
    return shoot_sound, enemy_sheet

shoot_sound, enemy_sheet = load_assets()

def get_enemy_frames(row):
    frames = []
    for col in range(5):
        rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
        img = enemy_sheet.subsurface(rect)
        img = pygame.transform.scale(img, (int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)))
        frames.append(img)
    return frames

def load_player_frames():
    image_file_path = resource_path("./assets/sprites/player.png")


    if os.path.exists(image_file_path):
        full_sheet = pygame.image.load(image_file_path).convert_alpha()
        sheet_w, sheet_h = full_sheet.get_size()
        
        frame_w = sheet_w // 5
        frame_h = sheet_h
        
        target_w = int(FRAME_W * DISPLAY_SCALE)
        scale_ratio = target_w / frame_w
        new_h = int(frame_h * scale_ratio)
        
        frames = []
        for i in range(5):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            img = full_sheet.subsurface(rect)
            img = pygame.transform.scale(img, (target_w, new_h))
            frames.append(img)
        return frames
    else:
        print(f"❌ [경고] 플레이어 이미지를 찾을 수 없습니다: {image_file_path}")
        temp_surf = pygame.Surface((int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)))
        temp_surf.fill((0, 255, 255))
        return [temp_surf] * 5

# 스프라이트 변수 할당
plane1 = load_player_frames()    
plane2 = get_enemy_frames(1)     
plane3 = get_enemy_frames(0)     
boss_frames = get_enemy_frames(2)
superior_frames = get_enemy_frames(3) 
true_boss_frames = get_enemy_frames(4) # 진 최종 보스 (5번째 줄)

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

# --- 3. 메뉴 & 배경 함수 ---
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
            if event.type == pygame.QUIT: 
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # ESC를 누르면 다시 게임으로 (unpause 후 리턴)
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.unpause()
                    return "RESUME"
                
                # --- [수정된 부분] R을 누르면 RESTART 문자열을 반환 ---
                if event.key == pygame.K_r:
                    pygame.mixer.music.unpause() # 음악 다시 재생 준비
                    return "RESTART"
                # -----------------------------------------------

                if event.key == pygame.K_q: 
                    pygame.quit(); sys.exit()
                
                # (테스트용 단축키 3, 4, 5는 일시정지 중엔 점수만 바꾸고 
                # 화면 반영이 안 되므로 여기보다는 메인 루프에 두는 게 좋습니다.)
        clock.tick(10)

def game_over_menu(current_score):
    high_score = load_high_score()
    is_new = current_score > high_score
    if is_new: save_high_score(current_score); high_score = current_score

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 0, 0))
    screen.blit(overlay, (0, 0))
    
    draw_text_center("GAME OVER", FONT_72, RED, -100)
    draw_text_center(f"Your Score: {current_score}", FONT_36, WHITE, -20)
    draw_text_center(f"{'NEW ' if is_new else ''}BEST SCORE: {high_score}", FONT_36, YELLOW if is_new else WHITE, 30)
    draw_text_center("Press R to Restart | Q to Quit", FONT_36, WHITE, 110)
    pygame.display.flip()
    
    # [수정] 들여쓰기 위치를 정상적으로 복구
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.unpause()
                    return "RESUME"
                if event.key == pygame.K_r:
                    return "RESTART"
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
        clock.tick(10)

def create_cloud_surface(width, height):
    cloud_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    base_alpha = random.randint(100, 180)
    
    num_circles = random.randint(4, 8)
    for _ in range(num_circles):
        radius = random.randint(width // 4, width // 2)
        ellip_w = radius * 2
        ellip_h = random.randint(int(ellip_w * 0.7), ellip_w)
        
        cx = width // 2 + random.randint(-width // 4, width // 4)
        cy = height // 2 + random.randint(-height // 4, height // 4)
        
        alpha = max(0, base_alpha - random.randint(0, 50))
        color = (255, 255, 255, alpha)
        
        ellip_rect = pygame.Rect(0, 0, ellip_w, ellip_h)
        ellip_rect.center = (cx, cy)
        pygame.draw.ellipse(cloud_surf, color, ellip_rect)
        
    return cloud_surf

# --- 4. 메인 게임 루프 ---
LEVELS = [
    {"speed": 2.0, "spawn": 60, "label": "Lv.1", "delay": 3000, "elite": 0.0}, 
    {"speed": 2.2, "spawn": 56, "label": "Lv.2", "delay": 2600, "elite": 0.0}, 
    {"speed": 2.4, "spawn": 52, "label": "Lv.3", "delay": 2200, "elite": 0.1}, 
    {"speed": 2.7, "spawn": 48, "label": "Lv.4", "delay": 1800, "elite": 0.2}, 
    {"speed": 3.0, "spawn": 44, "label": "Lv.5", "delay": 1400, "elite": 0.3}, 
    {"speed": 3.3, "spawn": 40, "label": "Lv.6", "delay": 1100, "elite": 0.4},
    {"speed": 3.6, "spawn": 36, "label": "Lv.7", "delay": 850,  "elite": 0.5},
    {"speed": 3.9, "spawn": 32, "label": "Lv.8", "delay": 650,  "elite": 0.6},
    {"speed": 4.2, "spawn": 28, "label": "Lv.9", "delay": 500,  "elite": 0.7},
    {"speed": 4.5, "spawn": 25, "label": "Lv.10 - MAX", "delay": 350, "elite": 0.8},
]
THRESHOLDS = [100, 200, 300, 400, 600, 800, 1000, 1200, 1500]

def main_game():
    high_score = load_high_score()
    
    p_w, p_h = plane1[0].get_width(), plane1[0].get_height()
    player = pygame.Rect(WIDTH//2-p_w//2, HEIGHT-p_h-20, p_w, p_h)
    
    e_w, e_h = int(FRAME_W * DISPLAY_SCALE), int(FRAME_H * DISPLAY_SCALE)
    
    bullets, enemies, e_bullets, heavy_e_bullets = [], [], [], []
    
    potions = []
    last_potion_time = pygame.time.get_ticks()
    POTION_INTERVAL = 10000
    
    # --- [추가] 부스트 아이템 변수 ---
    boost_items = []
    last_boost_time = pygame.time.get_ticks()
    BOOST_INTERVAL = 30000  # 30초마다 스폰
    boost_active = False
    boost_end_time = 0
    # --------------------------------
    
    clouds = []
    num_clouds = 12 
    for _ in range(num_clouds):
        w = random.randint(150, 350)
        h = int(w * random.uniform(0.6, 0.9))
        surf = create_cloud_surface(w, h)
        clouds.append({
            "surf": surf,
            "x": random.randint(-w//2, WIDTH - w//2),
            "y": random.randint(-h//2, HEIGHT - h//2),
            "speed": random.uniform(0.5, 2.5) 
        })
    clouds.sort(key=lambda c: c["surf"].get_width()) 

    score, lives, shoot_cd, spawn_timer, invincible = 0, 3.0, 0, 0, 0
    level_idx = 0
    
    # 보스 상태 플래그
    boss_active = False
    mid_boss_done, true_boss_done = False, False  
    boss_hp, boss_invincible_timer, boss_hurt, boss_shoot_cd = 30, 0, 0, 0
    boss_approaching = False # [추가] 보스 경고 화면 상태
    approach_timer = 0       # [추가] 경고 화면 지속 시간
    boss_rect = pygame.Rect(WIDTH//2 - 100, -200, 200, 150)
    boss_move_dir = 1
    current_boss_frames = boss_frames
    
    # --- [추가] 보스 패턴용 변수 ---
    boss_pattern = 0
    boss_pattern_timer = 0
    boss_warning_timer = 0  # 전조 현상 지속 시간
    # -------------------------------
 # 최종 보스 처치 이후 스폰 증가 타이머 변수
    post_boss_timer_started = False
    time_post_boss_started = 0

    # --- [여기에 추가] 중간 보스 전환용 타이머 변수 ---
    midboss_transitioning = False
    midboss_timer = 0
    MIDBOSS_DELAY = 2000
    # -----------------------------------------------

    while True:
        now = pygame.time.get_ticks()
        
        # 진 최종 보스 처치 후 스폰 루프가 다시 시작되는 시점 기록
        if true_boss_done and not post_boss_timer_started:
            post_boss_timer_started = True
            time_post_boss_started = now
            
        # 레벨업 로직 (진 최종 보스 처치 시 만렙 처리)
        if true_boss_done: level_idx = 9
        else: level_idx = min(sum(1 for t in THRESHOLDS if score >= t), 9)
        cfg = LEVELS[level_idx]
        
        # [수정] for 루프 들여쓰기 정상화
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pause_menu() == "RESTART": return "RESTART"
                
                # --- [추가] 시연 및 테스트용 단축키 ---
                if event.key == pygame.K_3:
                    if score < 200: score = 200
                
                if event.key == pygame.K_4:
                    if score < 500: score = 500
                
                if event.key == pygame.K_5:
                    if score < 2000:
                        score = 2000
                        mid_boss_done = True
                # ------------------------------------

        # 중간 보스 스폰 (500점)
        if score >= 500 and not mid_boss_done and not boss_active:
            boss_active, boss_invincible_timer = True, 90
            boss_hp = 30
            boss_rect.y, boss_rect.x = -200, WIDTH // 2 - 100
            current_boss_frames = boss_frames

        # --- [수정] 진 최종 보스 경고 및 스폰 로직 ---
        if score >= 2000 and mid_boss_done and not true_boss_done and not boss_active and not boss_approaching:
            boss_approaching = True
            approach_timer = 180  # 60프레임 * 3초 = 180 (3초간 경고)
            
            # 보스 등장의 긴장감을 위해 남은 일반 적과 적 총알을 싹 치워줍니다.
            enemies.clear()
            e_bullets.clear()
            heavy_e_bullets.clear()

        if boss_approaching:
            approach_timer -= 1
            if approach_timer <= 0:  # 3초가 지나면 실제 보스 스폰
                boss_approaching = False
                boss_active, boss_invincible_timer = True, 90
                boss_hp = 120
                boss_rect.y, boss_rect.x = -200, WIDTH // 2 - 100
                current_boss_frames = true_boss_frames
        # ----------------------------------------------

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 6
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 6
        
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            # --- [수정] 부스트 활성화 시 2발 발사 ---
            if boost_active:
                bullets.append(pygame.Rect(player.centerx - 15, player.top, 8, 20))
                bullets.append(pygame.Rect(player.centerx + 7, player.top, 8, 20))
            else:
                bullets.append(pygame.Rect(player.centerx - 4, player.top, 8, 20))
            # ----------------------------------------
            shoot_cd = 15
            if shoot_sound: shoot_sound.play()
        if shoot_cd > 0: shoot_cd -= 1

        # [수정] 경고 중일 때도 일반 적이 스폰되지 않도록 막음
        if not boss_active and not boss_approaching:
            spawn_timer += 1
            if spawn_timer >= cfg["spawn"]:
                spawn_timer = 0
                rand_val = random.random()
                
                if level_idx >= 5:
                    heavy_prob = 0.1 + (level_idx - 5) * 0.1
                    
                    # 최종 보스 처치 이후 10초(10000ms)마다 heavy_prob 증가
                    if post_boss_timer_started:
                        elapsed_10s = (now - time_post_boss_started) // 10000
                        heavy_prob += elapsed_10s * 0.05  # 10초마다 5%씩 증가
                        
                        if heavy_prob > 1.0:
                            heavy_prob = 1.0
                            
                    elite_prob = 1.0 - heavy_prob
                    if elite_prob < 0: elite_prob = 0.0 
                else:
                    heavy_prob = 0.0
                    elite_prob = cfg["elite"]
                
                if rand_val < heavy_prob:
                    e_type, e_hp, e_anim = "heavy", 3, superior_frames
                elif rand_val < heavy_prob + elite_prob:
                    e_type, e_hp, e_anim = "elite", 2, plane3
                else:
                    e_type, e_hp, e_anim = "normal", 1, plane2

                enemies.append({
                    "rect": pygame.Rect(random.randint(0, WIDTH-e_w), -e_h, e_w, e_h),
                    "spawn_time": now, "last_shot_time": now,
                    "speed": cfg["speed"] * 0.9 if e_type == "heavy" else cfg["speed"],
                    "type": e_type, "hp": e_hp, "hurt": 0, "anim_frames": e_anim
                })

        for b in bullets: b.y -= 12
        bullets = [b for b in bullets if b.bottom > 0]
        for eb in e_bullets: eb.y += 8
        e_bullets = [eb for eb in e_bullets if eb.top < HEIGHT]
        for heb in heavy_e_bullets: heb.y += 8
        heavy_e_bullets = [heb for heb in heavy_e_bullets if heb.top < HEIGHT]

        if now - last_potion_time > POTION_INTERVAL:
            potions.append(pygame.Rect(random.randint(0, WIDTH - 20), -20, 20, 20))
            last_potion_time = now
        for p in potions: p.y += 3
        potions = [p for p in potions if p.top < HEIGHT]
        
        # --- [추가] 부스트 아이템 스폰 및 이동 ---
        if now - last_boost_time > BOOST_INTERVAL:
            boost_items.append(pygame.Rect(random.randint(0, WIDTH - 20), -20, 20, 20))
            last_boost_time = now
            
        for b_item in boost_items: b_item.y += 3
        boost_items = [b for b in boost_items if b.top < HEIGHT]

        # 부스트 지속시간 종료 체크
        if boost_active and now > boost_end_time:
            boost_active = False
        # ----------------------------------------
        
        for en in enemies:
            en["rect"].y += en["speed"]
            if en["hurt"] > 0: en["hurt"] -= 1
            if now - en["last_shot_time"] >= cfg["delay"]:
                if en["type"] == "heavy":
                    heavy_e_bullets.append(pygame.Rect(en["rect"].centerx-4, en["rect"].bottom, 8, 20))
                else:
                    e_bullets.append(pygame.Rect(en["rect"].centerx-3, en["rect"].bottom, 6, 15))
                en["last_shot_time"] = now
        enemies = [en for en in enemies if en["rect"].top < HEIGHT]

        # 보스 이동 및 공격 로직
        if boss_active:
            if boss_invincible_timer > 0:
                boss_invincible_timer -= 1
            
            if boss_rect.y < 50:
                boss_rect.y += 2 
            else:
                # --- [수정] 진보스 전용 패턴 타이머 및 전조 현상 로직 ---
                if mid_boss_done:  # 진 최종 보스일 때만 패턴 시스템 가동
                    boss_pattern_timer += 1
                    
                    # 패턴 변경 1초 전(180프레임 시점)부터 전조 현상 시작
                    if boss_pattern_timer == 180:
                        boss_warning_timer = 60 # 1초 동안 깜빡임
                    
                    if boss_pattern_timer > 240:
                        boss_pattern = random.choice([0, 1, 2])
                        boss_pattern_timer = 0
                        boss_shoot_cd = 0
                        boss_warning_timer = 0 # 패턴 시작 시 전조 종료
                else:
                    # 중간 보스는 패턴 변화 및 전조 현상 없이 기본 패턴(0)만 고정 사용
                    boss_pattern = 0
                    boss_pattern_timer = 0
                # ------------------------------------------------

                # --- [수정] 패턴에 따른 보스 이동 ---
                if boss_pattern == 2:
                    pass  # 패턴 2(연사)일 때는 무섭게 제자리에 정지
                else:
                    move_speed = 4 if boss_pattern == 1 else 2
                    boss_rect.x += boss_move_dir * move_speed
                    if boss_rect.left < 0 or boss_rect.right > WIDTH:
                        boss_move_dir *= -1 
                # ------------------------------------
                
                # --- [수정] 패턴별 공격 로직 ---
                if boss_shoot_cd <= 0:
                    if boss_pattern == 0:
                        # [패턴 0] 기본 3갈래 샷 (진보스는 5갈래)
                        heavy_e_bullets.append(pygame.Rect(boss_rect.centerx - 30, boss_rect.bottom, 8, 20))
                        heavy_e_bullets.append(pygame.Rect(boss_rect.centerx + 30, boss_rect.bottom, 8, 20))
                        heavy_e_bullets.append(pygame.Rect(boss_rect.centerx - 4, boss_rect.bottom + 10, 8, 20))
                        
                        if mid_boss_done:
                            heavy_e_bullets.append(pygame.Rect(boss_rect.centerx - 65, boss_rect.bottom - 10, 8, 20))
                            heavy_e_bullets.append(pygame.Rect(boss_rect.centerx + 65, boss_rect.bottom - 10, 8, 20))
                        boss_shoot_cd = 40 if mid_boss_done else 50
                        
                    elif boss_pattern == 1:
                        # [패턴 1] 와이드 산탄 (넓게 퍼지는 폭격)
                        offsets = [-100, -50, 0, 50, 100] if mid_boss_done else [-60, -30, 0, 30, 60]
                        for offset in offsets:
                            heavy_e_bullets.append(pygame.Rect(boss_rect.centerx + offset, boss_rect.bottom + (abs(offset)//3), 8, 20))
                        boss_shoot_cd = 55 # 한 번 쏘고 딜레이가 긺
                        
                    elif boss_pattern == 2:
                        # [패턴 2] 무호흡 기관총 (중앙으로 빠르게 난사)
                        heavy_e_bullets.append(pygame.Rect(boss_rect.centerx - 12, boss_rect.bottom, 8, 20))
                        heavy_e_bullets.append(pygame.Rect(boss_rect.centerx + 12, boss_rect.bottom, 8, 20))
                        boss_shoot_cd = 8 if mid_boss_done else 14 # 쿨타임이 매우 짧음
                else:
                    boss_shoot_cd -= 1
                # --------------------------------
                
        for b in bullets[:]:
            hit_ebullet = False
            for eb in e_bullets[:]:
                if b.colliderect(eb):
                    if b in bullets: bullets.remove(b)
                    if eb in e_bullets: e_bullets.remove(eb)
                    hit_ebullet = True; break
            if hit_ebullet: continue
            
            for heb in heavy_e_bullets[:]:
                if b.colliderect(heb):
                    if b in bullets: bullets.remove(b)
                    if heb in heavy_e_bullets: heavy_e_bullets.remove(heb)
                    hit_ebullet = True; break
            if hit_ebullet: continue

            if boss_active and b.colliderect(boss_rect):
                if b in bullets: bullets.remove(b)
                if boss_invincible_timer <= 0: 
                    boss_hp -= 1; boss_hurt = 5
                    if boss_hp <= 0: 
                        score += 300 if mid_boss_done else 100
                        boss_active = False
                        boss_rect.y = -200 
                        boss_rect.x = WIDTH // 2 - 100
                        
                        if not mid_boss_done: mid_boss_done = True
                        else: true_boss_done = True
                continue
            
            for en in enemies[:]:
                if b.colliderect(en["rect"]):
                    if b in bullets: bullets.remove(b)
                    en["hp"] -= 1; en["hurt"] = 5
                    
                    if en["hp"] <= 0:
                        if en["type"] == "heavy":
                            score += 50
                        elif en["type"] == "elite":
                            score += 30
                        else:
                            score += 10
                            
                        enemies.remove(en)
                    break

        for p in potions[:]:
            if player.colliderect(p):
                potions.remove(p)
                lives += 0.5 
                if lives > 4.0: lives = 4.0
                
        # --- [추가] 부스트 아이템 충돌 처리 ---
        for b_item in boost_items[:]:
            if player.colliderect(b_item):
                boost_items.remove(b_item)
                boost_active = True
                boost_end_time = now + 10000  # 10초
        # -------------------------------------
        
        if invincible > 0: invincible -= 1
        else:
            damage_taken = 0
            if any(player.colliderect(en["rect"]) for en in enemies) or (boss_active and player.colliderect(boss_rect)):
                damage_taken = 0.5
            if damage_taken == 0:
                for eb in e_bullets[:]:
                    if player.colliderect(eb): damage_taken = 0.5; e_bullets.remove(eb); break
            if damage_taken == 0:
                for heb in heavy_e_bullets[:]:
                    if player.colliderect(heb): damage_taken = 1.0; heavy_e_bullets.remove(heb); break
            
            if damage_taken > 0:
                lives -= damage_taken
                invincible = 90
                if lives <= 0: 
                    if game_over_menu(score) == "RESTART": return "RESTART"

        # --- 렌더링 영역 ---
        screen.fill(SKY_BLUE)
        
        for cloud in clouds:
            cloud["y"] += cloud["speed"]
            if cloud["y"] > HEIGHT:
                cloud["y"] = -cloud["surf"].get_height()
                cloud["x"] = random.randint(-cloud["surf"].get_width()//2, WIDTH - cloud["surf"].get_width()//2)
                cloud["speed"] = random.uniform(0.5, 2.5)
            screen.blit(cloud["surf"], (cloud["x"], cloud["y"]))

        current_frame_idx = (now // FRAME_DELAY) % 5
        for b in bullets: pygame.draw.rect(screen, YELLOW, b)
        for eb in e_bullets: pygame.draw.rect(screen, ORANGE, eb)
        for heb in heavy_e_bullets: pygame.draw.rect(screen, RED, heb)

        for p in potions:
            pygame.draw.rect(screen, (50, 200, 50), p)
            pygame.draw.rect(screen, WHITE, (p.centerx - 2, p.top + 4, 4, 12))
            pygame.draw.rect(screen, WHITE, (p.left + 4, p.centery - 2, 12, 4))
            
        # --- [추가] 부스트 아이템 렌더링 ---
        for b_item in boost_items:
            pygame.draw.rect(screen, (50, 50, 255), b_item)  # 파란상자
            pygame.draw.rect(screen, YELLOW, (b_item.centerx - 4, b_item.centery - 4, 8, 8)) # 노란점

        if boost_active:
            time_left = (boost_end_time - now) // 1000
            screen.blit(FONT_36.render(f"BOOST: {time_left}s", True, YELLOW), (10, 90))
        # -----------------------------------
        
        # --- [수정] 보스 렌더링 및 전조 현상 효과 ---
        if boss_active:
            display_boss = True
            
            # 1. 전조 현상 타이머 감소 및 깜빡임 로직
            if boss_warning_timer > 0:
                boss_warning_timer -= 1
                # 5프레임 간격으로 보였다 안 보였다 깜빡임
                if (boss_warning_timer // 5) % 2 == 0:
                    display_boss = False
            
            # 2. 보스 이미지 그리기 (깜빡이지 않는 타이밍일 때만 그림)
            if display_boss:
                b_img = current_boss_frames[current_frame_idx].copy()
                b_img = pygame.transform.scale(b_img, (boss_rect.width, boss_rect.height))
                b_img = pygame.transform.rotate(b_img, 180)
                
                # 전조 현상 중일 때는 붉은색 경고 필터 씌우기
                if boss_warning_timer > 0:
                    b_img.fill((255, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)
                
                # 기존 무적 깜빡임 및 피격 효과 유지
                if boss_invincible_timer > 0 and (now // 100) % 2 == 0: b_img.set_alpha(100)
                if boss_hurt > 0:
                    b_img.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                    boss_hurt -= 1
                    
                screen.blit(b_img, boss_rect)
            
            # 3. 보스 체력바 그리기
            max_hp = 120 if mid_boss_done else 30
            hp_ratio = boss_hp / max_hp
            pygame.draw.rect(screen, RED, (WIDTH//2-100, 30, 200 * hp_ratio, 10))
        # ---------------------------------------------

        for en in enemies:
            img = en["anim_frames"][current_frame_idx].copy()
            if en["hurt"] > 0: img.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
            img = pygame.transform.rotate(img, 180); screen.blit(img, en["rect"])
        
        if (invincible // 10) % 2 == 0: screen.blit(plane1[current_frame_idx], player)

        screen.blit(FONT_36.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(FONT_36.render(f"Best: {max(score, high_score)}", True, BLUE), (10, 50))
        
        # --- [추가] 진보스 경고 텍스트 및 효과 ---
        if boss_approaching:
            # 1. 화면 전체에 붉은 반투명 필터 깔기
            warning_overlay = pygame.Surface((WIDTH, HEIGHT))
            warning_overlay.set_alpha(40)  # 살짝만 붉게
            warning_overlay.fill(RED)
            screen.blit(warning_overlay, (0, 0))
            
            # 2. 10프레임 간격으로 깜빡이는 WARNING 텍스트
            if (approach_timer // 10) % 2 == 0:
                draw_text_center("WARNING", FONT_72, RED, -40)
                draw_text_center("TRUE FINAL BOSS APPROACHING", FONT_36, RED, 20)
        # ---------------------------------------
        
        heart_x = WIDTH - 135 - 10 
        heart_y = 90
        for i in range(4): 
            bx = heart_x + i * 35 
            
            pygame.draw.circle(screen, (100, 100, 100), (bx + 8, heart_y + 8), 8)
            pygame.draw.circle(screen, (100, 100, 100), (bx + 22, heart_y + 8), 8)
            pygame.draw.polygon(screen, (100, 100, 100), [(bx, heart_y + 8), (bx + 30, heart_y + 8), (bx + 15, heart_y + 25)])
            
            if lives >= i + 1: 
                pygame.draw.circle(screen, RED, (bx + 8, heart_y + 8), 8)
                pygame.draw.circle(screen, RED, (bx + 22, heart_y + 8), 8)
                pygame.draw.polygon(screen, RED, [(bx, heart_y + 8), (bx + 30, heart_y + 8), (bx + 15, heart_y + 25)])
            elif lives >= i + 0.5: 
                pygame.draw.circle(screen, RED, (bx + 8, heart_y + 8), 8)
                pygame.draw.polygon(screen, RED, [(bx, heart_y + 8), (bx + 15, heart_y + 8), (bx + 15, heart_y + 25)])

        if boss_active and not mid_boss_done: label_text = "MID BOSS"
        elif boss_active and mid_boss_done: label_text = "TRUE FINAL BOSS"
        else: label_text = cfg["label"]
            
        screen.blit(FONT_36.render(label_text, True, YELLOW), (WIDTH//2-100, 10))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    while True:
        if main_game() == "RESTART": continue
        else: break