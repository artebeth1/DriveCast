from typing import TypedDict, List
from app.agents.agent import agent_node
from app.agents.producer import producer_node
from langgraph.graph import StateGraph, START, END
from functools import partial
import logging
logger = logging.getLogger("drivecast.agents")

class DriveState(TypedDict):
    lat: float
    lon: float
    heading: float
    requirements: str
    narrated_landmarks: list[str]
    speed: float
    content_packets: list
    script: str



def build_graph(cache):
    graph = StateGraph(DriveState)
    graph.add_node("agent", partial(agent_node, cache=cache))
    graph.add_node("producer", producer_node)

    graph.add_edge(START, "agent")
    graph.add_edge("agent", "producer")
    graph.add_edge("producer", END)

    return graph.compile()       
