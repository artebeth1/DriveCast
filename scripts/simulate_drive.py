import gpxpy
import time
import asyncio
from app.geo.distance import haversine, bearing
import logging
from app.logging_setup import setup_logging
from app.agents.graph import build_graph
setup_logging()
logger = logging.getLogger("drivecast.simulator")

app = build_graph()

R = 6371000


INTERVAL_SECONDS = 10.0

with open("data/Chicago.gpx") as f:
    parsed_gpx = gpxpy.parse(f)

async def main():
    la, lo = None, None

    for track in parsed_gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if la is None:
                    la, lo = point.latitude, point.longitude
                    continue

                distance = haversine(la, lo, point.latitude, point.longitude)
                heading = bearing(la, lo, point.latitude, point.longitude)
                speed = distance / INTERVAL_SECONDS

                logger.info("position update",
                            extra={"extra_data": {"lat": la, "lon": lo,
                                                  "speed": speed, "heading": heading}})

                state = {
                    "lat": la, "lon": lo,
                    "heading": heading, "speed": speed,
                    "requirements": "I like history",
                    "content_packets": [],
                    "script": "",
                }
                result = await app.ainvoke(state)          # await, not asyncio.run
                logger.info("script produced",
                            extra={"extra_data": {"script": result["script"]}})

                la, lo = point.latitude, point.longitude
                await asyncio.sleep(INTERVAL_SECONDS)      # async sleep

if __name__ == "__main__":
    asyncio.run(main())                                    # once, at the very end