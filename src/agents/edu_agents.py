from crewai import Agent
from langchain_ollama import OllamaLLM
from src.config import OLLAMA_MODEL, OLLAMA_BASE_URL

# Connect to local model
MODEL_STR = f"ollama/{OLLAMA_MODEL}"
# 1.The Data Analyst Agent
def get_analyst_agent():
    return Agent(
        role='Pedagogical Data Analyst',
        goal='Analyze student grade and trend data and produce accurate academic insights',
        backstory='''You are a data analytics expert in education. Your job is to look at numbers. 
        And understand what they say about the learning process. You know how to identify improvement, regression, or difficulty in certain subjects.''',
        llm=MODEL_STR,
        base_url=OLLAMA_BASE_URL,
        allow_delegation=False,
        verbose=True
    )

# 2.The Communicator Agent
def get_communicator_agent():
    return Agent(
        role='Parent-Teacher Communication Consultant',
        goal='Formulate the data analysts insights in an empathetic, clear, and constructive manner according to the target audience',
        backstory='''You are an expert in pedagogical communication. When you address a parent, you are sensitive and encouraging.. 
        When you approach a teacher, you are matter-of-fact and professional. Your job is to make technical information accessible in a human way.''',
        llm=MODEL_STR,
        base_url=OLLAMA_BASE_URL,
        allow_delegation=False,
        verbose=True
    )