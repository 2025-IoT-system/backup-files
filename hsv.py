from picamera2 import Picamera2
import cv2
import numpy as np

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 120)})
picam2.configure(config)
picam2.start()

def detect_crosswalk(mask):
    height, width = mask.shape
    roi = mask[:int(height * 0.7), :]
    roi = cv2.resize(roi,(160,66))

    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    stripe_count = 0
    #print(f"[DEBUG] Total contours: {len(contours)}")

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / h if h > 0 else 0
        #print(f"  → Contour: w={w}, h={h}, aspect={aspect_ratio:.2f}")

        if w > 5 and h > 5:
            stripe_count += 1
            cv2.rectangle(roi, (x, y), (x + w, y + h), 255, 1)

    #print(f"[DEBUG] Stripe count = {stripe_count}")
    return stripe_count >= 8, roi

try:
    while True:
        # Get frame from camera
        frame = picam2.capture_array()
        frame = cv2.flip(frame,0)
        frame = cv2.flip(frame,1)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Convert to HSV and create white mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 60, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Detect crosswalk
        detected, roi = detect_crosswalk(mask)
        
        if detected:
            print("@@ Crosswalk detected !!! \n")
        else:
            print("normal\n")

        # Display
        cv2.imshow("Camera", frame)
        #cv2.imshow("White Mask", mask)
        cv2.imshow("ROI + Contours", roi)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    picam2.stop()
    cv2.destroyAllWindows()

