from crewai import Task
from src.agents.edu_agents import get_analyst_agent, get_communicator_agent

# Analytic Task
def get_analysis_task(agent, data_context, user_query):
    return Task(
        description=f"""
        Analyze this raw pedagogical data: {data_context} to answer the user query: "{user_query}".
        Extract only the relevant raw scores, averages, and statistics. 
        Do not add any commentary, safety disclaimers, or advice. Just state the mathematical facts.
        """,
        expected_output="A clean summary of the calculated or extracted numerical grades.",
        agent=agent
    )
# The drafting task (depending on the role)
def get_response_task(agent, data_context, user_role, user_query):
    return Task(
        description=f"""
        You are replying directly to a {user_role} who asked: "{user_query}".
        Review the raw analysis and the strategy recommendations from the previous steps.

        CRITICAL FORMATTING RULES:
        1. FIRST LINE: State the direct answer or the numerical data immediately and clearly (e.g., "Your child's average in Mathematics is 85.0.").
        2. FOLLOWING LINES: Add the practical learning tips or encouraging remarks right below the data.
        3. LENGTH: The entire response must be extremely brief—maximum 2-3 sentences total.
        4. No bold titles, no headers, no bullet points, and absolutely NO safety or consent disclaimers. Just talk naturally.
        """,
        expected_output="A direct, short 2-3 sentence chat reply starting with the data followed by brief tips.",
        agent=agent
    )
def get_strategy_task(agent, user_query):
    return Task(
        description=f"""
        Review the academic facts from the previous analysis for the query: "{user_query}".
        If needed, provide maximum 1-2 very short, practical learning tips (e.g., "focus on algebra homework").
        If the student is doing perfectly fine, you can skip tips and just output a short encouraging note.
        """,
        expected_output="1-2 brief, actionable educational recommendations or an encouraging note.",
        agent=agent
    )