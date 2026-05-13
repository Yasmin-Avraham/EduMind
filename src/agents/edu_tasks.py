from crewai import Task
from src.agents.edu_agents import get_analyst_agent, get_communicator_agent

# Analytic Task
def get_analysis_task(agent, data_context, user_query):
    return Task(
        description=f"""
        1. Identify if the user asked about a specific subject in this query: "{user_query}".
        2. From the following data: {data_context}, extract information ONLY related to that subject if specified.
        3. If NO specific subject is mentioned, analyze the overall performance across all subjects.

        CRITICAL RULES:
        - NEVER mention a subject that does not appear in the data.
        - If the user asks about a subject that is missing from the data, state clearly: "I don't have data for [Subject]".
        - Focus ONLY on the facts provided in the context.
        """,
        expected_output="A factual analysis focused ONLY on the requested subject or a general overview if none requested.",
        agent=agent
    )
# The drafting task (depending on the role)
def get_response_task(agent, analysis_report, role, user_query):
    if role == 'parent':
        style_guide = """
        - TONE: Warm, supportive.
        - RULE: Directly answer the question asked in: "{user_query}".
        - STRUCTURE: [Direct Answer] + [One supporting detail] + [Encouragement].
        - EXAMPLE: "Hi! Regarding your question, [Student] is doing [Status] in [Subject] with a grade of [Grade]. Keep up the good work!"
        """
    else:  # teacher
        style_guide = """
        - TONE: Professional, concise.
        - RULE: Answer the query: "{user_query}" based ONLY on facts.
        - EXAMPLE: "Regarding [Subject]: The current average is [Grade]. Status: [Trend]."
        """

    return Task(
        description=f"""
        Based on the analysis: {analysis_report}, write a response to the user's query: "{user_query}".

        STRICT RULES:
        1. Use ONLY subjects mentioned in the analysis. 
        2. If the analysis says a subject is missing, tell the user you don't have that information.
        3. DO NOT mention History unless it's in the data.

        {style_guide}
        """,
        expected_output="A concise chat response (max 40 words) that directly addresses the user's query.",
        agent=agent
    )