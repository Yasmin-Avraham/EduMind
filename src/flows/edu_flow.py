import sys
import os
import asyncio
from typing import TypedDict

from sentence_transformers.sentence_transformer.modules.tokenizer import word

os.environ["PYTHONUNBUFFERED"] = "1"
sys.path.append(os.getcwd())

from langgraph.graph import StateGraph, START, END

from crewai import Crew
from src.mcp_servers.db_server import get_student_analytics, get_class_analytics
from src.config import PARENT_BLOCKED_KEYWORDS
from src.agents.edu_agents import get_analyst_agent, get_communicator_agent
from src.agents.edu_tasks import get_analysis_task, get_response_task

class EduState(TypedDict):
    user_role: str
    student_id: int
    class_id: str
    query: str
    analysis_result: str
    final_response: str
    route_signal: str

def validate_node(state: EduState):
    if state["user_role"] == "parent":
        if not state["student_id"]:
            return {"final_response":"Please enter the child's ID number.",
                    "route_signal":"stop"}
        if any(word in state["query"] for word in PARENT_BLOCKED_KEYWORDS):
            return {"final_response":"Access denied for privacy reasons.",
                    "route_signal":"stop"}
        return {"route_signal": "student"}
    elif state["user_role"] == "teacher":
        if "class" in state["query"]:
            if not state["class_id"]:
                return {"final_response": "Please indicate which class.", "route_signal": "stop"}
            return {"route_signal": "class"}
