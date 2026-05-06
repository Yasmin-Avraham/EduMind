

import sys
import os
import asyncio

os.environ["PYTHONUNBUFFERED"] = "1"
sys.path.append(os.getcwd())
from crewai import Crew
from crewai.flow.flow import Flow, start, listen, or_
from pydantic import BaseModel
from src.mcp_servers.db_server import get_student_analytics, get_class_analytics
from src.config import PARENT_BLOCKED_KEYWORDS
from src.agents.edu_agents import get_analyst_agent, get_communicator_agent
from src.agents.edu_tasks import get_analysis_task, get_response_task


class EduState(BaseModel):
    user_id: str = ""
    user_role: str = ""
    student_id: int = 0
    class_id: str = ""
    query: str = ""
    analysis_result: str = ""
    final_response: str = ""
    is_authorized: bool = True
    route_signal: str = ""  # New state-based signal


class EduMindFlow(Flow[EduState]):

    @start()
    def validate_and_route(self):
        print("--- DEBUG: Starting validate_and_route ---")

        if self.state.user_role == "parent":
            if not self.state.student_id or self.state.student_id == 0:
                self.state.is_authorized = False
                self.state.final_response = "So that I can help, please enter the child's ID number."
                return "missing_info"

            if any(word in self.state.query.lower() for word in PARENT_BLOCKED_KEYWORDS):
                return "denied"

            self.state.route_signal = "fetch_student_data"
            return "fetch_student_data"

        if self.state.user_role == "teacher":
            if "class" in self.state.query.lower():
                if not self.state.class_id:
                    self.state.final_response = "Hello teacher, please indicate which class you would like to perform the query for."
                    return "missing_info"
                self.state.route_signal = "fetch_class_data"
                return "fetch_class_data"
            self.state.route_signal = "fetch_student_data"
            return "fetch_student_data"

    @listen(validate_and_route)
    def get_individual_data(self):
        if self.state.route_signal != "fetch_student_data":
            return
        print("--- DEBUG: get_individual_data triggered! ---")
        try:
            res = get_student_analytics(self.state.student_id)
            self.state.analysis_result = res
            print(f"--- MCP Output: {self.state.analysis_result} ---")
        except Exception as e:
            print(f"--- MCP Error: {e} ---")
            self.state.analysis_result = "No data available due to error."

        return "data_ready"

    @listen(validate_and_route)
    def get_class_data(self):
        if self.state.route_signal != "fetch_class_data":
            return
        print("--- DEBUG: get_classroom_data triggered! ---")
        self.state.analysis_result = get_class_analytics(self.state.class_id)
        return "data_ready"

    @listen('denied')
    def handle_denial(self):
        print("--- DEBUG: handle_denial triggered! ---")
        self.state.final_response = "Access denied for privacy reasons."
        return "finished"

    @listen('missing_info')
    def handle_missing_info(self):
        print("Stopping flow: Missing essential ID.")

    @listen(or_(get_individual_data, get_class_data))
    async def generate_ai_response(self):
        print("--- DEBUG: generate_ai_response triggered! ---")
        if not self.state.analysis_result:
            self.state.final_response = "I couldn't retrieve the necessary data to answer your question."
            return "failed"

        analyst = get_analyst_agent()
        communicator = get_communicator_agent()

        analysis_task = get_analysis_task(analyst, self.state.analysis_result)
        response_task = get_response_task(communicator, "Use the provided analytics", self.state.user_role)

        crew = Crew(
            agents=[analyst, communicator],
            tasks=[analysis_task, response_task],
            verbose=True
        )

        result = await crew.kickoff_async()
        self.state.final_response = result.raw if hasattr(result, 'raw') else str(result)
        print("--- Flow finished successfully ---")
        return "finished"


async def run_edu_flow():
    print("--- Starting EduMind Simulation ---")

    initial_state = {
        "user_role": "parent",
        "student_id": 123456789,
        "query": "How is my child progressing in Math?"
    }

    flow = EduMindFlow()

    # התיקון הקריטי: משתמשים ב-kickoff_async() כי יש שלבי async ב-Flow
    result = await flow.kickoff_async(inputs=initial_state)

    print("\n" + "=" * 50)
    # מוודאים שאנחנו מדפיסים את מה שחזר מה-AI
    print(f"FINAL AI RESPONSE:\n{flow.state.final_response}")
    print("=" * 50)


if __name__ == "__main__":
    # הרצה דרך asyncio
    import asyncio

    asyncio.run(run_edu_flow())