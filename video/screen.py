import cv2


async def get_webcam_frames():
    capture = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = capture.read()

            if not ret:
                break

            yield frame
    finally:
        capture.release()
