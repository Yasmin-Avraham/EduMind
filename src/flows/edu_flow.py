from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel
from src.mcp_servers.db_server import get_student_analytics, get_class_analytics
from src.config import PARENT_BLOCKED_KEYWORDS

class EduState(BaseModel):
    user_id: str = ""
    user_role: str = ""  # "teacher" or "parent"
    student_id: int = 0
    class_id: str = ""
    query: str = ""
    analysis_result: str = ""
    final_response: str = ""
    is_authorized: bool = True


class EduMindFlow(Flow[EduState]):

    @start()
    def validate_and_route(self):
        """
        Strict permission checking by role and query[cite: 158].
        """
        print(f"User Role: {self.state.user_role} | Query: {self.state.query}")

        # role: parent
        if self.state.user_role == "parent":
            if any(word in self.state.query.lower() for word in PARENT_BLOCKED_KEYWORDS):
                self.state.is_authorized = False
                self.state.final_response = "As a parent, the system allows you to view only your child's data for privacy reasons."
                return "denied"
            return "fetch_personal_data"

        # role: teacher
        if self.state.user_role == "teacher":
            if "class" in self.state.query:
                return "fetch_class_data"
            return "fetch_personal_data"

    @listen("fetch_personal_data")
    def get_individual_data(self):
        # Calling the personal analytics tool in MCP that we wrote about earlier
        print(f"Fetching data for student {self.state.student_id}...")
        self.state.analysis_result = get_student_analytics(self.state.student_id)

    @listen("fetch_class_data")
    def get_classroom_data(self):
        # Call for the new classroom analytics tool in MCP
        print(f"Fetching classroom data for {self.state.class_id}...")
        self.state.analysis_result = get_class_analytics(self.state.class_id)