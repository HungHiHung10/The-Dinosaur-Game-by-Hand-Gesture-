import asyncio
import pygame
import cv2
import mediapipe as mp
import time
from collections import deque

pygame.init()

# Kích thước cửa sổ game
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dinosaur Game with Hand Gesture")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Thuộc tính khủng long
dino_x = 50
dino_y = HEIGHT - 50
dino_width = 40
dino_height = 50
dino_velocity = 0
JUMP_POWER = -15
GRAVITY = 0.8

# Tải hình khủng long
try:
    dino_image = pygame.image.load("dinosaur.png")
    dino_image = pygame.transform.scale(dino_image, (dino_width, dino_height))
except pygame.error as e:
    print(f"Error loading dinosaur image: {e}")
    dino_image = None

# Cactus
cactus_x = WIDTH
cactus_y = HEIGHT - 50
cactus_width = 20
cactus_height = 50
cactus_speed = 5

# Biến game
score = 0
game_over = False

# Webcam + MediaPipe
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
history = deque(maxlen=15)  # Tăng để mượt hơn
wave_detected = False
last_detect_time = 0

# Font
font = pygame.font.SysFont('arial', 30)

def setup():
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return False
    return True

def update_loop():
    global dino_y, dino_velocity, cactus_x, score, game_over, wave_detected, last_detect_time

    if game_over:
        return

    # Đọc ảnh từ webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        return

    # Nhận diện tay
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    h, w, _ = frame.shape
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            wrist = hand_landmarks.landmark[0]
            wrist_x = int(wrist.x * w)
            history.append(wrist_x)

    # Phát hiện vẫy tay (tăng độ nhạy)
    if len(history) >= 6:
        dx1 = (history[-1] - history[-3]) / w
        dx2 = (history[-3] - history[-6]) / w
        if abs(dx1) > 0.015 and abs(dx2) > 0.015 and dx1 * dx2 < 0:
            if time.time() - last_detect_time > 0.7:
                wave_detected = True
                last_detect_time = time.time()

    # Nhảy khi phát hiện vẫy
    if wave_detected and dino_y == HEIGHT - 50:
        dino_velocity = JUMP_POWER
        wave_detected = False

    # Cập nhật vị trí khủng long
    dino_y += dino_velocity
    dino_velocity += GRAVITY
    if dino_y > HEIGHT - 50:
        dino_y = HEIGHT - 50
        dino_velocity = 0

    # Cập nhật vị trí cactus
    cactus_x -= cactus_speed
    if cactus_x < -cactus_width:
        cactus_x = WIDTH
        score += 1

    # Kiểm tra va chạm
    dino_rect = pygame.Rect(dino_x, dino_y, dino_width, dino_height)
    cactus_rect = pygame.Rect(cactus_x, cactus_y, cactus_width, cactus_height)
    if dino_rect.colliderect(cactus_rect):
        game_over = True

    # Vẽ game
    screen.fill(WHITE)
    if dino_image:
        screen.blit(dino_image, (dino_x, dino_y))
    else:
        pygame.draw.rect(screen, BLACK, (dino_x, dino_y, dino_width, dino_height))
    pygame.draw.rect(screen, BLACK, (cactus_x, cactus_y, cactus_width, cactus_height))
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    if game_over:
        game_over_text = font.render("Game Over! Press R to Restart", True, BLACK)
        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))
    else:
        guide_text = font.render("Wave your hand to jump!", True, BLACK)
        screen.blit(guide_text, (WIDTH//2 - 160, 20))

    pygame.display.flip()

    # Hiển thị webcam để debug
    cv2.imshow("Webcam", frame)
    cv2.waitKey(1)

# async def main():
#     global dino_y, dino_velocity, cactus_x, score, game_over
#     if not setup():
#         return
#     clock = pygame.time.Clock()
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 cap.release()
#                 cv2.destroyAllWindows()
#                 pygame.quit()
#                 return
#             if event.type == pygame.KEYDOWN:
#                 if game_over and event.key == pygame.K_r:
#                     dino_y = HEIGHT - 50
#                     dino_velocity = 0
#                     cactus_x = WIDTH
#                     score = 0
#                     game_over = False
#                 elif event.key == pygame.K_SPACE and dino_y == HEIGHT - 50:
#                     dino_velocity = JUMP_POWER  # Nhảy bằng phím cách (test)
#         update_loop()
#         clock.tick(60)
#         await asyncio.sleep(0)

# # Jupyter notebook compatibility
# import nest_asyncio
# nest_asyncio.apply()
# loop = asyncio.get_event_loop()
# loop.create_task(main())

def main():
    global dino_y, dino_velocity, cactus_x, score, game_over
    if not setup():
        return
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    dino_y = HEIGHT - 50
                    dino_velocity = 0
                    cactus_x = WIDTH
                    score = 0
                    game_over = False
                elif event.key == pygame.K_SPACE and dino_y == HEIGHT - 50:
                    dino_velocity = JUMP_POWER  # Nhảy bằng phím cách

        update_loop()
        clock.tick(60)

    # Dọn dẹp
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
