import pygame
import random

# 초기화
pygame.init()
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("용사님 돌았어요? - 심연의 이벤트 에디션")
clock = pygame.time.Clock()

# 색상 정의
BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
RED = (255, 80, 80)
GREEN = (60, 220, 100)
BLUE = (60, 140, 240)
YELLOW = (255, 210, 40)
PURPLE = (180, 80, 255)
GRAY = (100, 105, 115)
DARK_GRAY = (35, 35, 40)
LINE_COLOR = (15, 15, 15)
WOOD_BROWN = (115, 75, 45)

# 폰트 설정
try:
    FONT_MINI = pygame.font.SysFont("malgungothic", 11)
    FONT_LABEL = pygame.font.SysFont("malgungothic", 12, True)
    FONT = pygame.font.SysFont("malgungothic", 18)
    BOLD_FONT = pygame.font.SysFont("malgungothic", 22, True)
except:
    FONT_MINI = pygame.font.SysFont("arial", 11)
    FONT_LABEL = pygame.font.SysFont("arial", 12, True)
    FONT = pygame.font.SysFont("arial", 18)
    BOLD_FONT = pygame.font.SysFont("arial", 22, True)

# --- 보드 배치 세부 설정 ---
TILE_SIZE = 60    
TILE_GAP = 4
START_X = 180     
START_Y = 120
MAX_FLOOR = 30

def get_tile_pos(i):
    if i < 10:          gx, gy = i, 0
    elif i < 16:        gx, gy = 9, i - 9
    elif i < 25:        gx, gy = 24 - i, 6
    else:               gx, gy = 0, 30 - i
    x = START_X + gx * (TILE_SIZE + TILE_GAP)
    y = START_Y + gy * (TILE_SIZE + TILE_GAP)
    return x, y

# --- 타일 및 장비 데이터 ---
TILE_INFO = {
    "start": {"label": "시작", "color": WHITE},
    "boss": {"label": "보스", "color": RED},
    "monster": {"label": "몬스터", "color": GRAY},
    "shop": {"label": "상점", "color": YELLOW},
    "heal": {"label": "회복", "color": GREEN},
    "event": {"label": "이벤트", "color": PURPLE}
}

EQUIPMENT_DB = [
    {"name": "낡은 철검", "atk": 3, "hp": 0},
    {"name": "기사의 방패", "atk": 0, "hp": 25},
    {"name": "불꽃의 지팡이", "atk": 6, "hp": 0},
    {"name": "도적의 단검", "atk": 4, "hp": 0},
    {"name": "강철 갑옷", "atk": 0, "hp": 30},
]

def draw_tile_icon(surf, tile_type, cx, cy):
    if tile_type == "start":  
        pygame.draw.line(surf, LINE_COLOR, (cx - 8, cy - 14), (cx - 8, cy + 12), 2)
        pygame.draw.polygon(surf, (230, 40, 40), [(cx - 8, cy - 14), (cx + 12, cy - 7), (cx - 8, cy)])
    elif tile_type == "boss":  
        pygame.draw.polygon(surf, (255, 180, 0), [(cx-14, cy+10), (cx+14, cy+10), (cx+14, cy-4), (cx+7, cy+3), (cx, cy-10), (cx-7, cy+3), (cx-14, cy-4)])
    elif tile_type == "monster":  
        pygame.draw.line(surf, WHITE, (cx - 12, cy - 12), (cx + 12, cy + 12), 3)
        pygame.draw.line(surf, WHITE, (cx + 12, cy - 12), (cx - 12, cy + 12), 3)
    elif tile_type == "shop":  
        pygame.draw.rect(surf, LINE_COLOR, (cx - 12, cy - 8, 22, 14), 2)
    elif tile_type == "heal":  
        pygame.draw.circle(surf, (240, 40, 80), (cx - 5, cy - 4), 6)
        pygame.draw.circle(surf, (240, 40, 80), (cx + 5, cy - 4), 6)
        pygame.draw.polygon(surf, (240, 40, 80), [(cx - 11, cy - 2), (cx + 11, cy - 2), (cx, cy + 10)])
    elif tile_type == "event":  
        draw_text("?", (cx - 5, cy - 12), WHITE, True)

