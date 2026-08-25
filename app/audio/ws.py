import time, logging
from fastapi import APIRouter, WebSocket
from app.config import ELEVENLABS_API_KEY   # triggers load_dotenv() in server process
from app.audio.tts import synthesize

logger = logging.getLogger("drivecast.audio")
router = APIRouter()                          # NOT FastAPI()

@router.websocket("/ws/audio")
async def audio_ws(ws: WebSocket):
    await ws.accept()
    first_script = True
    try:
        while True:                              # loop: many scripts per connection
            script = await ws.receive_text()     # wait for the next script

            if not first_script:
                await ws.send_text("FLUSH")      # tell client to clear before new audio
                logger.info("audio buffer flushed")
            first_script = False

            logger.info("audio stream start", extra={"extra_data": {"chars": len(script)}})
            start = time.time()
            seq = 0
            sent_first = False

            for chunk in synthesize(script):
                if not sent_first:
                    ttfb = (time.time() - start) * 1000
                    logger.info("ttfb", extra={"extra_data": {"ttfb_ms": round(ttfb, 1)}})
                    sent_first = True
                await ws.send_bytes(chunk)
                seq += 1

            logger.info("audio stream end", extra={"extra_data": {"chunks": seq}})
    except WebSocketDisconnect:
        logger.info("client disconnected")