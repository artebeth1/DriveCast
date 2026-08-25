import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # add this line to load the ElevenLabs API key



if not MAPBOX_TOKEN:
    raise RuntimeError("MAPBOX_TOKEN not set")
