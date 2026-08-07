import logging
from google import genai
from google.genai import types
from app.memory.narration_memory import already_narrated
from app.geo.landmarks import get_nearby_landmarks
from app.geo.distance import bearing, is_ahead
from app.agents.researcher import research_landmark, ContentPacket

client = genai.Client()
logger = logging.getLogger("drivecast.agents")


async def agent_node(state, cache) -> dict:
    lat, lon = state["lat"], state["lon"]
    heading = state["heading"]
    speed = state["speed"]
    requirements = state["requirements"]
    narrated = state["narrated_landmarks"]

    found = {}        # name -> Landmark, everything discovered
    researched = {}   # name -> (Research, source_url), what the agent chose

    def search(category: str) -> str:
        """Search for points of interest ahead of the vehicle.

        Only returns places the vehicle is heading toward — things already
        passed are excluded automatically.

        Args:
            category: What kind of place to look for. Must be one of:
                coffee, bakery, restaurant, museum, historic, park.
        """
        landmarks = get_nearby_landmarks(lat, lon, category, 3000)
        ahead = [
            lm for lm in landmarks
            if is_ahead(heading, bearing(lat, lon, lm.lat, lm.lon))
        ]
        for lm in ahead:
            found[lm.name] = lm
        logger.info("agent searched",
                    extra={"extra_data": {"category": category,
                                          "found": len(landmarks),
                                          "ahead": len(ahead)}})
        if not ahead:
            return f"No {category} found ahead."
        return "\n".join(f"- {lm.name} ({lm.category}, {lm.distance_m:.0f}m)" for lm in ahead)

    async def research(name: str) -> str:
        """Research one landmark and return interesting facts about it.

        Args:
            name: The exact name of a landmark returned by search.
        """
        lm = found.get(name)
        if lm is None:
            return f"No landmark named {name} was found."

        if already_narrated(name, narrated):
            logger.info("memory blocked", extra={"extra_data": {"landmark": name}})
            return "Already covered this drive."

        query_key = f"{name} | {requirements}"
        hit = cache.lookup(query_key)
        if hit is not None:
            (research_obj, sources), score = hit
            logger.info("cache hit", extra={"extra_data": {"landmark": name, "similarity": score}})
            researched[name] = (research_obj, sources)
            return research_obj.summary

        logger.info("cache miss", extra={"extra_data": {"landmark": name}})
        result, source_url = await research_landmark(lm, requirements)
        sources = [source_url] if source_url else []
        cache.store(query_key, result, sources)
        logger.info("cache stored", extra={"extra_data": {"landmark": name}})
        researched[name] = (result, sources)
        return result.summary

    prompt = (
        f"You are a driving companion. The user says: '{requirements}'\n"
        f"Search for places ahead that match what they want, then research "
        f"only the ones genuinely worth telling them about. Most places aren't."
    )

    await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(tools=[search, research]),
    )

    packets = []
    for name, (result, sources) in researched.items():
        lm = found[name]
        eta = lm.distance_m / speed if speed > 0 else float("inf")
        packets.append(ContentPacket(
            landmark=lm, eta_seconds=eta,
            research_summary=result.summary, sources=sources,
        ))

    logger.info("agent built content packets",
                extra={"extra_data": {
                    "requirements": requirements,
                    "chosen_landmarks": list(researched.keys()),
                    "skipped_landmarks": [n for n in found if n not in researched],
                    "packets": len(packets),
                    "speed": speed,
                }})
    return {"content_packets": packets}