import pygame
import math
import cv2
import mediapipe as mp
import threading


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

gesture = "STOP" 

def detect_hand():
    global gesture
    cap = cv2.VideoCapture(0)
    tip_ids = [4, 8, 12, 16, 20]

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm_list = []
                h, w, _ = image.shape
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((cx, cy))

                fingers = []
                
                fingers.append(1 if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0] - 1][0] else 0)
                
                for i in range(1, 5):
                    fingers.append(1 if lm_list[tip_ids[i]][1] < lm_list[tip_ids[i] - 2][1] else 0)

                total = sum(fingers)
                if total == 0:
                    gesture = "STOP"
                elif total == 1:
                    gesture = "UP"
                elif total == 2:
                    gesture = "DOWN"
                elif total == 3:
                    gesture = "LEFT"
                elif total == 4:
                    gesture = "RIGHT"

        cv2.imshow("Camera", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


threading.Thread(target=detect_hand, daemon=True).start()

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Robot Arm Simulator")
clock = pygame.time.Clock()


angle1 = 0
angle2 = 0


length1 = 100
length2 = 80


base_x = 320
base_y = 240


running = True
while running:
    screen.fill((30, 30, 30))

   
    if gesture == "UP":
        angle1 -= 2
    elif gesture == "DOWN":
        angle1 += 2
    elif gesture == "LEFT":
        angle2 -= 2
    elif gesture == "RIGHT":
        angle2 += 2
    elif gesture == "STOP":
        pass  

    angle1 = max(-90, min(90, angle1))
    angle2 = max(-90, min(90, angle2))

    
    joint1_x = base_x + length1 * math.cos(math.radians(angle1))
    joint1_y = base_y + length1 * math.sin(math.radians(angle1))

    end_x = joint1_x + length2 * math.cos(math.radians(angle1 + angle2))
    end_y = joint1_y + length2 * math.sin(math.radians(angle1 + angle2))

  
    pygame.draw.line(screen, (0, 255, 0), (base_x, base_y), (joint1_x, joint1_y), 8)
    pygame.draw.line(screen, (0, 0, 255), (joint1_x, joint1_y), (end_x, end_y), 8)
    pygame.draw.circle(screen, (255, 255, 0), (int(end_x), int(end_y)), 10)

    
    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Gesture: {gesture}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(30)

pygame.quit()
