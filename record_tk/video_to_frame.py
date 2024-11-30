import cv2
import os


output_dir = r'\datasets\dxcjus\images\train'
video_files = [f for f in os.listdir('.') if f.endswith('.avi')]

cap = cv2.VideoCapture('output.avi')
video_fps = cap.get(cv2.CAP_PROP_FPS)
print(video_fps)

frame_count = 0
save_frame_cnt = 0
capture_interval = int(video_fps * 1.5)
print(capture_interval)

success, frame = cap.read()
while success:
    success, frame = cap.read()
    if frame_count % capture_interval == 0:
        save_frame_cnt += 1
        img_path = os.path.join(output_dir, f'frame_{save_frame_cnt:04d}.jpg')
        cv2.imwrite(img_path, frame)

    frame_count += 1

    print(frame_count)
print(f"total save frames: {save_frame_cnt}")
