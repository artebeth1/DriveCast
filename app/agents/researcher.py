from app.geo.landmarks import Landmark
from google import genai
import httpx
from pydantic import BaseModel
from google.genai import types
import asyncio
client = genai.Client() 
import logging
logger = logging.getLogger("drivecast.agents")


class Research(BaseModel):
    summary: str
    fun_facts: list[str]

class ContentPacket(BaseModel):
    landmark: Landmark
    eta_seconds: float
    research_summary: str
    sources: list[str]

async def research_landmark(landmark, requirements = ""):
    title = landmark.name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    headers = {"User-Agent": "DriveCast/0.1 (learning project)"}
    async with httpx.AsyncClient() as http:
        wiki_response = await http.get(url, headers=headers)

    source_url = ""
    extract = ""
    if wiki_response.status_code != 404:
        data = wiki_response.json()
        extract = data.get("extract", "")
        source_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        
    grounding = f"Based on: {extract}\n" if extract else ""

    prompt = grounding + f"Tell me about {landmark.name}, a {landmark.category}, within 70 words. I am a visitor walking toward this place. Talk with concise and easy tone like influencer." + requirements
    gemini_response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Research,
        ),
    )

    return gemini_response.parsed, source_url
