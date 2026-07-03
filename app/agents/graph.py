from typing import TypedDict, List
from app.geo.landmarks import Landmark, get_nearby_landmarks
from app.agents.researcher import research_landmark
from app.geo.distance import bearing, is_ahead
from app.agents.researcher import ContentPacket, researcher_node
from langgraph.graph import StateGraph, START, END
import asyncio

class DriveState(TypedDict):
    lat: float
    lon: float
    heading: float
    requirements: str
    speed: float
    predicted_landmarks: List[Landmark]
    content_packets: list


def geo_navigator(state: DriveState) -> dict:
    landmarks = get_nearby_landmarks(state["lat"], state["lon"], 3000)
    ahead = [
        lm for lm in landmarks
        if is_ahead(state["heading"], bearing(state["lat"], state["lon"], lm.lat, lm.lon))
    ]
    print(f"[Geo-Navigator] {len(ahead)} landmarks ahead")   # logging — the plan wants this
    return {"predicted_landmarks": ahead}


def build_graph():
    graph = StateGraph(DriveState)        
    graph.add_node("geo_navigator", geo_navigator)
    graph.add_node("researcher", researcher_node)

    graph.add_edge(START, "geo_navigator") 
    graph.add_edge("geo_navigator", "researcher") 
    graph.add_edge("researcher", END) 

    return graph.compile()           

if __name__ == "__main__":
    app = build_graph()
    state = {
        "lat": 41.876903,
        "lon": -87.629268,
        "heading": 90,
        "speed": 1.4,
        "requirements": "",
        "predicted_landmarks": [],
        "content_packets": [],
    }
    result = asyncio.run(app.ainvoke(state))   # ainvoke — async graph

    print(f"\n=== {len(result['content_packets'])} packets ===\n")
    for p in result["content_packets"]:
        print(f"{p.landmark.name}  (ETA {p.eta_seconds:.0f}s)")
        print(f"  {p.research_summary}")
        print(f"  sources: {p.sources}\n")