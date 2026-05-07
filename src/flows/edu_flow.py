import sys
import os
import asyncio
from typing import TypedDict

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

def fetch_student_node(state: EduState):
    print("--- [Node] Fetching Student Data ---")
    try:
        res = get_student_analytics(state["student_id"])
        return {"analysis_result": str(res)}
    except Exception as e:
        return {"analysis_result": f"Error: {e}"}

def fetch_class_node(state: EduState):
    print("--- [Node] Fetching Class Data ---")
    try:
        res = get_class_analytics(state["class_id"])
        return {"analysis_result": str(res)}
    except Exception as e:
        return {"analysis_result": f"Error: {e}"}


async def run_crewai_node(state: EduState):
    print("--- [Node] Running CrewAI Agents ---")

    if not state.get("analysis_result") or "No grades found" in state["analysis_result"]:
        return {"final_response": "I couldn't retrieve the necessary data."}

    analyst = get_analyst_agent()
    communicator = get_communicator_agent()

    task1 = get_analysis_task(analyst, state["analysis_result"])
    task2 = get_response_task(communicator, state["query"], state["user_role"])

    crew = Crew(agents=[analyst, communicator], tasks=[task1, task2], verbose=True)

    result = await crew.kickoff_async()
    final_text = result.raw if hasattr(result, 'raw') else str(result)

    return {"final_response": final_text}

def decide_next_step(state: EduState):
    if state["route_signal"] == "stop":
        return "end"
    elif state["route_signal"] == "student":
        return "fetch_student"
    elif state["route_signal"] == "class":
        return "fetch_class"
    return "end"

# ==========================================
# Building the Graph
# ==========================================
workflow = StateGraph(EduState)

workflow.add_node("validate", validate_node)
workflow.add_node("fetch_student", fetch_student_node)
workflow.add_node("fetch_class", fetch_class_node)
workflow.add_node("ai_agent", run_crewai_node)

workflow.add_edge(START, "validate")

workflow.add_conditional_edges(
    "validate",
    decide_next_step,
    {
        "fetch_student": "fetch_student",
        "fetch_class": "fetch_class",
        "end": END
    }
)

workflow.add_edge("fetch_student", "ai_agent")
workflow.add_edge("fetch_class", "ai_agent")

workflow.add_edge("ai_agent", END)

app_graph = workflow.compile()


async def main():
    print("--- Starting LangGraph EduMind Simulation ---")

    # מצב התחלתי
    initial_state = {
        "user_role": "parent",
        "student_id": 123456789,
        "class_id": "",
        "query": "How is my child progressing in Mathematics?",
        "analysis_result": "",
        "final_response": "",
        "route_signal": ""
    }

    final_state = await app_graph.ainvoke(initial_state)

    print("\n" + "=" * 50)
    print(f"FINAL AI RESPONSE:\n{final_state['final_response']}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())