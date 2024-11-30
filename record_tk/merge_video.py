import os
import cv2

video_files = [f for f in os.listdir('.') if f.endswith('.avi')]

cap = cv2.VideoCapture(video_files[0])
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
fcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter('output.avi', fcc, fps, (w, h))

c = 0
while c < len(video_files):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()

    if c < len(video_files) - 1:
        cap = cv2.VideoCapture(video_files[c + 1])

    c += 1

cap.release()
out.release()
cv2.destroyAllWindows()