# --- 시스템 클래스 ---
class Player:
    def __init__(self):
        self.hp = 120
        self.max_hp = 120
        self.atk = 15
        self.gold = 0
        self.charging = 0
        self.atk_charge = 50  
        self.inventory = []
        
        self.crit = 0.1
        self.buff_damage = 1.0
        self.buff_duration = 0
        self.buff_defense = 1.0
        self.buff_def_duration = 0

    def tick_buffs(self):
        if self.buff_duration > 0:
            self.buff_duration -= 1
            if self.buff_duration == 0: self.buff_damage = 1.0
        if self.buff_def_duration > 0:
            self.buff_def_duration -= 1
            if self.buff_def_duration == 0: self.buff_defense = 1.0

class Enemy:
    def __init__(self, name, hp, atk, gold_reward, is_boss=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.gold_reward = gold_reward
        self.charging = 0
        self.atk_charge = 70 if not is_boss else 55

def make_board():
    board = []
    shop_indices = [10, 20]  
    for i in range(MAX_FLOOR):
        if i == 0: 
            board.append({"type": "start"})
        elif i == MAX_FLOOR - 1: 
            board.append({"type": "boss"})
        elif i in shop_indices: 
            board.append({"type": "shop"})
        else:
            prev_type = board[-1]["type"] if board else None
            
            while True:
                prob = random.random()
                if prob < 0.50: new_type = "monster"
                elif prob < 0.75: new_type = "event"
                else: new_type = "heal"
                
                if new_type != "monster" and new_type == prev_type:
                    continue
                
                if new_type == "event":
                    sub = random.random()
                    if sub < 0.33: e_type = "blessing"
                    elif sub < 0.66: e_type = "equip"
                    else: e_type = "trade_risk"
                    board.append({"type": "event", "event_type": e_type})
                else:
                    board.append({"type": new_type})
                break
                
    return board

def draw_text(text, pos, color=WHITE, bold=False):
    surf = BOLD_FONT.render(text, True, color) if bold else FONT.render(text, True, color)
    screen.blit(surf, pos)

# --- 변수 초기화 ---
player = Player()
board = make_board()
player_pos = 0.0  
target_pos = 0
game_state = "MOVE" 
current_enemy = None
current_event_type = None
msg_text = "[SPACE] 키를 눌러 주사위를 굴리세요!"

running = True
waiting_for_roll = True
dice_result = 1
dice_roll_timer = 0
current_dice_display = 1

# --- 메인 루프 ---
while running:
    screen.fill(WOOD_BROWN)
    pygame.draw.rect(screen, BLACK, (20, 100, WIDTH-40, HEIGHT-160)) 
    dt = clock.tick(60)

    # 1. 키보드 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == "MOVE" and waiting_for_roll:
                if event.key == pygame.K_SPACE:
                    player.tick_buffs()
                    dice_result = random.randint(1, 6)
                    waiting_for_roll = False
                    dice_roll_timer = 70 
                    target_pos = min(int(player_pos) + dice_result, MAX_FLOOR - 1)
            
            elif game_state == "SHOP":
                if event.key == pygame.K_1 and player.gold >= 30:
                    player.gold -= 30; player.atk += 5; msg_text = "🛒 공격력 상승!"
                elif event.key == pygame.K_2 and player.gold >= 30:
                    player.gold -= 30; player.max_hp += 30; player.hp = player.max_hp; msg_text = "🛒 체력 증폭/회복!"
                elif event.key == pygame.K_SPACE:
                    game_state = "MOVE"; waiting_for_roll = True; msg_text = "모험을 계속합니다."
            
            elif game_state == "EVENT":
                handled = False
                if current_event_type == "blessing":
                    if event.key == pygame.K_1: player.atk += 10; player.buff_damage = 1.5; player.buff_duration = 3; handled = True
                    elif event.key == pygame.K_2: player.hp += 30; player.max_hp += 30; player.buff_defense = 0.5; player.buff_def_duration = 5; handled = True
                    elif event.key == pygame.K_3: player.crit += 0.1; handled = True
                elif current_event_type == "equip":
                    if event.key == pygame.K_1: player.atk += 8; handled = True
                    elif event.key == pygame.K_2: player.hp += 30; player.max_hp += 30; handled = True
                    elif event.key == pygame.K_3: player.crit += 0.15; handled = True
                    elif event.key == pygame.K_4: player.atk += 5; player.hp += 20; player.max_hp += 20; handled = True
                elif current_event_type == "trade_risk":
                    if event.key == pygame.K_1: player.hp = max(1, player.hp - 40); player.buff_damage = 2.0; player.buff_duration = 4; handled = True
                    elif event.key == pygame.K_2: player.hp += 50; player.max_hp += 50; player.atk += 5; handled = True
                    elif event.key == pygame.K_3: 
                        if random.randint(1, 6) <= 3: player.hp = max(1, player.hp - 30)
                        else: player.atk += 15
                        handled = True
                        
                if handled:
                    board[int(player_pos)]["event_type"] = None
                    game_state = "MOVE"
                    waiting_for_roll = True
                    msg_text = "선택 완료! 다음 주사위를 굴리세요."
                    
            elif game_state in ["GAMEOVER", "WIN"]:
                if event.key == pygame.K_SPACE:
                    player = Player(); player_pos = 0.0; target_pos = 0; board = make_board()
                    game_state = "MOVE"; waiting_for_roll = True; msg_text = "새로운 모험이 시작되었습니다!"

    # 2. 게임 상태 업데이트
    if game_state == "MOVE" and not waiting_for_roll:
        if dice_roll_timer > 0:
            dice_roll_timer -= 1
            if dice_roll_timer > 20:   
                if dice_roll_timer % 5 == 0: current_dice_display = random.randint(1, 6)
                msg_text = "🎲 주사위가 구르는 중..."
            else:                      
                current_dice_display = dice_result
                msg_text = f"🎲 결과: {dice_result}! 이동합니다."
        else:
            if player_pos < target_pos:
                player_pos += 0.15  
            else:
                player_pos = float(target_pos)
                tile = board[int(player_pos)]
                t_type = tile["type"]
                
                if t_type in ["monster", "boss"]:
                    is_boss = (t_type == "boss")
                    name = "🔥 어둠의 군단장" if is_boss else "👾 야생 몬스터"
                    current_enemy = Enemy(name, 200 if is_boss else 40 + (int(player_pos) * 5), 25 if is_boss else 8 + (int(player_pos) // 2), 30 + int(player_pos), is_boss)
                    game_state = "BATTLE"
                    msg_text = f"⚔️ 전투 개시!"
                elif t_type == "shop":
                    game_state = "SHOP"
                    msg_text = "🛒 비밀 상점"
                elif t_type == "heal":
                    player.hp = min(player.hp + 40, player.max_hp)
                    msg_text = "🌿 체력을 40 회복했습니다!"
                    waiting_for_roll = True
                elif t_type == "event":
                    if tile.get("event_type"):
                        current_event_type = tile["event_type"]
                        game_state = "EVENT"
                        msg_text = "❓ 신비한 이벤트가 발생했습니다! 선택지를 고르세요."
                    else:
                        msg_text = "빈 공터입니다."
                        waiting_for_roll = True
                else:
                    msg_text = "🚩 시작점"
                    waiting_for_roll = True

    elif game_state == "BATTLE":
        player.charging += 1
        current_enemy.charging += 1

        if player.charging >= player.atk_charge:
            base_dmg = player.atk * player.buff_damage
            is_crit = random.random() < player.crit
            final_dmg = int(base_dmg * 2.0) if is_crit else int(base_dmg)
            current_enemy.hp -= final_dmg
            player.charging = 0

        if current_enemy.hp > 0 and current_enemy.charging >= current_enemy.atk_charge:
            enemy_dmg = int(current_enemy.atk * player.buff_defense)
            player.hp -= enemy_dmg
            current_enemy.charging = 0

        if player.hp <= 0:
            game_state = "GAMEOVER"
            msg_text = "💀 용사 사망. [SPACE] 부활."
        elif current_enemy.hp <= 0:
            if int(player_pos) == MAX_FLOOR - 1:
                game_state = "WIN"
            else:
                player.gold += current_enemy.gold_reward
                dropped = random.choice(EQUIPMENT_DB)
                player.inventory.append(dropped["name"])
                player.atk += dropped["atk"]; player.max_hp += dropped["hp"]; player.hp += dropped["hp"]
                msg_text = f"🎉 승리! {dropped['name']} 획득!"
                game_state = "MOVE"
                waiting_for_roll = True

    # 3. 상단 대시보드 UI
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, 90))
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 90), 2)
    
    draw_text(f"층수: {int(player_pos)} / 30", (30, 15), WHITE, True)
    draw_text(f"❤️ HP: {max(0, int(player.hp))}/{player.max_hp}", (180, 15), RED, True)
    draw_text(f"⚔️ 공격력: {player.atk}", (380, 15), WHITE, True)
    draw_text(f"💰 골드: {player.gold}G", (550, 15), YELLOW, True)
    draw_text(f"🎒 장비: {len(player.inventory)}개", (730, 15), BLUE, True)
    
    draw_text(f"💥 치명타: {int(player.crit*100)}%", (380, 50), PURPLE, True)
    buff_msg = "🔥 버프: "
    if player.buff_duration > 0: buff_msg += f"공격력x{player.buff_damage}({player.buff_duration}턴) "
    if player.buff_def_duration > 0: buff_msg += f"받는피해x{player.buff_defense}({player.buff_def_duration}턴)"
    if player.buff_duration <= 0 and player.buff_def_duration <= 0: buff_msg += "없음"
    draw_text(buff_msg, (550, 50), GREEN)

    # 4. 보드판 그리기
    for i in range(MAX_FLOOR):
        bx, by = get_tile_pos(i)
        t_type = board[i]["type"]
        info = TILE_INFO[t_type]
        pygame.draw.rect(screen, info["color"], (bx, by, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, LINE_COLOR, (bx, by, TILE_SIZE, TILE_SIZE), 2)
        screen.blit(FONT_MINI.render(str(i), True, BLACK if info["color"] not in [GRAY, PURPLE] else WHITE), (bx + 4, by + 2))
        draw_tile_icon(screen, t_type, bx + TILE_SIZE // 2, by + TILE_SIZE // 2 - 2)
        lbl = FONT_LABEL.render(info["label"], True, BLACK if info["color"] not in [GRAY, PURPLE] else WHITE)
        screen.blit(lbl, lbl.get_rect(center=(bx + TILE_SIZE // 2, by + TILE_SIZE - 10)))

    # 5. 플레이어 현위치
    px, py = get_tile_pos(int(player_pos))
    pygame.draw.rect(screen, RED, (px + 2, py + 2, TILE_SIZE - 4, TILE_SIZE - 4), 4, 4)

    # 6. 중앙 상황판
    inner_x, inner_y = START_X + TILE_SIZE + 15, START_Y + TILE_SIZE + 15
    inner_w, inner_h = (TILE_SIZE + TILE_GAP) * 8 - 26, (TILE_SIZE + TILE_GAP) * 5 - 26
    center_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
    pygame.draw.rect(screen, DARK_GRAY, center_rect)
    pygame.draw.rect(screen, WHITE, center_rect, 2)

    cx, cy = center_rect.x, center_rect.y

    if game_state == "BATTLE" and current_enemy:
        # 🛠️ "몬스터와의 전투" 문구 출력 코드 삭제 (HP 바 시작 높이에 맞추어 레이아웃 유지)
        draw_text("플레이어 HP", (cx + 40, cy + 55), WHITE)
        pygame.draw.rect(screen, BLACK, (cx + 40, cy + 80, 260, 16))
        pygame.draw.rect(screen, GREEN, (cx + 40, cy + 80, int(260 * max(0, player.hp / player.max_hp)), 16))
        
        draw_text(f"몬스터 HP", (cx + 40, cy + 120), WHITE)
        pygame.draw.rect(screen, BLACK, (cx + 40, cy + 145, 260, 16))
        pygame.draw.rect(screen, RED, (cx + 40, cy + 145, int(260 * max(0, current_enemy.hp / current_enemy.max_hp)), 16))

    elif game_state == "EVENT":
        if current_event_type == "blessing":
            draw_text("✨ 여신의 축복", (cx + 40, cy + 20), YELLOW, True)
            draw_text("[1] 공격력 +10, 공격력 1.5배 (3칸 유지)", (cx + 40, cy + 70), WHITE)
            draw_text("[2] 체력 +30 및 최대체력 +30, 받는 피해 50% 감소 (5칸 유지)", (cx + 40, cy + 110), WHITE)
            draw_text("[3] 치명타 확률 영구적으로 +10%", (cx + 40, cy + 150), WHITE)
        elif current_event_type == "equip":
            draw_text("🗡️ 버려진 무기 더미", (cx + 40, cy + 20), PURPLE, True)
            draw_text("[1] 공격력 +8", (cx + 40, cy + 70), WHITE)
            draw_text("[2] 최대체력 +30", (cx + 40, cy + 110), WHITE)
            draw_text("[3] 치명타 확률 +15%", (cx + 40, cy + 150), WHITE)
            draw_text("[4] 최대체력 +20, 공격력 +5", (cx + 40, cy + 190), WHITE)
        elif current_event_type == "trade_risk":
            draw_text("👿 악마의 거래", (cx + 40, cy + 20), RED, True)
            draw_text("[1] 현재 HP -40 → 공격력 2배 버프 (4칸 유지)", (cx + 40, cy + 70), WHITE)
            draw_text("[2] 현재 HP +50, 최대체력 +50 → 공격력 +5", (cx + 40, cy + 110), WHITE)
            draw_text("[3] 도박: 50% 확률로 HP -30 또는 공격력 +15", (cx + 40, cy + 150), WHITE)
            
        draw_text("숫자 키를 눌러 선택하세요.", (cx + 40, cy + 230), GREEN)

    elif game_state == "SHOP":
        draw_text("🛒 떠돌이 비밀 상점 오픈", (cx + 40, cy + 25), YELLOW, True)
        draw_text("[1] 공격력 강화 (+5)   : 30 Gold", (cx + 40, cy + 80), WHITE)
        draw_text("[2] 최대체력 증폭 (+30) : 30 Gold", (cx + 40, cy + 120), WHITE)
        draw_text("[SPACE] 완료 후 나가기", (cx + 40, cy + 180), GREEN, True)

    elif game_state == "MOVE":
        if waiting_for_roll:
            draw_text("[SPACE] 키를 눌러 주사위를 굴리세요!", (cx + 40, cy + 100), YELLOW)
        elif dice_roll_timer > 0:
            dice_rect = pygame.Rect(center_rect.centerx - 27, center_rect.centery - 10, 54, 54)
            pygame.draw.rect(screen, WHITE, dice_rect, 0, 6)
            val = current_dice_display
            dcx, dcy = dice_rect.centerx, dice_rect.centery
            if val in [1, 3, 5]: pygame.draw.circle(screen, RED if val==1 else BLACK, (dcx, dcy), 4)
            if val in [2, 3, 4, 5, 6]: 
                pygame.draw.circle(screen, BLACK, (dice_rect.x+13, dice_rect.y+13), 4)
                pygame.draw.circle(screen, BLACK, (dice_rect.x+41, dice_rect.y+41), 4)
            if val in [4, 5, 6]: 
                pygame.draw.circle(screen, BLACK, (dice_rect.x+41, dice_rect.y+13), 4)
                pygame.draw.circle(screen, BLACK, (dice_rect.x+13, dice_rect.y+41), 4)
            if val == 6: 
                pygame.draw.circle(screen, BLACK, (dice_rect.x+13, dice_rect.y+27), 4)
                pygame.draw.circle(screen, BLACK, (dice_rect.x+41, dice_rect.y+27), 4)
        else:
            draw_text(f"【 {dice_result} 】 칸 행군!", (cx + 40, cy + 100), GREEN)

    elif game_state == "GAMEOVER": draw_text("💀 GAME OVER - [SPACE] 재시작", (cx + 60, cy + 100), RED, True)
    elif game_state == "WIN": draw_text("👑 VICTORY - [SPACE] 재시작", (cx + 60, cy + 100), YELLOW, True)

    # 7. 하단 자막 알림창
    pygame.draw.rect(screen, DARK_GRAY, (20, HEIGHT - 50, WIDTH - 40, 40))
    draw_text(msg_text, (35, HEIGHT - 42), WHITE)

    pygame.display.flip()

pygame.quit()