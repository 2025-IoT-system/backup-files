import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# === GPIO 설정 ===
PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for pin in [PWMA, AIN1, AIN2, PWMB, BIN1, BIN2]:
    GPIO.setup(pin, GPIO.OUT)

L_Motor = GPIO.PWM(PWMA, 500)
R_Motor = GPIO.PWM(PWMB, 500)
L_Motor.start(0)
R_Motor.start(0)

def motor_go(speed):
    GPIO.output(AIN1, 0)
    GPIO.output(AIN2, 1)
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, 0)
    GPIO.output(BIN2, 1)
    R_Motor.ChangeDutyCycle(speed)

def motor_left(speed):
    GPIO.output(AIN1, 1)
    GPIO.output(AIN2, 0)
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, 0)
    GPIO.output(BIN2, 1)
    R_Motor.ChangeDutyCycle(speed)

def motor_right(speed):
    GPIO.output(AIN1, 0)
    GPIO.output(AIN2, 1)
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, 1)
    GPIO.output(BIN2, 0)
    R_Motor.ChangeDutyCycle(speed)

def motor_stop():
    GPIO.output(AIN1, 0)
    GPIO.output(AIN2, 1)
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN1, 0)
    GPIO.output(BIN2, 1)
    R_Motor.ChangeDutyCycle(0)

# === 카메라 설정 ===
camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4, 480)

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read frame")
            continue

        # 전처리
        frame = cv2.flip(frame, -1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        #clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
        #blurred = clahe.apply(blurred)
        _, binary = cv2.threshold(frame, 170, 255, cv2.THRESH_BINARY)
        

        # 하단 절반만 사용 (240픽셀)
        frame_height, frame_width = binary.shape
        y_start = frame_height //2 
        cropped = binary[y_start:, :]
        resized = cv2.resize(cropped, (320, 240), interpolation=cv2.INTER_NEAREST)
`
        # 컨투어 검출
        contours, _ = cv2.findContours(resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 컬러 변환 → 시각화용
        vis = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)

        cxs = []
        for cnt in contours:

            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cxs.append(cx)
                # 무게중심 표시
                cv2.circle(vis, (cx, cy), 4, (0, 0, 255), -1)

        if len(cxs) > 0:
            cx = cxs[0]  # 첫 번째 중심값 기준으로 판단

            if 190 <= cx <= 250:
                print(f"⬅️ Turn Left | cx = {cx}")
                motor_left(80)
            elif 78 <= cx <= 130:
                print(f"➡️ Turn Right | cx = {cx}")
                motor_right(80)
            else:
                print(f"⬆️ Go Straight | cx = {cx}")
                motor_go(50)
        else:
            print("🛑 No contour detected")
            motor_stop()

        # 시각화
        cv2.imshow("Line Trace View", vis)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            motor_stop()
            print("👋 Quit by user")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    print("🛑 Stopped by user")

finally:
    GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
q
