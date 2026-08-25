from fastapi import FastAPI
from app.audio.ws import router
from app.logging_setup import setup_logging
setup_logging()
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)