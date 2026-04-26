

import sys
import os
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
                return self.handle_missing_info()

            if any(word in self.state.query.lower() for word in PARENT_BLOCKED_KEYWORDS):
                return self.handle_denial()
            return self.get_individual_data()

        if self.state.user_role == "teacher":
            if "class" in self.state.query.lower():
                if not self.state.class_id:
                    self.state.final_response = "Hello teacher, please indicate which class you would like to perform the query for."
                    return self.handle_missing_info()
                return self.get_classroom_data()
            return self.get_individual_data()

    # @listen("fetch_personal")
    def get_individual_data(self):
        print("--- DEBUG: get_individual_data triggered! ---")
        try:
            res = get_student_analytics(self.state.student_id)
            self.state.analysis_result = res
            print(f"--- MCP Output: {self.state.analysis_result} ---")
        except Exception as e:
            print(f"--- MCP Error: {e} ---")
            self.state.analysis_result = "No data available due to error."

        return "data_ready"

    # @listen("fetch_class")
    def get_classroom_data(self):
        print("--- DEBUG: get_classroom_data triggered! ---")
        self.state.analysis_result = get_class_analytics(self.state.class_id)
        return "data_ready"

    # @listen("denied")
    def handle_denial(self):
        print("--- DEBUG: handle_denial triggered! ---")
        self.state.final_response = "Access denied for privacy reasons."
        return "finished"

    def handle_missing_info(self):
        print("Stopping flow: Missing essential ID.")

    # @listen("data_ready")
    def generate_ai_response(self):
        print("--- DEBUG: generate_ai_response triggered! ---")

        analyst = get_analyst_agent()
        communicator = get_communicator_agent()

        analysis_task = get_analysis_task(analyst, self.state.analysis_result)
        response_task = get_response_task(communicator, "Use the provided analytics", self.state.user_role)

        crew = Crew(
            agents=[analyst, communicator],
            tasks=[analysis_task, response_task],
            verbose=True
        )

        result = crew.kickoff()
        self.state.final_response = str(result)
        print("--- Flow finished successfully ---")
        return "finished"


if __name__ == "__main__":
    # The CRITICAL change: Pass state inside kickoff
    initial_state = {
        "user_role": "parent",
        "student_id": 1,
        "query": "what is my childs grades"
    }

    flow = EduMindFlow()
    flow.kickoff(inputs=initial_state)  # Passing inputs here
    print(f"FINAL STATE RESPONSE: {flow.state.final_response}")