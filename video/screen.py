import cv2


async def detect_faces():
    capture = cv2.VideoCapture(0)

    while True:
        ret, frame = capture.read()

        if not ret:
            break
        
        yield frame

    capture.release()
