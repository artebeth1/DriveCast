from google import genai
from google.genai import types
import asyncio
client = genai.Client() 
import logging
logger = logging.getLogger("drivecast.agents")

async def producer_node(state) -> dict:
    packets = state["content_packets"]
    if not packets:
        return {"script": ""}
    eta = packets[0].eta_seconds
    eta = packets[0].eta_seconds
    words_allowed = eta * 2
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= f"write within {words_allowed:.0f} words: " + "\n".join([f"{p.landmark.name}: {p.research_summary}" for p in packets]),
        )
    script = response.text
    return {"script": script}