import asyncio
from camera import camera_manager

async def get_frame_bytes():

    print("[Screen] Request for frame stream received.")
    try:
        while True:
            frame_bytes = camera_manager.get_latest_frame_bytes()
            if frame_bytes:
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )
            else:
                await asyncio.sleep(0.1)

            await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        print("[Screen] Streaming generator cancelled by client disconnection.")
    except Exception as e:
        print(f"[Screen] Error during streaming frames: {e}")
    finally:
        print("[Screen] Frame byte generator finished.")