from crewai import Task
from src.agents.edu_agents import get_analyst_agent, get_communicator_agent

# Analytic Task
def get_analysis_task(agent, data_context):
    return Task(
        description=f"Analyze the following pedagogical data.: {data_context}. Identify trends, outliers, and improvement/regression.",
        expected_output="A specific and professional report that includes the main statistical findings.",
        agent=agent
    )

# The drafting task (depending on the role)
def get_response_task(agent, analysis_report, role):
    return Task(
        description=f"""Based on the analysis: {analysis_report}, Write an answer for {role}.
        If it's a parent - be empathetic and encouraging. If it's a teacher - be matter-of-fact and professional.""",
        expected_output="Final answer ready to be sent to the user in chat.",
        agent=agent
    )