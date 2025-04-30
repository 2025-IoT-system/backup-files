import cv2
import numpy as np

def main():
    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 480)

    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read frame from camera.")
            break

        frame = cv2.flip(frame, -1)

        # Preprocessing
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        _, binary = cv2.threshold(frame, 170, 255, cv2.THRESH_BINARY)

        frame_height, frame_width = binary.shape
        y_start = frame_height // 2
        cropped = binary[y_start:, :]  # (240, 640)

        # 🪞 창 1: threshold 이후 크롭된 이미지 (그대로 보여주기)
        cropped_resized_gray = cv2.resize(cropped, (320, 240), interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Thresholded (Before Contour)', cropped_resized_gray)

        # Contour 추출
        contours, _ = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 색상 보기 위해 컬러 변환
        cropped_color = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)

        # Draw contours
        cv2.drawContours(cropped_color, contours, -1, (0, 255, 0), 5)

        # Draw centroid (red circles)
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.circle(cropped_color, (cx, cy), 4, (0, 0, 255), -1)  # red dot

        # 창 2: 컨투어와 중심점이 시각화된 이미지
        cropped_resized_color = cv2.resize(cropped_color, (320, 240), interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Contours + Centroid (After)', cropped_resized_color)

        # Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Quitting...")
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
