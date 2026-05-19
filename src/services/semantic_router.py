from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate


class SemanticRoute(BaseModel):
    intent: Literal["child_only", "class_comparison", "general_regulations"] = Field(
        description="Select 'child_only' for individual student data, 'class_comparison' for entire class metrics, or 'general_regulations' for school rules."
    )
    reasoning: str = Field(description="A brief one-sentence explanation of the intent selection.")


def determine_semantic_route(user_query: str, user_role: str, llm_instance) -> str:
    """
    Semantically analyzes the user request and classifies it into the correct data path.
    Uses structured examples to train small models.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI Intent Router for a school dashboard.
        Your sole task is to classify the user's query into exactly ONE of the following categories.

        CATEGORIES:
        - 'child_only': The user is asking about an INDIVIDUAL student's grades, specific test scores, or personal averages (e.g., "my child's average", "his score").
        - 'class_comparison': The user is asking about COLLECTIVE class metrics, overall class averages, or comparing a student to the rest of the class (e.g., "class average", "compared to the class").
        - 'general_regulations': The user is asking about general school policies, rules, or code of conduct.
        

        CRITICAL DIRECTION FOR THE WORD 'AVG' / 'AVERAGE':
        - If the query mentions "avg of my child", "my son's average", or "my daughter's math average", it is STRICTLY 'child_only' because it belongs to ONE specific child.
        - Only select 'class_comparison' if they ask about the whole class average.
        - If the user asks about rules, rules for being late, attendance policies, dress code, or school handbook guidelines, it is STRICTLY 'general_regulations'.
        - Even if they mention "my child is late to class" or "rules for my child", if the core question is about a RULE or REGULATION, choose 'general_regulations'.

        EXAMPLES FOR TRAINING:
        Query: "What is the avg of my child in Mathematics?" -> Intent: "child_only"
        Query: "What's my daughter's average grade?" -> Intent: "child_only"
        Query: "How did David do on his last exam?" -> Intent: "child_only"
        Query: "What is the class average for the math test?" -> Intent: "class_comparison"
        Query: "How is my child doing compared to the class average?" -> Intent: "class_comparison"
        Query: "What is the dress code policy?" -> Intent: "general_regulations"
        Query: "what is the regulation if my child late to the class?" -> Intent: "general_regulations"
        Query: "what happens if a student misses a test?" -> Intent: "general_regulations"
        Query: "Is there a specific dress code for the school?" -> Intent: "general_regulations"
        Query: "What is the avg of my child in Mathematics?" -> Intent: "child_only"
        Query: "What is the class average for the math test?" -> Intent: "class_comparison"

        Context: The logged-in user role is: {role}
        """),
        ("human", "Classify this query: {query}")
    ])

    try:
        structured_llm = llm_instance.with_structured_output(SemanticRoute)
        chain = prompt | structured_llm

        result = chain.invoke({"query": user_query, "role": user_role})

        print(f"\n--- [ROUTER DIAL] Intent: {result.intent} | Reason: {result.reasoning} ---\n")

        return result.intent

    except Exception as e:
        print(f"--- [ROUTER ERROR] Falling back to 'child_only'. Error: {e} ---")
        return "child_only"