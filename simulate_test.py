from src.flows.edu_flow import EduMindFlow
import asyncio
import sys


async def run_simulation():
    print("--- תחילת סימולציית מערכת EduMind ---")

    # סימולציה 1: הורה
    print("\n[Scenario 1: Parent Query]")
    parent_flow = EduMindFlow()

    print("מריץ סוכני בינה מלאכותית עבור הורה... (זה עשוי לקחת זמן בגלל Ollama)")

    # ב-CrewAI Flows, ה-kickoff עצמו מנהל את הריצה.
    # אם הוא מחזיר TypeError ב-await, נריץ אותו ללא await.
    try:
        parent_flow.kickoff(inputs={
            "user_role": "parent",
            "student_id": 1,
            "query": "How is my child progressing? Are there any comments from the teacher?"
        })
    except TypeError:
        # במידה והגרסה דורשת kickoff_async מפורש
        await parent_flow.kickoff_async(inputs={
            "user_role": "parent",
            "student_id": 1,
            "query": "How is my child progressing?"
        })

    print(f"\nFinal Response to Parent:")
    print(f"{parent_flow.state.final_response if parent_flow.state.final_response else 'No response generated.'}")

    print("\n" + "-" * 50 + "\n")

    # סימולציה 2: מורה
    print("[Scenario 2: Teacher Query]")
    teacher_flow = EduMindFlow()

    print("מריץ סוכני בינה מלאכותית עבור מורה...")
    try:
        teacher_flow.kickoff(inputs={
            "user_role": "teacher",
            "class_id": "Class_grade_D_2",
            "query": "What is the class average in Math?"
        })
    except TypeError:
        await teacher_flow.kickoff_async(inputs={
            "user_role": "teacher",
            "class_id": "Class_grade_D_2",
            "query": "What is the class average in Math?"
        })

    print(f"\nFinal Response to Teacher:")
    print(f"{teacher_flow.state.final_response if teacher_flow.state.final_response else 'No response generated.'}")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # הרצה דרך asyncio כדי לתמוך ב-Ollama וב-kickoff_async
    asyncio.run(run_simulation())