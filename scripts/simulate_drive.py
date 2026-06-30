import gpxpy
import time
from app.geo.landmarks import get_nearby_landmarks
from app.geo.distance import haversine, bearing

R = 6371000


INTERVAL_SECONDS = 1.0

with open("data/Chicago.gpx") as f:
    parsed_gpx = gpxpy.parse(f)

la, lo = None, None
seen_ids = set()   # remembers landmarks already shown, for dedup

for track in parsed_gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if la is None:
                la, lo = point.latitude, point.longitude
                continue

            distance = haversine(la, lo, point.latitude, point.longitude)
            heading = bearing(la, lo, point.latitude, point.longitude)
            speed = distance / INTERVAL_SECONDS
            print(f"Latitude: {la}, Longitude: {lo}, Speed: {speed:.1f} m/s, Heading: {heading:.0f}")
            
            landmarks = get_nearby_landmarks(la, lo, 3000)
            for lm in landmarks:
                if lm.id not in seen_ids:
                    seen_ids.add(lm.id)
                    print(f"    → {lm.name} ({lm.category}), {lm.distance_m:.0f}m away")

            la, lo = point.latitude, point.longitude
            time.sleep(INTERVAL_SECONDS)

print(f"Latitude: {la}, Longitude: {lo}, Speed: 0 m/s, Heading: n/a")