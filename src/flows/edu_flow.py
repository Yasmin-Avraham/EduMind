import sys
import os
sys.path.append(os.getcwd())
from crewai import Crew
from crewai.flow.flow import Flow, start, listen
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

class EduMindFlow(Flow[EduState]):

    @start()
    def validate_and_route(self):
        print(f"User Role: {self.state.user_role} | Query: {self.state.query}")

        if self.state.user_role == "parent":
            if any(word in self.state.query.lower() for word in PARENT_BLOCKED_KEYWORDS):
                print("Access denied: Blocked keywords found.")
                self.state.is_authorized = False
                return "denied"
            return "fetch_personal"

        if self.state.user_role == "teacher":
            if "class" in self.state.query.lower():
                return "fetch_class"
            return "fetch_personal"

    @listen("fetch_personal")
    def get_individual_data(self):
        print(f"Fetching data for student {self.state.student_id}...")
        self.state.analysis_result = get_student_analytics(self.state.student_id)
        print(f"MCP Result: {self.state.analysis_result}")
        return "data_ready"

    @listen("fetch_class")
    def get_classroom_data(self):
        print(f"Fetching classroom data for {self.state.class_id}...")
        self.state.analysis_result = get_class_analytics(self.state.class_id)
        print(f"MCP Result: {self.state.analysis_result}")
        return "data_ready"

    @listen("denied")
    def handle_denial(self):
        self.state.final_response = "Access denied for privacy reasons."
        print(self.state.final_response)
        return "finished"

    @listen("data_ready")
    def generate_ai_response(self):
        print("Starting Agentic execution...")

        analyst = get_analyst_agent()
        communicator = get_communicator_agent()

        analysis_task = get_analysis_task(analyst, self.state.analysis_result)
        response_task = get_response_task(communicator, "Analysis results provided in context", self.state.user_role)

        crew = Crew(
            agents=[analyst, communicator],
            tasks=[analysis_task, response_task],
            verbose=True
        )

        result = crew.kickoff()
        self.state.final_response = str(result)
        return "finished"

if __name__ == "__main__":
    flow = EduMindFlow()
    flow.state.user_role = "parent"
    flow.state.student_id = 1
    flow.state.query = "what is the grades of my class?"

    flow.kickoff()