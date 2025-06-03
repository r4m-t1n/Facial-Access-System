import cv2

capture = cv2.VideoCapture(0)


async def get_webcam_frames():
    try:
        while True:
            ret, frame = capture.read()

            if not ret:
                break

            yield frame
    finally:
        capture.release()

async def get_frame_bytes():
    while True:
        ret, frame = capture.read()
        
        if not ret:
            break
        
        _, buf = cv2.imencode(".jpg", frame)
        frame_bytes = buf.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )