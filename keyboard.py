import cv2
import RPi.GPIO as GPIO
import threading

# Motor pin configuration
PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24

# Move forward
def motor_go(speed):
    GPIO.output(AIN1, False)  # AIN1 pin
    GPIO.output(AIN2, True)   # AIN2 pin
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, False)  # BIN1 pin
    GPIO.output(BIN2, True)   # BIN2 pin
    R_Motor.ChangeDutyCycle(speed)

# Move backward
def motor_back(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, False)  # AIN2 pin
    GPIO.output(AIN1, True)   # AIN1 pin
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)   # BIN2 pin
    GPIO.output(BIN1, False)  # BIN1 pin

# Turn left
def motor_left(speed):
    GPIO.output(AIN1, 1)
    GPIO.output(AIN2, 0)
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, 0)
    GPIO.output(BIN2, 1)
    R_Motor.ChangeDutyCycle(speed)

# Turn right
def motor_right(speed):
    GPIO.output(AIN1, 0)
    GPIO.output(AIN2, 1)
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, 1)
    GPIO.output(BIN2, 0)
    R_Motor.ChangeDutyCycle(speed)

# Stop both motors
def motor_stop():
    GPIO.output(AIN1, 0)
    GPIO.output(AIN2, 1)
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN1, 0)
    GPIO.output(BIN2, 1)
    R_Motor.ChangeDutyCycle(0)
    

# Initialize GPIO settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)

# Initialize PWM for each motor
L_Motor = GPIO.PWM(PWMA, 100)
L_Motor.start(0)
R_Motor = GPIO.PWM(PWMB, 100)
R_Motor.start(0)

# Default speed setting
speedSet = 50


stop_timer = None

def schedule_stop(delay=0.25):
    """delay 초 후에 motor_stop() 호출"""
    global stop_timer
    if stop_timer is not None:
        stop_timer.cancel()
    stop_timer = threading.Timer(delay, motor_stop)
    stop_timer.start()

def main():
    camera = cv2.VideoCapture(-1)
    camera.set(3, 640)
    camera.set(4, 480)
    # filepath = "/home/username/AI_CAR/video/train"

    i = 0
    carState = "stop"

    while camera.isOpened():
        keyValue = cv2.waitKey(10)
        if keyValue == ord('q'):
            break
        elif keyValue == 82:  # Up arrow
            print("go")
            carState = "go"
            motor_go(speedSet)
            schedule_stop()
        elif keyValue == 84:  # Down arrow
            # do nothing
            print("stop")
            carState = "stop"
            motor_stop()
        elif keyValue == 81:  # Left arrow
            print("left")
            carState = "left"
            motor_left(speedSet)
            schedule_stop()
        elif keyValue == 83:  # Right arrow
            print("right")
            carState = "right"
            motor_right(speedSet)
            schedule_stop()

        # Read frame and flip it
        _, image = camera.read()
        image = cv2.flip(image, -1)
        cv2.imshow('Original', image)

        # Save only the bottom half of the image
        height, _, _ = image.shape
        save_image = image[int(height/2):, :, :]

        # Preprocess: convert to YUV, blur, and resize
        save_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2YUV)
        save_image = cv2.GaussianBlur(save_image, (3, 3), 0)
        save_image = cv2.resize(save_image, (200, 66))
        cv2.imshow('Save', save_image)

        # Save image files based on current state
        # if carState == "left":
        #     cv2.imwrite("%s_%05d_%03d.png" % (filepath, i, 45), save_image)
        #     i += 1
        # elif carState == "right":
        #     cv2.imwrite("%s_%05d_%03d.png" % (filepath, i, 135), save_image)
        #     i += 1
        # elif carState == "go":
        #     cv2.imwrite("%s_%05d_%03d.png" % (filepath, i, 90), save_image)
        #     i += 1

    if stop_timer is not None:
        stop_timer.cancel()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    GPIO.cleanup()
