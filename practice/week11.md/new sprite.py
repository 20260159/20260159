import pygame
import sys
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 게임 기본 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCREEN_W, SCREEN_H = 800, 600
COLS = 5                 # [중요] 나눌 칸 수 (정확히 5개)
FRAME_DELAY = 120        # 애니메이션 속도 (ms 단위, 작을수록 빨라짐)
DISPLAY_SCALE = 2.0      # 화면에 보여줄 배율 (이미지가 작으면 키우세요)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("5-Frame Sprite Animation")
clock = pygame.time.Clock()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 이미지 파일 로드 및 정확한 5등분 계산
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
base_path = r"C:\Users\Admin\Desktop\week7.md\assets\sprites"
image_name = "player.png" 
image_file_path = os.path.join(base_path, image_name)

if not os.path.exists(image_file_path):
    print(f"❌ 오류: 파일을 찾을 수 없습니다! 경로: {image_file_path}")
    pygame.quit()
    sys.exit()

# 전체 시트 이미지 로드
full_sheet = pygame.image.load(image_file_path).convert_alpha()

# [핵심] 이미지의 전체 가로/세로 크기를 가져와서 1칸의 크기를 자동으로 계산합니다.
sheet_w, sheet_h = full_sheet.get_size()
frame_w = sheet_w // COLS  # 전체 가로 길이를 5로 나눔
frame_h = sheet_h          # 세로는 일단 전체 높이 사용

# 5개의 조각(프레임)을 리스트에 순서대로 담기
player_frames = []
for i in range(COLS):
    # 왼쪽에서부터 순서대로 (0*w, 1*w, 2*w...) 좌표를 계산하여 자릅니다.
    rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
    frame_surf = full_sheet.subsurface(rect)
    player_frames.append(frame_surf)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 애니메이션 제어 변수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
current_index = 0
frame_timer = 0

# 화면 중앙 좌표 계산
def get_center_pos(w, h):
    return (SCREEN_W // 2 - w // 2, SCREEN_H // 2 - h // 2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 메인 루프
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
running = True
while running:
    # 60 FPS 유지하며 경과 시간(dt) 계산
    dt = clock.tick(60) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # [애니메이션 로직] 시간이 흐르면 다음 프레임으로 변경
    frame_timer += dt
    if frame_timer >= FRAME_DELAY:
        current_index = (current_index + 1) % COLS  # 0->1->2->3->4->0 순환
        frame_timer = 0

    # 화면 그리기
    screen.fill((30, 30, 40)) 
    
    # 현재 순서의 이미지 조각 가져오기
    current_frame = player_frames[current_index]
    
    # 크기 조절
    draw_w = int(frame_w * DISPLAY_SCALE)
    draw_h = int(frame_h * DISPLAY_SCALE)
    scaled_img = pygame.transform.scale(current_frame, (draw_w, draw_h))
    
    # 중앙 좌표에 출력
    pos = get_center_pos(draw_w, draw_h)
    screen.blit(scaled_img, pos)
    
    pygame.display.flip()

pygame.quit()
sys.exit()