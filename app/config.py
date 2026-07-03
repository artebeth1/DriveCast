import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not MAPBOX_TOKEN:
    raise RuntimeError("MAPBOX_TOKEN not set")
