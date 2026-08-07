from google import genai
from google.genai import types
import asyncio
client = genai.Client() 
import logging
logger = logging.getLogger("drivecast.agents")
from app.memory.narration_memory import record

async def producer_node(state) -> dict:
    packets = state["content_packets"]
    narrated = state["narrated_landmarks"]

    if not packets:
        return {"script": "", "narrated_landmarks": narrated}   # nothing to narrate

    eta = packets[0].eta_seconds
    words_allowed = eta * 2.5
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"write within {words_allowed:.0f} words: "
                 + "\n".join(f"{p.landmark.name}: {p.research_summary}" for p in packets),
    )
    script = response.text
    words = script.split()
    truncated = len(words) > words_allowed
    if truncated:
        script = " ".join(words[:int(words_allowed)])

    # RECORD narration — only after a non-empty script
    if script.strip():
        for p in packets:
            narrated = record(p.landmark.name, narrated)

    logger.info("producer wrote script",
                extra={"extra_data": {
                    "eta_seconds": eta,
                    "words_allowed": words_allowed,
                    "words_actual": len(words),
                    "truncated": truncated,
                    "narrated": narrated,
                }})
    return {"script": script, "narrated_landmarks": narrated}