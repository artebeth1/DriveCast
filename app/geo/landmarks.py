import math
import httpx
from pydantic import BaseModel
from app.config import MAPBOX_TOKEN
from app.geo.distance import haversine, bearing, is_ahead



class Landmark(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lon: float
    distance_m: float


def get_nearby_landmarks(lat, lon, radius_m, limit=5):
    category = "coffee"
    url = f"https://api.mapbox.com/search/searchbox/v1/category/{category}"

    lat_offset = radius_m / 111320
    lon_offset = radius_m / (111320 * abs(math.cos(math.radians(lat))))
    min_lon, max_lon = lon - lon_offset, lon + lon_offset
    min_lat, max_lat = lat - lat_offset, lat + lat_offset

    params = {
        "access_token": MAPBOX_TOKEN,
        "proximity": f"{lon},{lat}",
        "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "limit": limit,
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    landmarks = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"] 
        landmark_lon, landmark_lat = coords[0], coords[1]

        poi_categories = props.get("poi_category", [])
        category_value = poi_categories[0] if poi_categories else category

        distance = haversine(lat, lon, landmark_lat, landmark_lon)

        if distance > radius_m:
            continue

        landmarks.append(
            Landmark(
                id=props["mapbox_id"],
                name=props.get("name", "Unknown"),
                category=category_value,
                lat=landmark_lat,
                lon=landmark_lon,
                distance_m=round(distance, 1),
            )
        )

    return landmarks




if __name__ == "__main__":
    results = get_nearby_landmarks(41.876903, -87.629268, 3000)  # Chicago
    print("haha")